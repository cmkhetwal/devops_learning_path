# Terraform with AWS: Building Real Infrastructure

## Why This Matters in DevOps

AWS is the most widely used cloud provider, and Terraform is the most widely used IaC tool. The combination of Terraform and AWS is the bread and butter of DevOps infrastructure work. When you interview for DevOps roles, you will be asked to design and build AWS infrastructure with Terraform. When you start a new job, you will inherit Terraform code that manages AWS resources.

This lesson moves beyond local file providers into real cloud infrastructure. You will learn to build the foundational components — VPCs, subnets, security groups, EC2 instances, S3 buckets, and IAM roles — that form the backbone of every AWS deployment. More importantly, you will learn how to review a Terraform plan methodically, which is the skill that prevents costly mistakes in production.

---

## Core Concepts

### AWS Provider Configuration

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5.0"
}

# Basic configuration — uses AWS credentials from environment or ~/.aws/credentials
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "terraform"
      Project     = var.project_name
      Environment = var.environment
    }
  }
}

# Provider alias for multi-region deployments
provider "aws" {
  alias  = "us_west"
  region = "us-west-2"
}
```

**Authentication methods (in order of preference):**

```bash
# 1. Environment variables (CI/CD pipelines)
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_REGION="us-east-1"

# 2. AWS CLI profile (~/.aws/credentials)
provider "aws" {
  region  = "us-east-1"
  profile = "myprofile"
}

# 3. IAM role assumption (for cross-account access)
provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn = "arn:aws:iam::123456789012:role/TerraformRole"
  }
}

# 4. OIDC (for CI/CD — no long-lived credentials)
# Configured in GitHub Actions or similar, not in Terraform directly
```

### Creating a VPC

A Virtual Private Cloud (VPC) is the network foundation for everything in AWS. Every EC2 instance, database, and load balancer lives inside a VPC.

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

# Internet Gateway — allows public subnets to reach the internet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-igw"
  }
}
```

### Creating Subnets

Subnets divide your VPC into segments. Public subnets have internet access; private subnets do not (directly).

```hcl
# Public subnets — for load balancers, bastion hosts
resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-${var.availability_zones[count.index]}"
    Tier = "public"
  }
}

# Private subnets — for application servers, databases
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.environment}-private-${var.availability_zones[count.index]}"
    Tier = "private"
  }
}

# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-public-rt"
  }
}

# Associate public subnets with the public route table
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway for private subnets (allows outbound internet access)
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.environment}-nat-eip"
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.environment}-nat-gw"
  }

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
```

### Security Groups

Security groups act as virtual firewalls for your instances.

```hcl
# ALB security group — allows HTTP/HTTPS from anywhere
resource "aws_security_group" "alb" {
  name_prefix = "${var.environment}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-alb-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Application security group — allows traffic only from ALB
resource "aws_security_group" "app" {
  name_prefix = "${var.environment}-app-"
  description = "Security group for application servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-app-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

### EC2 Instances

```hcl
# Find the latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.private[0].id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.web.name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y nginx
    systemctl start nginx
    systemctl enable nginx
    echo "<h1>Hello from $(hostname)</h1>" > /var/www/html/index.html
  EOF

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "${var.environment}-web-server"
    Role = "web"
  }
}
```

### S3 Buckets

```hcl
resource "aws_s3_bucket" "app_assets" {
  bucket = "${var.project_name}-${var.environment}-assets"

  tags = {
    Name = "${var.environment}-app-assets"
  }
}

resource "aws_s3_bucket_versioning" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}
```

### IAM Roles

```hcl
# IAM role for EC2 instances
data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "web" {
  name               = "${var.environment}-web-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

# Policy allowing the web server to access the S3 bucket
data "aws_iam_policy_document" "web_s3_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.app_assets.arn,
      "${aws_s3_bucket.app_assets.arn}/*",
    ]
  }
}

resource "aws_iam_role_policy" "web_s3" {
  name   = "s3-access"
  role   = aws_iam_role.web.id
  policy = data.aws_iam_policy_document.web_s3_access.json
}

resource "aws_iam_instance_profile" "web" {
  name = "${var.environment}-web-profile"
  role = aws_iam_role.web.name
}
```

### Plan Review Methodology

Reviewing a Terraform plan is your last line of defense before changes hit production. Use this methodology:

```
1. READ THE SUMMARY FIRST
   Plan: 3 to add, 1 to change, 1 to destroy.
   → Do these numbers match your expectations?

2. CHECK FOR DESTROYS
   Search for "will be destroyed" or "must be replaced"
   → Is any destruction intentional? Replacements cause downtime.

3. CHECK WHAT IS BEING CREATED
   Look at + (create) resources
   → Are the values correct? AMI, instance type, subnet?

4. CHECK IN-PLACE UPDATES
   Look at ~ (update) resources
   → Are only the intended fields changing?

5. CHECK FOR SENSITIVE VALUES
   → Are secrets appearing in plain text in the plan?

6. CHECK RESOURCE DEPENDENCIES
   → Will the destroy/create order cause issues?

7. VERIFY TAGS AND NAMING
   → Are names and tags consistent with your standards?
```

---

## Step-by-Step Practical

### Complete Web Server Infrastructure

This practical builds a complete, production-ready web server setup from scratch. All resources work together.

**File structure:**

```
aws-web-server/
  main.tf
  variables.tf
  outputs.tf
  versions.tf
  terraform.tfvars
```

**versions.tf:**

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

**variables.tf:**

```hcl
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "app_port" {
  description = "Port the application listens on"
  type        = number
  default     = 80
}
```

**main.tf:**

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# --- NETWORKING ---

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "${var.project_name}-${var.environment}-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-${var.environment}-igw" }
}

resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.environment}-public-${count.index}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = { Name = "${var.project_name}-${var.environment}-public-rt" }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# --- SECURITY ---

resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-${var.environment}-web-"
  description = "Allow HTTP traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-${var.environment}-web-sg" }

  lifecycle {
    create_before_destroy = true
  }
}

# --- COMPUTE ---

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y nginx
    cat > /var/www/html/index.html <<'HTML'
    <!DOCTYPE html>
    <html>
    <body>
      <h1>Deployed with Terraform</h1>
      <p>Environment: ${var.environment}</p>
      <p>Instance: $(hostname)</p>
    </body>
    </html>
    HTML
    systemctl enable nginx
    systemctl start nginx
  EOF

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = { Name = "${var.project_name}-${var.environment}-web" }
}

# --- STORAGE ---

resource "aws_s3_bucket" "assets" {
  bucket = "${var.project_name}-${var.environment}-assets-${data.aws_caller_identity.current.account_id}"

  tags = { Name = "${var.project_name}-${var.environment}-assets" }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket                  = aws_s3_bucket.assets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "current" {}
```

**outputs.tf:**

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "web_server_public_ip" {
  description = "Public IP of the web server"
  value       = aws_instance.web.public_ip
}

output "web_server_url" {
  description = "URL to access the web server"
  value       = "http://${aws_instance.web.public_ip}"
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.assets.bucket
}
```

**terraform.tfvars:**

```hcl
project_name = "mywebapp"
environment  = "dev"
aws_region   = "us-east-1"
instance_type = "t3.micro"
```

**Deployment:**

```bash
terraform init
terraform plan
# Review the plan carefully using the methodology above
terraform apply
# Visit the output URL to see your web server
```

---

## Exercises

### Exercise 1: Add a Database
Extend the web server infrastructure to include an RDS PostgreSQL instance in a private subnet. Create the necessary subnet group, security group (allowing port 5432 only from the app security group), and parameter group.

### Exercise 2: Multi-AZ High Availability
Modify the configuration to deploy web servers across two availability zones behind an Application Load Balancer. Add a target group and health check.

### Exercise 3: Plan Review Exercise
Given the following Terraform plan output, identify all potential issues:
```
Plan: 2 to add, 1 to change, 3 to destroy.
  -/+ aws_instance.web (forces replacement: ami changed)
  -   aws_security_group.old_sg
  -   aws_eip.web
  ~   aws_s3_bucket.data (tags changed)
  +   aws_security_group.new_sg
  +   aws_instance.worker
```

### Exercise 4: Least Privilege IAM
Create an IAM role for the web server that follows the principle of least privilege. The server needs to: read objects from the assets S3 bucket, write logs to CloudWatch, and read parameters from SSM Parameter Store (under a specific path). Write the IAM policy using `aws_iam_policy_document` data sources.

---

## Knowledge Check

### Question 1
Why should you use `name_prefix` instead of `name` for security groups?

<details>
<summary>Answer</summary>

Using `name_prefix` combined with `lifecycle { create_before_destroy = true }` allows Terraform to create a replacement security group before destroying the old one during updates. With a fixed `name`, Terraform must destroy the old security group first (since names must be unique), which would temporarily leave instances without a security group, causing connection failures. `name_prefix` generates a unique name like `prod-web-abc123`, allowing both old and new security groups to coexist during the transition.
</details>

### Question 2
What is the purpose of a NAT Gateway and when can you skip it?

<details>
<summary>Answer</summary>

A NAT Gateway allows instances in private subnets to make outbound connections to the internet (for software updates, API calls, etc.) without being directly accessible from the internet. You can skip a NAT Gateway in: (1) development environments where cost savings matter (NAT Gateways cost ~$32/month minimum), (2) environments where private instances do not need internet access, (3) situations where you use VPC endpoints for AWS services instead. In production, NAT Gateways are almost always required for private subnets.
</details>

### Question 3
Why is it important to use data sources for AMI IDs instead of hardcoding them?

<details>
<summary>Answer</summary>

AMI IDs are region-specific and change when new versions are published. Hardcoding `ami-0abc123` means: (1) the same code cannot work in different regions, (2) you must manually update IDs when new AMI versions are released, (3) there is no way to know what the AMI actually contains without looking it up. Using a `data "aws_ami"` data source with filters automatically resolves to the correct, latest AMI for any region, is self-documenting (the filters describe what you want), and stays current without manual intervention. However, in production you may want to pin specific AMI IDs for stability and test updates explicitly.
</details>

### Question 4
What happens when you change the `user_data` of an EC2 instance in Terraform?

<details>
<summary>Answer</summary>

Changing `user_data` forces the EC2 instance to be replaced (destroyed and recreated). This is because AWS does not support modifying user_data on a running instance — it is only executed at instance launch. In the Terraform plan, you will see `-/+` (destroy and recreate). This means: downtime during replacement, a new instance ID, potentially a new public IP, and the old instance's ephemeral data is lost. To avoid this in production, consider using configuration management tools (Ansible) or Systems Manager Run Command for post-launch configuration changes instead of relying solely on user_data.
</details>
