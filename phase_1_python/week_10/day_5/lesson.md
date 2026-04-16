# Week 10, Day 5: CloudWatch & Lambda with boto3

## What You'll Learn
- CloudWatch metrics and how to query them
- Setting up CloudWatch alarms
- AWS Lambda basics and invocation
- Monitoring infrastructure with CloudWatch
- Serverless function patterns

## CloudWatch Overview

CloudWatch is AWS's monitoring and observability service. It collects:
- **Metrics**: CPU, memory, disk, network, custom metrics
- **Logs**: Application and system logs
- **Alarms**: Notifications when thresholds are breached
- **Dashboards**: Visual monitoring panels

## CloudWatch Metrics

```python
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

# Get CPU utilization for an EC2 instance
response = cloudwatch.get_metric_statistics(
    Namespace="AWS/EC2",
    MetricName="CPUUtilization",
    Dimensions=[
        {"Name": "InstanceId", "Value": "i-1234567890abcdef0"},
    ],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,           # 5-minute intervals
    Statistics=["Average", "Maximum"],
)

for point in sorted(response["Datapoints"], key=lambda x: x["Timestamp"]):
    print(f"{point['Timestamp']}  Avg: {point['Average']:.1f}%  Max: {point['Maximum']:.1f}%")
```

## Common AWS Namespaces

```python
# AWS/EC2      - CPUUtilization, NetworkIn, NetworkOut, DiskReadOps
# AWS/ELB      - RequestCount, Latency, HTTPCode_Backend_2XX
# AWS/RDS      - DatabaseConnections, FreeStorageSpace, CPUUtilization
# AWS/S3       - BucketSizeBytes, NumberOfObjects
# AWS/Lambda   - Invocations, Duration, Errors, Throttles
```

## CloudWatch Alarms

```python
# Create an alarm
cloudwatch.put_metric_alarm(
    AlarmName="HighCPU-WebServer",
    MetricName="CPUUtilization",
    Namespace="AWS/EC2",
    Statistic="Average",
    Period=300,
    EvaluationPeriods=2,
    Threshold=80.0,
    ComparisonOperator="GreaterThanThreshold",
    Dimensions=[
        {"Name": "InstanceId", "Value": "i-1234567890abcdef0"},
    ],
    AlarmActions=[
        "arn:aws:sns:us-east-1:123456789012:alerts",
    ],
    AlarmDescription="Alarm when CPU exceeds 80% for 10 minutes",
)

# List alarms
response = cloudwatch.describe_alarms()
for alarm in response["MetricAlarms"]:
    print(f"{alarm['AlarmName']:30s}  State: {alarm['StateValue']}")
```

## AWS Lambda Overview

Lambda runs code without servers. You upload a function, and AWS handles
the infrastructure.

```python
lambda_client = boto3.client("lambda", region_name="us-east-1")

# Invoke a Lambda function
response = lambda_client.invoke(
    FunctionName="my-function",
    InvocationType="RequestResponse",  # synchronous
    Payload=json.dumps({"key": "value"}),
)

result = json.loads(response["Payload"].read())
print(f"Status: {response['StatusCode']}")
print(f"Result: {result}")
```

## Lambda Function Example

```python
# This is what a Lambda function looks like
def lambda_handler(event, context):
    """AWS Lambda entry point."""
    name = event.get("name", "World")
    return {
        "statusCode": 200,
        "body": f"Hello, {name}!",
    }
```

## Simulating CloudWatch and Lambda

```python
import random
from datetime import datetime, timedelta

class MockCloudWatch:
    """Simulates CloudWatch for learning."""

    def __init__(self):
        self.alarms = {}
        self.metrics = {}

    def put_metric_data(self, namespace, metric_name, value, dimensions=None):
        key = f"{namespace}/{metric_name}"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append({
            "Timestamp": datetime.utcnow().isoformat(),
            "Value": value,
            "Dimensions": dimensions or [],
        })

    def get_metric_statistics(self, namespace, metric_name, period_minutes=5,
                               points=12):
        """Generate simulated metric data."""
        data = []
        now = datetime.utcnow()
        for i in range(points):
            ts = now - timedelta(minutes=i * period_minutes)
            value = random.uniform(10, 90)
            data.append({
                "Timestamp": ts.isoformat(),
                "Average": round(value, 1),
                "Maximum": round(value + random.uniform(5, 15), 1),
            })
        return data
```

## DevOps Connection
- **Monitoring**: CloudWatch is the default AWS monitoring solution
- **Alerting**: Alarms trigger notifications via SNS, actions via Auto Scaling
- **Serverless**: Lambda replaces many batch jobs and microservices
- **Cost**: CloudWatch helps identify resource waste
- **Automation**: Lambda functions respond to events (S3 uploads, API calls)

## Key Takeaways
1. CloudWatch collects metrics from all AWS services automatically
2. Use `get_metric_statistics()` to query historical metric data
3. Alarms trigger when metrics cross thresholds for a sustained period
4. Lambda runs functions on-demand without managing servers
5. Lambda is invoked synchronously or asynchronously
6. CloudWatch + Lambda = powerful event-driven automation
