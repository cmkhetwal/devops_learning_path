# Week 4, Day 2: Function Arguments

## What You'll Learn
- Positional arguments vs keyword arguments
- Default parameter values
- `*args` for variable positional arguments
- `**kwargs` for variable keyword arguments
- How to combine them all

---

## Positional Arguments

When you call a function, arguments are matched to parameters **by position**:

```python
def deploy(app_name, version, environment):
    print(f"Deploying {app_name} v{version} to {environment}")

# Positional: order matters!
deploy("my-api", "2.1.0", "production")
# Output: Deploying my-api v2.1.0 to production

deploy("production", "my-api", "2.1.0")   # WRONG - mixed up!
# Output: Deploying production vmy-api to 2.1.0
```

---

## Keyword Arguments

You can also pass arguments **by name**, so order doesn't matter:

```python
def deploy(app_name, version, environment):
    print(f"Deploying {app_name} v{version} to {environment}")

# Keyword arguments: order doesn't matter
deploy(environment="production", app_name="my-api", version="2.1.0")
# Output: Deploying my-api v2.1.0 to production
```

You can mix positional and keyword, but positional must come first:

```python
deploy("my-api", environment="production", version="2.1.0")   # OK
deploy(app_name="my-api", "2.1.0", "production")              # ERROR!
```

---

## Default Parameter Values

Give parameters a default value so they're optional when calling:

```python
def deploy(app_name, version, environment="staging"):
    print(f"Deploying {app_name} v{version} to {environment}")

deploy("my-api", "2.1.0")                # Uses default: staging
deploy("my-api", "2.1.0", "production")  # Overrides: production
```

**Rule:** Parameters with defaults must come AFTER those without:

```python
def deploy(app_name, environment="staging", version):   # ERROR!
    pass

def deploy(app_name, version, environment="staging"):   # CORRECT!
    pass
```

A realistic DevOps example:

```python
def create_server(hostname, region="us-east-1", size="t2.micro", count=1):
    print(f"Creating {count}x {size} in {region}: {hostname}")

create_server("web-01")
# Creating 1x t2.micro in us-east-1: web-01

create_server("db-01", region="eu-west-1", size="r5.large")
# Creating 1x r5.large in eu-west-1: db-01
```

---

## *args - Variable Positional Arguments

Sometimes you don't know how many arguments will be passed. Use `*args` to
collect them all into a **tuple**:

```python
def restart_servers(*server_names):
    print(f"Restarting {len(server_names)} servers...")
    for server in server_names:
        print(f"  Restarting {server}")

restart_servers("web-01")
restart_servers("web-01", "web-02", "web-03")
restart_servers()   # Also valid - empty tuple
```

The name `args` is just a convention. You could use `*servers` or `*items`.
The `*` is what matters.

How it works under the hood:

```python
def show_args(*args):
    print(type(args))   # <class 'tuple'>
    print(args)         # ('web-01', 'web-02', 'web-03')

show_args("web-01", "web-02", "web-03")
```

---

## **kwargs - Variable Keyword Arguments

Use `**kwargs` to collect extra keyword arguments into a **dictionary**:

```python
def configure_server(hostname, **settings):
    print(f"Configuring {hostname}:")
    for key, value in settings.items():
        print(f"  {key} = {value}")

configure_server("web-01", port=8080, workers=4, debug=False)
# Configuring web-01:
#   port = 8080
#   workers = 4
#   debug = False
```

Again, `kwargs` is just a convention. The `**` is what matters.

---

## Combining Everything

The order matters when you combine argument types:

```python
def deploy(app_name, version="latest", *extra_args, **options):
    print(f"App: {app_name}, Version: {version}")
    print(f"Extra args: {extra_args}")
    print(f"Options: {options}")

deploy("my-api", "2.0", "flag1", "flag2", timeout=30, retries=3)
# App: my-api, Version: 2.0
# Extra args: ('flag1', 'flag2')
# Options: {'timeout': 30, 'retries': 3}
```

**The order rule:**
1. Regular positional parameters
2. `*args`
3. Keyword-only parameters (after `*args`)
4. `**kwargs`

```python
def full_example(required, *args, keyword_only="default", **kwargs):
    print(f"required: {required}")
    print(f"args: {args}")
    print(f"keyword_only: {keyword_only}")
    print(f"kwargs: {kwargs}")
```

---

## Practical Example: Logging Function

```python
def log_event(message, level="INFO", *tags, **metadata):
    """Log an event with optional tags and metadata."""
    tag_str = ", ".join(tags) if tags else "none"
    print(f"[{level}] {message}")
    print(f"  Tags: {tag_str}")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

log_event("Server started")
# [INFO] Server started
#   Tags: none

log_event("Deploy failed", "ERROR", "deploy", "critical",
          server="web-01", version="2.1.0")
# [ERROR] Deploy failed
#   Tags: deploy, critical
#   server: web-01
#   version: 2.1.0
```

---

## Unpacking Arguments

You can also use `*` and `**` when **calling** functions to unpack lists
and dictionaries:

```python
def deploy(app_name, version, environment):
    print(f"Deploying {app_name} v{version} to {environment}")

# Unpack a list into positional args
args = ["my-api", "2.1.0", "production"]
deploy(*args)

# Unpack a dictionary into keyword args
config = {"app_name": "my-api", "version": "2.1.0", "environment": "staging"}
deploy(**config)
```

---

## DevOps Connection

Flexible arguments make your tools adaptable:
- **Default values** mean sensible defaults (region, instance size, retries)
- **`*args`** lets you pass variable numbers of servers, files, or tags
- **`**kwargs`** lets you pass configuration options without changing the function signature
- Real tools like Ansible, Docker SDK, and Boto3 use these patterns heavily

---

## Today's Exercise

Open `exercise.py` and complete the tasks. You'll build:
1. A flexible server config function with defaults
2. A logging function using `*args` and `**kwargs`
3. A function that unpacks config dictionaries

Run `python check.py` to verify your solutions!
