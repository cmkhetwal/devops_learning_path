# Week 9, Day 1: Docker SDK for Python

## What You'll Learn
- Installing and importing the Docker SDK for Python
- Connecting to the Docker daemon with `docker.from_env()`
- Understanding the client object and its capabilities
- Handling connection errors gracefully

## Why Docker + Python?
In DevOps, Docker is everywhere. While you can run `docker` commands in a shell,
the Python SDK lets you **automate container workflows programmatically** -- build
CI/CD pipelines, manage deployments, create monitoring tools, and orchestrate
complex multi-container environments all from Python code.

## Installing the Docker SDK

```bash
pip install docker
```

The `docker` package provides a pure-Python client for the Docker Engine API.

## Connecting to Docker

```python
import docker

# Connect using environment variables / default socket
client = docker.from_env()

# Verify the connection
info = client.info()
print(f"Docker version: {info['ServerVersion']}")
print(f"Containers: {info['Containers']}")
print(f"Images: {info['Images']}")
```

## The Client Object

The `client` object is your gateway to everything Docker:

```python
client = docker.from_env()

# Main sub-APIs:
# client.containers  -> manage containers
# client.images      -> manage images
# client.networks    -> manage networks
# client.volumes     -> manage volumes

# Quick test: ping the Docker daemon
print(client.ping())  # Returns True if Docker is reachable
```

## Handling Connection Errors

Not every machine has Docker installed. Good DevOps code handles this:

```python
import docker
from docker.errors import DockerException

def get_docker_client():
    """Safely connect to Docker, return None if unavailable."""
    try:
        client = docker.from_env()
        client.ping()
        print("Connected to Docker successfully!")
        return client
    except DockerException as e:
        print(f"Docker not available: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

client = get_docker_client()
if client:
    info = client.info()
    print(f"OS: {info.get('OperatingSystem', 'Unknown')}")
    print(f"Architecture: {info.get('Architecture', 'Unknown')}")
    print(f"CPUs: {info.get('NCPU', 'Unknown')}")
    print(f"Memory: {info.get('MemTotal', 0) / (1024**3):.1f} GB")
else:
    print("Running in simulation mode -- no Docker daemon found.")
```

## Docker Client Configuration

```python
import docker

# Connect to a remote Docker host
# client = docker.DockerClient(base_url='tcp://192.168.1.100:2376')

# Connect with TLS
# tls_config = docker.tls.TLSConfig(
#     client_cert=('/path/to/client-cert.pem', '/path/to/client-key.pem'),
#     ca_cert='/path/to/ca.pem'
# )
# client = docker.DockerClient(base_url='tcp://remote:2376', tls=tls_config)

# Using from_env with a timeout
client = docker.from_env(timeout=10)
```

## Exploring Docker Info

```python
def print_docker_summary(client):
    """Print a summary of the Docker environment."""
    info = client.info()
    version = client.version()

    summary = {
        "Docker Version": version.get("Version", "Unknown"),
        "API Version": version.get("ApiVersion", "Unknown"),
        "OS": info.get("OperatingSystem", "Unknown"),
        "Architecture": info.get("Architecture", "Unknown"),
        "Total Containers": info.get("Containers", 0),
        "Running": info.get("ContainersRunning", 0),
        "Stopped": info.get("ContainersStopped", 0),
        "Images": info.get("Images", 0),
        "CPUs": info.get("NCPU", 0),
        "Memory (GB)": round(info.get("MemTotal", 0) / (1024**3), 1),
    }

    print("=" * 45)
    print("       DOCKER ENVIRONMENT SUMMARY")
    print("=" * 45)
    for key, value in summary.items():
        print(f"  {key:<20}: {value}")
    print("=" * 45)
```

## Simulating Docker for Learning

When Docker is not installed, you can still learn the patterns:

```python
class MockDockerClient:
    """Simulates a Docker client for learning purposes."""

    def ping(self):
        return True

    def info(self):
        return {
            "ServerVersion": "24.0.7",
            "Containers": 5,
            "ContainersRunning": 2,
            "ContainersStopped": 3,
            "Images": 12,
            "OperatingSystem": "Linux",
            "Architecture": "x86_64",
            "NCPU": 4,
            "MemTotal": 8 * (1024**3),
        }

    def version(self):
        return {
            "Version": "24.0.7",
            "ApiVersion": "1.43",
            "Os": "linux",
            "Arch": "amd64",
        }

# Use mock when Docker is unavailable
try:
    client = docker.from_env()
except:
    client = MockDockerClient()
```

## DevOps Connection
In production DevOps:
- **CI/CD Pipelines**: Programmatically build and push images
- **Monitoring**: Watch container health and resource usage
- **Deployment**: Spin up containers as part of automated deployments
- **Cleanup**: Remove old images and stopped containers automatically
- **Testing**: Spin up test environments in containers, tear them down after

## Key Takeaways
1. `docker.from_env()` connects using the local Docker socket
2. The client object provides access to containers, images, networks, volumes
3. Always handle `DockerException` -- Docker may not be available
4. The Python SDK mirrors the Docker CLI but gives you full programming power
