# Week 2, Day 3: While Loops

## What You'll Learn Today

- How to repeat code using `while` loops
- How to use counters to control how many times a loop runs
- How to avoid infinite loops (and when they are useful!)
- How to use `break` to exit a loop early

---

## 1. What Is a While Loop?

A `while` loop keeps running as long as its condition is `True`.

```python
# Basic while loop
count = 1

while count <= 5:
    print(f"Attempt {count}")
    count = count + 1      # IMPORTANT: Update the counter!

# Output:
# Attempt 1
# Attempt 2
# Attempt 3
# Attempt 4
# Attempt 5
```

**How it works step by step:**
1. Check the condition: `count <= 5` -- is 1 <= 5? Yes!
2. Run the indented code block
3. Go back to step 1 and check again
4. When `count` becomes 6, 6 <= 5 is `False`, so the loop stops

---

## 2. The Counter Pattern

The most common while loop pattern uses a counter variable:

```python
# Counter pattern
retries = 0
max_retries = 3

while retries < max_retries:
    print(f"Connection attempt {retries + 1} of {max_retries}")
    retries += 1    # This is shorthand for: retries = retries + 1

print("Done trying!")

# Output:
# Connection attempt 1 of 3
# Connection attempt 2 of 3
# Connection attempt 3 of 3
# Done trying!
```

The `+=` shorthand: `retries += 1` is the same as `retries = retries + 1`.

---

## 3. Infinite Loops (Danger!)

If the condition never becomes `False`, the loop runs forever:

```python
# WARNING: This loop NEVER stops!
# count = 1
# while count <= 5:
#     print(f"Count: {count}")
#     # Oops! We forgot to update count!
#     # count stays at 1 forever, and 1 <= 5 is always True

# If you accidentally run an infinite loop, press Ctrl+C to stop it!
```

**Always make sure something inside the loop changes the condition!**

---

## 4. Intentional Infinite Loops with `break`

Sometimes you WANT a loop that runs "forever" -- until a specific condition is met:

```python
# Monitoring loop with break
attempts = 0

while True:                    # This runs forever...
    attempts += 1
    print(f"Checking server... attempt {attempts}")

    if attempts >= 5:
        print("Max attempts reached, stopping.")
        break                  # ...until break exits the loop!

print("Monitoring ended.")
```

`break` immediately exits the loop. Code after the loop continues normally.

---

## 5. Countdown Timer

While loops are great for counting down:

```python
# Countdown timer for a deployment
seconds = 5

print("Deploying in...")
while seconds > 0:
    print(f"  {seconds}...")
    seconds -= 1    # Shorthand for: seconds = seconds - 1

print("  DEPLOYED!")

# Output:
# Deploying in...
#   5...
#   4...
#   3...
#   2...
#   1...
#   DEPLOYED!
```

---

## 6. While Loop with User-Like Input (Simulated)

In DevOps, you might loop until a condition changes:

```python
# Simulate checking server health until it is healthy
check_count = 0
server_healthy = False

while not server_healthy:
    check_count += 1
    print(f"Health check #{check_count}...")

    # Simulate: server becomes healthy on check #3
    if check_count >= 3:
        server_healthy = True
        print("Server is now healthy!")

print(f"Total checks performed: {check_count}")
```

---

## 7. Combining While Loops with If Statements

```python
# Retry logic with different outcomes
attempt = 0
max_attempts = 5
connected = False

while attempt < max_attempts and not connected:
    attempt += 1
    print(f"Attempt {attempt}: Connecting to database...")

    # Simulate: connection succeeds on attempt 3
    if attempt == 3:
        connected = True
        print("Connected successfully!")

if not connected:
    print("Failed to connect after all attempts.")
else:
    print(f"Connected on attempt {attempt}.")
```

Notice: the while condition checks TWO things with `and`:
- We have not exceeded max attempts
- We are not connected yet

---

## 8. The `+=`, `-=`, `*=` Shorthand

These save you typing:

```python
x = 10
x += 5     # x = x + 5  -> x is now 15
x -= 3     # x = x - 3  -> x is now 12
x *= 2     # x = x * 2  -> x is now 24

# You will use += a lot with counters in while loops
```

---

## DevOps Connection

While loops are essential in DevOps for:

- **Retry logic**: Keep trying to connect to a server/database until it works or you hit a limit
- **Monitoring loops**: Continuously check system health
- **Polling**: Wait for a deployment to finish by checking its status repeatedly
- **Countdown timers**: Wait before retrying, graceful shutdown countdowns
- **Queue processing**: Keep processing messages until the queue is empty

```python
# Real-world pattern: Retry with attempt limit
import time   # We will learn imports later, just showing the pattern

attempt = 0
max_retries = 3
success = False

while attempt < max_retries and not success:
    attempt += 1
    print(f"[Attempt {attempt}/{max_retries}] Deploying application...")

    # In real code, you would try the deployment here
    # success = deploy_application()

    if not success and attempt < max_retries:
        print("  Failed. Retrying in 5 seconds...")
        # time.sleep(5)  # Wait 5 seconds before retry
```

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks.
When you are done, run `python check.py` to see your score.
