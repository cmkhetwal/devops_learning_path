# Week 10, Day 2: EC2 Management with boto3

## What You'll Learn
- Describing EC2 instances with `describe_instances()`
- Starting, stopping, and terminating instances
- Using filters to find specific instances
- Understanding instance types, states, and tags
- Writing EC2 management functions

## EC2 Overview

EC2 (Elastic Compute Cloud) is AWS's virtual server service. Each instance
is a virtual machine with a specific CPU, memory, storage, and network config.

```
Instance Lifecycle:
  pending -> running -> stopping -> stopped -> terminated
                  |                    |
                  +-----> shutting-down +
```

## Describing Instances

```python
import boto3

ec2 = boto3.client("ec2", region_name="us-east-1")

# Get all instances
response = ec2.describe_instances()
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        print(f"ID: {instance['InstanceId']}")
        print(f"Type: {instance['InstanceType']}")
        print(f"State: {instance['State']['Name']}")
        print(f"Launch: {instance.get('LaunchTime', 'N/A')}")
        print()
```

## Filtering Instances

```python
# Filter by state
running = ec2.describe_instances(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
)

# Filter by tag
production = ec2.describe_instances(
    Filters=[{"Name": "tag:Environment", "Values": ["production"]}]
)

# Filter by instance type
large = ec2.describe_instances(
    Filters=[{"Name": "instance-type", "Values": ["t3.large", "t3.xlarge"]}]
)

# Multiple filters (AND logic)
response = ec2.describe_instances(
    Filters=[
        {"Name": "instance-state-name", "Values": ["running"]},
        {"Name": "tag:Team", "Values": ["backend"]},
    ]
)
```

## Start, Stop, Terminate

```python
# Stop instances
ec2.stop_instances(InstanceIds=["i-1234567890abcdef0"])

# Start instances
ec2.start_instances(InstanceIds=["i-1234567890abcdef0"])

# Terminate (permanent!)
ec2.terminate_instances(InstanceIds=["i-1234567890abcdef0"])
```

## Tags

Tags are key-value pairs for organizing resources:

```python
# Get instance name from tags
def get_instance_name(instance):
    tags = instance.get("Tags", [])
    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]
    return "unnamed"

# Add tags
ec2.create_tags(
    Resources=["i-1234567890abcdef0"],
    Tags=[
        {"Key": "Name", "Value": "web-server-01"},
        {"Key": "Environment", "Value": "production"},
    ]
)
```

## Instance Types

```python
# Common instance types:
# t3.micro  - 2 vCPU, 1 GB RAM  (free tier)
# t3.small  - 2 vCPU, 2 GB RAM
# t3.medium - 2 vCPU, 4 GB RAM
# t3.large  - 2 vCPU, 8 GB RAM
# m5.large  - 2 vCPU, 8 GB RAM  (compute optimized)
# r5.large  - 2 vCPU, 16 GB RAM (memory optimized)
```

## Simulating EC2 for Practice

```python
MOCK_INSTANCES = [
    {
        "InstanceId": "i-0abc123def456789a",
        "InstanceType": "t3.micro",
        "State": {"Name": "running", "Code": 16},
        "LaunchTime": "2024-01-10T08:00:00Z",
        "Tags": [
            {"Key": "Name", "Value": "web-server-01"},
            {"Key": "Environment", "Value": "production"},
        ],
        "PublicIpAddress": "54.123.45.67",
        "PrivateIpAddress": "10.0.1.10",
    },
]
```

## DevOps Connection
- **Auto-scaling**: Start/stop instances based on load
- **Cost management**: Stop dev instances after hours, terminate unused
- **Inventory**: Track all instances across regions
- **Compliance**: Ensure proper tags, security groups, instance types
- **Disaster recovery**: Quickly spin up instances in another region

## Key Takeaways
1. `describe_instances()` returns nested dicts: Reservations -> Instances
2. Use `Filters` to find specific instances by state, tags, type
3. `stop_instances()` preserves the instance; `terminate_instances()` destroys it
4. Tags are essential for organization -- always name your instances
5. Instance state transitions follow a specific lifecycle
