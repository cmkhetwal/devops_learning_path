"""
Week 5, Day 7: Quiz - Code Completion
======================================

Complete the 10 code snippets below. Each one has a missing piece
marked with # YOUR CODE HERE. Fill in the correct code.

Run check.py when finished to see your score.
"""

import json
import csv
import logging
import os

# === Cleanup ===
for f in ["quiz_output.txt", "quiz_data.csv", "quiz_config.json",
          "quiz_append.txt", "quiz.log"]:
    if os.path.exists(f):
        os.remove(f)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


# ============================================
# QUESTION 1: Read a file and count lines
# ============================================
# Create a sample file, then read it and count lines.

with open("quiz_output.txt", "w") as f:
    f.write("line one\nline two\nline three\nline four\nline five\n")

# Fill in the blank to read the file and count lines
with open("quiz_output.txt", "r") as f:
    # YOUR CODE HERE - read all lines into a list
    q1_lines = None

q1_answer = len(q1_lines) if q1_lines else 0


# ============================================
# QUESTION 2: Write to a file
# ============================================
# Fill in the blank to write "Hello DevOps" to quiz_output.txt

# YOUR CODE HERE - open file in write mode and write the text
# The file should contain exactly: "Hello DevOps\n"

q2_answer = None
if os.path.exists("quiz_output.txt"):
    with open("quiz_output.txt", "r") as f:
        q2_answer = f.read()


# ============================================
# QUESTION 3: Append to a file
# ============================================
# quiz_output.txt currently has "Hello DevOps\n" from Q2.
# Append "Welcome to Python\n" to it WITHOUT erasing the existing content.

# YOUR CODE HERE - open in append mode and write the new line

q3_answer = None
if os.path.exists("quiz_output.txt"):
    with open("quiz_output.txt", "r") as f:
        q3_answer = f.read()


# ============================================
# QUESTION 4: Parse a JSON string
# ============================================
# Fill in the blank to parse this JSON string into a Python dict.

json_text = '{"hostname": "web-01", "port": 8080, "active": true}'

# YOUR CODE HERE - parse json_text into a dictionary
q4_data = None

q4_answer = q4_data["hostname"] if q4_data else None


# ============================================
# QUESTION 5: Write JSON to a file
# ============================================
# Fill in the blank to write this dictionary to a JSON file.

config = {"server": "db-01", "port": 5432, "ssl": True}

# YOUR CODE HERE - write config to "quiz_config.json" with indent=2

q5_answer = False
if os.path.exists("quiz_config.json"):
    with open("quiz_config.json", "r") as f:
        try:
            loaded = json.load(f)
            q5_answer = loaded == config
        except:
            q5_answer = False


# ============================================
# QUESTION 6: Write a CSV file
# ============================================
# Fill in the blanks to write a CSV file with a header and data rows.

rows = [
    ["name", "role", "status"],
    ["web-01", "frontend", "online"],
    ["db-01", "database", "online"],
]

# YOUR CODE HERE - write all rows to "quiz_data.csv" using csv.writer
# Remember to use newline=""

q6_answer = False
if os.path.exists("quiz_data.csv"):
    with open("quiz_data.csv", "r", newline="") as f:
        reader = csv.reader(f)
        q6_data = list(reader)
        q6_answer = q6_data == rows


# ============================================
# QUESTION 7: Handle a missing file
# ============================================
# Fill in the blank to handle the FileNotFoundError.
# If the file is not found, set q7_answer to "not_found".
# If the file is found, set q7_answer to the file contents.

q7_answer = None

# YOUR CODE HERE - use try/except to read "nonexistent_file_xyz.txt"
# Set q7_answer to "not_found" if FileNotFoundError occurs
# Set q7_answer to the file contents (stripped) if it exists


# ============================================
# QUESTION 8: Custom exception
# ============================================
# Fill in the blank to create a custom exception class called
# PortError that inherits from Exception.
# Then fill in the function to raise PortError if port is out of range.

# YOUR CODE HERE - define PortError class


def check_port(port):
    # YOUR CODE HERE - raise PortError if port < 1 or port > 65535
    # The error message should be "Invalid port: {port}"
    # If valid, return True
    pass

q8_answer = None
try:
    check_port(80)
    check_port(99999)
    q8_answer = "no_error"
except PortError as e:
    q8_answer = str(e)
except NameError:
    q8_answer = "PortError not defined"


# ============================================
# QUESTION 9: try/except/else/finally
# ============================================
# Fill in the blanks. The function should:
# - Try to convert value to an integer
# - In except: set result to -1
# - In else: set result to the converted integer
# - In finally: set q9_finally to True

q9_finally = False

def safe_int(value):
    global q9_finally
    # YOUR CODE HERE - complete the try/except/else/finally
    result = None
    return result

q9_valid = safe_int("42")
q9_invalid = safe_int("not_a_number")
q9_answer = (q9_valid, q9_invalid, q9_finally)


# ============================================
# QUESTION 10: Set up logging to a file
# ============================================
# Fill in the blanks to configure logging that writes to "quiz.log"
# with level INFO and format "%(levelname)s: %(message)s".
# Then log one INFO and one ERROR message.

# YOUR CODE HERE - configure basicConfig to write to quiz.log
# Then log: "Quiz started" at INFO level
# Then log: "Something went wrong" at ERROR level

q10_answer = False
if os.path.exists("quiz.log"):
    with open("quiz.log", "r") as f:
        content = f.read()
        q10_answer = "INFO" in content and "ERROR" in content


# === Display Results ===
print("=" * 50)
print("QUIZ ANSWERS")
print("=" * 50)
print(f"Q1  - Line count: {q1_answer}")
print(f"Q2  - File write: {q2_answer!r}")
print(f"Q3  - File append: {q3_answer!r}")
print(f"Q4  - JSON parse: {q4_answer}")
print(f"Q5  - JSON write: {q5_answer}")
print(f"Q6  - CSV write: {q6_answer}")
print(f"Q7  - Error handling: {q7_answer}")
print(f"Q8  - Custom exception: {q8_answer}")
print(f"Q9  - try/except/else/finally: {q9_answer}")
print(f"Q10 - Logging: {q10_answer}")
