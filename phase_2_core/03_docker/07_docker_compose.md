# Docker Compose

## Why This Matters in DevOps

Running individual `docker run` commands with their flags for networks, volumes, ports, and environment variables quickly becomes unmanageable. A typical application with a web server, API, database, and cache requires four separate `docker run` commands, each with a dozen flags, and they need to be started in the right order with the right networks. Docker Compose solves this by defining your entire multi-container application in a single YAML file.

For DevOps engineers, Docker Compose is the bridge between local development and production orchestration. It teaches you to think declaratively about infrastructure: instead of writing imperative scripts ("run this, then run that"), you describe the desired state ("I want these services with these configurations") and let the tool figure out the execution. This same declarative mindset is exactly what Kubernetes, Terraform, and every other modern infrastructure tool requires.

Docker Compose is also the standard tool for local development environments. When a new developer joins the team, they should be able to clone the repository and run `docker compose up` to have a complete working environment in seconds. This dramatically reduces onboarding time and eliminates environment configuration bugs.

---

## Core Concepts

### What Docker Compose Does

Docker Compose takes a YAML file (`docker-compose.yml` or `compose.yml`) that describes your application's services, networks, and volumes, and translates it into Docker API calls. One command starts everything, another stops everything.

```
docker-compose.yml  →  docker compose up  →  Creates networks
                                           →  Creates volumes
                                           →  Pulls images
                                           →  Starts containers
                                           →  In correct order
```

### The Compose File Structure

A compose file has three top-level sections:

```yaml
services:    # Container definitions (the main section)
networks:    # Custom network definitions
volumes:     # Named volume definitions
```

### Service Definition

Each service maps to a container. The service definition includes everything you would put in a `docker run` command:

```yaml
services:
  web:
    image: nginx:1.25           # Or build: ./path
    ports:
      - "8080:80"
    environment:
      - ENV_VAR=value
    volumes:
      - ./html:/usr/share/nginx/html
    networks:
      - frontend
    depends_on:
      - api
    restart: unless-stopped
```

### depends_on and Service Ordering

`depends_on` controls startup order. Docker Compose starts dependencies first but does NOT wait for them to be "ready" -- only "started." This distinction matters for databases that take time to initialize.

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy  # Wait for health check to pass
  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s
      retries: 5
```

### Override Files

Docker Compose supports file layering. The base file (`docker-compose.yml`) defines the application structure. Override files modify it for specific environments.

```
docker-compose.yml              # Base configuration
docker-compose.override.yml     # Auto-loaded; typically dev settings
docker-compose.prod.yml         # Production overrides (explicit load)
```

The override file only needs to contain the differences, not the entire configuration.

---

## Step-by-Step Practical

### Basic Compose File

```bash
# Create a project directory
mkdir -p ~/compose-demo && cd ~/compose-demo

# Create the compose file
cat > docker-compose.yml <<'EOF'
services:
  web:
    image: nginx:1.25-alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    restart: unless-stopped

  api:
    image: python:3.12-slim
    working_dir: /app
    command: python -m http.server 8000
    volumes:
      - ./api:/app:ro
    expose:
      - "8000"
    restart: unless-stopped
EOF

# Create content directories
mkdir -p html api
echo '<h1>Frontend</h1>' > html/index.html
echo 'API is running' > api/index.html

# Start the application
docker compose up -d
```

Expected output:

```
[+] Running 3/3
 ✔ Network compose-demo_default  Created
 ✔ Container compose-demo-api-1  Started
 ✔ Container compose-demo-web-1  Started
```

```bash
# Verify services are running
docker compose ps
```

Expected output:

```
NAME                   IMAGE               COMMAND                  SERVICE   STATUS    PORTS
compose-demo-api-1     python:3.12-slim    "python -m http.serv…"  api       Up 10s    8000/tcp
compose-demo-web-1     nginx:1.25-alpine   "/docker-entrypoint.…"  web       Up 10s    0.0.0.0:8080->80/tcp
```

```bash
# Test the web service
curl http://localhost:8080
```

Expected output:

```html
<h1>Frontend</h1>
```

### Full-Stack Application with Compose

```bash
cat > docker-compose.yml <<'EOF'
services:
  # PostgreSQL Database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: ${DB_PASSWORD:-defaultpass}
      POSTGRES_DB: appdb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Application API
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://appuser:${DB_PASSWORD:-defaultpass}@db:5432/appdb
      REDIS_URL: redis://redis:6379
      LOG_LEVEL: ${LOG_LEVEL:-info}
    ports:
      - "8080:8080"
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - frontend
    depends_on:
      - api
    restart: unless-stopped

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
EOF
```

### Using Environment Variables

```bash
# Create a .env file (NOT committed to Git)
cat > .env <<'EOF'
DB_PASSWORD=supersecretpassword
LOG_LEVEL=debug
COMPOSE_PROJECT_NAME=myapp
EOF

# Docker Compose automatically reads .env
docker compose config  # Shows the resolved configuration
```

### Managing the Application Lifecycle

```bash
# Start all services in the background
docker compose up -d

# View logs from all services
docker compose logs

# Follow logs from a specific service
docker compose logs -f api

# Stop all services (containers remain)
docker compose stop

# Start stopped services
docker compose start

# Restart a specific service
docker compose restart api

# Stop and remove everything (containers, networks, but NOT volumes)
docker compose down

# Stop and remove everything INCLUDING volumes (destructive!)
docker compose down -v
```

### Scaling Services

```bash
# Scale the API to 3 instances
docker compose up -d --scale api=3

# Verify
docker compose ps
```

Expected output:

```
NAME              IMAGE       STATUS    PORTS
myapp-api-1       myapp-api   Up 5s     0.0.0.0:8080->8080/tcp
myapp-api-2       myapp-api   Up 5s     8080/tcp
myapp-api-3       myapp-api   Up 5s     8080/tcp
```

Note: Only the first instance gets the host port mapping. Use a load balancer (Nginx) to distribute traffic to scaled instances.

### Building Images with Compose

```bash
# Build all services that have a 'build' section
docker compose build

# Build without cache
docker compose build --no-cache

# Build and start in one command
docker compose up --build -d

# Build a specific service
docker compose build api
```

### Override Files for Development vs Production

```bash
# Base configuration: docker-compose.yml (shown above)

# Development overrides: docker-compose.override.yml
cat > docker-compose.override.yml <<'EOF'
services:
  api:
    build:
      context: ./api
      target: development
    volumes:
      - ./api:/app  # Mount source code for live reload
    environment:
      LOG_LEVEL: debug
      FLASK_DEBUG: "1"
    command: flask run --host=0.0.0.0 --port=8080 --reload

  db:
    ports:
      - "5432:5432"  # Expose DB port for local tools

  redis:
    ports:
      - "6379:6379"  # Expose Redis port for local debugging
EOF
```

```bash
# Development: override is auto-loaded
docker compose up -d
# Uses: docker-compose.yml + docker-compose.override.yml

# Production: explicitly specify files
cat > docker-compose.prod.yml <<'EOF'
services:
  api:
    build:
      context: ./api
      target: production
    environment:
      LOG_LEVEL: warning
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  db:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G

  nginx:
    ports:
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
EOF

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# Uses: docker-compose.yml + docker-compose.prod.yml (skips override)
```

### Executing Commands in Services

```bash
# Run a one-off command in a service
docker compose exec db psql -U appuser -d appdb -c "SELECT version();"

# Run a command in a new container (not the running one)
docker compose run --rm api python manage.py migrate

# Open a shell in a running service
docker compose exec api bash
```

### Viewing and Debugging

```bash
# Show running services and their status
docker compose ps

# Show the resolved compose file (with env vars expanded)
docker compose config

# Show resource usage per service
docker compose top

# Show events from all services
docker compose events
```

---

## Exercises

### Exercise 1: Basic Compose Application

Create a Docker Compose file that runs: an Nginx web server serving static files from a bind-mounted directory, and a Redis instance. Verify that Nginx responds on port 8080 and that you can connect to Redis from the Nginx container by name.

### Exercise 2: Full Stack with Health Checks

Build a compose file with PostgreSQL, Redis, and a Python API. Add health checks to PostgreSQL and Redis, and use `depends_on` with `condition: service_healthy` to ensure the API starts only after its dependencies are ready. Verify the startup order in the logs.

### Exercise 3: Development vs Production Configuration

Create a base `docker-compose.yml` and two override files: one for development (with source code bind mounts, debug logging, and exposed database ports) and one for production (with resource limits and no exposed database ports). Run each configuration and verify the differences.

### Exercise 4: Environment Variable Management

Create a compose file that uses environment variables for all configuration values (database credentials, API keys, log levels). Use a `.env` file for defaults and demonstrate overriding values at runtime with `DB_PASSWORD=newpass docker compose up -d`. Verify that the `.env` file is in `.gitignore`.

### Exercise 5: Service Scaling

Create a compose file with Nginx as a reverse proxy and a Python HTTP server as the backend. Scale the backend to three instances. Configure Nginx to load-balance across all three instances. Verify that requests are distributed by checking container logs.

---

## Knowledge Check

**Q1: What problem does Docker Compose solve, and how does it differ from plain `docker run` commands?**

<details>
<summary>Answer</summary>

Docker Compose solves the problem of managing multi-container applications. A typical application requires multiple `docker run` commands with dozens of flags for networks, volumes, ports, environment variables, and dependencies. These commands must be executed in the right order, and the configuration is scattered across shell scripts or documentation.

Docker Compose declares the entire application in a single YAML file: all services, their configurations, networks, and volumes. One command (`docker compose up`) creates everything in the correct order. This is declarative (describe what you want) rather than imperative (describe how to do it), which is easier to maintain, review, and version control.

</details>

**Q2: What is the difference between `depends_on` and a health check condition? Why does the distinction matter?**

<details>
<summary>Answer</summary>

`depends_on` without a condition only controls **startup order** -- it ensures the dependency container is started before the dependent container, but does NOT wait for the dependency to be ready. A database container might be "started" but still initializing and unable to accept connections.

`depends_on` with `condition: service_healthy` waits for the dependency's HEALTHCHECK to pass before starting the dependent service. This ensures the database is not just running but actually accepting connections.

This matters because without health check conditions, the API might start before the database is ready, causing connection errors on startup. In production, this leads to restart loops and failed deployments.

</details>

**Q3: How do override files work, and what is the development/production strategy?**

<details>
<summary>Answer</summary>

Docker Compose automatically loads `docker-compose.yml` and `docker-compose.override.yml` (if it exists). The override file merges with the base file, adding or replacing values.

The strategy: (1) `docker-compose.yml` contains the base application definition that works for all environments. (2) `docker-compose.override.yml` contains development-specific settings (bind mounts for code, debug flags, exposed database ports) and is auto-loaded during `docker compose up`. (3) `docker-compose.prod.yml` contains production settings (resource limits, no debug flags, no exposed database ports) and is explicitly loaded with `docker compose -f docker-compose.yml -f docker-compose.prod.yml up`.

This separation keeps environment-specific configuration out of the base file while sharing the common application structure.

</details>

**Q4: What is the difference between `docker compose exec` and `docker compose run`?**

<details>
<summary>Answer</summary>

`docker compose exec` runs a command inside an **already running** container. It connects to the existing container and executes the command in that context. Use it for: debugging a running service (`docker compose exec api bash`), running database queries (`docker compose exec db psql`), or checking service state.

`docker compose run` creates a **new container** from the service's configuration and runs the command in it. The new container gets the same network, volumes, and environment as the service definition, but it is a separate instance. Use it for: one-off tasks like database migrations (`docker compose run --rm api python manage.py migrate`), running tests, or executing administrative commands.

The `--rm` flag with `docker compose run` removes the container after the command finishes, preventing container accumulation.

</details>

**Q5: Why should you use `docker compose down -v` with caution?**

<details>
<summary>Answer</summary>

`docker compose down` stops containers and removes containers and networks, but preserves named volumes. `docker compose down -v` additionally removes all named volumes defined in the compose file.

This is dangerous because named volumes contain persistent data: database records, uploaded files, cache state, and application data. Running `docker compose down -v` in a production or staging environment deletes all persistent data irreversibly. It is useful for: resetting a development environment to a clean state, cleaning up after testing, or when you intentionally want to start fresh.

Always use `docker compose down` (without `-v`) unless you explicitly intend to destroy all persistent data. In CI/CD pipelines, `-v` is appropriate for cleanup after integration tests.

</details>
