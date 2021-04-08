from troposphere import (
    Template, Tag, Parameter, Ref, ImportValue, iam, ec2
)
from .constants import *

from awacs.aws import (
    Policy,
    PolicyDocument,
    Statement,
    Allow,
    Principal
)
import awacs.sts

template = Template('Tech Challenge Application')


key_name = template.add_parameter(
    Parameter(
        'KeyName',
        Type='String',
        Default='default',
        Description='Keypair to use for application instance'
    )
)


instance_sg = template.add_resource(
    ec2.SecurityGroup(
        'ApplicationInstanceSecurityGroup',
        GroupName='ApplicationInstanceSecurityGroup',
        GroupDescription='ApplicationInstanceSecurityGroup',
        VpcId=ImportValue('TechChallengeVpc'),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                CidrIp='0.0.0.0/0',
                IpProtocol='tcp',
                FromPort=80,
                ToPort=80
            )
        ]
    )
)

role = template.add_resource(
    iam.Role(
        'ApplicationInstanceRole',
        Description='Application Instance Role granting SSM management access',
        AssumeRolePolicyDocument=PolicyDocument(
            Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[awacs.sts.AssumeRole],
                        Principal=Principal("Service", ["ec2.amazonaws.com"])
                    )
            ]
        ),
        Path='/',
        ManagedPolicyArns=[
            'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        ],
    )
)

profile = template.add_resource(
    iam.InstanceProfile(
        'InstanceProfile',
        Path='/',
        Roles=[Ref(role)]
    )
)

instance = template.add_resource(
    ec2.Instance(
        'ApplicationInstance',
        AvailabilityZone=AZ_1,
        ImageId=AMI_ID,
        IamInstanceProfile=Ref(profile),
        InstanceType='t3.small',
        KeyName=Ref(key_name),
        SecurityGroupIds=[
            Ref(instance_sg),
            ImportValue('DatabaseSecurityGroupAccess')
        ],
        SubnetId=ImportValue('PublicSubnetA'),
        Tags=[Tag('Name', 'ApplicationInstance')]
    )
)
