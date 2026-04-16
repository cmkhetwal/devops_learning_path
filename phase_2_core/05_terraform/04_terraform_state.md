# Terraform State Management

## Why This Matters in DevOps

The state file is both Terraform's greatest strength and its most dangerous liability. It is the single source of truth that maps your code to real infrastructure. Without it, Terraform cannot determine what exists, what changed, or what to delete. Mismanage state, and you will either lose track of infrastructure (orphaned resources costing money) or accidentally destroy production.

Every Terraform incident you will hear about in your career involves state: someone deleted the state file, two engineers applied simultaneously and corrupted it, or secrets leaked because state was stored insecurely. Understanding state management is not optional — it is the difference between a reliable infrastructure platform and a ticking time bomb.

---

## Core Concepts

### Why State Matters

Terraform state serves four critical functions:

1. **Mapping code to reality**: Your config says `resource "aws_instance" "web"`. State records that this corresponds to EC2 instance `i-0abc123def456`. Without this mapping, Terraform would try to create a new instance every time.

2. **Tracking metadata**: Dependencies between resources, provider configurations, and resource ordering information.

3. **Performance**: For large infrastructures, Terraform can query state instead of making API calls to every cloud resource on every plan. (Use `terraform refresh` to sync state with reality.)

4. **Collaboration**: Remote state allows teams to share a single source of truth about what infrastructure exists.

### Local State

By default, Terraform stores state in `terraform.tfstate` in your working directory. This is fine for learning but dangerous for teams.

```json
{
  "version": 4,
  "terraform_version": "1.9.0",
  "serial": 5,
  "lineage": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "outputs": {
    "instance_ip": {
      "value": "54.210.167.99",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "web",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "id": "i-0abc123def456",
            "ami": "ami-0c55b159cbfafe1f0",
            "instance_type": "t3.micro",
            "public_ip": "54.210.167.99",
            "private_ip": "10.0.1.42"
          }
        }
      ]
    }
  ]
}
```

Problems with local state:
- **No collaboration**: Only the person with the file can run Terraform
- **No locking**: Two simultaneous applies corrupt the file
- **No encryption**: Secrets are stored in plain text on disk
- **No backup**: Disk failure loses your state
- **Accidental commit**: Easy to push to Git (it should NEVER be in Git)

### Remote State

Remote state stores `terraform.tfstate` in a shared, durable location with locking.

**AWS S3 + DynamoDB (the industry standard):**

```hcl
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/networking/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}
```

**What each component does:**
- **S3 bucket**: Stores the state file with versioning (so you can recover previous versions)
- **encrypt = true**: Enables server-side encryption (SSE-S3 or SSE-KMS)
- **DynamoDB table**: Provides state locking — only one person can modify state at a time
- **key**: The path within the bucket — use it to organize state files by environment and component

### State Locking

State locking prevents concurrent modifications. When you run `terraform apply`, Terraform acquires a lock. If someone else tries to apply, they see:

```
Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException: The conditional request failed
Lock Info:
  ID:        a1b2c3d4-e5f6-7890
  Path:      mycompany-terraform-state/prod/networking/terraform.tfstate
  Operation: OperationTypeApply
  Who:       engineer@laptop
  Version:   1.9.0
  Created:   2024-01-15 14:30:00.000000 UTC
```

If a lock is stuck (the process crashed), you can force-unlock:

```bash
# DANGEROUS — only use when you are certain no one else is applying
terraform force-unlock LOCK_ID
```

### Setting Up the Remote Backend (AWS)

**Step 1: Create the S3 bucket and DynamoDB table (bootstrap):**

This is a chicken-and-egg problem — you need infrastructure to store state for infrastructure. The bootstrap resources are typically created manually or with a separate, locally-stated Terraform config.

```hcl
# bootstrap/main.tf — run this ONCE with local state
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "mycompany-terraform-state"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

**Step 2: Configure your project to use the remote backend:**

```hcl
# In your project's main.tf
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/web-app/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}
```

**Step 3: Migrate from local to remote:**

```bash
terraform init
# Terraform detects the backend change:
# Initializing the backend...
# Do you want to copy existing state to the new backend? (yes/no)
# Enter a value: yes
# Successfully configured the backend "s3"!
```

### State Commands

Terraform provides commands to inspect and manipulate state directly. Use these carefully — incorrect state manipulation can orphan or destroy resources.

```bash
# List all resources in state
terraform state list
# aws_instance.web
# aws_security_group.web
# aws_s3_bucket.logs

# Show details of a specific resource
terraform state show aws_instance.web
# resource "aws_instance" "web" {
#     ami           = "ami-0c55b159cbfafe1f0"
#     instance_type = "t3.micro"
#     id            = "i-0abc123def456"
#     public_ip     = "54.210.167.99"
# }

# Move a resource (rename in state without destroying/recreating)
terraform state mv aws_instance.web aws_instance.application
# This is useful when you refactor your code (rename a resource)
# without wanting to destroy and recreate the actual infrastructure

# Remove a resource from state (Terraform forgets about it)
terraform state rm aws_instance.legacy
# The real infrastructure continues to exist — Terraform just stops managing it
# Useful when you want to hand off management to another tool

# Pull remote state to local file (for inspection)
terraform state pull > state_backup.json

# Push local state to remote (DANGEROUS)
terraform state push state_backup.json
```

### Importing Existing Resources

When you have infrastructure that was created manually (or by another tool) and you want Terraform to manage it:

```bash
# Step 1: Write the resource block in your .tf file
# resource "aws_instance" "legacy_server" {
#   # Will be filled in after import
# }

# Step 2: Import the resource into state
terraform import aws_instance.legacy_server i-0abc123def456

# Step 3: Run terraform plan to see what needs to change
terraform plan
# Terraform shows the diff between the imported resource's actual
# configuration and what your .tf file says

# Step 4: Update your .tf file to match reality
# (so that terraform plan shows no changes)
```

**Terraform 1.5+ import blocks (declarative import):**

```hcl
import {
  to = aws_instance.legacy_server
  id = "i-0abc123def456"
}

resource "aws_instance" "legacy_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
}
```

```bash
# Generate configuration for imported resources
terraform plan -generate-config-out=generated.tf
```

### State File Security

**The state file contains secrets.** This is not a theoretical concern. Terraform stores resource attributes in state, and many attributes contain sensitive data:

- Database passwords (stored in `aws_db_instance` attributes)
- TLS private keys (from `tls_private_key` resources)
- IAM access keys (from `aws_iam_access_key` resources)
- API tokens and connection strings
- Private IP addresses and internal DNS names

**Security measures:**
1. Never commit state to Git (use `.gitignore`)
2. Enable encryption on your S3 bucket (SSE-KMS preferred)
3. Restrict access to the S3 bucket with IAM policies
4. Enable versioning for state recovery
5. Enable access logging on the S3 bucket
6. Use `sensitive = true` on outputs (hides from CLI, still in state)
7. Consider Terraform Cloud for enhanced state security features

### Workspaces vs Directory Structure

Terraform offers two approaches for managing multiple environments:

**Workspaces (built-in):**

```bash
terraform workspace list
# * default

terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

terraform workspace select prod
terraform workspace show
# prod

# Use in code
resource "aws_instance" "web" {
  instance_type = terraform.workspace == "prod" ? "t3.large" : "t3.micro"

  tags = {
    Environment = terraform.workspace
  }
}
```

Each workspace has its own state file, stored at `env:/workspace-name/terraform.tfstate` in the backend.

**Directory structure (widely preferred):**

```
infrastructure/
  modules/
    vpc/
    ec2/
    rds/
  environments/
    dev/
      main.tf        ← calls modules with dev-specific values
      backend.tf     ← points to dev state file
      terraform.tfvars
    staging/
      main.tf
      backend.tf
      terraform.tfvars
    prod/
      main.tf
      backend.tf
      terraform.tfvars
```

**Why directories are preferred over workspaces:**
- Each environment has its own state file with a separate backend key
- You can apply to dev without any risk of accidentally applying to prod
- Each environment can use different provider versions or module versions
- Code review is clearer — PRs show which environment changes
- blast radius is limited — a mistake in dev cannot affect prod state

---

## Step-by-Step Practical

### Demonstrating State Operations with Local Provider

```bash
mkdir -p ~/terraform-lab/04-state && cd ~/terraform-lab/04-state
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

resource "local_file" "app_config" {
  filename = "${path.module}/output/app.conf"
  content  = "server.port=8080\nserver.host=0.0.0.0\n"
}

resource "local_file" "db_config" {
  filename = "${path.module}/output/db.conf"
  content  = "db.host=localhost\ndb.port=5432\ndb.name=myapp\n"
}

resource "local_file" "cache_config" {
  filename = "${path.module}/output/cache.conf"
  content  = "redis.host=localhost\nredis.port=6379\n"
}
```

```bash
# Initialize and apply
terraform init
terraform apply -auto-approve

# List resources in state
terraform state list
# local_file.app_config
# local_file.cache_config
# local_file.db_config

# Show a specific resource
terraform state show local_file.app_config

# Simulate a refactoring — rename a resource
# In main.tf, rename "app_config" to "application_config"
# Then move it in state to avoid destroy/recreate:
terraform state mv local_file.app_config local_file.application_config
# Move "local_file.app_config" to "local_file.application_config"
# Successfully moved 1 object(s).

# Remove a resource from state (Terraform forgets it)
terraform state rm local_file.cache_config
# Removed local_file.cache_config
# The file still exists on disk, but Terraform no longer manages it

terraform state list
# local_file.application_config
# local_file.db_config
```

### Workspace Demonstration

```bash
mkdir -p ~/terraform-lab/04-workspaces && cd ~/terraform-lab/04-workspaces
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
  config = {
    default = { log_level = "debug", replicas = 1 }
    dev     = { log_level = "debug", replicas = 1 }
    staging = { log_level = "info",  replicas = 2 }
    prod    = { log_level = "warn",  replicas = 3 }
  }

  env = local.config[terraform.workspace]
}

resource "local_file" "env_config" {
  filename = "${path.module}/output/${terraform.workspace}.json"
  content = jsonencode({
    environment = terraform.workspace
    log_level   = local.env.log_level
    replicas    = local.env.replicas
  })
}
```

```bash
terraform init
terraform apply -auto-approve
# Creates output/default.json

terraform workspace new dev
terraform apply -auto-approve
# Creates output/dev.json

terraform workspace new prod
terraform apply -auto-approve
# Creates output/prod.json

terraform workspace list
#   default
#   dev
# * prod

# Each workspace has its own state
ls terraform.tfstate.d/
# dev/  prod/
```

---

## Exercises

### Exercise 1: State Inspection
Create a configuration with 5 different `local_file` resources. Apply it. Use `terraform state list`, `terraform state show`, and examine `terraform.tfstate` directly to understand the state structure. Identify where resource IDs, attributes, and dependencies are stored.

### Exercise 2: State Migration Simulation
Start with local state. Create a second directory to act as a "remote" backend (use the `local` backend with a custom path). Migrate your state from the default location to the custom path using `terraform init -migrate-state`. Verify the old state file is gone and the new one exists.

### Exercise 3: Import Practice
Create a file manually on disk. Then write a Terraform `local_file` resource for it and use `terraform import` to bring it under management. Run `terraform plan` to verify zero changes.

### Exercise 4: Workspace Environment Separation
Using workspaces, create a configuration that generates different outputs for dev, staging, and prod. Deploy to all three workspaces and verify that each has independent state and resources.

### Exercise 5: State Recovery
Apply a configuration, then deliberately corrupt the state file (change a resource ID). Run `terraform plan` and observe the error. Restore from `terraform.tfstate.backup` and verify recovery.

---

## Knowledge Check

### Question 1
Why does Terraform need a state file? What problems would occur without it?

<details>
<summary>Answer</summary>

Terraform needs state to: (1) map resource names in code to real infrastructure IDs — without it, Terraform cannot determine that `aws_instance.web` corresponds to `i-0abc123`, so it would try to create a new instance on every apply; (2) track dependencies and ordering between resources; (3) store computed attributes (like IP addresses) that are not in the code but are needed by other resources; (4) improve performance by caching resource data instead of querying every API on every plan. Without state, Terraform would either create duplicates on every apply or have to make expensive API calls to discover all existing infrastructure and attempt to match it to code.
</details>

### Question 2
What is state locking and why is it necessary?

<details>
<summary>Answer</summary>

State locking prevents multiple Terraform processes from modifying state simultaneously. Without locking, if two engineers run `terraform apply` at the same time, both read the same state, both make changes, and whichever writes last overwrites the other's changes — potentially orphaning resources or creating duplicates. Locking is implemented by the backend: S3 uses a DynamoDB table where Terraform writes a lock record before modifying state and deletes it afterward. If a lock exists, other operations wait or fail. Force-unlock (`terraform force-unlock`) should only be used when you are certain no other process is running.
</details>

### Question 3
When should you use `terraform state mv` versus destroying and recreating a resource?

<details>
<summary>Answer</summary>

Use `terraform state mv` when you are refactoring your Terraform code (renaming a resource, moving it to a module, or reorganizing your project structure) but the actual infrastructure should not change. For example, renaming `aws_instance.web` to `aws_instance.application` in your code would normally cause Terraform to destroy the old instance and create a new one. Using `terraform state mv aws_instance.web aws_instance.application` updates the state mapping without touching real infrastructure. This avoids downtime, data loss, and unnecessary changes. Only destroy and recreate when you actually need a new resource.
</details>

### Question 4
Why do most teams prefer directory-based environment separation over Terraform workspaces?

<details>
<summary>Answer</summary>

Directory-based separation is preferred because: (1) each environment has completely isolated state, eliminating any risk of accidentally applying prod changes in a dev workspace; (2) environments can use different provider versions, module versions, or even different Terraform versions; (3) code review is clearer — a PR shows exactly which environment's directory changed; (4) you cannot accidentally forget to switch workspaces (a common error); (5) blast radius is limited — a bug in the dev configuration cannot corrupt prod state; (6) CI/CD pipelines are simpler with separate directories and backend keys. Workspaces are appropriate for simpler use cases like testing the same configuration against multiple identical environments.
</details>

### Question 5
What sensitive data exists in Terraform state files and how should you protect them?

<details>
<summary>Answer</summary>

State files contain every attribute of every managed resource, including: database passwords, IAM access keys and secret keys, TLS private keys, API tokens, connection strings, internal IP addresses, and any other attribute that a provider returns. To protect state: (1) never commit it to Git, (2) use a remote backend with server-side encryption (S3 with SSE-KMS), (3) restrict access to the state bucket with IAM policies, (4) enable bucket versioning for recovery, (5) enable access logging to audit who reads state, (6) use Terraform Cloud or similar products that provide additional access controls, (7) mark outputs as `sensitive = true` to prevent accidental display (though the value is still in state).
</details>
