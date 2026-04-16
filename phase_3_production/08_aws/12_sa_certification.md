# Lesson 12: AWS Solutions Architect Associate Certification

## Why This Matters in DevOps

The AWS Solutions Architect Associate (SAA-C03) certification validates your ability
to design distributed systems on AWS. It is one of the most sought-after cloud
certifications in the industry, and for good reason: it forces you to think
holistically about architecture, security, cost, and reliability.

For a DevOps engineer, this certification is not just a resume item. The knowledge
tested on this exam is exactly what you use daily: designing VPCs, choosing the right
database, implementing security controls, optimizing costs, and building highly
available architectures. Passing this exam means you can have architectural
conversations with solutions architects, understand the trade-offs behind design
decisions, and make better infrastructure choices.

This lesson is your exam strategy guide: what to study, how to study, what to expect
on exam day, and practice questions that mirror the real exam format.

---

## Core Concepts

### Exam Overview

```
EXAM: AWS Solutions Architect Associate (SAA-C03)

  Format:       65 questions (50 scored + 15 unscored experimental)
  Time:         130 minutes (2 hours 10 minutes)
  Passing:      720 out of 1000 (~72%)
  Cost:         $150 USD
  Valid for:    3 years
  Format:       Multiple choice (1 correct) and multiple response (2+ correct)
  Delivery:     Pearson VUE test center or online proctored

  QUESTION STYLE:
  Most questions are scenario-based:
  "A company has [situation]. They need [requirement].
   Which solution meets these requirements with the LEAST operational overhead?"
```

### Exam Domains

```
DOMAIN BREAKDOWN (SAA-C03):

  +---------------------------------------------+--------+
  | Domain                                      | Weight |
  +---------------------------------------------+--------+
  | 1. Design Secure Architectures              |  30%   |
  | 2. Design Resilient Architectures           |  26%   |
  | 3. Design High-Performing Architectures     |  24%   |
  | 4. Design Cost-Optimized Architectures      |  20%   |
  +---------------------------------------------+--------+

  DOMAIN 1 (30%): Security
  - IAM policies, roles, federation
  - Encryption at rest and in transit
  - VPC security (SGs, NACLs, endpoints)
  - Key management (KMS)
  - Logging and monitoring (CloudTrail, Config)

  DOMAIN 2 (26%): Resilience
  - Multi-AZ and multi-region architectures
  - Backup and restore strategies
  - Auto Scaling, fault tolerance
  - Disaster recovery (RPO/RTO)
  - Decoupling with SQS, SNS, EventBridge

  DOMAIN 3 (24%): Performance
  - EC2 instance types, placement groups
  - EBS volume types, instance stores
  - Caching (ElastiCache, CloudFront, DAX)
  - Database selection
  - Serverless architectures

  DOMAIN 4 (20%): Cost
  - EC2 pricing models
  - S3 storage classes
  - Right-sizing resources
  - Data transfer costs
  - Serverless vs provisioned cost comparison
```

### Most Tested Topics

```
HIGH-FREQUENCY TOPICS (appear in 60%+ of exams):

  1. S3 Storage Classes + Lifecycle Policies
  2. EC2 Instance Types + Pricing Models
  3. VPC Design (public/private subnets, NAT)
  4. RDS Multi-AZ vs Read Replicas
  5. IAM Roles vs Users vs Policies
  6. ALB vs NLB selection
  7. CloudWatch vs CloudTrail
  8. KMS encryption
  9. Auto Scaling configurations
  10. SQS/SNS decoupling patterns

MEDIUM-FREQUENCY TOPICS:
  - Aurora vs RDS vs DynamoDB selection
  - Lambda limits and use cases
  - ECS vs EKS vs Fargate
  - CloudFront + S3 origin
  - Route 53 routing policies
  - Direct Connect vs VPN
  - EFS vs EBS vs S3
  - Kinesis vs SQS for streaming
  - Disaster Recovery strategies
```

### Study Strategy

```
RECOMMENDED TIMELINE (8-12 weeks):

  Week 1-2:   Core Services
               EC2, S3, VPC, IAM
               Build hands-on labs for each

  Week 3-4:   Databases & Storage
               RDS, Aurora, DynamoDB, ElastiCache
               EBS types, EFS, S3 classes

  Week 5-6:   Networking & Content Delivery
               Route 53, CloudFront, VPC advanced
               Direct Connect, Transit Gateway

  Week 7-8:   Security & Monitoring
               KMS, Secrets Manager, GuardDuty
               CloudWatch, CloudTrail, Config

  Week 9-10:  Serverless & Containers
               Lambda, API Gateway, Step Functions
               ECS, EKS, Fargate

  Week 11:    Practice Exams
               Take 3-4 full practice exams
               Review every wrong answer
               Identify weak areas

  Week 12:    Final Review
               Re-study weak areas
               Review cheat sheets
               Take one more practice exam
               Schedule and take the real exam

STUDY METHODS:
  1. Video Course (choose one): Adrian Cantrill, Stephane Maarek, or Neal Davis
  2. Hands-on Labs: Build everything you learn about
  3. Practice Exams: Tutorials Dojo (Jon Bonso) -- closest to real exam
  4. Documentation: AWS FAQs for key services (S3, EC2, VPC, RDS)
  5. Flashcards: Create your own for limits, port numbers, key differences
```

---

## Practice Scenarios

### Scenario 1: Design a Highly Available Web Application

**Situation:** A company runs a web application on a single EC2 instance with an
attached EBS volume. The database is self-managed PostgreSQL on another EC2 instance.
They need high availability with automatic recovery.

**Requirements:** Minimize downtime, maintain data durability, automate recovery.

```
SOLUTION:

  +--Route 53 (DNS)--+
          |
  +---CloudFront----+
          |
  +------ALB--------+
     |           |
  +--ASG---------+--+
  | EC2  | EC2   |  |    AZ-A          AZ-B
  +------+-------+--+
     |           |
  +--RDS Multi-AZ---+
  | Primary | Standby|
  +------------------+

  KEY DECISIONS:
  1. Replace single EC2 with ASG (min 2, across 2 AZs)
  2. Replace self-managed DB with RDS Multi-AZ (automatic failover)
  3. Add ALB for load distribution and health checks
  4. Add CloudFront for caching and DDoS protection
  5. Use Route 53 with health checks and failover routing
  6. Store static assets in S3 (not on EC2 EBS)
```

### Scenario 2: Choose the Right Database

**Situation:** An e-commerce company needs databases for three use cases:
a) Product catalog with complex queries and joins
b) User session data with sub-millisecond reads
c) Order history that must be immutable for auditing

**Solution:**
```
  a) Product Catalog:
     Aurora PostgreSQL
     - Complex queries with JOINs (relational)
     - Up to 15 read replicas for read-heavy catalog browsing
     - Auto-scaling storage
     - Multi-AZ for high availability

  b) User Sessions:
     DynamoDB + DAX
     - Key-value access pattern (session ID -> data)
     - Sub-millisecond reads with DAX cache
     - Auto-scales to any traffic level
     - TTL for automatic session expiration

  c) Order History:
     Amazon QLDB (Quantum Ledger Database)
     - Immutable, cryptographically verifiable journal
     - Complete audit trail of all changes
     - SQL-like query language
     Alternative: DynamoDB with Streams + S3 for archival
```

### Scenario 3: Design a Secure VPC

**Situation:** A healthcare company needs a VPC that meets HIPAA requirements. Web
servers must be publicly accessible, application servers must be private, and database
servers must be completely isolated.

```
SOLUTION:

  INTERNET
      |
  +---IGW---+
      |
  +---WAF + ALB---+  (Public Subnets)
  |   SG: 443 from 0.0.0.0/0    |
  +---+--------+--+
      |        |
  +---v---+ +--v---+  (Private Subnets - App Tier)
  | App-1 | | App-2|
  | SG: 8080 from ALB-SG only  |
  +---+---+ +--+---+
      |        |
  +---v---+ +--v---+  (Isolated Subnets - DB Tier)
  | RDS-P | | RDS-S|
  | SG: 5432 from App-SG only  |
  | Encrypted at rest (KMS)     |
  | No internet route           |
  +-------+ +------+

  SECURITY CONTROLS:
  - VPC Flow Logs enabled -> CloudWatch Logs
  - NACLs on each subnet tier
  - VPC Endpoints for S3 and DynamoDB (no internet needed)
  - NAT Gateway for app tier outbound only
  - No public IPs on app or DB instances
  - All data encrypted at rest (EBS, RDS) and in transit (TLS)
  - CloudTrail logging all API calls
  - GuardDuty monitoring for threats
  - AWS Config rules for compliance checks
```

### Scenario 4: Optimize Costs

**Situation:** A company spends $50,000/month on AWS. Analysis shows:
- 20 m5.xlarge instances running 24/7 (web tier)
- 10 c5.2xlarge instances running batch jobs 6 hours/day
- 500 TB in S3 Standard (80% not accessed in 90+ days)
- Data transfer costs of $5,000/month

```
OPTIMIZATION STRATEGY:

  1. EC2 PRICING:
     Web tier (20 instances, 24/7):
     On-Demand: 20 * $0.192/hr * 730 = $2,803/month
     Reserved (1yr, no upfront): 20 * $0.120/hr * 730 = $1,752/month
     SAVINGS: $1,051/month (37%)

     Batch tier (10 instances, 6 hrs/day):
     On-Demand: 10 * $0.340/hr * 180 = $612/month
     Spot (70% discount): 10 * $0.102/hr * 180 = $184/month
     SAVINGS: $428/month (70%)

  2. S3 STORAGE:
     500 TB Standard: 500,000 GB * $0.023 = $11,500/month
     Lifecycle policy (move 80% to IA after 90 days):
     100 TB Standard: 100,000 * $0.023 = $2,300
     400 TB Standard-IA: 400,000 * $0.0125 = $5,000
     Total: $7,300/month
     SAVINGS: $4,200/month (37%)

  3. DATA TRANSFER:
     Use CloudFront (data out from CloudFront is cheaper)
     Use VPC Endpoints (S3 traffic stays in AWS network)
     Compress data before transfer
     Estimated SAVINGS: $1,500/month (30%)

  TOTAL MONTHLY SAVINGS: ~$7,179 (14% of total spend)
```

---

## Exam Tips

### Answering Strategy

```
1. READ THE QUESTION CAREFULLY:
   - Look for keywords: "LEAST operational overhead," "MOST cost-effective,"
     "highest availability," "MINIMUM latency"
   - These qualifiers are how AWS differentiates between similar answers

2. ELIMINATE WRONG ANSWERS:
   - If an answer mentions a service that does not exist, eliminate it
   - If an answer solves the problem but ignores a requirement, eliminate it
   - If an answer is overly complex for the requirement, likely wrong

3. LOOK FOR AWS-PREFERRED PATTERNS:
   - Managed services over self-managed (RDS over EC2+PostgreSQL)
   - Serverless when possible (Lambda > EC2 for event processing)
   - Decoupled architectures (SQS between services)
   - Multi-AZ for high availability
   - Encryption by default

4. TIME MANAGEMENT:
   - 130 minutes / 65 questions = 2 minutes per question
   - Flag difficult questions and come back
   - Never leave a question unanswered (no penalty for guessing)

5. KEY PHRASES AND WHAT THEY MEAN:
   "Cost-effective"         --> Consider Spot, Reserved, right-sizing
   "Least operational"      --> Managed service, serverless
   "Highly available"       --> Multi-AZ, Auto Scaling, load balancing
   "Durable"                --> S3 (11 nines), cross-region replication
   "Scalable"               --> Auto Scaling, DynamoDB, Lambda
   "Secure"                 --> Encryption, IAM, private subnets
   "Decoupled"              --> SQS, SNS, EventBridge
   "Real-time"              --> Kinesis, not SQS
   "Temporary credentials"  --> IAM Roles, STS
```

### Common Traps

```
TRAP 1: "Use a larger instance" is rarely the right answer.
         Scale horizontally (more instances) not vertically (bigger instance).

TRAP 2: "Store credentials in environment variables" is WRONG.
         Use Secrets Manager or Parameter Store.

TRAP 3: "Use a NAT Instance" is almost always wrong.
         Use NAT Gateway (managed, scales automatically).

TRAP 4: "Create an IAM user with access keys for the application."
         Use IAM Roles for applications on EC2, Lambda, ECS.

TRAP 5: "Use S3 Transfer Acceleration" does not always apply.
         Only useful for long-distance transfers (intercontinental).

TRAP 6: Read replicas for high availability is WRONG.
         Multi-AZ is for HA. Read replicas are for read scaling.

TRAP 7: "Use CloudWatch Events" -- this is now EventBridge.
         Same service, renamed. Both terms may appear.
```

---

## Sample Questions with Explanations

### Question 1

A company runs a web application on EC2 instances behind an ALB. The application
stores user-uploaded images on the local EC2 file system. When the Auto Scaling
Group launches new instances, the images are not available on the new instances.
What is the MOST operationally efficient solution?

A) Copy images between instances using rsync on a cron job
B) Store images in Amazon S3 and reference them via URLs
C) Use an EBS Multi-Attach volume shared between instances
D) Use Amazon EFS mounted on all instances

**Answer: B**

**Explanation:** S3 is the most operationally efficient because it is fully managed,
infinitely scalable, highly durable (11 nines), and does not require any
synchronization. EFS (D) would also work but adds complexity and cost. EBS
Multi-Attach (C) only works with io1/io2 and within a single AZ. Rsync (A) is
operational overhead and fragile. The key phrase is "MOST operationally efficient,"
which points to the managed solution (S3).

### Question 2

A company needs to process 10 million records from a CSV file in S3 every night.
Each record takes approximately 100ms to process. The processing can be done in
any order. What is the MOST cost-effective solution?

A) A single large EC2 instance (c5.9xlarge)
B) An AWS Lambda function triggered by an S3 event
C) Multiple Spot Instances in an ASG processing from an SQS queue
D) An AWS Batch job with Fargate

**Answer: C**

**Explanation:** 10M records at 100ms = 1,000,000 seconds of compute (~278 hours).
Lambda (B) is limited to 15 minutes per invocation and would require complex
chunking. A single large EC2 (A) is not cost-effective and is a single point of
failure. AWS Batch with Fargate (D) works but is more expensive than Spot. Multiple
Spot Instances processing from SQS (C) is the most cost-effective: Spot provides
up to 90% savings, SQS handles message distribution, and the architecture is
fault-tolerant (if a Spot Instance is reclaimed, messages return to the queue).

### Question 3

A company has a relational database that receives 1,000 read queries per second
and 50 write queries per second. The read latency must be under 5ms. The current
RDS instance is at 90% CPU. What should they do?

A) Upgrade to a larger RDS instance
B) Add an ElastiCache cluster in front of RDS
C) Create RDS read replicas
D) Migrate to DynamoDB

**Answer: B**

**Explanation:** The 20:1 read-to-write ratio and the requirement for sub-5ms
latency make caching the best solution. ElastiCache (Redis) provides microsecond
read latency for cached data. Most of the 1,000 reads/sec will hit the cache,
dramatically reducing RDS load. Read replicas (C) would help scale reads but add
more latency than a cache. Upgrading (A) is expensive and temporary. Migrating to
DynamoDB (D) requires significant application changes for a relational schema.

### Question 4

A Solutions Architect needs to design a disaster recovery strategy for a critical
application with an RTO of 1 hour and an RPO of 15 minutes. Which DR strategy is
the MOST cost-effective while meeting these requirements?

A) Multi-site active-active
B) Warm standby
C) Pilot light
D) Backup and restore

**Answer: C**

```
DR STRATEGIES (cost vs recovery time):

  Strategy          Cost    RTO        RPO
  Backup/Restore    $       Hours      Hours       (D - too slow)
  Pilot Light       $$      Minutes-1hr Minutes    (C - meets req)
  Warm Standby      $$$     Minutes    Seconds     (B - meets but costly)
  Multi-Site         $$$$    Near-zero  Near-zero   (A - overkill)
```

**Explanation:** Pilot light keeps core infrastructure running (database replication)
with minimal resources. On failover, you scale up the compute layer (launch EC2,
scale ASG). This meets the 1-hour RTO and 15-minute RPO at lower cost than warm
standby. Backup and restore (D) typically has hours of RTO and RPO, which violates
requirements. Warm standby (B) and multi-site (A) both exceed requirements and cost
more.

### Question 5

A company wants to restrict all IAM users in their development account from
launching EC2 instances larger than t3.medium. The restriction must apply even
if an IAM policy explicitly allows larger instances. What should they use?

A) IAM permission boundary
B) Service Control Policy (SCP)
C) IAM group policy with explicit deny
D) AWS Config rule with auto-remediation

**Answer: B**

**Explanation:** SCPs are applied at the AWS Organizations level and restrict what
is possible in an account, regardless of IAM policies within that account. Even if
an admin attaches a policy allowing all EC2 actions, the SCP can deny instances
larger than t3.medium. Permission boundaries (A) apply to individual users/roles
and must be set per entity. Group policies (C) can be bypassed by directly attached
policies. Config rules (D) detect after the fact, not prevent.

---

## Exercises

### Exercise 1: Full Practice Exam
Take a complete 65-question practice exam (Tutorials Dojo or Whizlabs). Score
yourself, then review every question --- both correct and incorrect --- and write
a one-sentence explanation for why each answer is right or wrong.

### Exercise 2: Architecture Design
Design a complete architecture for an e-commerce platform that handles 10,000
concurrent users, includes a product catalog, shopping cart, order processing, and
payment. Draw the architecture diagram, list all AWS services used, and justify
each choice. Calculate the estimated monthly cost.

### Exercise 3: Weak Area Deep Dive
Based on your practice exam results, identify your 3 weakest areas. For each area,
read the relevant AWS FAQ and whitepaper, complete a hands-on lab, and create 10
flashcards covering the most important facts.

### Exercise 4: Scenario Analysis
For each of the following scenarios, write a 1-paragraph solution:
a) A media company needs to process 4K video files (10-50 GB each) uploaded by users
b) A financial institution needs a database that handles 100,000 transactions/second
c) A startup needs to deploy a web app with zero DevOps experience
d) A hospital needs to store patient records with strict compliance requirements

### Exercise 5: Cost Optimization Challenge
Take your own AWS account (or a mock account) and identify at least 5 cost
optimization opportunities. Use AWS Cost Explorer, Trusted Advisor, and Compute
Optimizer. Document each finding with the current cost, recommended change, and
estimated savings.

---

## Knowledge Check

### Question 1
What are the four domains of the SAA-C03 exam and their weights?

**Answer:** (1) Design Secure Architectures: 30%, (2) Design Resilient Architectures:
26%, (3) Design High-Performing Architectures: 24%, (4) Design Cost-Optimized
Architectures: 20%. Security is the heaviest domain, reflecting AWS's emphasis on
security as a foundational concern.

### Question 2
What is the difference between RTO and RPO?

**Answer:** RTO (Recovery Time Objective) is the maximum acceptable time to restore
service after a disaster --- how long can you be down? RPO (Recovery Point Objective)
is the maximum acceptable data loss measured in time --- how much data can you afford
to lose? For example, RTO of 4 hours means the system must be back online within 4
hours. RPO of 1 hour means you can lose at most 1 hour of data (so backups must be
at least hourly).

### Question 3
Why does AWS recommend managed services over self-managed alternatives?

**Answer:** Managed services reduce operational overhead: AWS handles provisioning,
patching, scaling, backups, and high availability. This lets your team focus on
application development rather than infrastructure management. Managed services
also typically provide better availability (built-in Multi-AZ), security (encryption
by default, compliance certifications), and cost efficiency (pay for what you use,
no idle capacity). On the exam, managed services are almost always preferred unless
the question specifically requires a custom configuration that managed services
cannot support.

### Question 4
What distinguishes a "most cost-effective" answer from a "least operational overhead" answer?

**Answer:** "Most cost-effective" means the cheapest solution that still meets all
requirements --- this often means Spot Instances, S3 lifecycle policies, Reserved
Instances, or serverless for variable workloads. "Least operational overhead" means
the solution requiring the least management effort --- this favors fully managed
services (RDS over EC2+PostgreSQL, Fargate over EC2, Lambda over containers, S3 over
EBS). Sometimes these overlap (serverless is both cheap and low-overhead for
variable workloads), but sometimes they conflict (Spot Instances are cheap but
require handling interruptions).

### Question 5
List 5 exam topics where candidates most commonly lose points.

**Answer:** (1) Confusing Multi-AZ (high availability, synchronous, not readable)
with Read Replicas (performance, asynchronous, readable). (2) Not understanding
when to use NLB versus ALB (NLB for TCP/UDP and static IPs, ALB for HTTP routing).
(3) Confusing Security Groups (stateful, instance level, allow only) with NACLs
(stateless, subnet level, allow and deny). (4) Not knowing which S3 storage class
to recommend for a given access pattern and retention requirement. (5) Choosing
IAM users with access keys instead of IAM roles for applications running on AWS
compute services.
