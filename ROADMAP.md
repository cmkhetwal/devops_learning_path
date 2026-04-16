# DevOps & Cloud Learning Path — Complete Curriculum

## Overview

A structured, methodology-first learning path covering 20 modules across 4 phases.
Each lesson teaches the **WHY** (methodology) before the **HOW** (tool), with step-by-step practicals.

**No prerequisites** — Phase 1 starts from zero programming knowledge.

---

## Phase 1: Python for DevOps (Weeks 1-12) — BUILD YOUR FOUNDATION

A 90-day, 12-week Python course designed specifically for DevOps.
Located in `phase_1_python/`.

| Weeks | Topics | Format |
|-------|--------|--------|
| 1-4 | Variables, control flow, data structures, functions, modules | Daily lesson + exercise + auto-checker |
| 5-8 | File handling, JSON/YAML, error handling, OS automation, APIs, OOP, testing | Daily lesson + exercise + auto-checker |
| 9-12 | Docker SDK, AWS boto3, Git automation, CI/CD, Prometheus, Flask, capstone | Daily lesson + exercise + auto-checker |

**84 daily lessons** with exercises and auto-grading checkers + weekly quizzes + progress tracker.

```bash
# Start here
cat phase_1_python/ROADMAP.md
cat phase_1_python/week_01/day_1/lesson.md
python3 phase_1_python/week_01/day_1/check.py    # Check your answers
python3 phase_1_python/tracker.py                  # Track progress
python3 phase_1_python/quiz.py 1                   # Weekly quiz
```

---

## Phase 2: Core Skills (Months 4-9) — GET A JOB

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

## Total: 220 lessons (84 Python + 136 DevOps) across 4 phases and 20 modules

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
# If you're a complete beginner — start with Phase 1 (Python)
cat phase_1_python/week_01/day_1/lesson.md

# If you already know Python — start with Phase 2 (Linux & Bash)
cat phase_2_core/01_linux_bash/01_linux_fundamentals.md

# Work through each lesson sequentially
# Practice every command shown
# Complete exercises before moving on
```
