# Week 5, Day 5: Logging

## What You'll Learn
- The Python `logging` module and why it is better than `print()`
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Formatting log messages
- Writing logs to files with FileHandler
- Log rotation to manage file sizes

---

## Why Logging Matters in DevOps

In production, `print()` is not enough:
- Print statements go to the console and are lost when the terminal closes
- You cannot filter messages by severity
- You cannot send different messages to different destinations
- There are no timestamps or source information

The `logging` module solves all of these problems. It is the standard way to record what your scripts and applications do.

---

## Getting Started with logging

```python
import logging

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)

# Log messages at different levels
logging.debug("Checking server connectivity...")
logging.info("Connected to web-01 successfully")
logging.warning("Disk usage at 85% on db-01")
logging.error("Failed to connect to web-03")
logging.critical("Database server db-02 is DOWN!")
```

Output:
```
DEBUG:root:Checking server connectivity...
INFO:root:Connected to web-01 successfully
WARNING:root:Disk usage at 85% on db-01
ERROR:root:Failed to connect to web-03
CRITICAL:root:Database server db-02 is DOWN!
```

---

## Log Levels

Each level has a numeric value. Setting a level filters out everything below it.

| Level | Value | When to Use |
|-------|-------|-------------|
| `DEBUG` | 10 | Detailed info for diagnosing problems |
| `INFO` | 20 | Confirmation that things work as expected |
| `WARNING` | 30 | Something unexpected but not broken |
| `ERROR` | 40 | Something failed, but the program continues |
| `CRITICAL` | 50 | Serious failure, program may not continue |

```python
import logging

# Only show WARNING and above
logging.basicConfig(level=logging.WARNING)

logging.debug("This will NOT show")      # Filtered out
logging.info("This will NOT show")       # Filtered out
logging.warning("This WILL show")        # Shows
logging.error("This WILL show")          # Shows
logging.critical("This WILL show")       # Shows
```

---

## Formatting Log Messages

The `format` parameter controls what information appears in each log line.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Deployment started")
# Output: 2024-01-15 08:30:00,123 - INFO - Deployment started
```

### Common Format Fields

| Field | Description | Example |
|-------|-------------|---------|
| `%(asctime)s` | Timestamp | 2024-01-15 08:30:00,123 |
| `%(levelname)s` | Level name | INFO, ERROR, etc. |
| `%(message)s` | The log message | Your text |
| `%(name)s` | Logger name | root |
| `%(filename)s` | Source file | deploy.py |
| `%(lineno)d` | Line number | 42 |
| `%(funcName)s` | Function name | deploy_app |

### DevOps-Friendly Format

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("Server check started")
# Output: 2024-01-15 08:30:00 [INFO    ] Server check started

logging.error("Connection failed")
# Output: 2024-01-15 08:30:01 [ERROR   ] Connection failed
```

The `%-8s` pads the level name to 8 characters, making the output aligned.

---

## Writing Logs to a File

### Using basicConfig

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="deploy.log",
    filemode="a"  # "a" = append (default), "w" = overwrite
)

logging.info("Deployment started")
logging.info("Downloading package v2.1.0")
logging.warning("Slow network detected")
logging.info("Deployment complete")
```

This writes all messages to `deploy.log` instead of the console.

### Logging to Both Console AND File

```python
import logging

# Create a logger
logger = logging.getLogger("deploy")
logger.setLevel(logging.DEBUG)

# Console handler - shows INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_format)

# File handler - records everything (DEBUG and above)
file_handler = logging.FileHandler("deploy.log")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(file_format)

# Add both handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Now use the logger
logger.debug("Debug details - only in file")
logger.info("Deployment started - console and file")
logger.error("Connection failed - console and file")
```

---

## Log Rotation

Log files can grow very large. Log rotation automatically creates new files when the current one gets too big.

### RotatingFileHandler (by size)

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Rotate when file reaches 1MB, keep 5 backup files
handler = RotatingFileHandler(
    "app.log",
    maxBytes=1_000_000,    # 1 MB
    backupCount=5           # Keep app.log.1 through app.log.5
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))

logger.addHandler(handler)
```

This creates files: `app.log`, `app.log.1`, `app.log.2`, etc.

### TimedRotatingFileHandler (by time)

```python
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Rotate every day at midnight, keep 7 days
handler = TimedRotatingFileHandler(
    "app.log",
    when="midnight",
    interval=1,
    backupCount=7
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))

logger.addHandler(handler)
```

---

## Practical Examples

### Example 1: Deployment Script with Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def deploy(server, version):
    logging.info(f"Starting deployment of v{version} to {server}")

    logging.info(f"Downloading package v{version}...")
    # download_package(version)
    logging.info("Download complete")

    logging.info(f"Stopping service on {server}...")
    # stop_service(server)
    logging.info("Service stopped")

    logging.info(f"Installing v{version}...")
    # install_package(server, version)
    logging.info("Installation complete")

    logging.info(f"Starting service on {server}...")
    # start_service(server)
    logging.info("Service started")

    logging.info(f"Deployment of v{version} to {server} COMPLETE")

servers = ["web-01", "web-02", "web-03"]
for server in servers:
    deploy(server, "2.1.0")
```

### Example 2: Health Checker

```python
import logging

logger = logging.getLogger("healthcheck")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("health.log")
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))
logger.addHandler(handler)

def check_server(hostname, cpu, memory, disk):
    logger.info(f"Checking {hostname}...")

    if cpu > 90:
        logger.critical(f"{hostname}: CPU at {cpu}% - CRITICAL")
    elif cpu > 70:
        logger.warning(f"{hostname}: CPU at {cpu}% - High")
    else:
        logger.debug(f"{hostname}: CPU at {cpu}% - OK")

    if memory > 90:
        logger.critical(f"{hostname}: Memory at {memory}% - CRITICAL")
    elif memory > 70:
        logger.warning(f"{hostname}: Memory at {memory}% - High")
    else:
        logger.debug(f"{hostname}: Memory at {memory}% - OK")

    if disk > 90:
        logger.error(f"{hostname}: Disk at {disk}% - FULL")
    elif disk > 80:
        logger.warning(f"{hostname}: Disk at {disk}% - Getting full")
    else:
        logger.debug(f"{hostname}: Disk at {disk}% - OK")
```

---

## DevOps Connection

Logging is fundamental to:
- **Deployment automation** - Record every step for troubleshooting
- **Monitoring and alerting** - Log problems for alert systems to detect
- **Audit trails** - Track who did what and when
- **Debugging in production** - Use DEBUG level to troubleshoot live issues
- **Compliance** - Many regulations require detailed operational logs

---

## Key Takeaways

1. Use `logging` instead of `print()` for anything beyond quick debugging
2. Choose the right level: DEBUG for details, INFO for progress, WARNING for concerns, ERROR for failures, CRITICAL for disasters
3. Include timestamps and level names in your format
4. Use FileHandler to write logs to files
5. Use RotatingFileHandler to prevent log files from growing forever
6. You can log to multiple destinations (console + file) at the same time
