# Week 1, Day 3: Input & Output

## What You'll Learn Today
- How to get input from the user with `input()`
- How to convert input to the right data type
- How to use f-strings for clean, formatted output
- How to build interactive scripts

## Getting User Input
The `input()` function pauses your program and waits for the user to type something.

```python
# Basic input - always returns a STRING
name = input("What is your name? ")
print(name)

# The prompt message is optional
answer = input()  # Just waits, no message shown
```

Whatever the user types is stored as a **string**, even if they type a number.

## Type Conversion of Input
Since `input()` always returns a string, you need to convert it when you want a number.

```python
# This WON'T work for math:
age = input("Enter your age: ")
# age is "25" (a string), not 25 (a number)

# Convert to integer:
age = int(input("Enter your age: "))
# Now age is 25 (an integer) and you can do math

# Convert to float:
cpu_usage = float(input("Enter CPU usage: "))
# Now cpu_usage is a decimal number like 75.5
```

### Common Pattern
```python
# Ask for a port number
port_str = input("Enter port number: ")    # "8080" (string)
port = int(port_str)                        # 8080 (integer)

# Or do it in one line:
port = int(input("Enter port number: "))    # 8080 (integer)
```

### What Happens If You Forget to Convert?
```python
# BUG: string + string concatenates instead of adding!
a = input("First number: ")    # User types "5"
b = input("Second number: ")   # User types "3"
print(a + b)                    # Output: "53" (not 8!)

# FIX: convert to int first
a = int(input("First number: "))    # 5
b = int(input("Second number: "))   # 3
print(a + b)                         # Output: 8
```

## f-strings (Formatted String Literals)
f-strings let you put variables directly inside a string. Just put `f` before the opening quote and wrap variables in `{}`.

```python
server = "web-01"
port = 8080

# WITHOUT f-strings (ugly, hard to read)
print("Server " + server + " is running on port " + str(port))

# WITH f-strings (clean and readable!)
print(f"Server {server} is running on port {port}")

# Both output: Server web-01 is running on port 8080
```

### f-string Formatting Tricks
```python
# Put any expression inside the braces
cpu_cores = 4
print(f"Total threads: {cpu_cores * 2}")  # Total threads: 8

# Format decimal places
cpu_usage = 78.5678
print(f"CPU: {cpu_usage:.1f}%")    # CPU: 78.6%
print(f"CPU: {cpu_usage:.2f}%")    # CPU: 78.57%

# Padding and alignment
name = "web-01"
status = "OK"
print(f"{name:<20} {status}")      # web-01               OK
print(f"{name:>20} {status}")      #               web-01 OK

# Padding numbers with zeros
server_num = 3
print(f"server-{server_num:03d}")  # server-003
```

## Putting It All Together
```python
# A simple interactive script
hostname = input("Enter hostname: ")
port = int(input("Enter port: "))
is_https = input("HTTPS? (yes/no): ")

protocol = "https" if is_https == "yes" else "http"
url = f"{protocol}://{hostname}:{port}"

print(f"\nServer URL: {url}")
```

## Key Concepts
| Concept | Example | What It Does |
|---------|---------|-------------|
| `input()` | `name = input("Name: ")` | Ask user for text (returns string) |
| `int()` | `int(input("Port: "))` | Convert input to whole number |
| `float()` | `float(input("CPU: "))` | Convert input to decimal number |
| f-string | `f"Hello {name}"` | Put variables inside strings |
| `:.2f` | `f"{num:.2f}"` | Format to 2 decimal places |
| `:<20` | `f"{text:<20}"` | Left-align, pad to 20 chars |

## DevOps Connection
Interactive scripts are used for setup wizards, config generators, and deployment prompts:
```python
# A mini deployment prompt
app_name = input("Application name: ")
env = input("Environment (dev/staging/prod): ")
replicas = int(input("Number of replicas: "))

print(f"\n--- Deployment Plan ---")
print(f"App:        {app_name}")
print(f"Env:        {env}")
print(f"Replicas:   {replicas}")
print(f"Ready to deploy {app_name} to {env} with {replicas} replicas.")
```

In real-world DevOps, you'll use input to build:
- Server provisioning scripts
- Configuration file generators
- Interactive troubleshooting tools

## Now Do The Exercise!
Open `exercise.py` and complete the tasks.
Then run `python3 check.py` to verify your answers.
