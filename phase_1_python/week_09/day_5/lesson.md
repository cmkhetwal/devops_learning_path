# Week 9, Day 5: Container Monitoring with Python

## What You'll Learn
- Reading container stats (CPU, memory, network)
- Fetching container logs
- Implementing health checks
- Building a monitoring dashboard in the terminal
- Setting up alerts based on resource thresholds

## Why Monitor Containers?

Containers are ephemeral -- they start, run, and die. Monitoring tells you:
- Is the container healthy?
- How much CPU/memory is it using?
- Are there errors in the logs?
- Do we need to scale up or down?

## Container Stats

```python
import docker

client = docker.from_env()
container = client.containers.get("my-web-server")

# Get a single stats snapshot (stream=False)
stats = container.stats(stream=False)

# CPU usage calculation
cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
            stats["precpu_stats"]["cpu_usage"]["total_usage"]
system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
               stats["precpu_stats"]["system_cpu_usage"]
cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0

# Memory usage
mem_usage = stats["memory_stats"]["usage"]
mem_limit = stats["memory_stats"]["limit"]
mem_percent = (mem_usage / mem_limit) * 100.0

print(f"CPU:    {cpu_percent:.1f}%")
print(f"Memory: {mem_usage / (1024**2):.1f} MB / {mem_limit / (1024**2):.0f} MB ({mem_percent:.1f}%)")
```

## Container Logs

```python
# Get all logs
logs = container.logs()
print(logs.decode())

# Get last 50 lines
logs = container.logs(tail=50)

# Get logs since a timestamp
from datetime import datetime, timedelta
since = datetime.utcnow() - timedelta(hours=1)
logs = container.logs(since=since)

# Stream logs in real-time
for line in container.logs(stream=True, follow=True):
    print(line.decode(), end="")
```

## Health Checks

```python
def check_container_health(container):
    """Check the health of a container."""
    container.reload()  # refresh state from daemon

    health = {
        "name": container.name,
        "status": container.status,
        "running": container.status == "running",
    }

    # Check if health check is configured
    state = container.attrs.get("State", {})
    if "Health" in state:
        health["health_status"] = state["Health"]["Status"]
        health["failing_streak"] = state["Health"].get("FailingStreak", 0)
    else:
        health["health_status"] = "no healthcheck"

    return health
```

## Simulating Container Stats

```python
import random
import time

class MockContainerStats:
    """Simulates container stats for learning."""

    def __init__(self, name, base_cpu=15.0, base_mem_mb=256):
        self.name = name
        self.base_cpu = base_cpu
        self.base_mem_mb = base_mem_mb

    def get_stats(self):
        """Return simulated stats with some variation."""
        cpu = max(0, self.base_cpu + random.uniform(-5, 10))
        mem = max(10, self.base_mem_mb + random.uniform(-50, 50))
        net_rx = random.randint(1000, 50000)
        net_tx = random.randint(500, 25000)

        return {
            "name": self.name,
            "cpu_percent": round(cpu, 1),
            "memory_mb": round(mem, 1),
            "memory_limit_mb": 512,
            "memory_percent": round((mem / 512) * 100, 1),
            "network_rx_bytes": net_rx,
            "network_tx_bytes": net_tx,
        }

    def get_logs(self, lines=10):
        """Return simulated log lines."""
        log_templates = [
            "INFO: Request handled in {ms}ms",
            "INFO: Connection from {ip}",
            "WARNING: High latency detected: {ms}ms",
            "INFO: Health check passed",
            "ERROR: Connection timeout after 30s",
            "INFO: Cache hit ratio: {ratio}%",
        ]
        logs = []
        for _ in range(lines):
            template = random.choice(log_templates)
            line = template.format(
                ms=random.randint(1, 500),
                ip=f"192.168.1.{random.randint(1, 254)}",
                ratio=random.randint(60, 99),
            )
            logs.append(line)
        return logs
```

## Building a Monitor

```python
def monitor_containers(stats_list):
    """Print a monitoring dashboard."""
    print(f"\n{'NAME':20s} {'CPU':>8s} {'MEM':>10s} {'MEM%':>6s} {'NET RX':>10s} {'NET TX':>10s}")
    print("-" * 70)

    alerts = []
    for s in stats_list:
        stats = s.get_stats()
        print(f"{stats['name']:20s} "
              f"{stats['cpu_percent']:>7.1f}% "
              f"{stats['memory_mb']:>7.1f} MB "
              f"{stats['memory_percent']:>5.1f}% "
              f"{stats['network_rx_bytes']:>8d} B "
              f"{stats['network_tx_bytes']:>8d} B")

        if stats["cpu_percent"] > 80:
            alerts.append(f"HIGH CPU: {stats['name']} at {stats['cpu_percent']}%")
        if stats["memory_percent"] > 80:
            alerts.append(f"HIGH MEM: {stats['name']} at {stats['memory_percent']}%")

    if alerts:
        print("\nALERTS:")
        for alert in alerts:
            print(f"  ! {alert}")
```

## DevOps Connection
- **Observability**: Container metrics feed into Prometheus, Grafana, Datadog
- **Auto-scaling**: Scale container count based on CPU/memory thresholds
- **Incident response**: Automated alerts when containers are unhealthy
- **Log aggregation**: Collect logs from all containers into ELK/Splunk
- **Capacity planning**: Track resource usage trends over time

## Key Takeaways
1. `container.stats(stream=False)` gives a point-in-time resource snapshot
2. `container.logs()` retrieves stdout/stderr from the container
3. Health checks reveal whether the application inside is actually working
4. Set thresholds and alerts for CPU, memory, and error rates
5. Real monitoring systems poll stats continuously and store time-series data
