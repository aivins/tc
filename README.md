# Tech Challenge

## CloudFormation templates/stacks

CloudFormation templates are authored using Troposphere, which in turn generates the YAML which is sent to CloudFormation.

* Pipeline - sets up CI/CD
* Network - establish a fresh VPC with private and public subnets in 2 AZs
* Database - PostgreSQL database for application
* Application - Compute resources to host application

## Prerequisites

* python3

```
pip3 install -r requirements.txt
```

## Deploying stack manually

```
./apply <template_nbame>
```

Where `template_name` is one of the python modules under `templates/*`. This will either create or update a stack with the same name as the template.