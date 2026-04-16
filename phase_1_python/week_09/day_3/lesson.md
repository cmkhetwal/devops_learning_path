# Week 9, Day 3: Docker Image Management with Python

## What You'll Learn
- Listing Docker images with `client.images.list()`
- Pulling images with `client.images.pull()`
- Inspecting image details (tags, size, ID)
- Building images from Dockerfiles
- Removing unused images
- Tagging and organizing images

## Understanding Docker Images

Images are read-only templates used to create containers. Think of them as
blueprints -- you pull them from a registry, optionally build your own, then
run containers from them.

```
Registry (Docker Hub) --pull--> Local Images --run--> Containers
                                     ^
                                     |
                               Dockerfile --build-->
```

## Listing Images

```python
import docker

client = docker.from_env()

# List all local images
images = client.images.list()
for img in images:
    tags = img.tags if img.tags else ["<none>:<none>"]
    size_mb = img.attrs["Size"] / (1024 * 1024)
    print(f"  {tags[0]:30s}  {size_mb:8.1f} MB  {img.short_id}")
```

## Pulling Images

```python
# Pull an image
image = client.images.pull("nginx", tag="latest")
print(f"Pulled: {image.tags}")

# Pull with progress (low-level API)
for line in client.api.pull("python", tag="3.11-slim", stream=True, decode=True):
    status = line.get("status", "")
    progress = line.get("progress", "")
    print(f"  {status} {progress}")
```

## Image Details

```python
image = client.images.get("nginx:latest")

print(f"ID:      {image.id}")
print(f"Short:   {image.short_id}")
print(f"Tags:    {image.tags}")
print(f"Size:    {image.attrs['Size'] / (1024**2):.1f} MB")
print(f"Created: {image.attrs['Created']}")
print(f"OS:      {image.attrs['Os']}")
print(f"Arch:    {image.attrs['Architecture']}")
```

## Building Images

```python
# Build from a Dockerfile in the current directory
image, logs = client.images.build(
    path="./my-app",          # directory with Dockerfile
    tag="my-app:v1.0",        # name and tag
    rm=True,                  # remove intermediate containers
)
print(f"Built: {image.tags}")

# Build from a string (Dockerfile content)
import io
dockerfile = io.BytesIO(b"""
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
""")
image, logs = client.images.build(fileobj=dockerfile, tag="my-app:v2.0")
```

## Tagging and Removing

```python
# Tag an existing image
image = client.images.get("my-app:v1.0")
image.tag("my-registry.com/my-app", tag="v1.0")
image.tag("my-registry.com/my-app", tag="latest")

# Remove an image
client.images.remove("my-app:v1.0")

# Prune unused images (like `docker image prune`)
removed = client.images.prune()
print(f"Reclaimed: {removed.get('SpaceReclaimed', 0)} bytes")
```

## Simulating Images for Practice

```python
class MockImage:
    """Simulates a Docker image."""
    def __init__(self, name, tag="latest", size_mb=100):
        self.tags = [f"{name}:{tag}"]
        self.short_id = f"sha256:{hash(name) % (10**10):010d}"
        self.id = self.short_id
        self.attrs = {
            "Size": size_mb * 1024 * 1024,
            "Created": "2024-01-15T10:30:00Z",
            "Os": "linux",
            "Architecture": "amd64",
        }

    def tag(self, repository, tag="latest"):
        new_tag = f"{repository}:{tag}"
        if new_tag not in self.tags:
            self.tags.append(new_tag)

    def __repr__(self):
        return f"<Image: {self.tags[0]}>"
```

## Real-World Pattern: Image Inventory Report

```python
def image_report(images):
    """Generate a report of all local images."""
    total_size = 0
    print(f"{'IMAGE':35s} {'SIZE':>10s}  {'ID':12s}")
    print("-" * 60)

    for img in sorted(images, key=lambda i: i.tags[0] if i.tags else ""):
        tag = img.tags[0] if img.tags else "<none>"
        size = img.attrs["Size"]
        total_size += size
        print(f"{tag:35s} {size/(1024**2):>8.1f} MB  {img.short_id}")

    print("-" * 60)
    print(f"{'TOTAL':35s} {total_size/(1024**2):>8.1f} MB  ({len(images)} images)")
```

## DevOps Connection
- **CI/CD**: Build images automatically on code push
- **Registry management**: Tag and push images to private registries
- **Cleanup**: Prune old images to reclaim disk space
- **Inventory**: Know exactly what images are on each host
- **Security**: Scan images for vulnerabilities, track base image versions

## Key Takeaways
1. `client.images.list()` returns all local images
2. `client.images.pull("name", tag="tag")` downloads from a registry
3. Images have tags, sizes, IDs, and metadata in `.attrs`
4. `client.images.build()` creates images from Dockerfiles
5. Regular cleanup with `client.images.prune()` saves disk space
