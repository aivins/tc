from troposphere import (
    Template, Ref, Tag, Output, Export, ec2
)
from .constants import *



template = Template('Tech Challenge Network Infrastructure')

# Fresh VPC, mostly for tech challenge demonstration purposes
vpc = template.add_resource(
    ec2.VPC(
        'VPC',
        CidrBlock='10.0.0.0/22',
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        InstanceTenancy='default',
        Tags=[Tag('Name', 'TechChallengeVpc')]
    )
)

igw = template.add_resource(
    ec2.InternetGateway(
        'InternetGateway'
    )
)

vpc_igw = template.add_resource(
    ec2.VPCGatewayAttachment(
        'VpcInternetGateway',
        InternetGatewayId=Ref(igw),
        VpcId=Ref(vpc),
    )
)

public_route_table = template.add_resource(
    ec2.RouteTable(
        'PublicRouteTable',
        VpcId=Ref(vpc)
    )
)

default_route = template.add_resource(
    ec2.Route(
        'PublicDefaultRoute',
        RouteTableId=Ref(public_route_table),
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=Ref(igw)
    )
)


# Public subnets across 2 AZ to host application
public_subnet_a = template.add_resource(
    ec2.Subnet(
        'PublicSubnetA',
        VpcId=Ref(vpc),
        AvailabilityZone=AZ_1,
        CidrBlock='10.0.0.0/24',
        MapPublicIpOnLaunch=True,
        Tags=[Tag('Name', 'PublicSubnetA')]
    )
)

public_subnet_b = template.add_resource(
    ec2.Subnet(
        'PublicSubnetB',
        VpcId=Ref(vpc),
        AvailabilityZone=AZ_2,
        CidrBlock='10.0.1.0/24',
        MapPublicIpOnLaunch=True,
        Tags=[Tag('Name', 'PublicSubnetB')]
    )
)

public_subnet_route_table_assoc_a = template.add_resource(
    ec2.SubnetRouteTableAssociation(
        'PublicSubnetRouteTableAssocA',
        RouteTableId=Ref(public_route_table),
        SubnetId=Ref(public_subnet_a)
    )
)

public_subnet_route_table_assoc_b = template.add_resource(
    ec2.SubnetRouteTableAssociation(
        'PublicSubnetRouteTableAssocB',
        RouteTableId=Ref(public_route_table),
        SubnetId=Ref(public_subnet_b)
    )
)

# Private subnets across 2 AZ to host database
private_subnet_a = template.add_resource(
    ec2.Subnet(
        'PrivateSubnetA',
        VpcId=Ref(vpc),
        AvailabilityZone=AZ_1,
        CidrBlock='10.0.2.0/24',
        Tags=[Tag('Name', 'PrivateSubnetA')]
    )
)

private_subnet_b = template.add_resource(
    ec2.Subnet(
        'PrivateSubnetB',
        VpcId=Ref(vpc),
        AvailabilityZone=AZ_2,
        CidrBlock='10.0.3.0/24',
        Tags=[Tag('Name', 'PrivateSubnetB')]
    )
)

# Expoted values

template.add_output(
    Output(
        'TechChallengeVpcOutput',
        Description='TechChallengeVpc',
        Value=Ref(vpc),
        Export=Export('TechChallengeVpc')
    ),
)
template.add_output(
    Output(
        'PublicSubnetAOutput',
        Description='PublicSubnetA',
        Value=Ref(public_subnet_a),
        Export=Export('PublicSubnetA')
    )
)
template.add_output(
    Output(
        'PublicSubnetBOutput',
        Description='PublicSubnetB',
        Value=Ref(public_subnet_b),
        Export=Export('PublicSubnetB')
    )
)
template.add_output(
    Output(
        'PrivateSubnetAOutput',
        Description='PrivateSubnetA',
        Value=Ref(private_subnet_a),
        Export=Export('PrivateSubnetA')
    )
)
template.add_output(
    Output(
        'PrivateSubnetBOutput',
        Description='PrivateSubnetB',
        Value=Ref(private_subnet_b),
        Export=Export('PrivateSubnetB')
    )
)