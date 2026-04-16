# Building Real CI/CD Pipelines

## Why This Matters in DevOps

A "Hello World" workflow proves GitHub Actions works. A production pipeline proves your software works. The gap between them is massive. Real pipelines have multiple jobs that depend on each other, test across multiple language versions, cache dependencies to save time, pass artifacts between jobs, and handle secrets securely.

Every minute your pipeline takes is a minute a developer waits. Every flaky test erodes trust in your pipeline. Every missing check is a bug that reaches production. Building efficient, reliable pipelines is a core DevOps competency that directly impacts your team's productivity.

---

## Core Concepts

### Multi-Job Workflows with Dependencies

By default, jobs run in parallel. Use `needs` to create dependencies:

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Linting code..."

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Running tests..."

  build:
    needs: [lint, test]               # Waits for BOTH lint and test to pass
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Building application..."

  deploy-staging:
    needs: build                       # Waits for build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to staging..."

  deploy-production:
    needs: deploy-staging              # Waits for staging
    runs-on: ubuntu-latest
    environment: production            # Requires approval
    steps:
      - run: echo "Deploying to production..."
```

Execution flow:

```
lint ──────────┐
               ├──▶ build ──▶ deploy-staging ──▶ deploy-production
test ──────────┘
(parallel)        (sequential from here)
```

### Matrix Strategy

Test across multiple versions, operating systems, or configurations simultaneously:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
        exclude:
          - os: macos-latest
            python-version: "3.10"     # Skip this combo
        include:
          - os: ubuntu-latest
            python-version: "3.12"
            experimental: true         # Add extra variable to one combo

      fail-fast: false                 # Continue running other combos if one fails
      max-parallel: 4                  # Limit concurrent jobs

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run tests
        run: |
          python -m pip install -r requirements.txt
          pytest tests/ -v
```

This creates 8 jobs (3 OS x 3 Python versions - 1 excluded):

```
test (ubuntu-latest, 3.10)   ──┐
test (ubuntu-latest, 3.11)   ──┤
test (ubuntu-latest, 3.12)   ──┤  All run in parallel
test (macos-latest, 3.11)    ──┤  (limited to 4 at a time)
test (macos-latest, 3.12)    ──┤
test (windows-latest, 3.10)  ──┤
test (windows-latest, 3.11)  ──┤
test (windows-latest, 3.12)  ──┘
```

### Caching Dependencies

Downloading dependencies on every run wastes time. Cache them:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Python pip cache (built into setup-python)
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"                 # Caches pip packages automatically

      - run: pip install -r requirements.txt
      - run: pytest tests/

  test-node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"                 # Caches node_modules automatically

      - run: npm ci
      - run: npm test

  test-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
          cache: true                  # Caches Go modules automatically

      - run: go test ./...

  # Manual cache for custom scenarios
  custom-cache:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Cache custom directory
        uses: actions/cache@v4
        with:
          path: |
            ~/.custom-cache
            /tmp/build-cache
          key: custom-${{ runner.os }}-${{ hashFiles('**/lockfile') }}
          restore-keys: |
            custom-${{ runner.os }}-

      - run: echo "Build with cached dependencies"
```

### Artifacts

Artifacts pass files between jobs or store build outputs:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build application
        run: |
          mkdir -p dist
          echo "Build output v1.2.3" > dist/app.tar.gz
          echo "Build complete" > dist/build-info.txt

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 5            # Keep for 5 days (default: 90)

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/

      - name: Deploy
        run: |
          cat dist/build-info.txt
          echo "Deploying dist/app.tar.gz..."

  test-results:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests and generate report
        run: |
          mkdir -p reports
          echo "<html><body><h1>Test Report</h1></body></html>" > reports/test-report.html

      # Upload test reports as artifacts (downloadable from Actions tab)
      - name: Upload test report
        uses: actions/upload-artifact@v4
        if: always()                   # Upload even if tests fail
        with:
          name: test-reports
          path: reports/
```

### Environment Variables and Secrets

```yaml
name: Pipeline with Secrets

env:                                   # Workflow-level env vars
  APP_NAME: my-service
  REGISTRY: ghcr.io

jobs:
  build:
    runs-on: ubuntu-latest
    env:                               # Job-level env vars
      BUILD_ENV: ci

    steps:
      - name: Use environment variables
        env:                           # Step-level env vars
          STEP_VAR: "step-value"
        run: |
          echo "App: $APP_NAME"
          echo "Registry: $REGISTRY"
          echo "Build env: $BUILD_ENV"
          echo "Step var: $STEP_VAR"

      # Access secrets (set in Settings → Secrets → Actions)
      - name: Use secrets
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        run: |
          echo "Password length: ${#DB_PASSWORD}"
          # Secrets are masked in logs — GitHub replaces the value with ***

      # NEVER do this:
      # run: echo ${{ secrets.DB_PASSWORD }}
      # This could leak if the secret contains special characters
```

**Setting secrets:**
```
Repository → Settings → Secrets and variables → Actions → New repository secret
  Name: DB_PASSWORD
  Value: your-secret-value
```

### Building Docker Images in CI

```yaml
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write                  # Required for GHCR

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Working with Different Languages

**Go:**

```yaml
  build-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - run: go build ./...
      - run: go test ./... -v -race -coverprofile=coverage.out
      - run: go vet ./...
```

**Node.js:**

```yaml
  build-node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

**Python:**

```yaml
  build-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest tests/ -v --cov
```

---

## Step-by-Step Practical

### Complete Multi-Language Pipeline

```yaml
# .github/workflows/pipeline.yml
name: Complete Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Stage 1: Quality checks (parallel)
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install ruff
      - run: ruff check src/ tests/
      - run: ruff format --check src/ tests/

  # Stage 1: Tests across Python versions (parallel with lint)
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest tests/ -v --tb=short --junitxml=test-results.xml

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: test-results.xml

  # Stage 2: Build Docker image (after lint and all tests pass)
  build:
    name: Build Docker Image
    needs: [lint, test]
    runs-on: ubuntu-latest
    timeout-minutes: 15
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Stage 3: Deploy to staging (only on main branch)
  deploy-staging:
    name: Deploy to Staging
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
          echo "Image: ${{ needs.build.outputs.image-tag }}"

  # Stage 4: Deploy to production (manual approval via environment)
  deploy-production:
    name: Deploy to Production
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production            # Has required reviewers configured

    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
```

---

## Exercises

### Exercise 1: Matrix Testing
Create a workflow that tests a Python application across Python 3.10, 3.11, and 3.12 on both Ubuntu and macOS. Exclude Python 3.10 on macOS. Set `fail-fast: false` and observe how failures in one combination do not cancel others.

### Exercise 2: Artifact Passing
Create a two-job workflow where Job 1 generates a build report (a text file with the date, commit SHA, and a random build number) and Job 2 downloads and displays that report. Verify data passes correctly between the jobs.

### Exercise 3: Dependency Caching
Create a Python project with 10+ dependencies. Run the workflow twice — once without caching, once with pip caching enabled. Compare the installation times in the workflow logs.

### Exercise 4: Docker Build Pipeline
Create a simple Dockerfile for any application and a GitHub Actions workflow that builds the image, tags it with the Git SHA, and pushes it to GitHub Container Registry (ghcr.io). Verify the image appears in your repository's Packages tab.

### Exercise 5: Secret Management
Create a workflow that uses a repository secret to configure a (simulated) database connection. Verify that the secret value is masked in logs by printing the length of the secret, then trying to echo the secret itself (observe the masking).

---

## Knowledge Check

### Question 1
How does the `needs` keyword affect job execution order?

<details>
<summary>Answer</summary>

The `needs` keyword creates explicit dependencies between jobs. Without `needs`, all jobs run in parallel. With `needs: [jobA, jobB]`, the job waits until both jobA and jobB complete successfully before starting. If any dependency fails, the dependent job is skipped. This creates a directed acyclic graph (DAG) of job execution. You can create sequential pipelines (lint → build → deploy) or diamond patterns (lint and test run in parallel, then build waits for both). Jobs connected by `needs` can also pass data using job outputs.
</details>

### Question 2
What is the purpose of the `fail-fast` option in matrix strategies?

<details>
<summary>Answer</summary>

`fail-fast` controls whether GitHub Actions cancels remaining matrix jobs when one fails. With `fail-fast: true` (the default), if Python 3.10 tests fail, the 3.11 and 3.12 test jobs are immediately cancelled. This saves CI minutes but means you only see one failure at a time. With `fail-fast: false`, all matrix combinations run to completion regardless of individual failures. This is useful when you want to see the full picture — which versions pass and which fail — especially during migration or debugging. For PR workflows, `fail-fast: false` is often preferred; for deployment gates, `fail-fast: true` saves time.
</details>

### Question 3
Why should you use `actions/cache` or built-in caching, and what are the limitations?

<details>
<summary>Answer</summary>

Caching avoids re-downloading dependencies on every workflow run. Without caching, `pip install` or `npm ci` downloads packages from the internet every time, adding minutes to every run. With caching, dependencies are stored in GitHub's cache storage and restored in seconds. Limitations: (1) cache size is limited to 10 GB per repository, (2) caches not accessed in 7 days are evicted, (3) caches are scoped to branches (a PR can read the base branch's cache but not other PRs'), (4) cache keys must be designed carefully — using `hashFiles('**/lockfile')` ensures the cache is invalidated when dependencies change, (5) caching is not useful for the first run or after lockfile changes.
</details>

### Question 4
How do artifacts differ from caches in GitHub Actions?

<details>
<summary>Answer</summary>

Artifacts and caches serve different purposes. Artifacts are for sharing files between jobs in a workflow or persisting build outputs for human download. They are uploaded explicitly with `upload-artifact` and downloaded with `download-artifact`. They persist after the workflow completes (default 90 days). Caches are for speeding up repeated operations by storing dependencies between workflow runs. They are transparent (the cached content is restored to the same path) and are automatically invalidated by cache key changes. Key differences: artifacts work between jobs in the same run; caches work between runs. Artifacts are for outputs (test reports, binaries); caches are for inputs (dependencies, build tools).
</details>

### Question 5
What is the security risk of using `${{ secrets.VALUE }}` directly in a `run` command?

<details>
<summary>Answer</summary>

Using `${{ secrets.VALUE }}` directly in a `run` command is risky because the expression is evaluated before the shell processes it, which can lead to script injection. If a secret contains special characters (backticks, dollar signs, quotes, semicolons), they could be interpreted as shell commands. For example, a secret containing `; rm -rf /` would execute that command. The safe pattern is to pass secrets as environment variables: `env: MY_SECRET: ${{ secrets.VALUE }}` and then reference `$MY_SECRET` in the run command. Environment variables are passed safely to the shell process without interpretation. GitHub will mask the secret value in logs regardless of how it is passed.
</details>
