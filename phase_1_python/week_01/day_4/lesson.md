# Week 1, Day 4: Math Operations

## What You'll Learn Today
- Arithmetic operators for calculations
- Comparison operators to compare values
- Assignment operators for shortcuts
- Operator precedence (what gets calculated first)

## Arithmetic Operators
These let you do math with numbers.

```python
a = 15
b = 4

print(a + b)     # 19   Addition
print(a - b)     # 11   Subtraction
print(a * b)     # 60   Multiplication
print(a / b)     # 3.75 Division (always returns a float!)
print(a // b)    # 3    Floor division (drops the decimal)
print(a % b)     # 3    Modulo (remainder after division)
print(a ** b)    # 50625  Exponent (15 to the power of 4)
```

### Division Details
```python
# Regular division always gives a float
print(10 / 3)    # 3.3333333333333335
print(10 / 2)    # 5.0 (still a float!)

# Floor division drops the decimal part
print(10 // 3)   # 3   (not 3.33, just 3)
print(7 // 2)    # 3   (not 3.5, just 3)

# Modulo gives the remainder
print(10 % 3)    # 1   (10 / 3 = 3 remainder 1)
print(7 % 2)     # 1   (7 / 2 = 3 remainder 1)
print(8 % 2)     # 0   (8 / 2 = 4 remainder 0 -> even number!)
```

### Practical DevOps Math
```python
# How many full servers can we fill?
total_containers = 25
containers_per_server = 8
full_servers = total_containers // containers_per_server
leftover = total_containers % containers_per_server
print(f"Full servers: {full_servers}")    # 3
print(f"Leftover containers: {leftover}")  # 1

# Convert bytes to megabytes
bytes_total = 5368709120
mb = bytes_total / (1024 ** 2)
print(f"Size: {mb:.1f} MB")  # Size: 5120.0 MB
```

## Comparison Operators
These compare two values and return `True` or `False`.

```python
x = 10
y = 20

print(x == y)    # False  Equal to
print(x != y)    # True   Not equal to
print(x < y)     # True   Less than
print(x > y)     # False  Greater than
print(x <= y)    # True   Less than or equal to
print(x >= y)    # False  Greater than or equal to
```

### Common Mistake
```python
# = is ASSIGNMENT (store a value)
port = 8080

# == is COMPARISON (check if equal)
print(port == 8080)   # True
print(port == 3000)   # False

# Don't mix them up!
```

### Practical Comparisons
```python
cpu_usage = 85
memory_free = 2.5

print(f"CPU critical: {cpu_usage > 90}")         # False
print(f"CPU warning: {cpu_usage >= 80}")          # True
print(f"Low memory: {memory_free < 1.0}")         # False
print(f"Port is default HTTP: {port == 80}")      # False
```

## Assignment Operators
Shortcuts for updating a variable's value.

```python
# Instead of writing:
count = count + 1

# You can write:
count += 1    # Same as: count = count + 1
```

### All Assignment Operators
```python
x = 10

x += 5     # x = x + 5    -> x is now 15
x -= 3     # x = x - 3    -> x is now 12
x *= 2     # x = x * 2    -> x is now 24
x /= 4     # x = x / 4    -> x is now 6.0
x //= 2    # x = x // 2   -> x is now 3.0
x %= 2     # x = x % 2    -> x is now 1.0
x **= 3    # x = x ** 3   -> x is now 1.0
```

### Practical Example
```python
# Counting errors in a deployment
error_count = 0

error_count += 1   # First error
error_count += 1   # Second error
error_count += 1   # Third error

print(f"Total errors: {error_count}")  # 3

# Calculating remaining disk space
disk_total = 500   # GB
disk_total -= 120  # OS and apps
disk_total -= 200  # Databases
disk_total -= 50   # Logs
print(f"Free space: {disk_total} GB")  # 130 GB
```

## Operator Precedence
Python follows math rules for the order of operations (like PEMDAS/BODMAS).

```python
# Highest to lowest priority:
# 1. **      (exponent)
# 2. *, /, //, %  (multiplication, division, floor div, modulo)
# 3. +, -    (addition, subtraction)

print(2 + 3 * 4)       # 14 (not 20!)  -> 3*4=12, then 2+12=14
print((2 + 3) * 4)     # 20            -> parentheses first: 5*4=20
print(10 - 2 ** 3)     # 2             -> 2**3=8, then 10-8=2
print(100 / 5 + 3)     # 23.0          -> 100/5=20.0, then 20.0+3=23.0
```

### Tip: Use Parentheses for Clarity
```python
# Even when not strictly needed, parentheses make code readable
disk_used_percent = (used_space / total_space) * 100
average_cpu = (cpu1 + cpu2 + cpu3) / 3
```

## Key Concepts
| Operator | Example | What It Does |
|----------|---------|-------------|
| `+` `-` `*` | `5 + 3` | Basic math |
| `/` | `10 / 3` -> `3.33` | Division (gives float) |
| `//` | `10 // 3` -> `3` | Floor division (drops decimal) |
| `%` | `10 % 3` -> `1` | Modulo (remainder) |
| `**` | `2 ** 3` -> `8` | Exponent (power) |
| `==` `!=` | `x == 5` | Equal / not equal (returns bool) |
| `<` `>` `<=` `>=` | `x > 10` | Comparisons (returns bool) |
| `+=` `-=` etc. | `x += 1` | Update variable in place |

## DevOps Connection
Math operations show up everywhere in DevOps:
```python
# Calculate uptime percentage
total_minutes = 30 * 24 * 60          # Minutes in a month
downtime_minutes = 45
uptime_percent = ((total_minutes - downtime_minutes) / total_minutes) * 100
print(f"Uptime: {uptime_percent:.3f}%")  # Uptime: 99.896%

# Check if server count can be evenly split across zones
servers = 17
zones = 3
per_zone = servers // zones
extra = servers % zones
print(f"Servers per zone: {per_zone}, extra: {extra}")
# Servers per zone: 5, extra: 2
```

## Now Do The Exercise!
Open `exercise.py` and complete the tasks.
Then run `python3 check.py` to verify your answers.
