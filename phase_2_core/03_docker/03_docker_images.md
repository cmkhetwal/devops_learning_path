# Docker Images

## Why This Matters in DevOps

Docker images are the artifacts that flow through your CI/CD pipeline. Every build produces an image, every registry stores images, every deployment runs images. Understanding how images are structured -- layers, caching, and the build process -- directly affects your build speed, deployment reliability, and infrastructure costs.

A poorly built image can be 2 GB when it should be 50 MB. A Dockerfile that does not leverage caching rebuilds everything from scratch on every commit, turning a 30-second build into a 15-minute one. In a DevOps organization building hundreds of images per day across dozens of services, these inefficiencies compound into real costs: slower feedback loops, higher compute bills, and longer deployment times.

This lesson teaches you how Docker images are constructed, how to write Dockerfiles that produce efficient images, and how multi-stage builds keep production images small and secure.

---

## Core Concepts

### What Is a Docker Image?

An image is a read-only template used to create containers. It contains everything needed to run an application: code, runtime, libraries, environment variables, and configuration files. An image is defined by a Dockerfile and built using `docker build`.

Think of an image as a class in object-oriented programming. A container is an instance of that class. You can create many containers from one image.

### Layers and the Union Filesystem

Images are built in layers. Each instruction in a Dockerfile creates a new layer on top of the previous one. These layers are stacked using a union filesystem (typically overlay2) that presents them as a single coherent filesystem.

```
Layer 5: COPY . /app           (your application code)
Layer 4: RUN pip install ...    (Python dependencies)
Layer 3: RUN apt-get install .. (system packages)
Layer 2: ENV PYTHONPATH=/app    (environment variable)
Layer 1: FROM python:3.12-slim  (base image layers)
```

Key properties of layers:
- **Read-only:** Once a layer is created, it never changes
- **Shared:** If two images use the same base image, they share those layers on disk
- **Cached:** If a layer has not changed, Docker reuses the cached version during builds
- **Additive:** Each layer only contains the differences from the previous layer

### Layer Caching

Docker caches each layer. During a build, Docker checks if the instruction and its context have changed. If nothing changed, it reuses the cached layer instead of rebuilding. This is why Dockerfile instruction order matters enormously.

```dockerfile
# BAD: Copying code before installing dependencies
# Any code change invalidates the pip install cache
COPY . /app
RUN pip install -r requirements.txt

# GOOD: Install dependencies first, then copy code
# Dependencies are cached unless requirements.txt changes
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app
```

### Dockerfile Instructions

| Instruction | Purpose | Example |
|-------------|---------|---------|
| `FROM` | Set the base image | `FROM python:3.12-slim` |
| `RUN` | Execute a command during build | `RUN apt-get update && apt-get install -y curl` |
| `COPY` | Copy files from host to image | `COPY app.py /app/` |
| `ADD` | Like COPY but can extract tars and fetch URLs | `ADD archive.tar.gz /app/` |
| `WORKDIR` | Set the working directory | `WORKDIR /app` |
| `ENV` | Set environment variables | `ENV PORT=8080` |
| `EXPOSE` | Document which port the app uses | `EXPOSE 8080` |
| `CMD` | Default command when container starts | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | Main executable (CMD becomes arguments) | `ENTRYPOINT ["python"]` |
| `ARG` | Build-time variable | `ARG VERSION=1.0` |
| `LABEL` | Add metadata | `LABEL maintainer="team@example.com"` |
| `USER` | Set the user to run as | `USER appuser` |
| `VOLUME` | Declare a mount point | `VOLUME /data` |
| `HEALTHCHECK` | Define container health check | `HEALTHCHECK CMD curl -f http://localhost/` |

### CMD vs ENTRYPOINT

These are often confused but serve different purposes:

- **CMD:** Provides the default command. Can be overridden entirely at runtime.
- **ENTRYPOINT:** Sets the main executable. CMD values become arguments to ENTRYPOINT.

```dockerfile
# CMD only: entire command can be overridden
CMD ["python", "app.py"]
# docker run myapp               --> runs: python app.py
# docker run myapp bash           --> runs: bash (CMD replaced)

# ENTRYPOINT + CMD: entrypoint is fixed, CMD provides default args
ENTRYPOINT ["python"]
CMD ["app.py"]
# docker run myapp               --> runs: python app.py
# docker run myapp test.py        --> runs: python test.py (CMD replaced)
```

### Multi-Stage Builds

Multi-stage builds use multiple `FROM` statements in a single Dockerfile. Each `FROM` starts a new build stage. You can copy artifacts from one stage to another, leaving behind build tools and intermediate files.

```dockerfile
# Stage 1: Build
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp .

# Stage 2: Production (only the binary, no build tools)
FROM alpine:3.19
COPY --from=builder /app/myapp /usr/local/bin/
CMD ["myapp"]
```

Result: The final image contains only the compiled binary and Alpine Linux (~15 MB), not the entire Go toolchain (~800 MB).

### .dockerignore

Like `.gitignore`, the `.dockerignore` file excludes files from the build context. This speeds up builds and prevents sensitive files from being included in images.

---

## Step-by-Step Practical

### Building Your First Image

```bash
# Create a project directory
mkdir ~/flask-app && cd ~/flask-app

# Create a simple Flask application
cat > app.py <<'EOF'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "service": "api",
        "version": os.getenv("APP_VERSION", "unknown"),
        "status": "running"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

# Create requirements file
cat > requirements.txt <<'EOF'
flask==3.0.0
gunicorn==21.2.0
EOF

# Create the Dockerfile
cat > Dockerfile <<'EOF'
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (leverages layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Set environment variables
ENV APP_VERSION=1.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
EOF
```

```bash
# Build the image
docker build -t flask-api:1.0.0 .
```

Expected output:

```
[+] Building 15.2s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.12-slim
 => [1/5] FROM docker.io/library/python:3.12-slim@sha256:...
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY app.py .
 => exporting to image
 => => naming to docker.io/library/flask-api:1.0.0
```

```bash
# Run the image
docker run -d --name api -p 8080:8080 flask-api:1.0.0

# Test it
curl http://localhost:8080
```

Expected output:

```json
{"service":"api","status":"running","version":"1.0.0"}
```

### Demonstrating Layer Caching

```bash
# Modify the application code
echo '# Updated' >> app.py

# Rebuild -- notice cached layers
docker build -t flask-api:1.0.1 .
```

Expected output:

```
[+] Building 1.8s (10/10) FINISHED
 => CACHED [2/5] WORKDIR /app
 => CACHED [3/5] COPY requirements.txt .
 => CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY app.py .
```

Notice that steps 2-4 say "CACHED" -- Docker reused those layers because `requirements.txt` did not change. Only the `COPY app.py` step ran again. This is why you copy dependency files before copying application code.

### Creating a .dockerignore

```bash
cat > .dockerignore <<'EOF'
# Version control
.git
.gitignore

# Python artifacts
__pycache__
*.pyc
*.pyo
.pytest_cache
.venv
venv

# IDE
.vscode
.idea

# Docker
Dockerfile
docker-compose*.yml
.dockerignore

# Documentation
README.md
docs/

# CI/CD
.github
.gitlab-ci.yml

# Secrets (should never be in an image)
.env
*.pem
*.key
EOF
```

### Inspecting Image Layers

```bash
# View the layers of an image
docker history flask-api:1.0.0
```

Expected output:

```
IMAGE          CREATED          CREATED BY                                      SIZE
a1b2c3d4e5f6   5 minutes ago   CMD ["gunicorn" "--bind" "0.0.0.0:8080" "app…   0B
<missing>      5 minutes ago   EXPOSE map[8080/tcp:{}]                         0B
<missing>      5 minutes ago   ENV PYTHONUNBUFFERED=1                          0B
<missing>      5 minutes ago   ENV APP_VERSION=1.0.0                           0B
<missing>      5 minutes ago   COPY app.py . # buildkit                       523B
<missing>      5 minutes ago   RUN pip install --no-cache-dir -r requiremen…   15.2MB
<missing>      5 minutes ago   COPY requirements.txt . # buildkit              52B
<missing>      5 minutes ago   WORKDIR /app                                    0B
<missing>      2 weeks ago     /bin/sh -c #(nop)  CMD ["python3"]              0B
...
```

```bash
# Check image size
docker images flask-api
```

Expected output:

```
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
flask-api    1.0.1     b2c3d4e5f6g7   2 minutes ago    155MB
flask-api    1.0.0     a1b2c3d4e5f6   5 minutes ago    155MB
```

### Multi-Stage Build Example

```bash
# Create a Go application with multi-stage build
mkdir ~/go-app && cd ~/go-app

cat > main.go <<'EOF'
package main

import (
    "fmt"
    "net/http"
    "os"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        hostname, _ := os.Hostname()
        fmt.Fprintf(w, `{"host":"%s","status":"running"}`, hostname)
    })
    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
EOF

cat > go.mod <<'EOF'
module go-app
go 1.22
EOF

cat > Dockerfile <<'EOF'
# Stage 1: Build the Go binary
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod .
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# Stage 2: Minimal production image
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/server /usr/local/bin/server
EXPOSE 8080
CMD ["server"]
EOF

# Build
docker build -t go-api:1.0.0 .

# Compare sizes
docker images | head -5
```

Expected output:

```
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
go-api       1.0.0     c3d4e5f6g7h8   10 seconds ago   12.3MB
golang       1.22      x9y0z1a2b3c4   1 week ago       815MB
```

The multi-stage build produced a 12 MB image instead of 815 MB.

### Tagging Strategy

```bash
# Tag an image with multiple tags
docker tag flask-api:1.0.0 myregistry.com/flask-api:1.0.0
docker tag flask-api:1.0.0 myregistry.com/flask-api:latest

# Tag with Git SHA for traceability
GIT_SHA=$(git rev-parse --short HEAD)
docker tag flask-api:1.0.0 myregistry.com/flask-api:${GIT_SHA}

# List all tags for an image
docker images myregistry.com/flask-api
```

---

## Exercises

### Exercise 1: Build a Python Application Image

Create a Dockerfile for a Python application that: uses `python:3.12-slim` as base, sets a working directory, installs dependencies from `requirements.txt` (leveraging caching), copies the application code, and runs with gunicorn. Build and run it, then verify the application responds.

### Exercise 2: Optimize Layer Caching

Take the Dockerfile from Exercise 1 and modify the application code without changing dependencies. Rebuild and observe which layers are cached. Then modify `requirements.txt` and rebuild again. Document how many layers were rebuilt in each case and why.

### Exercise 3: Multi-Stage Build

Create a multi-stage Dockerfile for a Node.js application: the first stage installs dependencies and builds the app (`npm ci && npm run build`), the second stage copies only the built artifacts into a minimal image. Compare the final image size with a single-stage build.

### Exercise 4: Image Inspection

Build an image and use `docker history`, `docker inspect`, and `docker image ls --filter` to investigate it. Document: how many layers it has, which layer is the largest, what the total image size is, and what environment variables are set.

### Exercise 5: .dockerignore Effectiveness

Create a project with a large `.git` directory, `node_modules`, and test files. Build an image without a `.dockerignore` and note the build time and image size. Add a comprehensive `.dockerignore`, rebuild, and compare. Calculate the difference.

---

## Knowledge Check

**Q1: Why does the order of instructions in a Dockerfile matter for build performance?**

<details>
<summary>Answer</summary>

Docker builds layers sequentially and caches each one. When a layer changes, all subsequent layers must be rebuilt (the cache is invalidated from that point onward). By placing instructions that change infrequently (installing system packages, copying dependency files, installing dependencies) before instructions that change frequently (copying application code), you maximize cache utilization. A change to application code only rebuilds the last layer instead of the entire image.

</details>

**Q2: What is the difference between COPY and ADD, and which should you prefer?**

<details>
<summary>Answer</summary>

`COPY` simply copies files and directories from the build context into the image. `ADD` does everything `COPY` does, plus it can: (1) extract compressed archives (tar, gzip, etc.) automatically, and (2) fetch files from URLs.

Prefer `COPY` in almost all cases because it is explicit and predictable. `ADD`'s auto-extraction behavior can be surprising (you might not want a tar file extracted), and fetching URLs in a Dockerfile is better handled with `RUN curl` or `RUN wget` where you can verify checksums. The Docker best practices documentation recommends `COPY` over `ADD` unless you specifically need auto-extraction.

</details>

**Q3: How do multi-stage builds reduce image size, and why does image size matter?**

<details>
<summary>Answer</summary>

Multi-stage builds use separate `FROM` statements for build and runtime stages. The build stage contains compilers, build tools, and source code. The runtime stage contains only the compiled artifact and minimal runtime dependencies, copied from the build stage with `COPY --from=builder`.

Image size matters because: (1) smaller images pull faster, reducing deployment time, (2) smaller images have fewer packages, reducing the attack surface for security vulnerabilities, (3) smaller images use less storage in registries and on nodes, reducing costs, and (4) in Kubernetes, smaller images mean faster pod startup during autoscaling events.

</details>

**Q4: What is the purpose of .dockerignore and what should it always exclude?**

<details>
<summary>Answer</summary>

`.dockerignore` excludes files from the Docker build context -- the set of files sent to the Docker daemon when you run `docker build`. It should always exclude: (1) `.git` directory (can be very large and contains repository history), (2) `node_modules` or virtual environments (dependencies should be installed fresh in the image), (3) test files and documentation (not needed at runtime), (4) IDE and OS files (`.vscode`, `.DS_Store`), (5) secrets and credentials (`.env`, `*.pem`, `*.key` -- these must NEVER be in an image), and (6) Docker-related files (`Dockerfile`, `docker-compose.yml`). A good `.dockerignore` speeds up builds and prevents sensitive data from leaking into images.

</details>

**Q5: Explain the difference between CMD and ENTRYPOINT with a practical example.**

<details>
<summary>Answer</summary>

`CMD` provides the default command that can be completely overridden at runtime. `ENTRYPOINT` defines the main executable, and `CMD` provides default arguments that can be overridden.

Practical example for a database migration tool:

```dockerfile
ENTRYPOINT ["python", "migrate.py"]
CMD ["--target", "latest"]
```

- `docker run migrator` runs: `python migrate.py --target latest`
- `docker run migrator --target v5` runs: `python migrate.py --target v5`
- The tool (`python migrate.py`) is always the entrypoint; only the arguments change

If you used only `CMD ["python", "migrate.py", "--target", "latest"]`, then `docker run migrator bash` would run `bash` instead of the migration tool, which is probably not what you want.

</details>
