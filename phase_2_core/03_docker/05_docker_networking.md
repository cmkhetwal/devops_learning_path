# Docker Networking

## Why This Matters in DevOps

Containers rarely run in isolation. A typical application involves a web server, an API, a database, a cache, and possibly a message queue -- all running as separate containers that need to communicate. Docker networking is the mechanism that connects these containers while maintaining isolation from services they should not access.

For DevOps engineers, understanding Docker networking is essential for: designing microservice architectures, debugging connectivity issues between containers, securing inter-service communication, and translating local Docker Compose setups into production Kubernetes networking. The concepts here -- network namespaces, DNS-based service discovery, and network isolation -- carry directly into Kubernetes, where they become Services, Pods, and Network Policies.

When a production container cannot reach its database, or when a service is accidentally exposed to the internet, the root cause is almost always a networking misconfiguration. This lesson gives you the mental model and practical skills to prevent and diagnose these issues.

---

## Core Concepts

### Docker Network Drivers

Docker provides several network drivers, each serving a different purpose:

| Driver | Use Case | Isolation | Performance |
|--------|----------|-----------|-------------|
| **bridge** | Default; containers on same host | Moderate | Good |
| **host** | Container uses host's network stack | None | Best |
| **none** | No networking at all | Maximum | N/A |
| **overlay** | Multi-host networking (Swarm) | Moderate | Good |
| **macvlan** | Container gets its own MAC address | Full | Best |

### Bridge Network (Default)

When you run a container without specifying a network, Docker attaches it to the default `bridge` network. Containers on the default bridge can communicate via IP addresses but NOT by container name.

```
Host Machine
┌─────────────────────────────────────────┐
│  docker0 bridge (172.17.0.1)            │
│  ┌──────────┐  ┌──────────┐             │
│  │ Container │  │ Container │            │
│  │ 172.17.0.2│  │ 172.17.0.3│           │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
```

### Custom Bridge Networks

Custom bridge networks are the recommended approach. Unlike the default bridge, custom networks provide:
- **DNS-based service discovery:** Containers can reach each other by name
- **Better isolation:** Only containers on the same network can communicate
- **On-the-fly connection:** Containers can be connected/disconnected without restarting

### Host Network

The container shares the host's network namespace. There is no network isolation -- the container's ports are directly on the host. Use this for performance-sensitive applications or when a container needs full access to the host's network.

### None Network

The container has no network interfaces (except loopback). Use this for containers that process data but should never make network connections, such as batch processing jobs that read from mounted volumes.

### DNS in Docker

On custom networks, Docker runs an embedded DNS server at 127.0.0.11. Containers can resolve other containers by their name or network aliases. This is how microservices find each other without hardcoded IP addresses.

```
Container "api" wants to reach Container "database"
  → DNS query: "database" → 127.0.0.11 → 172.18.0.3
  → Connection established
```

### Port Mapping

Port mapping connects a port on the host to a port inside a container using the `-p` flag.

```
-p HOST_PORT:CONTAINER_PORT
-p 8080:80          # Map host 8080 to container 80
-p 127.0.0.1:8080:80  # Map only on localhost (not externally accessible)
-p 8080-8090:80-90  # Map a range of ports
```

Without port mapping, container ports are only accessible from other containers on the same network, not from the host or external clients.

---

## Step-by-Step Practical

### Exploring the Default Bridge Network

```bash
# List existing networks
docker network ls
```

Expected output:

```
NETWORK ID     NAME      DRIVER    SCOPE
a1b2c3d4e5f6   bridge    bridge    local
e4f5g6h7i8j9   host      host      local
k0l1m2n3o4p5   none      null      local
```

```bash
# Run two containers on the default bridge
docker run -d --name container1 alpine sleep 3600
docker run -d --name container2 alpine sleep 3600

# Get container1's IP address
docker inspect container1 --format '{{.NetworkSettings.IPAddress}}'
```

Expected output:

```
172.17.0.2
```

```bash
# container2 can reach container1 by IP
docker exec container2 ping -c 3 172.17.0.2
```

Expected output:

```
PING 172.17.0.2 (172.17.0.2): 56 data bytes
64 bytes from 172.17.0.2: seq=0 ttl=64 time=0.098 ms
64 bytes from 172.17.0.2: seq=1 ttl=64 time=0.089 ms
64 bytes from 172.17.0.2: seq=2 ttl=64 time=0.081 ms
```

```bash
# But NOT by name on the default bridge
docker exec container2 ping -c 1 container1
```

Expected output:

```
ping: bad address 'container1'
```

```bash
# Clean up
docker rm -f container1 container2
```

### Creating and Using Custom Networks

```bash
# Create a custom bridge network
docker network create app-network
```

Expected output:

```
f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6
```

```bash
# Run containers on the custom network
docker run -d --name api --network app-network alpine sleep 3600
docker run -d --name database --network app-network alpine sleep 3600

# Now DNS-based discovery works!
docker exec api ping -c 3 database
```

Expected output:

```
PING database (172.18.0.3): 56 data bytes
64 bytes from 172.18.0.3: seq=0 ttl=64 time=0.082 ms
64 bytes from 172.18.0.3: seq=1 ttl=64 time=0.075 ms
64 bytes from 172.18.0.3: seq=2 ttl=64 time=0.068 ms
```

### Network Isolation Between Networks

```bash
# Create a second network
docker network create backend-network

# Run a container on the backend network
docker run -d --name cache --network backend-network alpine sleep 3600

# The API container CANNOT reach the cache (different networks)
docker exec api ping -c 1 cache
```

Expected output:

```
ping: bad address 'cache'
```

```bash
# Connect the API container to the backend network too
docker network connect backend-network api

# Now the API can reach both networks
docker exec api ping -c 1 database   # Works (app-network)
docker exec api ping -c 1 cache      # Works (backend-network)

# But database still cannot reach cache (different networks)
docker exec database ping -c 1 cache
```

Expected output:

```
ping: bad address 'cache'
```

This demonstrates network-based isolation: the API can reach both tiers, but the database and cache cannot reach each other.

### Port Mapping in Practice

```bash
# Run Nginx with port mapping
docker run -d --name web -p 8080:80 nginx:1.25

# Accessible from the host
curl http://localhost:8080
```

Expected output:

```html
<!DOCTYPE html>
<html>
<head><title>Welcome to nginx!</title></head>
...
```

```bash
# Bind to localhost only (not accessible from other machines)
docker run -d --name web-local -p 127.0.0.1:8081:80 nginx:1.25

# Verify binding
docker port web-local
```

Expected output:

```
80/tcp -> 127.0.0.1:8081
```

### Realistic Multi-Container Application

```bash
# Create a network for the application
docker network create myapp-network

# Run a PostgreSQL database
docker run -d \
  --name postgres \
  --network myapp-network \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=secretpass \
  -e POSTGRES_DB=appdb \
  postgres:16-alpine

# Run a Redis cache
docker run -d \
  --name redis \
  --network myapp-network \
  redis:7-alpine

# Run the application container that connects to both
docker run -d \
  --name app \
  --network myapp-network \
  -p 8080:8080 \
  -e DATABASE_URL=postgresql://appuser:secretpass@postgres:5432/appdb \
  -e REDIS_URL=redis://redis:6379 \
  python:3.12-slim sleep 3600

# Verify DNS resolution from the app container
docker exec app getent hosts postgres
```

Expected output:

```
172.18.0.2      postgres
```

```bash
docker exec app getent hosts redis
```

Expected output:

```
172.18.0.3      redis
```

### Inspecting Networks

```bash
# Inspect a network to see connected containers
docker network inspect myapp-network
```

Expected output (abbreviated):

```json
[
    {
        "Name": "myapp-network",
        "Driver": "bridge",
        "Containers": {
            "abc123...": {
                "Name": "postgres",
                "IPv4Address": "172.18.0.2/16"
            },
            "def456...": {
                "Name": "redis",
                "IPv4Address": "172.18.0.3/16"
            },
            "ghi789...": {
                "Name": "app",
                "IPv4Address": "172.18.0.4/16"
            }
        }
    }
]
```

### Host Network Mode

```bash
# Run a container using the host's network stack
docker run -d --name host-nginx --network host nginx:1.25

# No port mapping needed -- Nginx binds directly to host port 80
curl http://localhost:80
```

Expected output:

```html
<!DOCTYPE html>
<html>
<head><title>Welcome to nginx!</title></head>
...
```

```bash
# Note: port mapping (-p) is ignored in host network mode
docker rm -f host-nginx
```

### Cleaning Up Networks

```bash
# Remove all containers on the network first
docker rm -f app postgres redis

# Remove the network
docker network rm myapp-network

# Remove all unused networks
docker network prune
```

---

## Exercises

### Exercise 1: Default vs Custom Bridge

Run two containers on the default bridge network and verify they cannot resolve each other by name. Then create a custom network, run two containers on it, and verify DNS resolution works. Document the difference and explain why custom networks are preferred.

### Exercise 2: Multi-Tier Network Isolation

Design a three-tier application (frontend, backend, database) with two networks: `frontend-net` (frontend + backend) and `backend-net` (backend + database). Verify that the frontend can reach the backend, the backend can reach the database, but the frontend cannot directly reach the database.

### Exercise 3: Port Mapping Security

Run a web server and experiment with different port mapping options: `-p 8080:80` (all interfaces), `-p 127.0.0.1:8080:80` (localhost only), and `-p 192.168.1.100:8080:80` (specific interface). Use `docker port` and `ss -tlnp` to verify the bindings. Explain when you would use each option.

### Exercise 4: Full Stack Local Environment

Set up a complete local development environment with Docker networking: a PostgreSQL database, a Redis cache, an API server (use any language), and an Nginx reverse proxy. All services should communicate over a custom network. Only Nginx should have port mapping to the host. Document the network topology.

### Exercise 5: Network Troubleshooting

Intentionally misconfigure a multi-container setup (wrong network name, missing port mapping, typo in hostname). Practice diagnosing each issue using `docker network inspect`, `docker exec ... ping`, `docker exec ... nslookup`, and `docker logs`. Document your troubleshooting process for each scenario.

---

## Knowledge Check

**Q1: Why should you use custom bridge networks instead of the default bridge network?**

<details>
<summary>Answer</summary>

Custom bridge networks provide three critical advantages: (1) **DNS-based service discovery** -- containers can resolve each other by name (e.g., `ping database`), while the default bridge requires IP addresses which change on restart; (2) **better isolation** -- only containers explicitly placed on the same custom network can communicate, while all containers on the default bridge can reach each other; (3) **dynamic connectivity** -- containers can be connected to and disconnected from custom networks without restarting, while the default bridge requires stopping the container. Custom networks are the standard for both development and production Docker environments.

</details>

**Q2: How does Docker DNS work, and why is it important for microservices?**

<details>
<summary>Answer</summary>

On custom bridge networks, Docker runs an embedded DNS server at 127.0.0.11. When a container makes a DNS query for another container's name, the embedded DNS server resolves it to the container's IP address on that network. This is important for microservices because: (1) services can find each other by name rather than hardcoded IPs, (2) containers can be replaced (new IP) without updating configurations in other containers, (3) it mirrors production service discovery patterns (Kubernetes DNS, Consul), and (4) environment variables like `DATABASE_URL=postgresql://dbhost:5432/mydb` work consistently because the hostname resolves dynamically.

</details>

**Q3: When would you use host network mode, and what are the trade-offs?**

<details>
<summary>Answer</summary>

Use host network mode when: (1) you need maximum network performance (eliminates the bridge network overhead), (2) the container needs to see all host network traffic (monitoring/debugging tools), or (3) the application binds to many dynamic ports that are impractical to map.

Trade-offs: (1) no network isolation -- the container shares the host's network stack, (2) port conflicts -- the container's ports compete with host ports, (3) reduced security -- the container has direct access to all host network interfaces, and (4) reduced portability -- the setup depends on the host's network configuration. In production, bridge networks with port mapping are preferred for isolation and security.

</details>

**Q4: How does network isolation enable a secure multi-tier architecture?**

<details>
<summary>Answer</summary>

By creating separate networks for each tier, you enforce the principle of least privilege at the network level:

- Frontend network: contains the reverse proxy and API server
- Backend network: contains the API server and database

The API server is connected to both networks and can communicate with both tiers. The reverse proxy can only reach the API server, not the database. The database can only be reached by the API server, not directly by the reverse proxy or external traffic.

This mirrors production network segmentation where databases are in private subnets inaccessible from the public internet, and only application servers in the middle tier can reach them.

</details>

**Q5: What is the difference between EXPOSE in a Dockerfile and `-p` in `docker run`?**

<details>
<summary>Answer</summary>

`EXPOSE` in a Dockerfile is purely documentation -- it declares which ports the application uses but does not actually publish them. It helps other developers and tools understand the container's interface but has no runtime effect on network accessibility.

`-p` (or `--publish`) in `docker run` actually creates a port mapping between the host and the container, making the container's port accessible from outside. Without `-p`, the port is only accessible from other containers on the same Docker network.

Think of `EXPOSE` as the API documentation and `-p` as the actual firewall rule. You need `-p` for the port to be reachable from the host; `EXPOSE` alone does nothing for connectivity.

</details>
