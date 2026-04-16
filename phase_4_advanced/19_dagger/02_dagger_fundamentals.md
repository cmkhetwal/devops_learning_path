# Dagger Fundamentals

## Why This Matters in DevOps

Writing your first Dagger pipeline shifts your mental model from "CI/CD configuration" to "CI/CD programming." Instead of memorizing GitHub Actions YAML syntax or GitLab CI keywords, you use Python functions, type hints, and standard programming patterns. Once you write a Dagger function, you can run it locally in seconds, share it as a module, and call it from any CI system. This lesson gets you from zero to a working pipeline that builds and tests a real application.

---

## Core Concepts

### Installing Dagger

```bash
# macOS
brew install dagger/tap/dagger

# Linux
curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
sudo mv ./bin/dagger /usr/local/bin/

# Verify
dagger version
# dagger v0.13.0
```

### Dagger CLI

```bash
# Initialize a Dagger module in your project
dagger init --sdk=python --name=ci

# Call a function
dagger call <function-name> [arguments]

# List available functions
dagger functions

# Interactive terminal into a container
dagger call build --source=. terminal

# View logs
dagger call test --source=. --debug
```

### Dagger Functions

Everything in Dagger is a function. Functions take typed inputs and return typed outputs. They are composable -- one function's output can be another's input.

```python
# Key types:
# dagger.Directory  → a directory (your source code)
# dagger.File       → a single file
# dagger.Container  → a container (with filesystem, env, etc.)
# dagger.Secret     → a secret value (never logged)
# dagger.Service    → a running service (database, Redis)
# str               → plain string output
```

### Container Operations

```python
# Building a container step by step
container = (
    dag.container()                              # Start empty
    .from_("python:3.12-slim")                   # Base image
    .with_directory("/app", source)              # Add source code
    .with_workdir("/app")                        # Set working directory
    .with_exec(["pip", "install", "-r", "requirements.txt"])  # Run command
    .with_env_variable("ENVIRONMENT", "test")    # Set env var
    .with_exposed_port(8080)                     # Expose port
    .with_exec(["python", "app.py"])             # Run app
)

# Get output
stdout = await container.stdout()               # Capture stdout
stderr = await container.stderr()               # Capture stderr
exit_code = await container.exit_code()         # Check exit code

# Export as image
await container.publish("ghcr.io/mycompany/app:v1")  # Push to registry
await container.export("./image.tar")                  # Save as tarball
```

### File/Directory Operations

```python
# Read files
content = await dag.directory().file("config.yaml").contents()

# Filter directories
source = dag.host().directory(".", exclude=[".git", "node_modules", "__pycache__"])

# Create files in containers
container = (
    dag.container()
    .from_("alpine")
    .with_new_file("/app/config.json", contents='{"key": "value"}')
)
```

---

## Step-by-Step Practical

### Building and Testing a Python App with Dagger

**Step 1: Create a Sample Python Project**

```
myapp/
├── src/
│   ├── __init__.py
│   └── calculator.py
├── tests/
│   └── test_calculator.py
├── requirements.txt
├── Dockerfile
└── ci/
    ├── __init__.py
    └── main.py          ← Dagger module
```

```python
# src/calculator.py
def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

```python
# tests/test_calculator.py
from src.calculator import add, multiply, divide
import pytest

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(4, 5) == 20

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)
```

```
# requirements.txt
pytest==8.3.0
pytest-cov==5.0.0
ruff==0.6.0
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "src"]
```

**Step 2: Initialize Dagger Module**

```bash
cd myapp
dagger init --sdk=python --name=ci --source=./ci
```

**Step 3: Write the Pipeline**

```python
# ci/main.py
"""CI/CD pipeline for the Python application."""

import dagger
from dagger import dag, function, object_type


@object_type
class Ci:
    """CI/CD pipeline functions."""

    @function
    def base_container(self, source: dagger.Directory) -> dagger.Container:
        """Create a base container with dependencies installed."""
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/app", source, exclude=[".git", "__pycache__", ".venv", "ci/"])
            .with_workdir("/app")
            .with_exec(["pip", "install", "--no-cache-dir", "-r", "requirements.txt"])
        )

    @function
    async def lint(self, source: dagger.Directory) -> str:
        """Run ruff linter on the source code."""
        return await (
            self.base_container(source)
            .with_exec(["ruff", "check", "src/", "--output-format=text"])
            .stdout()
        )

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Run pytest with coverage."""
        return await (
            self.base_container(source)
            .with_exec([
                "pytest", "tests/",
                "--cov=src",
                "--cov-report=term-missing",
                "-v",
            ])
            .stdout()
        )

    @function
    def build(self, source: dagger.Directory) -> dagger.Container:
        """Build the Docker image using the Dockerfile."""
        return dag.container().build(source)

    @function
    async def publish(
        self,
        source: dagger.Directory,
        image_ref: str,
        registry_username: str | None = None,
        registry_password: dagger.Secret | None = None,
    ) -> str:
        """Build and publish the Docker image to a registry."""
        container = self.build(source)

        if registry_username and registry_password:
            registry = image_ref.split("/")[0]
            container = container.with_registry_auth(
                registry, registry_username, registry_password
            )

        addr = await container.publish(image_ref)
        return addr

    @function
    async def ci(self, source: dagger.Directory) -> str:
        """Run the full CI pipeline: lint, test, build."""
        # Lint
        print("Running lint...")
        lint_output = await self.lint(source)
        print(f"Lint passed:\n{lint_output}")

        # Test
        print("Running tests...")
        test_output = await self.test(source)
        print(f"Tests passed:\n{test_output}")

        # Build
        print("Building image...")
        container = self.build(source)
        # Verify the build works by running a health check
        health = await (
            container
            .with_exec(["python", "-c", "from src.calculator import add; print(add(1,2))"])
            .stdout()
        )
        print(f"Build verification: {health.strip()}")

        return "CI pipeline completed successfully"
```

**Step 4: Run Locally**

```bash
# Run individual functions
dagger call lint --source=.
dagger call test --source=.
dagger call build --source=.

# Run the full pipeline
dagger call ci --source=.
```

Expected output:
```
Running lint...
Lint passed:
All checks passed!

Running tests...
Tests passed:
tests/test_calculator.py::test_add PASSED
tests/test_calculator.py::test_multiply PASSED
tests/test_calculator.py::test_divide PASSED
tests/test_calculator.py::test_divide_by_zero PASSED

---------- coverage: 100% ----------
Name                   Stmts   Miss  Cover
------------------------------------------
src/__init__.py            0      0   100%
src/calculator.py          8      0   100%
------------------------------------------
TOTAL                      8      0   100%

Build verification: 3

CI pipeline completed successfully
```

**Step 5: Connect to GitHub Actions**

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint
        uses: dagger/dagger-for-github@v6
        with:
          verb: call
          args: lint --source=.

      - name: Test
        uses: dagger/dagger-for-github@v6
        with:
          verb: call
          args: test --source=.

      - name: Build & Publish
        if: github.ref == 'refs/heads/main'
        uses: dagger/dagger-for-github@v6
        with:
          verb: call
          args: >
            publish
            --source=.
            --image-ref=ghcr.io/${{ github.repository }}:${{ github.sha }}
            --registry-username=${{ github.actor }}
            --registry-password=env:GITHUB_TOKEN
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Step 6: Connect to GitLab CI (same Dagger code)**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build

lint:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - apk add --no-cache curl
    - curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
  script:
    - dagger call lint --source=.

test:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - apk add --no-cache curl
    - curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
  script:
    - dagger call test --source=.

publish:
  stage: build
  only:
    - main
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - apk add --no-cache curl
    - curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
  script:
    - dagger call publish --source=. --image-ref=registry.gitlab.com/$CI_PROJECT_PATH:$CI_COMMIT_SHA
```

---

## Exercises

1. **First Pipeline**: Install Dagger and create a module that lints, tests, and builds a Python application. Run it locally and verify all steps pass.

2. **Container Debugging**: Write a Dagger function that builds a container and use `dagger call build --source=. terminal` to get an interactive shell inside the built container. Explore the filesystem.

3. **Multi-Language**: Create a Dagger pipeline for a Node.js application (npm install, npm test, npm build). Compare the experience with the Python pipeline.

4. **CI Integration**: Take your Dagger pipeline and create wrapper configurations for both GitHub Actions and GitLab CI. Verify the same Dagger code runs on both.

5. **Parameterized Pipeline**: Create a Dagger function that accepts parameters: Python version (3.11, 3.12), test coverage threshold, and whether to publish. Use Python logic to handle all cases.

---

## Knowledge Check

**Q1: What is the Dagger Engine and how does it relate to BuildKit?**

<details>
<summary>Answer</summary>

The Dagger Engine is a runtime that executes pipeline operations inside containers. It uses BuildKit (the same build engine Docker uses for `docker build`) for container operations, filesystem management, and caching. When you call a Dagger function, the SDK sends instructions to the engine via a GraphQL API. The engine translates these into BuildKit operations, executing each step in an isolated container. BuildKit provides content-addressed caching, meaning if a step's inputs have not changed, the cached result is reused. The engine runs as a Docker container itself, so it works anywhere Docker runs.
</details>

**Q2: How do Dagger secrets differ from environment variables?**

<details>
<summary>Answer</summary>

Dagger secrets (`dagger.Secret` type) are specially handled to prevent accidental exposure. Unlike regular environment variables: (1) secrets are never included in logs or stdout output, (2) they are not visible in the container's build cache, (3) they are passed through a secure channel between the SDK and the engine, (4) they are explicitly typed in function signatures, making it clear which values are sensitive. You provide secrets via `--secret=env:VAR_NAME` (reads from local environment) or `--secret=file:/path/to/file`. In contrast, `with_env_variable()` values are visible in logs and cached.
</details>

**Q3: What does `dag.container().from_("python:3.12-slim")` return?**

<details>
<summary>Answer</summary>

It returns a `dagger.Container` object representing a container based on the `python:3.12-slim` image. The container is not running yet -- it is a lazy description of a container. Operations are chained declaratively (`.with_directory()`, `.with_exec()`, etc.) and only executed when a terminal operation is called (`.stdout()`, `.publish()`, `.exit_code()`). This lazy evaluation enables the engine to optimize execution, skip unnecessary steps via caching, and parallelize independent operations.
</details>

**Q4: How does Dagger caching work?**

<details>
<summary>Answer</summary>

Dagger uses BuildKit's content-addressed caching. Each operation (`.from_()`, `.with_exec()`, etc.) creates a cache layer. If the inputs to an operation have not changed since the last run, the cached result is reused. For example, if your requirements.txt has not changed, `pip install -r requirements.txt` is cached and skipped. Caching is automatic and granular -- only changed steps are re-executed. You can also use explicit cache volumes with `.with_mounted_cache()` for package manager caches (pip, npm, go modules). Cache persists between runs on the same machine because the Dagger Engine maintains its BuildKit cache in a Docker volume.
</details>
