# Week 10, Day 7: Quiz Day - AWS with Python (boto3) Cheat Sheet

## Week 10 Quick Reference

### boto3 Setup
```python
import boto3

# Session
session = boto3.Session(region_name="us-east-1", profile_name="default")

# Client (low-level, returns dicts)
ec2 = boto3.client("ec2", region_name="us-east-1")

# Resource (high-level, returns objects)
s3 = boto3.resource("s3")

# Available in session
session.available_profiles
session.region_name
```

### EC2 Management
```python
ec2 = boto3.client("ec2")

# List instances
response = ec2.describe_instances()
for r in response["Reservations"]:
    for i in r["Instances"]:
        print(i["InstanceId"], i["State"]["Name"])

# Filter
ec2.describe_instances(Filters=[
    {"Name": "instance-state-name", "Values": ["running"]},
    {"Name": "tag:Environment", "Values": ["production"]},
])

# Start / Stop / Terminate
ec2.start_instances(InstanceIds=["i-abc123"])
ec2.stop_instances(InstanceIds=["i-abc123"])
ec2.terminate_instances(InstanceIds=["i-abc123"])

# Tags
def get_tag(instance, key):
    for tag in instance.get("Tags", []):
        if tag["Key"] == key:
            return tag["Value"]
    return None
```

### S3 Operations
```python
s3 = boto3.client("s3")

# Buckets
s3.create_bucket(Bucket="my-bucket",
    CreateBucketConfiguration={"LocationConstraint": "us-west-2"})
s3.list_buckets()                    # {"Buckets": [...]}
s3.delete_bucket(Bucket="my-bucket")

# Objects
s3.upload_file("local.txt", "bucket", "key/path.txt")
s3.download_file("bucket", "key/path.txt", "local.txt")
s3.put_object(Bucket="b", Key="k", Body="data")
s3.get_object(Bucket="b", Key="k")  # response["Body"].read()
s3.list_objects_v2(Bucket="b", Prefix="logs/")  # {"Contents": [...]}
s3.delete_object(Bucket="b", Key="k")
```

### IAM Management
```python
iam = boto3.client("iam")

# Users
iam.create_user(UserName="alice")
iam.delete_user(UserName="alice")
iam.list_users()

# Policies
policy_doc = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["s3:GetObject"],
        "Resource": ["arn:aws:s3:::bucket/*"]
    }]
}
iam.create_policy(PolicyName="name", PolicyDocument=json.dumps(policy_doc))
iam.attach_user_policy(UserName="alice", PolicyArn="arn:...")
```

### CloudWatch
```python
cw = boto3.client("cloudwatch")

# Metrics
cw.get_metric_statistics(
    Namespace="AWS/EC2", MetricName="CPUUtilization",
    Dimensions=[{"Name": "InstanceId", "Value": "i-abc"}],
    StartTime=start, EndTime=end, Period=300,
    Statistics=["Average"]
)

# Alarms
cw.put_metric_alarm(AlarmName="HighCPU", MetricName="CPUUtilization",
    Namespace="AWS/EC2", Threshold=80.0,
    ComparisonOperator="GreaterThanThreshold",
    EvaluationPeriods=2, Period=300, Statistic="Average")
cw.describe_alarms()
```

### Lambda
```python
lmb = boto3.client("lambda")

# Invoke
response = lmb.invoke(
    FunctionName="my-func",
    InvocationType="RequestResponse",
    Payload=json.dumps({"key": "value"})
)
result = json.loads(response["Payload"].read())
```

### Error Handling
```python
from botocore.exceptions import ClientError, NoCredentialsError

try:
    response = ec2.describe_instances()
except NoCredentialsError:
    print("No credentials configured")
except ClientError as e:
    code = e.response["Error"]["Code"]
    msg = e.response["Error"]["Message"]
    print(f"AWS Error [{code}]: {msg}")
```

## Key Concepts Learned This Week
1. boto3 has clients (low-level) and resources (high-level)
2. EC2 instances have states, types, tags, and security groups
3. S3 organizes data in buckets and objects with keys
4. IAM follows the principle of least privilege
5. Policies are JSON: Effect + Action + Resource
6. CloudWatch monitors metrics and triggers alarms
7. Lambda runs serverless functions on events
8. Always handle credentials carefully -- never hardcode them
