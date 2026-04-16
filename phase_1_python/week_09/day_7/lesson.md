# Week 9, Day 7: Quiz Day - Docker & Containers Cheat Sheet

## Week 9 Quick Reference

### Docker SDK Setup
```python
import docker
from docker.errors import DockerException

# Connect
client = docker.from_env()
client.ping()           # True if connected
client.info()           # dict with Docker host info
client.version()        # dict with version details
```

### Container Management
```python
# List
client.containers.list()               # running only
client.containers.list(all=True)       # all (including stopped)

# Filter
client.containers.list(filters={"status": "running"})
client.containers.list(filters={"name": "web"})
client.containers.list(filters={"label": "env=prod"})

# Run
container = client.containers.run("nginx:latest", name="web", detach=True,
                                   ports={"80/tcp": 8080})

# Operations
container.stop(timeout=10)
container.start()
container.restart()
container.remove(force=True)

# Info
container.name          # str
container.status        # "running", "exited", etc.
container.id            # full SHA256
container.short_id      # 10-char prefix
container.image.tags    # list of tags
```

### Image Management
```python
# List
client.images.list()

# Pull
image = client.images.pull("nginx", tag="latest")

# Build
image, logs = client.images.build(path="./app", tag="myapp:v1")

# Info
image.tags              # ["nginx:latest"]
image.short_id          # "sha256:abc123..."
image.attrs["Size"]     # size in bytes

# Tag
image.tag("myregistry.com/myapp", tag="v1.0")

# Remove
client.images.remove("myapp:v1")
client.images.prune()   # remove unused images
```

### Docker Compose with PyYAML
```python
import yaml

# Read
with open("docker-compose.yml") as f:
    config = yaml.safe_load(f)

# Write
with open("docker-compose.yml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

# Structure
compose = {
    "version": "3.8",
    "services": {
        "web": {"image": "nginx", "ports": ["80:80"]},
        "db":  {"image": "postgres:15"},
    }
}
```

### Container Monitoring
```python
# Stats
stats = container.stats(stream=False)

# CPU calculation
cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
            stats["precpu_stats"]["cpu_usage"]["total_usage"]
system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
               stats["precpu_stats"]["system_cpu_usage"]
cpu_percent = (cpu_delta / system_delta) * 100.0

# Memory
mem_usage = stats["memory_stats"]["usage"]
mem_limit = stats["memory_stats"]["limit"]
mem_percent = (mem_usage / mem_limit) * 100.0

# Logs
logs = container.logs(tail=100)
logs = container.logs(stream=True)   # real-time
```

### Error Handling Pattern
```python
from docker.errors import DockerException, NotFound, APIError

try:
    container = client.containers.get("my-container")
except NotFound:
    print("Container not found")
except APIError as e:
    print(f"API error: {e}")
except DockerException as e:
    print(f"Docker error: {e}")
```

## Key Concepts Learned This Week
1. The Docker SDK provides a Pythonic interface to the Docker Engine API
2. Containers have a lifecycle: create -> run -> stop -> remove
3. Images are pulled from registries and can be built locally
4. Docker Compose files are YAML -- Python reads/writes them easily
5. Monitoring containers means tracking CPU, memory, logs, and health
6. Always handle the case where Docker is not available
7. Mock objects let you learn API patterns without a running daemon
