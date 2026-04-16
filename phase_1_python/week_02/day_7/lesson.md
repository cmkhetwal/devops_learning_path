# Week 2, Day 7: Quiz Day -- Control Flow Cheat Sheet

## Week 2 Summary

Congratulations on completing Week 2! Here is your complete reference guide for
everything you learned about control flow in Python.

---

## If / Elif / Else

```python
# Basic if
if condition:
    # runs when condition is True
    pass

# if/else
if condition:
    # runs when True
    pass
else:
    # runs when False
    pass

# if/elif/else
if condition_1:
    # runs when condition_1 is True
    pass
elif condition_2:
    # runs when condition_2 is True (and condition_1 was False)
    pass
elif condition_3:
    # runs when condition_3 is True (and above were False)
    pass
else:
    # runs when NONE of the above were True
    pass
```

---

## Comparison Operators

| Operator | Meaning                  | Example         |
|----------|--------------------------|-----------------|
| `==`     | Equal to                 | `x == 5`        |
| `!=`     | Not equal to             | `x != 5`        |
| `>`      | Greater than             | `x > 5`         |
| `<`      | Less than                | `x < 5`         |
| `>=`     | Greater than or equal to | `x >= 5`        |
| `<=`     | Less than or equal to    | `x <= 5`        |

---

## Logical Operators

| Operator | Meaning                        | Example                      |
|----------|--------------------------------|------------------------------|
| `and`    | Both must be True              | `x > 0 and x < 100`         |
| `or`     | At least one must be True      | `x < 0 or x > 100`          |
| `not`    | Reverses True/False            | `not is_maintenance`         |

**Precedence (highest to lowest):** `not` -> `and` -> `or`

Use parentheses to be explicit: `(a or b) and c`

---

## While Loops

```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1        # DO NOT forget to update your counter!

# While True with break
while True:
    # do something
    if exit_condition:
        break         # exits the loop
```

**Watch out for infinite loops!** Always make sure the condition can become False.

---

## For Loops

```python
# Loop through a list
for item in my_list:
    print(item)

# Loop with range
for i in range(5):         # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):      # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    print(i)

# Loop through a string
for char in "hello":
    print(char)

# Loop with index using enumerate
for index, item in enumerate(my_list):
    print(f"{index}: {item}")
```

---

## Loop Control

```python
# break -- exits the loop entirely
for item in items:
    if item == target:
        break              # stop looping

# continue -- skips to the next iteration
for item in items:
    if item == skip_this:
        continue           # skip this one, keep looping
    print(item)

# else on loops -- runs if loop completed without break
for item in items:
    if item == target:
        print("Found!")
        break
else:
    print("Not found!")    # only runs if break was NOT hit
```

---

## Nested Loops

```python
# Inner loop runs completely for each outer iteration
for server in servers:
    for port in ports:
        print(f"{server}:{port}")
```

---

## Common Patterns

### Retry Pattern
```python
attempt = 0
max_retries = 3
while attempt < max_retries:
    attempt += 1
    # try something
    if success:
        break
```

### Search Pattern
```python
for item in collection:
    if item matches criteria:
        # found it
        break
else:
    # not found
```

### Filter Pattern
```python
for item in collection:
    if should_skip(item):
        continue
    # process item
```

### Accumulator Pattern
```python
total = 0
for value in values:
    total += value
```

---

## Shorthand Operators

| Shorthand  | Equivalent            |
|------------|-----------------------|
| `x += 5`   | `x = x + 5`          |
| `x -= 5`   | `x = x - 5`          |
| `x *= 5`   | `x = x * 5`          |

---

## Truthy and Falsy Values

| Falsy Values         | Truthy Values               |
|----------------------|-----------------------------|
| `False`              | `True`                      |
| `0`                  | Any non-zero number         |
| `""` (empty string)  | Any non-empty string        |
| `None`               | Most other objects           |
| `[]` (empty list)    | Non-empty lists              |

---

## Now Do The Quiz!

Open `exercise.py` and complete all 10 code completion questions.
When you are done, run `python check.py` to see your final Week 2 score!
