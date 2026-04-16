# OpenTofu: The Open-Source Fork of Terraform

## Why This Matters in DevOps

In August 2023, HashiCorp changed Terraform's license from the Mozilla Public License (MPL 2.0) — a permissive open-source license — to the Business Source License (BSL 1.1), which restricts commercial use. This was one of the most consequential events in the DevOps ecosystem. Within weeks, a coalition of companies and individuals forked Terraform into OpenTofu under the Linux Foundation, guaranteeing it would remain truly open source forever.

Then in 2024, IBM acquired HashiCorp for $6.4 billion, adding another layer of uncertainty about Terraform's future direction. Understanding this landscape is critical because you will encounter both tools in your career: existing organizations running Terraform, new projects considering OpenTofu, and active debates about which to choose. You need to understand the technical differences, the political context, and the practical migration path.

---

## Core Concepts

### Why OpenTofu Exists

**The timeline:**

```
2014       Terraform created by HashiCorp under MPL 2.0 (open source)
2014-2023  Terraform grows to dominate IaC, community builds providers/modules
Aug 2023   HashiCorp switches to BSL 1.1 license
Aug 2023   "OpenTF" manifesto signed by 100+ companies
Sep 2023   OpenTofu announced as a fork under Linux Foundation
Jan 2024   OpenTofu 1.6.0 released (first stable release)
Apr 2024   IBM acquires HashiCorp for $6.4 billion
2024-2025  Both projects continue development with diverging features
```

**The BSL license change explained:**

The BSL 1.1 license prohibits using Terraform to build products that compete with HashiCorp's commercial offerings (Terraform Cloud, HCP Terraform). This affects:

- Companies building internal IaC platforms that could be seen as competing with Terraform Cloud
- Managed service providers offering Terraform-as-a-service
- Companies embedding Terraform in their own products
- Potentially any commercial use that HashiCorp deems competitive

What it does NOT affect:
- Using Terraform to manage your own infrastructure (most users)
- Using Terraform in your CI/CD pipelines
- Using Terraform for consulting/professional services

However, the concern is broader than immediate impact. Many organizations build long-term infrastructure strategies, and relying on a tool whose license terms could be reinterpreted or tightened creates strategic risk.

**The OpenTofu response:**

OpenTofu is Terraform forked at version 1.5.x (the last MPL-licensed version), placed under the Linux Foundation with a commitment to the MPL 2.0 license. The Linux Foundation provides governance that prevents any single company from changing the license.

### Differences from Terraform

As of 2025, OpenTofu and Terraform are largely compatible but diverging:

**What is the same:**
- HCL syntax is identical
- State file format is compatible
- Most providers work with both
- Core workflow (init/plan/apply/destroy) is the same
- Module format is identical
- Registry modules are compatible

**Where OpenTofu has diverged:**

```
Feature                    | Terraform  | OpenTofu
---------------------------|------------|------------------
License                    | BSL 1.1    | MPL 2.0
State encryption           | No (native)| Yes (native)
Early variable/locals eval | No         | Yes
Provider-defined functions | Different  | Different approach
Registry                   | registry.terraform.io | registry.opentofu.org
CLI binary                 | terraform  | tofu
Governance                 | HashiCorp  | Linux Foundation
```

**State encryption** is OpenTofu's flagship differentiator. Terraform stores state with secrets in plain text (relying on backend encryption). OpenTofu can encrypt state at the application level:

```hcl
# OpenTofu state encryption
terraform {
  encryption {
    key_provider "pbkdf2" "mykey" {
      passphrase = var.state_passphrase
    }

    method "aes_gcm" "encrypt" {
      keys = key_provider.pbkdf2.mykey
    }

    state {
      method = method.aes_gcm.encrypt
    }

    plan {
      method = method.aes_gcm.encrypt
    }
  }
}
```

### The IBM Acquisition Factor

IBM's acquisition of HashiCorp adds uncertainty to Terraform's future:

- **Potential positives**: More resources, enterprise integration, long-term stability
- **Potential concerns**: IBM's history with acquisitions (Red Hat has maintained independence, but Softlayer and others were absorbed), potential focus shift toward IBM Cloud, possible further license restrictions, slower open-source community engagement

This is not about predicting the future — it is about managing risk. Organizations evaluate:
- Will Terraform remain the best tool for their needs?
- Is vendor lock-in to a single company (now IBM-owned) acceptable?
- Does the open-source foundation backing of OpenTofu provide better long-term assurance?

### Community vs Corporate Control

```
Terraform (Corporate-controlled):
  HashiCorp (now IBM) decides:
    - Feature roadmap
    - License terms
    - Which contributions to accept
    - Pricing for Terraform Cloud
    - When to deprecate features

OpenTofu (Community-governed):
  Linux Foundation provides:
    - Neutral governance
    - License protection (cannot be changed by one entity)
    - Community steering committee
    - Multiple contributing companies
    - Transparent RFC process
```

### When to Choose OpenTofu vs Terraform

**Choose Terraform when:**
- Your organization already uses Terraform extensively
- You use Terraform Cloud or HCP Terraform
- Your team has Terraform expertise and certifications
- The BSL license does not affect your use case
- You need the largest ecosystem of existing modules and examples
- Stability and backward compatibility are paramount

**Choose OpenTofu when:**
- Starting a new project with no existing Terraform investment
- Open-source licensing is a business requirement
- You need state encryption as a native feature
- You are building a product or platform that might compete with Terraform Cloud
- Your organization has a policy against BSL-licensed software
- You want governance guarantees against future license changes

**The pragmatic answer:**
For most individual DevOps engineers in 2025, the choice makes little practical difference. The syntax is the same, the skills transfer completely, and you can switch between them relatively easily. Learn the concepts and workflow — they apply to both.

---

## Step-by-Step Practical

### Installing OpenTofu

**Linux (Ubuntu/Debian):**

```bash
# Install via snap
sudo snap install --classic opentofu

# Or via install script
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh
chmod +x install-opentofu.sh
./install-opentofu.sh --install-method deb
rm install-opentofu.sh

# Verify
tofu version
# OpenTofu v1.8.x
```

**macOS:**

```bash
brew install opentofu
```

### Migration from Terraform to OpenTofu

**Step 1: Verify compatibility**

```bash
# Check your Terraform version — OpenTofu forked from 1.5.x
terraform version
# If you are on Terraform 1.5.x or 1.6.x, migration is straightforward

# Check for HashiCorp-specific features that may not be supported
# (These are rare — most configs work without changes)
```

**Step 2: Install OpenTofu alongside Terraform**

```bash
# Both can coexist on the same system
which terraform    # /usr/bin/terraform
which tofu         # /usr/bin/tofu
```

**Step 3: Initialize with OpenTofu**

```bash
cd your-terraform-project

# OpenTofu reads the same .tf files
tofu init

# Expected output (note: downloads from OpenTofu registry)
# Initializing the backend...
# Initializing provider plugins...
# - Finding hashicorp/aws versions matching "~> 5.0"...
# - Installing hashicorp/aws v5.x.x...
# OpenTofu has been successfully initialized!
```

**Step 4: Verify state compatibility**

```bash
# OpenTofu reads Terraform state files
tofu plan
# Should show "No changes. Your infrastructure matches the configuration."
# If it shows changes, investigate before applying
```

**Step 5: Update CI/CD pipelines**

```yaml
# Before (GitHub Actions with Terraform)
- name: Setup Terraform
  uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: 1.9.0

- name: Terraform Plan
  run: terraform plan

# After (GitHub Actions with OpenTofu)
- name: Setup OpenTofu
  uses: opentofu/setup-opentofu@v1
  with:
    tofu_version: 1.8.0

- name: OpenTofu Plan
  run: tofu plan
```

**Step 6: Update lock files**

```bash
# Delete the existing lock file and regenerate
rm .terraform.lock.hcl
tofu init

# Commit the new lock file
git add .terraform.lock.hcl
git commit -m "Migrate from Terraform to OpenTofu"
```

### Same Infrastructure with OpenTofu

The following configuration is identical to what you would write in Terraform. That is the point — the HCL is the same.

```hcl
# main.tf — works with both `terraform` and `tofu` commands
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
  required_version = ">= 1.5.0"
}

resource "local_file" "demo" {
  filename = "${path.module}/output/opentofu-demo.txt"
  content  = <<-EOT
    This infrastructure was provisioned by OpenTofu.
    The HCL syntax is identical to Terraform.
    The workflow (init/plan/apply/destroy) is identical.
    The state format is compatible.

    The key difference is governance and licensing.
  EOT
}

output "file_path" {
  value = local_file.demo.filename
}
```

```bash
# Run with OpenTofu
tofu init
tofu plan
tofu apply -auto-approve

# Verify
cat output/opentofu-demo.txt

# Now try running the same config with Terraform (if installed)
# terraform init
# terraform plan
# Same result — the configs are interchangeable
```

### Using OpenTofu State Encryption

This is a feature only available in OpenTofu:

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = "my-secret-passphrase"  # In practice, use a variable
    }

    method "aes_gcm" "main" {
      keys = key_provider.pbkdf2.main
    }

    state {
      method = method.aes_gcm.main
    }
  }

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

resource "local_file" "sensitive" {
  filename = "${path.module}/output/sensitive.txt"
  content  = "This content is protected by encrypted state"
}
```

```bash
tofu init
tofu apply -auto-approve

# Examine the state file — it is encrypted!
cat terraform.tfstate
# You will see encrypted binary data instead of readable JSON
```

### Comparing Terraform and OpenTofu Side by Side

```bash
# Create two directories with identical configs
mkdir -p ~/tofu-comparison/{terraform,opentofu}

# Copy the same main.tf to both
cp main.tf ~/tofu-comparison/terraform/
cp main.tf ~/tofu-comparison/opentofu/

# In terraform directory
cd ~/tofu-comparison/terraform
terraform init && terraform plan

# In opentofu directory
cd ~/tofu-comparison/opentofu
tofu init && tofu plan

# Compare outputs — they should be functionally identical
```

---

## Exercises

### Exercise 1: Side-by-Side Installation
Install both Terraform and OpenTofu on your system. Create the same configuration and deploy it with each tool separately. Compare: initialization output, plan output, state file format, and .terraform directory contents. Document every difference you find.

### Exercise 2: State Encryption
Create an OpenTofu configuration with state encryption enabled. Deploy some resources. Examine the state file and verify it is encrypted. Try to read the state with Terraform (it will fail). Discuss what this means for state security.

### Exercise 3: Migration Assessment
Review an existing Terraform project (or create one with 10+ resources across VPC, EC2, S3, and IAM). Write a migration plan that covers: (a) compatibility check, (b) testing strategy, (c) CI/CD pipeline updates, (d) rollback plan if migration fails, (e) team training needs.

### Exercise 4: License Impact Analysis
For each of the following scenarios, determine whether the BSL license would affect the use case: (a) a startup using Terraform to manage its AWS infrastructure, (b) a consulting firm building infrastructure for clients, (c) a company building an internal developer platform with a Terraform wrapper, (d) a SaaS company offering automated infrastructure provisioning that runs Terraform under the hood.

### Exercise 5: Feature Comparison
Research the latest release notes for both Terraform and OpenTofu. Identify three features that exist in one but not the other. For each, explain whether the feature would be relevant to a mid-size organization running 50 microservices on AWS.

---

## Knowledge Check

### Question 1
Why did HashiCorp change Terraform's license, and what was the community response?

<details>
<summary>Answer</summary>

HashiCorp changed from MPL 2.0 to BSL 1.1 because competitors were offering managed Terraform services that directly competed with HashiCorp's commercial products (Terraform Cloud) without contributing back to the project. The BSL restricts using Terraform to build competitive products. The community response was swift: over 100 companies signed the "OpenTF manifesto" calling for a return to open source. When HashiCorp did not reverse the decision, the community forked Terraform into OpenTofu under the Linux Foundation, which provides governance guarantees that the license cannot be changed by a single entity. This was one of the largest and fastest open-source forks in history.
</details>

### Question 2
Can you use Terraform state files with OpenTofu and vice versa?

<details>
<summary>Answer</summary>

Yes, as of the current versions, Terraform and OpenTofu state files are compatible. OpenTofu can read and write Terraform state files, and you can migrate from Terraform to OpenTofu without recreating infrastructure — just run `tofu init` and `tofu plan` to verify. However, if you use OpenTofu's state encryption feature, the encrypted state files cannot be read by Terraform. As both projects continue to diverge, future compatibility is not guaranteed, so migration should be tested thoroughly and performed deliberately rather than assumed.
</details>

### Question 3
What is the practical significance of OpenTofu's state encryption feature?

<details>
<summary>Answer</summary>

OpenTofu's native state encryption encrypts the state file at the application level before it is stored, so even if someone gains access to the storage backend (S3 bucket, filesystem), they cannot read the state contents. This matters because Terraform state files contain sensitive data (database passwords, API keys, private IPs) in plain text. With Terraform, you rely solely on backend-level encryption (S3 SSE, for example), meaning anyone with bucket access can read the state. OpenTofu's encryption adds a layer where the state is encrypted before it leaves the client, requiring a decryption key to read. This is particularly important for organizations with strict compliance requirements.
</details>

### Question 4
If you are starting a brand-new DevOps role at a company with no existing IaC, which would you recommend and why?

<details>
<summary>Answer</summary>

This depends on context, but a strong argument exists for either: Choose OpenTofu if open-source licensing is important to the organization, you want long-term governance guarantees, or you are building a platform that might be affected by BSL restrictions. Choose Terraform if the team values the largest ecosystem of documentation, examples, and community support, if you want access to Terraform Cloud/HCP Terraform features, or if the team has existing Terraform certifications. The pragmatic recommendation is that both tools use the same language (HCL) and same concepts, so the skills transfer completely. Make the decision based on licensing needs and existing tooling, not technical differences. Document the rationale so the team can revisit the decision as both projects evolve.
</details>
