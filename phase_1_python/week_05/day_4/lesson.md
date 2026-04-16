# Week 5, Day 4: Error Handling

## What You'll Learn
- How to use `try`, `except`, `else`, and `finally`
- Catching specific exception types
- Raising your own exceptions with `raise`
- Creating custom exception classes
- Error handling patterns for DevOps scripts

---

## Why Error Handling Matters in DevOps

In DevOps, things go wrong constantly:
- A server is unreachable
- A config file is missing or corrupted
- A disk is full and you cannot write
- A network request times out
- A service returns unexpected data

**Your scripts must handle these failures gracefully** instead of crashing. Good error handling means the difference between a script that fails silently at 3 AM and one that logs the problem, retries, and alerts your team.

---

## The Basics: `try` and `except`

```python
try:
    # Code that might fail
    file = open("config.json", "r")
    data = file.read()
    file.close()
except:
    # Code that runs if an error occurs
    print("Something went wrong!")
```

**Warning:** A bare `except:` catches ALL exceptions, including keyboard interrupts. This is bad practice. Always catch specific exceptions.

---

## Catching Specific Exceptions

```python
try:
    with open("config.json", "r") as f:
        data = f.read()
except FileNotFoundError:
    print("Error: config.json not found!")
except PermissionError:
    print("Error: No permission to read config.json!")
```

### Common Exception Types

| Exception | When It Happens |
|-----------|----------------|
| `FileNotFoundError` | File does not exist |
| `PermissionError` | No permission to access file |
| `IsADirectoryError` | Tried to open a directory as a file |
| `json.JSONDecodeError` | Invalid JSON data |
| `KeyError` | Dictionary key not found |
| `ValueError` | Wrong type of value |
| `TypeError` | Wrong type for an operation |
| `IndexError` | List index out of range |
| `ZeroDivisionError` | Division by zero |
| `ConnectionError` | Network connection failed |
| `TimeoutError` | Operation timed out |
| `OSError` | Operating system error (general) |

---

## Getting Error Details

Use `as` to capture the exception object:

```python
try:
    with open("missing_file.txt", "r") as f:
        data = f.read()
except FileNotFoundError as e:
    print(f"Error: {e}")
    # Output: Error: [Errno 2] No such file or directory: 'missing_file.txt'
```

---

## Multiple `except` Blocks

Handle different errors differently:

```python
import json

def load_config(filename):
    try:
        with open(filename, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Config file '{filename}' has invalid JSON: {e}")
        return None
    except PermissionError:
        print(f"No permission to read '{filename}'.")
        return None
```

### Catching Multiple Exceptions Together

```python
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except (FileNotFoundError, PermissionError) as e:
    print(f"Cannot access config file: {e}")
except json.JSONDecodeError as e:
    print(f"Invalid config file: {e}")
```

---

## The `else` Block

Code in `else` runs only if no exception occurred:

```python
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("Config not found, using defaults.")
    config = {"debug": False, "port": 8080}
else:
    # This runs ONLY if no exception happened
    print(f"Config loaded successfully: {config['app_name']}")
```

---

## The `finally` Block

Code in `finally` runs no matter what -- even if an exception occurred:

```python
connection = None
try:
    connection = connect_to_database()
    data = connection.query("SELECT * FROM servers")
except ConnectionError:
    print("Failed to connect to database!")
finally:
    # This ALWAYS runs - perfect for cleanup
    if connection:
        connection.close()
        print("Connection closed.")
```

---

## The Complete Structure

```python
try:
    # Attempt the operation
    result = risky_operation()
except SpecificError as e:
    # Handle the specific error
    print(f"Known error: {e}")
except Exception as e:
    # Handle any other unexpected error
    print(f"Unexpected error: {e}")
else:
    # Runs only if NO exception occurred
    print(f"Success: {result}")
finally:
    # ALWAYS runs (cleanup code goes here)
    print("Operation complete.")
```

---

## Raising Exceptions with `raise`

You can raise your own exceptions when something is wrong:

```python
def deploy_to_server(server, version):
    if not server:
        raise ValueError("Server name cannot be empty")
    if not version:
        raise ValueError("Version cannot be empty")

    print(f"Deploying version {version} to {server}...")

# This will raise ValueError
try:
    deploy_to_server("", "1.0.0")
except ValueError as e:
    print(f"Deployment error: {e}")
```

---

## Custom Exceptions

Create your own exception types for clearer error handling:

```python
class ConfigError(Exception):
    """Raised when there is a configuration problem."""
    pass

class ServerUnreachableError(Exception):
    """Raised when a server cannot be reached."""
    pass

class DeploymentError(Exception):
    """Raised when a deployment fails."""
    pass

def validate_config(config):
    required_keys = ["app_name", "version", "servers"]
    for key in required_keys:
        if key not in config:
            raise ConfigError(f"Missing required config key: '{key}'")

    if not config["servers"]:
        raise ConfigError("Server list cannot be empty")

    return True

# Usage
try:
    config = {"app_name": "myapp", "version": "1.0"}
    validate_config(config)
except ConfigError as e:
    print(f"Configuration problem: {e}")
```

---

## Practical DevOps Examples

### Example 1: Safe File Reader

```python
import json

def safe_load_json(filepath, default=None):
    """Load a JSON file safely, returning default on any error."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, using defaults")
        return default
    except json.JSONDecodeError as e:
        print(f"Warning: {filepath} has invalid JSON: {e}")
        return default

# Usage
config = safe_load_json("config.json", default={"debug": False})
```

### Example 2: Retry Logic

```python
import time

def deploy_with_retry(server, max_retries=3):
    """Try to deploy, retrying on failure."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}: Deploying to {server}...")
            # Simulate deployment
            connect_and_deploy(server)
            print(f"Successfully deployed to {server}")
            return True
        except ConnectionError as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait = attempt * 2  # Exponential backoff
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)

    print(f"FAILED: Could not deploy to {server} after {max_retries} attempts")
    return False
```

### Example 3: Config Validator

```python
class ConfigValidationError(Exception):
    pass

def validate_server_config(config):
    """Validate a server configuration dictionary."""
    errors = []

    if "hostname" not in config:
        errors.append("Missing 'hostname'")
    elif not isinstance(config["hostname"], str):
        errors.append("'hostname' must be a string")

    if "port" not in config:
        errors.append("Missing 'port'")
    elif not isinstance(config["port"], int):
        errors.append("'port' must be an integer")
    elif not (1 <= config["port"] <= 65535):
        errors.append("'port' must be between 1 and 65535")

    if "role" not in config:
        errors.append("Missing 'role'")
    elif config["role"] not in ("web", "database", "cache"):
        errors.append(f"Invalid role: '{config['role']}'")

    if errors:
        raise ConfigValidationError(
            f"Config validation failed: {'; '.join(errors)}"
        )

    return True
```

---

## DevOps Connection

Error handling is critical for:
- **Automated deployments** - Handle failures gracefully, roll back if needed
- **Monitoring scripts** - Continue checking other servers even if one is down
- **Configuration management** - Validate configs before applying them
- **Data processing** - Handle corrupt or missing files without crashing
- **CI/CD pipelines** - Provide clear error messages when builds fail

---

## Key Takeaways

1. Always catch **specific** exceptions, not bare `except:`
2. Use `as e` to get error details for logging
3. `else` runs when no error occurred; `finally` always runs
4. `raise` lets you signal errors in your own functions
5. Custom exceptions make error handling more readable
6. Never silence errors without logging them -- use `print()` or the `logging` module
