# Pulumi Fundamentals

## Why This Matters in DevOps

Every DevOps engineer who has written complex Terraform knows the pain: workarounds for conditional logic, awkward `for_each` expressions, the inability to write unit tests, and HCL's limited type system. Pulumi eliminates these problems by letting you write infrastructure in real programming languages -- Python, TypeScript, Go, C#, or Java. This means you get IDE autocomplete, type checking, test frameworks, and the full power of a general-purpose language. If your team already writes Python or TypeScript, Pulumi removes an entire language (HCL) from your stack and lets engineers use skills they already have.

---

## Core Concepts

### What Is Pulumi?

Pulumi is an open-source IaC platform that uses general-purpose programming languages instead of domain-specific languages (DSLs). You write infrastructure definitions in Python, TypeScript, Go, C#, or Java, and Pulumi's engine translates them into cloud API calls.

```
Traditional IaC:                    Pulumi:
┌──────────┐                       ┌──────────┐
│   HCL    │                       │  Python  │
│  YAML    │                       │TypeScript│
│  JSON    │                       │   Go     │
└────┬─────┘                       └────┬─────┘
     │                                  │
     ▼                                  ▼
┌──────────┐                       ┌──────────┐
│ Terraform│                       │  Pulumi  │
│  Engine  │                       │  Engine  │
└────┬─────┘                       └────┬─────┘
     │                                  │
     ▼                                  ▼
┌──────────┐                       ┌──────────┐
│Cloud APIs│                       │Cloud APIs│
└──────────┘                       └──────────┘
```

### Pulumi vs Terraform

| Aspect | Terraform | Pulumi |
|---|---|---|
| Language | HCL (DSL) | Python, TypeScript, Go, C#, Java |
| Logic | Limited (`count`, `for_each`, `dynamic`) | Full language constructs |
| Testing | `terraform test` (limited) | pytest, Jest, Go test (full) |
| IDE Support | Basic HCL extensions | Full IntelliSense, type checking |
| State | State file (S3, Terraform Cloud) | Pulumi Cloud, S3, Azure Blob, local |
| Modularity | Modules (limited OOP) | Classes, packages, inheritance |
| Ecosystem | 3000+ providers | 150+ providers + Terraform bridge |
| Debugging | terraform console, logs | Standard debuggers (pdb, VS Code) |
| License | BSL 1.1 | Apache 2.0 |

### Pulumi Stack Concept

A **stack** is an instance of a Pulumi program -- typically one per environment. The same code deploys to different environments with different configurations.

```
Pulumi Program (Python code)
     │
     ├── Stack: dev        → deploys to us-east-1, t3.micro
     ├── Stack: staging    → deploys to us-east-1, t3.medium
     └── Stack: production → deploys to us-west-2, r6g.xlarge
```

Each stack has its own:
- Configuration values (`pulumi config set key value`)
- State (tracked independently)
- Outputs (exported values)

### State Management

Pulumi needs to track the mapping between your code and real cloud resources. State options:

| Backend | Description | Best For |
|---|---|---|
| Pulumi Cloud | Managed SaaS (free tier available) | Teams, collaboration |
| S3 + DynamoDB | Self-managed on AWS | AWS-native organizations |
| Azure Blob | Self-managed on Azure | Azure-native organizations |
| GCS | Self-managed on GCP | GCP-native organizations |
| Local file | `~/.pulumi` directory | Development, testing |

```bash
# Use Pulumi Cloud (default)
pulumi login

# Use S3 backend
pulumi login s3://my-pulumi-state-bucket

# Use local backend
pulumi login --local
```

### Pulumi CLI

```bash
# Create a new project
pulumi new aws-python          # Python + AWS template
pulumi new kubernetes-python   # Python + Kubernetes template

# Preview changes (like terraform plan)
pulumi preview

# Deploy changes (like terraform apply)
pulumi up

# Destroy all resources (like terraform destroy)
pulumi destroy

# View stack outputs
pulumi stack output

# Manage configuration
pulumi config set aws:region us-east-1
pulumi config set --secret dbPassword MySuperSecret

# Stack management
pulumi stack ls                 # List stacks
pulumi stack select production  # Switch stacks
pulumi stack export             # Export state
```

---

## Step-by-Step Practical

### Deploy AWS Infrastructure Using Python

**Step 1: Install Pulumi**

```bash
# Install Pulumi CLI
curl -fsSL https://get.pulumi.com | sh

# Verify
pulumi version
# v3.120.0

# Install AWS plugin (done automatically on first run)
pulumi plugin install resource aws v6.50.0
```

**Step 2: Create a New Project**

```bash
mkdir my-infra && cd my-infra
pulumi new aws-python --name my-infra --description "Production infrastructure"
```

This creates:
```
my-infra/
├── __main__.py      # Infrastructure code
├── Pulumi.yaml      # Project metadata
├── Pulumi.dev.yaml  # Stack-specific config
├── requirements.txt # Python dependencies
└── venv/            # Virtual environment
```

**Step 3: Configure the Stack**

```bash
# Set AWS region
pulumi config set aws:region us-east-1

# Set custom configuration values
pulumi config set environment dev
pulumi config set instanceType t3.micro
pulumi config set --secret dbPassword "SuperSecret123!"
```

**Step 4: Write Infrastructure Code**

```python
# __main__.py
"""Production-grade AWS infrastructure with Pulumi."""

import json
import pulumi
import pulumi_aws as aws

# Load configuration
config = pulumi.Config()
environment = config.require("environment")
instance_type = config.get("instanceType") or "t3.micro"
db_password = config.require_secret("dbPassword")

# --- Tagging Strategy ---
common_tags = {
    "Environment": environment,
    "ManagedBy": "pulumi",
    "Project": pulumi.get_project(),
    "Stack": pulumi.get_stack(),
}

# --- VPC ---
vpc = aws.ec2.Vpc("main-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={**common_tags, "Name": f"vpc-{environment}"},
)

# --- Subnets (2 AZs for high availability) ---
azs = ["us-east-1a", "us-east-1b"]
public_subnets = []
private_subnets = []

for i, az in enumerate(azs):
    public_subnet = aws.ec2.Subnet(f"public-{az}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{i * 2}.0/24",
        availability_zone=az,
        map_public_ip_on_launch=True,
        tags={**common_tags, "Name": f"public-{az}-{environment}"},
    )
    public_subnets.append(public_subnet)

    private_subnet = aws.ec2.Subnet(f"private-{az}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{i * 2 + 1}.0/24",
        availability_zone=az,
        tags={**common_tags, "Name": f"private-{az}-{environment}"},
    )
    private_subnets.append(private_subnet)

# --- Internet Gateway ---
igw = aws.ec2.InternetGateway("main-igw",
    vpc_id=vpc.id,
    tags={**common_tags, "Name": f"igw-{environment}"},
)

# --- Route Table ---
public_rt = aws.ec2.RouteTable("public-rt",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
    tags={**common_tags, "Name": f"public-rt-{environment}"},
)

for i, subnet in enumerate(public_subnets):
    aws.ec2.RouteTableAssociation(f"public-rta-{i}",
        subnet_id=subnet.id,
        route_table_id=public_rt.id,
    )

# --- Security Groups ---
web_sg = aws.ec2.SecurityGroup("web-sg",
    vpc_id=vpc.id,
    description="Allow HTTP/HTTPS inbound",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp", from_port=80, to_port=80,
            cidr_blocks=["0.0.0.0/0"],
            description="HTTP",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp", from_port=443, to_port=443,
            cidr_blocks=["0.0.0.0/0"],
            description="HTTPS",
        ),
    ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        protocol="-1", from_port=0, to_port=0,
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={**common_tags, "Name": f"web-sg-{environment}"},
)

db_sg = aws.ec2.SecurityGroup("db-sg",
    vpc_id=vpc.id,
    description="Allow PostgreSQL from web tier",
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        protocol="tcp", from_port=5432, to_port=5432,
        security_groups=[web_sg.id],
        description="PostgreSQL from web tier",
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        protocol="-1", from_port=0, to_port=0,
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={**common_tags, "Name": f"db-sg-{environment}"},
)

# --- RDS Database ---
db_subnet_group = aws.rds.SubnetGroup("db-subnets",
    subnet_ids=[s.id for s in private_subnets],
    tags=common_tags,
)

# Determine instance class based on environment
db_instance_class = {
    "dev": "db.t3.micro",
    "staging": "db.t3.medium",
    "production": "db.r6g.large",
}.get(environment, "db.t3.micro")

database = aws.rds.Instance("app-database",
    engine="postgres",
    engine_version="15.4",
    instance_class=db_instance_class,
    allocated_storage=20,
    storage_encrypted=True,
    db_name="appdb",
    username="dbadmin",
    password=db_password,
    db_subnet_group_name=db_subnet_group.name,
    vpc_security_group_ids=[db_sg.id],
    multi_az=(environment == "production"),
    backup_retention_period=30 if environment == "production" else 1,
    skip_final_snapshot=(environment != "production"),
    tags=common_tags,
)

# --- S3 Bucket for Application Assets ---
assets_bucket = aws.s3.BucketV2("app-assets",
    bucket=f"mycompany-{environment}-app-assets",
    tags=common_tags,
)

aws.s3.BucketVersioningV2("app-assets-versioning",
    bucket=assets_bucket.id,
    versioning_configuration=aws.s3.BucketVersioningV2VersioningConfigurationArgs(
        status="Enabled",
    ),
)

aws.s3.BucketServerSideEncryptionConfigurationV2("app-assets-encryption",
    bucket=assets_bucket.id,
    rules=[aws.s3.BucketServerSideEncryptionConfigurationV2RuleArgs(
        apply_server_side_encryption_by_default=
            aws.s3.BucketServerSideEncryptionConfigurationV2RuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm="aws:kms",
            ),
    )],
)

# --- Outputs ---
pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnet_ids", [s.id for s in public_subnets])
pulumi.export("private_subnet_ids", [s.id for s in private_subnets])
pulumi.export("database_endpoint", database.endpoint)
pulumi.export("database_port", database.port)
pulumi.export("assets_bucket_name", assets_bucket.bucket)
```

**Step 5: Preview and Deploy**

```bash
# Preview (like terraform plan)
pulumi preview
```

Expected output:
```
Previewing update (dev):
     Type                              Name              Plan
 +   pulumi:pulumi:Stack               my-infra-dev      create
 +   ├─ aws:ec2:Vpc                    main-vpc          create
 +   ├─ aws:ec2:Subnet                 public-us-east-1a create
 +   ├─ aws:ec2:Subnet                 public-us-east-1b create
 +   ├─ aws:ec2:Subnet                 private-us-east-1a create
 +   ├─ aws:ec2:Subnet                 private-us-east-1b create
 +   ├─ aws:ec2:InternetGateway        main-igw          create
 +   ├─ aws:ec2:RouteTable             public-rt         create
 +   ├─ aws:ec2:RouteTableAssociation  public-rta-0      create
 +   ├─ aws:ec2:RouteTableAssociation  public-rta-1      create
 +   ├─ aws:ec2:SecurityGroup          web-sg            create
 +   ├─ aws:ec2:SecurityGroup          db-sg             create
 +   ├─ aws:rds:SubnetGroup            db-subnets        create
 +   ├─ aws:rds:Instance               app-database      create
 +   ├─ aws:s3:BucketV2                app-assets        create
 +   ├─ aws:s3:BucketVersioningV2      app-assets-ver    create
 +   └─ aws:s3:BucketServerSide...     app-assets-enc    create

Resources:
    + 17 to create
```

```bash
# Deploy
pulumi up --yes

# View outputs
pulumi stack output
```

Expected output:
```
Current stack outputs (6):
    OUTPUT               VALUE
    vpc_id               vpc-0abc123def456789
    public_subnet_ids    ["subnet-0aaa111","subnet-0bbb222"]
    private_subnet_ids   ["subnet-0ccc333","subnet-0ddd444"]
    database_endpoint    app-database-abc123.cdefghij.us-east-1.rds.amazonaws.com
    database_port        5432
    assets_bucket_name   mycompany-dev-app-assets
```

**Step 6: Create a Production Stack**

```bash
# Create new stack
pulumi stack init production

# Configure it differently
pulumi config set aws:region us-west-2
pulumi config set environment production
pulumi config set instanceType r6g.xlarge
pulumi config set --secret dbPassword "ProdSuperSecret456!"

# Preview production deployment
pulumi preview
# Same code, different configuration = different infrastructure
```

---

## Exercises

1. **First Pulumi Project**: Install Pulumi and create a project that provisions an S3 bucket with versioning, encryption, and a lifecycle rule. Deploy to a `dev` stack, then create a `production` stack with different configuration.

2. **Dynamic Infrastructure**: Write a Pulumi program that reads a JSON config file containing a list of S3 buckets to create (name, versioning, encryption settings) and provisions all of them using a loop. Add/remove entries from JSON and run `pulumi up` to see the diff.

3. **Conditional Logic**: Create a Pulumi program where the environment parameter controls: instance sizes, multi-AZ settings, backup retention, and deletion protection. Use Python if/else statements (something impossible in HCL without workarounds).

4. **Stack Outputs**: Create two Pulumi stacks -- one for networking (VPC, subnets) and one for compute (EC2 instances). Use stack references to pass VPC ID from the networking stack to the compute stack.

---

## Knowledge Check

**Q1: What is the main advantage of using a real programming language for IaC instead of HCL?**

<details>
<summary>Answer</summary>

Real programming languages provide: (1) Full logic constructs -- if/else, loops, list comprehensions, error handling, (2) Type safety -- IDE autocomplete and compile-time error detection, (3) Testability -- use pytest, Jest, or Go's testing framework to unit test infrastructure code, (4) Abstraction -- use classes, interfaces, and packages to create reusable components, (5) Ecosystem -- access to all language libraries (HTTP clients, parsers, templating engines), (6) Familiar tooling -- standard debuggers, linters, and formatters.
</details>

**Q2: How do Pulumi stacks differ from Terraform workspaces?**

<details>
<summary>Answer</summary>

Pulumi stacks are first-class concepts with independent configuration and state. Each stack has its own `Pulumi.<stack>.yaml` config file, its own state, and its own outputs. Stacks can reference other stacks' outputs via StackReference. Terraform workspaces share the same configuration and backend but isolate state -- they are often considered limited because you cannot have different variable values per workspace without external tooling (like tfvars files). Pulumi stacks are closer to separate Terraform root modules with separate tfvars files.
</details>

**Q3: How does Pulumi handle secrets differently from Terraform?**

<details>
<summary>Answer</summary>

Pulumi encrypts secrets in state by default. When you use `pulumi config set --secret`, the value is encrypted before being stored. In state, secret values are encrypted and never stored in plaintext. In code, secrets are wrapped in `Output[T]` types that prevent accidental logging. Pulumi Cloud uses per-stack encryption keys. Self-managed backends can use passphrase-based or cloud KMS encryption. Terraform, by contrast, stores all values in state as plaintext JSON, requiring you to encrypt the entire state file at rest in S3 or similar.
</details>

**Q4: What is `pulumi preview` and how does it compare to `terraform plan`?**

<details>
<summary>Answer</summary>

`pulumi preview` executes your program, computes the desired state, compares it with the current state, and shows what changes would be made -- without actually making them. It is functionally equivalent to `terraform plan`. The key differences: (1) Pulumi preview runs your actual code (Python/TypeScript), so syntax errors or runtime exceptions are caught here, (2) Pulumi shows a resource tree that includes the parent-child hierarchy, (3) Pulumi preview can be run with `--diff` to show detailed property-level changes similar to `terraform plan`'s detailed output.
</details>
