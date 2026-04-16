# Week 10, Day 4: IAM & Security with boto3

## What You'll Learn
- IAM concepts: users, groups, roles, policies
- Managing IAM users with boto3
- Understanding and creating policies
- The principle of least privilege
- Security best practices for AWS automation

## IAM Overview

IAM (Identity and Access Management) controls WHO can do WHAT on AWS:

```
Users   -- Human identities with credentials
Groups  -- Collections of users with shared permissions
Roles   -- Temporary identities assumed by services or users
Policies -- JSON documents that define permissions
```

## The Principle of Least Privilege

**Never give more access than needed.**  In DevOps, this means:
- CI/CD pipelines get only the permissions they need for deployments
- Dev accounts cannot modify production resources
- Service roles are scoped to their specific function

## IAM Users

```python
import boto3

iam = boto3.client("iam")

# Create a user
iam.create_user(UserName="deploy-bot")

# List users
response = iam.list_users()
for user in response["Users"]:
    print(f"{user['UserName']:20s}  {user['Arn']}")

# Delete a user
iam.delete_user(UserName="deploy-bot")
```

## IAM Policies

Policies are JSON documents:

```python
import json

# An example policy allowing S3 read access
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*",
            ],
        }
    ],
}

# Create a managed policy
iam.create_policy(
    PolicyName="S3ReadOnlyPolicy",
    PolicyDocument=json.dumps(policy_document),
    Description="Read-only access to S3 bucket",
)

# Attach policy to a user
iam.attach_user_policy(
    UserName="deploy-bot",
    PolicyArn="arn:aws:iam::123456789012:policy/S3ReadOnlyPolicy"
)
```

## IAM Roles

Roles are used by AWS services (EC2, Lambda, etc.) to access other services:

```python
# Trust policy: who can assume this role
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}

iam.create_role(
    RoleName="EC2-S3-ReadOnly",
    AssumeRolePolicyDocument=json.dumps(trust_policy),
    Description="Allows EC2 instances to read S3",
)
```

## Common Policy Patterns

```python
# Admin access (DANGEROUS - use sparingly)
admin_policy = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
}

# EC2 management
ec2_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
            ],
            "Resource": "*",
        }
    ],
}

# Deny policy (explicit deny overrides any allow)
deny_delete = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "s3:DeleteBucket",
                "ec2:TerminateInstances",
            ],
            "Resource": "*",
        }
    ],
}
```

## Security Best Practices
1. **Never use root account** for daily tasks
2. **Enable MFA** for all human users
3. **Rotate access keys** regularly
4. **Use roles** instead of long-lived credentials
5. **Audit** policies regularly with IAM Access Analyzer
6. **Never commit credentials** to source code

## DevOps Connection
- **CI/CD Security**: Service accounts with minimal permissions
- **Secret Management**: Rotate keys, use IAM roles for EC2/Lambda
- **Compliance**: Audit who has access to what
- **Automation**: Programmatically manage users as team grows
- **Zero Trust**: Verify identity at every level

## Key Takeaways
1. IAM users are for people; roles are for services
2. Policies are JSON documents with Effect, Action, Resource
3. Least privilege: give only the permissions needed
4. Explicit Deny always wins over Allow
5. Use `iam.list_users()`, `iam.list_policies()` for auditing
6. AWS managed policies exist for common use cases
