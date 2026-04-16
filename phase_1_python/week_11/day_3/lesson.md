# Week 11, Day 3: GitHub Actions with Python

## What You'll Learn

- GitHub Actions workflow file structure (YAML)
- How to run Python scripts in CI/CD pipelines
- Using environment variables and artifacts
- Generating workflow YAML files programmatically

## Why This Matters for DevOps

GitHub Actions is a popular CI/CD platform built into GitHub. Understanding
how to create, modify, and generate workflow files programmatically lets you
standardize CI/CD across many repositories, enforce best practices, and
automate pipeline creation.

---

## 1. GitHub Actions Basics

Workflows live in `.github/workflows/` as YAML files:

```yaml
name: CI Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
```

## 2. Key Concepts

| Concept | Description |
|---------|-------------|
| `on` | Trigger events (push, pull_request, schedule, workflow_dispatch) |
| `jobs` | Groups of steps that run on a runner |
| `runs-on` | The runner environment (ubuntu-latest, windows-latest, etc.) |
| `steps` | Individual tasks within a job |
| `uses` | Reference a reusable action |
| `run` | Execute a shell command |
| `env` | Environment variables |
| `with` | Input parameters for an action |

## 3. Environment Variables

```yaml
env:
  APP_ENV: production
  AWS_REGION: us-east-1

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      DEPLOY_TARGET: staging
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          echo "Deploying to $DEPLOY_TARGET"
          python deploy.py --env $APP_ENV
```

## 4. Matrix Strategy

Run the same job with different configurations:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

## 5. Artifacts

Upload and download build artifacts:

```yaml
steps:
  - name: Run tests with coverage
    run: pytest --cov=app --cov-report=html

  - name: Upload coverage report
    uses: actions/upload-artifact@v4
    with:
      name: coverage-report
      path: htmlcov/
      retention-days: 30
```

## 6. Job Dependencies

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building..."

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing..."

  deploy:
    needs: [build, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: echo "Deploying..."
```

## 7. Generating YAML with Python

```python
import yaml

workflow = {
    "name": "CI Pipeline",
    "on": {
        "push": {"branches": ["main"]},
        "pull_request": {"branches": ["main"]},
    },
    "jobs": {
        "test": {
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v5",
                    "with": {"python-version": "3.11"},
                },
                {
                    "name": "Install deps",
                    "run": "pip install -r requirements.txt",
                },
                {"name": "Test", "run": "pytest"},
            ],
        }
    },
}

# Write to file
with open(".github/workflows/ci.yml", "w") as f:
    yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
```

## 8. Cron Schedules

```yaml
on:
  schedule:
    # Every day at midnight UTC
    - cron: "0 0 * * *"
    # Every Monday at 9 AM UTC
    - cron: "0 9 * * 1"
```

## DevOps Connection

Programmatic workflow generation is used for:
- **Template standardization**: Ensure all repos follow the same CI/CD pattern
- **Monorepo management**: Generate per-service workflows dynamically
- **Compliance**: Auto-inject security scanning steps into all pipelines
- **Migration tooling**: Convert Jenkinsfiles or CircleCI configs to GitHub Actions

---

## Key Takeaways

| Feature | Purpose |
|---------|---------|
| `on.push` | Trigger on code push |
| `on.pull_request` | Trigger on PR |
| `strategy.matrix` | Test multiple configs |
| `needs` | Job dependencies |
| `secrets.*` | Access encrypted secrets |
| `artifacts` | Save build outputs |
| `yaml.dump()` | Generate YAML from Python dicts |
