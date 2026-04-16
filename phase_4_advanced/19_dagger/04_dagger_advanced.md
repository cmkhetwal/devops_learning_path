# Dagger Advanced

## Why This Matters in DevOps

Once you have mastered basic Dagger pipelines, the next step is building reusable modules, integrating with Kubernetes deployments, triggering GitOps workflows, and migrating existing CI/CD systems. These advanced patterns are what make Dagger practical for organizations with dozens of repositories and complex deployment requirements. This lesson covers the patterns that platform teams use to provide standardized, reusable CI/CD components across their organization.

---

## Core Concepts

### Custom Dagger Modules

A Dagger module packages functions for reuse across projects:

```bash
# Create a new module
mkdir python-ci-module && cd python-ci-module
dagger init --sdk=python --name=python-ci
```

```python
# python-ci-module/src/main.py
"""Reusable Python CI/CD module for the Daggerverse."""

import dagger
from dagger import dag, function, object_type


@object_type
class PythonCi:
    """Standard Python CI/CD pipeline functions."""

    python_version: str = "3.12"
    pip_cache_name: str = "pip-cache"

    @function
    def with_python_version(self, version: str) -> "PythonCi":
        """Set the Python version to use."""
        self.python_version = version
        return self

    def _base(self, source: dagger.Directory) -> dagger.Container:
        """Base container with Python and cached pip."""
        pip_cache = dag.cache_volume(self.pip_cache_name)
        return (
            dag.container()
            .from_(f"python:{self.python_version}-slim")
            .with_mounted_cache("/root/.cache/pip", pip_cache)
            .with_directory("/app", source, exclude=[".git", "__pycache__", ".venv"])
            .with_workdir("/app")
        )

    @function
    async def lint(
        self,
        source: dagger.Directory,
        config: str = "pyproject.toml",
    ) -> str:
        """Run ruff linter."""
        return await (
            self._base(source)
            .with_exec(["pip", "install", "ruff"])
            .with_exec(["ruff", "check", ".", "--config", config])
            .stdout()
        )

    @function
    async def test(
        self,
        source: dagger.Directory,
        coverage_threshold: int = 80,
        test_path: str = "tests/",
    ) -> str:
        """Run pytest with coverage enforcement."""
        return await (
            self._base(source)
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec([
                "pytest", test_path,
                f"--cov-fail-under={coverage_threshold}",
                "--cov=src",
                "-v",
            ])
            .stdout()
        )

    @function
    def build(
        self,
        source: dagger.Directory,
        dockerfile: str = "Dockerfile",
    ) -> dagger.Container:
        """Build Docker image from Dockerfile."""
        return dag.container().build(source, dockerfile=dockerfile)

    @function
    async def publish(
        self,
        source: dagger.Directory,
        image_ref: str,
        username: str,
        password: dagger.Secret,
    ) -> str:
        """Build and publish to container registry."""
        registry = image_ref.split("/")[0]
        return await (
            self.build(source)
            .with_registry_auth(registry, username, password)
            .publish(image_ref)
        )
```

**Using the module in another project:**

```bash
# Install the module
dagger install github.com/mycompany/python-ci-module@v1.0.0

# Use it
dagger call python-ci lint --source=.
dagger call python-ci test --source=. --coverage-threshold=90
```

### Cross-Language Module Support

Dagger modules are language-agnostic at the API level. A module written in Go can be called from Python:

```bash
# Install a Go-based module
dagger install github.com/purpleclay/daggerverse/helm@v0.1.0

# Call it from your Python pipeline
```

```python
@function
async def deploy_helm(
    self,
    chart_path: dagger.Directory,
    release_name: str,
    namespace: str,
    values: dagger.File,
) -> str:
    """Deploy using Helm (calling a Go-based Dagger module)."""
    return await (
        dag.helm()
        .install(
            chart=chart_path,
            name=release_name,
            namespace=namespace,
            values=[values],
        )
    )
```

### Dagger with Kubernetes Deployment

```python
@function
async def deploy_to_k8s(
    self,
    source: dagger.Directory,
    image_ref: str,
    kubeconfig: dagger.Secret,
    namespace: str = "default",
) -> str:
    """Deploy the built image to Kubernetes."""
    # Build and publish the image
    published_ref = await self.publish(source, image_ref)

    # Update Kubernetes deployment
    return await (
        dag.container()
        .from_("bitnami/kubectl:latest")
        .with_secret_variable("KUBECONFIG_DATA", kubeconfig)
        .with_exec(["sh", "-c", """
            echo "$KUBECONFIG_DATA" > /tmp/kubeconfig
            export KUBECONFIG=/tmp/kubeconfig
            kubectl set image deployment/myapp \
                myapp=""" + published_ref + """ \
                --namespace=""" + namespace + """ \
                --record
            kubectl rollout status deployment/myapp \
                --namespace=""" + namespace + """ \
                --timeout=300s
        """])
        .stdout()
    )
```

### Dagger + ArgoCD (Triggering GitOps)

Instead of directly deploying to Kubernetes, update the Git repository and let ArgoCD handle deployment:

```python
@function
async def trigger_gitops(
    self,
    source: dagger.Directory,
    image_ref: str,
    gitops_repo: str,
    git_token: dagger.Secret,
    environment: str = "production",
) -> str:
    """Update Helm values in GitOps repo to trigger ArgoCD deployment."""
    # Build and publish image
    published_ref = await self.publish(source, image_ref)

    # Clone GitOps repo, update values, push
    return await (
        dag.container()
        .from_("alpine/git:latest")
        .with_exec(["apk", "add", "--no-cache", "yq"])
        .with_secret_variable("GIT_TOKEN", git_token)
        .with_exec(["sh", "-c", f"""
            git clone https://x-access-token:$GIT_TOKEN@github.com/{gitops_repo}.git /gitops
            cd /gitops/apps/myapp/overlays/{environment}
            yq e '.image.tag = "{published_ref.split(":")[-1]}"' -i values.yaml
            git config user.email "dagger@ci.local"
            git config user.name "Dagger CI"
            git add .
            git commit -m "chore: update myapp image to {published_ref.split(":")[-1]}"
            git push
        """])
        .stdout()
    )
```

### Debugging Dagger Pipelines

```bash
# Interactive terminal at any point in the pipeline
dagger call build --source=. terminal

# Verbose logging
dagger call test --source=. --debug

# Export container filesystem for inspection
dagger call build --source=. export --path=./output.tar

# View Dagger engine logs
docker logs dagger-engine
```

### Migration from GitHub Actions to Dagger

```
Migration Strategy:
───────────────────

Phase 1: Shadow Mode
├── Keep existing GitHub Actions
├── Add Dagger pipeline alongside
├── Run both, compare results
└── Build team confidence

Phase 2: Gradual Migration
├── Replace one step at a time
├── Start with build/test (lowest risk)
├── Move to publish/deploy
└── Keep thin GHA wrapper

Phase 3: Full Migration
├── Dagger handles all pipeline logic
├── GHA only calls `dagger call pipeline`
├── Same pipeline runs locally
└── Can switch CI vendors in minutes
```

### When to Use Dagger vs Traditional CI

```
Use Dagger When:                          Use Traditional CI When:
─────────────────                         ────────────────────────
Local testing is important                Pipeline is simple (5-10 lines)
Multiple CI vendors (multi-repo)          Deep vendor integration needed
Complex pipeline logic                   GitHub-specific features used
Reusable pipelines across repos          Team knows YAML well
Team knows Python/TypeScript/Go          No Docker available
You want vendor independence             Marketplace actions sufficient
Pipeline debugging is frequent           Pipeline rarely changes
```

---

## Step-by-Step Practical

### Migrating a GitHub Actions Pipeline to Dagger

**Original GitHub Actions (to be migrated):**

```yaml
# .github/workflows/ci.yml (BEFORE - 80 lines of YAML)
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff
      - run: ruff check src/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_DB: test, POSTGRES_USER: test, POSTGRES_PASSWORD: test }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src --cov-fail-under=80
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test

  build-and-push:
    needs: [lint, test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

**Migrated to Dagger (Python):**

```python
# ci/main.py (AFTER - reusable, testable, portable)
import dagger
from dagger import dag, function, object_type


@object_type
class Ci:
    @function
    async def lint(self, source: dagger.Directory) -> str:
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
        postgres = (
            dag.container()
            .from_("postgres:16")
            .with_env_variable("POSTGRES_USER", "test")
            .with_env_variable("POSTGRES_PASSWORD", "test")
            .with_env_variable("POSTGRES_DB", "test")
            .with_exposed_port(5432)
            .as_service()
        )
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_service_binding("db", postgres)
            .with_env_variable("DATABASE_URL", "postgresql://test:test@db:5432/test")
            .with_exec(["pytest", "tests/", "--cov=src", "--cov-fail-under=80", "-v"])
            .stdout()
        )

    @function
    async def publish(self, source: dagger.Directory, tag: str, password: dagger.Secret) -> str:
        return await (
            dag.container()
            .build(source)
            .with_registry_auth("ghcr.io", "github-actor", password)
            .publish(f"ghcr.io/mycompany/myapp:{tag}")
        )

    @function
    async def pipeline(self, source: dagger.Directory, tag: str = "latest", password: dagger.Secret | None = None) -> str:
        await self.lint(source)
        await self.test(source)
        if password:
            addr = await self.publish(source, tag, password)
            return f"Published: {addr}"
        return "Pipeline passed (no publish)"
```

**New thin GitHub Actions wrapper:**

```yaml
# .github/workflows/ci.yml (AFTER - 15 lines)
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dagger/dagger-for-github@v6
        with:
          verb: call
          args: >
            pipeline
            --source=.
            --tag=${{ github.sha }}
            ${{ github.ref == 'refs/heads/main' && format('--password=env:GITHUB_TOKEN') || '' }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Exercises

1. **Module Development**: Create a reusable Dagger module for your organization's most common CI pattern. Include: configurable Python version, test framework, coverage threshold, and registry target.

2. **GitOps Integration**: Write a Dagger function that, after building and publishing an image, updates a Helm values file in a GitOps repository to trigger an ArgoCD deployment.

3. **Cross-Language**: Install a Dagger module written in a different language (e.g., a Go-based Helm module) and use it in your Python pipeline. Verify cross-language interoperability.

4. **Full Migration**: Take a real GitHub Actions pipeline (20+ lines) and migrate it completely to Dagger. Keep a thin CI wrapper. Measure: lines of code reduction, local testing capability gained, and any features lost.

5. **Pipeline Testing**: Write unit tests for your Dagger pipeline functions. Mock the container operations and verify that the pipeline logic (conditionals, error handling) works correctly.

---

## Knowledge Check

**Q1: How do Dagger modules promote reuse across an organization?**

<details>
<summary>Answer</summary>

Dagger modules package pipeline functions as versioned, installable packages -- similar to libraries in programming languages. A platform team can create a `python-ci` module with standardized lint, test, build, and publish functions. All repositories install this module (`dagger install github.com/mycompany/python-ci@v2.0`). When the platform team updates the module (adds security scanning, changes base image), all repositories get the update by bumping the version. This eliminates the copy-paste problem of YAML-based CI/CD where each repository has its own pipeline copy that drifts over time.
</details>

**Q2: How does Dagger integrate with GitOps workflows?**

<details>
<summary>Answer</summary>

Dagger handles the CI part (build, test, publish image) while ArgoCD handles the CD part (deploy to Kubernetes). The integration point is Git: after Dagger publishes a new image, it updates the image tag in a Helm values file or Kustomize overlay in the GitOps repository and pushes the commit. ArgoCD detects the change and syncs the new image to the cluster. This separation of concerns means Dagger does not need Kubernetes credentials -- it only needs Git push access to the GitOps repository.
</details>

**Q3: What are the main considerations when migrating from GitHub Actions to Dagger?**

<details>
<summary>Answer</summary>

Key considerations: (1) **Feature parity** -- some GitHub-specific features (environment protection rules, OIDC tokens, reusable workflows across repos) do not have direct Dagger equivalents and may need workarounds. (2) **Team skills** -- the team needs Python/TypeScript/Go skills, not just YAML editing. (3) **Docker dependency** -- all CI runners must support Docker, which some locked-down environments restrict. (4) **Migration strategy** -- do not rewrite everything at once. Start with shadow mode (run both), then gradually migrate step by step. (5) **Marketplace actions** -- heavily used marketplace actions may need to be reimplemented as Dagger functions or replaced with alternative approaches. (6) **Caching differences** -- GitHub Actions cache is different from Dagger's BuildKit cache; pipeline performance may differ initially.
</details>

**Q4: When should you NOT use Dagger?**

<details>
<summary>Answer</summary>

Do not use Dagger when: (1) your pipeline is very simple (5-10 lines of YAML) and the overhead of a Dagger module is not justified, (2) you heavily depend on CI vendor-specific features (GitHub environment protection rules, GitLab review apps, CircleCI orbs) that would be lost, (3) your CI environment does not support Docker (some enterprise environments with strict security policies), (4) your team is comfortable with YAML and local testing is not a priority, (5) you use a single CI vendor with no plans to change -- the portability benefit is moot. Evaluate the tradeoff: Dagger adds complexity upfront but pays off in reusability, testability, and portability for larger organizations with many repositories.
</details>
