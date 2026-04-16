# Week 6, Day 5: argparse -- Building CLI Tools

## What You'll Learn

- Create professional command-line interfaces with `argparse`
- Define positional and optional arguments
- Use flags, choices, default values, and help text
- Handle types, required arguments, and boolean flags
- Build a real CLI tool

## Why This Matters for DevOps

Every DevOps tool is a command-line tool. Think of `docker`, `kubectl`, `terraform`, `ansible`
-- they all take arguments and flags. When you build automation scripts, you need them to
accept configuration from the command line:

```
python deploy.py --env production --host web01 --verbose
python monitor.py --check disk --threshold 90 --alert
python backup.py /var/data --compress --retain 7
```

`argparse` turns your scripts into professional CLI tools with help messages, validation,
and error handling -- all for free.

---

## 1. Basic Setup

```python
import argparse

# Create the parser
parser = argparse.ArgumentParser(description="A simple DevOps tool")

# Parse the arguments (reads from sys.argv)
args = parser.parse_args()
```

Run it with `--help`:
```
$ python tool.py --help
usage: tool.py [-h]

A simple DevOps tool

optional arguments:
  -h, --help  show this help message and exit
```

You get `--help` for free. Every argument you add will appear in this help output.

---

## 2. Positional Arguments

Positional arguments are required and identified by their position (no `--` prefix):

```python
import argparse

parser = argparse.ArgumentParser(description="Deploy an application")
parser.add_argument("environment", help="Target environment (e.g., staging, production)")
parser.add_argument("version", help="Version to deploy (e.g., 1.2.3)")

args = parser.parse_args()
print(f"Deploying version {args.version} to {args.environment}")
```

Usage:
```
$ python deploy.py staging 1.2.3
Deploying version 1.2.3 to staging

$ python deploy.py
usage: deploy.py [-h] environment version
deploy.py: error: the following arguments are required: environment, version
```

---

## 3. Optional Arguments (Flags)

Optional arguments start with `--` (long form) or `-` (short form):

```python
import argparse

parser = argparse.ArgumentParser(description="Server management tool")
parser.add_argument("--host", default="localhost", help="Server hostname")
parser.add_argument("--port", type=int, default=8080, help="Server port")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

args = parser.parse_args()
print(f"Connecting to {args.host}:{args.port}")
if args.verbose:
    print("Verbose mode enabled")
```

Usage:
```
$ python server.py --host web01 --port 443 -v
Connecting to web01:443
Verbose mode enabled

$ python server.py
Connecting to localhost:8080
```

---

## 4. Key add_argument() Parameters

| Parameter | Purpose | Example |
|---|---|---|
| `help` | Description shown in --help | `help="Server hostname"` |
| `default` | Value when argument not provided | `default="localhost"` |
| `type` | Convert to this type | `type=int` |
| `required` | Make optional arg mandatory | `required=True` |
| `choices` | Restrict to specific values | `choices=["dev", "staging", "prod"]` |
| `action` | Special handling | `action="store_true"` for boolean flags |
| `nargs` | Number of values expected | `nargs="+"` for one or more |
| `dest` | Name of the attribute | `dest="output_file"` |

---

## 5. Type Conversion

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8080, help="Port number")
parser.add_argument("--timeout", type=float, default=30.0, help="Timeout in seconds")
parser.add_argument("--retries", type=int, default=3, help="Number of retries")

args = parser.parse_args()
# args.port is already an int, not a string
```

If someone passes a non-numeric value for `--port`, argparse will show an error automatically:
```
$ python tool.py --port abc
error: argument --port: invalid int value: 'abc'
```

---

## 6. Choices -- Restricting Values

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--env",
    choices=["development", "staging", "production"],
    default="development",
    help="Target environment"
)
parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default="INFO",
    help="Logging level"
)

args = parser.parse_args()
```

Invalid choices are rejected automatically:
```
$ python tool.py --env testing
error: argument --env: invalid choice: 'testing' (choose from 'development', 'staging', 'production')
```

---

## 7. Boolean Flags

Use `action="store_true"` for flags that don't take a value:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
parser.add_argument("--no-cache", action="store_true", help="Disable caching")

args = parser.parse_args()
# args.verbose is True if --verbose was passed, False otherwise
# Note: --dry-run becomes args.dry_run (hyphens become underscores)
```

---

## 8. Multiple Values with nargs

```python
import argparse

parser = argparse.ArgumentParser()

# Accept multiple hosts
parser.add_argument("--hosts", nargs="+", help="One or more hostnames")

# Accept exactly 2 values
parser.add_argument("--range", nargs=2, type=int, help="Start and end port")

# Accept zero or more
parser.add_argument("--tags", nargs="*", default=[], help="Optional tags")

args = parser.parse_args()
```

Usage:
```
$ python tool.py --hosts web01 web02 web03 --range 8000 9000 --tags prod us-east
```

---

## 9. Required Optional Arguments

Sometimes you want a `--flag` style argument that is required:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--api-key", required=True, help="API key (required)")
parser.add_argument("--region", required=True, choices=["us", "eu", "ap"], help="Region")

args = parser.parse_args()
```

---

## 10. Accessing Arguments

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("target")
parser.add_argument("--port", type=int, default=22)
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()

# Access as attributes
print(args.target)     # positional arg
print(args.port)       # optional arg
print(args.verbose)    # boolean flag

# Convert to dictionary
config = vars(args)
print(config)  # {'target': 'web01', 'port': 22, 'verbose': True}
```

---

## 11. Real-World Example: Server Health Checker CLI

```python
#!/usr/bin/env python3
"""Server health check tool."""
import argparse
import subprocess

def check_host(host, port, verbose):
    """Check if a host is reachable."""
    if verbose:
        print(f"Checking {host}:{port}...")

    result = subprocess.run(
        ["ping", "-c", "1", "-W", "2", host],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"  {host}: OK")
        return True
    else:
        print(f"  {host}: UNREACHABLE")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Check server health and connectivity"
    )
    parser.add_argument(
        "hosts",
        nargs="+",
        help="One or more hostnames or IPs to check"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=80,
        help="Port to check (default: 80)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=5,
        help="Timeout in seconds (default: 5)"
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"Checking {len(args.hosts)} host(s)...")

    results = {}
    for host in args.hosts:
        results[host] = check_host(host, args.port, args.verbose)

    ok = sum(1 for v in results.values() if v)
    print(f"\nResults: {ok}/{len(results)} hosts reachable")

if __name__ == "__main__":
    main()
```

Usage:
```
$ python health.py 8.8.8.8 1.1.1.1 --verbose
Checking 2 host(s)...
Checking 8.8.8.8:80...
  8.8.8.8: OK
Checking 1.1.1.1:80...
  1.1.1.1: OK

Results: 2/2 hosts reachable
```

---

## 12. Description and Epilog

```python
import argparse

parser = argparse.ArgumentParser(
    description="Deploy application to servers",
    epilog="Example: python deploy.py production --version 2.1.0 --verbose"
)
```

---

## Key Takeaways

1. **ArgumentParser()** -- create a parser with a description
2. **add_argument("name")** -- positional (required) argument
3. **add_argument("--name")** -- optional argument
4. **type=int** -- automatic type conversion
5. **choices=[...]** -- restrict valid values
6. **action="store_true"** -- boolean flags
7. **nargs="+"** -- accept multiple values
8. **required=True** -- make optional args mandatory
9. **parse_args()** -- parse and return a namespace object
10. **vars(args)** -- convert args to a dictionary

---

## DevOps Connection

| Real Tool | What argparse Gives You |
|---|---|
| `docker run -p 8080:80 --name web` | Positional + optional args |
| `kubectl get pods --namespace prod` | Optional args with defaults |
| `terraform plan -var-file=prod.tfvars` | Required flags |
| `ansible-playbook -i hosts --check` | Boolean flags, inventory args |

Tomorrow is Practice Day -- you will build 5 mini-projects that combine everything
from this week.
