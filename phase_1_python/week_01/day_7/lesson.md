# Week 1, Day 7: Weekly Quiz Day

## How Today Works
Today is quiz day! There are two parts:

### Part 1: Self-Assessment (exercise.py)
Open `exercise.py` in this folder. You will find 10 fill-in-the-blank code
questions. Each one is a commented-out line of code with a blank (`____`)
that you need to fill in. Uncomment the line, replace `____` with the correct
answer, and run `python3 check.py` to see your score.

### Part 2: Interactive Quiz
When you finish the self-assessment, run the interactive quiz:
```bash
python3 ../../quiz.py 1
```
This will test you on all Week 1 concepts with multiple-choice questions.

---

## Week 1 Cheat Sheet

Keep this page open as a reference. It covers everything you learned this week.

### print() - Displaying Output (Day 1)
```python
print("Hello, World!")                 # Print text
print(42)                              # Print a number
print("Port:", 8080)                   # Print multiple items
print(f"Host: {hostname}")             # f-string (variable in text)
print("Line1\nLine2")                  # \n = new line
print("Loading...", end="")            # end="" prevents new line
```

### Variables & Data Types (Day 2)
```python
# Four basic types
server = "web-01"          # str   (text in quotes)
port = 8080                # int   (whole number)
cpu = 75.5                 # float (decimal number)
is_live = True             # bool  (True or False)

# Check type
print(type(server))        # <class 'str'>

# Convert types
int("3000")                # str -> int
str(8080)                  # int -> str
float("75.5")              # str -> float
```

### Naming Rules
```python
# Use snake_case for variables
server_name = "web-01"     # GOOD
serverName = "web-01"      # Works but not Pythonic
# 2server = "web-01"       # ERROR: can't start with number
# server-name = "web-01"   # ERROR: hyphens not allowed
```

### input() - Getting User Input (Day 3)
```python
name = input("Your name: ")           # Always returns a string
port = int(input("Port number: "))    # Convert to int
cpu = float(input("CPU usage: "))     # Convert to float
```

### Math Operations (Day 4)
```python
10 + 3       # 13    Addition
10 - 3       # 7     Subtraction
10 * 3       # 30    Multiplication
10 / 3       # 3.333 Division (always returns float)
10 // 3      # 3     Floor division (whole number only)
10 % 3       # 1     Modulo (remainder)
10 ** 3      # 1000  Power (exponent)

round(3.14159, 2)   # 3.14  Round to 2 decimal places
abs(-5)              # 5     Absolute value
```

### Strings - Working with Text (Day 5)
```python
s = "Hello, World"

# Case methods
s.upper()                  # "HELLO, WORLD"
s.lower()                  # "hello, world"
s.title()                  # "Hello, World"

# Cleaning
"  hi  ".strip()           # "hi"
"  hi  ".lstrip()          # "hi  "
"  hi  ".rstrip()          # "  hi"

# Searching
s.find("World")            # 7 (index where found)
s.count("l")               # 3
s.startswith("Hello")      # True
s.endswith("World")        # True

# Modifying
s.replace("World", "DevOps")  # "Hello, DevOps"

# Slicing
s[0]                       # "H"      (first character)
s[0:5]                     # "Hello"  (index 0 to 4)
s[-5:]                     # "World"  (last 5 characters)

# Length
len(s)                     # 12

# f-strings
name = "web-01"
port = 8080
print(f"Server {name} on port {port}")
```

### Common Patterns in DevOps
```python
# Formatted log line
print(f"[{date} {time}] [{level}] {message}")

# Percentage calculation
rate = successful / total * 100
print(f"Success rate: {round(rate, 1)}%")

# Time conversion
minutes = total_seconds // 60
seconds = total_seconds % 60
print(f"Duration: {minutes}m {seconds}s")

# Hostname cleanup
clean = messy_hostname.strip().lower().replace("-", "_")
```

---

## Now Do The Exercise!
Open `exercise.py` and complete the 10 fill-in-the-blank questions.
Then run `python3 check.py` to see your score.

When you are done, run the interactive quiz:
```bash
python3 ../../quiz.py 1
```
