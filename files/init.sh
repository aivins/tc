#!/bin/bash

# Install some packages when application instance initializes
sudo yum install -y postgresql postgresql-devel jq

# Fetch database password from SSM
DB_PASS=$(aws ssm get-parameter --region ap-southeast-2 --name /master_user_password | jq '.Parameter.Value')

# Fetch tech challenge binary and unzip it 
mkdir -p /opt/techchallenge
curl -L -O 'https://github.com/servian/TechChallengeApp/releases/download/v.0.8.0/TechChallengeApp_v.0.8.0_linux64.zip'
unzip -d /opt/techchallenge TechChallengeApp_v.0.8.0_linux64.zip

# Create config file
cat <<EOF > /opt/techchallenge/dist/conf.toml
"DbUser" = "application"
"DbPassword" = ${!DB_PASS}
"DbName" = "application"
"DbPort" = "5432"
"DbHost" = "${DatabaseEndpoint}"
"ListenHost" = "0.0.0.0"
"ListenPort" = "3000"
EOF

# Create non-privileged system user to run app
useradd -r servian
chown -R servian.servian /opt/techchallenge

# Create systemd unit file to ensure app is running
cat <<EOF > /lib/systemd/system/techchallenge.service
[Unit]
Description=TechChallenge
After=network.target

[Service]
Type=simple
User=servian
WorkingDirectory=/opt/techchallenge/dist
ExecStart=/opt/techchallenge/dist/TechChallengeApp serve
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Update the database
# Looks like this destroys existing data, which isn't what we'd want on
# every new instance
cd /opt/techchallenge/dist
./TechChallengeApp updatedb -s

# Start serving now and after reboot
systemctl daemon-reload
systemctl enable techchallenge
systemctl start techchallenge
