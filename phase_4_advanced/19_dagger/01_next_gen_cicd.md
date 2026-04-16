# Next-Generation CI/CD

## Why This Matters in DevOps

Every DevOps engineer has felt the pain of YAML-based CI/CD: copying pipeline configurations between repositories, debugging failures that only happen in CI (not locally), and rewriting pipelines when switching from GitHub Actions to GitLab CI. Dagger solves these problems by letting you write CI/CD pipelines in real programming languages (Python, TypeScript, Go) that run identically on your laptop and in any CI system. Created by the founders of Docker, Dagger represents the next evolution in CI/CD -- from declarative YAML to programmable, containerized pipelines.

---

## Core Concepts

### Problems with YAML-Based CI/CD

```
Pain Point 1: Vendor Lock-In
─────────────────────────────
GitHub Actions syntax ≠ GitLab CI syntax ≠ Jenkins syntax
Moving between CI providers requires rewriting everything.

Pain Point 2: No Local Testing
──────────────────────────────
"It works on my machine" becomes "It works in CI"
You push, wait 5 minutes, see it fail, fix, push again.
The feedback loop is painful.

Pain Point 3: Copy-Paste Engineering
────────────────────────────────────
200 repositories × same pipeline = 200 copies
Update once? Update 200 times. Or don't, and they drift.

Pain Point 4: Limited Logic
───────────────────────────
YAML was designed for configuration, not logic.
Conditionals, loops, error handling = awkward workarounds.

Pain Point 5: Hidden Dependencies
─────────────────────────────────
Pipeline runs in a black-box environment.
Which tools are pre-installed? What versions?
"ubuntu-latest" changed and broke my pipeline.
```

### Dagger Philosophy

Dagger flips the CI/CD model: instead of writing YAML that describes steps for a specific CI vendor, you write code that defines containerized operations. The same code runs on your laptop (via Docker) and in any CI system.

```
Traditional CI/CD:              Dagger:
─────────────────               ──────

GitHub Actions YAML             Python/TypeScript/Go code
    │                               │
    ▼                               ▼
GitHub's runners               Any container runtime
(vendor-specific)              (Docker, Podman)
    │                               │
    ▼                               ▼
Works in GitHub only            Works EVERYWHERE
                                ├── Locally (laptop)
                                ├── GitHub Actions
                                ├── GitLab CI
                                ├── Jenkins
                                ├── CircleCI
                                └── Any CI with Docker
```

### Who Created Dagger?

Dagger was created by Solomon Hykes (co-founder of Docker) and the team behind Docker's early success. The insight: Docker containerized applications; Dagger containerizes CI/CD pipelines. Just as Docker made "works on my machine" a guarantee for applications, Dagger makes "works on my laptop" a guarantee for pipelines.

### Dagger vs Traditional CI

```
Feature              GitHub Actions    GitLab CI       Dagger
──────────────────────────────────────────────────────────────
Language             YAML              YAML            Python/TS/Go
Local testing        No (act limited)  No              Yes (native)
Vendor lock-in       High              High            None
Reusability          Reusable actions  Templates       Functions/modules
Debugging            Log reading       Log reading     Local debugger
Type safety          No                No              Yes
Unit testing         No                No              Yes
Caching              Built-in          Built-in        Built-in
Secrets              GitHub Secrets    CI Variables    Dagger secrets
Marketplace          Actions market    CI templates    Daggerverse
```

### Core Architecture

```
┌─────────────────────────────────────────────┐
│  Your CI/CD Code (Python/TypeScript/Go)     │
│                                             │
│  @function                                  │
│  async def build(src: dagger.Directory):    │
│      return (                               │
│          dag.container()                     │
│          .from_("python:3.12")              │
│          .with_directory("/app", src)       │
│          .with_exec(["pip", "install"...])  │
│          .with_exec(["pytest"])             │
│      )                                      │
└──────────────┬──────────────────────────────┘
               │ Dagger SDK
               ▼
┌──────────────────────────────────────────────┐
│  Dagger Engine (runs in Docker)              │
│                                             │
│  ┌──────────────┐  ┌────────────────────┐   │
│  │ BuildKit     │  │ Content-Addressed  │   │
│  │ (execution)  │  │ Cache             │   │
│  └──────────────┘  └────────────────────┘   │
└──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Container Runtime (Docker, Podman)          │
└──────────────────────────────────────────────┘
```

---

## Step-by-Step Practical

### Comparing YAML vs Dagger

**The same pipeline in GitHub Actions YAML:**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: ruff check src/
      - run: pytest tests/ --cov=src
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/mycompany/myapp:${{ github.sha }}
```

**The same pipeline in Dagger (Python):**

```python
# ci/main.py
import dagger
from dagger import dag, function, object_type


@object_type
class Ci:
    @function
    async def lint(self, source: dagger.Directory) -> str:
        """Run linting on the source code."""
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "ruff"])
            .with_exec(["ruff", "check", "src/"])
            .stdout()
        )

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Run tests with coverage."""
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec(["pytest", "tests/", "--cov=src", "-v"])
            .stdout()
        )

    @function
    async def build(self, source: dagger.Directory) -> dagger.Container:
        """Build the Docker image."""
        return (
            dag.container()
            .build(source)
        )

    @function
    async def publish(
        self,
        source: dagger.Directory,
        registry: str,
        username: str,
        password: dagger.Secret,
    ) -> str:
        """Build and publish the Docker image."""
        image = await self.build(source)
        addr = await (
            image
            .with_registry_auth(registry, username, password)
            .publish(f"{registry}/mycompany/myapp:latest")
        )
        return addr
```

```bash
# Run locally -- SAME code, SAME result as CI
dagger call lint --source=.
dagger call test --source=.
dagger call build --source=.
dagger call publish --source=. --registry=ghcr.io --username=myuser --password=env:GITHUB_TOKEN
```

**Running the same Dagger pipeline from GitHub Actions:**

```yaml
# .github/workflows/ci.yml (thin wrapper)
name: CI
on: [push]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dagger/dagger-for-github@v6
        with:
          verb: call
          args: test --source=.
      - uses: dagger/dagger-for-github@v6
        with:
          verb: call
          args: publish --source=. --registry=ghcr.io --username=${{ github.actor }} --password=env:GITHUB_TOKEN
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Exercises

1. **YAML vs Code Comparison**: Take one of your existing GitHub Actions/GitLab CI pipelines and rewrite it in Dagger (Python). Compare: lines of code, readability, testability, and local execution capability.

2. **Local Pipeline Testing**: Write a Dagger pipeline that lints, tests, and builds a Python application. Run it locally 5 times and verify it produces identical results each time.

3. **Vendor Independence**: Write a Dagger pipeline and create CI wrapper files for three different CI systems (GitHub Actions, GitLab CI, CircleCI). Verify the same Dagger code runs on all three.

4. **Pipeline Complexity**: Write a Dagger pipeline with conditional logic (if tests pass, build; if branch is main, publish). Compare the complexity with the equivalent YAML-based approach.

---

## Knowledge Check

**Q1: What fundamental problem does Dagger solve that YAML-based CI/CD cannot?**

<details>
<summary>Answer</summary>

Dagger solves the "works in CI but not locally" problem. YAML-based CI/CD runs in vendor-specific environments that cannot be reproduced locally. When a pipeline fails in GitHub Actions, you must push fixes and wait for CI to run -- a slow feedback loop. Dagger pipelines run in containers via Docker, meaning the exact same pipeline runs on your laptop, in GitHub Actions, in GitLab CI, or anywhere Docker runs. This eliminates vendor lock-in (same code works on any CI provider) and enables local debugging (set breakpoints, inspect state, iterate quickly).
</details>

**Q2: How does Dagger achieve CI vendor independence?**

<details>
<summary>Answer</summary>

Dagger pipelines run inside the Dagger Engine, which uses BuildKit for container execution. The pipeline code (Python/TypeScript/Go) interacts with the engine via the Dagger SDK. The CI provider only needs to: (1) install the Dagger CLI, (2) run `dagger call <function>`. This is a one-line step in any CI system that supports Docker. The actual pipeline logic is in your code repository, not in CI vendor configuration. Switching from GitHub Actions to GitLab CI means changing the thin CI wrapper, not rewriting the pipeline.
</details>

**Q3: Why did the Docker founders create Dagger?**

<details>
<summary>Answer</summary>

Solomon Hykes and the Docker team observed that Docker solved "works on my machine" for applications by containerizing them, but CI/CD pipelines still had the same problem -- they worked in CI but not locally. Additionally, the CI/CD space was fragmented across incompatible YAML formats (GitHub Actions, GitLab CI, Jenkins, CircleCI), creating vendor lock-in. Dagger applies Docker's containerization philosophy to CI/CD: package the pipeline in containers, make it portable across environments, and let developers use real programming languages instead of YAML.
</details>

**Q4: What are the tradeoffs of using Dagger instead of native CI features?**

<details>
<summary>Answer</summary>

Tradeoffs: (1) **Learning curve** -- engineers must learn the Dagger SDK, which is a new abstraction even for those who know Python/TypeScript. (2) **Ecosystem maturity** -- GitHub Actions has 20,000+ marketplace actions; Dagger's module ecosystem is growing but smaller. (3) **Native integration loss** -- CI providers offer built-in features (caching, artifact management, environment protection rules) that Dagger must replicate. (4) **Debugging complexity** -- while local debugging is easier, Dagger adds a layer (the engine) between your code and execution. (5) **Docker dependency** -- Dagger requires Docker (or a compatible runtime), which some restricted environments may not allow. These tradeoffs are acceptable for teams prioritizing portability and local testing.
</details>
