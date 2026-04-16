"""
Week 9, Day 4: Docker Compose + Python

GENERATING DOCKER COMPOSE FILES PROGRAMMATICALLY
==================================================

In this exercise you will read, write, validate, and generate
docker-compose.yml files using Python and PyYAML (or plain dicts with
yaml-like string output for portability).

NOTE: If PyYAML is not installed, this exercise uses a built-in fallback
that works with plain dictionaries and simple string formatting.

TASKS
-----
1. Build a compose config from a service list
2. Write a compose file to disk
3. Validate a compose config
4. Generate environment-specific compose files
5. Create a multi-tier application compose generator
"""

import os
import json

# Try to import yaml; fall back to json-based approach
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

OUTPUT_DIR = "/home/cmk/python/devops-python-path/week_09/day_4/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def dict_to_yaml_string(data, indent=0):
    """Simple fallback: convert a dict to YAML-like string without PyYAML."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(dict_to_yaml_string(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        first = True
                        for k, v in item.items():
                            if first:
                                lines.append(f"{prefix}  - {k}: {v}")
                                first = False
                            else:
                                lines.append(f"{prefix}    {k}: {v}")
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines)


# ============================================================
# TASK 1: Build a compose config from a service list
# ============================================================
# Write a function called `build_compose_config` that:
#   - Takes one argument: services (a list of dicts)
#   - Each dict has: "name" (str), "image" (str), and optionally
#     "ports" (list of str), "environment" (dict), "volumes" (list),
#     "depends_on" (list of str)
#   - Returns a dictionary structured as:
#     {
#       "version": "3.8",
#       "services": {
#           <name>: {
#               "image": <image>,
#               ... (only include keys that exist in the input)
#           }
#       }
#     }
#   - Prints "Compose config: X services" where X is the number of services

# YOUR CODE HERE


# ============================================================
# TASK 2: Write a compose file to disk
# ============================================================
# Write a function called `write_compose_file` that:
#   - Takes two arguments: config (dict), filepath (str)
#   - If PyYAML is available (HAS_YAML is True):
#       Use yaml.dump(config, f, default_flow_style=False, sort_keys=False)
#   - If PyYAML is not available:
#       Use json.dump(config, f, indent=2)
#   - Prints "Wrote compose file: <filepath>"
#   - Returns the filepath

# YOUR CODE HERE


# ============================================================
# TASK 3: Validate a compose config
# ============================================================
# Write a function called `validate_compose` that:
#   - Takes one argument: config (dict)
#   - Returns a list of error strings (empty list = valid)
#   - Check these rules:
#     1. "version" key must exist -> error: "Missing 'version'"
#     2. "services" key must exist -> error: "Missing 'services'"
#     3. If services is empty dict -> error: "No services defined"
#     4. Each service must have "image" or "build" -> error: "Service '<name>': missing image or build"
#     5. If a service has "depends_on", each dependency must be a defined
#        service name -> error: "Service '<name>': dependency '<dep>' not defined"
#   - Prints "Validation: X errors found" (or "Validation: OK" if 0 errors)

# YOUR CODE HERE


# ============================================================
# TASK 4: Environment-specific compose files
# ============================================================
# Write a function called `compose_for_environment` that:
#   - Takes two arguments: base_config (dict), env (str: "dev", "staging", "prod")
#   - Returns a NEW dict (do not modify the original -- use copy/deepcopy)
#   - Modifications by environment:
#     "dev":
#       - Add "restart": "no" to every service
#     "staging":
#       - Add "restart": "on-failure" to every service
#     "prod":
#       - Add "restart": "always" to every service
#       - Add "deploy": {"resources": {"limits": {"memory": "512M"}}} to every service
#   - Prints "Generated <env> config with X services"

# YOUR CODE HERE


# ============================================================
# TASK 5: Multi-tier app compose generator
# ============================================================
# Write a function called `generate_app_stack` that:
#   - Takes one argument: app_name (str)
#   - Returns a compose config dict for a 3-tier application:
#
#     Service 1: "<app_name>-web"
#       image: "nginx:latest"
#       ports: ["80:80"]
#       depends_on: ["<app_name>-api"]
#
#     Service 2: "<app_name>-api"
#       image: "python:3.11-slim"
#       ports: ["5000:5000"]
#       environment: {"APP_NAME": <app_name>, "DB_HOST": "<app_name>-db"}
#       depends_on: ["<app_name>-db"]
#
#     Service 3: "<app_name>-db"
#       image: "postgres:15"
#       environment: {"POSTGRES_DB": <app_name>, "POSTGRES_PASSWORD": "changeme"}
#       volumes: ["<app_name>_data:/var/lib/postgresql/data"]
#
#   - The config should also have a top-level "volumes" key:
#       {"<app_name>_data": None}   (or {"<app_name>_data": {}} is also fine)
#   - Prints "Generated stack for '<app_name>': 3 services"

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  WEEK 9, DAY 4 - Docker Compose + Python")
    print("=" * 55)
    print(f"PyYAML available: {HAS_YAML}")

    # Task 1 test
    print("\n--- Task 1: Build Config ---")
    services = [
        {"name": "web", "image": "nginx:latest", "ports": ["80:80"]},
        {"name": "api", "image": "node:20", "ports": ["3000:3000"],
         "depends_on": ["db"]},
        {"name": "db", "image": "mongo:7",
         "environment": {"MONGO_INITDB_DATABASE": "myapp"}},
    ]
    config = build_compose_config(services)
    print(f"Services in config: {list(config['services'].keys())}")

    # Task 2 test
    print("\n--- Task 2: Write File ---")
    filepath = write_compose_file(config, os.path.join(OUTPUT_DIR, "docker-compose.yml"))
    print(f"File exists: {os.path.exists(filepath)}")

    # Task 3 test
    print("\n--- Task 3: Validation ---")
    errors = validate_compose(config)
    print(f"Valid config errors: {errors}")

    bad_config = {
        "services": {
            "web": {"ports": ["80:80"]},
            "api": {"image": "node:20", "depends_on": ["nonexistent"]},
        }
    }
    bad_errors = validate_compose(bad_config)
    for e in bad_errors:
        print(f"  Error: {e}")

    # Task 4 test
    print("\n--- Task 4: Environment Configs ---")
    dev_config = compose_for_environment(config, "dev")
    prod_config = compose_for_environment(config, "prod")
    print(f"Dev restart: {dev_config['services']['web'].get('restart', 'NOT SET')}")
    print(f"Prod restart: {prod_config['services']['web'].get('restart', 'NOT SET')}")
    print(f"Prod deploy: {'deploy' in prod_config['services']['web']}")

    # Task 5 test
    print("\n--- Task 5: App Stack ---")
    stack = generate_app_stack("myapp")
    print(f"Stack services: {sorted(stack['services'].keys())}")
    print(f"Has volumes: {'volumes' in stack}")
    write_compose_file(stack, os.path.join(OUTPUT_DIR, "myapp-compose.yml"))
