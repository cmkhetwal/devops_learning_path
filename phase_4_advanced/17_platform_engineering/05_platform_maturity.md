# Platform Maturity

## Why This Matters in DevOps

Platform Engineering fails when teams try to build everything at once. The most common mistake is building a sophisticated IDP before understanding what developers actually need. Successful platforms start small, prove value quickly, and grow incrementally based on feedback. Understanding maturity models, product management thinking, and common pitfalls helps you avoid the multi-month projects that deliver platforms nobody uses. This lesson provides the strategic framework for building platforms that succeed.

---

## Core Concepts

### Platform Maturity Model

```
Level 0: Ad-Hoc                Level 1: Managed
──────────────────              ──────────────────
No platform team                Dedicated platform team
Each team builds own infra      Shared CI/CD templates
Inconsistent tooling            Standard monitoring
No self-service                 Basic self-service (wiki)
Tribal knowledge                Some documentation

Level 2: Standardized           Level 3: Optimized
──────────────────────          ──────────────────
Golden paths exist              Full self-service IDP
Service catalog (Backstage)     Automated everything
GitOps deployment               Cost optimization built-in
Crossplane self-service         AI-assisted operations
Comprehensive docs              Platform as a product

Timeline to reach each level:
L0 → L1: 3-6 months
L1 → L2: 6-12 months
L2 → L3: 12-24 months
```

**Detailed Maturity Assessment:**

```yaml
maturity_assessment:
  infrastructure_provisioning:
    level_0: "Ticket to ops team, days to provision"
    level_1: "Terraform run by platform team, hours"
    level_2: "Crossplane Claims, self-service, minutes"
    level_3: "Backstage template, fully automated, seconds"

  deployment:
    level_0: "Manual SSH, scripts, or Jenkins freestyle"
    level_1: "Standardized CI/CD, manual triggers"
    level_2: "GitOps (ArgoCD), automated per environment"
    level_3: "Progressive delivery, canary, automated rollback"

  monitoring:
    level_0: "No monitoring or ad-hoc scripts"
    level_1: "Prometheus + Grafana, manual dashboard creation"
    level_2: "Auto-discovery, standard dashboards per service"
    level_3: "Anomaly detection, AI-assisted root cause analysis"

  documentation:
    level_0: "Tribal knowledge, Slack messages"
    level_1: "Wiki (Confluence), sometimes outdated"
    level_2: "TechDocs in Backstage, docs-as-code"
    level_3: "Living documentation, auto-generated API docs"

  security:
    level_0: "Secrets in .env files, no scanning"
    level_1: "Vault for secrets, manual scanning"
    level_2: "Automated scanning in CI, policy enforcement"
    level_3: "Zero-trust, automated remediation, supply chain security"
```

### Starting Small

The "Minimum Viable Platform" approach:

```
Month 1: Pick ONE pain point
────────────────────────────
Ask: "What wastes the most developer time?"
Common answers:
  - "Setting up CI/CD for new services" → Reusable workflows
  - "Deploying takes too long" → ArgoCD
  - "No idea what services exist" → Backstage catalog

Build ONE solution. Prove value. Get feedback.

Month 2-3: Expand based on feedback
────────────────────────────────────
"The CI/CD templates are great, but now I need
 to provision databases too" → Add Crossplane

Month 4-6: Integrate
─────────────────────
Connect the pieces:
  Backstage → creates repo → CI/CD → ArgoCD → Crossplane

DO NOT try to build all of this in Month 1.
```

### Platform Product Management

Treat the platform as a product with internal customers:

```
Product Management Framework:
─────────────────────────────

1. User Research
   - Interview 10+ developers
   - Shadow developers for a day
   - Review support tickets and Slack questions
   - Analyze where developers waste time

2. Product Roadmap
   ┌─────────────────────────────────────────────────┐
   │  Q1: Foundation                                 │
   │  ├── Service catalog (Backstage)               │
   │  └── CI/CD templates (GitHub Actions)          │
   ├─────────────────────────────────────────────────┤
   │  Q2: Self-Service                               │
   │  ├── GitOps deployment (ArgoCD)                │
   │  └── Database provisioning (Crossplane)        │
   ├─────────────────────────────────────────────────┤
   │  Q3: Observability                              │
   │  ├── Monitoring dashboards                      │
   │  └── Alerting integration                       │
   ├─────────────────────────────────────────────────┤
   │  Q4: Optimization                               │
   │  ├── Cost visibility (Kubecost)                │
   │  └── Software templates                         │
   └─────────────────────────────────────────────────┘

3. Success Metrics
   - Adoption rate > 70% within 6 months
   - Developer NPS > 30
   - Time to first deployment < 1 day (from > 2 weeks)
   - Deployment frequency: 2x improvement

4. Feedback Loop
   - Monthly platform office hours
   - Quarterly developer surveys
   - Continuous Slack channel monitoring
   - Backstage plugin for feedback collection
```

### Getting Buy-In

```
Stakeholder                 What They Care About          How to Pitch
─────────────────────────────────────────────────────────────────────────
CTO / VP Engineering        Developer velocity,           "Reduce time to
                            competitive advantage          market by 50%"

Engineering Managers         Team productivity,            "Your team spends
                            fewer incidents                40% less time on
                                                          infrastructure"

Developers                  Less toil,                    "Create a new service
                            better tools                   in 30 minutes,
                                                          not 2 weeks"

Finance / CFO               Cost reduction                "30% cloud cost
                                                          savings through
                                                          standardization"

Security / CISO             Compliance,                   "Every service
                            fewer vulnerabilities          automatically scans
                                                          for vulnerabilities"
```

### Building a Platform Team

```yaml
platform_team:
  size: "Start with 2-3 engineers, grow to 5-8"

  recommended_roles:
    - title: "Platform Tech Lead"
      skills: ["Kubernetes", "IaC", "CI/CD", "architecture"]
      focus: "Technical direction, architecture decisions"

    - title: "Platform Engineer (Infrastructure)"
      skills: ["Kubernetes", "Crossplane/Terraform", "AWS/GCP"]
      focus: "Self-service infrastructure, Karpenter, networking"

    - title: "Platform Engineer (Developer Experience)"
      skills: ["Backstage", "GitHub Actions", "TypeScript"]
      focus: "Developer portal, templates, CI/CD pipelines"

    - title: "Platform Engineer (Observability)"
      skills: ["Prometheus", "Grafana", "Loki", "OpenTelemetry"]
      focus: "Monitoring, logging, tracing, alerting"

    - title: "Platform Product Manager (part-time)"
      skills: ["Product management", "user research"]
      focus: "Roadmap, stakeholder management, metrics"

  anti_patterns:
    - "Platform team becomes a ticket queue"
    - "Platform team mandates instead of enabling"
    - "Building features nobody asked for"
    - "Perfectionism before launching MVP"
    - "No user research, just assumptions"
```

### Common Pitfalls

```
Pitfall                          Solution
─────────────────────────────────────────────────────────────────
Over-engineering from day 1      Start with MVP, iterate based
                                 on feedback

Building without user research   Interview developers FIRST,
                                 then build what they need

Mandating instead of enabling    Make golden path the easiest
                                 option, not the only option

Ignoring documentation          No docs = no adoption;
                                 invest 20% of time in docs

Trying to support everything    Focus on 80% use case;
                                 support exceptions manually

No success metrics               Define metrics before building;
                                 measure continuously

Platform team as bottleneck      Self-service is the goal;
                                 if teams need you, automate it

Copy-pasting another company    Every org is different;
                                 learn from others, adapt to yours
```

### Case Studies

**Spotify**: Created Backstage to manage 2000+ microservices. Key lesson: the catalog came first, templates second. They solved discoverability before they solved provisioning.

**Netflix**: Built extensive internal tooling (Spinnaker for deployment, Zuul for routing). Key lesson: Netflix engineers were expected to own operations, so the platform reduced cognitive load without removing responsibility.

**Airbnb**: Built a service framework ("Thrift Service Framework") that standardized how services were built. Key lesson: standardization before tooling. When all services look the same, building tools for them is easier.

### The Future of Platforms

```
2024-2025: Current State
├── Backstage becoming the standard portal
├── ArgoCD/Flux dominant for GitOps
├── Crossplane growing for infrastructure abstraction
└── Platform Engineering becoming a career path

2025-2027: Near Future
├── AI-powered platform features (auto-generated docs,
│   intelligent incident response, code review)
├── Platform orchestration tools (Humanitec, Kratix)
├── Score (CNCF) for workload specification
└── Platform-as-a-Product becomes expected

2027+: Predictions
├── Natural language platform interaction
│   ("deploy my service to production")
├── Self-optimizing platforms (auto-scale, auto-tune)
├── Platforms that write their own golden paths
└── Developer experience as competitive advantage
```

---

## Step-by-Step Practical

### Creating a Platform Maturity Assessment

**Step 1: Assess Current State**

```yaml
# platform-maturity-assessment.yaml
organization: "MyCompany"
date: "2026-04-16"
assessor: "Platform Team"

dimensions:
  service_catalog:
    current_level: 0
    evidence: "No central catalog; teams maintain their own docs"
    target_level: 2
    gap: "Need to implement Backstage and register all services"

  deployment:
    current_level: 1
    evidence: "Standardized GitHub Actions but manual promotion"
    target_level: 2
    gap: "Need ArgoCD for GitOps deployment"

  infrastructure_provisioning:
    current_level: 0
    evidence: "All provisioning via tickets to ops team"
    target_level: 2
    gap: "Need Crossplane for self-service"

  monitoring:
    current_level: 1
    evidence: "Prometheus installed but dashboards are manual"
    target_level: 2
    gap: "Need auto-discovery and standard dashboard templates"

  secrets:
    current_level: 0
    evidence: "Secrets in .env files and GitHub Secrets"
    target_level: 2
    gap: "Need Vault or Infisical"

  documentation:
    current_level: 0
    evidence: "Scattered Confluence pages, mostly outdated"
    target_level: 2
    gap: "Need TechDocs in Backstage, docs-as-code"

overall_maturity_score: 0.5  # (0+1+0+1+0+0) / 6 dimensions, 0-3 scale
target_maturity_score: 2.0
timeline_to_target: "12 months"
```

**Step 2: Create an Action Plan**

```yaml
# platform-action-plan.yaml
quarter_1:
  theme: "Foundation"
  deliverables:
    - "Deploy Backstage, register all 30 services"
    - "Create CI/CD template library (Python, Node.js)"
    - "Hire 2nd platform engineer"
  success_criteria:
    - "100% of services in Backstage catalog"
    - "50% of repos using CI/CD templates"
    - "Developer NPS baseline established"

quarter_2:
  theme: "Self-Service Deployment"
  deliverables:
    - "Deploy ArgoCD for GitOps"
    - "Migrate 10 services to ArgoCD"
    - "Create first Backstage Software Template"
  success_criteria:
    - "10 services deployed via ArgoCD"
    - "New services created via template in < 1 hour"
    - "Deployment frequency increases 2x"

quarter_3:
  theme: "Self-Service Infrastructure"
  deliverables:
    - "Deploy Crossplane on production cluster"
    - "Create Database and Cache claims"
    - "Deploy Vault for secrets management"
  success_criteria:
    - "Developers can provision databases without tickets"
    - "All secrets managed by Vault"
    - "Infrastructure lead time < 10 minutes"

quarter_4:
  theme: "Optimization"
  deliverables:
    - "Deploy Kubecost for cost visibility"
    - "Build DORA metrics dashboard"
    - "Create comprehensive documentation"
  success_criteria:
    - "Per-team cost attribution enabled"
    - "DORA metrics tracked and improving"
    - "Developer NPS > 30"
```

---

## Exercises

1. **Maturity Assessment**: Conduct a platform maturity assessment for your organization using the framework above. Score each dimension, identify the biggest gaps, and create a 90-day action plan.

2. **MVP Definition**: Define a Minimum Viable Platform for a 10-person startup. What is the absolute minimum set of capabilities needed? Design it to be implementable in 2 weeks by one engineer.

3. **Buy-In Presentation**: Create a 10-slide presentation pitching a platform engineering initiative to your CTO. Include: current problems (with data), proposed solution, timeline, required investment, expected ROI.

4. **Platform Team Charter**: Write a team charter for a new platform team. Include: mission, scope, team composition, interaction model with other teams, success metrics, and what the team will NOT do.

5. **Post-Mortem Analysis**: Research a platform engineering failure (or imagine one). Identify what went wrong, which pitfalls were hit, and what should have been done differently.

---

## Knowledge Check

**Q1: Why should platform engineering start small?**

<details>
<summary>Answer</summary>

Starting small reduces risk and builds momentum: (1) You learn what developers actually need through real usage, not assumptions. (2) You demonstrate value quickly, which builds organizational support and funding. (3) You avoid building features nobody uses -- a common failure mode where teams spend months building a comprehensive platform that does not match developer needs. (4) You get feedback early and can course-correct before investing heavily. (5) Small wins create advocates -- developers who benefit from the first feature become champions for the platform. The recommended approach is to solve one painful problem in the first month, prove the ROI, and then expand.
</details>

**Q2: What is the difference between treating a platform as a project vs. a product?**

<details>
<summary>Answer</summary>

A project has a start date, end date, and defined deliverables. A product is ongoing, evolves based on user feedback, and is never "done." When treated as a project: the team builds what was scoped, delivers it, and moves on. There is no feedback loop, no iteration, and no maintenance. When treated as a product: the team continuously interviews users, prioritizes a backlog, measures adoption and satisfaction, and iterates. They have a roadmap that evolves. The platform has a "product manager" who advocates for users. Treating a platform as a product is critical because developer needs change over time, and a static platform quickly becomes irrelevant.
</details>

**Q3: What are the most common reasons platform engineering initiatives fail?**

<details>
<summary>Answer</summary>

Five common failure modes: (1) **Over-engineering** -- building a comprehensive platform before understanding needs, resulting in months of work that misses the mark. (2) **No user research** -- assuming what developers need instead of asking them, leading to features nobody uses. (3) **Mandating instead of enabling** -- forcing developers to use the platform instead of making it the obviously better option. (4) **Ignoring documentation** -- building tools without explaining how to use them. (5) **Platform team as bottleneck** -- becoming a ticket queue instead of providing self-service, which recreates the old ops model. The root cause is usually treating the platform as a technical project rather than a product with users who have choices.
</details>

**Q4: How do you measure platform ROI to justify continued investment?**

<details>
<summary>Answer</summary>

Measure ROI across four areas: (1) **Time savings** -- multiply time saved per developer per week by number of developers and hourly cost. Example: 2 hours/week saved * 80 developers * $75/hour = $12,000/week savings. (2) **Speed improvements** -- track DORA metrics before and after. If lead time drops from 5 days to 2 hours, quantify the business value of faster delivery. (3) **Incident reduction** -- fewer misconfigurations and inconsistencies mean fewer incidents. Track incident count and MTTR improvements. (4) **Cloud cost optimization** -- standardized infrastructure (right-sizing, spot instances, auto-scaling) typically saves 20-40% on cloud bills. Present these as ongoing savings vs. the one-time investment in the platform team.
</details>

**Q5: How should a platform team interact with stream-aligned (product) teams?**

<details>
<summary>Answer</summary>

Following Team Topologies, the primary interaction mode should be "X-as-a-Service" -- the platform team provides self-service capabilities that stream-aligned teams consume independently, without needing to interact with the platform team for routine tasks. For new capabilities or complex integrations, use "Collaboration" mode temporarily -- the platform team works alongside the product team to understand their needs and co-create solutions. "Facilitation" mode is used when helping teams adopt new platform features. The platform team should never become a dependency -- if product teams must wait for the platform team to act, the self-service model has failed. Measure this by tracking the ratio of self-service actions vs. support tickets.
</details>
