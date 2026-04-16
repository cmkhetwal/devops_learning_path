# Lesson 06: AWS Database Services

## Why This Matters in DevOps

Databases are the heart of every application. As a DevOps engineer, you are responsible
for provisioning, scaling, backing up, and monitoring databases --- but you are also
responsible for choosing the right database for each workload. A bad choice here is
expensive and painful to reverse.

AWS offers over 15 purpose-built database services. The SA Associate exam tests your
ability to recommend the right database for a given scenario. In production, your
choices directly affect application performance, cost, and reliability. Running a
relational database for time-series data wastes money. Using DynamoDB for complex
JOIN-heavy queries creates architectural nightmares.

This lesson covers the databases you will encounter most frequently: RDS for relational
workloads, Aurora for high-performance relational, DynamoDB for NoSQL at scale, and
ElastiCache for in-memory caching.

---

## Core Concepts

### Choosing the Right Database

```
DECISION TREE:

  Is your data structured with relationships?
      |
      +-- YES --> Do you need MySQL/PostgreSQL compatibility?
      |               |
      |               +-- YES --> Is performance critical?
      |               |              |
      |               |              +-- YES --> Aurora
      |               |              +-- NO  --> RDS
      |               |
      |               +-- NO --> Need Oracle/SQL Server? --> RDS
      |
      +-- NO --> Is it key-value or document?
                    |
                    +-- YES --> Need single-digit ms latency at any scale?
                    |              |
                    |              +-- YES --> DynamoDB
                    |              +-- NO  --> DocumentDB (MongoDB compat)
                    |
                    +-- NO --> Is it graph data? --> Neptune
                          --> Is it time-series? --> Timestream
                          --> Is it ledger? --> QLDB
                          --> Is it in-memory cache? --> ElastiCache
```

### RDS (Relational Database Service)

RDS is a managed relational database service that handles patching, backups,
and failover so you can focus on your application.

```
RDS ARCHITECTURE:

  +---------------------------------------------+
  |  RDS Instance                                |
  |  +-----------+  +------------------------+  |
  |  | DB Engine |  | EBS Storage            |  |
  |  | (Postgres,|  | (gp3, io2, magnetic)   |  |
  |  |  MySQL,   |  | Automated backups      |  |
  |  |  MariaDB, |  | to S3 (retention 0-35  |  |
  |  |  Oracle,  |  | days)                  |  |
  |  |  SQL Srv) |  +------------------------+  |
  |  +-----------+                               |
  +---------------------------------------------+

  Supported Engines:
  - PostgreSQL, MySQL, MariaDB (open source)
  - Oracle, SQL Server (commercial, bring your own license or included)
```

### Multi-AZ vs Read Replicas

```
MULTI-AZ (High Availability):

  AZ-A                     AZ-B
  +-----------+            +-----------+
  | PRIMARY   | --sync---> | STANDBY   |
  | (read +   |  repl.     | (no read  |
  |  write)   |            |  or write)|
  +-----------+            +-----------+
       |                        |
       +-- Automatic failover --+
           (DNS switches,
            ~60-120 seconds)

  - Synchronous replication
  - Same region, different AZ
  - Standby is NOT readable
  - Automatic failover on failure
  - Slight latency increase due to sync writes


READ REPLICAS (Performance):

  +-----------+
  | PRIMARY   | --async--> Read Replica 1 (same region)
  | (write)   | --async--> Read Replica 2 (same region)
  +-----------+ --async--> Read Replica 3 (cross-region)
                                  ^
                                  |
                            Application reads
                            are distributed here

  - Asynchronous replication
  - Up to 15 read replicas (Aurora) or 5 (RDS)
  - Can be in different regions (cross-region)
  - Replicas ARE readable
  - Can be promoted to standalone DB
  - Replication is free within same region
```

### Aurora

Aurora is Amazon's cloud-native relational database, compatible with MySQL and
PostgreSQL but with significant performance and availability improvements.

```
AURORA ARCHITECTURE:

  +---------+    +---------+    +---------+
  | Writer  |    | Reader  |    | Reader  |
  | Instance|    | Instance|    | Instance|
  +----+----+    +----+----+    +----+----+
       |              |              |
  +----v--------------v--------------v----+
  |        SHARED CLUSTER STORAGE         |
  |    (auto-scales 10GB to 128TB)        |
  |    (6 copies across 3 AZs)           |
  |    (self-healing, continuous backup)  |
  +---------------------------------------+

  Key advantages over standard RDS:
  - 5x MySQL, 3x PostgreSQL performance
  - Storage auto-scales (no manual provisioning)
  - 6 copies of data across 3 AZs
  - Continuous backup to S3 (no performance impact)
  - Up to 15 read replicas with <10ms replica lag
  - Aurora Serverless: auto-scales compute capacity
```

### DynamoDB

DynamoDB is a fully managed NoSQL key-value and document database that delivers
single-digit millisecond performance at any scale.

```
DYNAMODB DATA MODEL:

  TABLE: Orders
  +------------------------------------------------------------------+
  | Partition Key | Sort Key      | Attributes                       |
  | (OrderId)     | (Timestamp)   |                                  |
  +------------------------------------------------------------------+
  | ORD-001       | 2024-01-15T10 | {customer: "Alice", total: 99}   |
  | ORD-001       | 2024-01-16T14 | {customer: "Alice", total: 45}   |
  | ORD-002       | 2024-01-15T09 | {customer: "Bob", total: 150}    |
  +------------------------------------------------------------------+

  Access Patterns:
  - Get by Partition Key:      O(1) -- instant lookup
  - Query by PK + Sort Key:   O(log n) -- range queries
  - Scan entire table:        O(n) -- EXPENSIVE, avoid in production

CAPACITY MODES:
  - On-Demand: Pay per request, auto-scales, no planning needed
  - Provisioned: Set RCU/WCU, predictable cost, auto-scaling available
    1 RCU = 1 strongly consistent read/sec (4 KB)
    1 WCU = 1 write/sec (1 KB)
```

**DynamoDB Features:**
- **Global Tables**: Multi-region, multi-active replication
- **DynamoDB Streams**: Capture changes (like CDC) for event-driven architectures
- **DAX**: In-memory cache for DynamoDB (microsecond reads)
- **TTL**: Automatically delete expired items

### ElastiCache

```
ELASTICACHE ARCHITECTURE:

  Application --> ElastiCache (check cache first)
       |              |
       |         HIT: return cached data (microseconds)
       |         MISS: query database, store result in cache
       |              |
       +--- Database (only on cache miss)

  REDIS vs MEMCACHED:
  +-------------------+------------------+-------------------+
  | Feature           | Redis            | Memcached         |
  +-------------------+------------------+-------------------+
  | Data structures   | Strings, lists,  | Strings only      |
  |                   | sets, hashes,    |                   |
  |                   | sorted sets      |                   |
  | Persistence       | Yes (snapshots)  | No                |
  | Replication        | Yes (Multi-AZ)   | No                |
  | Pub/Sub           | Yes              | No                |
  | Clustering        | Yes              | Yes               |
  | Use case          | Sessions, leaderb| Simple caching    |
  |                   | queues, geo      |                   |
  +-------------------+------------------+-------------------+

  ALMOST ALWAYS CHOOSE REDIS (unless you need pure simplicity)
```

---

## Step-by-Step Practical

### Deploy RDS PostgreSQL with Read Replica

```bash
# Step 1: Create a DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name production-db-subnets \
    --db-subnet-group-description "Production database subnets" \
    --subnet-ids $PRIV_SUB_1 $PRIV_SUB_2

# Step 2: Create a security group for the database
DB_SG=$(aws ec2 create-security-group \
    --group-name db-sg \
    --description "Database security group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

# Allow PostgreSQL from app security group only
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG \
    --protocol tcp --port 5432 \
    --source-group $APP_SG

# Step 3: Create the primary RDS instance
aws rds create-db-instance \
    --db-instance-identifier production-postgres \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.4 \
    --master-username dbadmin \
    --master-user-password 'SecureP@ssw0rd2024!' \
    --allocated-storage 100 \
    --storage-type gp3 \
    --storage-encrypted \
    --kms-key-id alias/aws/rds \
    --db-subnet-group-name production-db-subnets \
    --vpc-security-group-ids $DB_SG \
    --multi-az \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "Mon:04:00-Mon:05:00" \
    --auto-minor-version-upgrade \
    --deletion-protection \
    --tags Key=Environment,Value=production Key=Team,Value=devops

# Expected output includes DBInstanceIdentifier, Status: "creating"

# Step 4: Wait for the instance to be available (takes 5-15 minutes)
aws rds wait db-instance-available \
    --db-instance-identifier production-postgres
echo "Primary database is ready"

# Step 5: Get the endpoint
aws rds describe-db-instances \
    --db-instance-identifier production-postgres \
    --query 'DBInstances[0].Endpoint.[Address,Port]' \
    --output table
# Expected:
# +------------------------------------------------------------+
# | production-postgres.xxxx.us-east-1.rds.amazonaws.com | 5432|
# +------------------------------------------------------------+

# Step 6: Create a read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier production-postgres-replica \
    --source-db-instance-identifier production-postgres \
    --db-instance-class db.t3.medium \
    --availability-zone us-east-1b

# Wait for the replica
aws rds wait db-instance-available \
    --db-instance-identifier production-postgres-replica

# Step 7: Verify replication status
aws rds describe-db-instances \
    --db-instance-identifier production-postgres-replica \
    --query 'DBInstances[0].[ReadReplicaSourceDBInstanceIdentifier,StatusInfos]' \
    --output table
```

### Connect to the Database

```bash
# Install PostgreSQL client
sudo dnf install -y postgresql15

# Connect to primary (read/write)
psql -h production-postgres.xxxx.us-east-1.rds.amazonaws.com \
     -U dbadmin -d postgres

# In psql:
CREATE DATABASE myapp;
\c myapp
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

# Connect to read replica (read only)
psql -h production-postgres-replica.xxxx.us-east-1.rds.amazonaws.com \
     -U dbadmin -d myapp
SELECT * FROM users;  -- works
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');  -- FAILS (read-only)
```

### Create a DynamoDB Table

```bash
# Create a table with on-demand capacity
aws dynamodb create-table \
    --table-name Sessions \
    --attribute-definitions \
        AttributeName=SessionId,AttributeType=S \
        AttributeName=UserId,AttributeType=S \
    --key-schema \
        AttributeName=SessionId,KeyType=HASH \
    --global-secondary-indexes \
        'IndexName=UserIndex,KeySchema=[{AttributeName=UserId,KeyType=HASH}],Projection={ProjectionType=ALL}' \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=production

# Wait for table to be active
aws dynamodb wait table-exists --table-name Sessions

# Insert an item
aws dynamodb put-item \
    --table-name Sessions \
    --item '{
        "SessionId": {"S": "sess-abc123"},
        "UserId": {"S": "user-001"},
        "CreatedAt": {"N": "1705334400"},
        "TTL": {"N": "1705420800"},
        "Data": {"M": {"role": {"S": "admin"}, "ip": {"S": "10.0.1.50"}}}
    }'

# Query by session ID
aws dynamodb get-item \
    --table-name Sessions \
    --key '{"SessionId": {"S": "sess-abc123"}}' \
    --output table

# Query by user ID using GSI
aws dynamodb query \
    --table-name Sessions \
    --index-name UserIndex \
    --key-condition-expression "UserId = :uid" \
    --expression-attribute-values '{":uid": {"S": "user-001"}}' \
    --output table

# Enable TTL (auto-delete expired items)
aws dynamodb update-time-to-live \
    --table-name Sessions \
    --time-to-live-specification "Enabled=true,AttributeName=TTL"
```

---

## Exercises

### Exercise 1: Database Selection
For each scenario, recommend the best AWS database service and justify your choice:
a) E-commerce product catalog with complex queries and transactions
b) IoT sensor data storing millions of readings per second
c) Social network with friend-of-friend graph queries
d) User session store needing sub-millisecond reads
e) Financial ledger requiring immutable audit trail

### Exercise 2: RDS High Availability
Deploy an RDS MySQL instance with Multi-AZ enabled. Simulate a failover using
`aws rds reboot-db-instance --force-failover`. Measure the failover time by
continuously pinging the endpoint. Document the failover behavior.

### Exercise 3: DynamoDB Capacity Planning
Create a DynamoDB table with provisioned capacity. Use a script to write 1000 items
and read them back. Enable auto-scaling. Monitor consumed capacity using CloudWatch
metrics. Switch to on-demand mode and compare costs.

### Exercise 4: ElastiCache Setup
Deploy a Redis ElastiCache cluster with a primary and replica node. Write a Python
script that checks the cache before querying RDS, implementing the cache-aside pattern.
Measure the latency difference between cache hits and database queries.

### Exercise 5: Backup and Restore
Create an automated backup of your RDS instance. Then perform a point-in-time
recovery to create a new instance restored to a specific timestamp. Verify the
restored data matches expectations. Document the RPO (Recovery Point Objective).

---

## Knowledge Check

### Question 1
When would you choose Aurora over standard RDS?

**Answer:** Choose Aurora when you need: (1) higher performance (5x MySQL, 3x
PostgreSQL), (2) storage that auto-scales up to 128 TB without downtime, (3) more
than 5 read replicas (Aurora supports up to 15), (4) faster failover (Aurora
typically fails over in under 30 seconds vs 60-120 seconds for RDS Multi-AZ),
(5) continuous backup to S3 without performance impact. Aurora costs about 20%
more than standard RDS but the operational benefits often justify the cost.

### Question 2
What is the difference between Multi-AZ and Read Replicas?

**Answer:** Multi-AZ is a high availability feature: it maintains a synchronous
standby in another AZ for automatic failover. The standby is not readable. Read
Replicas are a performance feature: they use asynchronous replication to create
readable copies of the database, distributing read traffic. They can be in the same
region, cross-region, or promoted to standalone databases. You can use both together:
Multi-AZ for HA + Read Replicas for read scaling.

### Question 3
When should you use DynamoDB versus RDS?

**Answer:** Use DynamoDB when: you need single-digit millisecond latency at any
scale, your access patterns are known and based on key lookups, you need
near-infinite horizontal scaling, or you want a fully serverless database with
zero management. Use RDS when: you need complex queries with JOINs, your data
has many relationships, you need ACID transactions across multiple tables, or
you are migrating an existing relational database.

### Question 4
What is DynamoDB DAX and when would you use it?

**Answer:** DAX (DynamoDB Accelerator) is a fully managed in-memory cache for
DynamoDB that reduces read latency from single-digit milliseconds to microseconds.
Use it for read-heavy workloads where even DynamoDB's native latency is too high
(e.g., real-time bidding, gaming leaderboards). DAX is API-compatible with
DynamoDB, so you only need to change the endpoint in your application code.

### Question 5
How does RDS handle automated backups?

**Answer:** RDS takes daily snapshots during the backup window and continuously
captures transaction logs. This enables point-in-time recovery to any second within
the retention period (1-35 days). Backups are stored in S3 (managed by AWS, not
visible in your S3 console). Automated backups are free up to the size of the
provisioned storage. Manual snapshots persist until you explicitly delete them.
Restoring always creates a new instance (not an in-place restore).
