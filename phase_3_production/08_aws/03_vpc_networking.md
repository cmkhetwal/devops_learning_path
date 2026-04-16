# Lesson 03: VPC and Networking

## Why This Matters in DevOps

Networking is the invisible backbone of every cloud deployment. A misconfigured VPC
means your database is exposed to the internet. A missing route table entry means
your application cannot reach its dependencies. A poorly designed network means
you cannot scale, cannot isolate environments, and cannot meet compliance requirements.

In the DevOps world, network design is infrastructure code. You will define VPCs
in Terraform, automate security group rules in CI/CD pipelines, and troubleshoot
connectivity issues at 2 AM when production is down. Understanding VPC networking
is not optional --- it is the foundation everything else sits on.

Every Solutions Architect Associate question about high availability, security,
or cost optimization has a networking component. If you cannot design a VPC with
public and private subnets, route tables, and security groups, you cannot pass
the exam or do the job.

---

## Core Concepts

### What is a VPC?

A Virtual Private Cloud (VPC) is your own isolated network within AWS. Think of it
as your private data center in the cloud, with full control over IP ranges, subnets,
route tables, and gateways.

```
                         AWS REGION (us-east-1)
    +----------------------------------------------------------+
    |                       YOUR VPC                            |
    |                   CIDR: 10.0.0.0/16                       |
    |                   (65,536 IP addresses)                   |
    |                                                          |
    |   AZ: us-east-1a          AZ: us-east-1b                |
    |   +-------------------+   +-------------------+          |
    |   | Public Subnet     |   | Public Subnet     |          |
    |   | 10.0.1.0/24       |   | 10.0.2.0/24       |          |
    |   | (256 IPs)         |   | (256 IPs)         |          |
    |   +-------------------+   +-------------------+          |
    |                                                          |
    |   +-------------------+   +-------------------+          |
    |   | Private Subnet    |   | Private Subnet    |          |
    |   | 10.0.11.0/24      |   | 10.0.12.0/24      |          |
    |   | (256 IPs)         |   | (256 IPs)         |          |
    |   +-------------------+   +-------------------+          |
    |                                                          |
    |   +-------------------+   +-------------------+          |
    |   | DB Subnet         |   | DB Subnet         |          |
    |   | 10.0.21.0/24      |   | 10.0.22.0/24      |          |
    |   | (256 IPs)         |   | (256 IPs)         |          |
    |   +-------------------+   +-------------------+          |
    +----------------------------------------------------------+
```

### CIDR Notation

CIDR (Classless Inter-Domain Routing) defines the IP address range of your VPC:

| CIDR Block | Subnet Mask | Total IPs | Usable IPs |
|-----------|-------------|-----------|------------|
| 10.0.0.0/16 | 255.255.0.0 | 65,536 | 65,531 |
| 10.0.0.0/20 | 255.255.240.0 | 4,096 | 4,091 |
| 10.0.0.0/24 | 255.255.255.0 | 256 | 251 |
| 10.0.0.0/28 | 255.255.255.240 | 16 | 11 |

AWS reserves 5 IPs in every subnet:
- .0 = Network address
- .1 = VPC router
- .2 = DNS server
- .3 = Reserved for future use
- .255 = Broadcast (not supported in VPC but reserved)

### Internet Gateway and NAT Gateway

```
         INTERNET
            |
    +-------v--------+
    | Internet Gateway|  (Allows public subnet to reach internet)
    +-------+--------+
            |
    +-------v--------+       +-------------------+
    | Public Subnet   |       | Public Subnet     |
    | 10.0.1.0/24     |       | 10.0.2.0/24       |
    | [NAT Gateway]   |       | [Bastion Host]    |
    +-------+---------+       +-------------------+
            |
    +-------v--------+       +-------------------+
    | Private Subnet  |       | Private Subnet    |
    | 10.0.11.0/24    |       | 10.0.12.0/24      |
    | [App Servers]   |       | [App Servers]     |
    +-------+---------+       +-------------------+
            |
    +-------v--------+       +-------------------+
    | DB Subnet       |       | DB Subnet         |
    | 10.0.21.0/24    |       | 10.0.22.0/24      |
    | [RDS Database]  |       | [RDS Replica]     |
    +-----------------+       +-------------------+
```

**Internet Gateway (IGW)**: Allows resources in public subnets to communicate with
the internet. Horizontally scaled, redundant, no bandwidth constraints. Free.

**NAT Gateway**: Allows resources in private subnets to initiate outbound connections
to the internet (e.g., downloading updates) while preventing inbound connections from
the internet. Costs money (~$0.045/hr + data processing). Place in a public subnet.

### Route Tables

Every subnet is associated with a route table. The route table determines where
traffic is directed.

```
PUBLIC SUBNET ROUTE TABLE:
+-------------------+-------------------+
| Destination       | Target            |
+-------------------+-------------------+
| 10.0.0.0/16       | local             |  <-- Traffic within VPC
| 0.0.0.0/0         | igw-xxxxxxxx      |  <-- Everything else to Internet
+-------------------+-------------------+

PRIVATE SUBNET ROUTE TABLE:
+-------------------+-------------------+
| Destination       | Target            |
+-------------------+-------------------+
| 10.0.0.0/16       | local             |  <-- Traffic within VPC
| 0.0.0.0/0         | nat-xxxxxxxx      |  <-- Outbound via NAT Gateway
+-------------------+-------------------+

DB SUBNET ROUTE TABLE:
+-------------------+-------------------+
| Destination       | Target            |
+-------------------+-------------------+
| 10.0.0.0/16       | local             |  <-- Traffic within VPC only
+-------------------+-------------------+       (no internet access)
```

### Security Groups vs NACLs

| Feature | Security Group | NACL |
|---------|---------------|------|
| Level | Instance (ENI) | Subnet |
| State | Stateful | Stateless |
| Rules | Allow only | Allow and Deny |
| Evaluation | All rules evaluated | Rules evaluated in order |
| Default | Deny all inbound, allow all outbound | Allow all in/out |
| Return traffic | Automatic | Must explicitly allow |

```
STATEFUL (Security Group):
  Inbound rule: Allow TCP 443  -->  Response traffic automatically allowed

STATELESS (NACL):
  Inbound rule: Allow TCP 443  -->  MUST also add outbound rule for
                                    ephemeral ports (1024-65535)
```

### VPC Peering

Connects two VPCs so they can communicate using private IPs. Peering is non-transitive:
if VPC-A peers with VPC-B, and VPC-B peers with VPC-C, VPC-A cannot reach VPC-C
through VPC-B.

### VPC Endpoints

Allow private connections to AWS services without going through the internet:

- **Gateway Endpoints**: S3 and DynamoDB (free, uses route tables)
- **Interface Endpoints**: Most other services (uses PrivateLink, costs money)

### Transit Gateway

Connects multiple VPCs, VPN connections, and Direct Connect gateways through a
central hub. Solves the scaling problem of VPC peering (no more mesh topology).

---

## Step-by-Step Practical

### Build a Production VPC from Scratch

```bash
# Step 1: Create the VPC
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=production-vpc}]' \
    --query 'Vpc.VpcId' --output text)
echo "VPC ID: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames '{"Value": true}'

# Step 2: Create an Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=production-igw}]' \
    --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID

# Step 3: Create Subnets
# Public subnets
PUB_SUB_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1a}]' \
    --query 'Subnet.SubnetId' --output text)

PUB_SUB_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1b}]' \
    --query 'Subnet.SubnetId' --output text)

# Private subnets
PRIV_SUB_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.11.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-1a}]' \
    --query 'Subnet.SubnetId' --output text)

PRIV_SUB_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.12.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-1b}]' \
    --query 'Subnet.SubnetId' --output text)

# Enable auto-assign public IPs for public subnets
aws ec2 modify-subnet-attribute \
    --subnet-id $PUB_SUB_1 \
    --map-public-ip-on-launch

aws ec2 modify-subnet-attribute \
    --subnet-id $PUB_SUB_2 \
    --map-public-ip-on-launch

# Step 4: Create Route Tables
# Public route table
PUB_RT=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]' \
    --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route \
    --route-table-id $PUB_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate public subnets with public route table
aws ec2 associate-route-table --subnet-id $PUB_SUB_1 --route-table-id $PUB_RT
aws ec2 associate-route-table --subnet-id $PUB_SUB_2 --route-table-id $PUB_RT

# Step 5: Create NAT Gateway (in public subnet)
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc \
    --query 'AllocationId' --output text)

NAT_GW=$(aws ec2 create-nat-gateway \
    --subnet-id $PUB_SUB_1 \
    --allocation-id $EIP_ALLOC \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=production-nat}]' \
    --query 'NatGateway.NatGatewayId' --output text)

# Wait for NAT Gateway to become available
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW

# Private route table (with NAT)
PRIV_RT=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-rt}]' \
    --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route \
    --route-table-id $PRIV_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_GW

aws ec2 associate-route-table --subnet-id $PRIV_SUB_1 --route-table-id $PRIV_RT
aws ec2 associate-route-table --subnet-id $PRIV_SUB_2 --route-table-id $PRIV_RT

# Step 6: Create Security Groups
WEB_SG=$(aws ec2 create-security-group \
    --group-name web-sg \
    --description "Security group for web servers" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp --port 22 --cidr 203.0.113.0/24  # Your IP only

APP_SG=$(aws ec2 create-security-group \
    --group-name app-sg \
    --description "Security group for app servers" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

# App servers only accept traffic from web servers
aws ec2 authorize-security-group-ingress \
    --group-id $APP_SG \
    --protocol tcp --port 8080 \
    --source-group $WEB_SG

# Step 7: Verify the VPC
aws ec2 describe-vpcs --vpc-ids $VPC_ID --output table
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone,Tags[?Key==`Name`].Value|[0]]' \
    --output table
```

### Create a VPC Endpoint for S3

```bash
# Create a Gateway endpoint for S3 (free)
aws ec2 create-vpc-endpoint \
    --vpc-id $VPC_ID \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids $PRIV_RT \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=s3-endpoint}]'
```

---

## Exercises

### Exercise 1: Design a Three-Tier VPC
Create a VPC with public, private, and database subnets across two AZs. Include
an Internet Gateway, NAT Gateway, and proper route tables. Draw the architecture
diagram before building it.

### Exercise 2: Security Group Chains
Create a chain of security groups: ALB-SG (allows 80/443 from internet) ->
App-SG (allows 8080 from ALB-SG only) -> DB-SG (allows 5432 from App-SG only).
Verify that traffic flows correctly through the chain.

### Exercise 3: NACL Implementation
Create a NACL for the public subnet that blocks traffic from a specific IP range.
Remember to allow ephemeral ports for return traffic. Test that the NACL blocks
the expected traffic.

### Exercise 4: VPC Flow Logs
Enable VPC Flow Logs on your VPC and send them to CloudWatch Logs. Generate some
traffic, then query the flow logs to see accepted and rejected connections.

### Exercise 5: Multi-VPC Peering
Create two VPCs and establish a peering connection between them. Update route tables
in both VPCs. Launch an instance in each VPC and verify they can ping each other
using private IPs.

---

## Knowledge Check

### Question 1
What makes a subnet "public" versus "private"?

**Answer:** A public subnet has a route table entry that sends internet-bound traffic
(0.0.0.0/0) to an Internet Gateway. A private subnet either has no internet route
or routes internet-bound traffic through a NAT Gateway. Additionally, instances in
public subnets need a public or Elastic IP to communicate with the internet.

### Question 2
Why are Security Groups called "stateful" and NACLs called "stateless"?

**Answer:** Security Groups are stateful because they automatically allow return
traffic for any allowed inbound connection. If you allow inbound TCP 443, the
response traffic is automatically permitted. NACLs are stateless because each
direction (inbound and outbound) must be explicitly configured. If you allow
inbound TCP 443, you must also create an outbound rule allowing ephemeral ports
(1024-65535) for the return traffic.

### Question 3
When would you use a NAT Gateway versus an Internet Gateway?

**Answer:** Use an Internet Gateway when resources need to be directly reachable
from the internet (e.g., web servers in public subnets). Use a NAT Gateway when
private resources need to initiate outbound connections (e.g., downloading patches,
calling external APIs) but should not be reachable from the internet. The NAT Gateway
translates the private IP to a public IP for outbound traffic only.

### Question 4
What is the difference between a VPC Gateway Endpoint and an Interface Endpoint?

**Answer:** Gateway Endpoints are free, work only for S3 and DynamoDB, and use route
table entries to direct traffic. Interface Endpoints (powered by PrivateLink) work
with most AWS services, create an ENI in your subnet with a private IP, and cost
money (~$0.01/hr + data processing). Interface Endpoints can be accessed from
on-premises networks via VPN or Direct Connect; Gateway Endpoints cannot.

### Question 5
If VPC-A peers with VPC-B, and VPC-B peers with VPC-C, can VPC-A communicate with VPC-C?

**Answer:** No. VPC peering is non-transitive. VPC-A can only communicate with VPC-B,
and VPC-B can only communicate with VPC-C. For VPC-A to reach VPC-C, you need a
direct peering connection between them, or you should use AWS Transit Gateway, which
acts as a central hub for connecting multiple VPCs.
