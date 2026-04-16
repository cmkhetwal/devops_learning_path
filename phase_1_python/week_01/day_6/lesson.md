# Week 1, Day 6: Practice Day - Putting It All Together

## What Today Is About
You have spent 5 days learning the building blocks of Python:
- **Day 1**: `print()` - displaying output
- **Day 2**: Variables & data types - storing information
- **Day 3**: `input()` - getting user input
- **Day 4**: Math & numbers - calculations
- **Day 5**: Strings - working with text

Today you combine **all of them** in 5 mini-projects. These are the kinds of
tasks you will do every day as a DevOps engineer.

## Quick Reference Table

| Concept | Syntax | Example |
|---------|--------|---------|
| Print text | `print("text")` | `print("Server started")` |
| Print variable | `print(variable)` | `print(hostname)` |
| Print mixed | `print("Name:", var)` | `print("Port:", 8080)` |
| f-string | `f"text {var}"` | `f"Host: {name}"` |
| Create variable | `name = value` | `port = 8080` |
| String variable | `name = "text"` | `region = "us-east-1"` |
| Integer variable | `name = number` | `retries = 3` |
| Float variable | `name = decimal` | `cpu = 75.5` |
| Boolean variable | `name = True/False` | `is_live = True` |
| Get input | `input("prompt")` | `name = input("Name: ")` |
| Input to int | `int(input("..."))` | `port = int(input("Port: "))` |
| Addition | `a + b` | `total = 10 + 5` |
| Subtraction | `a - b` | `remaining = 100 - 30` |
| Multiplication | `a * b` | `total_mem = 16 * 4` |
| Division | `a / b` | `avg = total / count` |
| Floor division | `a // b` | `groups = 10 // 3` |
| Modulo | `a % b` | `leftover = 10 % 3` |
| Power | `a ** b` | `squared = 2 ** 10` |
| Uppercase | `s.upper()` | `"hello".upper()` |
| Lowercase | `s.lower()` | `"HELLO".lower()` |
| Strip spaces | `s.strip()` | `" hi ".strip()` |
| Replace text | `s.replace(a, b)` | `"a-b".replace("-", "_")` |
| String length | `len(s)` | `len("hello")` |
| Slice string | `s[start:end]` | `"hello"[0:3]` |
| Check type | `type(var)` | `type(port)` |
| Convert to str | `str(value)` | `str(8080)` |
| Convert to int | `int(value)` | `int("3000")` |
| Convert to float | `float(value)` | `float("75.5")` |
| Round number | `round(n, digits)` | `round(3.14159, 2)` |

## Tips for Today
- Read each mini-project carefully before writing code
- Use f-strings whenever you need to mix text and variables
- Test your code often with `python3 exercise.py`
- When you are done, run `python3 check.py` to verify

## Now Do The Exercise!
Open `exercise.py` and complete the 5 mini-projects.
Then run `python3 check.py` to verify your answers.
