from troposphere import Template, ec2

template = Template('Tech Challenge Network Infrastructure')

vpc = template.add_resource(
    ec2.VPC(
        'VPC',
        CidrBlock='10.0.0.0/22',
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        InstanceTenancy='default'
    )
)