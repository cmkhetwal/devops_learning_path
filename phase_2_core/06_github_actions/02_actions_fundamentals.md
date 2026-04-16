# GitHub Actions Fundamentals

## Why This Matters in DevOps

GitHub Actions is where most of the industry has converged for CI/CD. If your code is on GitHub — and for most teams it is — GitHub Actions eliminates the need to set up and maintain a separate CI/CD system. No Jenkins server to patch, no CircleCI integration to configure. Your pipeline lives in the same repository as your code, reviewed in the same pull requests, versioned in the same Git history.

As a DevOps engineer, you will write, debug, and optimize GitHub Actions workflows constantly. Every new service needs a pipeline. Every pipeline needs updates when build requirements change. Understanding the architecture — workflows, jobs, steps, runners — lets you build pipelines that are fast, reliable, and maintainable.

---

## Core Concepts

### GitHub Actions Architecture

```
Workflow (YAML file in .github/workflows/)
  │
  ├── Event (what triggers the workflow)
  │     push, pull_request, schedule, manual, etc.
  │
  └── Jobs (units of work, run on separate runners)
        │
        ├── Job 1: "build" (runs on ubuntu-latest)
        │     ├── Step 1: Checkout code
        │     ├── Step 2: Install dependencies
        │     └── Step 3: Run tests
        │
        └── Job 2: "deploy" (depends on Job 1)
              ├── Step 1: Checkout code
              ├── Step 2: Build Docker image
              └── Step 3: Push to registry
```

**Key concepts:**

- **Workflow**: A configurable automated process defined in YAML. A repository can have multiple workflows.
- **Event**: Something that triggers a workflow (push, PR, schedule, manual).
- **Job**: A set of steps that execute on the same runner. Jobs run in parallel by default.
- **Step**: An individual task within a job. Steps run sequentially.
- **Runner**: A server that executes the job. GitHub provides hosted runners, or you can use your own.
- **Action**: A reusable unit of code that performs a specific task (checkout code, set up Node, deploy to AWS).

### YAML Workflow Syntax

Workflows are defined in `.github/workflows/*.yml`:

```yaml
# .github/workflows/ci.yml
name: CI Pipeline                        # Display name in the Actions tab

on:                                       # Event triggers
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

permissions:                              # Limit permissions (security)
  contents: read

env:                                      # Workflow-level environment variables
  APP_NAME: my-service
  PYTHON_VERSION: "3.11"

jobs:                                     # Define jobs
  test:                                   # Job ID
    name: Run Tests                       # Display name
    runs-on: ubuntu-latest               # Runner type
    timeout-minutes: 15                   # Prevent hung jobs

    steps:                                # Sequential steps
      - name: Checkout code
        uses: actions/checkout@v4        # Use an action

      - name: Set up Python
        uses: actions/setup-python@v5
        with:                             # Action inputs
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |                            # Run shell commands
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ -v --tb=short
```

### Triggering Events

```yaml
on:
  # Push to specific branches
  push:
    branches: [main, develop]
    paths:                                # Only trigger if these files change
      - 'src/**'
      - 'tests/**'
      - 'requirements.txt'
    paths-ignore:                         # Do NOT trigger for these
      - '**.md'
      - 'docs/**'

  # Pull request events
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

  # Scheduled (cron syntax)
  schedule:
    - cron: '0 6 * * 1'                  # Every Monday at 6 AM UTC

  # Manual trigger (button in Actions tab)
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [dev, staging, prod]
      debug:
        description: 'Enable debug logging'
        type: boolean
        default: false

  # When a release is published
  release:
    types: [published]

  # When another workflow completes
  workflow_run:
    workflows: ["Build"]
    types: [completed]
```

### Your First Workflow: Hello World

Create this file in your repository:

```yaml
# .github/workflows/hello.yml
name: Hello World

on:
  push:
    branches: [main]
  workflow_dispatch:    # Allows manual trigger

jobs:
  greet:
    runs-on: ubuntu-latest

    steps:
      - name: Say hello
        run: echo "Hello from GitHub Actions!"

      - name: Show environment info
        run: |
          echo "Runner OS: $RUNNER_OS"
          echo "Runner Arch: $RUNNER_ARCH"
          echo "Repository: $GITHUB_REPOSITORY"
          echo "Branch: $GITHUB_REF_NAME"
          echo "Commit SHA: $GITHUB_SHA"
          echo "Workflow: $GITHUB_WORKFLOW"
          echo "Run ID: $GITHUB_RUN_ID"

      - name: Show date and runner info
        run: |
          date
          uname -a
          python3 --version
          node --version
          docker --version
```

### Understanding the Actions Tab

After pushing a workflow, navigate to your repository's "Actions" tab:

```
Repository → Actions tab

You will see:
┌─────────────────────────────────────────────┐
│ All workflows                                │
│                                              │
│ ● Hello World                                │
│   ✓ Run #1 · main · abc1234 · 30s ago       │
│   ✓ Run #2 · main · def5678 · 2m ago        │
│   ✗ Run #3 · main · ghi9012 · 5m ago (fail) │
│                                              │
│ ● CI Pipeline                                │
│   ✓ Run #1 · PR #42 · 10m ago               │
└─────────────────────────────────────────────┘

Click a run to see:
  - Summary (jobs and their status)
  - Click a job to see step-by-step logs
  - Each step expands to show its output
  - Failed steps show error messages
```

### Workflow Logs

Logs are your primary debugging tool. Each step produces timestamped output:

```
▶ Run tests
  2024-01-15T14:30:01Z pytest tests/ -v --tb=short
  2024-01-15T14:30:02Z ====== test session starts ======
  2024-01-15T14:30:02Z collected 42 items
  2024-01-15T14:30:02Z tests/test_api.py::test_health_check PASSED
  2024-01-15T14:30:02Z tests/test_api.py::test_login PASSED
  2024-01-15T14:30:03Z tests/test_api.py::test_create_user FAILED
  ...
  2024-01-15T14:30:05Z ====== FAILED ======
  2024-01-15T14:30:05Z Error: Process completed with exit code 1
```

**Debug logging:**

```yaml
steps:
  - name: Enable debug logging
    run: echo "ACTIONS_STEP_DEBUG=true" >> $GITHUB_ENV

  # Or set the secret ACTIONS_STEP_DEBUG=true in repository settings
  # This shows internal action debug output
```

### GitHub-Hosted vs Self-Hosted Runners

**GitHub-hosted runners** (the default):

```yaml
runs-on: ubuntu-latest     # Ubuntu 22.04, fresh every run
runs-on: ubuntu-24.04      # Specific Ubuntu version
runs-on: macos-latest      # macOS
runs-on: windows-latest    # Windows
```

Characteristics:
- Fresh virtual machine for every job
- Pre-installed tools (Docker, Python, Node, Go, etc.)
- 7 GB RAM, 14 GB SSD (Linux)
- Included in GitHub plan (free tier: 2000 minutes/month)
- No maintenance required
- Cannot access private networks directly

**Self-hosted runners** (you manage the server):

```yaml
runs-on: self-hosted                           # Any self-hosted runner
runs-on: [self-hosted, linux, x64]            # With labels
runs-on: [self-hosted, gpu]                    # Custom label
```

When to use self-hosted:
- Need to access private networks (databases, internal services)
- Need specific hardware (GPU, ARM, high memory)
- Cost optimization at scale (thousands of minutes/month)
- Compliance requirements (data must stay on-premises)
- Need persistent caches between runs

```bash
# Setting up a self-hosted runner (on a Linux server):
# 1. Go to Repository → Settings → Actions → Runners → New self-hosted runner
# 2. Follow the download and configure instructions:

mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN
./run.sh  # Or install as a service with: sudo ./svc.sh install && sudo ./svc.sh start
```

---

## Step-by-Step Practical

### Building a Complete CI Workflow for a Python Project

**Project structure:**

```
my-python-app/
  src/
    app.py
    utils.py
  tests/
    test_app.py
    test_utils.py
  requirements.txt
  requirements-dev.txt
  .github/
    workflows/
      ci.yml
```

**Step 1: Create the workflow file**

```yaml
# .github/workflows/ci.yml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install linting tools
        run: pip install ruff mypy

      - name: Run ruff (linting)
        run: ruff check src/ tests/

      - name: Run ruff (formatting)
        run: ruff format --check src/ tests/

      - name: Run mypy (type checking)
        run: mypy src/ --ignore-missing-imports

  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests with coverage
        run: |
          pytest tests/ -v --tb=short --cov=src/ --cov-report=term-missing

      - name: Check coverage threshold
        run: |
          coverage_pct=$(pytest tests/ --cov=src/ --cov-report=term | grep TOTAL | awk '{print $NF}' | tr -d '%')
          echo "Coverage: ${coverage_pct}%"
          if [ "${coverage_pct}" -lt 80 ]; then
            echo "Coverage is below 80%!"
            exit 1
          fi

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install security tools
        run: pip install bandit safety

      - name: Run bandit (code security)
        run: bandit -r src/ -f json -o bandit-report.json || true

      - name: Run safety (dependency vulnerabilities)
        run: safety check -r requirements.txt
```

**Step 2: Push and observe**

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow"
git push

# Go to repository → Actions tab
# You should see the workflow running with 3 parallel jobs
```

**Step 3: Understand the execution flow**

```
Push event triggers workflow
  │
  ├── lint job (starts immediately)
  │     ├── Checkout → Setup Python → Install tools → Ruff → Mypy
  │     └── Takes ~1-2 minutes
  │
  ├── test job (starts immediately, parallel with lint)
  │     ├── Checkout → Setup Python → Install deps → Pytest
  │     └── Takes ~3-5 minutes
  │
  └── security job (starts immediately, parallel with others)
        ├── Checkout → Setup Python → Install tools → Bandit → Safety
        └── Takes ~1-2 minutes

Total time: ~3-5 minutes (parallel, not sequential!)
```

### Understanding GitHub Actions Contexts

```yaml
steps:
  - name: Show available contexts
    run: |
      echo "Event name: ${{ github.event_name }}"
      echo "Repository: ${{ github.repository }}"
      echo "Branch: ${{ github.ref_name }}"
      echo "Actor: ${{ github.actor }}"
      echo "SHA: ${{ github.sha }}"
      echo "Run number: ${{ github.run_number }}"
      echo "Run ID: ${{ github.run_id }}"
      echo "Runner OS: ${{ runner.os }}"
      echo "Runner arch: ${{ runner.arch }}"
      echo "Is PR: ${{ github.event_name == 'pull_request' }}"
```

### Working with Step Outputs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Set output
        id: build_step
        run: |
          echo "version=1.2.3" >> $GITHUB_OUTPUT
          echo "sha_short=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

      - name: Use output
        run: |
          echo "Version: ${{ steps.build_step.outputs.version }}"
          echo "Short SHA: ${{ steps.build_step.outputs.sha_short }}"
```

---

## Exercises

### Exercise 1: Hello World Workflow
Create a GitHub repository and add a "Hello World" workflow that triggers on push and manual dispatch. The workflow should print environment information, the current date, and available tools (Python, Node, Docker versions). Push it and verify it runs in the Actions tab.

### Exercise 2: Multi-Step Build
Create a workflow with 5 steps: checkout code, create a file with content, display the file, modify the file, display the modified version. This teaches you that steps share a filesystem within a job.

### Exercise 3: Trigger Types
Create three separate workflows: one triggered on push, one triggered on pull_request, and one triggered on schedule (every hour). Add a workflow_dispatch trigger to each. Observe when each runs.

### Exercise 4: Parallel Jobs
Create a workflow with 4 independent jobs (simulating lint, unit-test, integration-test, security-scan). Use `sleep` commands to simulate different runtimes (5s, 10s, 15s, 5s). Observe that they run in parallel and the total runtime is ~15 seconds, not 35.

### Exercise 5: Environment Variables
Create a workflow that uses environment variables at three levels: workflow-level, job-level, and step-level. Demonstrate how step-level variables override job-level, which override workflow-level.

---

## Knowledge Check

### Question 1
What is the relationship between workflows, jobs, and steps in GitHub Actions?

<details>
<summary>Answer</summary>

A workflow is the top-level automation defined in a YAML file in `.github/workflows/`. Each workflow contains one or more jobs. Jobs are independent units of work that run on separate runners (virtual machines) — by default they run in parallel, but can be made sequential using `needs`. Each job contains one or more steps, which are individual tasks that execute sequentially on the same runner. Steps share a filesystem within their job (so one step can create a file and the next step can read it), but jobs do NOT share a filesystem (use artifacts to share data between jobs). A workflow is triggered by an event (push, PR, schedule, etc.).
</details>

### Question 2
What is the difference between GitHub-hosted and self-hosted runners?

<details>
<summary>Answer</summary>

GitHub-hosted runners are virtual machines managed by GitHub. They provide a fresh environment for every job, come with pre-installed tools, require no maintenance, and are included in your GitHub plan. Self-hosted runners are machines you manage yourself. They are useful when you need: access to private networks, specific hardware (GPU, ARM), persistent caches between runs, compliance with data residency requirements, or cost optimization at high volumes. The tradeoff is that self-hosted runners require maintenance (updates, security patches, monitoring) and must be secured carefully since they execute code from your repository.
</details>

### Question 3
How do you pass data between steps within the same job?

<details>
<summary>Answer</summary>

Within the same job, steps share a filesystem, so the simplest way is to write to and read from files. For structured data passing, use step outputs: in the producing step, write `echo "key=value" >> $GITHUB_OUTPUT` (with an `id` on the step), then in the consuming step, reference it with `${{ steps.step_id.outputs.key }}`. For environment variables that persist across steps, use `echo "VAR=value" >> $GITHUB_ENV`, which makes `$VAR` available in all subsequent steps. For sharing data between jobs (which run on different runners), you must use artifacts (`actions/upload-artifact` and `actions/download-artifact`).
</details>

### Question 4
Why should you set `timeout-minutes` on your jobs?

<details>
<summary>Answer</summary>

Setting `timeout-minutes` prevents jobs from running indefinitely due to hangs, infinite loops, or waiting for resources that never become available. Without a timeout, a hung job consumes runner minutes until GitHub's default 6-hour timeout. This wastes money (GitHub-hosted runners bill by the minute), blocks self-hosted runners from running other jobs, and delays feedback to developers who may not notice the job is stuck. A reasonable timeout is 2-3x the expected job duration — enough headroom for slow runs but short enough to fail fast if something is wrong.
</details>

### Question 5
What does `paths` filtering do in workflow triggers and why is it important?

<details>
<summary>Answer</summary>

`paths` filtering restricts when a workflow runs based on which files were changed. For example, `paths: ['src/**', 'tests/**']` means the workflow only triggers when files in `src/` or `tests/` change. Changes to documentation, README, or unrelated files do not trigger the workflow. This is important because: (1) it saves CI minutes by not running unnecessary builds, (2) it speeds up feedback by reducing queue times, (3) it is essential in monorepos where different services have different pipelines, and (4) it reduces noise — developers do not see irrelevant workflow runs. Use `paths-ignore` for the inverse (run for everything EXCEPT these paths).
</details>
