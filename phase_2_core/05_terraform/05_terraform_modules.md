# Terraform Modules

## Why This Matters in DevOps

The first time you copy-paste a Terraform resource block from your dev environment to prod and change three values, you are doing it wrong. By the fifth time, you have five copies that have diverged in subtle ways. By the twentieth time, you have an unmaintainable mess where fixing a bug means updating twenty files and hoping you do not miss one.

Modules solve this by applying the DRY (Don't Repeat Yourself) principle to infrastructure. You write the pattern once — a VPC, an ECS service, a monitoring stack — and instantiate it with different parameters for each environment or team. This is how mature organizations manage hundreds of services across multiple environments without drowning in copy-pasted code.

---

## Core Concepts

### What Is a Module?

In Terraform, a module is any directory containing `.tf` files. Every Terraform configuration is a module:

- **Root module**: The directory where you run `terraform apply`. This is where you have your backend configuration and provider setup.
- **Child module**: A module called by another module. It encapsulates a reusable piece of infrastructure.

```
root module (you run terraform apply here)
  │
  ├── calls module "vpc"
  │     └── creates VPC, subnets, route tables, NAT gateways
  │
  ├── calls module "ecs_service"
  │     └── creates ECS task definition, service, load balancer, DNS
  │
  └── calls module "monitoring"
        └── creates CloudWatch alarms, dashboards, SNS topics
```

### Module Structure

A well-structured module follows this convention:

```
modules/
  vpc/
    main.tf          # Resource definitions
    variables.tf     # Input variables (the module's interface)
    outputs.tf       # Output values (what the module exposes)
    versions.tf      # Provider and Terraform version constraints
    README.md        # Documentation (optional but strongly recommended)
    locals.tf        # Local values (optional, can be in main.tf)
```

**variables.tf — the module's inputs:**

```hcl
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Whether to create NAT gateways for private subnets"
  type        = bool
  default     = true
}
```

**main.tf — the module's resources:**

```hcl
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-${var.availability_zones[count.index]}"
    Tier = "public"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.environment}-private-${var.availability_zones[count.index]}"
    Tier = "private"
  }
}
```

**outputs.tf — the module's outputs:**

```hcl
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "vpc_cidr" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.this.cidr_block
}
```

### Calling Modules

From the root module:

```hcl
# Call a local module
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr           = "10.0.0.0/16"
  environment        = "prod"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  enable_nat_gateway = true
}

# Use module outputs
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnet_ids[0]
}

# Call the same module again with different parameters
module "vpc_staging" {
  source = "../../modules/vpc"

  vpc_cidr           = "10.1.0.0/16"
  environment        = "staging"
  availability_zones = ["us-east-1a", "us-east-1b"]
  enable_nat_gateway = false  # Save costs in staging
}
```

### Module Sources

Terraform can fetch modules from many locations:

```hcl
# Local path
module "vpc" {
  source = "./modules/vpc"
}

# Terraform Registry (public)
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"
}

# GitHub
module "vpc" {
  source = "github.com/myorg/terraform-modules//vpc?ref=v2.0.0"
}

# S3 bucket
module "vpc" {
  source = "s3::https://s3-eu-west-1.amazonaws.com/mybucket/modules/vpc.zip"
}

# Generic Git
module "vpc" {
  source = "git::https://git.example.com/modules.git//vpc?ref=v1.2.3"
}
```

### Module Versioning

Always pin module versions in production:

```hcl
# Terraform Registry — use version constraint
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"  # Allows 5.x but not 6.0
}

# Git — use ref parameter
module "vpc" {
  source = "git::https://github.com/myorg/modules.git//vpc?ref=v2.1.0"
}
```

Never use `main` or `latest` in production. An upstream change could break your infrastructure without warning.

### Terraform Registry

The public Terraform Registry (registry.terraform.io) hosts thousands of community modules. The most popular ones are well-tested and widely used:

- `terraform-aws-modules/vpc/aws` — AWS VPC with all networking
- `terraform-aws-modules/eks/aws` — AWS EKS (Kubernetes)
- `terraform-aws-modules/rds/aws` — AWS RDS databases
- `terraform-aws-modules/s3-bucket/aws` — AWS S3 with best practices

```hcl
# Using a registry module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name = "prod-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true

  tags = {
    Environment = "prod"
    Terraform   = "true"
  }
}
```

### Module Composition Patterns

**Pattern 1: Flat modules (simple, direct)**

```
environments/
  prod/
    main.tf  → calls module "vpc", module "ec2", module "rds" directly
```

**Pattern 2: Nested composition (modules calling modules)**

```
environments/
  prod/
    main.tf  → calls module "web_platform"
                  → internally calls module "vpc"
                  → internally calls module "ec2"
                  → internally calls module "rds"
```

**Pattern 3: Facade modules (recommended for large orgs)**

```
# A "service" module that abstracts away all the details
module "checkout_service" {
  source = "../../modules/microservice"

  name        = "checkout"
  environment = "prod"
  team        = "payments"

  # Developers only set high-level parameters
  container_image  = "checkout:v2.1.0"
  cpu              = 512
  memory           = 1024
  desired_count    = 3
  health_check_path = "/health"
}

# The "microservice" module internally creates:
# - ECS task definition and service
# - Application load balancer target group
# - Security groups
# - CloudWatch alarms
# - IAM roles
# - DNS records
```

This pattern lets platform teams provide a simple, opinionated interface while handling all the complexity internally.

---

## Step-by-Step Practical

### Building a Reusable Module

We will build a module using the local provider that generates a complete application configuration directory.

**Directory structure:**

```
module-lab/
  modules/
    app_config/
      main.tf
      variables.tf
      outputs.tf
  environments/
    dev/
      main.tf
    prod/
      main.tf
```

**modules/app_config/variables.tf:**

```hcl
variable "app_name" {
  description = "Name of the application"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]+$", var.app_name))
    error_message = "App name must be lowercase alphanumeric with hyphens."
  }
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "port" {
  description = "Application port"
  type        = number
  default     = 8080
}

variable "log_level" {
  description = "Logging level"
  type        = string
  default     = "info"

  validation {
    condition     = contains(["debug", "info", "warn", "error"], var.log_level)
    error_message = "Log level must be debug, info, warn, or error."
  }
}

variable "database" {
  description = "Database configuration"
  type = object({
    host     = string
    port     = number
    name     = string
    pool_size = number
  })
}

variable "features" {
  description = "Feature flags"
  type        = map(bool)
  default     = {}
}

variable "output_dir" {
  description = "Base directory for output files"
  type        = string
}
```

**modules/app_config/main.tf:**

```hcl
locals {
  config_dir = "${var.output_dir}/${var.app_name}-${var.environment}"
}

resource "local_file" "app_config" {
  filename = "${local.config_dir}/application.json"
  content = jsonencode({
    app = {
      name        = var.app_name
      environment = var.environment
      port        = var.port
      log_level   = var.log_level
    }
    database = var.database
    features = var.features
  })
}

resource "local_file" "docker_compose" {
  filename = "${local.config_dir}/docker-compose.yml"
  content  = yamlencode({
    version = "3.8"
    services = {
      app = {
        image = "${var.app_name}:latest"
        ports = ["${var.port}:${var.port}"]
        environment = {
          APP_ENV       = var.environment
          APP_PORT      = tostring(var.port)
          LOG_LEVEL     = var.log_level
          DB_HOST       = var.database.host
          DB_PORT       = tostring(var.database.port)
          DB_NAME       = var.database.name
          DB_POOL_SIZE  = tostring(var.database.pool_size)
        }
      }
    }
  })
}

resource "local_file" "env_file" {
  filename = "${local.config_dir}/.env"
  content  = join("\n", concat(
    [
      "APP_NAME=${var.app_name}",
      "APP_ENV=${var.environment}",
      "APP_PORT=${var.port}",
      "LOG_LEVEL=${var.log_level}",
      "DB_HOST=${var.database.host}",
      "DB_PORT=${var.database.port}",
      "DB_NAME=${var.database.name}",
      "DB_POOL_SIZE=${var.database.pool_size}",
    ],
    [for flag, enabled in var.features : "FEATURE_${upper(flag)}=${enabled ? "true" : "false"}"],
    [""]
  ))
}
```

**modules/app_config/outputs.tf:**

```hcl
output "config_directory" {
  description = "Path to the generated configuration directory"
  value       = local.config_dir
}

output "config_files" {
  description = "List of generated configuration files"
  value = [
    local_file.app_config.filename,
    local_file.docker_compose.filename,
    local_file.env_file.filename,
  ]
}

output "application_url" {
  description = "Local URL where the application would run"
  value       = "http://localhost:${var.port}"
}
```

**environments/dev/main.tf:**

```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

module "api" {
  source = "../../modules/app_config"

  app_name    = "payments-api"
  environment = "dev"
  port        = 8080
  log_level   = "debug"
  output_dir  = "${path.module}/output"

  database = {
    host      = "localhost"
    port      = 5432
    name      = "payments_dev"
    pool_size = 5
  }

  features = {
    new_checkout   = true
    beta_dashboard = true
    rate_limiting  = false
  }
}

module "worker" {
  source = "../../modules/app_config"

  app_name    = "payments-worker"
  environment = "dev"
  port        = 9090
  log_level   = "debug"
  output_dir  = "${path.module}/output"

  database = {
    host      = "localhost"
    port      = 5432
    name      = "payments_dev"
    pool_size = 3
  }

  features = {
    async_processing = true
  }
}

output "api_config_dir" {
  value = module.api.config_directory
}

output "worker_config_dir" {
  value = module.worker.config_directory
}
```

**environments/prod/main.tf:**

```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

module "api" {
  source = "../../modules/app_config"

  app_name    = "payments-api"
  environment = "prod"
  port        = 8080
  log_level   = "warn"
  output_dir  = "${path.module}/output"

  database = {
    host      = "payments-db.prod.internal"
    port      = 5432
    name      = "payments"
    pool_size = 20
  }

  features = {
    new_checkout   = true
    beta_dashboard = false
    rate_limiting  = true
  }
}

output "api_url" {
  value = module.api.application_url
}
```

**Deploy and compare:**

```bash
# Dev environment
cd environments/dev
terraform init && terraform apply -auto-approve
cat output/payments-api-dev/application.json | python3 -m json.tool
cat output/payments-api-dev/.env

# Prod environment
cd ../prod
terraform init && terraform apply -auto-approve
cat output/payments-api-prod/application.json | python3 -m json.tool
# Notice: different database, different log level, different feature flags
```

---

## Exercises

### Exercise 1: Build a Server Config Module
Create a module that generates server configuration files (Nginx config, systemd unit file, and logrotate config). The module should accept variables for: server_name, port, log_directory, max_connections, and worker_processes. Call it twice with different parameters.

### Exercise 2: Module with Conditional Resources
Extend your module to accept an `enable_ssl` boolean. When true, generate an additional SSL configuration file. When false, skip it. Use `count` for conditional resource creation inside the module.

### Exercise 3: Registry Module Exploration
Visit registry.terraform.io and examine the `terraform-aws-modules/vpc/aws` module. Read its README, variables, and outputs. Without applying, write a root module that would call it with appropriate settings for a production VPC. Explain what each input variable controls.

### Exercise 4: Module Versioning Strategy
Create two versions of a module (v1 and v2) in separate directories. The v2 adds a new output and changes a default value. Create two root modules: one using v1 and one using v2. Discuss how you would manage the migration from v1 to v2 in a real team.

### Exercise 5: Facade Module Pattern
Design (on paper or in code) a "microservice" facade module that accepts only: name, docker_image, port, replicas, and environment. Internally, the module should generate configurations for a Docker Compose service, an Nginx reverse proxy config, a monitoring config, and a log aggregation config. This demonstrates how platform teams simplify infrastructure for developers.

---

## Knowledge Check

### Question 1
What is the difference between a root module and a child module?

<details>
<summary>Answer</summary>

The root module is the top-level directory where you run `terraform init`, `plan`, and `apply`. It contains the backend configuration, provider setup, and is the entry point for Terraform. A child module is any module called by another module using a `module` block. Child modules are reusable components that encapsulate resources and are parameterized through input variables. A child module cannot configure backends or providers — these are always defined in the root module. Every Terraform configuration is technically a module; the distinction is about which one is the entry point.
</details>

### Question 2
Why should you always pin module versions in production?

<details>
<summary>Answer</summary>

Pinning module versions prevents unexpected changes to your infrastructure. Without version pinning, `terraform init` fetches the latest version of a module, which may include breaking changes, removed variables, renamed resources (causing destroy/recreate), or behavioral changes. In production, you want predictable, reproducible deployments. A version constraint like `version = "~> 5.0"` allows patch updates (5.0.1, 5.1.0) but blocks major changes (6.0.0). For Git-sourced modules, use `?ref=v2.1.0` to pin to a specific tag. Module updates should be deliberate, tested in lower environments first, and reviewed in pull requests.
</details>

### Question 3
What files should every well-structured module contain and why?

<details>
<summary>Answer</summary>

Every module should contain: (1) `main.tf` — the resource definitions that implement the module's functionality; (2) `variables.tf` — all input variables with descriptions, types, defaults, and validations, serving as the module's interface contract; (3) `outputs.tf` — all output values that expose useful information to the calling module, enabling composition; (4) `versions.tf` — required provider versions and minimum Terraform version, ensuring compatibility. Optionally: `locals.tf` for computed values, `README.md` for documentation, and `examples/` directory showing how to use the module. This convention makes modules discoverable, self-documenting, and consistent across an organization.
</details>

### Question 4
What is the facade module pattern and when would you use it?

<details>
<summary>Answer</summary>

The facade module pattern creates a high-level, simplified interface that internally orchestrates multiple lower-level modules or resources. For example, a "microservice" facade module might accept only name, image, port, and replicas, but internally create an ECS task definition, service, load balancer target group, security groups, IAM roles, CloudWatch alarms, and DNS records. You use this pattern when: (1) platform teams want to provide a simple, opinionated interface to application developers, (2) you want to enforce organizational standards (security, tagging, monitoring) without requiring every team to know the details, and (3) you want to reduce the blast radius of changes by centralizing infrastructure patterns. It is the infrastructure equivalent of a well-designed API.
</details>
