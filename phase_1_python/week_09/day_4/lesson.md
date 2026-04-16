# Week 9, Day 4: Docker Compose + Python

## What You'll Learn
- Reading docker-compose.yml files with PyYAML
- Writing compose files programmatically
- Generating multi-service configurations from Python dicts
- Validating compose file structure
- Templating compose files for different environments

## Why Generate Compose Files with Python?

In real DevOps work you often need to:
- Generate different compose files for dev, staging, production
- Create compose files from inventory databases
- Validate compose files before deployment
- Merge multiple service definitions

Python + PyYAML makes this easy and repeatable.

## PyYAML Basics

```bash
pip install pyyaml
```

```python
import yaml

# Read a YAML file
with open("docker-compose.yml") as f:
    config = yaml.safe_load(f)

# Write a YAML file
with open("docker-compose.yml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

## Docker Compose File Structure

```yaml
version: "3.8"
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - api
  api:
    image: python:3.11
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgres://db:5432/mydb
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

## Building Compose Files in Python

```python
import yaml

def create_compose_config(services):
    """Generate a docker-compose config dict."""
    compose = {
        "version": "3.8",
        "services": {},
    }

    for svc in services:
        service_def = {"image": svc["image"]}

        if "ports" in svc:
            service_def["ports"] = svc["ports"]
        if "environment" in svc:
            service_def["environment"] = svc["environment"]
        if "volumes" in svc:
            service_def["volumes"] = svc["volumes"]
        if "depends_on" in svc:
            service_def["depends_on"] = svc["depends_on"]

        compose["services"][svc["name"]] = service_def

    return compose

# Example usage
services = [
    {
        "name": "web",
        "image": "nginx:latest",
        "ports": ["80:80"],
    },
    {
        "name": "api",
        "image": "python:3.11-slim",
        "ports": ["5000:5000"],
        "environment": {"FLASK_ENV": "production"},
        "depends_on": ["db"],
    },
    {
        "name": "db",
        "image": "postgres:15",
        "environment": {
            "POSTGRES_DB": "app",
            "POSTGRES_PASSWORD": "secret",
        },
    },
]

config = create_compose_config(services)

# Write to file
with open("docker-compose.yml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

## Environment-Specific Configs

```python
def compose_for_env(base_services, environment="dev"):
    """Generate environment-specific compose configs."""
    config = create_compose_config(base_services)

    if environment == "production":
        # Add restart policy and resource limits
        for name, svc in config["services"].items():
            svc["restart"] = "always"
            svc["deploy"] = {
                "resources": {
                    "limits": {"cpus": "0.5", "memory": "512M"}
                }
            }
    elif environment == "dev":
        # Add debug settings
        for name, svc in config["services"].items():
            svc["restart"] = "no"

    return config
```

## Reading and Modifying Compose Files

```python
import yaml

def add_service_to_compose(filepath, service_name, service_config):
    """Add a service to an existing docker-compose file."""
    with open(filepath) as f:
        compose = yaml.safe_load(f)

    compose["services"][service_name] = service_config

    with open(filepath, "w") as f:
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

    print(f"Added service '{service_name}' to {filepath}")
```

## Validating Compose Configs

```python
def validate_compose(config):
    """Basic validation of a compose config dict."""
    errors = []

    if "version" not in config:
        errors.append("Missing 'version' key")
    if "services" not in config:
        errors.append("Missing 'services' key")
        return errors  # Can't validate further

    for name, svc in config["services"].items():
        if "image" not in svc and "build" not in svc:
            errors.append(f"Service '{name}': needs 'image' or 'build'")
        if "depends_on" in svc:
            for dep in svc["depends_on"]:
                if dep not in config["services"]:
                    errors.append(f"Service '{name}': depends on '{dep}' which is not defined")

    return errors  # Empty list = valid
```

## DevOps Connection
- **Infrastructure as Code**: Compose files are IaC -- generating them from Python is powerful
- **Multi-environment**: Generate dev, staging, prod configs from one source
- **Service catalogs**: Build compose files from a database of available services
- **CI/CD**: Auto-generate test environments with the right service mix
- **GitOps**: Validate compose files in a pre-commit hook

## Key Takeaways
1. PyYAML's `safe_load()` reads YAML into Python dicts/lists
2. `yaml.dump()` writes Python dicts back to YAML format
3. Docker Compose files are just nested dictionaries -- perfect for Python
4. Validate configs before writing to catch errors early
5. Use Python to template compose files for different environments
