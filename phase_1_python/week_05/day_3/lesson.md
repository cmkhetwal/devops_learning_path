# Week 5, Day 3: JSON & YAML

## What You'll Learn
- How to read and write JSON files with the `json` module
- The difference between `load/dump` and `loads/dumps`
- How to work with YAML using the `pyyaml` library
- Common config file patterns in DevOps
- Converting between JSON and YAML

---

## Why JSON & YAML Matter in DevOps

Nearly every DevOps tool uses JSON or YAML:
- **JSON** - APIs, Terraform state, package.json, CloudFormation
- **YAML** - Kubernetes manifests, Ansible playbooks, Docker Compose, GitHub Actions, CI/CD pipelines

Understanding both formats is essential for any DevOps role.

---

## JSON Basics

JSON (JavaScript Object Notation) maps directly to Python data types:

| JSON | Python |
|------|--------|
| `{}` object | `dict` |
| `[]` array | `list` |
| `"string"` | `str` |
| `123` | `int` |
| `1.5` | `float` |
| `true/false` | `True/False` |
| `null` | `None` |

---

## Reading JSON Files: `json.load()`

```python
import json

# Read a JSON file
with open("config.json", "r") as file:
    config = json.load(file)

# config is now a Python dictionary (or list)
print(config)
print(type(config))
print(config["database"]["host"])
```

Example `config.json`:
```json
{
    "database": {
        "host": "db-01.example.com",
        "port": 5432,
        "name": "myapp"
    },
    "debug": false
}
```

---

## Writing JSON Files: `json.dump()`

```python
import json

config = {
    "app_name": "web-service",
    "version": "2.1.0",
    "servers": ["web-01", "web-02"],
    "database": {
        "host": "db-01.example.com",
        "port": 5432,
    },
    "debug": False,
}

with open("config.json", "w") as file:
    json.dump(config, file, indent=4)
```

The `indent=4` parameter makes the output human-readable with 4-space indentation.

---

## JSON Strings: `loads()` and `dumps()`

Sometimes you work with JSON as a string (e.g., from an API response), not a file.

```python
import json

# Parse a JSON string into Python
json_string = '{"server": "web-01", "status": "online"}'
data = json.loads(json_string)  # loads = load string
print(data["server"])  # "web-01"

# Convert Python to a JSON string
server_info = {"server": "web-01", "cpu": 45.2, "online": True}
json_output = json.dumps(server_info, indent=2)  # dumps = dump string
print(json_output)
```

### Memory Aid
- `json.load()` / `json.dump()` = work with **files**
- `json.loads()` / `json.dumps()` = work with **strings** (the "s" stands for "string")

---

## YAML Basics

YAML (YAML Ain't Markup Language) is a human-friendly data format.

### Installing PyYAML

YAML support requires the `pyyaml` package:

```bash
pip install pyyaml
```

### YAML Syntax

```yaml
# YAML uses indentation (like Python!)
app_name: web-service
version: "2.1.0"
debug: false

servers:
  - web-01
  - web-02

database:
  host: db-01.example.com
  port: 5432
  name: myapp
```

Key differences from JSON:
- No braces `{}` or brackets `[]` needed
- No quotes needed for most strings
- Lists use `- ` prefix
- Comments use `#`

---

## Reading YAML Files

```python
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# config is a Python dictionary
print(config)
print(config["database"]["host"])
```

**Always use `yaml.safe_load()`** instead of `yaml.load()`. The safe version prevents execution of arbitrary code embedded in YAML files.

---

## Writing YAML Files

```python
import yaml

config = {
    "app_name": "web-service",
    "version": "2.1.0",
    "servers": ["web-01", "web-02"],
    "database": {
        "host": "db-01.example.com",
        "port": 5432,
    },
    "debug": False,
}

with open("config.yaml", "w") as file:
    yaml.dump(config, file, default_flow_style=False)
```

The `default_flow_style=False` parameter ensures the output is in the readable block style rather than compact inline style.

---

## YAML Strings: `safe_load()` and `dump()`

```python
import yaml

# Parse a YAML string
yaml_string = """
servers:
  - web-01
  - web-02
database:
  host: db-01
  port: 5432
"""
data = yaml.safe_load(yaml_string)
print(data)

# Convert Python to YAML string
yaml_output = yaml.dump(data, default_flow_style=False)
print(yaml_output)
```

---

## Converting Between JSON and YAML

```python
import json
import yaml

# JSON to YAML
with open("config.json", "r") as f:
    data = json.load(f)

with open("config.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False)

# YAML to JSON
with open("config.yaml", "r") as f:
    data = yaml.safe_load(f)

with open("config.json", "w") as f:
    json.dump(data, f, indent=4)
```

---

## Common DevOps Patterns

### Pattern 1: Read Config, Use Values

```python
import json

with open("deploy_config.json", "r") as f:
    config = json.load(f)

target_env = config["environment"]
servers = config["servers"]

for server in servers:
    print(f"Deploying to {server} in {target_env}...")
```

### Pattern 2: Update a Config File

```python
import json

# Read existing config
with open("config.json", "r") as f:
    config = json.load(f)

# Modify a value
config["version"] = "2.2.0"
config["last_updated"] = "2024-01-15"

# Write it back
with open("config.json", "w") as f:
    json.dump(config, f, indent=4)
```

### Pattern 3: Merge Multiple Configs

```python
import yaml

# Load base config
with open("base.yaml", "r") as f:
    base = yaml.safe_load(f)

# Load environment override
with open("production.yaml", "r") as f:
    override = yaml.safe_load(f)

# Merge (override wins for duplicate keys)
merged = {**base, **override}

print("Merged config:")
for key, value in merged.items():
    print(f"  {key}: {value}")
```

---

## DevOps Connection

JSON and YAML are everywhere in DevOps:
- **Kubernetes** - All manifests are YAML
- **Docker Compose** - `docker-compose.yml`
- **Terraform** - State files and some configs in JSON
- **Ansible** - Playbooks and inventory in YAML
- **CI/CD** - GitHub Actions, GitLab CI, Jenkins pipelines
- **APIs** - Most REST APIs return JSON

---

## Key Takeaways

1. `json.load(file)` reads JSON from a file; `json.loads(string)` parses a JSON string
2. `json.dump(data, file, indent=4)` writes pretty JSON to a file
3. Install `pyyaml` with `pip install pyyaml` for YAML support
4. **Always** use `yaml.safe_load()` instead of `yaml.load()`
5. JSON and YAML are easily interchangeable since they both map to Python dicts and lists
6. Use `indent=4` for JSON and `default_flow_style=False` for YAML to get readable output
