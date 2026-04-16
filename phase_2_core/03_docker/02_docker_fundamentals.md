# Docker Fundamentals

## Why This Matters in DevOps

Docker is the tool that made containers accessible to every developer and operations engineer. Before Docker, using Linux containers required deep kernel knowledge -- namespaces, cgroups, and chroot configurations that few people could manage. Docker wrapped all of that complexity into a simple CLI and a declarative image format. Learning Docker fundamentals is not optional for a DevOps engineer; it is foundational.

Every CI/CD pipeline runs build and test steps inside containers. Every modern deployment pushes container images to registries and runs them in orchestrators. When a production container fails, you need to know how to inspect it, read its logs, and understand its lifecycle. The commands in this lesson are the ones you will use hundreds of times a week.

Understanding the container lifecycle -- creation, running, stopping, restarting, and removal -- is essential for designing reliable systems. Containers are ephemeral by design: they start fast, run a process, and can be replaced at any time. This lesson builds the muscle memory for working with that lifecycle.

---

## Core Concepts

### Docker Architecture

Docker uses a client-server architecture:

```
Docker CLI (client)  ──HTTP/socket──>  Docker Daemon (dockerd)
                                            │
                                       containerd
                                            │
                                          runc
                                            │
                                       Linux Kernel
```

- **Docker CLI:** The `docker` command you type in the terminal
- **Docker Daemon (dockerd):** A background process that manages containers, images, networks, and volumes
- **containerd:** Manages the container lifecycle (start, stop, pause)
- **runc:** The low-level runtime that creates containers using kernel features

### Registries

A registry is a storage and distribution system for Docker images. Think of it as a "package repository" for containers.

- **Docker Hub:** The default public registry (hub.docker.com)
- **Private registries:** AWS ECR, Google GCR, Azure ACR, Harbor, GitLab Container Registry
- **Image naming:** `registry/repository:tag` (e.g., `docker.io/nginx:1.25`)

When you run `docker pull nginx`, Docker downloads the image from Docker Hub by default.

### Container Lifecycle

```
Created  -->  Running  -->  Stopped  -->  Removed
  │              │             │
  │              │             └── docker start --> Running
  │              │
  │              └── docker stop/kill --> Stopped
  │
  └── docker start --> Running
```

A container goes through these states:
1. **Created:** Image has been instantiated but not started
2. **Running:** The main process is executing
3. **Stopped (Exited):** The main process has ended (exit code 0 = success, non-zero = error)
4. **Removed:** The container and its writable layer are deleted

Key insight: a stopped container still exists on disk and can be restarted. You must explicitly remove it to free resources.

### Interactive vs Detached Mode

- **Interactive (`-it`):** Attach your terminal to the container. Used for debugging, exploration, and running shells.
- **Detached (`-d`):** Run the container in the background. Used for services (web servers, databases, APIs).

---

## Step-by-Step Practical

### Installing Docker

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add the repository
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to the docker group (avoid sudo for every command)
sudo usermod -aG docker $USER

# Verify installation
docker --version
```

Expected output:

```
Docker version 27.0.3, build 7d4bcd8
```

```bash
# Test with hello-world
docker run hello-world
```

Expected output:

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

### Running Your First Container

```bash
# Run an Nginx web server in detached mode
docker run -d --name my-nginx -p 8080:80 nginx:1.25
```

Expected output:

```
Unable to find image 'nginx:1.25' locally
1.25: Pulling from library/nginx
...
Status: Downloaded newer image for nginx:1.25
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

Breaking down the flags:
- `-d`: Run in detached mode (background)
- `--name my-nginx`: Give the container a human-readable name
- `-p 8080:80`: Map host port 8080 to container port 80
- `nginx:1.25`: The image name and tag

```bash
# Test the running container
curl http://localhost:8080
```

Expected output:

```html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

### Listing Containers

```bash
# List running containers
docker ps
```

Expected output:

```
CONTAINER ID   IMAGE       COMMAND                  CREATED          STATUS          PORTS                  NAMES
a1b2c3d4e5f6   nginx:1.25  "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes    0.0.0.0:8080->80/tcp   my-nginx
```

```bash
# List ALL containers (including stopped)
docker ps -a
```

Expected output:

```
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                     PORTS                  NAMES
a1b2c3d4e5f6   nginx:1.25    "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes               0.0.0.0:8080->80/tcp   my-nginx
b2c3d4e5f6g7   hello-world   "/hello"                 5 minutes ago   Exited (0) 5 minutes ago                          sweet_turing
```

### Stopping, Starting, and Restarting Containers

```bash
# Stop a running container (sends SIGTERM, then SIGKILL after 10s)
docker stop my-nginx
```

Expected output:

```
my-nginx
```

```bash
# Start a stopped container
docker start my-nginx
```

Expected output:

```
my-nginx
```

```bash
# Restart a container (stop + start)
docker restart my-nginx

# Force stop (sends SIGKILL immediately -- use sparingly)
docker kill my-nginx
```

### Removing Containers

```bash
# Remove a stopped container
docker rm my-nginx

# Cannot remove a running container without force
docker rm my-nginx
```

Expected output:

```
Error response from daemon: cannot remove container "/my-nginx": container is running
```

```bash
# Force remove a running container
docker rm -f my-nginx

# Remove all stopped containers
docker container prune
```

Expected output:

```
WARNING! This will remove all stopped containers.
Are you sure you want to continue? [y/N] y
Deleted Containers:
b2c3d4e5f6g7
Total reclaimed space: 0B
```

### Interactive Mode

```bash
# Start an interactive shell in a new container
docker run --rm -it ubuntu:22.04 bash
```

Expected output:

```
root@a1b2c3d4e5f6:/#
```

```bash
# You are now inside the container
cat /etc/os-release
```

Expected output:

```
PRETTY_NAME="Ubuntu 22.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
...
```

```bash
# Type 'exit' to leave (container is removed because of --rm)
exit
```

The `--rm` flag automatically removes the container when it stops. Use this for throwaway containers.

### Working with Images

```bash
# List images on your system
docker images
```

Expected output:

```
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         1.25      a1b2c3d4e5f6   2 weeks ago    187MB
ubuntu        22.04     e4f5g6h7i8j9   3 weeks ago    77.8MB
hello-world   latest    k0l1m2n3o4p5   6 months ago   13.3kB
```

```bash
# Pull an image without running it
docker pull python:3.12-slim
```

Expected output:

```
3.12-slim: Pulling from library/python
...
Status: Downloaded newer image for python:3.12-slim
docker.io/library/python:3.12-slim
```

```bash
# Remove an image
docker rmi hello-world

# Remove all unused images
docker image prune -a
```

### Viewing Container Logs

```bash
# Start an Nginx container
docker run -d --name web nginx:1.25

# View logs
docker logs web
```

Expected output:

```
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/04/16 10:00:00 [notice] 1#1: nginx/1.25.0
2026/04/16 10:00:00 [notice] 1#1: built by gcc 12.2.0
```

```bash
# Follow logs in real-time (like tail -f)
docker logs -f web

# Show only the last 10 lines
docker logs --tail 10 web

# Show logs since a specific time
docker logs --since "2026-04-16T10:00:00" web
```

### Executing Commands in Running Containers

```bash
# Run a command in a running container
docker exec web cat /etc/nginx/nginx.conf

# Open an interactive shell in a running container
docker exec -it web bash
```

Expected output:

```
root@a1b2c3d4e5f6:/#
```

```bash
# This is useful for debugging, but remember:
# changes made here are LOST when the container is replaced.
exit
```

### Naming Conventions for Containers

Use meaningful, consistent names that indicate the container's purpose:

```bash
# Good naming
docker run -d --name api-gateway nginx
docker run -d --name auth-service python:3.12
docker run -d --name postgres-primary postgres:16

# Bad naming (Docker's random names are fun but useless for operations)
# romantic_panini, elastic_darwin, zen_hopper
```

---

## Exercises

### Exercise 1: Container Lifecycle Walkthrough

Run an Nginx container in detached mode with a name. Verify it is running with `docker ps`. Stop it and verify it appears in `docker ps -a` but not `docker ps`. Start it again and verify. Finally, remove it. Document each state transition.

### Exercise 2: Port Mapping Exploration

Run three Nginx containers simultaneously, each mapped to a different host port (8081, 8082, 8083). Verify you can reach each one with `curl`. Try to run a fourth on port 8081 and observe the error. Document why port conflicts occur.

### Exercise 3: Interactive Debugging

Run an Ubuntu container interactively. Inside it, install `curl` with `apt-get update && apt-get install -y curl`, then use it to make a web request. Exit and start a new container from the same image. Verify that `curl` is not installed in the new container. Explain why.

### Exercise 4: Log Investigation

Run a container that generates logs (use `docker run -d --name logger alpine sh -c 'while true; do echo "$(date): heartbeat"; sleep 5; done'`). Use `docker logs`, `docker logs -f`, `docker logs --tail 5`, and `docker logs --since` to practice different log viewing techniques. This simulates debugging a production service.

### Exercise 5: Cleanup Routine

After running multiple containers and pulling several images, practice a full cleanup: remove all stopped containers, remove all unused images, and verify with `docker ps -a` and `docker images`. Calculate the disk space reclaimed. Create a shell alias for this cleanup routine.

---

## Knowledge Check

**Q1: What is the difference between `docker run` and `docker start`?**

<details>
<summary>Answer</summary>

`docker run` creates a NEW container from an image and starts it. It is equivalent to `docker create` + `docker start`. Each `docker run` creates a new container instance.

`docker start` starts an EXISTING stopped container. It reuses the same container (with any changes that were made before it stopped, though those changes are in the writable layer and will be lost if the container is removed).

In DevOps practice, you typically use `docker run` for fresh deployments and `docker start` is rarely used because containers are treated as disposable -- you create new ones rather than restarting old ones.

</details>

**Q2: Why is the `--rm` flag useful, and when should you use it?**

<details>
<summary>Answer</summary>

The `--rm` flag automatically removes the container when its main process exits. Without it, stopped containers accumulate on disk and consume storage.

Use `--rm` for: (1) one-off tasks like running a test suite, (2) interactive debugging sessions, (3) CI/CD pipeline steps where the container is disposable, and (4) any temporary container you do not need to inspect after it stops.

Do NOT use `--rm` when you need to inspect a crashed container's logs or filesystem after it exits, as the container will be immediately removed.

</details>

**Q3: What does `-p 8080:80` mean, and why is port mapping necessary?**

<details>
<summary>Answer</summary>

`-p 8080:80` maps port 8080 on the host to port 80 inside the container. The format is `HOST_PORT:CONTAINER_PORT`.

Port mapping is necessary because containers run in their own network namespace. By default, container ports are not accessible from the host or external network. Port mapping creates a bridge between the host's network and the container's network. Without it, the service running inside the container is isolated and unreachable.

</details>

**Q4: What happens to changes made inside a running container when the container is removed?**

<details>
<summary>Answer</summary>

All changes are lost. A container has a writable layer on top of the read-only image layers. Any files created, modified, or installed inside the container exist only in this writable layer. When the container is removed (`docker rm`), the writable layer is deleted. This is why containers should be treated as immutable: all persistent changes belong in the Dockerfile (for image modifications) or in volumes (for data persistence).

</details>

**Q5: Explain the difference between `docker stop` and `docker kill`. When would you use each?**

<details>
<summary>Answer</summary>

`docker stop` sends SIGTERM to the container's main process, giving it a grace period (default 10 seconds) to shut down cleanly (close database connections, finish processing requests, flush buffers). If the process does not exit within the grace period, Docker sends SIGKILL.

`docker kill` sends SIGKILL immediately, forcing the process to terminate without cleanup.

Use `docker stop` in normal operations -- it allows graceful shutdown. Use `docker kill` only when a container is unresponsive and `docker stop` has timed out, or during incident response when you need immediate termination. In production, always prefer `docker stop` to avoid data corruption.

</details>
