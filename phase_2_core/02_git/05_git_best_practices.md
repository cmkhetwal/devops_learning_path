# Git Best Practices

## Why This Matters in DevOps

Git best practices are not style preferences -- they are operational necessities. A clean commit history is a debugging tool. Atomic commits make rollbacks safe. Signed commits prove who deployed what. Branch protection rules prevent accidental production outages. When an incident occurs at 2 AM and you need to figure out what changed, the difference between a well-maintained Git history and a messy one is the difference between a 10-minute fix and a multi-hour investigation.

In DevOps, Git is not just for developers. Infrastructure engineers, SREs, and platform engineers all use Git daily. The practices outlined here apply to Terraform modules, Ansible playbooks, Kubernetes manifests, and CI/CD pipeline definitions as much as they apply to application code. GitOps, the practice of using Git as the single source of truth for infrastructure, makes these best practices even more critical because every Git commit can potentially trigger a production change.

---

## Core Concepts

### Commit Message Conventions

A good commit message answers three questions: **What** changed, **why** it changed, and **what effect** it has. The widely adopted format is:

```
<type>(<scope>): <subject>     (50 chars or less)
                                (blank line)
<body>                          (wrap at 72 chars)
                                (blank line)
<footer>                        (references, breaking changes)
```

**Rules for the subject line:**
- Use imperative mood: "Add feature" not "Added feature" or "Adds feature"
- Do not end with a period
- Keep under 50 characters
- Capitalize the first word

**Good commit messages:**

```
feat(monitoring): add Prometheus alerting rules

Add alerting rules for high CPU (>80%), memory (>90%), and disk
usage (>85%). Rules notify the on-call channel via PagerDuty
integration.

Relates-to: OPS-1234
```

```
fix(pipeline): correct Docker image tag in staging deploy

The staging pipeline was using 'latest' instead of the Git SHA,
causing non-deterministic deployments. Changed to use the commit
SHA for reproducible builds.

Fixes: OPS-5678
```

**Bad commit messages:**

```
fixed stuff
update
WIP
asdfasdf
changes
```

### Atomic Commits

An atomic commit contains exactly one logical change. It should be small enough to understand at a glance and large enough to be meaningful. If a commit message requires the word "and," the commit should probably be split.

**Why atomic commits matter for DevOps:**

1. **Rollbacks are safe:** Reverting one atomic commit undoes exactly one change without side effects.
2. **Bisect works better:** Each commit is a testable unit, making `git bisect` more precise.
3. **Code review is effective:** Reviewers can understand each commit independently.
4. **Cherry-pick is reliable:** You can apply individual fixes to release branches without dragging unrelated changes.

**Atomic:**

```
Commit 1: "feat(auth): add JWT token validation middleware"
Commit 2: "feat(auth): add user role-based access control"
Commit 3: "test(auth): add integration tests for auth middleware"
```

**Not atomic:**

```
Commit 1: "Add auth, fix logging, update deps, refactor database"
```

### Monorepo vs Polyrepo

**Monorepo:** All services, libraries, and infrastructure code live in a single repository.

| Pros | Cons |
|------|------|
| Atomic cross-service changes | Large repo size |
| Shared tooling and CI | Complex permissions |
| Easy code reuse | Long CI times without optimization |
| Single source of truth | Requires specialized tooling (Bazel, Nx) |

**Polyrepo:** Each service or component has its own repository.

| Pros | Cons |
|------|------|
| Clear ownership boundaries | Cross-repo changes require coordination |
| Independent CI/CD pipelines | Dependency version drift |
| Simpler permissions | Harder to share code |
| Faster CI per repo | More repos to manage |

**DevOps consideration:** Monorepos work well for organizations with strong platform teams and shared CI infrastructure. Polyrepos work better for teams with autonomous microservice ownership. Many organizations use a hybrid: a monorepo for infrastructure code and polyrepos for application services.

### Branch Protection Rules

Branch protection is your last line of defense against accidental or unauthorized changes to production-affecting branches.

**Essential protections for `main`:**

| Rule | Why |
|------|-----|
| Require pull request | No direct pushes; all changes are reviewed |
| Require N approvals | At least one (ideally two) people review |
| Require status checks | CI must pass before merge |
| Require branch to be up-to-date | Prevents merging stale code |
| Require signed commits | Verify author identity |
| Block force pushes | Prevent history rewriting |
| Restrict deletions | Prevent accidental branch deletion |
| Include administrators | Rules apply to everyone |

### Signed Commits

GPG-signed commits prove that the commit was made by who it claims to be. In regulated environments (finance, healthcare, government), this is often a compliance requirement. In DevOps, signed commits prevent supply chain attacks where an attacker impersonates a trusted contributor.

### Git Blame for Debugging

`git blame` shows who last modified each line of a file and when. Despite its name, it is not about assigning blame -- it is about understanding context. When you find a problematic line of configuration, `git blame` tells you who wrote it, which commit introduced it, and (if the commit message is good) why it was written that way.

### Clean History

A clean history means every commit is meaningful, well-described, and logically organized. Strategies for clean history:

1. **Squash WIP commits** before merging (interactive rebase)
2. **Rebase feature branches** onto main before merging
3. **Use `--no-ff` merges** to clearly delineate feature integrations
4. **Never commit broken code** to shared branches
5. **Separate refactoring from feature work** into distinct commits

### GitOps: Git as the Source of Truth for Infrastructure

GitOps is the practice of using Git repositories as the single source of truth for declarative infrastructure and applications. Changes to infrastructure are made through pull requests, and automated systems (like ArgoCD or Flux) ensure the actual state matches the desired state in Git.

**Core principles:**
1. All infrastructure is declared in Git
2. Changes happen through pull requests
3. Approved changes are automatically applied
4. The system continuously reconciles actual state with desired state

---

## Step-by-Step Practical

### Writing Good Commit Messages

```bash
# Use -m for short messages
git commit -m "fix(api): handle null response from payment gateway"

# For longer messages, let Git open your editor
git commit
# This opens your $EDITOR where you can write a multi-line message

# Configure your preferred editor
git config --global core.editor "vim"
```

### Atomic Commits in Practice

```bash
# Scenario: you modified three files for two different purposes
git status
```

Expected output:

```
Changes not staged for commit:
  modified:   src/auth.py          # Part of auth feature
  modified:   src/middleware.py     # Part of auth feature
  modified:   src/config.py        # Unrelated config fix
```

```bash
# Commit 1: the auth feature (two related files)
git add src/auth.py src/middleware.py
git commit -m "feat(auth): add token refresh mechanism"

# Commit 2: the config fix (separate concern)
git add src/config.py
git commit -m "fix(config): correct database connection timeout value"
```

### Setting Up Signed Commits

```bash
# Generate a GPG key
gpg --full-generate-key
# Select RSA and RSA, 4096 bits, no expiration (or set one)

# List your keys
gpg --list-secret-keys --keyid-format=long
```

Expected output:

```
sec   rsa4096/ABC1234567890DEF 2026-04-16 [SC]
      1234567890ABCDEF1234567890ABC1234567890DEF
uid                 [ultimate] Your Name <you@example.com>
```

```bash
# Configure Git to use your key
git config --global user.signingkey ABC1234567890DEF
git config --global commit.gpgsign true

# Make a signed commit
git commit -S -m "feat(security): add input validation"

# Verify signatures in the log
git log --show-signature -1
```

Expected output:

```
commit a1b2c3d...
gpg: Signature made Thu Apr 16 15:00:00 2026
gpg: Good signature from "Your Name <you@example.com>"
Author: Your Name <you@example.com>
Date:   Thu Apr 16 15:00:00 2026 +0000

    feat(security): add input validation
```

### Using Git Blame Effectively

```bash
# Who last modified each line of a file?
git blame src/database.py
```

Expected output:

```
a1b2c3d4 (Alice   2026-03-01 10:00:00 +0000  1) import psycopg2
a1b2c3d4 (Alice   2026-03-01 10:00:00 +0000  2)
e4f5g6h7 (Bob     2026-03-15 14:30:00 +0000  3) POOL_SIZE = 20
a1b2c3d4 (Alice   2026-03-01 10:00:00 +0000  4) TIMEOUT = 30
i7j8k9l0 (Charlie 2026-04-10 09:15:00 +0000  5) MAX_RETRIES = 3
```

```bash
# Blame a specific line range
git blame -L 10,20 src/database.py

# Show the commit that last changed line 5
git log -1 i7j8k9l0

# Ignore whitespace-only changes (useful after formatting)
git blame -w src/database.py

# Detect moved or copied lines from other files
git blame -C src/database.py
```

### Branch Protection with GitHub CLI

```bash
# View current branch protection rules
gh api repos/{owner}/{repo}/branches/main/protection

# Set up branch protection (requires admin access)
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci/tests","ci/lint","ci/security"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":2}' \
  --field restrictions=null
```

### Maintaining Clean History

```bash
# Before merging a feature branch, clean up the history
git checkout feature/add-dashboard

# Squash the last 4 commits into meaningful ones
git rebase -i HEAD~4

# After cleaning up, merge with --no-ff for a clear merge commit
git checkout main
git merge --no-ff feature/add-dashboard -m "Merge feature/add-dashboard: monitoring dashboard"
```

### GitOps Repository Structure

```bash
# Example GitOps repository structure
mkdir -p {apps,infrastructure,clusters}/{dev,staging,prod}

# Application manifests
cat > apps/prod/api-deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api:v1.2.0
          resources:
            limits:
              memory: "256Mi"
              cpu: "500m"
EOF

git add .
git commit -m "deploy(prod): update API to v1.2.0

Deploying version 1.2.0 which includes:
- Health check endpoints
- Prometheus metrics
- Rate limiting

Approved-by: platform-team
Change-request: CR-2026-0416"
```

### Useful Git Aliases

```bash
# Set up productivity aliases
git config --global alias.st "status"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.lg "log --graph --oneline --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.unstage "reset HEAD --"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.contributors "shortlog --summary --numbered"

# Usage
git lg
```

Expected output:

```
* a1b2c3d (HEAD -> main) deploy(prod): update API to v1.2.0
* e4f5g6h feat(monitoring): add Prometheus alerting rules
* i7j8k9l fix(pipeline): correct Docker image tag
| * m0n1o2p (feature/new-api) WIP: new API endpoints
|/
* q3r4s5t Initial project structure
```

---

## Exercises

### Exercise 1: Commit Message Audit

Review the last 20 commits in a repository you work with (or a popular open-source project). Evaluate each commit message against the conventional commit format. Identify which messages are helpful during debugging and which are not. Rewrite three bad commit messages.

### Exercise 2: Practice Atomic Commits

Take a task that involves modifying five files across two logical concerns (e.g., adding a feature and fixing a bug). Practice staging files selectively to create two atomic commits instead of one large commit. Use `git diff --staged` to verify each commit contains only related changes.

### Exercise 3: Set Up Branch Protection

On a test repository, configure branch protection for `main` that requires: at least one approval, passing CI status checks, up-to-date branches, and no force pushes. Try to push directly to `main` and verify the push is rejected. Then create a pull request and go through the proper workflow.

### Exercise 4: Git Blame Investigation

Pick a configuration file in a production project. Use `git blame` to understand the history of each section. For the three most recent changes, use `git log` to read the full commit messages and understand why the changes were made. Document your findings.

### Exercise 5: Design a GitOps Repository

Create a repository structure for a GitOps workflow that manages three environments (dev, staging, prod) with two applications (frontend, backend). Include Kubernetes manifests, a CODEOWNERS file, and branch protection documentation. Make commits that simulate promoting a release from dev through staging to prod.

---

## Knowledge Check

**Q1: Why are atomic commits important for incident response?**

<details>
<summary>Answer</summary>

Atomic commits matter for incident response because: (1) when a deployment causes an issue, reverting a single atomic commit undoes exactly one logical change without side effects, (2) `git bisect` works more precisely when each commit is a single testable unit, (3) `git blame` points to a specific, understandable change rather than a large dump of unrelated modifications, and (4) the commit message of an atomic commit explains the intent of the change, which helps diagnose whether it could be related to the incident. A commit message like "fix auth, update logging, refactor database" is useless during an incident.

</details>

**Q2: What is the difference between monorepo and polyrepo, and how does the choice affect CI/CD pipelines?**

<details>
<summary>Answer</summary>

A monorepo stores all services and infrastructure in one repository; a polyrepo uses separate repositories for each component. The CI/CD impact is significant:

**Monorepo CI/CD:** Requires path-based triggers (only build services whose files changed), shared CI infrastructure, and tooling like Bazel or Nx for efficient builds. Cross-service changes are atomic. Pipeline complexity is higher but coordination is simpler.

**Polyrepo CI/CD:** Each repo has independent, simpler pipelines. Cross-service changes require coordinated releases across multiple repos. Dependency management becomes a challenge (which version of service A works with service B?). Each pipeline is faster but cross-cutting changes are harder.

</details>

**Q3: Why should branch protection rules apply to administrators as well?**

<details>
<summary>Answer</summary>

If administrators are exempt from branch protection, then: (1) any admin can bypass code review and push directly to main, which defeats the purpose of quality gates, (2) during incidents, the pressure to "just push the fix" can lead to deploying untested changes, (3) it creates a two-class system where some changes are reviewed and others are not, and (4) audit trails become incomplete because some changes skip the pull request process. The principle is: if a change affects production, it should be reviewed, regardless of who makes it.

</details>

**Q4: What is GitOps, and why is Git particularly suited to be the source of truth for infrastructure?**

<details>
<summary>Answer</summary>

GitOps uses Git as the single source of truth for declarative infrastructure. Git is suited for this because: (1) it provides a complete audit trail of every change with who, what, when, and why, (2) pull requests enable peer review of infrastructure changes before they are applied, (3) rollback is as simple as reverting a commit, (4) branching enables testing infrastructure changes in isolation, (5) Git's immutable history prevents tampering with the change record, and (6) Git's distributed nature provides redundancy. Tools like ArgoCD and Flux continuously reconcile the actual infrastructure state with the desired state defined in Git.

</details>

**Q5: How do signed commits protect the software supply chain?**

<details>
<summary>Answer</summary>

Signed commits use GPG (or SSH) keys to cryptographically prove that a commit was made by the person it claims to be from. This protects against: (1) impersonation attacks where someone configures `user.name` and `user.email` to match a trusted contributor, (2) supply chain attacks where malicious commits are injected into a repository, and (3) compliance violations in regulated industries that require non-repudiation (proof that a specific person authorized a change). In a GitOps workflow where commits trigger deployments, verifying signatures ensures only authorized personnel can trigger production changes.

</details>
