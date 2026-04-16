# Docker Troubleshooting

## Why This Matters in DevOps

Containers fail. Images do not build. Networks do not connect. Applications crash silently. Troubleshooting Docker issues is a core DevOps skill that you will exercise regularly, often under pressure during production incidents. The difference between an engineer who stares at a failing container and one who diagnoses and fixes it in minutes comes down to knowing the right commands and having a systematic debugging methodology.

Docker troubleshooting is particularly challenging because containers are ephemeral and isolated. You cannot SSH into them the way you would a traditional server. Crashed containers may be removed before you can inspect them. Logs might be lost. The filesystem is layered and read-only. Network namespaces hide connectivity issues from the host's perspective.

This lesson builds a troubleshooting toolkit and methodology that works for development, CI/CD pipelines, and production environments. Every command here is one you will use repeatedly in your DevOps career. When the pager goes off at 3 AM and the deployment is failing, these are the skills that get the system back online.

---

## Core Concepts

### The Troubleshooting Methodology

A systematic approach to Docker troubleshooting follows these steps:

```
1. Identify: What is the symptom? (container not starting, app not responding, etc.)
2. Gather: Collect information (logs, status, configuration, events)
3. Hypothesize: Form a theory about the root cause
4. Test: Verify the theory with targeted commands
5. Fix: Apply the solution
6. Verify: Confirm the fix resolves the issue
7. Prevent: Add monitoring, tests, or documentation to prevent recurrence
```

### Common Failure Categories

| Category | Symptoms | First Command |
|----------|----------|---------------|
| Container won't start | Exits immediately, status Exited(1) | `docker logs` |
| Application not responding | Container running but not serving | `docker exec` + `curl` |
| Networking issues | Cannot connect between containers | `docker network inspect` |
| Image build failures | Build errors, unexpected behavior | `docker build` output |
| Permission errors | Access denied inside container | `docker exec` + `ls -la` |
| Resource exhaustion | OOM killed, high CPU | `docker stats` |
| Volume issues | Data missing, permission denied | `docker inspect` mounts |
| Slow performance | High latency, timeouts | `docker stats` + `docker exec top` |

### Key Debugging Commands

| Command | Purpose |
|---------|---------|
| `docker logs` | Read container output (stdout/stderr) |
| `docker exec` | Run commands inside a running container |
| `docker inspect` | View detailed container/image/network configuration |
| `docker stats` | Real-time resource usage monitoring |
| `docker events` | Stream Docker daemon events |
| `docker diff` | Show filesystem changes in a container |
| `docker top` | View processes running in a container |
| `docker port` | Show port mappings |

---

## Step-by-Step Practical

### Debugging with docker logs

```bash
# View all logs from a container
docker logs my-container

# Follow logs in real-time (like tail -f)
docker logs -f my-container

# Show only the last 50 lines
docker logs --tail 50 my-container

# Show logs from the last 5 minutes
docker logs --since 5m my-container

# Show logs between two timestamps
docker logs --since "2026-04-16T10:00:00" --until "2026-04-16T10:30:00" my-container

# Show timestamps with each log line
docker logs -t my-container
```

Expected output (with timestamps):

```
2026-04-16T10:15:30.123456789Z Server starting on port 8080
2026-04-16T10:15:31.234567890Z Connected to database
2026-04-16T10:15:45.345678901Z ERROR: Failed to connect to Redis: Connection refused
```

### Debugging with docker exec

```bash
# Open an interactive shell in a running container
docker exec -it my-container bash

# If bash is not available (Alpine images):
docker exec -it my-container sh

# Run a specific debugging command
docker exec my-container cat /app/config.yml

# Check network connectivity from inside the container
docker exec my-container ping -c 3 database

# Check DNS resolution
docker exec my-container nslookup database

# Check if the application port is listening
docker exec my-container netstat -tlnp
# Or if netstat is not available:
docker exec my-container ss -tlnp
# Or:
docker exec my-container cat /proc/net/tcp

# Check environment variables
docker exec my-container env
```

### Debugging with docker inspect

```bash
# Full inspection (JSON output)
docker inspect my-container

# Get specific fields using Go template format
# Container IP address
docker inspect my-container --format '{{.NetworkSettings.IPAddress}}'

# Container state and exit code
docker inspect my-container --format '
  Status: {{.State.Status}}
  Running: {{.State.Running}}
  ExitCode: {{.State.ExitCode}}
  Error: {{.State.Error}}
  OOMKilled: {{.State.OOMKilled}}
  StartedAt: {{.State.StartedAt}}
  FinishedAt: {{.State.FinishedAt}}'
```

Expected output for a crashed container:

```
  Status: exited
  Running: false
  ExitCode: 137
  Error:
  OOMKilled: true
  StartedAt: 2026-04-16T10:15:30.123Z
  FinishedAt: 2026-04-16T10:16:45.456Z
```

Exit code 137 = killed by SIGKILL (128 + 9). Combined with OOMKilled: true, this tells you the container ran out of memory.

```bash
# View mounted volumes
docker inspect my-container --format '{{json .Mounts}}' | python3 -m json.tool

# View environment variables
docker inspect my-container --format '{{json .Config.Env}}' | python3 -m json.tool

# View network settings
docker inspect my-container --format '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
```

### Common Exit Codes and Their Meanings

```bash
# Check the exit code of a stopped container
docker inspect my-container --format '{{.State.ExitCode}}'
```

| Exit Code | Meaning | Common Cause |
|-----------|---------|-------------|
| 0 | Success | Process completed normally |
| 1 | General error | Application error, missing file, bad config |
| 2 | Shell misuse | Bad command syntax in CMD/ENTRYPOINT |
| 126 | Permission denied | Script not executable |
| 127 | Command not found | Typo in CMD, missing binary |
| 137 | SIGKILL (kill -9) | OOM killed, or `docker kill` |
| 139 | SIGSEGV | Segmentation fault (bad memory access) |
| 143 | SIGTERM | Graceful shutdown via `docker stop` |

### Monitoring Resource Usage

```bash
# Real-time resource monitoring for all containers
docker stats
```

Expected output:

```
CONTAINER ID   NAME       CPU %   MEM USAGE / LIMIT     MEM %   NET I/O       BLOCK I/O    PIDS
a1b2c3d4e5f6   api        15.2%   128MiB / 512MiB       25.0%   15.2MB/8.1MB  0B/12.5MB    12
e4f5g6h7i8j9   database   3.5%    256MiB / 1GiB         25.0%   8.1MB/15.2MB  45MB/120MB   35
k0l1m2n3o4p5   redis      0.5%    24MiB / 128MiB        18.8%   2.1MB/1.5MB   0B/0B        4
```

```bash
# One-shot stats (no streaming)
docker stats --no-stream

# Stats for specific containers
docker stats api database redis

# View processes inside a container
docker top my-container
```

Expected output:

```
UID     PID     PPID    C    STIME   TTY     TIME      CMD
1000    12345   12300   0    10:15   ?       00:00:05  gunicorn: master [app:app]
1000    12346   12345   0    10:15   ?       00:00:12  gunicorn: worker [app:app]
1000    12347   12345   0    10:15   ?       00:00:11  gunicorn: worker [app:app]
```

### Debugging Crashed Containers

A crashed container (status "Exited") cannot be exec'd into. Here is how to investigate:

```bash
# Step 1: Check the logs (most important)
docker logs crashed-container

# Step 2: Check the exit code and state
docker inspect crashed-container --format '
  ExitCode: {{.State.ExitCode}}
  OOMKilled: {{.State.OOMKilled}}
  Error: {{.State.Error}}'

# Step 3: View filesystem changes (what did the container modify?)
docker diff crashed-container
```

Expected output:

```
C /app
A /app/error.log
C /tmp
A /tmp/core.dump
```

- `C` = Changed
- `A` = Added
- `D` = Deleted

```bash
# Step 4: Copy files out of the crashed container for investigation
docker cp crashed-container:/app/error.log ./error.log
docker cp crashed-container:/tmp/core.dump ./core.dump

# Step 5: Start a debugging container from the same image
docker run --rm -it --entrypoint sh flask-api:1.0.0
# Now you can explore the filesystem, try running the app manually, etc.
```

### Debugging Networking Issues

```bash
# Check which networks a container is connected to
docker inspect my-container --format '{{range $net, $config := .NetworkSettings.Networks}}
  Network: {{$net}}
  IP: {{$config.IPAddress}}
  Gateway: {{$config.Gateway}}
{{end}}'

# List containers on a specific network
docker network inspect app-network --format '{{range .Containers}}
  {{.Name}}: {{.IPv4Address}}
{{end}}'

# Test connectivity from inside a container
docker exec my-container sh -c 'wget -qO- http://api:8080/health || echo "FAILED"'

# Check DNS resolution
docker exec my-container nslookup database 127.0.0.11

# Check if a port is open
docker exec my-container sh -c 'nc -zv database 5432'
```

Expected output (when connection works):

```
database (172.18.0.3:5432) open
```

Expected output (when connection fails):

```
nc: database (172.18.0.3:5432): Connection refused
```

```bash
# Common networking diagnosis checklist
echo "1. Are containers on the same network?"
docker network inspect app-network

echo "2. Is the service actually listening on the expected port?"
docker exec database ss -tlnp

echo "3. Is there a firewall or security group blocking traffic?"
docker exec my-container iptables -L 2>/dev/null || echo "No iptables access"

echo "4. Is DNS resolving correctly?"
docker exec my-container getent hosts database
```

### Debugging Build Issues

```bash
# Build with verbose output
docker build --progress=plain -t myapp:debug .

# Build without cache (force fresh build)
docker build --no-cache -t myapp:debug .

# Build up to a specific stage (multi-stage debugging)
docker build --target builder -t myapp:builder .

# Run a shell in the builder stage to inspect
docker run --rm -it myapp:builder sh
```

### Debugging Permission Issues

```bash
# Check file ownership inside the container
docker exec my-container ls -la /app/

# Check which user the container runs as
docker exec my-container whoami
docker exec my-container id
```

Expected output:

```
uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
```

```bash
# Common permission fix: ensure files are owned by the app user
# In Dockerfile:
# COPY --chown=appuser:appuser . /app/

# Debug volume mount permissions
docker exec my-container ls -la /data/
# If permission denied, check host directory ownership
ls -la /host/path/to/volume
```

### Using docker events

```bash
# Stream all Docker events in real-time
docker events
```

Expected output:

```
2026-04-16T10:30:00.000000000Z container create abc123 (image=flask-api:1.0.0, name=api)
2026-04-16T10:30:01.000000000Z container start abc123 (image=flask-api:1.0.0, name=api)
2026-04-16T10:30:15.000000000Z container die abc123 (exitCode=137, image=flask-api:1.0.0)
2026-04-16T10:30:16.000000000Z container start abc123 (image=flask-api:1.0.0, name=api)
```

```bash
# Filter events by type
docker events --filter type=container

# Filter by specific container
docker events --filter container=api

# Filter by event
docker events --filter event=die
```

### Common Dockerfile Mistakes

```bash
# Mistake 1: Shell form CMD (SIGTERM not forwarded)
# BAD:  CMD python app.py
# GOOD: CMD ["python", "app.py"]

# Mistake 2: Running as root
# BAD:  No USER instruction
# GOOD: USER appuser

# Mistake 3: Using ADD instead of COPY
# BAD:  ADD . /app/
# GOOD: COPY . /app/

# Mistake 4: Not leveraging layer caching
# BAD:  COPY . /app/ then RUN pip install
# GOOD: COPY requirements.txt then RUN pip install then COPY . /app/

# Mistake 5: Installing debug tools in production
# BAD:  RUN apt-get install -y vim curl wget strace gdb
# GOOD: Use multi-stage builds; debug with docker exec or sidecar containers

# Mistake 6: Large build context
# BAD:  No .dockerignore, sending .git, node_modules to daemon
# GOOD: Comprehensive .dockerignore
```

### Build Cache Issues

```bash
# Common symptom: build is slower than expected or includes stale code
# Solution 1: Clear build cache
docker builder prune

# Solution 2: Force fresh build
docker build --no-cache -t myapp:fresh .

# Solution 3: Clear everything
docker system prune -a

# Check build cache usage
docker system df
```

---

## Exercises

### Exercise 1: Diagnose a Crashing Container

Create a container that crashes on startup (e.g., missing configuration file, bad import, connection to nonexistent database). Without looking at the Dockerfile or source code, use only Docker commands (`docker logs`, `docker inspect`, `docker diff`) to diagnose the root cause. Document your troubleshooting steps.

### Exercise 2: Network Connectivity Debugging

Set up three containers (frontend, backend, database) on two networks. Intentionally misconfigure one (wrong network, wrong hostname). Use Docker networking commands to diagnose why the frontend cannot reach the database. Fix the issue and verify connectivity.

### Exercise 3: OOM Kill Investigation

Run a container with a 64 MB memory limit and an application that gradually allocates memory. Monitor it with `docker stats` until it is OOM-killed. Use `docker inspect` to confirm the OOM kill. Set an appropriate memory limit and verify the container runs stably.

### Exercise 4: Build Failure Debugging

Create a Dockerfile with three intentional errors (e.g., referencing a file that does not exist in COPY, using a command not available in the base image, incorrect multi-stage COPY reference). Debug each error using build output and fix them. Document the error messages and solutions.

### Exercise 5: Complete Incident Simulation

Set up a multi-container application (API + database + cache). Simulate a production incident by introducing a failure (kill the database, exhaust container memory, misconfigure the network). Practice the full troubleshooting workflow: identify the symptom, gather information, hypothesize, test, fix, and verify. Write an incident report documenting the timeline.

---

## Knowledge Check

**Q1: A container exits with code 137. What does this mean, and how do you investigate?**

<details>
<summary>Answer</summary>

Exit code 137 means the process was killed by SIGKILL (128 + signal 9). The two most common causes are:

1. **OOM kill:** The container exceeded its memory limit. Check with `docker inspect --format '{{.State.OOMKilled}}' container-name`. If true, increase the memory limit or fix the memory leak.
2. **Manual kill:** Someone ran `docker kill` or the orchestrator killed the container. Check `docker events --filter container=container-name` for the timeline.

Investigation steps: (1) `docker inspect` to check OOMKilled status, (2) `docker stats` to review resource usage patterns, (3) `docker events` to see who/what triggered the kill, (4) `docker logs` to check for application-level errors before the kill.

</details>

**Q2: How do you debug a container that starts but does not respond to HTTP requests?**

<details>
<summary>Answer</summary>

Systematic approach:

1. **Verify the container is running:** `docker ps` -- check status is "Up"
2. **Check logs for errors:** `docker logs container-name` -- look for startup errors, binding failures, or exception traces
3. **Verify the port mapping:** `docker port container-name` -- ensure host port maps to the correct container port
4. **Check if the app is listening inside the container:** `docker exec container-name ss -tlnp` -- verify the application is bound to `0.0.0.0:PORT` (not `127.0.0.1:PORT`, which only accepts internal connections)
5. **Test from inside the container:** `docker exec container-name curl http://localhost:PORT` -- this isolates whether the issue is the application or the network
6. **Check health status:** `docker inspect --format '{{.State.Health.Status}}'` -- check if health checks are failing

Common causes: application bound to localhost instead of 0.0.0.0, wrong port mapping, application crash after initial startup log, or dependency not ready.

</details>

**Q3: A container's filesystem changes are lost after restart. Is this a bug or expected behavior?**

<details>
<summary>Answer</summary>

This is expected behavior. Containers have a writable layer on top of read-only image layers. Changes made during runtime (installed packages, created files, modified configurations) exist only in this writable layer. When the container is removed and recreated (as happens during `docker compose down && up`, Kubernetes pod restarts, or deployments), a fresh writable layer is created from the image.

If data needs to persist, it must be stored in a volume (named volume or bind mount). If an application modification needs to persist, it belongs in the Dockerfile (image rebuild).

This is not a bug -- it is the immutable infrastructure pattern working as designed. Use `docker diff container-name` to see what files changed in the writable layer, and move anything important to a volume or the Dockerfile.

</details>

**Q4: How do you extract files from a stopped (crashed) container for investigation?**

<details>
<summary>Answer</summary>

You cannot use `docker exec` on a stopped container, but you can: (1) Copy files out with `docker cp crashed-container:/path/to/file ./local-file`, (2) View filesystem changes with `docker diff crashed-container`, (3) Create a new image from the crashed container with `docker commit crashed-container debug-image` and then run a shell in that image with `docker run --rm -it debug-image sh`, (4) Start a new container from the same image with an overridden entrypoint: `docker run --rm -it --entrypoint sh image-name` to explore the filesystem.

Always check `docker logs` first -- the answer is usually in the output. Use `docker inspect` to check exit codes and OOM status before diving into the filesystem.

</details>

**Q5: How do you diagnose Docker DNS resolution failures between containers?**

<details>
<summary>Answer</summary>

DNS resolution failures usually mean containers are on different networks or using the default bridge network (which does not support DNS).

Diagnostic steps:
1. **Check networks:** `docker inspect container-name --format '{{json .NetworkSettings.Networks}}'` for both containers -- they must share at least one custom network.
2. **Test DNS from inside the container:** `docker exec container-name nslookup target-container 127.0.0.11` (127.0.0.11 is Docker's embedded DNS server on custom networks).
3. **Verify the target container is running:** `docker ps` -- a stopped container is removed from DNS.
4. **Check the network:** `docker network inspect network-name` -- verify both containers are listed.
5. **Check for typos:** Container names in DNS must exactly match the `--name` parameter or the service name in Docker Compose.

Fix: Ensure both containers are on the same custom bridge network. The default bridge network does not provide DNS resolution between containers.

</details>
