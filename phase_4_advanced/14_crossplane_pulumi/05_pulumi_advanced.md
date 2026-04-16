# Pulumi Advanced

## Why This Matters in DevOps

Real-world infrastructure is not a single flat file. Production environments have shared networking, independent application stacks, reusable patterns, and automated testing requirements. Pulumi's advanced features -- component resources, stack references, testing, and the Automation API -- let you treat infrastructure like professional software: modular, tested, and embeddable. These capabilities are why organizations choose Pulumi for complex, multi-team environments where infrastructure code quality matters as much as application code quality.

---

## Core Concepts

### Component Resources (Reusable Abstractions)

A ComponentResource groups multiple resources into a single reusable unit -- similar to a Terraform module but with the full power of object-oriented programming.

```python
import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource, ResourceOptions


class SecureWebApp(ComponentResource):
    """A reusable component that creates a load-balanced, secure web application."""

    def __init__(self, name: str, args: dict, opts: ResourceOptions = None):
        super().__init__("mycompany:webapp:SecureWebApp", name, {}, opts)

        environment = args.get("environment", "dev")
        instance_count = args.get("instance_count", 2)
        instance_type = args.get("instance_type", "t3.micro")
        vpc_id = args["vpc_id"]
        subnet_ids = args["subnet_ids"]

        # Security Group
        self.sg = aws.ec2.SecurityGroup(f"{name}-sg",
            vpc_id=vpc_id,
            description=f"Security group for {name}",
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp", from_port=80, to_port=80,
                    cidr_blocks=["0.0.0.0/0"],
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp", from_port=443, to_port=443,
                    cidr_blocks=["0.0.0.0/0"],
                ),
            ],
            egress=[aws.ec2.SecurityGroupEgressArgs(
                protocol="-1", from_port=0, to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            )],
            tags={"Name": f"{name}-sg", "Environment": environment},
            opts=ResourceOptions(parent=self),
        )

        # Application Load Balancer
        self.alb = aws.lb.LoadBalancer(f"{name}-alb",
            internal=False,
            load_balancer_type="application",
            security_groups=[self.sg.id],
            subnets=subnet_ids,
            tags={"Name": f"{name}-alb", "Environment": environment},
            opts=ResourceOptions(parent=self),
        )

        # Target Group
        self.tg = aws.lb.TargetGroup(f"{name}-tg",
            port=80,
            protocol="HTTP",
            vpc_id=vpc_id,
            target_type="instance",
            health_check=aws.lb.TargetGroupHealthCheckArgs(
                path="/health",
                healthy_threshold=3,
                unhealthy_threshold=3,
                interval=30,
            ),
            tags={"Name": f"{name}-tg"},
            opts=ResourceOptions(parent=self),
        )

        # Listener
        self.listener = aws.lb.Listener(f"{name}-listener",
            load_balancer_arn=self.alb.arn,
            port=80,
            protocol="HTTP",
            default_actions=[aws.lb.ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=self.tg.arn,
            )],
            opts=ResourceOptions(parent=self),
        )

        # EC2 Instances
        self.instances = []
        for i in range(instance_count):
            instance = aws.ec2.Instance(f"{name}-instance-{i}",
                ami="ami-0c55b159cbfafe1f0",
                instance_type=instance_type,
                subnet_id=subnet_ids[i % len(subnet_ids)],
                vpc_security_group_ids=[self.sg.id],
                tags={
                    "Name": f"{name}-{i}",
                    "Environment": environment,
                },
                opts=ResourceOptions(parent=self),
            )
            self.instances.append(instance)

            aws.lb.TargetGroupAttachment(f"{name}-tga-{i}",
                target_group_arn=self.tg.arn,
                target_id=instance.id,
                port=80,
                opts=ResourceOptions(parent=self),
            )

        # Register outputs
        self.register_outputs({
            "url": self.alb.dns_name,
            "security_group_id": self.sg.id,
            "instance_ids": [inst.id for inst in self.instances],
        })

        # Public properties
        self.url = self.alb.dns_name
```

Usage:

```python
# __main__.py
from secure_webapp import SecureWebApp

app = SecureWebApp("orders-service", {
    "environment": "production",
    "instance_count": 3,
    "instance_type": "t3.medium",
    "vpc_id": vpc.id,
    "subnet_ids": [s.id for s in public_subnets],
})

pulumi.export("app_url", app.url)
```

### Stack References (Cross-Stack Dependencies)

Stack references let one stack consume outputs from another -- essential for separating concerns.

```
┌────────────────┐     StackReference     ┌────────────────┐
│  Network Stack │ ──────────────────────► │  App Stack     │
│                │                         │                │
│  Outputs:      │                         │  Reads:        │
│  - vpc_id      │                         │  - vpc_id      │
│  - subnet_ids  │                         │  - subnet_ids  │
│  - sg_ids      │                         │  - sg_ids      │
└────────────────┘                         └────────────────┘
```

**Network stack (producer):**

```python
# network/__main__.py
import pulumi
import pulumi_aws as aws

vpc = aws.ec2.Vpc("shared-vpc", cidr_block="10.0.0.0/16")

subnets = []
for i, az in enumerate(["us-east-1a", "us-east-1b"]):
    subnet = aws.ec2.Subnet(f"subnet-{az}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{i}.0/24",
        availability_zone=az,
    )
    subnets.append(subnet)

# Export values for other stacks
pulumi.export("vpc_id", vpc.id)
pulumi.export("subnet_ids", [s.id for s in subnets])
```

**App stack (consumer):**

```python
# app/__main__.py
import pulumi
from pulumi import StackReference

# Reference the network stack
network = StackReference("myorg/network/production")

# Read outputs from the network stack
vpc_id = network.get_output("vpc_id")
subnet_ids = network.get_output("subnet_ids")

# Use them in this stack
app = SecureWebApp("api-service", {
    "vpc_id": vpc_id,
    "subnet_ids": subnet_ids,
    "instance_count": 2,
})
```

### Testing Infrastructure Code

One of Pulumi's greatest strengths is testability.

**Unit Tests (test resource properties without deploying):**

```python
# test_infra.py
import unittest
import pulumi


class MyMocks(pulumi.runtime.Mocks):
    """Mock the Pulumi engine for unit testing."""

    def new_resource(self, args):
        outputs = args.inputs
        if args.typ == "aws:ec2/instance:Instance":
            outputs = {**args.inputs, "publicIp": "203.0.113.1", "publicDns": "ec2-203.compute.amazonaws.com"}
        return [args.name + "_id", outputs]

    def call(self, args):
        return {}


pulumi.runtime.set_mocks(MyMocks())

# Import AFTER setting mocks
from infra import database, web_sg, vpc


class TestInfrastructure(unittest.TestCase):

    @pulumi.runtime.test
    def test_database_not_publicly_accessible(self):
        """RDS instances should never be publicly accessible."""
        def check(publicly_accessible):
            self.assertFalse(
                publicly_accessible,
                "Database must not be publicly accessible"
            )
        database.publicly_accessible.apply(check)

    @pulumi.runtime.test
    def test_database_encrypted(self):
        """RDS instances must have storage encryption enabled."""
        def check(encrypted):
            self.assertTrue(encrypted, "Database storage must be encrypted")
        database.storage_encrypted.apply(check)

    @pulumi.runtime.test
    def test_security_group_no_unrestricted_ssh(self):
        """Security groups should not allow SSH from 0.0.0.0/0."""
        def check(ingress):
            for rule in ingress:
                if rule["from_port"] == 22:
                    self.assertNotIn(
                        "0.0.0.0/0",
                        rule.get("cidr_blocks", []),
                        "SSH must not be open to the world"
                    )
        web_sg.ingress.apply(check)

    @pulumi.runtime.test
    def test_vpc_cidr_is_private(self):
        """VPC CIDR must be in private range."""
        def check(cidr):
            self.assertTrue(
                cidr.startswith("10.") or cidr.startswith("172.") or cidr.startswith("192.168."),
                f"VPC CIDR {cidr} is not in private range"
            )
        vpc.cidr_block.apply(check)


if __name__ == "__main__":
    unittest.main()
```

```bash
# Run unit tests
python -m pytest test_infra.py -v
```

Expected output:
```
test_infra.py::TestInfrastructure::test_database_not_publicly_accessible PASSED
test_infra.py::TestInfrastructure::test_database_encrypted PASSED
test_infra.py::TestInfrastructure::test_security_group_no_unrestricted_ssh PASSED
test_infra.py::TestInfrastructure::test_vpc_cidr_is_private PASSED

4 passed in 0.5s
```

**Integration Tests (deploy to a real environment and verify):**

```python
# test_integration.py
import subprocess
import json
import pytest


@pytest.fixture(scope="module")
def stack_outputs():
    """Deploy the stack and return outputs."""
    # Deploy
    subprocess.run(["pulumi", "up", "--yes", "--stack", "test"], check=True)

    # Get outputs
    result = subprocess.run(
        ["pulumi", "stack", "output", "--json", "--stack", "test"],
        capture_output=True, text=True, check=True
    )
    yield json.loads(result.stdout)

    # Cleanup
    subprocess.run(["pulumi", "destroy", "--yes", "--stack", "test"])


def test_bucket_exists(stack_outputs):
    """Verify the S3 bucket was actually created."""
    import boto3
    s3 = boto3.client("s3")
    bucket_name = stack_outputs["assets_bucket_name"]
    response = s3.head_bucket(Bucket=bucket_name)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_database_reachable(stack_outputs):
    """Verify the database endpoint is reachable."""
    import socket
    endpoint = stack_outputs["database_endpoint"]
    host = endpoint.split(":")[0]
    port = int(stack_outputs["database_port"])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    assert result == 0, f"Cannot reach database at {host}:{port}"
```

### Pulumi Automation API

The Automation API lets you embed Pulumi inside your own applications -- build custom CLIs, web portals, or self-service platforms.

```python
# self_service_provisioner.py
"""Self-service infrastructure provisioning using Pulumi Automation API."""

import pulumi
import pulumi_aws as aws
from pulumi import automation as auto


def create_s3_program(bucket_name: str, environment: str):
    """A Pulumi program factory -- returns a function that defines infrastructure."""
    def pulumi_program():
        bucket = aws.s3.BucketV2("app-bucket",
            bucket=bucket_name,
            tags={
                "Environment": environment,
                "ManagedBy": "automation-api",
                "RequestedBy": "self-service-portal",
            },
        )

        aws.s3.BucketVersioningV2("bucket-versioning",
            bucket=bucket.id,
            versioning_configuration=aws.s3.BucketVersioningV2VersioningConfigurationArgs(
                status="Enabled",
            ),
        )

        pulumi.export("bucket_name", bucket.bucket)
        pulumi.export("bucket_arn", bucket.arn)

    return pulumi_program


def provision_bucket(team: str, project: str, environment: str):
    """Provision an S3 bucket for a team -- callable from a web API."""
    bucket_name = f"{team}-{project}-{environment}"
    stack_name = f"{team}-{project}-{environment}"

    # Create or select a stack
    stack = auto.create_or_select_stack(
        stack_name=stack_name,
        project_name="self-service-buckets",
        program=create_s3_program(bucket_name, environment),
    )

    # Set configuration
    stack.set_config("aws:region", auto.ConfigValue(value="us-east-1"))

    # Deploy
    print(f"Provisioning bucket for {team}/{project}/{environment}...")
    result = stack.up(on_output=print)

    return {
        "bucket_name": result.outputs["bucket_name"].value,
        "bucket_arn": result.outputs["bucket_arn"].value,
    }


def destroy_bucket(team: str, project: str, environment: str):
    """Destroy the infrastructure -- callable from a web API."""
    stack_name = f"{team}-{project}-{environment}"

    stack = auto.select_stack(
        stack_name=stack_name,
        project_name="self-service-buckets",
        program=create_s3_program("", ""),
    )

    stack.destroy(on_output=print)
    stack.workspace.remove_stack(stack_name)


# Example usage from a Flask/FastAPI endpoint
if __name__ == "__main__":
    result = provision_bucket("team-orders", "data-lake", "dev")
    print(f"Provisioned: {result}")
```

```bash
python self_service_provisioner.py
```

Expected output:
```
Provisioning bucket for team-orders/data-lake/dev...
Updating (team-orders-data-lake-dev):
     Type                              Name                        Status
 +   pulumi:pulumi:Stack               self-service-buckets        created
 +   ├─ aws:s3:BucketV2                app-bucket                  created
 +   └─ aws:s3:BucketVersioningV2      bucket-versioning           created
Resources:
    + 3 created
Provisioned: {'bucket_name': 'team-orders-data-lake-dev', 'bucket_arn': 'arn:aws:s3:::team-orders-data-lake-dev'}
```

---

## Step-by-Step Practical

### Build Reusable Infrastructure Components in Python

**Step 1: Create a Component Library**

```bash
mkdir -p infra-components/components
touch infra-components/components/__init__.py
```

```python
# infra-components/components/database.py
"""Reusable database component with security best practices."""

import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource, ResourceOptions, Output
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseArgs:
    """Arguments for the Database component."""
    engine: str = "postgres"
    engine_version: str = "15.4"
    instance_class: str = "db.t3.micro"
    allocated_storage: int = 20
    db_name: str = "appdb"
    username: str = "dbadmin"
    vpc_id: Output = None
    subnet_ids: list = None
    allowed_security_groups: list = None
    multi_az: bool = False
    backup_retention_days: int = 7
    deletion_protection: bool = False
    environment: str = "dev"


class Database(ComponentResource):
    """A production-ready database with security group, subnet group, and monitoring."""

    def __init__(self, name: str, args: DatabaseArgs, opts: ResourceOptions = None):
        super().__init__("mycompany:database:Database", name, {}, opts)

        child_opts = ResourceOptions(parent=self)

        # Port mapping
        port_map = {"postgres": 5432, "mysql": 3306, "mariadb": 3306}
        db_port = port_map.get(args.engine, 5432)

        # Security Group
        self.security_group = aws.ec2.SecurityGroup(f"{name}-db-sg",
            vpc_id=args.vpc_id,
            description=f"Security group for {name} database",
            ingress=[aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=db_port,
                to_port=db_port,
                security_groups=args.allowed_security_groups or [],
                description=f"{args.engine} access",
            )],
            egress=[aws.ec2.SecurityGroupEgressArgs(
                protocol="-1", from_port=0, to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            )],
            tags={"Name": f"{name}-db-sg", "Environment": args.environment},
            opts=child_opts,
        )

        # Subnet Group
        self.subnet_group = aws.rds.SubnetGroup(f"{name}-db-subnets",
            subnet_ids=args.subnet_ids,
            tags={"Name": f"{name}-db-subnets", "Environment": args.environment},
            opts=child_opts,
        )

        # Generate a random password
        self.password = aws.secretsmanager.Secret(f"{name}-db-password",
            name=f"/{args.environment}/{name}/db-password",
            description=f"Password for {name} database",
            opts=child_opts,
        )

        password_value = aws.secretsmanager.SecretVersion(f"{name}-db-password-value",
            secret_id=self.password.id,
            secret_string=pulumi.Output.secret("ChangeMe123!"),  # In production, use random
            opts=child_opts,
        )

        # RDS Instance
        self.instance = aws.rds.Instance(f"{name}-db",
            engine=args.engine,
            engine_version=args.engine_version,
            instance_class=args.instance_class,
            allocated_storage=args.allocated_storage,
            storage_encrypted=True,
            db_name=args.db_name,
            username=args.username,
            password=password_value.secret_string,
            db_subnet_group_name=self.subnet_group.name,
            vpc_security_group_ids=[self.security_group.id],
            multi_az=args.multi_az,
            backup_retention_period=args.backup_retention_days,
            deletion_protection=args.deletion_protection,
            skip_final_snapshot=not args.deletion_protection,
            tags={"Name": f"{name}-db", "Environment": args.environment},
            opts=child_opts,
        )

        # Export properties
        self.endpoint = self.instance.endpoint
        self.port = self.instance.port
        self.address = self.instance.address

        self.register_outputs({
            "endpoint": self.endpoint,
            "port": self.port,
            "security_group_id": self.security_group.id,
            "secret_arn": self.password.arn,
        })
```

**Step 2: Use the Component**

```python
# __main__.py
from components.database import Database, DatabaseArgs

orders_db = Database("orders", DatabaseArgs(
    engine="postgres",
    instance_class="db.r6g.large",
    allocated_storage=100,
    db_name="orders",
    vpc_id=vpc.id,
    subnet_ids=[s.id for s in private_subnets],
    allowed_security_groups=[app_sg.id],
    multi_az=True,
    backup_retention_days=30,
    deletion_protection=True,
    environment="production",
))

users_db = Database("users", DatabaseArgs(
    engine="postgres",
    instance_class="db.t3.medium",
    allocated_storage=50,
    db_name="users",
    vpc_id=vpc.id,
    subnet_ids=[s.id for s in private_subnets],
    allowed_security_groups=[app_sg.id],
    environment="production",
))

pulumi.export("orders_db_endpoint", orders_db.endpoint)
pulumi.export("users_db_endpoint", users_db.endpoint)
```

---

## Exercises

1. **Build a Component**: Create a `StaticWebsite` component that provisions an S3 bucket configured for static hosting, a CloudFront distribution, and a Route53 DNS record. It should accept `domain_name`, `certificate_arn`, and `environment` as parameters.

2. **Cross-Stack Architecture**: Create three stacks -- network (VPC, subnets), database (RDS using stack reference to network), and application (ECS/EC2 using references to both). Deploy all three and verify they work together.

3. **Unit Test Suite**: Write at least 5 unit tests for your infrastructure that verify: (a) no public databases, (b) all storage encrypted, (c) proper tagging, (d) security groups not overly permissive, (e) production resources have deletion protection.

4. **Automation API Portal**: Build a simple Python script using the Automation API that accepts command-line arguments (team, project, environment) and provisions a complete application stack (S3 + DynamoDB + Lambda). Include a `--destroy` flag for cleanup.

5. **Policy as Code**: Use Pulumi CrossGuard to write a policy pack that enforces: (a) all S3 buckets must have versioning, (b) all EC2 instances must be tagged, (c) no security groups allow 0.0.0.0/0 on port 22.

---

## Knowledge Check

**Q1: What is a ComponentResource and how does it differ from a regular resource?**

<details>
<summary>Answer</summary>

A ComponentResource is a logical grouping of multiple resources that acts as a single unit. Unlike a regular resource (which maps 1:1 to a cloud resource), a ComponentResource does not create anything itself -- it is a container for child resources. Benefits: (1) Resources appear nested in the Pulumi UI under the component, (2) Setting `parent=self` on child resources enables automatic dependency tracking and naming, (3) Components can be packaged, versioned, and shared as Python packages, (4) They support `register_outputs` to expose selected properties. They are the Pulumi equivalent of Terraform modules but with full OOP capabilities.
</details>

**Q2: How do stack references work and when should you use them?**

<details>
<summary>Answer</summary>

Stack references allow one Pulumi stack to read the outputs of another stack. You create a `StackReference("org/project/stack")` and call `get_output("key")` to read exported values. Use them when: (1) Different teams own different infrastructure layers (networking team, database team, application team), (2) Resources have different lifecycle -- VPCs change rarely, apps change frequently, (3) You want blast radius isolation -- a bug in the app stack cannot destroy the network, (4) You need to share resources across projects. Stack references create a loose coupling -- stacks communicate through well-defined output interfaces.
</details>

**Q3: What is the Pulumi Automation API and what problems does it solve?**

<details>
<summary>Answer</summary>

The Automation API lets you embed Pulumi as a library inside your own applications instead of using the CLI. It exposes `create_or_select_stack()`, `stack.up()`, `stack.preview()`, `stack.destroy()`, and `stack.outputs` as programmatic APIs. This solves: (1) Building self-service portals where developers provision infrastructure through a web UI, (2) Creating custom CLIs for your organization, (3) Implementing infrastructure provisioning in CI/CD pipelines without shelling out to the Pulumi CLI, (4) Building SaaS products that provision per-tenant infrastructure, (5) Orchestrating complex multi-stack deployments with custom logic.
</details>

**Q4: Why is testing infrastructure code important and what types of tests should you write?**

<details>
<summary>Answer</summary>

Infrastructure misconfigurations cause outages and security breaches. Testing catches issues before deployment. Three test levels: (1) **Unit tests** -- run instantly using mocks, verify resource properties (e.g., database is not public, encryption is enabled, tags are set). Catches configuration mistakes. (2) **Integration tests** -- deploy to a real environment, verify resources exist and are functional (e.g., can connect to database, bucket accepts uploads). Catches cloud API incompatibilities. (3) **Policy tests** -- CrossGuard policies run during `pulumi preview` and block deployments that violate organizational rules (e.g., no unencrypted storage). Acts as a guardrail for all teams.
</details>
