# Week 10, Day 1: boto3 Setup - AWS SDK for Python

## What You'll Learn
- Installing and importing boto3
- Understanding sessions, clients, and resources
- Configuring credentials and regions
- The difference between clients and resources
- Safe patterns for learning without an AWS account

## Why boto3?

boto3 is the official AWS SDK for Python. It lets you programmatically
manage AWS services -- EC2 instances, S3 buckets, IAM users, Lambda
functions, and over 200 other services. In DevOps, boto3 is the backbone
of AWS automation.

## Installation

```bash
pip install boto3
```

## Sessions

A session stores configuration state (credentials, region, profile):

```python
import boto3

# Default session (uses ~/.aws/credentials and ~/.aws/config)
session = boto3.Session()

# Session with explicit config
session = boto3.Session(
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region_name="us-east-1"
)

# Session with a named profile
session = boto3.Session(profile_name="dev")
```

## Clients vs Resources

boto3 offers two ways to interact with AWS:

### Clients (Low-Level)
- 1:1 mapping to AWS API
- Returns raw dictionaries
- Every AWS service has a client

```python
# Client example
ec2_client = boto3.client("ec2", region_name="us-east-1")
response = ec2_client.describe_instances()
# response is a dict with all the raw API data
```

### Resources (High-Level)
- Object-oriented interface
- More Pythonic
- Available for popular services (EC2, S3, IAM, etc.)

```python
# Resource example
ec2_resource = boto3.resource("ec2", region_name="us-east-1")
instances = ec2_resource.instances.all()
for instance in instances:
    print(instance.id, instance.state)  # attribute access!
```

### When to Use Which?
| Feature      | Client            | Resource          |
|-------------|-------------------|-------------------|
| Coverage    | All AWS services  | Popular services  |
| Return type | Dicts             | Objects           |
| Pagination  | Manual            | Automatic         |
| Recommended | Low-level control | Day-to-day work   |

## Credentials Configuration

AWS credentials can come from (in priority order):
1. Explicit parameters in code (not recommended for production)
2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. Shared credentials file (`~/.aws/credentials`)
4. IAM role (on EC2 instances, Lambda, etc.)

```ini
# ~/.aws/credentials
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[dev]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

```ini
# ~/.aws/config
[default]
region = us-east-1
output = json

[profile dev]
region = us-west-2
```

## Regions

```python
# List all available regions for a service
ec2_client = boto3.client("ec2", region_name="us-east-1")
regions = ec2_client.describe_regions()
for r in regions["Regions"]:
    print(r["RegionName"])

# Common regions:
# us-east-1      (N. Virginia)
# us-west-2      (Oregon)
# eu-west-1      (Ireland)
# ap-southeast-1 (Singapore)
```

## Safe Learning Without AWS

For this course, we simulate boto3 calls with mock classes:

```python
class MockAWSClient:
    """Simulates a boto3 client for learning."""

    def __init__(self, service_name, region_name="us-east-1"):
        self.service_name = service_name
        self.region_name = region_name
        self.meta = type("Meta", (), {"region_name": region_name})()

    def describe_instances(self):
        return {"Reservations": []}

    def list_buckets(self):
        return {"Buckets": []}


class MockSession:
    """Simulates a boto3 session."""

    def __init__(self, region_name="us-east-1", profile_name="default"):
        self.region_name = region_name
        self.profile_name = profile_name

    def client(self, service_name, **kwargs):
        region = kwargs.get("region_name", self.region_name)
        return MockAWSClient(service_name, region)
```

## Error Handling

```python
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

try:
    client = boto3.client("ec2")
    response = client.describe_instances()
except NoCredentialsError:
    print("No AWS credentials found")
except PartialCredentialsError:
    print("Incomplete AWS credentials")
except ClientError as e:
    error_code = e.response["Error"]["Code"]
    print(f"AWS API error: {error_code}")
```

## DevOps Connection
- **Infrastructure as Code**: boto3 is the engine behind many IaC tools
- **Automation**: Automate instance management, deployments, backups
- **Cost control**: Query billing, shut down unused resources
- **Security**: Audit IAM policies, rotate credentials
- **Monitoring**: Read CloudWatch metrics, set up alarms

## Key Takeaways
1. `boto3.Session()` manages configuration state
2. `boto3.client()` gives you a low-level dictionary-based API
3. `boto3.resource()` gives you a high-level object-oriented API
4. Credentials come from env vars, config files, or IAM roles
5. Always specify a region -- AWS is region-specific
6. Never hardcode credentials in source code
