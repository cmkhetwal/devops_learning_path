# DevOps & Cloud Learning Path — Complete Curriculum

## Overview

A structured, methodology-first learning path covering 20 modules across 3 phases.
Each lesson teaches the **WHY** (methodology) before the **HOW** (tool), with step-by-step practicals.

**Prerequisites**: Basic Python knowledge (complete the `devops-python-path` first)

---

## Phase 2: Core Skills (Months 1-6) — GET A JOB

| # | Module | Lessons | Duration | Key Methodology |
|---|--------|---------|----------|-----------------|
| 01 | Linux & Bash | 10 | 3 weeks | System administration, automation mindset |
| 02 | Git | 5 | 1 week | Version control, collaboration workflows |
| 03 | Docker | 10 | 3 weeks | Containerization, microservices philosophy |
| 04 | Kubernetes | 14 | 4 weeks | Container orchestration, declarative infrastructure |
| 05 | Terraform | 8 | 2.5 weeks | Infrastructure as Code (IaC) methodology |
| 06 | GitHub Actions | 6 | 2 weeks | CI/CD philosophy, pipeline design |
| 07 | Ansible | 8 | 2.5 weeks | Configuration management, idempotency |

## Phase 3: Production Skills (Months 6-12) — STAND OUT

| # | Module | Lessons | Duration | Key Methodology |
|---|--------|---------|----------|-----------------|
| 08 | AWS | 12 | 4 weeks | Cloud architecture, Well-Architected Framework |
| 09 | GitOps (ArgoCD) | 6 | 2 weeks | GitOps principles, progressive delivery |
| 10 | Observability | 10 | 3 weeks | Observability vs monitoring, SRE principles |
| 11 | Helm | 5 | 1.5 weeks | Package management, templating |
| 12 | Cilium & eBPF | 4 | 1 week | Kernel-level networking, zero-trust |
| 13 | DevSecOps | 6 | 2 weeks | Shift-left security, supply chain |

## Phase 4: Advanced (Months 12-18) — SENIOR LEVEL

| # | Module | Lessons | Duration | Key Methodology |
|---|--------|---------|----------|-----------------|
| 14 | Crossplane & Pulumi | 6 | 2 weeks | K8s-native IaC, multi-cloud |
| 15 | Karpenter | 3 | 1 week | Intelligent autoscaling |
| 16 | Secrets Management | 5 | 1.5 weeks | Zero-trust secrets, rotation |
| 17 | Platform Engineering | 5 | 1.5 weeks | Internal Developer Platforms |
| 18 | FinOps | 4 | 1 week | Cloud cost optimization |
| 19 | Dagger | 4 | 1 week | Programmable CI/CD |
| 20 | AI in DevOps | 5 | 1.5 weeks | AIOps, autonomous operations |

---

## Total: 136 lessons across 20 modules

## How to Use This Path

1. Go through lessons IN ORDER — each builds on previous knowledge
2. Each lesson file contains:
   - **Why This Matters** — methodology and philosophy
   - **Core Concepts** — theory you need to understand
   - **Step-by-Step Practical** — hands-on commands to run
   - **Exercises** — practice on your own
   - **Knowledge Check** — verify your understanding
3. Don't skip the methodology sections — understanding WHY is more important than HOW
4. Practice each lesson before moving to the next

## Lesson File Format

```
module_folder/
├── 01_topic_name.md      # Lesson 1
├── 02_topic_name.md      # Lesson 2
├── ...
└── practice/             # Config files, scripts, manifests (where needed)
```

---

## Certification Alignment

| Certification | Modules That Prepare You |
|--------------|--------------------------|
| AWS Solutions Architect Associate | 08 (AWS) |
| CKA (Kubernetes Admin) | 04 (K8s), 11 (Helm), 12 (Cilium) |
| Terraform Associate | 05 (Terraform) |
| GitOps Certified Associate | 09 (GitOps) |
| FinOps Practitioner | 18 (FinOps) |

---

## Quick Start

```bash
# Start with Module 01
cat phase_2_core/01_linux_bash/01_linux_fundamentals.md

# Work through each lesson sequentially
# Practice every command shown
# Complete exercises before moving on
```
