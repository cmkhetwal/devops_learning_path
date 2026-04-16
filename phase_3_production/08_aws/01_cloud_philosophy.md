# Lesson 01: Cloud Philosophy and AWS Foundations

## Why This Matters in DevOps

Cloud computing is not merely a technology shift --- it is a fundamental change in how
organizations think about infrastructure. Before the cloud, DevOps engineers managed
physical servers, estimated capacity months in advance, and dealt with hardware failures
at 3 AM. Cloud computing eliminates that burden and replaces it with a new set of
responsibilities: cost management, architectural design, and security configuration.

Understanding cloud philosophy means understanding that infrastructure is now code,
capacity is elastic, and failure is expected and designed for. Every DevOps engineer
working with AWS must internalize these principles before touching a single service.

The shift from CapEx (buying servers) to OpEx (paying for usage) changes not just
budgets but entire organizational structures. Teams that once waited weeks for hardware
now provision in seconds. This speed brings power --- and risk. A misconfigured S3
bucket can expose millions of records. An uncapped auto-scaling group can generate
a six-figure bill overnight. Cloud philosophy is about wielding this power responsibly.

---

## Core Concepts

### On-Premise vs Cloud Computing

```
ON-PREMISE                              CLOUD
+---------------------------+           +---------------------------+
| You Manage Everything     |           | Shared Responsibility     |
|                           |           |                           |
| [Application]             |           | [Application] -- You      |
| [Data]                    |           | [Data]        -- You      |
| [Runtime]                 |           | [Runtime]     -- Depends  |
| [Middleware]              |           | [Middleware]  -- Depends  |
| [Operating System]        |           | [OS]          -- Depends  |
| [Virtualization]          |           | [Virtualization] -- AWS   |
| [Servers]                 |           | [Servers]     -- AWS      |
| [Storage]                 |           | [Storage]     -- AWS      |
| [Networking]              |           | [Networking]  -- AWS      |
| [Physical Security]       |           | [Physical]    -- AWS      |
+---------------------------+           +---------------------------+
```

### Service Models: IaaS, PaaS, SaaS

| Model | You Manage | Provider Manages | AWS Example |
|-------|-----------|-----------------|-------------|
| **IaaS** | OS, runtime, app, data | Hardware, networking, virtualization | EC2, VPC |
| **PaaS** | App code, data | Everything below the app | Elastic Beanstalk, RDS |
| **SaaS** | Just use it | Everything | WorkMail, Chime |

Think of it as a spectrum of control vs convenience. IaaS gives you the most control
but the most responsibility. SaaS gives you the least of both.

### The Shared Responsibility Model

This is one of the most tested concepts on the SA Associate exam. AWS uses the
phrase: "Security OF the cloud vs Security IN the cloud."

```
+----------------------------------------------------------+
|              CUSTOMER RESPONSIBILITY                      |
|  "Security IN the Cloud"                                  |
|                                                          |
|  - Customer data                                         |
|  - Platform, applications, IAM                           |
|  - Operating system, network, firewall config            |
|  - Client-side encryption                                |
|  - Server-side encryption (file system / data)           |
|  - Network traffic protection (encryption, integrity)    |
+----------------------------------------------------------+
|              AWS RESPONSIBILITY                           |
|  "Security OF the Cloud"                                  |
|                                                          |
|  - Hardware / AWS Global Infrastructure                  |
|  - Regions, Availability Zones, Edge Locations           |
|  - Compute, Storage, Database, Networking (hardware)     |
|  - Managed services patching                             |
|  - Physical security of data centers                     |
+----------------------------------------------------------+
```

### AWS Global Infrastructure

AWS operates a global network of data centers organized into three tiers:

```
                    AWS GLOBAL INFRASTRUCTURE

    +-------------------+     +-------------------+
    |   Region:         |     |   Region:         |
    |   us-east-1       |     |   eu-west-1       |
    |                   |     |                   |
    |  +----+ +----+    |     |  +----+ +----+    |
    |  | AZ | | AZ |    |     |  | AZ | | AZ |    |
    |  | 1a | | 1b |    |     |  | 1a | | 1b |    |
    |  +----+ +----+    |     |  +----+ +----+    |
    |       +----+      |     |       +----+      |
    |       | AZ |      |     |       | AZ |      |
    |       | 1c |      |     |       | 1c |      |
    |       +----+      |     |       +----+      |
    +-------------------+     +-------------------+

    Edge Locations (400+): CloudFront CDN, Route 53 DNS
```

**Regions** (30+): Geographic areas with multiple data centers. Choose based on:
- Compliance requirements (data sovereignty)
- Proximity to users (latency)
- Service availability (not all services in all regions)
- Pricing (varies by region; us-east-1 is often cheapest)

**Availability Zones (AZs)**: Each region has 2-6 AZs. Each AZ is one or more
discrete data centers with redundant power, networking, and connectivity. AZs within
a region are connected by low-latency links but are physically separated (different
flood plains, power grids).

**Edge Locations**: Points of presence for CloudFront (CDN) and Route 53 (DNS).
These cache content close to end users for low latency.

### AWS Well-Architected Framework (6 Pillars)

| Pillar | Key Question | Core Principle |
|--------|-------------|----------------|
| **Operational Excellence** | How do you run and monitor systems? | Automate everything, iterate |
| **Security** | How do you protect information? | Least privilege, encryption, traceability |
| **Reliability** | How do you recover from failure? | Auto-recover, scale horizontally, test recovery |
| **Performance Efficiency** | How do you use resources efficiently? | Right-size, experiment, go serverless |
| **Cost Optimization** | How do you avoid unnecessary costs? | Pay only for what you use, measure |
| **Sustainability** | How do you minimize environmental impact? | Maximize utilization, use managed services |

### AWS Free Tier

Three types of free offerings:

1. **Always Free**: Services that are always free within limits (e.g., Lambda 1M requests/month, DynamoDB 25 GB)
2. **12 Months Free**: Free for the first 12 months after account creation (e.g., EC2 t2.micro 750 hrs/month, S3 5 GB)
3. **Trials**: Short-term free trials for specific services (e.g., Inspector 90-day trial)

---

## Step-by-Step Practical

### Creating an AWS Account

1. Navigate to https://aws.amazon.com and click "Create an AWS Account"
2. Enter email, account name, and verify email
3. Provide contact information (choose "Personal" for learning)
4. Enter payment information (credit card required, but free tier avoids charges)
5. Choose the "Basic (Free)" support plan
6. Sign in to the AWS Management Console

**Critical first steps after account creation:**

```bash
# Enable MFA on the root account (do this in the console)
# Console -> IAM -> Root account -> Security credentials -> MFA

# Create a billing alarm to avoid surprise charges
# Console -> CloudWatch -> Alarms -> Create alarm
# Select metric: Billing -> Total Estimated Charge
# Set threshold: USD 10.00
```

### Installing the AWS CLI

```bash
# On Ubuntu/Debian (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
# Expected output: aws-cli/2.x.x Python/3.x.x Linux/x86_64
```

```bash
# On macOS
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Configuring the AWS CLI

```bash
# Configure with your credentials (create an IAM user first, never use root keys)
aws configure
# AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name [None]: us-east-1
# Default output format [None]: json

# Verify configuration
aws sts get-caller-identity
# Expected output:
# {
#     "UserId": "AIDAJQABLZS4A3QDU576Q",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/devops-admin"
# }
```

### Using Named Profiles

```bash
# Create a named profile for different environments
aws configure --profile production
aws configure --profile staging

# Use a specific profile
aws s3 ls --profile production

# Set a default profile for a session
export AWS_PROFILE=staging

# List configured profiles
aws configure list-profiles
```

### Exploring AWS Services via CLI

```bash
# List all available regions
aws ec2 describe-regions --output table
# +----------------------------------------------------------+
# |                     DescribeRegions                       |
# +----------------------------+-----------------------------+
# |         Endpoint           |        RegionName           |
# +----------------------------+-----------------------------+
# | ec2.us-east-1.amazonaws.com|  us-east-1                  |
# | ec2.eu-west-1.amazonaws.com|  eu-west-1                  |
# ...

# List availability zones in your region
aws ec2 describe-availability-zones --region us-east-1 --output table

# Check which services are available
aws service-quotas list-services --output table --query 'Services[*].ServiceName'
```

### Setting Up a Billing Alarm via CLI

```bash
# Enable billing alerts (must be done in us-east-1)
# First, enable billing alerts in the console:
# Account -> Billing Preferences -> Receive Billing Alerts

# Create an SNS topic for alerts
aws sns create-topic --name billing-alerts --region us-east-1
# Returns: TopicArn

# Subscribe your email to the topic
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789012:billing-alerts \
    --protocol email \
    --notification-endpoint your-email@example.com \
    --region us-east-1

# Create the billing alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "MonthlyBillingAlarm" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 21600 \
    --threshold 10.00 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:billing-alerts \
    --dimensions Name=Currency,Value=USD \
    --region us-east-1
```

---

## Exercises

### Exercise 1: Account Setup Verification
Set up your AWS account, enable MFA on root, create an IAM admin user (not root),
install the CLI, and configure it with the IAM user credentials. Verify everything
works with `aws sts get-caller-identity`.

### Exercise 2: Explore Regions and AZs
Use the CLI to list all AWS regions and their availability zones. Create a table
showing which regions have the most AZs. Identify which region is closest to you
geographically.

### Exercise 3: Billing Protection
Set up a billing alarm that notifies you when estimated charges exceed $5. Create
an SNS topic, subscribe your email, confirm the subscription, and create the
CloudWatch alarm. Verify the alarm appears in the CloudWatch console.

### Exercise 4: Well-Architected Review
Pick any application you have deployed (even a simple web app). Map it against the
6 pillars of the Well-Architected Framework. For each pillar, write one sentence
describing how your app does or does not meet the pillar, and one improvement you
could make.

### Exercise 5: Cost Exploration
Use `aws ce get-cost-and-usage` (Cost Explorer API) to query your current month
spending by service. Even if you are on the free tier and spending is zero, practice
the command and understand the output format.

---

## Knowledge Check

### Question 1
What is the difference between a Region and an Availability Zone?

**Answer:** A Region is a geographic area (e.g., us-east-1 in Virginia) containing
multiple Availability Zones. An AZ is one or more discrete data centers within a
Region, each with independent power, cooling, and networking. AZs are connected to
each other with high-bandwidth, low-latency links but are physically isolated to
protect against localized failures.

### Question 2
In the Shared Responsibility Model, who is responsible for patching the operating
system on an EC2 instance?

**Answer:** The customer. EC2 is IaaS, so the customer manages the OS and everything
above it. AWS manages the underlying hardware, hypervisor, and physical security.
However, if you use a managed service like RDS, AWS handles OS patching.

### Question 3
Name the 6 pillars of the AWS Well-Architected Framework.

**Answer:** Operational Excellence, Security, Reliability, Performance Efficiency,
Cost Optimization, and Sustainability.

### Question 4
Why should you never use the root account for daily operations?

**Answer:** The root account has unrestricted access to all resources and billing.
If its credentials are compromised, an attacker can do anything including deleting
the entire account. Best practice is to create IAM users with appropriate permissions,
enable MFA on the root account, and lock away the root credentials. The root account
should only be used for account-level tasks like changing the support plan or
closing the account.

### Question 5
What are the three types of AWS Free Tier offerings?

**Answer:** (1) Always Free --- services with permanent free usage limits (e.g.,
Lambda 1M requests/month). (2) 12 Months Free --- services free for the first year
after account creation (e.g., EC2 t2.micro 750 hours/month). (3) Trials ---
short-term free trials for specific services (e.g., Amazon Inspector 90-day trial).
