# Dagger Pipelines

## Why This Matters in DevOps

Real CI/CD pipelines are not just "lint, test, build." They involve multi-stage builds with caching, test databases running alongside your tests, secret injection for registry authentication, and composed functions that build upon each other. This lesson covers the advanced pipeline patterns you need for production-grade CI/CD with Dagger -- from service dependencies to reusable modules.

---

## Core Concepts

### Multi-Stage Pipelines

Multi-stage pipelines use one container's output as another's input, similar to Docker multi-stage builds:

```python
@function
def build_production(self, source: dagger.Directory) -> dagger.Container:
    """Multi-stage build: test → build → production image."""
    # Stage 1: Install dependencies (cached)
    deps = (
        dag.container()
        .from_("python:3.12-slim")
        .with_exec(["pip", "install", "--no-cache-dir", "poetry"])
        .with_directory("/app", source.directory("pyproject.toml"))
        .with_workdir("/app")
        .with_exec(["poetry", "install", "--no-dev"])
    )

    # Stage 2: Build (uses deps layer)
    built = (
        deps
        .with_directory("/app/src", source.directory("src"))
        .with_exec(["poetry", "build"])
    )

    # Stage 3: Production image (minimal)
    production = (
        dag.container()
        .from_("python:3.12-slim")
        .with_file("/app/dist/app.whl", built.file("/app/dist/*.whl"))
        .with_exec(["pip", "install", "/app/dist/app.whl"])
        .with_entrypoint(["python", "-m", "myapp"])
    )

    return production
```

### Caching

```python
@function
def test_with_cache(self, source: dagger.Directory) -> str:
    """Run tests with pip cache for faster subsequent runs."""
    pip_cache = dag.cache_volume("pip-cache")

    return (
        dag.container()
        .from_("python:3.12-slim")
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_directory("/app", source)
        .with_workdir("/app")
        .with_exec(["pip", "install", "-r", "requirements.txt"])
        .with_exec(["pytest", "tests/", "-v"])
        .stdout()
    )
```

### Services (Databases, Redis for Testing)

Dagger can spin up service containers that your pipeline depends on:

```python
@function
async def test_with_database(self, source: dagger.Directory) -> str:
    """Run integration tests with a real PostgreSQL database."""
    # Start PostgreSQL as a service
    postgres = (
        dag.container()
        .from_("postgres:16")
        .with_env_variable("POSTGRES_USER", "test")
        .with_env_variable("POSTGRES_PASSWORD", "test")
        .with_env_variable("POSTGRES_DB", "testdb")
        .with_exposed_port(5432)
        .as_service()
    )

    # Run tests with the database service
    return await (
        dag.container()
        .from_("python:3.12-slim")
        .with_directory("/app", source)
        .with_workdir("/app")
        .with_exec(["pip", "install", "-r", "requirements.txt"])
        .with_service_binding("db", postgres)
        .with_env_variable("DATABASE_URL", "postgresql://test:test@db:5432/testdb")
        .with_exec(["pytest", "tests/integration/", "-v"])
        .stdout()
    )

@function
async def test_with_redis(self, source: dagger.Directory) -> str:
    """Run tests with Redis."""
    redis = (
        dag.container()
        .from_("redis:7")
        .with_exposed_port(6379)
        .as_service()
    )

    return await (
        dag.container()
        .from_("python:3.12-slim")
        .with_directory("/app", source)
        .with_workdir("/app")
        .with_exec(["pip", "install", "-r", "requirements.txt"])
        .with_service_binding("redis", redis)
        .with_env_variable("REDIS_URL", "redis://redis:6379")
        .with_exec(["pytest", "tests/", "-v"])
        .stdout()
    )
```

### Composing Functions

Functions can call each other, creating clean pipeline stages:

```python
@object_type
class Ci:
    @function
    async def all(
        self,
        source: dagger.Directory,
        registry: str = "ghcr.io",
        image_name: str = "mycompany/myapp",
        publish: bool = False,
        registry_username: str | None = None,
        registry_password: dagger.Secret | None = None,
    ) -> str:
        """Run the complete CI/CD pipeline."""
        results = []

        # Step 1: Lint
        lint_result = await self.lint(source)
        results.append(f"Lint: PASSED")

        # Step 2: Unit tests
        test_result = await self.test(source)
        results.append(f"Tests: PASSED")

        # Step 3: Integration tests with database
        int_result = await self.test_with_database(source)
        results.append(f"Integration Tests: PASSED")

        # Step 4: Build
        container = self.build(source)
        results.append(f"Build: PASSED")

        # Step 5: Publish (if requested)
        if publish and registry_username and registry_password:
            addr = await self.publish_image(
                source, f"{registry}/{image_name}",
                registry_username, registry_password
            )
            results.append(f"Published: {addr}")

        return "\n".join(results)
```

### Testing Pipelines Locally

```bash
# Run individual steps
dagger call lint --source=.
dagger call test --source=.
dagger call test-with-database --source=.
dagger call build --source=.

# Run the full pipeline
dagger call all --source=. --publish=false

# Debug: get a shell in the test container
dagger call test --source=. terminal

# Debug: see detailed logs
dagger call test --source=. --debug
```

### Dagger Modules (Reusable Pipeline Components)

Modules are packaged Dagger functions that can be shared and reused:

```bash
# Install a module from Daggerverse
dagger install github.com/purpleclay/daggerverse/golang@v0.3.0

# Use it in your pipeline
```

```python
# Using a community module
@function
async def security_scan(self, source: dagger.Directory) -> str:
    """Scan container for vulnerabilities using Trivy."""
    container = self.build(source)

    return await (
        dag.container()
        .from_("aquasec/trivy:latest")
        .with_exec([
            "trivy", "image",
            "--severity", "HIGH,CRITICAL",
            "--exit-code", "1",
            "--no-progress",
            "myapp:latest"
        ])
        .stdout()
    )
```

---

## Step-by-Step Practical

### Building a Complete CI/CD Pipeline

**Complete pipeline: lint, test, security scan, build, publish**

```python
# ci/main.py
"""Complete CI/CD pipeline with all production stages."""

import dagger
from dagger import dag, function, object_type


@object_type
class Ci:
    """Production CI/CD pipeline."""

    def _base(self, source: dagger.Directory) -> dagger.Container:
        """Shared base container with dependencies."""
        pip_cache = dag.cache_volume("pip-cache")
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_mounted_cache("/root/.cache/pip", pip_cache)
            .with_directory("/app", source, exclude=[".git", "__pycache__", ".venv", "ci/"])
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
        )

    @function
    async def lint(self, source: dagger.Directory) -> str:
        """Run linting with ruff."""
        return await (
            self._base(source)
            .with_exec(["ruff", "check", "src/"])
            .with_exec(["ruff", "format", "--check", "src/"])
            .stdout()
        )

    @function
    async def typecheck(self, source: dagger.Directory) -> str:
        """Run type checking with mypy."""
        return await (
            self._base(source)
            .with_exec(["pip", "install", "mypy"])
            .with_exec(["mypy", "src/", "--strict"])
            .stdout()
        )

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Run unit tests."""
        return await (
            self._base(source)
            .with_exec([
                "pytest", "tests/unit/",
                "--cov=src",
                "--cov-fail-under=80",
                "-v",
                "--tb=short",
            ])
            .stdout()
        )

    @function
    async def integration_test(self, source: dagger.Directory) -> str:
        """Run integration tests with PostgreSQL and Redis."""
        postgres = (
            dag.container()
            .from_("postgres:16")
            .with_env_variable("POSTGRES_USER", "test")
            .with_env_variable("POSTGRES_PASSWORD", "test")
            .with_env_variable("POSTGRES_DB", "testdb")
            .with_exposed_port(5432)
            .as_service()
        )

        redis = (
            dag.container()
            .from_("redis:7-alpine")
            .with_exposed_port(6379)
            .as_service()
        )

        return await (
            self._base(source)
            .with_service_binding("postgres", postgres)
            .with_service_binding("redis", redis)
            .with_env_variable("DATABASE_URL", "postgresql://test:test@postgres:5432/testdb")
            .with_env_variable("REDIS_URL", "redis://redis:6379")
            .with_exec(["pytest", "tests/integration/", "-v"])
            .stdout()
        )

    @function
    def build(self, source: dagger.Directory) -> dagger.Container:
        """Build the production Docker image."""
        return (
            dag.container()
            .build(source)
        )

    @function
    async def security_scan(self, source: dagger.Directory) -> str:
        """Scan the built image for vulnerabilities."""
        # Save the image as a tarball
        image_tar = await self.build(source).as_tarball()

        return await (
            dag.container()
            .from_("aquasec/trivy:latest")
            .with_file("/tmp/image.tar", image_tar)
            .with_exec([
                "trivy", "image",
                "--input", "/tmp/image.tar",
                "--severity", "HIGH,CRITICAL",
                "--no-progress",
            ])
            .stdout()
        )

    @function
    async def publish(
        self,
        source: dagger.Directory,
        image_ref: str,
        username: str,
        password: dagger.Secret,
    ) -> str:
        """Publish the image to a container registry."""
        registry = image_ref.split("/")[0]
        container = self.build(source)
        addr = await (
            container
            .with_registry_auth(registry, username, password)
            .publish(image_ref)
        )
        return addr

    @function
    async def pipeline(
        self,
        source: dagger.Directory,
        image_ref: str | None = None,
        username: str | None = None,
        password: dagger.Secret | None = None,
    ) -> str:
        """Run the complete CI/CD pipeline."""
        stages = []

        # Lint + Type Check (parallel in concept)
        await self.lint(source)
        stages.append("1. Lint: PASSED")

        await self.typecheck(source)
        stages.append("2. Type Check: PASSED")

        # Tests
        await self.test(source)
        stages.append("3. Unit Tests: PASSED")

        await self.integration_test(source)
        stages.append("4. Integration Tests: PASSED")

        # Build
        self.build(source)
        stages.append("5. Build: PASSED")

        # Security scan
        await self.security_scan(source)
        stages.append("6. Security Scan: PASSED")

        # Publish (optional)
        if image_ref and username and password:
            addr = await self.publish(source, image_ref, username, password)
            stages.append(f"7. Published: {addr}")

        return "\n".join(stages)
```

```bash
# Run the complete pipeline locally
dagger call pipeline --source=.

# Run with publishing
dagger call pipeline \
  --source=. \
  --image-ref=ghcr.io/mycompany/myapp:v1.0.0 \
  --username=myuser \
  --password=env:GITHUB_TOKEN
```

---

## Exercises

1. **Service Dependencies**: Write a Dagger pipeline that starts PostgreSQL and Redis as services, runs migrations, seeds test data, and then runs integration tests. Verify services are accessible.

2. **Caching Optimization**: Create a pipeline that uses `dag.cache_volume()` for pip, npm, or Go module caches. Measure the time difference between first run (no cache) and second run (cached).

3. **Complete Pipeline**: Build a complete CI/CD pipeline with all stages: lint, typecheck, unit test, integration test, security scan, build, and publish. Run it locally and then from GitHub Actions.

4. **Module Creation**: Create a reusable Dagger module that provides a `python_test()` function accepting source directory, Python version, and coverage threshold. Publish it to the Daggerverse (or document how you would).

5. **Migration Exercise**: Take an existing GitHub Actions workflow with 50+ lines of YAML and rewrite it in Dagger. Compare maintainability, local testing capability, and total lines of code.

---

## Knowledge Check

**Q1: How do Dagger services work and why are they useful for testing?**

<details>
<summary>Answer</summary>

Dagger services are containers that run as long-lived processes alongside your pipeline. You create them with `.as_service()` on a container and bind them with `.with_service_binding("name", service)`. The service is accessible via its binding name as a hostname. This is useful for testing because you can spin up real databases, caches, message queues, and other dependencies as part of your pipeline. Unlike Docker Compose or CI service containers, Dagger services are defined in the same code as your pipeline, are fully portable across CI vendors, and are automatically cleaned up after the pipeline completes.
</details>

**Q2: What is a cache volume and how does it speed up pipelines?**

<details>
<summary>Answer</summary>

A cache volume (`dag.cache_volume("name")`) is a persistent volume that survives between pipeline runs. You mount it at a path where package managers store their caches: `/root/.cache/pip` for pip, `/root/.npm` for npm, `$GOPATH/pkg/mod` for Go. On the first run, the package manager downloads everything. On subsequent runs, the cache volume contains the downloaded packages, so only new or updated packages are downloaded. This can reduce `pip install` from 60 seconds to 5 seconds. Cache volumes are stored in the Dagger Engine's Docker volume and persist as long as the engine runs.
</details>

**Q3: How do you compose Dagger functions for complex pipelines?**

<details>
<summary>Answer</summary>

Functions compose naturally through Python method calls. A shared `_base()` method creates a common container with dependencies installed, and other functions build on it. The `pipeline()` function calls `lint()`, `test()`, `build()`, and `publish()` sequentially. Functions return typed outputs (Container, str) that other functions can consume. This composition is more natural than YAML's `needs` dependencies because it uses standard programming patterns -- method calls, conditionals, loops, and error handling. You can also extract common patterns into shared functions or modules.
</details>

**Q4: What is the Daggerverse?**

<details>
<summary>Answer</summary>

The Daggerverse is a public registry of reusable Dagger modules, similar to GitHub Actions Marketplace. Modules provide pre-built functions for common tasks: building Go applications, running Helm, deploying to Kubernetes, scanning with Trivy, etc. You install modules with `dagger install github.com/author/module@version` and use them in your pipeline code. Unlike YAML-based action marketplaces, Dagger modules are type-safe, can be called from any supported language, and can be tested locally before use. The ecosystem is growing but is currently smaller than GitHub Actions' 20,000+ actions.
</details>
