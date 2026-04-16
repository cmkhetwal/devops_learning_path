# Week 6, Day 6: Practice Day -- 5 Mini-Projects

## What You'll Build

Today you will combine everything from Week 6 into 5 practical mini-projects:

1. **System Info Gatherer** -- collect hostname, OS, disk, memory info
2. **File Organizer** -- sort files into folders by extension
3. **Log Parser with Regex** -- extract errors, IPs, and stats from logs
4. **Disk Space Monitor** -- check disk usage and warn if thresholds exceeded
5. **CLI System Health Checker** -- a complete CLI tool with argparse

Each project uses multiple modules you have learned this week:
`os`, `subprocess`, `shutil`, `pathlib`, `re`, and `argparse`.

---

## Project 1: System Info Gatherer

**Concepts used:** `os`, `subprocess`, `os.path`

Collect and return system information as a dictionary. This is the kind of function
you would use in an inventory script or a monitoring dashboard.

```python
# Expected output example:
{
    "hostname": "web-server-01",
    "username": "deploy",
    "cwd": "/home/deploy/app",
    "python_version": "3.10.12",
    "home_dir": "/home/deploy",
    "os_type": "posix",
    "cpu_count": 4
}
```

---

## Project 2: File Organizer

**Concepts used:** `pathlib`, `shutil`

Take a messy directory full of files and organize them into subdirectories
by file extension. This is useful for organizing download folders, log archives,
or build artifacts.

```
Before:                  After:
  messy/                   messy/
    report.pdf               pdf/report.pdf
    data.csv                 csv/data.csv
    script.py                py/script.py
    photo.jpg                jpg/photo.jpg
    notes.txt                txt/notes.txt
    Makefile                 other/Makefile
```

---

## Project 3: Log Parser with Regex

**Concepts used:** `re`, string manipulation

Parse a realistic log file and extract structured information. This is one of
the most common DevOps tasks -- turning unstructured logs into actionable data.

```python
# Expected output example:
{
    "total_lines": 100,
    "error_count": 5,
    "warning_count": 12,
    "unique_ips": ["10.0.0.1", "192.168.1.10"],
    "error_messages": ["Connection refused", "Timeout exceeded"],
    "status_codes": {"200": 80, "404": 10, "500": 5}
}
```

---

## Project 4: Disk Space Monitor

**Concepts used:** `shutil`, `subprocess`, `os`

Check disk usage and return warnings when thresholds are exceeded. In real DevOps,
this would feed into an alerting system like PagerDuty or Slack notifications.

```python
# Expected output example:
{
    "path": "/",
    "total_gb": 50.0,
    "used_gb": 35.0,
    "free_gb": 15.0,
    "percent_used": 70.0,
    "status": "WARNING"       # OK, WARNING, or CRITICAL
}
```

---

## Project 5: CLI System Health Checker

**Concepts used:** `argparse`, `subprocess`, `os`, `shutil`, `re`

Build a complete CLI tool that combines all the skills from this week. It should
accept command-line arguments to control what checks are run and how results
are displayed.

```
$ python exercise.py --checks disk memory --threshold 80 --verbose
[VERBOSE] Running 2 checks...
[DISK] Usage: 65% - OK
[MEMORY] Usage: 72% - OK
Health Check Complete: 2/2 checks passed
```

---

## Tips for Today

1. **Start simple** -- get the basic functionality working first
2. **Test incrementally** -- run `check.py` after each project
3. **Refer to earlier lessons** -- Days 1-5 lesson files have all the syntax you need
4. **Handle errors gracefully** -- use try/except, check return codes
5. **Think about edge cases** -- what if a directory is empty? What if a command fails?

Good luck! These projects are a preview of real automation work.
