# Week 8, Day 4: Project Structure

## What You'll Learn
- How to organize a Python project properly
- Packages and `__init__.py`
- `setup.py` / `pyproject.toml` basics
- `requirements.txt` for dependencies
- Virtual environments (`venv`)
- The standard project layout

## Why Project Structure Matters

As your DevOps scripts grow from single files to full tools, proper
structure makes them maintainable, shareable, and professional.

## The Standard Project Layout

```
my-devops-tool/
├── my_devops_tool/          # Main package (use underscores)
│   ├── __init__.py          # Makes it a package
│   ├── core.py              # Core functionality
│   ├── servers.py           # Server-related code
│   ├── monitoring.py        # Monitoring code
│   └── utils.py             # Utility functions
├── tests/                   # Test directory
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_servers.py
│   └── test_monitoring.py
├── requirements.txt         # Dependencies
├── setup.py                 # Package configuration
├── README.md                # Documentation
└── .gitignore               # Git ignore rules
```

## Packages and __init__.py

A package is a directory with an `__init__.py` file. This file can be
empty or contain initialization code.

```python
# my_devops_tool/__init__.py
"""My DevOps Tool - Infrastructure automation toolkit."""

__version__ = "1.0.0"

# Optional: import commonly used items for convenience
from .core import DevOpsClient
from .servers import Server, WebServer
```

```python
# my_devops_tool/servers.py
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

    def start(self):
        self.status = "running"
        return f"{self.name} started"

class WebServer(Server):
    def __init__(self, name, ip_address, port=80):
        super().__init__(name, ip_address)
        self.port = port
```

```python
# my_devops_tool/utils.py
def validate_ip(ip_address):
    """Validate an IPv4 address."""
    parts = ip_address.split(".")
    if len(parts) != 4:
        return False
    return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

def format_bytes(num_bytes):
    """Convert bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"
```

## Importing from Packages

```python
# From outside the package:
from my_devops_tool import DevOpsClient           # From __init__.py
from my_devops_tool.servers import Server, WebServer
from my_devops_tool.utils import validate_ip

# Relative imports (inside the package):
# In my_devops_tool/core.py:
from .servers import Server          # . means current package
from .utils import validate_ip
from .monitoring import Monitor
```

## requirements.txt

Lists your project's dependencies:

```
# requirements.txt
requests>=2.28.0
paramiko>=3.0.0
click>=8.0.0
pyyaml>=6.0
```

```bash
# Install all dependencies:
pip install -r requirements.txt

# Generate from current environment:
pip freeze > requirements.txt
```

## Virtual Environments (venv)

Virtual environments isolate project dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Your prompt shows (venv) when active
# (venv) $ python main.py

# Deactivate when done
deactivate
```

## setup.py

Makes your project installable:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-devops-tool",
    version="1.0.0",
    description="Infrastructure automation toolkit",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),          # Auto-find packages
    install_requires=[
        "requests>=2.28.0",
        "paramiko>=3.0.0",
        "click>=8.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "devops-tool=my_devops_tool.cli:main",  # CLI command
        ],
    },
)
```

```bash
# Install your package in development mode:
pip install -e .

# Now you can import it from anywhere:
from my_devops_tool import Server
```

## Modern Alternative: pyproject.toml

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=65.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "my-devops-tool"
version = "1.0.0"
description = "Infrastructure automation toolkit"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
    "paramiko>=3.0.0",
]

[project.scripts]
devops-tool = "my_devops_tool.cli:main"
```

## .gitignore for Python Projects

```
# .gitignore
__pycache__/
*.pyc
*.pyo
venv/
.env
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
```

## Complete Example Project

```
server-manager/
├── server_manager/
│   ├── __init__.py           # Package init
│   ├── models/
│   │   ├── __init__.py
│   │   ├── server.py         # Server, WebServer, DatabaseServer
│   │   └── deployment.py     # Deployment classes
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── health.py         # Health check functions
│   │   └── metrics.py        # Metrics collection
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── network.py        # Network utilities
│   │   └── formatting.py     # Output formatting
│   └── cli.py                # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_monitoring.py
│   └── test_utils.py
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

## DevOps Connection

Proper project structure is critical for DevOps because:
- **Collaboration**: Team members can navigate code easily
- **Testing**: Structured code is easier to test
- **CI/CD**: Standard layout works with CI/CD tools automatically
- **Packaging**: Distributable to other teams or PyPI
- **Maintenance**: Organized code is easier to debug and extend
- **Standards**: Following conventions makes onboarding faster

Every DevOps tool you use (Ansible, Terraform providers, AWS CDK)
follows these same patterns.
