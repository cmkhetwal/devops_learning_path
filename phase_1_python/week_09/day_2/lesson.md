# Week 9, Day 2: Container Management with Python

## What You'll Learn
- Listing containers with `client.containers.list()`
- Running containers with `client.containers.run()`
- Stopping, starting, and removing containers
- Filtering containers by name, status, and labels
- Reading container attributes: status, name, id, image

## Container Lifecycle

```
create -> start -> running -> stop -> stopped -> remove
                      |                  |
                      +---> pause -------+
```

## Listing Containers

```python
import docker

client = docker.from_env()

# List running containers only (default)
running = client.containers.list()
for c in running:
    print(f"{c.short_id}  {c.name:25s}  {c.status}  {c.image.tags}")

# List ALL containers (including stopped)
all_containers = client.containers.list(all=True)
for c in all_containers:
    print(f"{c.short_id}  {c.name:25s}  {c.status}")
```

## Running Containers

```python
# Run a container (like `docker run`)
container = client.containers.run(
    "nginx:latest",         # image name
    name="my-web-server",   # container name
    detach=True,            # run in background
    ports={"80/tcp": 8080}, # port mapping
)
print(f"Started: {container.name} ({container.short_id})")

# Run and get output (foreground)
output = client.containers.run("alpine", "echo Hello from container!")
print(output.decode())  # b'Hello from container!\n'
```

## Container Operations

```python
container = client.containers.get("my-web-server")

# Check status
print(f"Status: {container.status}")  # running, exited, paused, etc.

# Stop a container
container.stop(timeout=10)
print(f"After stop: {container.status}")

# Restart
container.restart()

# Pause / unpause
container.pause()
container.unpause()

# Remove (must be stopped first, or force=True)
container.stop()
container.remove()
# Or: container.remove(force=True)  # stops and removes
```

## Filtering Containers

```python
# Filter by status
running = client.containers.list(filters={"status": "running"})
exited = client.containers.list(all=True, filters={"status": "exited"})

# Filter by name (partial match)
web_containers = client.containers.list(filters={"name": "web"})

# Filter by label
labeled = client.containers.list(filters={"label": "env=production"})

# Filter by ancestor image
nginx_containers = client.containers.list(filters={"ancestor": "nginx"})
```

## Container Attributes

```python
container = client.containers.get("my-container")

print(f"ID:      {container.id}")          # full SHA256
print(f"Short:   {container.short_id}")    # 10-char prefix
print(f"Name:    {container.name}")
print(f"Status:  {container.status}")      # running, exited, etc.
print(f"Image:   {container.image.tags}")  # ['nginx:latest']
print(f"Created: {container.attrs['Created']}")
print(f"Ports:   {container.ports}")
```

## Simulating Containers for Practice

Since Docker may not be available, here is a mock system:

```python
class MockContainer:
    """Simulates a Docker container object."""
    def __init__(self, name, image, status="running", container_id=None):
        self.name = name
        self.image_name = image
        self.status = status
        self.id = container_id or f"sha256:{'a' * 64}"
        self.short_id = self.id[:10]

    def stop(self):
        self.status = "exited"

    def start(self):
        self.status = "running"

    def remove(self):
        self.status = "removed"

    def __repr__(self):
        return f"<Container: {self.name} ({self.status})>"
```

## Real-World Pattern: Container Inventory

```python
def container_inventory(client):
    """Generate an inventory of all containers."""
    containers = client.containers.list(all=True)
    inventory = {"running": [], "stopped": [], "other": []}

    for c in containers:
        entry = {"name": c.name, "id": c.short_id, "image": str(c.image.tags)}
        if c.status == "running":
            inventory["running"].append(entry)
        elif c.status == "exited":
            inventory["stopped"].append(entry)
        else:
            inventory["other"].append(entry)

    return inventory
```

## DevOps Connection
- **Deployment**: Programmatically start/stop containers during releases
- **Scaling**: Spin up or tear down containers based on demand
- **Cleanup**: Remove old, exited containers automatically
- **Health checks**: Monitor container status and restart unhealthy ones
- **Inventory**: Track what is running across multiple hosts

## Key Takeaways
1. `client.containers.list(all=True)` shows all containers, not just running
2. `client.containers.run()` creates and starts a container
3. Use filters to find specific containers by name, status, or label
4. Always handle the case where a container might not exist
5. `container.remove(force=True)` stops and removes in one step
