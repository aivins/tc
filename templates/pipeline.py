from troposphere import Template, Ref, ec2

template = Template('Tech Challenge CI/CD pipeline')





vpc = template.add_resource(
    ec2.VPC(
        'VPC',
        CidrBlock='10.0.0.0/22',
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        InstanceTenancy='default'
    )
)



