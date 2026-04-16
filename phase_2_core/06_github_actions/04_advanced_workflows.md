# Advanced GitHub Actions Workflows

## Why This Matters in DevOps

Once you have basic pipelines working, you face a new problem: duplication. Every repository needs a CI workflow. Every CI workflow has the same lint-test-build-deploy pattern. You are copy-pasting YAML across 50 repositories, and when you need to change the linting tool, you update 50 files.

Advanced workflow features — reusable workflows, composite actions, concurrency control, and manual approvals — solve the maintenance problem. They let you build a CI/CD platform that scales across your organization, not just a pipeline that works for one repository.

---

## Core Concepts

### Reusable Workflows (workflow_call)

Reusable workflows are complete workflows that other workflows can call, like a function call in programming.

**Define a reusable workflow (in a central repository):**

```yaml
# .github/workflows/python-ci.yml (in org/shared-workflows repo)
name: Reusable Python CI

on:
  workflow_call:                       # This makes it callable
    inputs:
      python-version:
        description: "Python version to use"
        type: string
        default: "3.11"
      working-directory:
        description: "Directory containing the Python code"
        type: string
        default: "."
      run-security-scan:
        description: "Whether to run security scanning"
        type: boolean
        default: true
    secrets:
      SONAR_TOKEN:
        required: false
    outputs:
      test-result:
        description: "Test result (pass/fail)"
        value: ${{ jobs.test.outputs.result }}

jobs:
  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
      - run: pip install ruff
      - run: ruff check .
      - run: ruff format --check .

  test:
    runs-on: ubuntu-latest
    outputs:
      result: ${{ steps.test.outcome }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests
        id: test
        run: pytest tests/ -v --tb=short

  security:
    if: ${{ inputs.run-security-scan }}
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pip install bandit safety
      - run: bandit -r src/ -ll
      - run: safety check -r requirements.txt
```

**Call it from any repository:**

```yaml
# .github/workflows/ci.yml (in any repo)
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  python-ci:
    uses: org/shared-workflows/.github/workflows/python-ci.yml@v1.0.0
    with:
      python-version: "3.12"
      working-directory: "backend"
      run-security-scan: true
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Composite Actions

Composite actions bundle multiple steps into a single reusable action. They are lighter than reusable workflows — think of them as reusable step groups.

```yaml
# .github/actions/setup-python-env/action.yml
name: Setup Python Environment
description: Install Python, dependencies, and dev tools

inputs:
  python-version:
    description: "Python version"
    required: false
    default: "3.11"
  install-dev-deps:
    description: "Install development dependencies"
    required: false
    default: "true"

outputs:
  python-path:
    description: "Path to the Python binary"
    value: ${{ steps.setup.outputs.python-path }}

runs:
  using: "composite"
  steps:
    - name: Set up Python
      id: setup
      uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip

    - name: Install production dependencies
      shell: bash
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install dev dependencies
      if: ${{ inputs.install-dev-deps == 'true' }}
      shell: bash
      run: pip install -r requirements-dev.txt

    - name: Show installed packages
      shell: bash
      run: pip list --format=columns | head -20
```

**Use it in a workflow:**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Use the composite action
      - name: Setup environment
        uses: ./.github/actions/setup-python-env
        with:
          python-version: "3.12"
          install-dev-deps: "true"

      - name: Run tests
        run: pytest tests/ -v
```

### Creating Custom Actions

Custom actions can be written in JavaScript or as Docker containers:

**JavaScript action (faster startup):**

```yaml
# .github/actions/notify-slack/action.yml
name: Notify Slack
description: Send a notification to Slack

inputs:
  webhook-url:
    description: "Slack webhook URL"
    required: true
  message:
    description: "Message to send"
    required: true
  status:
    description: "Build status (success/failure)"
    required: true

runs:
  using: "node20"
  main: "index.js"
```

```javascript
// .github/actions/notify-slack/index.js
const core = require('@actions/core');
const https = require('https');

async function run() {
  const webhookUrl = core.getInput('webhook-url');
  const message = core.getInput('message');
  const status = core.getInput('status');

  const emoji = status === 'success' ? ':white_check_mark:' : ':x:';
  const color = status === 'success' ? '#36a64f' : '#dc3545';

  const payload = JSON.stringify({
    attachments: [{
      color: color,
      text: `${emoji} ${message}`,
      footer: `GitHub Actions | ${new Date().toISOString()}`
    }]
  });

  // Send to Slack webhook
  const url = new URL(webhookUrl);
  const options = {
    hostname: url.hostname,
    path: url.pathname,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      core.info(`Slack notification sent: ${res.statusCode}`);
      resolve();
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

run().catch(core.setFailed);
```

### Marketplace Actions

The GitHub Actions Marketplace has thousands of pre-built actions. Use them wisely:

```yaml
steps:
  # Pin to a specific SHA (most secure)
  - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0

  # Pin to a major version tag (convenient, less secure)
  - uses: actions/checkout@v4

  # Pin to exact version tag (good balance)
  - uses: actions/checkout@v4.1.0

  # NEVER use main/master branch (unpredictable)
  # - uses: actions/checkout@main  # DO NOT DO THIS
```

### Conditional Execution

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # Run only on main branch
      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: echo "Deploying..."

      # Run only on PRs
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        run: echo "This is a PR"

      # Run only if previous step failed
      - name: Notify on failure
        if: failure()
        run: echo "Something failed!"

      # Run always (even if previous steps failed)
      - name: Cleanup
        if: always()
        run: echo "Cleaning up..."

      # Run only if a specific job succeeded
      - name: Post-deploy check
        if: needs.deploy.result == 'success'
        run: echo "Deploy succeeded"

      # Complex condition
      - name: Deploy staging
        if: |
          github.ref == 'refs/heads/main' &&
          github.event_name == 'push' &&
          !contains(github.event.head_commit.message, '[skip ci]')
        run: echo "Deploy to staging"
```

### Concurrency Control

Prevent multiple workflow runs from deploying simultaneously:

```yaml
# At the workflow level
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false           # Queue instead of cancel

# Common patterns:

# For PRs: cancel outdated runs (only latest push matters)
concurrency:
  group: ci-${{ github.event.pull_request.number || github.sha }}
  cancel-in-progress: true            # Cancel older runs for this PR

# For deployments: queue (never cancel a deploy in progress)
concurrency:
  group: deploy-production
  cancel-in-progress: false

# Per-environment concurrency
jobs:
  deploy:
    concurrency:
      group: deploy-${{ inputs.environment }}
      cancel-in-progress: false
```

### Manual Approvals with Environments

```yaml
# First, configure in GitHub:
# Repository → Settings → Environments → New environment
#   Name: production
#   Required reviewers: add team leads
#   Wait timer: 5 minutes (optional cooling-off period)
#   Deployment branches: main only

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging              # No approval required
    steps:
      - run: echo "Deployed to staging"

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production            # Requires approval!
    steps:
      - run: echo "Deployed to production"
      # This job will WAIT until a reviewer approves in the Actions tab
```

### workflow_dispatch Inputs

Manual triggers with typed inputs:

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod
      version:
        description: "Version to deploy (e.g., v1.2.3)"
        required: true
        type: string
      dry-run:
        description: "Dry run (show what would happen)"
        required: false
        type: boolean
        default: false
      log-level:
        description: "Logging level"
        required: false
        type: choice
        options:
          - info
          - debug
          - warn
        default: info

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Show inputs
        run: |
          echo "Environment: ${{ inputs.environment }}"
          echo "Version: ${{ inputs.version }}"
          echo "Dry run: ${{ inputs.dry-run }}"
          echo "Log level: ${{ inputs.log-level }}"

      - name: Deploy
        if: ${{ !inputs.dry-run }}
        run: echo "Deploying ${{ inputs.version }} to ${{ inputs.environment }}"

      - name: Dry run
        if: ${{ inputs.dry-run }}
        run: echo "Would deploy ${{ inputs.version }} to ${{ inputs.environment }}"
```

---

## Step-by-Step Practical

### Building an Organization-Wide CI/CD Platform

**Scenario**: You are the DevOps engineer for a team with 10 Python microservices. Each needs the same CI/CD pipeline.

**Step 1: Create a shared workflows repository (org/ci-platform)**

```yaml
# org/ci-platform/.github/workflows/python-service.yml
name: Python Service Pipeline

on:
  workflow_call:
    inputs:
      service-name:
        type: string
        required: true
      python-version:
        type: string
        default: "3.11"
      dockerfile-path:
        type: string
        default: "Dockerfile"
      deploy-to-staging:
        type: boolean
        default: true
    secrets:
      REGISTRY_PASSWORD:
        required: true
      SLACK_WEBHOOK:
        required: false

jobs:
  quality:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
      - run: |
          pip install ruff bandit
          ruff check .
          ruff format --check .
          bandit -r src/ -ll

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
      - run: |
          pip install -r requirements.txt -r requirements-dev.txt
          pytest tests/ -v --cov=src/ --cov-fail-under=80

  build:
    needs: [quality, test]
    runs-on: ubuntu-latest
    timeout-minutes: 15
    outputs:
      image-tag: ${{ steps.tag.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - id: tag
        run: echo "tag=${{ inputs.service-name }}:$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: .
          file: ${{ inputs.dockerfile-path }}
          push: true
          tags: registry.example.com/${{ steps.tag.outputs.tag }}

  deploy-staging:
    if: ${{ inputs.deploy-to-staging }}
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.image-tag }} to staging"
```

**Step 2: Call from each service repository**

```yaml
# org/payment-service/.github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  pipeline:
    uses: org/ci-platform/.github/workflows/python-service.yml@v2.0.0
    with:
      service-name: payment-service
      python-version: "3.12"
    secrets:
      REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
      SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

Now updating the pipeline for all 10 services means updating one file in `org/ci-platform`.

---

## Exercises

### Exercise 1: Reusable Workflow
Create a reusable workflow for linting and testing. Call it from two different repositories (or two workflows in the same repository). Verify that changes to the reusable workflow affect both callers.

### Exercise 2: Composite Action
Create a composite action that sets up a development environment (Python, Node, or Go), installs dependencies, and runs a health check. Use it in a workflow to verify it works.

### Exercise 3: Manual Deploy with Inputs
Create a workflow_dispatch workflow with inputs for environment (choice), version (string), and dry-run (boolean). Implement the deployment logic using conditional steps based on the inputs.

### Exercise 4: Concurrency Control
Create a workflow that simulates a 30-second deployment. Trigger it twice rapidly. First with `cancel-in-progress: true` (observe the first run being cancelled), then with `cancel-in-progress: false` (observe queuing).

### Exercise 5: Environment Approvals
Set up a workflow with staging and production environments. Configure production to require approval. Deploy to staging automatically and verify that production waits for manual approval in the Actions tab.

---

## Knowledge Check

### Question 1
What is the difference between a reusable workflow and a composite action?

<details>
<summary>Answer</summary>

A reusable workflow (`workflow_call`) is a complete workflow that defines its own jobs and runs on its own runners. It is called from another workflow and appears as a separate workflow in the Actions tab. A composite action is a bundle of steps that runs within an existing job on the caller's runner. Key differences: (1) reusable workflows can have multiple jobs; composite actions are steps within a single job, (2) reusable workflows run on separate runners; composite actions share the caller's runner, (3) reusable workflows have more overhead but more isolation; composite actions are lightweight, (4) reusable workflows can define their own `permissions`; composite actions inherit the caller's permissions. Use reusable workflows for complete pipelines; use composite actions for common step sequences.
</details>

### Question 2
Why should you pin action versions to SHA hashes in production workflows?

<details>
<summary>Answer</summary>

Pinning to SHA hashes (`uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608`) provides the strongest security guarantee because: (1) tags can be moved — a malicious actor who gains access to an action's repository could point the `v4` tag to compromised code; (2) SHA hashes are immutable — they always reference the exact same code; (3) it prevents supply chain attacks where an upstream action is modified to steal secrets or inject malicious code. The downside is that SHA hashes are not human-readable and do not auto-update with security patches. The compromise is to pin to SHA with a comment noting the version (`# v4.1.0`) and use tools like Dependabot or Renovate to propose updates.
</details>

### Question 3
How does concurrency control work and when should you use `cancel-in-progress: true` vs `false`?

<details>
<summary>Answer</summary>

Concurrency control groups workflow runs by a key and determines how multiple runs in the same group are handled. Use `cancel-in-progress: true` for CI on PRs — when a developer pushes a new commit, the previous run for that PR is no longer relevant, so cancelling it saves resources and gives faster feedback. Use `cancel-in-progress: false` for deployments — you never want to cancel a deployment in progress, as that could leave infrastructure in a partial state. Instead, the new run queues and waits. The concurrency group key should reflect what you are protecting: `deploy-production` for single-target deployments, `ci-${{ github.event.pull_request.number }}` for per-PR CI.
</details>

### Question 4
How do GitHub Environments enable manual approvals for production deployments?

<details>
<summary>Answer</summary>

GitHub Environments (configured in Settings → Environments) can have protection rules including required reviewers. When a job references an environment with required reviewers (`environment: production`), the job pauses and sends a notification to the reviewers. The workflow run shows a "Waiting for review" status in the Actions tab. Reviewers can approve or reject from the Actions tab or the notification. Only after approval does the job proceed. Additional protections include: wait timers (mandatory delay before deployment), deployment branch restrictions (only allow deployments from main), and environment-specific secrets (only available to jobs using that environment). This provides the manual gate needed for Continuous Delivery.
</details>

### Question 5
What is the `workflow_run` event and when would you use it?

<details>
<summary>Answer</summary>

The `workflow_run` event triggers a workflow when another workflow completes (or is requested). It is useful for: (1) triggering deployment after a build workflow completes, when you want to keep build and deploy as separate workflows for clarity, (2) running post-deployment tasks (smoke tests, notifications) after a deployment workflow completes, (3) triggering workflows in response to workflows triggered by external events (e.g., a Dependabot PR triggers CI, and `workflow_run` can trigger additional checks). The event provides the conclusion of the triggering workflow (`success`, `failure`, `cancelled`), so you can conditionally execute based on the outcome. Note that `workflow_run` always runs on the default branch, not the PR branch, which can be confusing.
</details>
