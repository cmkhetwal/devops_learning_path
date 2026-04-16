# Lesson 10: Monitoring with CloudWatch and Observability

## Why This Matters in DevOps

Monitoring is the eyes and ears of your infrastructure. Without it, you are flying
blind --- you do not know when things break, why they break, or how to prevent them
from breaking again. In DevOps, monitoring is not an afterthought; it is a first-class
concern that is built into every deployment.

AWS provides a suite of monitoring and observability services that together give you
complete visibility into your infrastructure: CloudWatch for metrics and logs,
CloudTrail for API auditing, AWS Config for compliance, X-Ray for distributed tracing,
and EventBridge for event-driven automation.

As a DevOps engineer, you will set up dashboards for executive visibility, create
alarms that page on-call engineers, write log queries to diagnose production issues,
and audit API calls to investigate security incidents. The SA Associate exam tests
your ability to choose the right monitoring tool for a given scenario and design
monitoring architectures that provide actionable insights.

---

## Core Concepts

### AWS Observability Stack

```
THREE PILLARS OF OBSERVABILITY:

  METRICS                LOGS                  TRACES
  (CloudWatch Metrics)   (CloudWatch Logs)     (X-Ray)
  |                      |                     |
  "What is happening?"   "Why is it happening?" "Where is it happening?"
  |                      |                     |
  CPU at 95%             Error: connection     Request took 2.3s
  Latency at 500ms       timeout to DB at      200ms in Lambda
  5xx errors spiking     10:32:15 UTC          1800ms in DynamoDB
                                               300ms in S3

  +--EventBridge (React to events)
  +--CloudTrail (Who did what, and when?)
  +--AWS Config (Is my infrastructure compliant?)
```

### CloudWatch Metrics

```
METRIC STRUCTURE:

  Namespace:  AWS/EC2
  MetricName: CPUUtilization
  Dimensions: InstanceId=i-1234567890abcdef0
  Timestamp:  2024-01-15T10:30:00Z
  Value:      75.5
  Unit:       Percent

METRIC TYPES:
  Built-in (free):
  - EC2: CPUUtilization, NetworkIn/Out, DiskRead/Write
  - RDS: DatabaseConnections, FreeStorageSpace, ReadLatency
  - ALB: RequestCount, TargetResponseTime, HTTP_5XX_Count
  - Lambda: Invocations, Duration, Errors, Throttles

  Custom (you create):
  - Application-level metrics (orders/minute, cache hit rate)
  - System-level (memory utilization, disk usage -- NOT default for EC2!)
  - Business metrics (revenue, active users)

IMPORTANT: EC2 does NOT report memory or disk metrics by default!
You must install the CloudWatch Agent to collect these.

RESOLUTION:
  Standard: 5-minute intervals (free)
  Detailed: 1-minute intervals (costs extra)
  High-res custom: 1-second intervals (costs extra)
```

### CloudWatch Alarms

```
ALARM STATES:

  OK  -----> ALARM -----> OK
        ^         |
        |         v
        +-- INSUFFICIENT_DATA

ALARM CONFIGURATION:
  +-------------------------------------------+
  | Alarm: High-CPU-Web-Server                |
  | Metric: AWS/EC2 CPUUtilization            |
  | Statistic: Average                        |
  | Period: 300 seconds (5 minutes)           |
  | Evaluation Periods: 3                     |
  | Threshold: > 80%                          |
  | Action: SNS -> PagerDuty -> On-call       |
  +-------------------------------------------+

  This means: "If average CPU exceeds 80% for 3 consecutive
  5-minute periods (15 minutes total), trigger the alarm."

COMPOSITE ALARMS:
  Combine multiple alarms with AND/OR logic
  Example: Alert only if CPU > 80% AND Memory > 90%
  Reduces alarm fatigue
```

### CloudWatch Logs

```
LOG ARCHITECTURE:

  Log Sources:
  +-- EC2 (via CloudWatch Agent)
  +-- Lambda (automatic)
  +-- ECS/Fargate (awslogs driver)
  +-- API Gateway (access logs)
  +-- VPC Flow Logs
  +-- CloudTrail
  +-- RDS (slow query logs)
  +-- Custom application logs

  Structure:
  LOG GROUP:    /app/production/web-server
      |
      +-- LOG STREAM: i-1234567890abcdef0
      |       |
      |       +-- Log Event: "2024-01-15 10:30:15 INFO  Request processed in 45ms"
      |       +-- Log Event: "2024-01-15 10:30:16 ERROR Connection refused to db:5432"
      |
      +-- LOG STREAM: i-0987654321fedcba0
              |
              +-- Log Event: ...

  RETENTION: 1 day to 10 years (or never expire)
  EXPORT: To S3 for long-term storage or to Kinesis for real-time processing
```

### CloudWatch Logs Insights

```
QUERY LANGUAGE (similar to SQL):

  # Find top 10 most common error messages in the last hour
  fields @timestamp, @message
  | filter @message like /ERROR/
  | stats count(*) as error_count by @message
  | sort error_count desc
  | limit 10

  # Calculate average response time by endpoint
  fields @timestamp, endpoint, response_time
  | stats avg(response_time) as avg_rt,
          max(response_time) as max_rt,
          count(*) as requests
    by endpoint
  | sort avg_rt desc

  # Find all 5xx errors with request details
  fields @timestamp, @message
  | filter status >= 500
  | sort @timestamp desc
  | limit 50

  # Detect anomalous request patterns
  fields @timestamp
  | stats count(*) as request_count by bin(5m)
  | sort request_count desc
```

### CloudTrail

```
CLOUDTRAIL: "Who did what, when, and from where?"

  Every AWS API call is logged:
  +------------------------------------------+
  | Event:                                   |
  |   EventName: TerminateInstances          |
  |   EventTime: 2024-01-15T10:30:00Z        |
  |   UserIdentity:                          |
  |     ARN: arn:aws:iam::123:user/devops-eng|
  |   SourceIPAddress: 203.0.113.50          |
  |   RequestParameters:                     |
  |     instancesSet: [i-1234567890abcdef0]  |
  |   ResponseElements:                      |
  |     instancesSet: [{currentState:        |
  |       shutting-down}]                    |
  +------------------------------------------+

  USE CASES:
  - Security investigation: "Who deleted the production database?"
  - Compliance: "Prove that only authorized users accessed PHI data"
  - Operational: "What change caused the outage at 3 AM?"

  TRAIL TYPES:
  - Management events: API calls to manage resources (free, 1 copy)
  - Data events: S3 object operations, Lambda invocations (charged)
  - Insights events: Detect unusual API activity (charged)
```

### AWS Config

```
AWS CONFIG: "Is my infrastructure compliant?"

  RULES (examples):
  - ec2-instances-in-vpc: All EC2 instances must be in a VPC
  - encrypted-volumes: All EBS volumes must be encrypted
  - s3-bucket-public-read-prohibited: No public S3 buckets
  - rds-multi-az-support: RDS instances must be Multi-AZ
  - restricted-ssh: No security groups allowing 0.0.0.0/0 on port 22

  REMEDIATION:
  Config can trigger automatic remediation via SSM Automation
  Example: Non-compliant SG detected -> automatically remove the rule

  CONFIGURATION HISTORY:
  Track how resources changed over time
  "Show me the security group rules for sg-xxx as they were on Jan 15"
```

### X-Ray (Distributed Tracing)

```
X-RAY: Trace requests across microservices

  Client -> API GW -> Lambda -> DynamoDB
              |                    |
              |    +--> S3         |
              |    |              |
  Trace: =====[====[=============]====]=====>
              200ms   1500ms   300ms
              |         |        |
              v         v        v
          API GW     Lambda   DynamoDB
          Latency    Latency  Latency

  X-Ray shows:
  - End-to-end request flow
  - Latency breakdown per service
  - Error rates per service
  - Service dependency map
  - Bottleneck identification
```

---

## Step-by-Step Practical

### Set Up Monitoring for an EC2 Web App

```bash
# Step 1: Install CloudWatch Agent on EC2
# SSH into the instance first, then:
sudo yum install -y amazon-cloudwatch-agent

# Step 2: Create CloudWatch Agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json << 'EOF'
{
    "agent": {
        "metrics_collection_interval": 60,
        "run_as_user": "cwagent"
    },
    "metrics": {
        "namespace": "Custom/WebServer",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
                "totalcpu": true
            },
            "mem": {
                "measurement": ["mem_used_percent", "mem_available_percent"]
            },
            "disk": {
                "measurement": ["used_percent"],
                "resources": ["/"]
            },
            "net": {
                "measurement": ["bytes_sent", "bytes_recv"],
                "resources": ["eth0"]
            }
        },
        "append_dimensions": {
            "InstanceId": "${aws:InstanceId}",
            "AutoScalingGroupName": "${aws:AutoScalingGroupName}"
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/httpd/access_log",
                        "log_group_name": "/app/webserver/access",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/httpd/error_log",
                        "log_group_name": "/app/webserver/error",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "/app/webserver/system",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    }
}
EOF

# Start the agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
    -s

# Verify the agent is running
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a status
```

### Create CloudWatch Alarms

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "WebServer-HighCPU" \
    --alarm-description "CPU utilization exceeds 80% for 15 minutes" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --evaluation-periods 3 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --alarm-actions arn:aws:sns:us-east-1:$ACCOUNT_ID:ops-alerts \
    --ok-actions arn:aws:sns:us-east-1:$ACCOUNT_ID:ops-alerts \
    --tags Key=Environment,Value=production

# Memory utilization alarm (custom metric from CloudWatch Agent)
aws cloudwatch put-metric-alarm \
    --alarm-name "WebServer-HighMemory" \
    --alarm-description "Memory utilization exceeds 90%" \
    --metric-name mem_used_percent \
    --namespace Custom/WebServer \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 90 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --alarm-actions arn:aws:sns:us-east-1:$ACCOUNT_ID:ops-alerts

# ALB 5xx error alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ALB-High5xxRate" \
    --alarm-description "5xx error rate exceeds 5% of requests" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 60 \
    --evaluation-periods 5 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=LoadBalancer,Value=app/web-alb/1234567890 \
    --alarm-actions arn:aws:sns:us-east-1:$ACCOUNT_ID:ops-alerts \
    --treat-missing-data notBreaching

# ALB latency alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ALB-HighLatency" \
    --alarm-description "p99 latency exceeds 2 seconds" \
    --metric-name TargetResponseTime \
    --namespace AWS/ApplicationELB \
    --extended-statistic p99 \
    --period 60 \
    --evaluation-periods 3 \
    --threshold 2.0 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=LoadBalancer,Value=app/web-alb/1234567890 \
    --alarm-actions arn:aws:sns:us-east-1:$ACCOUNT_ID:ops-alerts

# List all alarms
aws cloudwatch describe-alarms \
    --query 'MetricAlarms[*].[AlarmName,StateValue,MetricName,Threshold]' \
    --output table
```

### Create a CloudWatch Dashboard

```bash
cat > dashboard.json << 'EOF'
{
    "widgets": [
        {
            "type": "metric",
            "x": 0, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "EC2 CPU Utilization",
                "metrics": [
                    ["AWS/EC2", "CPUUtilization", "InstanceId", "i-EXAMPLE1"],
                    ["AWS/EC2", "CPUUtilization", "InstanceId", "i-EXAMPLE2"]
                ],
                "period": 300,
                "stat": "Average",
                "view": "timeSeries"
            }
        },
        {
            "type": "metric",
            "x": 12, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "ALB Request Count & Latency",
                "metrics": [
                    ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/web-alb/xxx", {"stat": "Sum"}],
                    ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/web-alb/xxx", {"stat": "Average", "yAxis": "right"}]
                ],
                "period": 60,
                "view": "timeSeries"
            }
        },
        {
            "type": "metric",
            "x": 0, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "ALB Error Rates",
                "metrics": [
                    ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", "app/web-alb/xxx", {"stat": "Sum", "color": "#2ca02c"}],
                    ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", "app/web-alb/xxx", {"stat": "Sum", "color": "#ff7f0e"}],
                    ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "app/web-alb/xxx", {"stat": "Sum", "color": "#d62728"}]
                ],
                "period": 60,
                "view": "timeSeries"
            }
        },
        {
            "type": "log",
            "x": 12, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "Recent Errors",
                "query": "SOURCE '/app/webserver/error' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20",
                "region": "us-east-1",
                "view": "table"
            }
        }
    ]
}
EOF

aws cloudwatch put-dashboard \
    --dashboard-name "Production-WebApp" \
    --dashboard-body file://dashboard.json
```

### Set Up CloudTrail

```bash
# Create an S3 bucket for CloudTrail logs
TRAIL_BUCKET="cloudtrail-logs-${ACCOUNT_ID}-$(date +%s)"
aws s3api create-bucket --bucket $TRAIL_BUCKET --region us-east-1

# Apply bucket policy for CloudTrail
cat > trail-bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {"Service": "cloudtrail.amazonaws.com"},
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::${TRAIL_BUCKET}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {"Service": "cloudtrail.amazonaws.com"},
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${TRAIL_BUCKET}/AWSLogs/${ACCOUNT_ID}/*",
            "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $TRAIL_BUCKET \
    --policy file://trail-bucket-policy.json

# Create the trail
aws cloudtrail create-trail \
    --name production-trail \
    --s3-bucket-name $TRAIL_BUCKET \
    --is-multi-region-trail \
    --enable-log-file-validation

aws cloudtrail start-logging --name production-trail

# Look up recent events
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances \
    --max-results 5 \
    --query 'Events[*].[EventTime,Username,EventName]' \
    --output table
```

### Query CloudWatch Logs Insights

```bash
# Query logs via CLI
aws logs start-query \
    --log-group-name /app/webserver/access \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'fields @timestamp, @message
        | filter @message like /500/
        | stats count(*) as error_count by bin(5m)
        | sort error_count desc'

# The above returns a queryId. Use it to get results:
# aws logs get-query-results --query-id <queryId>
```

---

## Exercises

### Exercise 1: Complete Monitoring Stack
Set up full monitoring for a web application: CloudWatch Agent for memory and disk
metrics, access and error log collection, alarms for CPU, memory, disk, 5xx errors,
and latency. Create a dashboard that shows all these metrics in one view.

### Exercise 2: Log-Based Alerting
Create a CloudWatch Logs metric filter that detects the pattern "OutOfMemoryError"
in application logs. Create an alarm on this metric that triggers an SNS notification.
Test by writing the pattern to the log group.

### Exercise 3: CloudTrail Investigation
Enable CloudTrail in your account. Perform several actions (launch an instance,
create a bucket, delete a security group). Then use `lookup-events` and Logs
Insights to find all actions performed by your user in the last hour. Create a
report of all destructive actions (Delete*, Terminate*).

### Exercise 4: Custom Metrics
Write a script that publishes custom application metrics to CloudWatch every 60
seconds: request count, average response time, error rate, and active user sessions.
Use `aws cloudwatch put-metric-data`. Create alarms on these custom metrics.

### Exercise 5: EventBridge Automation
Create an EventBridge rule that triggers when an EC2 instance is terminated. The rule
should invoke a Lambda function that logs the event details and sends a Slack
notification (via SNS). Test by terminating a test instance.

---

## Knowledge Check

### Question 1
What EC2 metrics does CloudWatch collect by default, and which require the
CloudWatch Agent?

**Answer:** Default metrics (no agent needed): CPUUtilization, NetworkIn/Out,
NetworkPacketsIn/Out, DiskReadOps/WriteOps, DiskReadBytes/WriteBytes, StatusCheck
Failed. Metrics requiring the CloudWatch Agent: memory utilization, disk space
utilization, swap usage, and any custom application metrics. This is a commonly
tested topic because many assume memory is collected by default, but it is not.

### Question 2
What is the difference between CloudWatch Logs and CloudTrail?

**Answer:** CloudWatch Logs collects and stores log data from applications,
operating systems, and AWS services (application logs, system logs, error logs).
CloudTrail logs every AWS API call (who, what, when, from where) for auditing
and compliance. Think of CloudWatch Logs as "what is happening in your
application" and CloudTrail as "what is happening in your AWS account." They
complement each other: CloudTrail can send its logs to CloudWatch Logs for
querying and alerting.

### Question 3
How would you create an alarm that fires only when both CPU and memory are high?

**Answer:** Use a CloudWatch Composite Alarm. Create two individual alarms (one for
CPU > 80%, one for memory > 90%), then create a composite alarm that triggers only
when both are in ALARM state (AND logic). This reduces alert fatigue because high
CPU alone might be normal during deployments, and high memory alone might be expected
for cache-heavy applications.

### Question 4
What is AWS Config and how does it differ from CloudTrail?

**Answer:** CloudTrail records API calls (actions taken). AWS Config records resource
configurations and changes over time. Config answers "what is the current state and
history of my resources?" while CloudTrail answers "who made what API calls?"
Config also evaluates resources against compliance rules (e.g., "are all EBS volumes
encrypted?") and can trigger automatic remediation. They work together: CloudTrail
shows who changed a security group, Config shows what the security group looked like
before and after.

### Question 5
When would you use X-Ray versus CloudWatch Logs for debugging?

**Answer:** Use X-Ray when you need to trace a request across multiple services and
identify which service is causing latency or errors in a distributed architecture
(microservices, Lambda chains, API Gateway pipelines). Use CloudWatch Logs when you
need to see detailed application-level log messages, stack traces, and debug output
from a specific service. X-Ray tells you where the problem is; CloudWatch Logs tell
you why the problem is happening.
