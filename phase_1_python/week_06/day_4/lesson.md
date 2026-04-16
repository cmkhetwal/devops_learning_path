# Week 6, Day 4: Regular Expressions

## What You'll Learn

- Understand what regular expressions (regex) are and when to use them
- Use `re.search()`, `re.findall()`, `re.sub()`, and `re.match()`
- Master common regex patterns: `\d`, `\w`, `\s`, `+`, `*`, `?`
- Parse IP addresses, emails, and error codes from log files

## Why This Matters for DevOps

Log files are the lifeblood of troubleshooting. When a production server goes down at 3 AM,
you need to quickly extract IP addresses, timestamps, error codes, and status messages from
thousands of lines of text. Regular expressions let you find patterns in text with surgical
precision. They are used in log analysis, input validation, configuration parsing, and
monitoring alert rules.

---

## 1. What Is a Regular Expression?

A regular expression (regex) is a pattern that describes a set of strings. Instead of
searching for an exact word like "error", you can search for patterns like "any line
that starts with a timestamp followed by ERROR".

```python
import re

text = "Server started on port 8080"

# Search for a number
match = re.search(r"\d+", text)
if match:
    print(f"Found number: {match.group()}")  # 8080
```

Always use raw strings (`r"..."`) for regex patterns. This prevents Python from
interpreting backslashes as escape characters.

---

## 2. Common Pattern Characters

| Pattern | Matches | Example |
|---|---|---|
| `\d` | Any digit (0-9) | `\d+` matches "8080" |
| `\D` | Any non-digit | `\D+` matches "port " |
| `\w` | Any word character (a-z, A-Z, 0-9, _) | `\w+` matches "Server" |
| `\W` | Any non-word character | `\W` matches " " |
| `\s` | Any whitespace (space, tab, newline) | `\s+` matches "  " |
| `\S` | Any non-whitespace | `\S+` matches "Server" |
| `.` | Any character (except newline) | `a.b` matches "acb" |
| `^` | Start of string/line | `^Error` matches "Error at..." |
| `$` | End of string/line | `\.log$` matches "app.log" |

---

## 3. Quantifiers

| Quantifier | Meaning | Example |
|---|---|---|
| `+` | One or more | `\d+` matches "123" (not empty) |
| `*` | Zero or more | `\d*` matches "" or "123" |
| `?` | Zero or one | `https?` matches "http" or "https" |
| `{3}` | Exactly 3 | `\d{3}` matches "192" |
| `{2,4}` | Between 2 and 4 | `\d{2,4}` matches "80" or "8080" |

---

## 4. re.search() -- Find the First Match

`re.search()` scans the entire string and returns the first match:

```python
import re

log_line = "2024-01-15 ERROR: Connection refused from 192.168.1.50"

# Find the IP address
match = re.search(r"\d+\.\d+\.\d+\.\d+", log_line)
if match:
    print(f"IP: {match.group()}")  # 192.168.1.50

# Find the date
match = re.search(r"\d{4}-\d{2}-\d{2}", log_line)
if match:
    print(f"Date: {match.group()}")  # 2024-01-15
```

**Always check if match is not None before calling `.group()`!**

---

## 5. re.findall() -- Find ALL Matches

```python
import re

log = """
192.168.1.10 - GET /api/users 200
10.0.0.5 - POST /api/login 401
192.168.1.10 - GET /api/data 200
172.16.0.1 - DELETE /api/users/5 403
"""

# Find all IP addresses
ips = re.findall(r"\d+\.\d+\.\d+\.\d+", log)
print(ips)  # ['192.168.1.10', '10.0.0.5', '192.168.1.10', '172.16.0.1']

# Find all HTTP status codes (3 digits at end of line)
codes = re.findall(r"\b\d{3}$", log, re.MULTILINE)
print(codes)  # ['200', '401', '200', '403']

# Find all URLs
urls = re.findall(r"/\S+", log)
print(urls)  # ['/api/users', '/api/login', '/api/data', '/api/users/5']
```

---

## 6. Groups -- Extracting Parts of a Match

Use parentheses `()` to define groups within a pattern:

```python
import re

log_line = "2024-01-15 10:30:45 ERROR [auth] Login failed for user admin"

# Extract date, time, level, and module
pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\w+) \[(\w+)\]"
match = re.search(pattern, log_line)

if match:
    print(f"Date: {match.group(1)}")    # 2024-01-15
    print(f"Time: {match.group(2)}")    # 10:30:45
    print(f"Level: {match.group(3)}")   # ERROR
    print(f"Module: {match.group(4)}")  # auth
    print(f"All groups: {match.groups()}")  # ('2024-01-15', '10:30:45', 'ERROR', 'auth')
```

With `re.findall()`, groups are returned as tuples:

```python
import re

log = """
2024-01-15 ERROR disk_full
2024-01-15 WARNING high_cpu
2024-01-16 ERROR out_of_memory
"""

# Find all (date, level, message) tuples
entries = re.findall(r"(\d{4}-\d{2}-\d{2}) (\w+) (\w+)", log)
for date, level, msg in entries:
    print(f"{date} [{level}] {msg}")
```

---

## 7. re.sub() -- Search and Replace

```python
import re

# Mask IP addresses in a log
log = "Connection from 192.168.1.50 to 10.0.0.1 on port 8080"
masked = re.sub(r"\d+\.\d+\.\d+\.\d+", "X.X.X.X", log)
print(masked)  # Connection from X.X.X.X to X.X.X.X on port 8080

# Remove timestamps from log lines
log_line = "2024-01-15 10:30:45 ERROR Something broke"
clean = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", "", log_line)
print(clean)  # ERROR Something broke

# Replace multiple spaces with a single space
messy = "too    many     spaces"
clean = re.sub(r"\s+", " ", messy)
print(clean)  # too many spaces
```

---

## 8. re.match() vs re.search()

```python
import re

line = "ERROR: disk full"

# re.match() -- only checks the BEGINNING of the string
match = re.match(r"ERROR", line)
print(bool(match))  # True

match = re.match(r"disk", line)
print(bool(match))  # False (disk is not at the start)

# re.search() -- checks ANYWHERE in the string
match = re.search(r"disk", line)
print(bool(match))  # True
```

Rule of thumb: Use `re.search()` unless you specifically need to match the start.

---

## 9. Character Classes

```python
import re

# Match specific characters with []
re.findall(r"[aeiou]", "hello world")        # ['e', 'o', 'o']

# Match a range
re.findall(r"[a-f]", "abcdefghij")           # ['a', 'b', 'c', 'd', 'e', 'f']

# Negate with ^
re.findall(r"[^0-9]", "abc123")              # ['a', 'b', 'c']

# Common log levels
re.findall(r"\b(ERROR|WARNING|CRITICAL)\b", "ERROR: disk WARNING: cpu")
# ['ERROR', 'WARNING']
```

---

## 10. Useful Regex Flags

```python
import re

# re.IGNORECASE (re.I) -- case-insensitive matching
re.findall(r"error", "Error ERROR error", re.IGNORECASE)
# ['Error', 'ERROR', 'error']

# re.MULTILINE (re.M) -- ^ and $ match line boundaries
text = "line one\nERROR: bad\nline three"
re.findall(r"^ERROR.*$", text, re.MULTILINE)
# ['ERROR: bad']
```

---

## 11. Common DevOps Regex Patterns

```python
import re

# IPv4 address
ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"

# Email address (basic)
email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

# HTTP status code
status_pattern = r"\b[1-5]\d{2}\b"

# Timestamp (YYYY-MM-DD HH:MM:SS)
timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

# URL
url_pattern = r"https?://[^\s]+"

# MAC address
mac_pattern = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"
```

---

## 12. Real-World Example: Log Analyzer

```python
import re

def analyze_log(log_text):
    """Extract key information from a log file."""
    results = {
        "error_count": len(re.findall(r"\bERROR\b", log_text)),
        "warning_count": len(re.findall(r"\bWARNING\b", log_text)),
        "unique_ips": list(set(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", log_text))),
        "error_messages": re.findall(r"ERROR[:\s]+(.+)", log_text),
        "timestamps": re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", log_text),
    }
    return results
```

---

## Key Takeaways

1. **re.search()** -- find the first match anywhere in a string
2. **re.findall()** -- find all matches, returns a list
3. **re.sub()** -- search and replace
4. **Groups `()`** -- extract specific parts of a match
5. **`\d` `\w` `\s`** -- digits, word chars, whitespace
6. **`+` `*` `?`** -- one+, zero+, optional
7. Always use **raw strings** `r"pattern"` for regex

---

## DevOps Connection

| Task | Regex Pattern |
|---|---|
| Find IP addresses in logs | `r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"` |
| Extract error messages | `r"ERROR[:\s]+(.+)"` |
| Validate email input | `r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"` |
| Parse HTTP status codes | `r"\b[1-5]\d{2}\b"` |
| Strip ANSI color codes | `r"\033\[[0-9;]*m"` |
| Find URLs in text | `r"https?://\S+"` |

Tomorrow you will learn `argparse` -- building professional command-line interfaces
for your DevOps tools.
