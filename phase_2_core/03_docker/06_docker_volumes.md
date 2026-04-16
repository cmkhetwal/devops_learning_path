# Docker Volumes

## Why This Matters in DevOps

Containers are ephemeral by design -- when a container is removed, all data inside it is lost. This is a feature, not a bug: it enables immutable infrastructure, fast scaling, and clean rollbacks. But applications need to persist data. Databases store records, applications generate logs, and services share files. Docker volumes solve this tension by providing persistent storage that exists independently of any container's lifecycle.

For DevOps engineers, understanding volume management is critical for running stateful services (databases, message queues, file storage), implementing backup strategies, managing data across container upgrades, and designing systems that balance the stateless container philosophy with real-world data persistence needs. Mismanaging volumes leads to data loss during deployments, orphaned volumes consuming disk space, and containers that cannot share the data they need.

The choice between bind mounts, named volumes, and tmpfs mounts directly affects your application's performance, portability, and security. Getting this right is the difference between a database that survives container restarts and one that loses all records on the next deployment.

---

## Core Concepts

### The Data Persistence Problem

When a container runs, it has a writable layer on top of the read-only image layers. Files created or modified in the container exist in this writable layer. When the container is removed, the writable layer is deleted along with all its data.

```
Container Running:
┌─────────────────────────┐
│  Writable Layer (data)  │  ← Lost when container is removed
├─────────────────────────┤
│  Image Layer 3 (code)   │  ← Read-only, shared
│  Image Layer 2 (deps)   │  ← Read-only, shared
│  Image Layer 1 (base)   │  ← Read-only, shared
└─────────────────────────┘
```

Volumes provide storage outside the container's filesystem, ensuring data survives container lifecycle events.

### Three Types of Mounts

Docker provides three mechanisms for persistent storage:

**1. Named Volumes** (Docker-managed)
```
Docker Area (/var/lib/docker/volumes/)  ←→  Container
```
- Managed by Docker
- Best for production data (databases, application state)
- Portable across hosts (with volume drivers)
- Survive container removal

**2. Bind Mounts** (Host directory)
```
Host Directory (/home/user/data/)  ←→  Container
```
- Map a specific host path to a container path
- Best for development (mount source code for live reloading)
- Depend on host filesystem structure
- Can be any directory on the host

**3. tmpfs Mounts** (Memory only)
```
Host RAM  ←→  Container
```
- Stored in the host's memory, never written to disk
- Best for sensitive data (secrets, temporary tokens)
- Data is lost when container stops
- Not shared between containers

### When to Use Each

| Use Case | Mount Type | Why |
|----------|-----------|-----|
| Database data | Named volume | Managed lifecycle, backup support |
| Source code in dev | Bind mount | Live reload, edit from host |
| Secrets at runtime | tmpfs | Never touches disk |
| Shared config files | Bind mount | Easy to edit from host |
| Container log files | Named volume | Persist across restarts |
| Build cache | Named volume | Faster rebuilds |

### Volume Lifecycle

Named volumes exist independently of containers:

```
1. Create volume:   docker volume create mydata
2. Use in container: docker run -v mydata:/data ...
3. Stop container:   docker stop mycontainer    → data persists
4. Remove container: docker rm mycontainer      → data persists
5. Start new container: docker run -v mydata:/data ...  → same data!
6. Remove volume:    docker volume rm mydata    → data deleted
```

### The Stateless Container Philosophy

The ideal container is stateless: it receives input, processes it, and sends output without storing anything locally. Persistent data should live in external systems:

- **Databases:** PostgreSQL, MySQL, MongoDB (running in their own containers with volumes, or as managed services)
- **Object storage:** S3, MinIO, GCS
- **Caches:** Redis, Memcached
- **Message queues:** RabbitMQ, Kafka

When a container must have local state (like a database container), volumes provide the mechanism. But the application container itself should remain stateless, enabling horizontal scaling and zero-downtime deployments.

---

## Step-by-Step Practical

### Creating and Using Named Volumes

```bash
# Create a named volume
docker volume create app-data
```

Expected output:

```
app-data
```

```bash
# List volumes
docker volume ls
```

Expected output:

```
DRIVER    VOLUME NAME
local     app-data
```

```bash
# Inspect the volume
docker volume inspect app-data
```

Expected output:

```json
[
    {
        "CreatedAt": "2026-04-16T10:00:00Z",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/app-data/_data",
        "Name": "app-data",
        "Options": {},
        "Scope": "local"
    }
]
```

```bash
# Run a container with the volume mounted
docker run -d --name writer \
  -v app-data:/data \
  alpine sh -c 'echo "Hello from container 1" > /data/message.txt && sleep 3600'

# Verify the file was written
docker exec writer cat /data/message.txt
```

Expected output:

```
Hello from container 1
```

```bash
# Remove the container
docker rm -f writer

# Run a NEW container with the SAME volume
docker run --rm -v app-data:/data alpine cat /data/message.txt
```

Expected output:

```
Hello from container 1
```

The data survived the container removal because it lives in the volume, not the container.

### Using Bind Mounts for Development

```bash
# Create a project directory on the host
mkdir -p ~/dev-project
echo '<h1>Hello World</h1>' > ~/dev-project/index.html

# Mount the host directory into the container
docker run -d --name dev-server \
  -p 8080:80 \
  -v ~/dev-project:/usr/share/nginx/html:ro \
  nginx:1.25

# Test the page
curl http://localhost:8080
```

Expected output:

```html
<h1>Hello World</h1>
```

```bash
# Modify the file on the HOST -- the container sees the change immediately
echo '<h1>Updated Content</h1>' > ~/dev-project/index.html

curl http://localhost:8080
```

Expected output:

```html
<h1>Updated Content</h1>
```

The `:ro` flag mounts the volume as read-only inside the container, preventing the container from modifying your source code. Remove `:ro` if the container needs write access.

### Using tmpfs Mounts for Sensitive Data

```bash
# Create a container with tmpfs mount
docker run -d --name secure-app \
  --tmpfs /secrets:rw,size=64m \
  alpine sh -c 'echo "API_KEY=abc123" > /secrets/api.key && sleep 3600'

# The secret is in memory, not on disk
docker exec secure-app cat /secrets/api.key
```

Expected output:

```
API_KEY=abc123
```

```bash
# Stop and remove the container -- secret is gone forever
docker rm -f secure-app
```

### PostgreSQL with Persistent Data

```bash
# Create a volume for PostgreSQL data
docker volume create postgres-data

# Run PostgreSQL with the volume
docker run -d --name postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secretpass \
  -e POSTGRES_DB=myapp \
  -v postgres-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Wait for PostgreSQL to start
sleep 5

# Create a table and insert data
docker exec -it postgres psql -U admin -d myapp -c "
CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie');
"
```

Expected output:

```
CREATE TABLE
INSERT 0 3
```

```bash
# Verify data exists
docker exec postgres psql -U admin -d myapp -c "SELECT * FROM users;"
```

Expected output:

```
 id |  name
----+---------
  1 | Alice
  2 | Bob
  3 | Charlie
(3 rows)
```

```bash
# Simulate a container upgrade (remove and recreate)
docker rm -f postgres

# Start a new container with the SAME volume
docker run -d --name postgres-new \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secretpass \
  -e POSTGRES_DB=myapp \
  -v postgres-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

sleep 5

# Data is still there!
docker exec postgres-new psql -U admin -d myapp -c "SELECT * FROM users;"
```

Expected output:

```
 id |  name
----+---------
  1 | Alice
  2 | Bob
  3 | Charlie
(3 rows)
```

### Sharing Data Between Containers

```bash
# Create a shared volume
docker volume create shared-data

# Writer container
docker run -d --name producer \
  -v shared-data:/output \
  alpine sh -c 'while true; do date >> /output/log.txt; sleep 5; done'

# Reader container
docker run -d --name consumer \
  -v shared-data:/input:ro \
  alpine sh -c 'tail -f /input/log.txt'

# Check the consumer's output
sleep 15
docker logs consumer
```

Expected output:

```
Thu Apr 16 10:00:00 UTC 2026
Thu Apr 16 10:00:05 UTC 2026
Thu Apr 16 10:00:10 UTC 2026
```

### Backup and Restore Volumes

```bash
# Backup a volume to a tar file
docker run --rm \
  -v postgres-data:/source:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz -C /source .

# Verify the backup
ls -lh postgres-backup.tar.gz
```

Expected output:

```
-rw-r--r-- 1 root root 5.2M Apr 16 10:15 postgres-backup.tar.gz
```

```bash
# Restore from backup to a new volume
docker volume create postgres-restored

docker run --rm \
  -v postgres-restored:/target \
  -v $(pwd):/backup:ro \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /target
```

### Cleaning Up Volumes

```bash
# Remove a specific volume (fails if in use)
docker volume rm app-data

# Remove all unused volumes (not attached to any container)
docker volume prune
```

Expected output:

```
WARNING! This will remove all local volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Volumes:
shared-data
postgres-restored

Total reclaimed space: 125MB
```

```bash
# List dangling volumes (created but never used)
docker volume ls -f dangling=true
```

---

## Exercises

### Exercise 1: Volume Persistence Proof

Run a container that writes a file to a named volume. Remove the container. Start a new container with the same volume and verify the file exists. Then remove the volume and start another container -- verify the data is gone. Document the entire lifecycle.

### Exercise 2: Development Workflow with Bind Mounts

Set up a development workflow using bind mounts: create a simple Python Flask application on your host, mount it into a container running Python, and demonstrate that editing the file on the host is immediately reflected inside the container. Use `--reload` to enable auto-restarting.

### Exercise 3: Database Upgrade Simulation

Run PostgreSQL 15 with a named volume, create tables and insert data. Stop and remove the container. Start PostgreSQL 16 with the same volume and verify all data survived the "upgrade." Document the steps and explain why this works.

### Exercise 4: Backup and Disaster Recovery

Create a PostgreSQL database with meaningful data. Write a backup script that creates a timestamped tar archive of the volume. Write a restore script that recreates the volume from a backup. Test the complete backup/restore cycle. This simulates a disaster recovery workflow.

### Exercise 5: Multi-Container Data Sharing

Create a pipeline where: Container A generates log files to a shared volume, Container B processes those logs and writes results to a second shared volume, and Container C serves the results via a web server. Verify the entire pipeline works and data flows correctly.

---

## Knowledge Check

**Q1: What is the difference between a named volume and a bind mount? When should you use each?**

<details>
<summary>Answer</summary>

**Named volumes** are managed by Docker and stored in `/var/lib/docker/volumes/`. They are portable, support volume drivers for remote storage, and their lifecycle is managed by Docker commands (`docker volume create/rm`). Use them for production data: databases, application state, and anything that must persist reliably.

**Bind mounts** map a specific host directory into the container. They depend on the host's filesystem structure and are not portable. Use them for development: mounting source code for live reloading, sharing configuration files, and accessing host files from containers.

Key difference: named volumes are managed by Docker and are the right choice for production. Bind mounts depend on the host path and are the right choice for development.

</details>

**Q2: Why do containers lose data when they are removed, and how do volumes solve this?**

<details>
<summary>Answer</summary>

Containers have a writable layer on top of the read-only image layers. All files created or modified during the container's lifetime exist in this writable layer. When the container is removed (`docker rm`), the writable layer is deleted along with all its data.

Volumes solve this by storing data outside the container's filesystem. A named volume exists at `/var/lib/docker/volumes/` on the host and persists regardless of the container's state. When a container is removed, the volume remains. A new container can mount the same volume and access the same data. The volume's lifecycle is independent of any container.

</details>

**Q3: When would you use a tmpfs mount, and why?**

<details>
<summary>Answer</summary>

Use tmpfs mounts for data that: (1) is sensitive and should never be written to disk (API keys, tokens, passwords), (2) is temporary and does not need to survive a container restart, and (3) benefits from the performance of in-memory storage (temporary computation results, caches).

tmpfs data exists only in the host's memory. It is never written to the Docker storage driver or the host filesystem. When the container stops, the data is gone. This makes tmpfs ideal for handling secrets that should not leave a trace on disk, even if the host is compromised.

</details>

**Q4: How do you backup and restore a Docker volume?**

<details>
<summary>Answer</summary>

**Backup:** Run a temporary container that mounts both the volume (as read-only) and a host directory, then create a tar archive:

```bash
docker run --rm -v myvolume:/source:ro -v $(pwd):/backup alpine \
  tar czf /backup/myvolume-backup.tar.gz -C /source .
```

**Restore:** Create a new volume and run a temporary container that extracts the archive into it:

```bash
docker volume create myvolume-restored
docker run --rm -v myvolume-restored:/target -v $(pwd):/backup:ro alpine \
  tar xzf /backup/myvolume-backup.tar.gz -C /target
```

For production databases, prefer database-native backup tools (`pg_dump`, `mysqldump`) as they ensure data consistency.

</details>

**Q5: What does the "stateless container philosophy" mean, and how do volumes fit into it?**

<details>
<summary>Answer</summary>

The stateless container philosophy means that application containers should not store persistent state locally. They receive input, process it, and send output. Any data that must persist (database records, user uploads, session state) should be stored in external systems: databases (their own containers with volumes or managed services), object storage (S3, MinIO), or caches (Redis).

Volumes fit into this philosophy as the mechanism that makes stateful backing services possible. The database container uses a volume for data persistence, but the application container connecting to it remains stateless. This separation enables: horizontal scaling (multiple stateless app containers, one database), zero-downtime deployments (replace app containers without touching data), and clean rollbacks (revert app containers without data side effects).

</details>
