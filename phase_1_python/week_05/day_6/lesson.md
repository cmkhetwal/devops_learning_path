# Week 5, Day 6: Practice Day

## What You'll Do Today

Today is practice day! You will work on 5 mini-projects that combine everything you learned this week:

- **Day 1** - Reading files
- **Day 2** - Writing files and CSV
- **Day 3** - JSON and YAML
- **Day 4** - Error handling
- **Day 5** - Logging

Each mini-project uses multiple skills from the week.

---

## Mini-Project 1: Log File Analyzer

**Skills used:** Reading files, writing files, string processing

Read a log file, count errors and warnings, and write a summary report.

**Key steps:**
1. Read the log file line by line
2. Count lines by level (INFO, WARNING, ERROR, CRITICAL)
3. Collect the actual ERROR and CRITICAL lines
4. Write a summary report to a text file

**Pattern:**
```python
with open("logfile.log", "r") as f:
    for line in f:
        if "ERROR" in line:
            # count it, save it
            pass

with open("summary.txt", "w") as f:
    f.write(f"Total errors: {error_count}\n")
```

---

## Mini-Project 2: Config File Manager

**Skills used:** JSON, error handling, reading/writing files

Build functions that safely read, validate, and update JSON config files.

**Key steps:**
1. Read a JSON config file with proper error handling
2. Validate that required fields exist
3. Update values and write back
4. Handle missing files and invalid JSON gracefully

**Pattern:**
```python
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = default_config
except json.JSONDecodeError:
    print("Invalid config!")
```

---

## Mini-Project 3: CSV Report Generator

**Skills used:** CSV module, writing files, data processing

Generate a CSV report from server data, including computed fields.

**Key steps:**
1. Process a list of server dictionaries
2. Compute additional fields (like status labels)
3. Write the data to a CSV file using DictWriter
4. Read it back and display a summary

**Pattern:**
```python
import csv

with open("report.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
```

---

## Mini-Project 4: Error-Resilient File Processor

**Skills used:** Error handling, file reading, logging

Process multiple files where some may be missing or corrupted. Log every step.

**Key steps:**
1. Iterate over a list of filenames
2. Try to open and process each one
3. Handle missing/corrupt files without crashing
4. Track successes and failures
5. Report results at the end

**Pattern:**
```python
results = {"success": [], "failed": []}
for filename in file_list:
    try:
        data = process_file(filename)
        results["success"].append(filename)
    except Exception as e:
        results["failed"].append((filename, str(e)))
```

---

## Mini-Project 5: Deployment Logger

**Skills used:** Logging module, file handlers, writing files

Simulate a deployment with full logging to both console and file.

**Key steps:**
1. Set up a logger with a FileHandler
2. Simulate deployment steps
3. Log each step at the appropriate level
4. Handle failures with error logging
5. Write a final summary

**Pattern:**
```python
import logging

logger = logging.getLogger("deploy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("deployment.log")
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))
logger.addHandler(handler)

logger.info("Deployment started")
```

---

## Tips for Today

1. **Read the task carefully** before writing code
2. **Use `with` statements** for all file operations
3. **Handle errors** - do not let your code crash on bad input
4. **Test each mini-project** individually before running the checker
5. **Review past lessons** if you get stuck on a specific concept

Good luck! These mini-projects represent the kind of scripts you will write regularly in a DevOps role.
