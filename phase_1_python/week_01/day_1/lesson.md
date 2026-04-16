# Week 1, Day 1: Setup & Hello World

## What You'll Learn Today
- What Python is and why DevOps engineers use it
- How to run Python on your computer
- Your first Python program

## Why Python for DevOps?
Python is the #1 language for DevOps because:
- **Automation**: Automate server management, deployments, monitoring
- **Cloud SDKs**: AWS (boto3), Azure, GCP all have Python libraries
- **Tools**: Ansible, SaltStack, many CI/CD tools are built with Python
- **Simple syntax**: Easy to learn, easy to read, easy to maintain

## Step 1: Check Python is Installed
Open your terminal and type:
```bash
python3 --version
```
You should see something like `Python 3.x.x`. If not, install it:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Mac
brew install python3
```

## Step 2: Your First Program
The `print()` function displays text on the screen.

```python
# This is a comment - Python ignores lines starting with #
print("Hello, World!")
```

## Step 3: The print() Function
```python
# Print text (strings go in quotes)
print("Hello, DevOps Engineer!")

# Print numbers (no quotes needed)
print(42)
print(3.14)

# Print multiple things
print("Server count:", 5)

# Print on same line
print("Loading", end="")
print("...", end="")
print("Done!")
# Output: Loading...Done!

# Print empty line
print()

# Print with special characters
print("Path: C:\\Users\\admin")      # \\ prints one backslash
print("Line 1\nLine 2")              # \n creates a new line
print("Column1\tColumn2")            # \t creates a tab
```

## Key Concepts
| Concept | Example | Meaning |
|---------|---------|---------|
| `print()` | `print("hi")` | Show output on screen |
| String | `"hello"` or `'hello'` | Text in quotes |
| Comment | `# this is ignored` | Notes for humans, Python skips it |
| `\n` | `print("a\nb")` | New line |
| `end=` | `print("hi", end=" ")` | Change what comes after print |

## DevOps Connection
In DevOps, `print()` is how your scripts give feedback:
```python
print("[INFO] Deployment started...")
print("[OK] Server 1 is healthy")
print("[ERROR] Server 2 is unreachable")
```

## Now Do The Exercise!
Open `exercise.py` in this folder and complete the tasks.
Then run `python3 check.py` to verify your answers.
