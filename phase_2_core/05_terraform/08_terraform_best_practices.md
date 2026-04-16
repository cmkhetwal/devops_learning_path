# Terraform Best Practices

## Why This Matters in DevOps

You can write Terraform that works. You can also write Terraform that works today and becomes an unmaintainable, insecure liability in six months. The difference is following established best practices — directory structure, code quality tools, security scanning, and CI/CD integration.

These practices are not theoretical. They are hard-won lessons from organizations that learned the expensive way: a flat directory with 200 resources and a 30-second plan time, a production outage from unvalidated Terraform, a security audit failure from unscanned infrastructure code. This lesson codifies what mature teams do, so you can start with good habits instead of learning from your own mistakes.

---

## Core Concepts

### Directory Structure for Large Projects

**Small project (1-2 environments, < 20 resources):**

```
project/
  main.tf
  variables.tf
  outputs.tf
  versions.tf
  terraform.tfvars
  .gitignore
```

**Medium project (multiple environments, 20-100 resources):**

```
project/
  modules/
    vpc/
      main.tf, variables.tf, outputs.tf
    compute/
      main.tf, variables.tf, outputs.tf
    database/
      main.tf, variables.tf, outputs.tf
  environments/
    dev/
      main.tf, backend.tf, terraform.tfvars
    staging/
      main.tf, backend.tf, terraform.tfvars
    prod/
      main.tf, backend.tf, terraform.tfvars
  .gitignore
```

**Large project (many teams, 100+ resources, multi-account):**

```
infrastructure/
  modules/                          # Shared, versioned modules
    networking/
    compute/
    database/
    monitoring/
    security/
  live/                             # Actual deployments
    account-prod/
      us-east-1/
        vpc/
          main.tf, backend.tf, terragrunt.hcl
        ecs-cluster/
          main.tf, backend.tf
        databases/
          main.tf, backend.tf
      us-west-2/
        vpc/
          main.tf, backend.tf
    account-staging/
      us-east-1/
        vpc/
          main.tf, backend.tf
    account-dev/
      us-east-1/
        vpc/
          main.tf, backend.tf
  global/                           # Resources that span accounts
    iam/
    route53/
    cloudfront/
```

**Key principle: Each directory has its own state.** A VPC change should never risk your database state. Blast radius isolation is the primary driver of directory structure.

### Environment Separation

**The wrong way (workspaces for environments):**

```bash
terraform workspace select prod
terraform apply
# One typo and you are applying to production
# One bug in any resource affects all environments
# Cannot test module upgrades in dev before prod
```

**The right way (separate directories):**

```
environments/dev/backend.tf:
  backend "s3" {
    bucket = "mycompany-tfstate"
    key    = "dev/infrastructure/terraform.tfstate"
  }

environments/prod/backend.tf:
  backend "s3" {
    bucket = "mycompany-tfstate"
    key    = "prod/infrastructure/terraform.tfstate"
  }
```

Each environment has its own state file, its own backend key, and can even use different module versions:

```hcl
# dev uses latest module version for testing
module "vpc" {
  source  = "../../modules/vpc"
  # ...
}

# prod uses a pinned, tested version
module "vpc" {
  source  = "git::https://github.com/myorg/modules.git//vpc?ref=v2.1.0"
  # ...
}
```

### Code Quality Tools

**terraform fmt — automatic formatting:**

```bash
# Check formatting (returns non-zero if files need formatting)
terraform fmt -check -recursive

# Auto-format all .tf files
terraform fmt -recursive

# Show what would change
terraform fmt -diff -recursive
```

Always run `terraform fmt` before committing. Add it to your pre-commit hooks.

**terraform validate — syntax and logic checking:**

```bash
terraform init -backend=false  # Init without backend (for CI)
terraform validate

# Example output for a valid config:
# Success! The configuration is valid.

# Example output for an invalid config:
# Error: Reference to undeclared variable
#   on main.tf line 5:
#   An input variable with the name "regon" has not been declared.
#   Did you mean "region"?
```

**tflint — Terraform linter:**

tflint catches errors that `terraform validate` misses, including provider-specific issues like invalid instance types.

```bash
# Install
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Create .tflint.hcl configuration
cat > .tflint.hcl << 'EOF'
plugin "aws" {
  enabled = true
  version = "0.31.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_naming_convention" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_documented_outputs" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}
EOF

# Run
tflint --init
tflint

# Example findings:
# Warning: instance_type is not a valid value (main.tf:12)
#   resource "aws_instance" "web" {
#     instance_type = "t3.micr"  ← typo!
# Warning: variable "old_var" is declared but not used (variables.tf:20)
```

**checkov — security scanning:**

Checkov scans Terraform code for security misconfigurations against hundreds of policies.

```bash
# Install
pip install checkov

# Scan
checkov -d . --framework terraform

# Example output:
# Passed checks: 12, Failed checks: 3, Skipped checks: 0
#
# Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
#   FAILED for resource: aws_s3_bucket.assets
#   File: /main.tf:45-50
#
# Check: CKV_AWS_145: "Ensure that S3 Bucket is encrypted by KMS"
#   FAILED for resource: aws_s3_bucket.assets
#   File: /main.tf:45-50
#
# Check: CKV_AWS_8: "Ensure all data stored in the Launch configuration EBS is encrypted"
#   PASSED for resource: aws_instance.web

# Scan with specific checks
checkov -d . --check CKV_AWS_18,CKV_AWS_145

# Skip specific checks (with justification)
checkov -d . --skip-check CKV_AWS_18  # Access logging handled by org-level policy
```

### CI/CD Integration

**The standard Terraform CI/CD pattern:**

```
PR Created / Updated:
  1. terraform fmt -check
  2. terraform init -backend=false
  3. terraform validate
  4. tflint
  5. checkov
  6. terraform plan (with actual backend)
  7. Post plan output as PR comment

PR Merged to main:
  8. terraform plan (verify again)
  9. terraform apply -auto-approve
```

**GitHub Actions workflow:**

```yaml
name: Terraform CI/CD

on:
  pull_request:
    paths:
      - 'infrastructure/**'
  push:
    branches: [main]
    paths:
      - 'infrastructure/**'

permissions:
  contents: read
  pull-requests: write
  id-token: write  # For OIDC

env:
  TF_VERSION: "1.9.0"
  WORKING_DIR: "infrastructure/environments/prod"

jobs:
  validate:
    name: Validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        working-directory: infrastructure/

      - name: Terraform Init
        run: terraform init -backend=false
        working-directory: ${{ env.WORKING_DIR }}

      - name: Terraform Validate
        run: terraform validate
        working-directory: ${{ env.WORKING_DIR }}

      - name: TFLint
        uses: terraform-linters/setup-tflint@v4
        with:
          tflint_version: latest
      - run: |
          tflint --init
          tflint
        working-directory: ${{ env.WORKING_DIR }}

      - name: Checkov Security Scan
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: ${{ env.WORKING_DIR }}
          framework: terraform
          soft_fail: false

  plan:
    name: Plan
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/TerraformCI
          aws-region: us-east-1

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -out=tfplan
        working-directory: ${{ env.WORKING_DIR }}

      - name: Comment Plan on PR
        uses: actions/github-script@v7
        with:
          script: |
            const plan = `${{ steps.plan.outputs.stdout }}`;
            const truncated = plan.length > 60000
              ? plan.substring(0, 60000) + "\n\n... (truncated)"
              : plan;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan\n\`\`\`\n${truncated}\n\`\`\``
            });

  apply:
    name: Apply
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production  # Requires approval
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/TerraformCD
          aws-region: us-east-1

      - name: Terraform Apply
        run: |
          terraform init
          terraform apply -auto-approve
        working-directory: ${{ env.WORKING_DIR }}
```

### Common Mistakes and Anti-Patterns

**1. Hardcoding values:**

```hcl
# BAD
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  subnet_id     = "subnet-abc123"
}

# GOOD
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_ids[0]
}
```

**2. Monolithic configurations:**

```
# BAD — everything in one directory with one state file
infrastructure/
  main.tf          # 2000 lines, VPC + EC2 + RDS + S3 + IAM + ...

# GOOD — separated by component
infrastructure/
  networking/main.tf    # VPC, subnets, route tables
  compute/main.tf       # EC2, ASG, launch templates
  database/main.tf      # RDS, ElastiCache
  storage/main.tf       # S3, EFS
```

**3. Not using remote state:**

```hcl
# BAD — state on local disk
# (no backend block)

# GOOD — state in S3 with locking
terraform {
  backend "s3" {
    bucket         = "mycompany-tfstate"
    key            = "prod/web/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

**4. Ignoring lifecycle rules:**

```hcl
# BAD — database can be accidentally destroyed
resource "aws_db_instance" "prod" {
  # ...
}

# GOOD — prevent accidental destruction
resource "aws_db_instance" "prod" {
  # ...
  deletion_protection = true

  lifecycle {
    prevent_destroy = true
  }
}
```

**5. Overly broad security groups:**

```hcl
# BAD — open to the world
ingress {
  from_port   = 0
  to_port     = 65535
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

# GOOD — specific ports and sources
ingress {
  from_port       = 8080
  to_port         = 8080
  protocol        = "tcp"
  security_groups = [aws_security_group.alb.id]
}
```

**6. Not tagging resources:**

```hcl
# BAD — no tags
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}

# GOOD — comprehensive tags (use default_tags in provider)
provider "aws" {
  default_tags {
    tags = {
      Environment = var.environment
      Team        = var.team
      ManagedBy   = "terraform"
      CostCenter  = var.cost_center
    }
  }
}
```

**7. Secrets in Terraform code:**

```hcl
# BAD — secrets in code
resource "aws_db_instance" "prod" {
  password = "SuperSecret123!"
}

# GOOD — secrets from external sources
resource "aws_db_instance" "prod" {
  password = data.aws_ssm_parameter.db_password.value
}

# Or use random_password
resource "random_password" "db" {
  length  = 32
  special = true
}

resource "aws_db_instance" "prod" {
  password = random_password.db.result
}
```

### Terraform Associate Certification Prep

The HashiCorp Terraform Associate certification validates your foundational Terraform knowledge. Key areas:

```
Exam Domains:
  1. Understand IaC concepts (what we covered in lesson 01)
  2. Understand Terraform's purpose (vs other IaC tools)
  3. Understand Terraform basics (init/plan/apply, providers, state)
  4. Use Terraform outside of core workflow (import, workspaces, debugging)
  5. Interact with Terraform modules (registry, writing modules)
  6. Use the core Terraform workflow (write, plan, apply)
  7. Implement and maintain state (remote state, locking, backends)
  8. Read, generate, and modify configuration (HCL, variables, outputs)
  9. Understand Terraform Cloud (free tier features)

Preparation Tips:
  - Practice with real infrastructure, not just reading docs
  - Know the CLI commands and their flags
  - Understand state concepts deeply
  - Know the variable precedence order
  - Understand module versioning and sources
  - Practice with Terraform Cloud free tier
  - Take the official practice exam
```

---

## Step-by-Step Practical

### Setting Up a Complete Terraform Development Workflow

```bash
mkdir -p ~/terraform-lab/best-practices && cd ~/terraform-lab/best-practices
```

**Step 1: Pre-commit hooks**

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.92.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
        args:
          - '--args=--config=__GIT_WORKING_DIR__/.tflint.hcl'
      - id: terraform_docs
        args:
          - '--args=--config=.terraform-docs.yml'
      - id: terraform_checkov
        args:
          - '--args=--quiet'
EOF

# Install the hooks
pre-commit install
```

**Step 2: Create a proper .gitignore**

```bash
cat > .gitignore << 'EOF'
**/.terraform/*
*.tfstate
*.tfstate.*
crash.log
crash.*.log
*.tfvars
*.tfvars.json
override.tf
override.tf.json
*_override.tf
*_override.tf.json
.terraformrc
terraform.rc
.terraform.lock.hcl
EOF
```

**Step 3: Run the full quality check**

```bash
# Format check
terraform fmt -check -recursive

# Initialize (backend=false for validation only)
terraform init -backend=false

# Validate
terraform validate

# Lint
tflint --init && tflint

# Security scan
checkov -d . --framework terraform --compact

# All checks pass? Ready to commit and push.
```

**Step 4: Makefile for consistency**

```makefile
# Makefile
.PHONY: init plan apply destroy fmt validate lint security

ENV ?= dev

init:
	cd environments/$(ENV) && terraform init

plan:
	cd environments/$(ENV) && terraform plan

apply:
	cd environments/$(ENV) && terraform apply

destroy:
	cd environments/$(ENV) && terraform destroy

fmt:
	terraform fmt -recursive

validate:
	@for dir in environments/*/; do \
		echo "Validating $$dir..."; \
		cd $$dir && terraform init -backend=false && terraform validate && cd ../..; \
	done

lint:
	tflint --recursive

security:
	checkov -d . --framework terraform --compact

check: fmt validate lint security
	@echo "All checks passed!"
```

```bash
# Usage
make check         # Run all quality checks
make plan ENV=dev  # Plan for dev
make apply ENV=prod # Apply to production
```

---

## Exercises

### Exercise 1: Project Structure Design
Design a directory structure for a company with: 3 environments (dev, staging, prod), 2 AWS accounts (non-prod, prod), 3 regions (us-east-1, eu-west-1, ap-southeast-1), and services including VPC, EKS, RDS, and S3. Explain your decisions for state isolation.

### Exercise 2: Security Scanning Pipeline
Set up checkov on an existing Terraform project. Run a scan, analyze the findings, and fix at least 3 security issues. For any findings you choose to skip, document the justification using inline skip comments.

### Exercise 3: Pre-Commit Setup
Configure pre-commit hooks for a Terraform project that enforce: formatting, validation, linting, and documentation generation. Test by deliberately introducing formatting errors and invalid configurations.

### Exercise 4: CI/CD Pipeline
Write a complete GitHub Actions workflow that handles Terraform for a project with dev and prod environments. Include: format check, validation, linting, security scan, plan on PRs, and apply on merge. Handle the prod environment with an approval gate.

### Exercise 5: Anti-Pattern Audit
Review the following Terraform code and identify all anti-patterns, security issues, and improvement opportunities. Rewrite it following best practices.

```hcl
resource "aws_instance" "server" {
  ami = "ami-12345"
  instance_type = "t3.micro"
  security_groups = ["sg-all-open"]
  key_name = "my-key"
  user_data = "#!/bin/bash\napt install mysql-client\nmysql -h db.prod -u admin -p Password123"
  tags = {
    Name = "server"
  }
}

resource "aws_db_instance" "db" {
  engine = "mysql"
  instance_class = "db.t3.micro"
  password = "Password123"
  publicly_accessible = true
  skip_final_snapshot = true
}
```

---

## Knowledge Check

### Question 1
Why should Terraform configurations be split into separate state files by component?

<details>
<summary>Answer</summary>

Splitting into separate state files provides blast radius isolation. If all resources share one state, a bug in an EC2 change could corrupt the state for your database or VPC. With separate state files: (1) a failed apply to compute cannot affect networking state, (2) plan times are faster because Terraform only checks the resources in that state, (3) access control is granular — the team managing databases does not need access to networking state, (4) parallel development is easier — teams can apply to their own components without blocking each other, (5) state locking is less contentious with smaller scopes.
</details>

### Question 2
What is the difference between `terraform validate` and `tflint`?

<details>
<summary>Answer</summary>

`terraform validate` checks for syntax errors, invalid references, type mismatches, and internal consistency of the configuration. It catches errors that would prevent Terraform from creating a plan. `tflint` goes further: it checks provider-specific rules (e.g., "t3.micr" is not a valid AWS instance type), enforces naming conventions, detects deprecated syntax, finds unused variables and declarations, and can enforce organization-specific rules. Think of `validate` as "will this parse correctly?" and `tflint` as "is this actually correct and well-written?" Both should be used together in CI/CD.
</details>

### Question 3
What is checkov and what types of issues does it detect?

<details>
<summary>Answer</summary>

Checkov is a static analysis tool for infrastructure as code that checks for security and compliance misconfigurations. It scans Terraform configurations against hundreds of built-in policies covering: unencrypted storage (S3 without encryption, EBS without encryption), overly permissive security groups (0.0.0.0/0 access), missing access logging, public exposure of resources (publicly accessible RDS, S3 public access), missing backup configurations, IAM policy issues, and compliance requirements (CIS benchmarks, SOC2, HIPAA). It does not run Terraform or access cloud APIs — it analyzes the code statically. Failed checks should either be fixed or explicitly skipped with documented justification.
</details>

### Question 4
Describe the ideal Terraform CI/CD pipeline and explain why each step matters.

<details>
<summary>Answer</summary>

The ideal pipeline has two phases. On PR: (1) `terraform fmt -check` ensures consistent formatting across the team, (2) `terraform validate` catches syntax errors before wasting time on later steps, (3) `tflint` catches provider-specific errors and enforces standards, (4) `checkov` scans for security misconfigurations before they reach production, (5) `terraform plan` shows the exact changes that will be made, posted as a PR comment for review. On merge to main: (6) `terraform plan` runs again to verify the plan is still valid, (7) `terraform apply -auto-approve` executes the changes. The prod apply should require manual approval through an environment protection rule. OIDC authentication should be used instead of long-lived credentials. Each step catches different classes of errors, from formatting to security to actual infrastructure changes.
</details>

### Question 5
What are three common Terraform anti-patterns and how do you fix them?

<details>
<summary>Answer</summary>

(1) Hardcoded values: Using literal AMI IDs, subnet IDs, or IP addresses makes code non-portable and fragile. Fix by using data sources for AMIs, variables for configurable values, and module outputs for cross-reference. (2) Monolithic configurations: Putting all resources in a single state makes plans slow, increases blast radius, and creates team bottlenecks. Fix by splitting into components (networking, compute, database) with separate state files. (3) Secrets in code: Putting passwords, API keys, or tokens directly in .tf files means they are committed to Git in plain text. Fix by using external secret sources (SSM Parameter Store, Secrets Manager, Vault), `random_password` for generated credentials, or environment variables in CI/CD.
</details>
