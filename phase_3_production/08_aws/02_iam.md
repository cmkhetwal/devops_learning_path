# Lesson 02: Identity and Access Management (IAM)

## Why This Matters in DevOps

IAM is the front door to every AWS resource. Before you launch a single EC2 instance,
store a single file in S3, or deploy a single Lambda function, you must answer: "Who
can do what, and under what conditions?" Getting IAM wrong means either a security
breach or an operational gridlock where developers cannot do their jobs.

In a DevOps context, IAM is not just about user accounts. It is about service-to-service
communication, CI/CD pipeline permissions, and automated infrastructure provisioning.
When your Terraform code creates an RDS database, what role does it assume? When your
Lambda function reads from DynamoDB, what policy grants it access? When a developer
pushes to a CodePipeline, what permissions does the pipeline have?

The principle of zero trust underpins modern IAM: never trust, always verify. Every
request is authenticated and authorized, regardless of where it originates. This
lesson teaches you to think in terms of least privilege --- granting the minimum
permissions necessary for a task and nothing more.

---

## Core Concepts

### IAM Building Blocks

```
                        AWS ACCOUNT
                            |
            +---------------+---------------+
            |               |               |
         USERS           GROUPS           ROLES
            |               |               |
            +-------+-------+               |
                    |                        |
                 POLICIES  <-----------------+
                    |
            +-------+-------+
            |               |
       IDENTITY-BASED   RESOURCE-BASED
        (attached to     (attached to
         user/group/      the resource
         role)            like S3 bucket)
```

### Users, Groups, and Roles

**IAM Users**: Represent a person or application that interacts with AWS. Each user
has permanent credentials (access key + secret key for CLI, password for console).

**IAM Groups**: Collections of users. Policies attached to a group apply to all
members. A user can belong to multiple groups. Groups cannot be nested.

**IAM Roles**: Temporary identities that can be assumed by users, services, or
external accounts. Roles do not have permanent credentials; they provide temporary
security tokens via AWS STS (Security Token Service). This is the preferred method
for granting access.

```
WHEN TO USE WHAT:

  User Account     --> Human logging into the console or using CLI daily
  Group            --> Organizing users by job function (Developers, Admins, ReadOnly)
  Role (EC2)       --> EC2 instance needs to access S3 or DynamoDB
  Role (Lambda)    --> Lambda function needs to read from SQS
  Role (Cross-Acct)--> Another AWS account needs access to your resources
  Role (Federation)--> Users authenticated by corporate SAML/OIDC identity provider
```

### IAM Policy Documents (JSON)

Every permission in AWS is defined in a JSON policy document:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3ReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-app-bucket",
                "arn:aws:s3:::my-app-bucket/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "203.0.113.0/24"
                }
            }
        },
        {
            "Sid": "DenyDeleteBucket",
            "Effect": "Deny",
            "Action": "s3:DeleteBucket",
            "Resource": "*"
        }
    ]
}
```

**Key fields:**
- **Version**: Always "2012-10-17" (the current policy language version)
- **Effect**: "Allow" or "Deny" (Deny always wins over Allow)
- **Action**: The API call(s) being permitted or denied
- **Resource**: The ARN(s) of the resource(s) the action applies to
- **Condition**: Optional constraints (IP address, time, MFA, tags)

### Policy Evaluation Logic

```
                   START
                     |
                     v
            +------------------+
            | Is there an      |     YES
            | explicit DENY?   |---------> DENIED
            +------------------+
                     | NO
                     v
            +------------------+
            | Is there an      |     YES
            | explicit ALLOW?  |---------> ALLOWED
            +------------------+
                     | NO
                     v
                  DENIED
            (implicit deny)
```

### Policy Types and Precedence

| Policy Type | Attached To | Purpose |
|-------------|-----------|---------|
| **AWS Managed** | Users/Groups/Roles | Predefined by AWS (e.g., AmazonS3ReadOnlyAccess) |
| **Customer Managed** | Users/Groups/Roles | Created by you for your specific needs |
| **Inline** | Single User/Group/Role | Embedded directly, one-to-one relationship |
| **Resource-Based** | Resources (S3, SQS, etc.) | Attached to the resource, not the identity |
| **Permission Boundary** | Users/Roles | Sets maximum permissions (ceiling) |
| **SCP** | AWS Organization OU/Account | Restricts what accounts in an org can do |

### Multi-Factor Authentication (MFA)

MFA adds a second layer of authentication beyond username and password:

```
Authentication Flow:
  Username + Password  -->  Something you KNOW
  MFA Token            -->  Something you HAVE (phone, hardware key)

  Both required = much harder to compromise
```

Options: Virtual MFA (Google Authenticator, Authy), Hardware MFA (YubiKey), SMS (not recommended).

### AWS Organizations and Service Control Policies

```
                  ORGANIZATION ROOT
                        |
              +---------+---------+
              |                   |
        OU: Production       OU: Development
        SCP: No delete       SCP: Region restrict
              |                   |
        +---------+          +---------+
        |         |          |         |
    Account A  Account B  Account C  Account D
    (Prod Web) (Prod DB)  (Dev Team1)(Dev Team2)
```

**Service Control Policies (SCPs)** are guardrails applied at the Organization level.
They do NOT grant permissions; they restrict what is possible. Even if an IAM policy
in Account A says "Allow *", an SCP on the Production OU saying "Deny ec2:TerminateInstances"
will prevent instance termination.

### Cross-Account Access

```
ACCOUNT A (Trusting)              ACCOUNT B (Trusted)
+------------------------+       +------------------------+
| Role: CrossAccountRole |       | User: DevOpsEngineer   |
| Trust Policy:          |       |                        |
|   Principal:           |<------| aws sts assume-role    |
|     Account B          |       |   --role-arn <RoleARN> |
| Permissions Policy:    |       |                        |
|   Allow S3 access      |       | Gets temporary creds   |
+------------------------+       +------------------------+
```

---

## Step-by-Step Practical

### Create an IAM Admin Group and User

```bash
# Create an admin group
aws iam create-group --group-name Admins

# Attach the AdministratorAccess managed policy
aws iam attach-group-policy \
    --group-name Admins \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create a user
aws iam create-user --user-name devops-engineer

# Add user to admin group
aws iam add-user-to-group \
    --user-name devops-engineer \
    --group-name Admins

# Create access keys for CLI usage
aws iam create-access-key --user-name devops-engineer
# Save the AccessKeyId and SecretAccessKey securely!

# Enable console access with a password
aws iam create-login-profile \
    --user-name devops-engineer \
    --password 'TempP@ssw0rd!2024' \
    --password-reset-required
```

### Create a Least-Privilege Policy

```bash
# Create a custom policy that allows read-only S3 access to a specific bucket
cat > s3-readonly-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListSpecificBucket",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::my-app-data-bucket"
        },
        {
            "Sid": "ReadObjectsInBucket",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
            "Resource": "arn:aws:s3:::my-app-data-bucket/*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name S3ReadOnlyMyAppBucket \
    --policy-document file://s3-readonly-policy.json
# Returns the policy ARN
```

### Create a Role for EC2

```bash
# Create the trust policy (who can assume this role)
cat > ec2-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the role
aws iam create-role \
    --role-name EC2-S3-ReadOnly \
    --assume-role-policy-document file://ec2-trust-policy.json

# Attach the policy to the role
aws iam attach-role-policy \
    --role-name EC2-S3-ReadOnly \
    --policy-arn arn:aws:iam::123456789012:policy/S3ReadOnlyMyAppBucket

# Create an instance profile (required to attach a role to EC2)
aws iam create-instance-profile \
    --instance-profile-name EC2-S3-ReadOnly-Profile

aws iam add-role-to-instance-profile \
    --instance-profile-name EC2-S3-ReadOnly-Profile \
    --role-name EC2-S3-ReadOnly
```

### Create a Developer Group with Boundaries

```bash
# Create a developers group
aws iam create-group --group-name Developers

# Attach permissions
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Create a permission boundary to prevent IAM escalation
cat > dev-boundary.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "s3:*",
                "lambda:*",
                "dynamodb:*",
                "logs:*",
                "cloudwatch:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Deny",
            "Action": [
                "iam:CreateUser",
                "iam:DeleteUser",
                "iam:CreateRole",
                "iam:DeleteRole",
                "organizations:*"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name DeveloperBoundary \
    --policy-document file://dev-boundary.json

# Apply boundary when creating a user
aws iam create-user \
    --user-name junior-dev \
    --permissions-boundary arn:aws:iam::123456789012:policy/DeveloperBoundary
```

### Audit IAM Configuration

```bash
# Generate a credential report
aws iam generate-credential-report
aws iam get-credential-report --output text --query Content | base64 -d > cred-report.csv

# List all users
aws iam list-users --output table

# List policies attached to a user
aws iam list-attached-user-policies --user-name devops-engineer

# List groups a user belongs to
aws iam list-groups-for-user --user-name devops-engineer

# Check who has access keys that have not been rotated
aws iam list-users --query 'Users[*].[UserName,CreateDate]' --output table
```

---

## Exercises

### Exercise 1: Build a Team Structure
Create three groups: Admins, Developers, and ReadOnly. Create one user in each group.
Attach appropriate AWS managed policies (AdministratorAccess, PowerUserAccess,
ReadOnlyAccess). Verify each user can only perform their allowed actions.

### Exercise 2: Write a Custom Policy
Write a custom IAM policy that allows a user to start and stop EC2 instances but
only if they are tagged with `Environment=Development`. Use the `Condition` block
with `ec2:ResourceTag/Environment`.

### Exercise 3: Cross-Account Role
Create a role that can be assumed by another AWS account (use a second account or
a different user). Write the trust policy, create the role, attach permissions, and
test assuming the role with `aws sts assume-role`.

### Exercise 4: IAM Security Audit
Run `aws iam generate-credential-report` and analyze the output. Identify any users
without MFA enabled, any access keys older than 90 days, and any users who have
never logged in. Document your findings and recommend remediation steps.

### Exercise 5: Policy Simulator
Use the IAM Policy Simulator (console or CLI) to test whether a specific user or
role can perform a given action. Test at least 5 different action/resource combinations
and document the results.

---

## Knowledge Check

### Question 1
What is the difference between an IAM role and an IAM user?

**Answer:** An IAM user has permanent long-term credentials (password, access keys)
and represents a specific person or application. An IAM role has no permanent
credentials; instead, it provides temporary security tokens via STS when assumed.
Roles are preferred for granting access to AWS services (EC2, Lambda), cross-account
access, and federated users because temporary credentials automatically expire and
cannot be leaked in the same way.

### Question 2
If an IAM policy has both an Allow and a Deny for the same action on the same
resource, what happens?

**Answer:** Deny always wins. The explicit Deny overrides any Allow. This is a
fundamental rule of IAM policy evaluation. The only way to override an explicit
Deny is to remove it; you cannot override it with an Allow.

### Question 3
What is a Service Control Policy (SCP), and how does it differ from an IAM policy?

**Answer:** SCPs are policies applied at the AWS Organizations level to OUs or
accounts. They set the maximum permissions boundary for all users and roles in
the affected accounts. SCPs do not grant permissions --- they only restrict what
is possible. Even if an IAM policy in an account allows an action, an SCP denying
that action will prevent it. SCPs do not affect the management account.

### Question 4
Why should you use IAM roles instead of access keys for EC2 instances?

**Answer:** Access keys are long-term credentials that can be leaked, stolen, or
accidentally committed to source code. IAM roles provide temporary credentials
that are automatically rotated by AWS and delivered to the instance via the
instance metadata service. If an instance is compromised, the temporary credentials
expire quickly. Roles also eliminate the need to distribute and manage credentials.

### Question 5
What is a permission boundary and when would you use it?

**Answer:** A permission boundary is an advanced IAM feature that sets the maximum
permissions that an identity-based policy can grant to an IAM entity (user or role).
The effective permissions are the intersection of the identity policy and the
boundary. Use them when you want to delegate IAM administration (let developers
create their own roles) but prevent privilege escalation (they cannot create roles
with more permissions than the boundary allows).
