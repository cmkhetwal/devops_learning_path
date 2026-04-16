# Week 12, Day 4: Capstone Project - Part 2 (File I/O, Error Handling, Logging)

## Today's Goals

Building on Part 1's data models and core classes, today you will add:

1. **File I/O**: Save and load inventory and deployment data to/from JSON
2. **Error Handling**: Robust exception handling throughout the platform
3. **Logging**: Professional logging with configurable levels
4. **Health Checker**: Simulated health checking for servers

## Key Concepts

### JSON Persistence
```python
import json

def save_to_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_from_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
```

### Custom Exceptions
```python
class PlatformError(Exception):
    """Base exception for our platform."""
    pass

class ServerNotFoundError(PlatformError):
    pass

class DuplicateServerError(PlatformError):
    pass
```

### Logging Best Practices
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

## Tips
- Reuse your Day 3 classes (Server, Deployment, HealthCheck)
- Always validate data when loading from files
- Log important operations at appropriate levels
- Handle file-not-found gracefully with defaults
