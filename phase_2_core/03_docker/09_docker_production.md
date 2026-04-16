# Docker in Production

## Why This Matters in DevOps

Running Docker in development and running Docker in production are fundamentally different disciplines. In development, you care about fast iteration and easy debugging. In production, you care about reliability, resource efficiency, security, and graceful failure handling. A container that works perfectly on a developer's laptop can consume all available memory on a production server, fail to restart after a crash, or refuse to shut down cleanly during deployments.

DevOps engineers are responsible for the entire lifecycle of containers -- from build to production to decommissioning. This means setting resource limits that prevent one misbehaving container from taking down the host, configuring restart policies that handle crashes without human intervention, implementing health checks that enable load balancers and orchestrators to route traffic correctly, and ensuring containers shut down gracefully so that in-flight requests are completed and connections are closed cleanly.

Production readiness is not something you add at the end. It is a set of practices baked into your Dockerfiles, compose files, and deployment configurations from the start. This lesson covers the production concerns that separate a hobby project from a production system.

---

## Core Concepts

### Why Container Orchestration?

Running a single container on a single server is simple. Running hundreds of containers across dozens of servers requires orchestration. Container orchestration handles:

- **Scheduling:** Deciding which server runs which container
- **Scaling:** Adding or removing container instances based on load
- **Self-healing:** Restarting failed containers automatically
- **Networking:** Connecting containers across multiple hosts
- **Rolling updates:** Deploying new versions with zero downtime
- **Service discovery:** Helping containers find each other

Docker provides basic orchestration via Docker Swarm. Kubernetes is the industry standard for production orchestration. This lesson focuses on the Docker-level production practices that apply regardless of your orchestrator.

### Resource Limits

Without resource limits, a container can consume all available CPU and memory on the host, affecting every other container and the host itself. Resource limits are your first line of defense against noisy neighbors and runaway processes.

**Memory limits:** If a container exceeds its memory limit, Docker kills it (OOM -- Out of Memory). This is better than letting it consume all host memory and crash everything.

**CPU limits:** CPU limits throttle a container's CPU usage. Unlike memory limits, exceeding CPU limits does not kill the container -- it just runs slower.

### Restart Policies

Containers crash. Networks fail. Processes have bugs. Restart policies define how Docker responds when a container's main process exits.

| Policy | Behavior |
|--------|----------|
| `no` | Never restart (default) |
| `on-failure` | Restart only on non-zero exit code |
| `on-failure:5` | Restart on failure, max 5 attempts |
| `always` | Always restart, regardless of exit code |
| `unless-stopped` | Like `always`, but honors `docker stop` |

### Graceful Shutdown

When Docker stops a container, it sends `SIGTERM` to the main process (PID 1). The process should catch this signal and shut down cleanly: finish processing current requests, close database connections, flush buffers, and then exit. If the process does not exit within the grace period (default 10 seconds), Docker sends `SIGKILL`, which forces immediate termination.

Applications that do not handle SIGTERM drop in-flight requests, corrupt data, and leave connections hanging. Proper SIGTERM handling is a production requirement.

### Logging Drivers

Docker captures everything written to a container's stdout and stderr. By default, this goes to JSON files on the host. In production, you need to send logs to a centralized system (ELK stack, CloudWatch, Datadog, Splunk).

| Driver | Destination |
|--------|-------------|
| `json-file` | Local JSON files (default) |
| `syslog` | Syslog daemon |
| `journald` | Systemd journal |
| `fluentd` | Fluentd collector |
| `awslogs` | AWS CloudWatch |
| `gcplogs` | Google Cloud Logging |
| `splunk` | Splunk |

### Health Checks in Production

Health checks tell Docker (and your orchestrator) whether a container is actually working, not just running. A web server process might be alive but unable to serve requests due to a deadlock, exhausted connections, or a broken dependency.

Two types of health checks in the Kubernetes world:

- **Liveness probe:** Is the process alive? If not, restart it.
- **Readiness probe:** Can the process handle traffic? If not, remove it from the load balancer.

Docker's HEALTHCHECK maps to these concepts for non-Kubernetes deployments.

---

## Step-by-Step Practical

### Setting Resource Limits

```bash
# Run with memory and CPU limits
docker run -d --name limited-api \
  --memory=256m \
  --memory-swap=256m \
  --cpus=0.5 \
  --pids-limit=100 \
  flask-api:1.0.0
```

Breaking down the flags:
- `--memory=256m`: Hard memory limit (container is killed if exceeded)
- `--memory-swap=256m`: Same as memory = no swap allowed
- `--cpus=0.5`: Limit to 50% of one CPU core
- `--pids-limit=100`: Limit number of processes (prevents fork bombs)

```bash
# Verify resource limits
docker inspect limited-api --format '
  Memory: {{.HostConfig.Memory}}
  CPUs: {{.HostConfig.NanoCpus}}
  PidsLimit: {{.HostConfig.PidsLimit}}'
```

Expected output:

```
  Memory: 268435456
  CPUs: 500000000
  PidsLimit: 100
```

```bash
# Monitor resource usage in real-time
docker stats limited-api
```

Expected output:

```
CONTAINER ID   NAME          CPU %   MEM USAGE / LIMIT   MEM %   NET I/O     BLOCK I/O   PIDS
a1b2c3d4e5f6   limited-api   0.15%   42MiB / 256MiB      16.41%  1.2kB/0B    0B/0B       3
```

```bash
# Simulate OOM (Out of Memory) kill
docker run --rm --memory=10m alpine sh -c 'dd if=/dev/zero of=/dev/null bs=20M'
```

Expected output:

```
Killed
```

### Configuring Restart Policies

```bash
# Always restart unless explicitly stopped
docker run -d --name resilient-api \
  --restart=unless-stopped \
  flask-api:1.0.0

# Restart on failure with a maximum retry count
docker run -d --name careful-api \
  --restart=on-failure:5 \
  flask-api:1.0.0

# Check restart policy and count
docker inspect careful-api --format '
  Policy: {{.HostConfig.RestartPolicy.Name}}
  MaxRetries: {{.HostConfig.RestartPolicy.MaximumRetryCount}}
  RestartCount: {{.RestartCount}}'
```

Expected output:

```
  Policy: on-failure
  MaxRetries: 5
  RestartCount: 0
```

```bash
# Simulate a crashing container and watch it restart
docker run -d --name crasher \
  --restart=on-failure:3 \
  alpine sh -c 'echo "Starting..."; sleep 2; exit 1'

# Watch the restart count increase
sleep 10
docker inspect crasher --format 'RestartCount: {{.RestartCount}}'
```

Expected output:

```
RestartCount: 3
```

### Implementing Graceful Shutdown

```bash
# Create an application that handles SIGTERM properly
mkdir -p ~/graceful-app && cd ~/graceful-app

cat > app.py <<'EOF'
import signal
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        print(f"Request: {args[0]}", flush=True)

def graceful_shutdown(signum, frame):
    print("SIGTERM received. Starting graceful shutdown...", flush=True)
    print("Closing database connections...", flush=True)
    time.sleep(2)  # Simulate cleanup
    print("Flushing buffers...", flush=True)
    time.sleep(1)  # Simulate flush
    print("Shutdown complete.", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)

server = HTTPServer(('0.0.0.0', 8080), Handler)
print("Server starting on port 8080", flush=True)
server.serve_forever()
EOF

cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY app.py .
EXPOSE 8080
# Use exec form so Python receives SIGTERM directly (not shell)
CMD ["python", "app.py"]
EOF
```

```bash
# Build and run
docker build -t graceful-app:1.0.0 .
docker run -d --name graceful graceful-app:1.0.0

# Stop the container and watch the graceful shutdown
docker stop graceful
docker logs graceful
```

Expected output:

```
Server starting on port 8080
SIGTERM received. Starting graceful shutdown...
Closing database connections...
Flushing buffers...
Shutdown complete.
```

**Critical note:** Use the exec form (`CMD ["python", "app.py"]`) not the shell form (`CMD python app.py`). The shell form runs the process under `/bin/sh`, which does not forward signals to the child process. The exec form runs the process directly as PID 1, ensuring it receives SIGTERM.

### Configuring Logging

```bash
# Run with a specific logging driver
docker run -d --name logged-api \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  flask-api:1.0.0
```

This keeps at most 3 log files of 10 MB each (30 MB total), preventing disk exhaustion from verbose logging.

```bash
# Configure logging for AWS CloudWatch
docker run -d --name cloudwatch-api \
  --log-driver=awslogs \
  --log-opt awslogs-region=us-east-1 \
  --log-opt awslogs-group=/ecs/flask-api \
  --log-opt awslogs-stream-prefix=api \
  flask-api:1.0.0
```

### Health Checks in Production

```bash
# Run with a health check
docker run -d --name production-api \
  --health-cmd="curl -f http://localhost:8080/health || exit 1" \
  --health-interval=30s \
  --health-timeout=5s \
  --health-start-period=15s \
  --health-retries=3 \
  flask-api:1.0.0

# Monitor health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output:

```
NAMES            STATUS
production-api   Up 30 seconds (healthy)
```

### System Cleanup for Production Hosts

```bash
# See disk usage by Docker
docker system df
```

Expected output:

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          25        5         4.2GB     3.1GB (73%)
Containers      8         3         150MB     120MB (80%)
Local Volumes   12        4         2.5GB     1.8GB (72%)
Build Cache     50        0         1.2GB     1.2GB (100%)
```

```bash
# Remove all stopped containers, unused networks, dangling images, and build cache
docker system prune

# Remove everything including unused images (not just dangling)
docker system prune -a

# Remove everything including volumes (DESTRUCTIVE)
docker system prune -a --volumes
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
services:
  api:
    image: registry.example.com/api:v1.2.0
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      start_period: 15s
      retries: 3
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
```

### Production Checklist

```bash
# Verify an image is production-ready
echo "=== Production Readiness Checklist ==="

# 1. Non-root user
echo -n "Non-root user: "
docker inspect flask-api:1.0.0 --format '{{.Config.User}}'

# 2. Health check defined
echo -n "Health check: "
docker inspect flask-api:1.0.0 --format '{{.Config.Healthcheck}}'

# 3. No exposed unnecessary ports
echo -n "Exposed ports: "
docker inspect flask-api:1.0.0 --format '{{.Config.ExposedPorts}}'

# 4. Image size
echo -n "Image size: "
docker images flask-api:1.0.0 --format '{{.Size}}'

# 5. Vulnerability scan
echo "Running vulnerability scan..."
docker run --rm aquasec/trivy image --severity HIGH,CRITICAL flask-api:1.0.0
```

---

## Exercises

### Exercise 1: Resource Limits Testing

Run a container with 128 MB memory limit. Inside it, run a process that gradually allocates memory. Observe the OOM kill. Then set appropriate limits for a real application by monitoring `docker stats` under load and setting limits 20% above observed usage.

### Exercise 2: Restart Policy Comparison

Create a container that exits with code 1 after 5 seconds. Run it with each restart policy (`no`, `on-failure:3`, `always`, `unless-stopped`). Document the behavior of each policy: how many times does the container restart? What happens after `docker stop`? What happens after Docker daemon restart?

### Exercise 3: Graceful Shutdown Implementation

Write a Python or Node.js application that: opens a database connection on startup, handles HTTP requests, catches SIGTERM, stops accepting new requests, finishes processing in-flight requests, closes the database connection, and exits with code 0. Dockerize it and verify the shutdown sequence in the logs.

### Exercise 4: Logging Configuration

Run a container that generates 1 log line per second. Configure it with `json-file` driver with `max-size=1m` and `max-file=3`. Let it run for several minutes and verify that total log size never exceeds 3 MB. Then configure it to send logs to a Fluentd or Loki collector.

### Exercise 5: Production Readiness Audit

Take an existing Docker image from your team or an open-source project. Audit it against the production checklist: non-root user, health check, resource limits, logging configuration, security scanning, graceful shutdown handling, image size, and no secrets in the image. Write a report with findings and fixes.

---

## Knowledge Check

**Q1: Why are resource limits critical in production, and what happens when a container exceeds its memory limit?**

<details>
<summary>Answer</summary>

Without resource limits, a single container with a memory leak or CPU-intensive bug can consume all host resources, affecting every other container and potentially crashing the host. Resource limits isolate the blast radius of failures.

When a container exceeds its memory limit, the Linux OOM killer terminates it. Docker records this as an OOMKilled event. The container's restart policy then determines what happens next -- it may restart automatically (with `on-failure` or `always` policies) or stay stopped.

CPU limits work differently: exceeding a CPU limit does not kill the container but throttles it (the container gets less CPU time). This prevents a CPU-intensive container from starving others while keeping the container alive.

</details>

**Q2: What is the difference between `CMD ["python", "app.py"]` and `CMD python app.py` for graceful shutdown?**

<details>
<summary>Answer</summary>

`CMD ["python", "app.py"]` (exec form) runs Python directly as PID 1 in the container. When Docker sends SIGTERM, Python receives it directly and can handle it gracefully.

`CMD python app.py` (shell form) runs `/bin/sh -c "python app.py"`, making the shell PID 1. When Docker sends SIGTERM, the shell receives it but does NOT forward it to the Python process. The shell ignores SIGTERM, and after the grace period (default 10 seconds), Docker sends SIGKILL, which forcefully terminates everything without cleanup.

Always use exec form for production containers to ensure the application receives and can handle shutdown signals. This is one of the most common production issues with Docker containers.

</details>

**Q3: What restart policy should you use in production, and why?**

<details>
<summary>Answer</summary>

Use `unless-stopped` for most production services. It automatically restarts the container on crashes (non-zero exit codes), accidental exits, and Docker daemon restarts. But it respects `docker stop`, meaning when you intentionally stop a container, it stays stopped.

`always` is similar but restarts the container even after `docker stop` when the daemon restarts, which can be surprising during maintenance.

`on-failure:N` is useful for batch jobs or tasks that should not retry indefinitely -- they attempt N restarts and then stay stopped for investigation.

`no` should never be used for production services, as the first crash would leave the service permanently down until manual intervention.

</details>

**Q4: Why should you configure log rotation for production containers?**

<details>
<summary>Answer</summary>

Without log rotation, Docker's default `json-file` driver writes logs indefinitely to disk. A verbose application can generate gigabytes of logs, filling the disk and causing: (1) the Docker daemon to fail (cannot create new containers), (2) the host OS to become unresponsive, (3) other containers to crash due to no disk space, and (4) monitoring and alerting to stop working.

Configure `max-size` and `max-file` options to cap total log storage. For example, `max-size=10m` and `max-file=3` limits each container to 30 MB of logs. In production, you should also send logs to a centralized logging system (ELK, CloudWatch, Datadog) so that log rotation does not lose important data.

</details>

**Q5: What is the purpose of the `--read-only` flag and `no-new-privileges` security option?**

<details>
<summary>Answer</summary>

`--read-only` makes the container's filesystem read-only. The container cannot write to any path except explicitly mounted volumes or tmpfs mounts. This prevents attackers from: writing malicious scripts, modifying application code, or installing backdoors. Applications that need to write temporary files use tmpfs mounts (`--tmpfs /tmp`).

`no-new-privileges` prevents processes inside the container from gaining additional privileges through setuid/setgid binaries or other mechanisms. Even if an attacker finds a setuid binary inside the container, they cannot use it to escalate privileges.

Together, these options significantly reduce the attack surface of a container. They should be enabled for all production containers unless the application specifically requires write access or privilege escalation (which should be rare and documented).

</details>
