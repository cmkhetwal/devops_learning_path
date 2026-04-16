# Week 8, Day 5: Unit Testing

## What You'll Learn
- Why testing matters for DevOps
- `pytest` basics: test functions, assertions
- Writing good test cases
- Fixtures for test setup/teardown
- Running tests and reading output
- Testing the Server class from earlier lessons

## Why Test?

In DevOps, untested code can break production. Testing gives you:
- **Confidence**: Know your code works before deploying
- **Safety**: Catch bugs before they reach production
- **Documentation**: Tests show how code is supposed to work
- **Refactoring**: Change code safely with tests as a safety net

## Installing pytest

```bash
pip install pytest
```

## Writing Your First Test

```python
# test_example.py

def add(a, b):
    return a + b

# Test functions must start with "test_"
def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_add_zeros():
    assert add(0, 0) == 0
```

```bash
# Run tests:
pytest test_example.py

# Run with verbose output:
pytest -v test_example.py

# Run a specific test:
pytest test_example.py::test_add
```

## Assert Statements

```python
# Basic assertions
assert value == expected         # Equal
assert value != other            # Not equal
assert value > 0                 # Greater than
assert value in collection       # In container
assert isinstance(obj, MyClass)  # Type check
assert value is None             # Is None
assert value is not None         # Is not None
assert len(items) == 5           # Length check

# With error messages (shown on failure)
assert result == 42, f"Expected 42 but got {result}"

# Boolean assertions
assert is_valid                  # True
assert not is_invalid            # False

# Exception testing
import pytest

def test_raises_error():
    with pytest.raises(ValueError):
        int("not_a_number")

def test_raises_with_message():
    with pytest.raises(ValueError, match="invalid literal"):
        int("not_a_number")
```

## Testing Classes

```python
# server.py
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

    def start(self):
        self.status = "running"
        return f"{self.name} started"

    def stop(self):
        self.status = "stopped"
        return f"{self.name} stopped"

# test_server.py
from server import Server

def test_server_creation():
    s = Server("web-01", "10.0.1.10")
    assert s.name == "web-01"
    assert s.ip_address == "10.0.1.10"
    assert s.status == "stopped"

def test_server_start():
    s = Server("web-01", "10.0.1.10")
    result = s.start()
    assert s.status == "running"
    assert "started" in result

def test_server_stop():
    s = Server("web-01", "10.0.1.10")
    s.start()
    result = s.stop()
    assert s.status == "stopped"
    assert "stopped" in result
```

## Fixtures

Fixtures provide reusable test setup:

```python
import pytest

@pytest.fixture
def server():
    """Create a test server."""
    return Server("web-01", "10.0.1.10")

@pytest.fixture
def running_server():
    """Create a running test server."""
    s = Server("web-01", "10.0.1.10")
    s.start()
    return s

# Use fixtures as function parameters:
def test_server_name(server):
    assert server.name == "web-01"

def test_running_status(running_server):
    assert running_server.status == "running"

def test_stop_running(running_server):
    running_server.stop()
    assert running_server.status == "stopped"
```

## Parametrize (Multiple Test Cases)

```python
import pytest

@pytest.mark.parametrize("ip,expected", [
    ("10.0.1.10", True),
    ("192.168.1.1", True),
    ("255.255.255.255", True),
    ("999.0.1.1", False),
    ("10.0.1", False),
    ("abc.def.ghi.jkl", False),
    ("", False),
])
def test_validate_ip(ip, expected):
    assert validate_ip(ip) == expected
```

## Test Organization

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_server.py        # Server tests
├── test_deployment.py    # Deployment tests
└── test_utils.py         # Utility function tests
```

```python
# conftest.py - shared fixtures available to all test files
import pytest

@pytest.fixture
def web_server():
    return WebServer("web-01", "10.0.1.10")

@pytest.fixture
def db_server():
    return DatabaseServer("db-01", "10.0.2.10")
```

## Testing Patterns for DevOps

```python
# Test that configurations are valid
def test_config_has_required_keys():
    config = load_config("test_config.yaml")
    required_keys = ["server", "port", "database"]
    for key in required_keys:
        assert key in config, f"Missing required key: {key}"

# Test error handling
def test_connection_failure():
    with pytest.raises(ConnectionError):
        connect_to_server("nonexistent.example.com")

# Test that output format is correct
def test_status_output_format():
    result = get_server_status("web-01")
    assert isinstance(result, dict)
    assert "name" in result
    assert "status" in result
    assert result["status"] in ["running", "stopped", "error"]
```

## Running Tests

```bash
# Run all tests in current directory
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run specific file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::test_server_start

# Run tests matching a keyword
pytest -k "server"

# Show test coverage (requires pytest-cov)
pip install pytest-cov
pytest --cov=my_package tests/
```

## DevOps Connection

Testing is non-negotiable in DevOps:
- **CI/CD Pipelines**: Tests run automatically on every commit
- **Infrastructure as Code**: Test your Terraform/Ansible before applying
- **Deployment Safety**: Tests prevent breaking changes
- **Monitoring Scripts**: Ensure your monitors actually detect failures
- **Configuration**: Validate configs before deploying them

Most CI/CD systems (GitHub Actions, Jenkins, GitLab CI) run pytest
as part of the pipeline.
