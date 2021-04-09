# Tech Challenge

This project deploys the techchallange binary into an AWS environment

## Architecture

Brief architecture explanation is as follows:

* One non-default VPC
* Two public subnets across two AZ
* Two private subnets across two AZ
* ALB and ASG in public subnets to serve application
* PostgreSQL RDS in multi AZ mode in the two private subnets
* RDS accepts connections on 5432 only from application instances
* Application instances accept connections on 3000 only from load balancer
* Load balancer accepts connections from anywhere on port 80

## CloudFormation templates/stacks

CloudFormation templates are authored using Troposphere, which in turn generates the YAML which is sent to CloudFormation. Troposphere templates are able to be read intuitively by anybody who is familiar with Cloudformation YAML/JSON.

* Network - establish a fresh VPC with private and public subnets in 2 AZs
* Database - PostgreSQL database for application
* Application - Compute resources to host application

## Prerequisites

* python3
* Configured awscli/boto3 environment to an account with full AWS admin access, most likely by setting AWS_PROFILE to something appropriate

This was developed and tested on MacOS with python 3.8.2.

## Deployment

Below is an example of how to deploy the project once above prequisites are met.

There is one manual task, that is to create the RDS Master Password in SSM Paramter Store. To do so, set SSM Parameter `/master_user_password` to the value of your chosen master password for RDS

```
git clone git@github.com-personal:aivins/tc.git techchallenge
cd techchallenge
python3 -mvenv venv
source venv/bin/activate
pip install -r requirements.txt
./apply.py network
./apply.py database
./apply.py application
```

When the final `apply.py` command finishes, the application will be available at the DNS name of the newly-created Application Load Balancer on port 80.

## Notes

* Assumption made that some kind of codebuild/codedeploy pipeline was overkill
* `TechChallengeApp update` needs `-s` flag because we're running on RDS and the named database already exists 
* Recreating an instance will reset the database tables due to how `TechChallengeApp update` works, assumed fixing this is out of scope
* Assumed no need to supply a tear down process, but can be easily done by manually deleting each stack with the AWS console