# Infrastructure as Code: Philosophy and Foundations

## Why This Matters in DevOps

Every outage you will investigate in your career will eventually trace back to one question: "What changed?" In organizations that manage infrastructure manually — clicking through web consoles, running ad-hoc commands on servers — the answer is almost always "we don't know." Someone made a change on a Friday afternoon, didn't document it, and now the production database is unreachable.

Infrastructure as Code (IaC) exists because manual infrastructure management is fundamentally incompatible with modern software delivery. When you need to deploy to 15 regions, maintain parity between development and production, or recover from a disaster in minutes rather than days, you cannot rely on human memory and runbooks. IaC transforms infrastructure from a fragile, artisanal craft into a repeatable, auditable, version-controlled engineering discipline.

This is the single most important concept in modern DevOps. Every tool you learn after this — Terraform, Ansible, Kubernetes — is built on the assumption that infrastructure is defined in code.

---

## Core Concepts

### The Problem with Manual Infrastructure

Consider a typical growth scenario. You start with one server. You SSH in, install packages, configure services. Everything works. Then you need a second server. You try to remember what you did. You miss a step. The second server behaves differently. Now multiply this by 50 servers, 3 environments, and 4 team members.

Manual infrastructure fails because of:

- **Snowflake servers**: Each machine becomes unique, with undocumented changes accumulated over months
- **Configuration drift**: Environments that were once identical slowly diverge
- **Knowledge silos**: Only the person who built it knows how it works
- **Slow recovery**: Rebuilding from scratch takes days because no one remembers every step
- **No audit trail**: When something breaks, you cannot trace what changed
- **Human error**: Repetitive manual tasks guarantee mistakes

### What Infrastructure as Code Actually Means

IaC is the practice of managing and provisioning infrastructure through machine-readable definition files rather than manual processes. Your infrastructure — servers, networks, databases, load balancers, DNS records — is described in text files that are:

- **Version controlled**: Every change is tracked in Git
- **Reviewed**: Changes go through pull requests like application code
- **Tested**: You can validate infrastructure changes before applying them
- **Repeatable**: The same code produces the same infrastructure every time
- **Self-documenting**: The code IS the documentation of your infrastructure

### Imperative vs Declarative IaC

This is a fundamental distinction that shapes how you think about infrastructure.

**Imperative (procedural)**: You write step-by-step instructions telling the system HOW to reach the desired state.

```bash
# Imperative approach — a shell script
aws ec2 run-instances --image-id ami-0abcdef1234 --instance-type t3.micro
aws ec2 create-security-group --group-name web-sg --description "Web SG"
aws ec2 authorize-security-group-ingress --group-name web-sg --protocol tcp --port 80
```

Problems with imperative: What happens if you run this twice? You get two instances. What if the security group already exists? The script fails. You must handle every edge case yourself.

**Declarative**: You describe WHAT the desired end state should be, and the tool figures out how to get there.

```hcl
# Declarative approach — Terraform
resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234"
  instance_type = "t3.micro"
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Web SG"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

Run this once: it creates the resources. Run it again: it detects they already exist and does nothing. Change the instance type: it updates only what changed. This is the power of declarative IaC.

### Mutable vs Immutable Infrastructure

**Mutable infrastructure**: You update servers in place. You SSH in, run `apt upgrade`, change configurations. The server accumulates changes over time, like a pet you care for.

**Immutable infrastructure**: You never modify a running server. Instead, you build a new server image with the changes, deploy it, and destroy the old one. Servers are cattle, not pets.

```
Mutable (pets):        Deploy v1 → Patch → Patch → Patch → ???
Immutable (cattle):    Deploy v1 → Replace with v2 → Replace with v3
```

Immutable infrastructure eliminates configuration drift entirely. If every deployment is a fresh build from a known image, you always know exactly what is running.

In practice, most organizations use a hybrid: immutable for application servers (containers, VM images), mutable for stateful services that are harder to replace (databases, legacy systems).

### Idempotency

An operation is idempotent if applying it multiple times produces the same result as applying it once. This is critical for IaC because:

- Network failures may interrupt an apply halfway through
- Developers may accidentally run the same deployment twice
- CI/CD pipelines retry failed steps

Good IaC tools guarantee idempotency. Running `terraform apply` ten times with the same configuration produces the same infrastructure as running it once.

```
First apply:   No server exists → Create server    → 1 server running
Second apply:  1 server exists  → No changes needed → 1 server running
Third apply:   1 server exists  → No changes needed → 1 server running
```

### Drift Detection

Drift occurs when the actual state of your infrastructure diverges from the state defined in your code. Someone logs into the AWS console, manually adds a firewall rule, and now your code no longer represents reality.

Good IaC tools detect drift by comparing the desired state (your code) against the actual state (what exists in the cloud). Terraform does this on every `plan` and `apply`.

```
Your code says:        instance_type = "t3.micro"
Actual infrastructure: instance_type = "t3.large"  ← someone changed it manually

Terraform plan output:
  ~ instance_type = "t3.large" -> "t3.micro"  # will revert the manual change
```

### The IaC Tools Landscape

| Tool | Type | Language | Cloud Support | Model |
|------|------|----------|--------------|-------|
| **Terraform** | Provisioning | HCL | Multi-cloud | Declarative |
| **OpenTofu** | Provisioning | HCL | Multi-cloud | Declarative |
| **AWS CloudFormation** | Provisioning | JSON/YAML | AWS only | Declarative |
| **AWS CDK** | Provisioning | TypeScript/Python/etc | AWS primarily | Imperative→Declarative |
| **Pulumi** | Provisioning | TypeScript/Python/Go/etc | Multi-cloud | Imperative→Declarative |
| **Crossplane** | Provisioning | YAML (K8s CRDs) | Multi-cloud | Declarative |
| **Ansible** | Configuration | YAML | Multi-cloud | Declarative (procedural exec) |
| **Puppet** | Configuration | Puppet DSL | Any | Declarative |
| **Chef** | Configuration | Ruby | Any | Imperative |

### Why Terraform Became the Standard

Terraform achieved dominance for several practical reasons:

1. **Multi-cloud from day one**: One language (HCL) for AWS, Azure, GCP, and hundreds of other providers
2. **Provider ecosystem**: Over 3,000 providers covering everything from major clouds to DNS, monitoring, and databases
3. **Plan before apply**: The `terraform plan` command shows you exactly what will change before anything happens
4. **State management**: Terraform tracks what it created, enabling accurate diffs and safe updates
5. **HCL is purpose-built**: Unlike YAML or JSON, HCL was designed specifically for infrastructure definition — it supports variables, loops, conditionals, and functions
6. **Community and hiring**: The largest community means more examples, modules, and job opportunities
7. **Maturity**: Years of production use across thousands of organizations

That said, Terraform is not perfect. The HashiCorp BSL license change in 2023 and subsequent IBM acquisition led to the creation of OpenTofu as an open-source fork. We will cover this in detail in a later lesson.

---

## Step-by-Step Practical

### Visualizing the IaC Workflow

```
Developer writes infrastructure code
        │
        ▼
Code pushed to Git repository
        │
        ▼
Pull request created for review
        │
        ▼
CI pipeline runs: lint → validate → plan
        │
        ▼
Team reviews the plan output
        │
        ▼
PR merged to main branch
        │
        ▼
CD pipeline runs: terraform apply
        │
        ▼
Infrastructure updated to match code
        │
        ▼
State file updated with new reality
```

### Comparing Imperative and Declarative in Practice

Create a simple example to feel the difference.

**Imperative script (create-infra.sh):**

```bash
#!/bin/bash
set -e

# Check if the file already exists to avoid duplicates
if [ ! -f /tmp/iac-demo/config.json ]; then
    mkdir -p /tmp/iac-demo
    echo '{"app": "web", "port": 8080}' > /tmp/iac-demo/config.json
    echo "Created config.json"
else
    echo "config.json already exists, skipping"
fi

# What if we want to change the port?
# We need to add MORE logic to handle updates
# What if we want to delete it?
# We need EVEN MORE logic for teardown
```

**Declarative definition (main.tf):**

```hcl
resource "local_file" "config" {
  filename = "/tmp/iac-demo/config.json"
  content  = jsonencode({
    app  = "web"
    port = 8080
  })
}
```

With the declarative version:
- Run `terraform apply` → file is created
- Run `terraform apply` again → no changes (idempotent)
- Change port to 9090, run `terraform apply` → file is updated
- Run `terraform destroy` → file is deleted
- All of this is handled automatically

### Understanding Drift Detection

```bash
# After terraform creates a resource, simulate drift:
# 1. Terraform creates a file with content "Hello"
# 2. You manually edit the file to say "Hello World"
# 3. Run terraform plan
# 4. Terraform detects the drift and proposes to fix it

# Plan output would look like:
# ~ content = "Hello World" -> "Hello"
# Terraform wants to revert your manual change to match the code
```

### Evaluating IaC Tools for Your Organization

Ask these questions when choosing an IaC tool:

```
1. What clouds do we use?
   - Single cloud (AWS) → CloudFormation or CDK are valid
   - Multi-cloud → Terraform, OpenTofu, or Pulumi

2. What does our team know?
   - DevOps/Ops background → Terraform (HCL is approachable)
   - Developer background → Pulumi or CDK (use familiar languages)

3. How important is open source?
   - Critical → OpenTofu, Pulumi (community edition)
   - Not critical → Terraform, CloudFormation

4. What scale are we operating at?
   - Small → Any tool works
   - Large → Terraform/OpenTofu (mature ecosystem, modules)

5. Do we need Kubernetes-native?
   - Yes → Consider Crossplane
   - No → Terraform/OpenTofu
```

---

## Exercises

### Exercise 1: Categorize Your Current Infrastructure
List 10 pieces of infrastructure at your organization (or a hypothetical one). For each, identify: (a) is it currently managed as code? (b) what tool manages it? (c) what would happen if you needed to rebuild it from scratch? How long would it take?

### Exercise 2: Imperative to Declarative Translation
Take the following imperative script and describe what the equivalent declarative configuration would look like (pseudocode is fine):

```bash
#!/bin/bash
aws s3 mb s3://my-app-logs-bucket
aws s3api put-bucket-versioning --bucket my-app-logs-bucket --versioning-configuration Status=Enabled
aws s3api put-bucket-lifecycle-configuration --bucket my-app-logs-bucket --lifecycle-configuration '{
  "Rules": [{"ID": "expire-old", "Status": "Enabled", "Expiration": {"Days": 90}}]
}'
```

### Exercise 3: Drift Scenario Analysis
A junior engineer manually changed a security group in the AWS console to add port 22 access for debugging. Describe: (a) how this drift would be detected, (b) what Terraform would propose, (c) what the correct process should have been, (d) how to prevent this from happening again.

### Exercise 4: Tool Selection
Your company runs workloads on AWS and Azure, has a team of 5 DevOps engineers who know Python, and needs to manage 200+ microservices. Evaluate Terraform, Pulumi, and CloudFormation. Which would you recommend and why?

### Exercise 5: Mutable vs Immutable Decision
For each of the following, decide whether mutable or immutable infrastructure is more appropriate and explain why: (a) stateless API servers, (b) PostgreSQL database cluster, (c) machine learning training instances, (d) developer sandbox environments.

---

## Knowledge Check

### Question 1
What is the key difference between imperative and declarative IaC?

<details>
<summary>Answer</summary>

Imperative IaC describes the specific steps (HOW) to reach a desired state — "create this, then configure that, then enable this." Declarative IaC describes the desired end state (WHAT) — "I want a server with these properties" — and the tool determines the steps needed to get there. Declarative IaC is preferred because it handles idempotency, updates, and drift correction automatically, whereas imperative scripts require you to code all that logic yourself.
</details>

### Question 2
Why is idempotency critical for Infrastructure as Code?

<details>
<summary>Answer</summary>

Idempotency ensures that applying the same configuration multiple times produces the same result as applying it once. This is critical because: (1) network failures may interrupt operations, requiring retries, (2) CI/CD pipelines may run the same deployment multiple times, (3) multiple team members may apply the same configuration, and (4) drift correction requires re-applying the desired state without creating duplicates. Without idempotency, you risk creating duplicate resources, conflicting configurations, or failed deployments.
</details>

### Question 3
What is configuration drift and why is it dangerous?

<details>
<summary>Answer</summary>

Configuration drift occurs when the actual state of infrastructure diverges from the state defined in code. This happens when someone makes manual changes (through a web console, SSH, or API calls) outside of the IaC workflow. It is dangerous because: (1) your code no longer represents reality, making it unreliable as documentation, (2) applying the code may revert critical manual fixes, (3) you cannot accurately reproduce the environment, (4) debugging becomes harder because the running configuration is unknown, and (5) disaster recovery fails because rebuilding from code produces different infrastructure than what was actually running.
</details>

### Question 4
When would you choose mutable infrastructure over immutable infrastructure?

<details>
<summary>Answer</summary>

Mutable infrastructure is appropriate for: (1) stateful services like databases where replacing the instance means data migration, (2) long-running systems where the cost of full replacement is prohibitive, (3) legacy applications that are difficult to containerize or reimage, and (4) development environments where speed of iteration matters more than reproducibility. Immutable infrastructure is preferred for stateless application servers, containers, and any system where you can afford to replace rather than update, because it eliminates configuration drift entirely.
</details>

### Question 5
Why did Terraform achieve market dominance over alternatives like CloudFormation and Puppet?

<details>
<summary>Answer</summary>

Terraform achieved dominance because: (1) it was multi-cloud from inception, unlike CloudFormation which is AWS-only, (2) HCL is a purpose-built language that is more readable than JSON/YAML for infrastructure, (3) the plan-before-apply workflow provides safety and visibility, (4) the provider ecosystem grew to cover thousands of services, (5) state management enables accurate change detection, (6) it occupies the provisioning layer (creating infrastructure) rather than configuration management (configuring servers), filling a gap that Puppet and Chef did not address, and (7) strong community adoption created a network effect in hiring, documentation, and shared modules.
</details>
