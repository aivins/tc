import os
from troposphere import (
    Template, Tag, Parameter, Ref, ImportValue, Sub, Base64, iam, ec2
)
from troposphere import elasticloadbalancingv2 as elb
from .constants import *

from awacs.aws import (
    Policy,
    PolicyDocument,
    Statement,
    Allow,
    Principal
)
import awacs.sts


fh = open(os.path.join(os.path.dirname(__file__), '..', 'files', 'init.sh'), 'r')
init_script = fh.read()
fh.close()


template = Template('Tech Challenge Application')

vpc_id = ImportValue('TechChallengeVpc')
public_subnet_a = ImportValue('PublicSubnetA')
public_subnet_b = ImportValue('PublicSubnetB')


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
        VpcId=vpc_id,
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
        NetworkInterfaces=[
            ec2.NetworkInterfaceProperty(
                AssociatePublicIpAddress=True,
                DeviceIndex=0,
                GroupSet=[
                    Ref(instance_sg),
                    ImportValue('DatabaseAccess')
                ],
                SubnetId=public_subnet_a
            )
        ],
        UserData=Base64(
            Sub(
                init_script,
                DatabaseEndpoint=ImportValue('DatabaseEndpoint')
            )
        ),
        Tags=[Tag('Name', 'ApplicationInstance')]
    )
)

load_balancer_sg = template.add_resource(
    ec2.SecurityGroup(
        'LoadBalancerSecurityGroup',
        GroupDescription='Permit port 80',
        VpcId=vpc_id,
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="80",
                ToPort="80",
                CidrIp="0.0.0.0/0"
            )
        ]
    )
)

load_balancer = template.add_resource(
    elb.LoadBalancer(
        'LoadBalancer',
        Type='application',
        Scheme='internet-facing',
        Subnets=[public_subnet_a, public_subnet_b],
        SecurityGroups=[Ref(load_balancer_sg)]
    )
)

target_group = template.add_resource(
    elb.TargetGroup(
        'TargetGroup',
        VpcId=vpc_id,
        Port=3000,
        Protocol='HTTP',
        TargetType='instance',
        HealthCheckEnabled=True,
        HealthCheckPath='/healthcheck/'
    )
)


listener = template.add_resource(
    elb.Listener(
        'HttpListener',
        LoadBalancerArn=Ref(load_balancer),
        Port=80,
        Protocol='HTTP',
        DefaultActions=[
            elb.Action(
                Type='forward',
                TargetGroupArn=Ref(target_group)
            )
        ]
    )
)
