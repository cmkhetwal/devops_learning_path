"""
Week 6, Day 4: Exercise - Regular Expressions

THEME: Log Parsing and Input Validation

You are building log analysis and validation tools that a DevOps
engineer would use daily. Each function uses regex to parse or
validate text data.

Complete all 5 tasks below.
"""

import re


# TASK 1: Write a function that takes a string of log text and returns
#         a list of all unique IPv4 addresses found in it.
#
# Example:
#   text = "Request from 192.168.1.10 forwarded to 10.0.0.5, reply to 192.168.1.10"
#   extract_ips(text) -> ["10.0.0.5", "192.168.1.10"]
#
# Requirements:
#   - Use re.findall() with an appropriate IP pattern
#   - Return only unique IPs (no duplicates)
#   - Return the list sorted in alphabetical order
#   - IP pattern: one to three digits, dot, repeated 4 times
#
# Hint: Pattern for IPv4: r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
#       Use set() to remove duplicates, then sorted() to sort.

def extract_ips(text):
    # YOUR CODE HERE
    pass


# TASK 2: Write a function that takes a string and returns True if it
#         is a valid email address, False otherwise.
#
# Rules for valid email (simplified):
#   - Has exactly one @ symbol
#   - Before @: one or more word characters, dots, hyphens, or plus signs
#   - After @: one or more word characters, dots, or hyphens
#   - Ends with a dot followed by 2 or more letters (e.g., .com, .io, .co.uk)
#   - The ENTIRE string must be the email (no extra text before/after)
#
# Valid:   "admin@server.com", "dev.ops@company.io", "user+tag@mail.co.uk"
# Invalid: "no-at-sign.com", "@missing.com", "user@", "user @space.com"
#
# Hint: Use re.match() with ^ and $ anchors, or re.fullmatch()
# Pattern: r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

def is_valid_email(text):
    # YOUR CODE HERE
    pass


# TASK 3: Write a function that takes a multi-line log string and returns
#         a list of dictionaries, one per ERROR line found.
#
# Log format:
#   "2024-01-15 10:30:45 ERROR [module_name] Error message here"
#
# Each dictionary should contain:
#   "timestamp" -> "2024-01-15 10:30:45"
#   "module"    -> "module_name"
#   "message"   -> "Error message here"
#
# Requirements:
#   - Only extract lines that contain "ERROR" (not WARNING, INFO, etc.)
#   - Use re.findall() with groups to extract the parts
#   - Return a list of dicts (empty list if no errors found)
#
# Hint: Pattern with groups:
#   r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ERROR \[(\w+)\] (.+)"

def parse_error_logs(log_text):
    # YOUR CODE HERE
    pass


# TASK 4: Write a function that takes a text string and masks all
#         sensitive data in it.
#
# Mask the following:
#   - IP addresses: replace with "X.X.X.X"
#   - Email addresses: replace with "***@***.***"
#   - Numbers with 10+ digits (like phone/account numbers): replace with "**REDACTED**"
#
# Apply masks in this order: emails first, then IPs, then long numbers.
#
# Example:
#   "Contact admin@server.com from 192.168.1.1 ref 1234567890"
#   -> "Contact ***@***.*** from X.X.X.X ref **REDACTED**"
#
# Hint: Use re.sub() three times in sequence.
#   - Email pattern: r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
#   - IP pattern: r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
#   - Long number pattern: r"\b\d{10,}\b"

def mask_sensitive_data(text):
    # YOUR CODE HERE
    pass


# TASK 5: Write a function that takes a log string from an HTTP access
#         log and extracts structured data from it.
#
# Log format (common Apache/Nginx format):
#   '192.168.1.10 - - [15/Jan/2024:10:30:45 +0000] "GET /api/users HTTP/1.1" 200 1234'
#
# Extract and return a dictionary:
#   "ip"      -> "192.168.1.10"
#   "date"    -> "15/Jan/2024:10:30:45 +0000"
#   "method"  -> "GET"
#   "path"    -> "/api/users"
#   "status"  -> "200"      (as a string)
#   "size"    -> "1234"     (as a string)
#
# If the line doesn't match the pattern, return an empty dict {}.
#
# Hint: Build a pattern with groups for each part:
#   r'(\S+) - - \[(.+?)\] "(\S+) (\S+) \S+" (\d{3}) (\d+)'

def parse_access_log(log_line):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    print("=== Task 1: Extract IPs ===")
    sample = "Failed login from 192.168.1.10, blocked 10.0.0.5, retry from 192.168.1.10"
    ips = extract_ips(sample)
    print(f"  IPs found: {ips}")

    print("\n=== Task 2: Validate Email ===")
    emails = ["admin@server.com", "bad@", "user@host.io", "not an email", "a@b.c"]
    for e in emails:
        result = is_valid_email(e)
        print(f"  {e:25s} -> {'valid' if result else 'invalid'}")

    print("\n=== Task 3: Parse Error Logs ===")
    logs = """2024-01-15 10:30:45 INFO [app] Started successfully
2024-01-15 10:31:00 ERROR [auth] Invalid token for user admin
2024-01-15 10:31:05 WARNING [disk] Space below 20%
2024-01-15 10:31:10 ERROR [db] Connection timeout after 30s"""
    errors = parse_error_logs(logs)
    if errors:
        for err in errors:
            print(f"  [{err.get('timestamp')}] {err.get('module')}: {err.get('message')}")

    print("\n=== Task 4: Mask Sensitive Data ===")
    text = "User admin@company.com logged in from 10.0.0.5, account 9876543210"
    masked = mask_sensitive_data(text)
    print(f"  Original: {text}")
    print(f"  Masked:   {masked}")

    print("\n=== Task 5: Parse Access Log ===")
    line = '172.16.0.1 - - [15/Jan/2024:10:30:45 +0000] "POST /api/login HTTP/1.1" 401 52'
    parsed = parse_access_log(line)
    if parsed:
        for k, v in parsed.items():
            print(f"  {k}: {v}")
