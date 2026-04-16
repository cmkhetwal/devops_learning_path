# Collaboration Workflows

## Why This Matters in DevOps

DevOps is fundamentally about breaking down silos between teams. Git collaboration workflows are the mechanism through which developers, operations engineers, security teams, and platform engineers all contribute to the same codebase. A well-designed collaboration workflow ensures that changes are reviewed before deployment, knowledge is shared across the team, and the main branch remains stable at all times.

In modern DevOps organizations, the pull request is not just a code review tool -- it is a quality gate. Automated pipelines run tests, security scans, and linting on every pull request. Manual reviewers verify logic and architecture. The pull request becomes the point where "shift left" actually happens: catching bugs, security vulnerabilities, and misconfigurations before they reach production.

Understanding remote repositories, fetch vs pull, forking workflows, and branch protection is essential for anyone who will configure CI/CD pipelines, manage repository permissions, or participate in on-call rotations where understanding who changed what and when is critical.

---

## Core Concepts

### Remote Repositories

A remote is a version of your repository hosted on a server (GitHub, GitLab, Bitbucket). Remotes enable collaboration by providing a central point for sharing changes.

- **origin:** The default name for the remote you cloned from. This is your primary remote.
- **upstream:** A conventional name for the original repository when you are working on a fork.

```
Your Fork (origin)          Original Repo (upstream)
github.com/you/project      github.com/org/project
        |                           |
        +---- your local clone -----+
```

### Push, Pull, and Fetch

These three commands manage the flow of changes between your local repository and remotes.

- **`git fetch`** downloads new commits from the remote but does NOT modify your working files. It updates your remote-tracking branches (`origin/main`). This is always safe.
- **`git pull`** is `git fetch` + `git merge`. It downloads new commits AND integrates them into your current branch.
- **`git push`** uploads your local commits to the remote.

The safest workflow is: fetch first, review what changed, then merge or rebase manually. Using `git pull --rebase` avoids unnecessary merge commits when pulling updates.

### Pull Requests / Merge Requests

A pull request (GitHub/Bitbucket term) or merge request (GitLab term) is a formal proposal to merge changes from one branch into another. It provides:

1. **A diff view** showing exactly what changed
2. **A discussion thread** for code review comments
3. **Automated checks** from CI/CD pipelines
4. **An approval workflow** requiring one or more reviewers
5. **A permanent record** of why changes were made

In DevOps, pull requests are where infrastructure changes, application code, and pipeline configurations are reviewed before they affect production.

### Forking Workflow

Forking creates a personal copy of a repository under your own account. This is the standard workflow for open-source contributions and for organizations that want to restrict who can push to the main repository.

```
1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a feature branch
4. Push to your fork
5. Open a pull request to the original repository
```

### CODEOWNERS

The `CODEOWNERS` file defines who is responsible for reviewing changes to specific parts of the codebase. When a pull request modifies files matching a pattern in CODEOWNERS, the specified owners are automatically requested as reviewers.

```
# .github/CODEOWNERS
*.tf          @platform-team
Dockerfile    @platform-team @security-team
*.py          @backend-team
/docs/        @docs-team
.github/      @devops-team
```

### Conventional Commits

Conventional commits are a standardized format for commit messages that enables automated tooling (changelogs, version bumping, release notes).

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Common types:

| Type | Purpose |
|------|---------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `chore` | Maintenance (deps, configs) |
| `ci` | CI/CD pipeline changes |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `perf` | Performance improvement |

Examples:

```
feat(auth): add OAuth2 login support
fix(api): handle null response from payment service
ci(pipeline): add security scanning stage
chore(deps): update terraform provider to v4.0
```

### Protecting the Main Branch

Branch protection rules ensure that the main branch stays stable. Common protections include:

- **Require pull request reviews:** No direct pushes to main
- **Require status checks:** CI must pass before merging
- **Require up-to-date branches:** Branch must be current with main
- **Require signed commits:** Verify author identity
- **Restrict who can push:** Only specific teams or automation
- **Require linear history:** No merge commits (rebase only)

---

## Step-by-Step Practical

### Working with Remotes

```bash
# View configured remotes
git remote -v
```

Expected output:

```
origin  https://github.com/youruser/project.git (fetch)
origin  https://github.com/youruser/project.git (push)
```

```bash
# Add an upstream remote (for forked repos)
git remote add upstream https://github.com/original-org/project.git

# Verify
git remote -v
```

Expected output:

```
origin    https://github.com/youruser/project.git (fetch)
origin    https://github.com/youruser/project.git (push)
upstream  https://github.com/original-org/project.git (fetch)
upstream  https://github.com/original-org/project.git (push)
```

### Fetching and Pulling

```bash
# Fetch updates from origin (safe -- does not change your files)
git fetch origin

# See what changed on the remote
git log HEAD..origin/main --oneline
```

Expected output:

```
f8a9b2c Update deployment configuration
d3e4f5a Fix health check endpoint
```

```bash
# Merge remote changes into your branch
git merge origin/main

# Or pull (fetch + merge) in one step
git pull origin main

# Pull with rebase to avoid merge commits
git pull --rebase origin main
```

### Pushing Changes

```bash
# Push current branch to origin
git push origin main

# Push a new branch and set up tracking
git push -u origin feature/add-metrics
```

Expected output:

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 312 bytes | 312.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0)
remote: Resolving deltas: 100% (1/1), done.
To https://github.com/youruser/project.git
   a1b2c3d..e4f5g6h  main -> main
```

### The Complete Pull Request Workflow

```bash
# 1. Start from an up-to-date main
git checkout main
git pull origin main

# 2. Create a feature branch
git checkout -b feature/add-health-check

# 3. Make your changes
cat > healthcheck.py <<'EOF'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "version": "1.2.0"})

@app.route('/ready')
def ready():
    # Check database connectivity, cache, etc.
    return jsonify({"status": "ready"})
EOF

# 4. Commit with conventional commit format
git add healthcheck.py
git commit -m "feat(api): add health and readiness endpoints

These endpoints enable Kubernetes liveness and readiness probes
to monitor application health during rolling deployments."

# 5. Push to your remote
git push -u origin feature/add-health-check
```

Expected output:

```
Total 3 (delta 1), reused 0 (delta 0)
remote:
remote: Create a pull request for 'feature/add-health-check' on GitHub by visiting:
remote:   https://github.com/youruser/project/pull/new/feature/add-health-check
remote:
To https://github.com/youruser/project.git
 * [new branch]      feature/add-health-check -> feature/add-health-check
Branch 'feature/add-health-check' set up to track 'origin/feature/add-health-check'.
```

```bash
# 6. Create pull request using GitHub CLI
gh pr create \
  --title "feat(api): add health and readiness endpoints" \
  --body "## Summary
- Add /health endpoint for liveness probes
- Add /ready endpoint for readiness probes
- Enables Kubernetes health monitoring

## Testing
- Tested locally with curl
- Unit tests added in test_healthcheck.py"
```

### Setting Up CODEOWNERS

```bash
# Create CODEOWNERS file
mkdir -p .github
cat > .github/CODEOWNERS <<'EOF'
# Default owners for everything
*               @devops-team

# Infrastructure code
*.tf            @platform-team
*.tfvars        @platform-team

# Docker and container configs
Dockerfile*     @platform-team @security-team
docker-compose* @platform-team

# Application code
/src/           @backend-team
/frontend/      @frontend-team

# CI/CD pipelines
.github/workflows/  @devops-team
.gitlab-ci.yml      @devops-team
Jenkinsfile         @devops-team

# Security-sensitive files
/security/      @security-team
*.pem           @security-team
EOF

git add .github/CODEOWNERS
git commit -m "chore: add CODEOWNERS for automated review assignment"
```

### Syncing a Fork with Upstream

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream main into your local main
git checkout main
git merge upstream/main

# Push updated main to your fork
git push origin main
```

---

## Exercises

### Exercise 1: Fork and Contribute

Find a public repository on GitHub (or use a team member's repo). Fork it, clone your fork, create a branch, make a small change, push to your fork, and open a pull request. Experience the full contribution workflow.

### Exercise 2: Set Up CODEOWNERS

Create a CODEOWNERS file for a hypothetical project with this structure: Terraform files owned by the platform team, Python files owned by the backend team, Dockerfiles owned by both platform and security teams, and CI pipeline files owned by the DevOps team.

### Exercise 3: Conventional Commits Practice

Write conventional commit messages for the following scenarios:
- Adding a new user registration feature
- Fixing a database connection timeout
- Updating the CI pipeline to include security scanning
- Removing deprecated API endpoints
- Improving the response time of the search endpoint

### Exercise 4: Sync a Fork

Simulate the fork sync workflow: create two local repositories (one acting as "upstream" and one as "origin"). Make changes in "upstream," then practice fetching and merging those changes into your "origin" repository.

### Exercise 5: Branch Protection Rules

Using GitHub's web interface or the `gh` CLI, configure branch protection rules on a test repository: require pull request reviews, require status checks, and prevent force pushes. Document each rule and explain why it matters for production stability.

---

## Knowledge Check

**Q1: What is the difference between `git fetch` and `git pull`? Why might you prefer `git fetch` in a DevOps workflow?**

<details>
<summary>Answer</summary>

`git fetch` downloads commits from the remote but does not modify your working directory or current branch. `git pull` does `git fetch` followed by `git merge` (or `git rebase` with `--rebase`).

You might prefer `git fetch` because: (1) it is always safe and never causes conflicts, (2) you can review remote changes before integrating them (`git log HEAD..origin/main`), and (3) in CI/CD pipelines, you often want to fetch specific branches without merging. Using `git fetch` gives you more control over when and how integration happens.

</details>

**Q2: Why are pull requests considered a quality gate in DevOps, not just a code review tool?**

<details>
<summary>Answer</summary>

Pull requests serve as a quality gate because they are the integration point for multiple automated checks: CI pipelines run tests, linters verify code style, security scanners detect vulnerabilities, and infrastructure validators check configurations. Combined with mandatory human review from CODEOWNERS, branch protection rules that require passing status checks, and the requirement for up-to-date branches, the pull request becomes the point where all quality criteria must be satisfied before changes reach the main branch. This is "shift left" in practice.

</details>

**Q3: What is the purpose of the CODEOWNERS file, and how does it improve DevOps collaboration?**

<details>
<summary>Answer</summary>

CODEOWNERS automatically assigns reviewers based on which files are changed in a pull request. It ensures that: (1) the right experts review changes to their domain (security team reviews Dockerfiles, platform team reviews Terraform), (2) no changes slip through without appropriate review, (3) review responsibility is distributed and codified rather than ad hoc, and (4) new team members can see who owns what. It bridges the DevOps silo problem by ensuring cross-team visibility.

</details>

**Q4: Why do conventional commits matter for CI/CD automation?**

<details>
<summary>Answer</summary>

Conventional commits follow a machine-readable format (`type(scope): description`) that enables: (1) automated semantic version bumping (`feat` = minor, `fix` = patch, `BREAKING CHANGE` = major), (2) automated changelog generation, (3) automated release notes, (4) filtering commits by type in CI pipelines (e.g., skip deployment for `docs` or `chore` commits), and (5) consistent, searchable commit history. Tools like `semantic-release` and `standard-version` rely on this format.

</details>

**Q5: Describe the forking workflow and explain when it is preferred over direct branch-based collaboration.**

<details>
<summary>Answer</summary>

In the forking workflow: (1) you create a personal copy (fork) of the repository, (2) clone your fork locally, (3) create feature branches on your fork, (4) push to your fork, and (5) open a pull request from your fork to the original repository.

It is preferred when: (1) you are contributing to open-source projects where you do not have write access, (2) the organization wants to restrict who can push to the main repository, (3) external contractors or partners need to contribute without direct repository access, or (4) you want an extra layer of isolation to prevent accidental pushes to the main repository.

</details>
