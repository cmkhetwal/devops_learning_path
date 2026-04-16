# Week 4, Day 6: Practice Day - 5 Mini-Projects

## What You'll Build Today

Today is all about practice! You'll build 5 mini-projects that combine
everything you've learned about functions and modules this week.

Each mini-project is a realistic tool that a DevOps engineer might actually use.

---

## Mini-Project 1: Password Generator

Generate secure passwords for service accounts, database users, and API keys.

**Concepts used:** functions, default parameters, random module, string operations

```python
import random
import string

def generate_password(length=16, use_uppercase=True, use_digits=True, use_special=True):
    """Generate a random password with configurable options."""
    chars = string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_special:
        chars += "!@#$%^&*"

    password = ''.join(random.choice(chars) for _ in range(length))
    return password
```

---

## Mini-Project 2: File Size Converter

Convert between bytes, KB, MB, and GB -- essential for monitoring disk usage.

**Concepts used:** functions, return values, conditional logic

```python
def bytes_to_human(size_bytes):
    """Convert bytes to a human-readable string."""
    units = [("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)]
    for unit, threshold in units:
        if size_bytes >= threshold:
            value = size_bytes / threshold
            return f"{value:.2f} {unit}"
    return f"{size_bytes} bytes"

print(bytes_to_human(1536))         # "1.50 KB"
print(bytes_to_human(2621440))      # "2.50 MB"
```

---

## Mini-Project 3: Server Health Check Library

A collection of functions that work together to check server health.

**Concepts used:** multiple functions, dictionaries, *args, return values

```python
def check_cpu(cpu_percent, threshold=90):
    return {"metric": "cpu", "value": cpu_percent, "ok": cpu_percent < threshold}

def check_memory(mem_percent, threshold=85):
    return {"metric": "memory", "value": mem_percent, "ok": mem_percent < threshold}

def check_disk(disk_percent, threshold=80):
    return {"metric": "disk", "value": disk_percent, "ok": disk_percent < threshold}

def full_health_check(cpu, memory, disk):
    checks = [check_cpu(cpu), check_memory(memory), check_disk(disk)]
    all_ok = all(c["ok"] for c in checks)
    return {"status": "healthy" if all_ok else "unhealthy", "checks": checks}
```

---

## Mini-Project 4: Simple Encryption/Decryption

A Caesar cipher for learning -- shift each letter by a fixed number.

**Concepts used:** functions, string iteration, chr/ord built-ins

```python
def encrypt(text, shift=3):
    """Encrypt text using Caesar cipher."""
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def decrypt(text, shift=3):
    """Decrypt by shifting in the opposite direction."""
    return encrypt(text, -shift)
```

---

## Mini-Project 5: CLI Tool

Combine functions into a command-line tool with a menu system.

**Concepts used:** functions, input(), loops, all previous concepts

```python
def show_menu():
    print("1. Generate Password")
    print("2. Convert File Size")
    print("3. Check Server Health")
    print("4. Encrypt/Decrypt Text")
    print("5. Exit")

def main():
    while True:
        show_menu()
        choice = input("Choose: ")
        if choice == "1":
            # call password generator
            pass
        elif choice == "5":
            print("Goodbye!")
            break
```

---

## Tips for Today

1. **Start simple** -- get each function working before combining them
2. **Test as you go** -- run `python exercise.py` to test individual functions
3. **Read the docstrings** -- each task has clear instructions
4. **Use the lesson examples** -- the code above shows patterns to follow

---

## Today's Exercise

Open `exercise.py` and build all 5 mini-projects. Each is a set of functions
you need to implement.

Run `python check.py` to verify your solutions!
