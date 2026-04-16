# Week 2, Day 1: If/Else Statements

## What You'll Learn Today

- How to make decisions in your Python code using `if`, `else`, and `elif`
- How to write conditions that evaluate to `True` or `False`
- The basics of boolean logic
- How comparison operators work (`==`, `!=`, `>`, `<`, `>=`, `<=`)

---

## Why Does This Matter?

Every DevOps script needs to make decisions. Should we restart a server? Is a port
open or closed? Did a deployment succeed or fail? **Control flow** is how your code
decides what to do next.

---

## 1. The `if` Statement

The simplest decision: "If something is true, do this."

```python
# Basic if statement
# The code inside the if block ONLY runs when the condition is True

server_status = 200

if server_status == 200:
    print("Server is healthy!")
    # This line prints because 200 == 200 is True
```

**Key things to notice:**
- The condition comes after `if` and before the colon `:`
- The code that runs when the condition is True is **indented** (4 spaces)
- `==` means "is equal to" (two equals signs, not one!)

---

## 2. The `if/else` Statement

"If something is true do this, otherwise do that."

```python
# if/else gives us two paths
server_status = 500

if server_status == 200:
    print("Server is healthy!")       # This does NOT run
else:
    print("Server has a problem!")    # This DOES run because 500 != 200
```

Think of it like a fork in the road -- your code always goes one way or the other.

---

## 3. The `elif` Statement (Else If)

When you have more than two possible outcomes, use `elif`:

```python
# elif lets us check multiple conditions in order
server_status = 404

if server_status == 200:
    print("OK - Server is healthy")
elif server_status == 301:
    print("REDIRECT - Resource has moved")
elif server_status == 404:
    print("NOT FOUND - Page does not exist")    # This one matches!
elif server_status == 500:
    print("ERROR - Internal server error")
else:
    print(f"UNKNOWN - Status code: {server_status}")
```

**How it works:**
1. Python checks each condition from top to bottom
2. It runs the FIRST block that matches
3. It skips everything after that
4. `else` catches anything that didn't match above

---

## 4. Comparison Operators

These are the tools you use to build conditions:

```python
# == (equal to)
print(200 == 200)    # True
print(200 == 404)    # False

# != (not equal to)
print(200 != 404)    # True
print(200 != 200)    # False

# > (greater than)
print(100 > 50)      # True
print(50 > 100)      # False

# < (less than)
print(50 < 100)      # True

# >= (greater than or equal to)
print(80 >= 80)      # True
print(80 >= 81)      # False

# <= (less than or equal to)
print(80 <= 100)     # True
```

---

## 5. Boolean Values

Conditions always evaluate to either `True` or `False`. These are called **booleans**.

```python
# You can store booleans in variables
is_server_running = True
is_maintenance_mode = False

if is_server_running:
    print("Server is up!")          # This runs

if is_maintenance_mode:
    print("In maintenance mode")    # This does NOT run
```

---

## 6. Checking Strings

You can compare strings too:

```python
# String comparison
environment = "production"

if environment == "production":
    print("CAREFUL! This is production!")
elif environment == "staging":
    print("This is staging, safer to test here.")
else:
    print("This is a development environment.")
```

---

## 7. Truthy and Falsy Values

In Python, some values act like `True` and others act like `False`:

```python
# These are "falsy" -- they act like False
# False, 0, "" (empty string), None

error_message = ""

if error_message:
    print(f"Error: {error_message}")
else:
    print("No errors!")             # This runs because "" is falsy

# These are "truthy" -- they act like True
# Any non-zero number, any non-empty string

server_name = "web-01"

if server_name:
    print(f"Server name is: {server_name}")   # This runs
```

---

## DevOps Connection

If/else statements are everywhere in DevOps:

- **Health checks**: Is the HTTP status 200? If yes, server is healthy. If not, send an alert.
- **Deployment gates**: Is the test suite passing? If yes, deploy. If not, stop.
- **Port validation**: Is the port number in the valid range (1-65535)?
- **Environment checks**: Are we in production or staging? Different configs for each.

```python
# Real-world example: Simple health check decision
status_code = 503
response_time_ms = 2500

if status_code == 200:
    print("HEALTHY - Server responded OK")
elif status_code == 503:
    print("UNHEALTHY - Service unavailable, paging on-call engineer")
else:
    print(f"WARNING - Unexpected status code: {status_code}")
```

---

## Common Mistakes to Avoid

```python
# MISTAKE 1: Using = instead of ==
# if x = 5:     # WRONG! This is assignment, not comparison
# if x == 5:    # RIGHT! This checks equality

# MISTAKE 2: Forgetting the colon
# if x == 5     # WRONG! Missing colon
# if x == 5:    # RIGHT!

# MISTAKE 3: Wrong indentation
# if x == 5:
# print("yes")      # WRONG! Not indented
#     print("yes")   # RIGHT! Indented with 4 spaces
```

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. They are all DevOps-themed!
When you are done, run `python check.py` to see your score.
