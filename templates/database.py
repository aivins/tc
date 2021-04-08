from troposphere import (
    Template, Output, Export, Ref, GetAtt, Parameter, ImportValue
)

from troposphere import ec2, rds

template = Template('Tech Challenge Database')

master_user_password = template.add_parameter(
    Parameter(
        'MasterUserPassword',
        Default='/master_user_password',
        Description='PostgreSQL Master User Password',
        Type='AWS::SSM::Parameter::Value<String>'
    )
)

db_access_source_security_group = template.add_resource(
    ec2.SecurityGroup(
        'DatabaseAccessSecurityGroup',
        GroupDescription='DB access source security group',
        VpcId=ImportValue('TechChallengeVpc')
    )
)

db_security_group = template.add_resource(
    ec2.SecurityGroup(
        'DatabaseSecurityGroup',
        GroupDescription='DB access',
        VpcId=ImportValue('TechChallengeVpc'),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                SourceSecurityGroupId=Ref(db_access_source_security_group),
                IpProtocol='tcp',
                FromPort=5432,
                ToPort=5432
            )
        ]

    )
)

db_subnet_group = template.add_resource(
    rds.DBSubnetGroup(
        'DatabaseSubnetGroup',
        DBSubnetGroupDescription='DatabaseSubnet Group',
        DBSubnetGroupName='DatabaseSubnetGroup',
        SubnetIds=[
            ImportValue('PrivateSubnetA'),
            ImportValue('PrivateSubnetB'),
        ]
    )
)

database = template.add_resource(
    rds.DBInstance(
        'DatabaseInstance',
        DBInstanceClass='db.t3.small',
        Engine='postgres',
        DBName='application',
        MasterUsername='application',
        MasterUserPassword=Ref(master_user_password),
        StorageType='gp2',
        AllocatedStorage='10',
        PubliclyAccessible=False,
        MultiAZ=True,
        AllowMajorVersionUpgrade=False,
        AutoMinorVersionUpgrade=False,
        DBSubnetGroupName=Ref(db_subnet_group),
        VPCSecurityGroups=[Ref(db_security_group)]
    )
)


template.add_output(
    Output(
        'DatabaseEndpoint',
        Description='DatabaseEndpoint',
        Value=GetAtt(database, 'Endpoint.Address'),
        Export=Export('DatabaseEndpoint')
    )
)

template.add_output(
    Output(
        'DatabaseSecurityGroupAccess',
        Description='DatabaseSecurityGroupAccess',
        Value=Ref(db_security_group),
        Export=Export('DatabaseSecurityGroupAccess')
    )
)

template.add_output(
    Output(
        'DatabaseAccess',
        Description='DatabaseAccess',
        Value=Ref(db_access_source_security_group),
        Export=Export('DatabaseAccess')
    )
)
