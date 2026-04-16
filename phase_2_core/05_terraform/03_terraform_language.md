# Terraform Language Deep Dive

## Why This Matters in DevOps

Real infrastructure is not a handful of static resources. It is dozens of servers across multiple environments, each slightly different. You need variables so configurations are reusable. You need conditionals so behavior changes between dev and prod. You need loops so you do not copy-paste the same resource block 50 times. You need data sources so Terraform can discover existing infrastructure.

Without mastering the Terraform language, you will write brittle, repetitive configurations that break every time requirements change. With mastery, you write infrastructure code that is as flexible and maintainable as application code.

---

## Core Concepts

### Input Variables

Variables parameterize your Terraform configuration. They let you reuse the same code for different environments, regions, or teams.

```hcl
# variables.tf
variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "instance_count" {
  description = "Number of instances to create"
  type        = number
  default     = 1
}

variable "enable_monitoring" {
  description = "Whether to enable detailed monitoring"
  type        = bool
  default     = false
}

variable "allowed_cidrs" {
  description = "List of CIDR blocks allowed to access the service"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "instance_config" {
  description = "Configuration for instances by role"
  type = map(object({
    instance_type = string
    disk_size     = number
    monitoring    = bool
  }))
  default = {
    web = {
      instance_type = "t3.micro"
      disk_size     = 20
      monitoring    = true
    }
    worker = {
      instance_type = "t3.small"
      disk_size     = 50
      monitoring    = false
    }
  }
}
```

**Variable types:**
- `string` — text values
- `number` — numeric values
- `bool` — true/false
- `list(type)` — ordered collection: `["a", "b", "c"]`
- `set(type)` — unordered unique collection
- `map(type)` — key-value pairs: `{key = "value"}`
- `object({...})` — structured type with named attributes
- `tuple([...])` — sequence with different types per element

**Setting variable values (in order of precedence, lowest to highest):**

```bash
# 1. Default values in variable declarations
# 2. terraform.tfvars file (auto-loaded)
# 3. *.auto.tfvars files (auto-loaded, alphabetical order)
# 4. -var-file flag
terraform apply -var-file="prod.tfvars"

# 5. -var flag
terraform apply -var="environment=prod" -var="instance_count=3"

# 6. TF_VAR_ environment variables
export TF_VAR_environment="prod"
export TF_VAR_instance_count=3
terraform apply
```

**Variable validation:**

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  type = string

  validation {
    condition     = can(regex("^t3\\.", var.instance_type))
    error_message = "Only t3 instance types are allowed."
  }
}
```

### Output Values

Outputs expose information about your infrastructure — useful for other Terraform configurations, scripts, or human operators.

```hcl
output "instance_ip" {
  description = "The public IP of the web server"
  value       = aws_instance.web.public_ip
}

output "database_endpoint" {
  description = "The database connection string"
  value       = aws_db_instance.main.endpoint
  sensitive   = true  # Hides value in CLI output
}

output "all_instance_ids" {
  description = "IDs of all created instances"
  value       = aws_instance.web[*].id
}
```

Query outputs after apply:

```bash
terraform output
terraform output instance_ip
terraform output -json  # Machine-readable
```

### Local Values

Locals are computed values you define once and reference multiple times. They reduce repetition and improve readability.

```hcl
locals {
  common_tags = {
    Project     = "web-platform"
    Environment = var.environment
    ManagedBy   = "terraform"
    Team        = "platform-engineering"
  }

  name_prefix = "${var.project}-${var.environment}"

  is_production = var.environment == "prod"

  subnet_cidrs = [
    for i in range(3) : cidrsubnet(var.vpc_cidr, 8, i)
  ]
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = local.is_production ? "t3.large" : "t3.micro"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web"
  })
}
```

### Data Sources

Data sources let you fetch information about existing infrastructure that Terraform does not manage. They are read-only.

```hcl
# Find the latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Look up an existing VPC
data "aws_vpc" "existing" {
  tags = {
    Name = "main-vpc"
  }
}

# Get current AWS account info
data "aws_caller_identity" "current" {}

# Use data sources in resources
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = data.aws_subnet.selected.id

  tags = {
    Name    = "web-server"
    Account = data.aws_caller_identity.current.account_id
  }
}
```

### Resource Dependencies

Terraform automatically detects dependencies through attribute references (implicit dependencies). Sometimes you need to declare them explicitly.

```hcl
# Implicit dependency — Terraform knows the instance needs the security group
resource "aws_security_group" "web" {
  name = "web-sg"
}

resource "aws_instance" "web" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web.id]  # ← implicit dependency
}

# Explicit dependency — when there is no attribute reference but order matters
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  depends_on = [aws_s3_bucket.logs]  # ← explicit dependency
  # The instance does not reference the bucket, but we need the bucket
  # to exist first (maybe the instance's userdata script writes to it)
}
```

### count and for_each

These meta-arguments let you create multiple instances of a resource.

**count — create N copies:**

```hcl
resource "aws_instance" "web" {
  count         = 3
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server-${count.index}"  # web-server-0, web-server-1, web-server-2
  }
}

# Reference: aws_instance.web[0], aws_instance.web[1], etc.
# All IDs: aws_instance.web[*].id
```

**for_each — create instances from a map or set:**

```hcl
variable "instances" {
  default = {
    web    = "t3.micro"
    api    = "t3.small"
    worker = "t3.medium"
  }
}

resource "aws_instance" "server" {
  for_each      = var.instances
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = each.value

  tags = {
    Name = each.key  # "web", "api", "worker"
  }
}

# Reference: aws_instance.server["web"], aws_instance.server["api"]
```

**Why for_each is usually preferred over count:**

With `count`, if you remove item at index 1 from a list of 3, items 1 and 2 are both affected (indexes shift). With `for_each`, removing "api" only affects "api" — "web" and "worker" are untouched.

### Conditional Expressions

```hcl
# Ternary syntax: condition ? true_value : false_value

resource "aws_instance" "web" {
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"
  monitoring    = var.environment == "prod" ? true : false
}

# Conditional resource creation
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name  = "high-cpu"
  namespace   = "AWS/EC2"
  metric_name = "CPUUtilization"
  threshold   = 80
}
```

### Dynamic Blocks

When you need to repeat nested blocks within a resource:

```hcl
variable "ingress_rules" {
  default = [
    { port = 80, description = "HTTP" },
    { port = 443, description = "HTTPS" },
    { port = 8080, description = "App" },
  ]
}

resource "aws_security_group" "web" {
  name = "web-sg"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = ingress.value.description
    }
  }
}
```

### Built-in Functions

Terraform has dozens of built-in functions. No user-defined functions (use modules instead).

```hcl
# String functions
upper("hello")                    # "HELLO"
lower("HELLO")                    # "hello"
format("Hello, %s!", "world")     # "Hello, world!"
join(", ", ["a", "b", "c"])       # "a, b, c"
split(",", "a,b,c")              # ["a", "b", "c"]
replace("hello world", " ", "-") # "hello-world"
trimspace("  hello  ")           # "hello"

# Collection functions
length(["a", "b", "c"])          # 3
contains(["a", "b"], "a")        # true
merge({a = 1}, {b = 2})          # {a = 1, b = 2}
keys({a = 1, b = 2})             # ["a", "b"]
values({a = 1, b = 2})           # [1, 2]
flatten([[1, 2], [3, 4]])        # [1, 2, 3, 4]
lookup({a = 1}, "a", 0)          # 1
lookup({a = 1}, "b", 0)          # 0 (default)

# Numeric functions
max(5, 12, 9)                    # 12
min(5, 12, 9)                    # 5
ceil(4.3)                        # 5
floor(4.7)                       # 4

# Filesystem functions
file("${path.module}/scripts/init.sh")     # Read file contents
fileexists("${path.module}/config.json")   # true/false
templatefile("${path.module}/template.tpl", { name = "web" })

# Encoding functions
jsonencode({app = "web", port = 8080})     # JSON string
yamlencode({app = "web", port = 8080})     # YAML string
base64encode("hello")                      # "aGVsbG8="

# IP/Network functions
cidrsubnet("10.0.0.0/16", 8, 1)           # "10.0.1.0/24"
cidrhost("10.0.1.0/24", 5)                # "10.0.1.5"

# Type conversion
tostring(42)                               # "42"
tonumber("42")                             # 42
tolist(toset(["a", "b", "a"]))            # ["a", "b"]
```

---

## Step-by-Step Practical

### Building a Parameterized Configuration

Create a configuration that demonstrates variables, locals, for_each, and functions working together.

**File structure:**

```
parameterized-infra/
  main.tf
  variables.tf
  outputs.tf
  terraform.tfvars
  environments/
    dev.tfvars
    prod.tfvars
```

**variables.tf:**

```hcl
variable "project_name" {
  description = "Name of the project"
  type        = string

  validation {
    condition     = length(var.project_name) >= 3 && length(var.project_name) <= 20
    error_message = "Project name must be between 3 and 20 characters."
  }
}

variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "services" {
  description = "Map of services to deploy"
  type = map(object({
    port     = number
    replicas = number
  }))
}

variable "enable_debug" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}
```

**main.tf:**

```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  timestamp   = formatdate("YYYY-MM-DD", timestamp())

  common_config = {
    project     = var.project_name
    environment = var.environment
    debug       = var.enable_debug
    generated   = local.timestamp
  }

  # Compute total replicas across all services
  total_replicas = sum([for svc in var.services : svc.replicas])
}

# Generate a config file for each service
resource "local_file" "service_config" {
  for_each = var.services

  filename = "${path.module}/output/${local.name_prefix}-${each.key}.json"
  content = jsonencode(merge(local.common_config, {
    service  = each.key
    port     = each.value.port
    replicas = each.value.replicas
    url      = "http://localhost:${each.value.port}"
  }))
}

# Generate a summary file
resource "local_file" "summary" {
  filename = "${path.module}/output/${local.name_prefix}-summary.txt"
  content  = <<-EOT
    Deployment Summary
    ==================
    Project:     ${var.project_name}
    Environment: ${var.environment}
    Services:    ${join(", ", keys(var.services))}
    Total Replicas: ${local.total_replicas}
    Debug Mode:  ${var.enable_debug ? "ENABLED" : "disabled"}

    Service Details:
    %{for name, svc in var.services~}
    - ${name}: port ${svc.port}, ${svc.replicas} replica(s)
    %{endfor~}
  EOT
}
```

**outputs.tf:**

```hcl
output "service_files" {
  description = "Generated service config file paths"
  value       = { for k, v in local_file.service_config : k => v.filename }
}

output "total_replicas" {
  description = "Total number of replicas across all services"
  value       = local.total_replicas
}
```

**environments/dev.tfvars:**

```hcl
project_name = "myapp"
environment  = "dev"
enable_debug = true

services = {
  api = {
    port     = 8080
    replicas = 1
  }
  web = {
    port     = 3000
    replicas = 1
  }
}
```

**environments/prod.tfvars:**

```hcl
project_name = "myapp"
environment  = "prod"
enable_debug = false

services = {
  api = {
    port     = 8080
    replicas = 3
  }
  web = {
    port     = 3000
    replicas = 2
  }
  worker = {
    port     = 9090
    replicas = 4
  }
}
```

**Run it:**

```bash
# Development environment
terraform init
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# Check results
cat output/myapp-dev-api.json | python3 -m json.tool
cat output/myapp-dev-summary.txt

# Switch to production
terraform destroy -var-file="environments/dev.tfvars" -auto-approve
terraform apply -var-file="environments/prod.tfvars"

# Production creates an additional "worker" service config
ls output/
```

### Testing Functions in the Terraform Console

```bash
terraform console

> upper("hello terraform")
"HELLO TERRAFORM"

> cidrsubnet("10.0.0.0/16", 8, 1)
"10.0.1.0/24"

> formatdate("YYYY-MM-DD hh:mm", timestamp())
"2024-01-15 14:30"

> jsonencode({name = "web", ports = [80, 443]})
"{\"name\":\"web\",\"ports\":[80,443]}"

> contains(["dev", "staging", "prod"], "dev")
true

> exit
```

---

## Exercises

### Exercise 1: Variable Validation
Create a variable for `instance_type` that only accepts values starting with "t3." or "t4g." and a variable for `disk_size` that must be between 20 and 1000 GB. Test with valid and invalid inputs.

### Exercise 2: Dynamic Environments
Using the local file provider and `for_each`, create a configuration that generates environment-specific configuration files (dev, staging, prod) from a single map variable. Each file should contain different settings (database host, log level, cache TTL).

### Exercise 3: Conditional Resources
Create a configuration where a monitoring config file is only created when `var.environment == "prod"` and a debug config file is only created when `var.enable_debug == true`. Use `count` for conditional creation.

### Exercise 4: Complex Data Transformation
Given a variable containing a list of server definitions, use `for` expressions and built-in functions to: (a) filter only servers with more than 2 replicas, (b) create a map of server name to port, (c) generate a comma-separated list of all server names.

### Exercise 5: Template Files
Create a `templatefile` that generates an Nginx configuration. The template should accept variables for server_name, upstream servers (a list), and enable_ssl (boolean). Use Jinja-like template syntax with conditionals and loops.

---

## Knowledge Check

### Question 1
What is the difference between `count` and `for_each`, and when should you prefer `for_each`?

<details>
<summary>Answer</summary>

`count` creates N copies of a resource indexed by number (0, 1, 2...). `for_each` creates instances indexed by string keys from a map or set. You should prefer `for_each` when resources have meaningful identities because: (1) removing an item from the middle of a `count` list shifts all subsequent indexes, causing unnecessary destroy/recreate operations, while `for_each` only affects the specific key removed; (2) `for_each` produces more readable state (`aws_instance.server["web"]` vs `aws_instance.server[0]`); (3) `for_each` makes it clear which configuration belongs to which instance. Use `count` only for simple "create N identical copies" scenarios or for conditional resource creation (`count = var.enabled ? 1 : 0`).
</details>

### Question 2
How do you pass variable values to Terraform, and what is the precedence order?

<details>
<summary>Answer</summary>

Variable values can be set through (from lowest to highest precedence): (1) default values in the variable declaration, (2) `terraform.tfvars` file (auto-loaded), (3) `*.auto.tfvars` files (auto-loaded in alphabetical order), (4) `-var-file` flag on the command line, (5) `-var` flag on the command line, (6) `TF_VAR_` environment variables. Higher-precedence sources override lower ones. In practice, defaults provide sensible fallbacks, `.tfvars` files hold environment-specific values, and `TF_VAR_` environment variables are used in CI/CD pipelines for secrets.
</details>

### Question 3
What are data sources and how do they differ from resources?

<details>
<summary>Answer</summary>

Data sources allow Terraform to query and read information from external sources (cloud APIs, other Terraform state, etc.) without managing or modifying them. They are read-only. Resources, by contrast, represent infrastructure objects that Terraform creates, updates, and destroys. Data sources are declared with `data` blocks and referenced with `data.type.name.attribute`. Common uses include: looking up the latest AMI, finding an existing VPC by tags, reading the current AWS account ID, or fetching outputs from another Terraform state. Data sources are refreshed on every plan/apply to ensure they reflect current reality.
</details>

### Question 4
What does the `sensitive = true` attribute do on an output value?

<details>
<summary>Answer</summary>

Setting `sensitive = true` on an output prevents Terraform from displaying its value in the CLI output during `plan` and `apply`. The output will show as `(sensitive value)` instead of the actual content. This is used for outputs that contain secrets like database passwords, API keys, or connection strings. However, the value is still stored in the state file in plain text, so state file security remains critical. The value can still be accessed programmatically via `terraform output -json` or by other Terraform configurations that reference this state as a data source.
</details>
