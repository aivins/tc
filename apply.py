#!/usr/bin/env python3
#
# apply.py
# Quick script to drive troposphere and deploy CFN templates in development
# and from CI pipelines

import sys
import argparse
import boto3
import templates


def get_args():
    parser = argparse.ArgumentParser(description='Apply CFN templates')
    parser.add_argument('template', type=str,
                        help='an integer for the accumulator')
    args = parser.parse_args()
    return args


def deploy_template(template_name, template):
    create = False
    template_body = template.to_yaml()
    cfn = boto3.client('cloudformation')

    try:
        cfn.describe_stacks(
            StackName=template_name
        )
    except cfn.exceptions.ClientError as e:
        if 'stack with id network does not exist' in str(e).lower():
            create = True

    if create:
        print('Creating stack {template_name}...')
        cfn.create_stack(
            StackName=template_name,
            TemplateBody=template_body,
        )
        waiter = cfn.get_waiter('stack_create_complete')

    else:
        print('Updating stack {template_name}...')
        try:
            cfn.update_stack(
                StackName=template_name,
                TemplateBody=template_body,
            )
        except cfn.exceptions.ClientError as e:
            if 'no updates are to be performed' in str(e).lower():
                print('No updates are required!')
                sys.exit(1)

        waiter = cfn.get_waiter('stack_update_complete')

    print('Waiting for stack', 'creation...' if create else 'update...')
    waiter.wait(
        StackName=template_name,
        Delay=30,
        MaxAttempts=20
    )
    print(f'Stack {template_name} successfully',
          'created!' if create else 'updated!')


def main():
    args = get_args()

    template = getattr(templates, args.template, None)

    if not template:
        print(f'Template {args.template} not known')
        sys.exit(1)

    deploy_template(args.template, template)


if __name__ == '__main__':
    main()
