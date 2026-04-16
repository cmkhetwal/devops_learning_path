# Terraform Fundamentals

## Why This Matters in DevOps

Every infrastructure change in a well-run organization should follow a predictable cycle: write code, review the plan, apply the change, verify the result. Terraform provides exactly this workflow. Before Terraform, provisioning a new environment meant filing tickets, waiting for ops teams, and hoping the result matched what you asked for. With Terraform, a developer can describe what they need, see exactly what will happen, and execute it — all in minutes, all tracked in version control.

Understanding Terraform fundamentals is non-negotiable for DevOps engineers. You will use Terraform (or OpenTofu) in nearly every infrastructure role. The concepts you learn here — providers, resources, state, the init/plan/apply cycle — form the mental model you will use for years.

---

## Core Concepts

### Installing Terraform

Terraform is distributed as a single binary. No runtime dependencies, no package managers for plugins (Terraform handles that itself).

**Linux (Ubuntu/Debian):**

```bash
# Add HashiCorp GPG key and repository
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify installation
terraform version
# Terraform v1.9.x on linux_amd64
```

**macOS:**

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Version management with tfenv (recommended for teams):**

```bash
git clone https://github.com/tfutils/tfenv.git ~/.tfenv
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

tfenv install 1.9.0
tfenv use 1.9.0
terraform version
```

### HCL — HashiCorp Configuration Language

HCL is Terraform's domain-specific language. It is not JSON. It is not YAML. It was purpose-built for defining infrastructure.

```hcl
# Comments use hash
// C-style comments also work
/* Block comments work too */

# Basic block structure
block_type "label1" "label2" {
  argument1 = "value"
  argument2 = 42
  argument3 = true

  nested_block {
    key = "value"
  }
}
```

Key HCL data types:

```hcl
# String
name = "web-server"

# Number
count = 3

# Boolean
enabled = true

# List
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

# Map
tags = {
  Environment = "production"
  Team        = "platform"
}
```

### Providers

Providers are plugins that let Terraform interact with APIs. Every cloud, service, or platform has a provider. Terraform downloads providers automatically during `terraform init`.

```hcl
# Configure the AWS provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "us-east-1"
}
```

The `terraform` block declares which providers you need and constrains their versions. The `provider` block configures them.

Version constraints:
- `= 5.0.0` — exact version
- `>= 5.0.0` — minimum version
- `~> 5.0` — allows 5.x but not 6.0 (pessimistic constraint, most common)
- `>= 5.0, < 6.0` — range

### Resources

Resources are the most important element in Terraform. Each resource block describes one or more infrastructure objects.

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}
```

The syntax is: `resource "TYPE" "NAME" { ... }`

- **TYPE**: Determined by the provider. `aws_instance` means the AWS provider's instance resource.
- **NAME**: A local identifier you choose. Used to reference this resource elsewhere in your code.
- **Arguments**: The configuration inside the block. Each resource type has required and optional arguments.

Every resource has attributes you can reference after creation:

```hcl
# Reference the instance's public IP (computed after creation)
output "web_ip" {
  value = aws_instance.web.public_ip
}
```

### The Terraform Workflow: init / plan / apply / destroy

This four-command workflow is the heartbeat of Terraform.

**terraform init** — Initializes the working directory. Downloads providers, sets up the backend for state storage. You run this once when starting a project or when you change providers/backends.

**terraform plan** — Generates an execution plan. Compares your code against the current state and shows what Terraform would do. This is a dry run — nothing changes.

**terraform apply** — Executes the plan. Creates, updates, or deletes infrastructure to match your code. Terraform shows the plan again and asks for confirmation.

**terraform destroy** — Destroys all infrastructure managed by the current configuration. The nuclear option. Use with caution.

```
terraform init    →  Download providers, initialize backend
      │
terraform plan    →  Show what would change (safe, read-only)
      │
terraform apply   →  Make the changes (prompts for confirmation)
      │
terraform destroy →  Remove everything (prompts for confirmation)
```

### State: The Bridge Between Code and Reality

Terraform needs to know what infrastructure it manages. It stores this mapping in a state file (`terraform.tfstate`). This file is JSON and contains:

- Every resource Terraform created
- Their current attribute values (IPs, IDs, ARNs)
- Metadata about dependencies and provider configurations

```json
{
  "version": 4,
  "terraform_version": "1.9.0",
  "resources": [
    {
      "type": "local_file",
      "name": "config",
      "instances": [
        {
          "attributes": {
            "filename": "/tmp/demo/config.json",
            "content": "{\"app\":\"web\"}"
          }
        }
      ]
    }
  ]
}
```

Without state, Terraform cannot determine what already exists, what needs to change, or what to delete. We will cover state management in depth in a dedicated lesson.

### Understanding the Plan Output

Reading a Terraform plan is a critical skill. The plan uses symbols to indicate what will happen:

```
# Create a new resource
  + resource "aws_instance" "web" {
      + ami           = "ami-0c55b159cbfafe1f0"
      + instance_type = "t3.micro"
      + id            = (known after apply)
      + public_ip     = (known after apply)
    }

# Modify an existing resource in-place
  ~ resource "aws_instance" "web" {
      ~ instance_type = "t3.micro" -> "t3.small"
        # (other attributes unchanged)
    }

# Destroy and recreate (forces replacement)
-/+ resource "aws_instance" "web" {
      ~ ami           = "ami-old" -> "ami-new"  # forces replacement
      ~ id            = "i-abc123" -> (known after apply)
    }

# Destroy
  - resource "aws_instance" "web" {
      - ami           = "ami-0c55b159cbfafe1f0"
      - instance_type = "t3.micro"
    }
```

Symbols:
- `+` — Create
- `-` — Destroy
- `~` — Update in-place
- `-/+` — Destroy and recreate (replacement)
- `<=` — Read (data source)

---

## Step-by-Step Practical

### First Deployment: Local File Provider

You do not need a cloud account to learn Terraform. The `local` provider creates files on your local machine. This lets you learn the workflow risk-free.

**Step 1: Create a project directory**

```bash
mkdir -p ~/terraform-lab/01-fundamentals
cd ~/terraform-lab/01-fundamentals
```

**Step 2: Write your first configuration (main.tf)**

```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
  required_version = ">= 1.5.0"
}

resource "local_file" "greeting" {
  filename = "${path.module}/output/hello.txt"
  content  = "Hello from Terraform!\nThis file was created by Infrastructure as Code.\n"
}

resource "local_file" "config" {
  filename = "${path.module}/output/app-config.json"
  content  = jsonencode({
    application = "web-api"
    port        = 8080
    debug       = false
    database = {
      host = "db.internal"
      port = 5432
    }
  })
}

output "greeting_file" {
  description = "Path to the greeting file"
  value       = local_file.greeting.filename
}

output "config_file" {
  description = "Path to the config file"
  value       = local_file.config.filename
}
```

**Step 3: Initialize**

```bash
terraform init
```

Expected output:
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/local versions matching "~> 2.4"...
- Installing hashicorp/local v2.4.1...
- Installed hashicorp/local v2.4.1 (signed by HashiCorp)

Terraform has been successfully initialized!
```

This creates a `.terraform/` directory with the provider binary and a `.terraform.lock.hcl` file that locks provider versions.

**Step 4: Plan**

```bash
terraform plan
```

Expected output:
```
Terraform will perform the following actions:

  # local_file.config will be created
  + resource "local_file" "config" {
      + content              = jsonencode({ ... })
      + directory_permission = "0777"
      + file_permission      = "0777"
      + filename             = "./output/app-config.json"
      + id                   = (known after apply)
    }

  # local_file.greeting will be created
  + resource "local_file" "greeting" {
      + content              = <<-EOT
            Hello from Terraform!
            This file was created by Infrastructure as Code.
        EOT
      + filename             = "./output/hello.txt"
      + id                   = (known after apply)
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + config_file   = "./output/app-config.json"
  + greeting_file = "./output/hello.txt"
```

**Step 5: Apply**

```bash
terraform apply
```

Terraform shows the plan again and prompts:
```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

Type `yes`. Expected output:
```
local_file.greeting: Creating...
local_file.config: Creating...
local_file.greeting: Creation complete after 0s [id=abc123...]
local_file.config: Creation complete after 0s [id=def456...]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:
config_file = "./output/app-config.json"
greeting_file = "./output/hello.txt"
```

**Step 6: Verify**

```bash
cat output/hello.txt
# Hello from Terraform!
# This file was created by Infrastructure as Code.

cat output/app-config.json | python3 -m json.tool
# {
#     "application": "web-api",
#     "port": 8080,
#     ...
# }

ls terraform.tfstate
# terraform.tfstate exists — this is your state file
```

**Step 7: Experience idempotency**

```bash
terraform plan
# No changes. Your infrastructure matches the configuration.
```

**Step 8: Make a change**

Edit `main.tf` and change the port from 8080 to 9090:

```bash
terraform plan
```

Expected output:
```
  # local_file.config must be replaced
-/+ resource "local_file" "config" {
      ~ content              = jsonencode({ ... port = 8080 ... })
                               -> jsonencode({ ... port = 9090 ... })
      ~ id                   = "abc123" -> (known after apply)
        # (3 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.
```

Apply to update the file:
```bash
terraform apply -auto-approve
# -auto-approve skips the confirmation prompt (use in CI/CD, not production)
```

**Step 9: Destroy**

```bash
terraform destroy
```

Expected output:
```
Plan: 0 to add, 0 to change, 2 to destroy.

Do you really want to destroy all resources?
  Enter a value: yes

local_file.config: Destroying...
local_file.greeting: Destroying...
Destroy complete! Resources: 2 destroyed.
```

**Step 10: Examine what was created**

```bash
ls -la
# main.tf                    ← your configuration
# terraform.tfstate          ← state file (now shows 0 resources)
# terraform.tfstate.backup   ← backup of previous state
# .terraform/                ← provider binaries
# .terraform.lock.hcl        ← provider version lock
```

### Files You Should Know

| File | Purpose | Git? |
|------|---------|------|
| `*.tf` | Your Terraform configuration | Yes |
| `.terraform.lock.hcl` | Provider version lock | Yes |
| `terraform.tfstate` | State file | NO (use remote backend) |
| `terraform.tfstate.backup` | Previous state | NO |
| `.terraform/` | Provider binaries | NO (in .gitignore) |

### The .gitignore for Terraform Projects

```gitignore
# Local .terraform directories
**/.terraform/*

# State files (should use remote backend)
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# Variable definitions with secrets
*.tfvars
*.tfvars.json

# Override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# CLI config
.terraformrc
terraform.rc
```

---

## Exercises

### Exercise 1: Multi-File Configuration
Create a Terraform configuration that produces three local files: (a) an Nginx configuration file, (b) a Docker Compose YAML file, and (c) a README. Use `jsonencode` and `templatestring` or heredoc syntax as appropriate. Run the full init/plan/apply cycle.

### Exercise 2: Observe State Changes
After creating resources, open `terraform.tfstate` in a text editor. Find the resource IDs. Manually edit one of the created files (simulating drift). Run `terraform plan` and observe how Terraform detects the change. Run `terraform apply` to correct it.

### Exercise 3: Plan Reading Practice
Write a configuration with 5 `local_file` resources. Apply it. Then modify 2 files, delete 1 resource from the configuration, and add 1 new resource. Run `terraform plan` and identify which symbols (`+`, `-`, `~`, `-/+`) appear and why.

### Exercise 4: Version Constraints
Experiment with provider version constraints. Try `= 2.4.0`, `~> 2.0`, `>= 2.0, < 2.4`. Run `terraform init -upgrade` for each and observe which version is selected.

---

## Knowledge Check

### Question 1
What does `terraform init` do and when should you run it?

<details>
<summary>Answer</summary>

`terraform init` initializes a Terraform working directory. It downloads and installs the providers declared in your configuration, sets up the backend for state storage, and installs any modules referenced. You should run it when: (1) starting a new project for the first time, (2) adding or changing provider versions, (3) changing the backend configuration, (4) adding new module references, or (5) cloning an existing Terraform project. It is safe to run multiple times.
</details>

### Question 2
What is the difference between `terraform plan` and `terraform apply`?

<details>
<summary>Answer</summary>

`terraform plan` is a read-only operation that generates and displays an execution plan. It shows what Terraform would do (create, modify, or destroy resources) without actually making any changes. `terraform apply` performs the actual changes. By default, `apply` first runs a plan and asks for confirmation before proceeding. The `plan` step is critical for safety — it lets you verify that Terraform will do what you expect before committing to changes. In CI/CD pipelines, you typically run `plan` on pull requests (for review) and `apply` on merge to main.
</details>

### Question 3
Why should `terraform.tfstate` never be committed to Git?

<details>
<summary>Answer</summary>

The state file should not be in Git for several reasons: (1) it contains sensitive information — resource attributes often include passwords, access keys, private IPs, and other secrets in plain text; (2) concurrent modifications by multiple team members cause merge conflicts that corrupt the state; (3) Git does not provide state locking, so two people applying simultaneously could corrupt infrastructure; (4) the file changes on every apply, creating noisy diffs. Instead, state should be stored in a remote backend (S3 + DynamoDB for AWS, Azure Blob Storage, GCS, or Terraform Cloud) that provides encryption, locking, and access control.
</details>

### Question 4
What does the `-/+` symbol mean in a Terraform plan?

<details>
<summary>Answer</summary>

The `-/+` symbol means the resource must be destroyed and recreated (replaced). This happens when you change an attribute that cannot be updated in-place — the cloud provider requires the resource to be deleted and a new one created. For example, changing the AMI of an EC2 instance forces replacement because AWS cannot change the base image of a running instance. This is important to watch for because replacement causes downtime and may change resource IDs, IP addresses, and other attributes that other resources depend on.
</details>

### Question 5
What is the purpose of `.terraform.lock.hcl`?

<details>
<summary>Answer</summary>

`.terraform.lock.hcl` is the dependency lock file for Terraform providers. It records the exact version and cryptographic hashes of every provider that was selected during `terraform init`. This ensures that every team member and CI/CD pipeline uses identical provider versions, preventing "works on my machine" issues. It should be committed to Git. When you want to update provider versions, run `terraform init -upgrade` to update the lock file.
</details>
