# Lesson 01: GitOps Philosophy

## Why This Matters in DevOps

Every operations team has experienced the dreaded "but it worked in staging" moment.
Configuration drift, undocumented manual changes, and opaque deployment pipelines
erode trust and slow delivery. GitOps emerged as an answer to a fundamental question:
*What if the entire desired state of your infrastructure lived in Git, and the system
continuously reconciled itself to match?*

Coined by Alexis Richardson of Weaveworks in August 2017, GitOps took the DevOps
principle of "Infrastructure as Code" and elevated it into a full operational model.
Instead of treating Git as merely a place to store scripts, GitOps makes Git the
single source of truth for *what your system should look like right now*. The cluster
watches Git and fixes itself — not the other way around.

Understanding GitOps philosophy is essential because it fundamentally changes how
teams think about deployments, incident response, and compliance. It is not just
another tool; it is an operational framework.

---

## Core Concepts

### The Birth of GitOps

In 2017 Weaveworks published a blog post describing how they managed Kubernetes
clusters at scale. Their approach boiled down to:

1. Store everything declaratively in Git.
2. Let an agent running inside the cluster pull changes and apply them.
3. If someone manually changes the cluster, the agent reverts the change.

This was not entirely new — configuration management tools like Puppet had "desired
state" models for years — but GitOps married that idea with Kubernetes-native
controllers, Git-based workflows, and the cultural norms of pull requests and code
review.

### The Four Principles of GitOps

The OpenGitOps project (a CNCF Sandbox project) codified four principles:

#### Principle 1: Declarative

The entire system must be described declaratively. In Kubernetes this means YAML or
Helm charts or Kustomize overlays — never a sequence of imperative `kubectl` commands.

```yaml
# Declarative: "I want 3 replicas of nginx 1.25"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
```

#### Principle 2: Versioned and Immutable

The desired state is stored in a way that enforces immutability and versioning.
Git provides both naturally: every commit is a SHA-addressed, immutable snapshot,
and the full history is preserved.

```bash
# Every change is a commit — fully auditable
git log --oneline
# a3f9c21 Bump nginx to 1.25
# 8b2d4e7 Add resource limits to web-frontend
# 1c0a9f3 Initial deployment manifest
```

#### Principle 3: Pulled Automatically

Approved changes are automatically applied to the system. A software agent inside
the cluster pulls the desired state from Git, compares it to the actual state, and
applies any differences. No human runs `kubectl apply`.

#### Principle 4: Continuously Reconciled

Software agents continuously observe the actual system state and attempt to apply
the desired state. If someone manually scales a deployment from 3 to 5 replicas,
the agent detects the drift and scales it back to 3.

### Push vs Pull Deployment Models

```
PUSH MODEL (Traditional CI/CD)
================================
Developer -> Git -> CI Pipeline -> kubectl apply -> Cluster
                                   ^^^^^^^^^^^^
                                   CI has cluster credentials

PULL MODEL (GitOps)
================================
Developer -> Git <- Agent (in cluster) -> applies changes
                   ^^^^^^^^^^^^^^^^^^^^
                   Agent pulls from Git; CI never touches the cluster
```

| Aspect              | Push Model               | Pull Model (GitOps)         |
|----------------------|-------------------------|-----------------------------|
| Who applies changes? | CI server               | In-cluster agent            |
| Cluster credentials  | Stored in CI            | Stay inside the cluster     |
| Drift detection      | None (fire-and-forget)  | Continuous reconciliation   |
| Security surface     | Larger (CI has access)  | Smaller (agent has access)  |
| Rollback             | Re-run old pipeline     | `git revert` + auto-sync   |

### Why GitOps Matters

**Audit Trail**: Every change is a Git commit with an author, timestamp, and
description. Compliance teams can answer "who changed what, when, and why?" by
reading `git log`.

**Rollback**: Rolling back is `git revert <sha>`. The agent detects the new HEAD
and reconciles. No need to figure out which Helm values were used three weeks ago.

**Consistency**: The cluster always converges to Git. Manual `kubectl edit` changes
are overwritten, eliminating snowflake configurations.

**Developer Experience**: Developers use the same Git workflow (branches, PRs,
reviews) for infrastructure changes that they use for application code.

**Disaster Recovery**: If a cluster is destroyed, you stand up a new one, point the
agent at your Git repo, and the entire state is recreated.

### GitOps vs Traditional CI/CD

Traditional CI/CD pipelines are imperative: "run these steps in order." GitOps is
declarative: "here is what I want; make it so."

```
Traditional CI/CD Pipeline:
  1. Build image
  2. Push to registry
  3. Run helm upgrade --install ...
  4. Run smoke tests
  5. If fail, run helm rollback

GitOps Pipeline:
  1. Build image, push to registry         (CI responsibility)
  2. Update image tag in Git config repo   (CI responsibility)
  3. Agent detects change, syncs cluster   (GitOps responsibility)
  4. Health checks via agent               (GitOps responsibility)
```

The key shift: CI builds and tests. GitOps deploys and reconciles. They are
complementary, not competing.

### When GitOps Is NOT Appropriate

GitOps is not a silver bullet. It may be the wrong choice when:

- **Stateful operations require imperative steps**: Database migrations, data
  backups, and one-time scripts do not map cleanly to declarative state.
- **Rapid prototyping**: If you are experimenting on a throwaway cluster, the
  overhead of committing every change to Git slows you down.
- **Non-Kubernetes workloads**: GitOps tooling is heavily Kubernetes-oriented.
  Managing VMs, DNS records, or SaaS configurations via GitOps requires glue.
- **Teams without Git literacy**: If operators are not comfortable with Git
  workflows, forcing GitOps adds friction without the cultural benefits.
- **Secrets management**: Storing secrets in Git (even encrypted) adds complexity.
  GitOps requires companion tools like Sealed Secrets or External Secrets Operator.
- **Extremely high-frequency deployments**: If you deploy hundreds of times per
  hour (e.g., feature flags), a Git commit per change may become a bottleneck.

---

## Step-by-Step Practical

### Scenario: Understanding the GitOps Feedback Loop

We will walk through a mental model of how GitOps works end-to-end, using a
concrete example.

**Step 1: Developer creates a change**

```bash
# Clone the config repo (not the app repo)
git clone git@github.com:acme/platform-config.git
cd platform-config

# Create a feature branch
git checkout -b bump-api-to-v2.3.1
```

**Step 2: Modify the desired state**

```yaml
# apps/api-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: production
spec:
  replicas: 5
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
        - name: api
          image: acme/api-service:v2.3.1    # Changed from v2.3.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
```

**Step 3: Commit and open a pull request**

```bash
git add apps/api-service/deployment.yaml
git commit -m "Bump api-service to v2.3.1 (fixes CVE-2024-1234)"
git push origin bump-api-to-v2.3.1

# Open PR for review
gh pr create --title "Bump api-service to v2.3.1" \
  --body "Patches CVE-2024-1234. Changelog: https://..."
```

**Step 4: Review and merge**

A teammate reviews the YAML diff, approves, and merges to `main`.

**Step 5: GitOps agent detects the change**

The agent (ArgoCD, Flux, etc.) polls the repo every 3 minutes (or receives a
webhook) and detects that `main` has a new commit.

**Step 6: Agent reconciles**

```
INFO  Comparing desired state (Git SHA a3f9c21) with live state
INFO  Detected diff: api-service image changed from v2.3.0 to v2.3.1
INFO  Applying: kubectl apply -f apps/api-service/deployment.yaml
INFO  Waiting for rollout: deployment/api-service
INFO  Rollout complete: 5/5 replicas updated
INFO  Health status: Healthy
INFO  Sync status: Synced
```

**Step 7: Drift detection (continuous)**

If someone runs `kubectl scale deployment api-service --replicas=10`, the agent
detects the drift and scales back to 5.

```
WARN  Drift detected: api-service replicas changed from 5 to 10
INFO  Self-healing: reverting to desired state (5 replicas)
INFO  Applied: api-service replicas set to 5
```

---

## Exercises

### Exercise 1: Map Your Current Workflow
Document your team's current deployment process. Identify each step and classify
it as "would stay in CI" or "would move to GitOps." Write down which steps are
imperative and which could be made declarative.

### Exercise 2: Design a Rollback Scenario
Imagine a deployment introduced a bug. Write the exact Git commands you would use
to roll back using GitOps (hint: `git revert`). Compare this with your current
rollback process.

### Exercise 3: Evaluate GitOps Fit
Pick three applications or services your team runs. For each one, evaluate whether
GitOps is appropriate. Consider: Is the deployment declarative? Are there imperative
steps (migrations, seed data)? How would secrets be handled?

### Exercise 4: Push vs Pull Security Analysis
Draw a diagram showing where credentials live in your current push-based deployment.
Then draw the equivalent GitOps pull-based diagram. Identify which attack surfaces
are eliminated and which new ones are introduced.

### Exercise 5: Write a GitOps Proposal
Draft a one-page proposal for adopting GitOps in your organization. Include: the
problem statement (what pain points exist today), the proposed solution, expected
benefits, risks, and the first three steps to get started.

---

## Knowledge Check

### Question 1
What are the four principles of GitOps as defined by the OpenGitOps project?

<details>
<summary>Answer</summary>

1. **Declarative** — The entire system is described declaratively.
2. **Versioned and Immutable** — The desired state is stored in a versioned,
   immutable store (Git).
3. **Pulled Automatically** — Approved changes are automatically pulled and applied.
4. **Continuously Reconciled** — Agents continuously compare desired vs actual state
   and correct drift.

</details>

### Question 2
What is the key security advantage of the pull model over the push model?

<details>
<summary>Answer</summary>

In the pull model, cluster credentials never leave the cluster. The GitOps agent
runs inside the cluster and pulls configuration from Git. In the push model, the CI
server must hold cluster credentials (kubeconfig), creating a larger attack surface
— if the CI server is compromised, the attacker has direct cluster access.

</details>

### Question 3
Name three scenarios where GitOps may NOT be the right approach.

<details>
<summary>Answer</summary>

1. **Stateful imperative operations** like database migrations that require ordered
   steps and cannot be expressed declaratively.
2. **Rapid prototyping** where the overhead of committing every change to Git slows
   experimentation.
3. **Non-Kubernetes workloads** where GitOps tooling has limited support (e.g., VM
   management, SaaS configuration).

Other valid answers include: teams without Git literacy, extremely high-frequency
deployments, or environments where secrets management adds unacceptable complexity.

</details>

### Question 4
How does GitOps handle rollbacks differently from traditional CI/CD?

<details>
<summary>Answer</summary>

In GitOps, a rollback is a `git revert` of the offending commit. The agent detects
the new HEAD, compares it to the cluster state, and reconciles — effectively
re-deploying the previous version. In traditional CI/CD, rollback typically means
re-running an older pipeline or executing `helm rollback`, which may not restore the
exact previous state if other changes were made in between.

</details>

### Question 5
Who coined the term "GitOps" and when?

<details>
<summary>Answer</summary>

Alexis Richardson, CEO of Weaveworks, coined the term "GitOps" in a blog post
published in August 2017. He described how Weaveworks managed their Kubernetes
clusters using Git as the single source of truth.

</details>
