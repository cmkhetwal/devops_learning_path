# Week 2, Day 2: Nested Conditions & Logical Operators

## What You'll Learn Today

- How to combine conditions using `and`, `or`, and `not`
- How to nest `if` statements inside other `if` statements
- How to build complex decision-making logic
- When to use each logical operator

---

## 1. The `and` Operator

Both conditions must be `True` for the whole thing to be `True`.

```python
# "and" means BOTH must be true
cpu_usage = 92
memory_usage = 88

if cpu_usage > 90 and memory_usage > 85:
    print("ALERT: Both CPU and memory are high!")
    # This runs because BOTH conditions are True
```

Think of it like a checklist -- every box must be checked.

```python
# Truth table for "and":
# True  and True  -> True
# True  and False -> False
# False and True  -> False
# False and False -> False
```

---

## 2. The `or` Operator

Only ONE condition needs to be `True` for the whole thing to be `True`.

```python
# "or" means AT LEAST ONE must be true
cpu_usage = 95
memory_usage = 40

if cpu_usage > 90 or memory_usage > 85:
    print("ALERT: At least one resource is high!")
    # This runs because cpu_usage > 90 is True (that is enough)
```

Think of it like an alarm system -- any sensor can trigger it.

```python
# Truth table for "or":
# True  or True  -> True
# True  or False -> True
# False or True  -> True
# False or False -> False
```

---

## 3. The `not` Operator

Flips `True` to `False` and `False` to `True`.

```python
# "not" reverses the boolean
is_maintenance = False

if not is_maintenance:
    print("System is available!")     # This runs because not False == True

# Another example
server_running = True

if not server_running:
    print("Server is down!")          # Does NOT run because not True == False
```

---

## 4. Combining Multiple Operators

You can chain `and`, `or`, and `not` together:

```python
# Complex condition example
cpu = 85
memory = 72
disk = 95
is_production = True

# Alert if ANY resource is critical AND we are in production
if (cpu > 90 or memory > 90 or disk > 90) and is_production:
    print("PRODUCTION ALERT: Resource threshold exceeded!")
    # This runs because disk > 90 is True AND is_production is True
```

**Use parentheses `()` to make your logic clear!** Python follows operator precedence
(`not` first, then `and`, then `or`), but parentheses make it obvious what you mean.

---

## 5. Nested If Statements

An `if` inside another `if`. Each level adds more indentation.

```python
# First check if server is reachable, then check its status
server_reachable = True
status_code = 500

if server_reachable:
    print("Server is reachable.")

    if status_code == 200:
        print("And it is healthy!")
    elif status_code == 500:
        print("But it has an internal error!")    # This runs
    else:
        print(f"Status code: {status_code}")
else:
    print("Server is NOT reachable!")
```

**How nesting works:**
- The outer `if` checks `server_reachable`
- Only if that is True do we even look at `status_code`
- Each nested level gets 4 more spaces of indentation

---

## 6. Nested vs. Combined Conditions

These two approaches often do the same thing:

```python
# NESTED approach
role = "admin"
has_2fa = True

if role == "admin":
    if has_2fa:
        print("Access granted to admin panel")

# COMBINED approach (same result, often cleaner)
if role == "admin" and has_2fa:
    print("Access granted to admin panel")
```

Use **nesting** when you want to handle different outcomes at each level.
Use **combined conditions** when you just need one yes/no decision.

---

## 7. Real-World Example: Access Control

```python
# DevOps access control system
username = "deploy-bot"
role = "deployer"
environment = "production"
has_approval = True

# Check access step by step
if role == "admin":
    print(f"{username}: Full access granted (admin)")
elif role == "deployer":
    # Deployers need approval for production
    if environment == "production":
        if has_approval:
            print(f"{username}: Production deploy approved")
        else:
            print(f"{username}: DENIED - Need approval for production")
    else:
        print(f"{username}: Deploy to {environment} granted")
else:
    print(f"{username}: DENIED - Insufficient role")
```

---

## 8. Common Patterns

```python
# Pattern: Check if a value is within a range
port = 443
if 1 <= port <= 65535:
    print("Valid port")    # Python supports chained comparisons!

# Pattern: Check if a string is not empty
hostname = "web-server-01"
if hostname:               # Empty string is falsy
    print(f"Connecting to {hostname}")

# Pattern: Default values with conditions
timeout = 0
if not timeout:
    timeout = 30           # Set default if timeout is 0 or not set
print(f"Timeout: {timeout}s")
```

---

## DevOps Connection

Complex conditions are the backbone of monitoring and alerting:

- **Multi-condition alerts**: CPU high AND memory high? That is worse than just one.
- **Access control**: Does the user have the right role AND the right permissions?
- **Deployment gates**: Are tests passing AND is it not a deploy freeze?
- **Escalation logic**: If critical AND production AND no one has acknowledged it, page the manager.

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. They use `and`, `or`, `not`, and nested conditions.
When you are done, run `python check.py` to see your score.
