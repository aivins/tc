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

db_security_group = template.add_resource(
    ec2.SecurityGroup(
        'ApplicationDatabaseSecurityGroup',
        GroupDescription='DB access for application',
        VpcId=ImportValue('TechChallengeVpc')
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
