# Lesson 9: Text Processing

## Why This Matters in DevOps

In DevOps, almost everything is text. Configuration files are text. Log files are text. API
responses are text (JSON, XML, YAML). Command output is text. Monitoring data is text. The
ability to search, filter, transform, and extract information from text is arguably the most
powerful practical skill a DevOps engineer can have. When a production incident occurs and
you need to find the one error message in a 500MB log file from the last hour, text
processing tools are what save you.

Linux provides a suite of text processing tools that have been refined over 50 years. Each
tool does one thing well: `grep` finds patterns, `sed` transforms text, `awk` extracts
structured data, `sort` orders lines, `uniq` removes duplicates, `cut` extracts columns.
Individually, each tool is simple. Combined through pipes, they become a data analysis
powerhouse that can replace hundreds of lines of Python or a dedicated log analysis tool.

The reason these tools matter so much in DevOps specifically is the nature of the data you
work with. A typical web server generates thousands of log lines per minute. Each line
contains an IP address, a timestamp, a request path, an HTTP status code, a response time,
and a user agent. With `awk` and `sort`, you can answer questions like "What are the top 10
IPs hitting our server?" or "How many 500 errors occurred in the last hour?" or "What is the
average response time for the /api/users endpoint?" -- all from the command line, in seconds.

These skills also apply to configuration management. When you need to find which of 200
configuration files contains a specific database hostname, `grep -r` gives you the answer
instantly. When you need to change a port number across all config files, `sed` does it in
one command. When you need to extract a list of all IP addresses allowed in your firewall
rules, `awk` and `grep` together handle it effortlessly.

Text processing is a multiplier for everything else you do. It makes debugging faster,
automation more powerful, and ad-hoc analysis possible. Engineers who master these tools
routinely solve in 30 seconds what others spend 30 minutes writing a Python script to
accomplish. Invest the time to learn them deeply -- the return on investment is enormous.

---

## Core Concepts

### The Text Processing Toolkit

| Tool    | Primary Purpose                    | Key Strength                    |
|---------|------------------------------------|---------------------------------|
| `grep`  | Search for patterns                | Finding needles in haystacks    |
| `sed`   | Stream editing (find and replace)  | Transforming text in-place      |
| `awk`   | Column-based data extraction       | Structured data analysis        |
| `cut`   | Extract columns by delimiter       | Simple column extraction        |
| `sort`  | Sort lines                         | Ordering data                   |
| `uniq`  | Remove/count duplicate lines       | Deduplication and counting      |
| `wc`    | Count lines, words, characters     | Quick statistics                |
| `tr`    | Translate/delete characters        | Character-level transformation  |
| `head`  | Show first N lines                 | Previewing files                |
| `tail`  | Show last N lines (or follow)      | Log monitoring                  |
| `xargs` | Build commands from stdin          | Batch operations                |

### Regular Expression Basics

Regular expressions (regex) are patterns for matching text:

| Pattern  | Meaning                          | Example Match              |
|----------|----------------------------------|----------------------------|
| `.`      | Any single character             | `c.t` matches `cat`, `cot` |
| `*`      | Zero or more of the previous     | `ab*c` matches `ac`, `abc` |
| `+`      | One or more of the previous      | `ab+c` matches `abc`       |
| `^`      | Start of line                    | `^Error` matches lines starting with Error |
| `$`      | End of line                      | `\.conf$` matches lines ending in .conf    |
| `[]`     | Character class                  | `[0-9]` matches any digit  |
| `\|`     | OR (in extended regex)           | `cat\|dog` matches either  |
| `()`     | Grouping (in extended regex)     | `(ab)+` matches `abab`     |

---

## Step-by-Step Practical

### 0. Create Sample Data

```bash
mkdir -p ~/textlab

# Create a sample web server access log
cat > ~/textlab/access.log << 'EOF'
192.168.1.10 - - [16/Apr/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 5432 0.012
192.168.1.20 - - [16/Apr/2026:10:00:02 +0000] "GET /api/users HTTP/1.1" 200 1234 0.045
10.0.0.5 - - [16/Apr/2026:10:00:03 +0000] "POST /api/login HTTP/1.1" 401 98 0.023
192.168.1.10 - - [16/Apr/2026:10:00:04 +0000] "GET /css/style.css HTTP/1.1" 200 8765 0.003
10.0.0.15 - - [16/Apr/2026:10:00:05 +0000] "GET /api/products HTTP/1.1" 500 234 2.456
192.168.1.20 - - [16/Apr/2026:10:00:06 +0000] "GET /api/users HTTP/1.1" 200 1234 0.048
192.168.1.10 - - [16/Apr/2026:10:00:07 +0000] "GET /index.html HTTP/1.1" 200 5432 0.011
10.0.0.5 - - [16/Apr/2026:10:00:08 +0000] "POST /api/login HTTP/1.1" 200 456 0.034
192.168.1.30 - - [16/Apr/2026:10:00:09 +0000] "GET /favicon.ico HTTP/1.1" 404 0 0.001
10.0.0.15 - - [16/Apr/2026:10:00:10 +0000] "GET /api/products HTTP/1.1" 500 234 2.890
192.168.1.10 - - [16/Apr/2026:10:00:11 +0000] "DELETE /api/users/5 HTTP/1.1" 403 87 0.005
192.168.1.20 - - [16/Apr/2026:10:00:12 +0000] "GET /api/users HTTP/1.1" 200 1234 0.042
10.0.0.5 - - [16/Apr/2026:10:00:13 +0000] "POST /api/login HTTP/1.1" 401 98 0.019
192.168.1.40 - - [16/Apr/2026:10:00:14 +0000] "GET /index.html HTTP/1.1" 200 5432 0.015
10.0.0.15 - - [16/Apr/2026:10:00:15 +0000] "GET /api/products HTTP/1.1" 200 1567 0.234
EOF

# Create a sample application log
cat > ~/textlab/app.log << 'EOF'
2026-04-16 10:00:01 INFO  [main] Application starting
2026-04-16 10:00:02 INFO  [main] Loading configuration from /etc/myapp/config.yml
2026-04-16 10:00:02 WARN  [config] Deprecated setting 'legacy_mode' detected
2026-04-16 10:00:03 INFO  [db] Connecting to database at 10.0.1.50:5432
2026-04-16 10:00:03 INFO  [db] Connection established (pool size: 10)
2026-04-16 10:00:05 ERROR [auth] Failed login attempt for user 'admin' from 203.0.113.50
2026-04-16 10:00:06 INFO  [http] Server listening on port 8080
2026-04-16 10:00:10 WARN  [http] Slow response: /api/products took 2456ms
2026-04-16 10:00:15 ERROR [db] Query timeout after 5000ms: SELECT * FROM products WHERE category='electronics'
2026-04-16 10:00:16 ERROR [http] 500 Internal Server Error: /api/products
2026-04-16 10:00:20 INFO  [health] Health check passed (memory: 67%, cpu: 23%)
2026-04-16 10:00:25 WARN  [auth] Multiple failed login attempts from 203.0.113.50
2026-04-16 10:00:30 ERROR [db] Connection pool exhausted (10/10 connections in use)
2026-04-16 10:00:31 INFO  [db] Expanding connection pool to 15
2026-04-16 10:00:35 INFO  [health] Health check passed (memory: 72%, cpu: 31%)
EOF
```

### 1. grep -- Pattern Matching

Find all errors in the application log:

```bash
grep "ERROR" ~/textlab/app.log
```

Expected output:
```
2026-04-16 10:00:05 ERROR [auth] Failed login attempt for user 'admin' from 203.0.113.50
2026-04-16 10:00:15 ERROR [db] Query timeout after 5000ms: SELECT * FROM products
2026-04-16 10:00:16 ERROR [http] 500 Internal Server Error: /api/products
2026-04-16 10:00:30 ERROR [db] Connection pool exhausted (10/10 connections in use)
```

Count errors:

```bash
grep -c "ERROR" ~/textlab/app.log
```

Expected output: `4`

Case-insensitive search:

```bash
grep -i "error\|warn" ~/textlab/app.log
```

Show line numbers:

```bash
grep -n "ERROR" ~/textlab/app.log
```

Show context (2 lines before and after each match):

```bash
grep -C 2 "Connection pool exhausted" ~/textlab/app.log
```

Search recursively in a directory:

```bash
grep -r "ERROR" ~/textlab/
```

Find lines that do NOT match a pattern:

```bash
grep -v "INFO" ~/textlab/app.log
```

### 2. sed -- Stream Editing

Replace text (display only, does not modify the file):

```bash
sed 's/ERROR/CRITICAL/' ~/textlab/app.log
```

Replace text in-place (modifies the file):

```bash
cp ~/textlab/app.log ~/textlab/app.log.bak
sed -i 's/8080/9090/g' ~/textlab/app.log
grep "port" ~/textlab/app.log
```

Delete lines matching a pattern:

```bash
sed '/INFO/d' ~/textlab/app.log.bak
```

Print only specific lines:

```bash
sed -n '5,10p' ~/textlab/app.log.bak
```

Insert text before a matching line:

```bash
sed '/Server listening/i\# --- Server startup complete ---' ~/textlab/app.log.bak
```

Extract text between two patterns:

```bash
sed -n '/Application starting/,/Server listening/p' ~/textlab/app.log.bak
```

### 3. awk -- Data Extraction

Print specific columns from the access log:

```bash
awk '{print $1, $9}' ~/textlab/access.log
```

Expected output:
```
192.168.1.10 200
192.168.1.20 200
10.0.0.5 401
192.168.1.10 200
10.0.0.15 500
...
```

Count requests per IP address:

```bash
awk '{print $1}' ~/textlab/access.log | sort | uniq -c | sort -rn
```

Expected output:
```
      4 192.168.1.10
      3 192.168.1.20
      3 10.0.0.5
      3 10.0.0.15
      1 192.168.1.40
      1 192.168.1.30
```

Filter by status code (show only 500 errors):

```bash
awk '$9 == 500 {print $1, $7, $NF}' ~/textlab/access.log
```

Expected output:
```
10.0.0.15 /api/products 2.456
10.0.0.15 /api/products 2.890
```

Calculate average response time:

```bash
awk '{sum += $NF; count++} END {printf "Average response time: %.3f seconds\n", sum/count}' ~/textlab/access.log
```

Expected output:
```
Average response time: 0.389 seconds
```

Count requests by status code:

```bash
awk '{count[$9]++} END {for (code in count) print code, count[code]}' ~/textlab/access.log | sort
```

Expected output:
```
200 9
401 2
403 1
404 1
500 2
```

### 4. cut, sort, uniq, wc, tr

Extract the request paths from the access log:

```bash
cut -d'"' -f2 ~/textlab/access.log | cut -d' ' -f2 | sort | uniq -c | sort -rn
```

Expected output:
```
      3 /api/users
      3 /api/products
      3 /index.html
      2 /api/login
      1 /favicon.ico
      1 /css/style.css
      1 /api/users/5
      1 /api/login
```

Count lines, words, and characters:

```bash
wc ~/textlab/access.log
```

Expected output:
```
 15  195 1395 /home/ubuntu/textlab/access.log
```

Translate characters (convert to uppercase):

```bash
echo "hello world" | tr 'a-z' 'A-Z'
```

Expected output: `HELLO WORLD`

Delete specific characters:

```bash
echo "phone: (555) 123-4567" | tr -d '()-'
```

Expected output: `phone:  555 1234567`

### 5. head, tail, and Log Monitoring

Show the first 5 lines:

```bash
head -5 ~/textlab/access.log
```

Show the last 3 lines:

```bash
tail -3 ~/textlab/app.log.bak
```

Follow a log file in real time (press Ctrl+C to stop):

```bash
# In a real scenario:
# tail -f /var/log/syslog

# Simulated:
tail -f ~/textlab/app.log.bak &
echo "2026-04-16 10:01:00 INFO  [test] New log entry" >> ~/textlab/app.log.bak
sleep 1
kill %1 2>/dev/null
```

### 6. xargs -- Building Commands from Input

Find and delete all `.bak` files:

```bash
find ~/textlab -name "*.bak" | xargs ls -la
```

Process items in parallel:

```bash
echo -e "google.com\ngithub.com\n8.8.8.8" | xargs -I{} -P3 ping -c 1 -W 1 {} 2>/dev/null | grep "bytes from"
```

### 7. Real-World Log Analysis Scenario

Combine everything to analyze a production incident:

```bash
echo "=== Incident Analysis Report ==="
echo ""

echo "1. Error Summary:"
grep -c "ERROR" ~/textlab/app.log.bak
echo "   errors found in application log"

echo ""
echo "2. Errors by Component:"
grep "ERROR" ~/textlab/app.log.bak | awk -F'[][]' '{print $2}' | sort | uniq -c | sort -rn

echo ""
echo "3. HTTP 500 Errors by Source IP:"
awk '$9 == 500 {print $1}' ~/textlab/access.log | sort | uniq -c | sort -rn

echo ""
echo "4. Top Requested URLs:"
awk '{print $7}' ~/textlab/access.log | sort | uniq -c | sort -rn | head -5

echo ""
echo "5. Slowest Requests (>1 second):"
awk '$NF > 1.0 {printf "  %s %s - %.3fs\n", $1, $7, $NF}' ~/textlab/access.log
```

---

## Exercises

1. **Log Forensics**: Using the sample access log, answer these questions with one-line
   commands: (a) How many unique IP addresses accessed the server? (b) Which IP made the
   most requests? (c) What percentage of requests resulted in errors (status >= 400)?

2. **sed Transformation**: Using `sed`, write commands to: (a) Replace all IP addresses in
   the access log with `[REDACTED]`. (b) Delete all lines containing "favicon". (c) Add a
   `#` comment prefix to every line containing "WARN" in the app log.

3. **awk Report**: Write an `awk` command that reads the access log and produces a summary
   table showing: status code, count, and percentage of total requests. Format it as a
   proper table with headers.

4. **Pipeline Challenge**: Write a single pipeline that extracts all unique IP addresses
   from the access log, performs a reverse DNS lookup on each (`host IP_ADDRESS`), and saves
   the results to a file.

5. **Configuration Extraction**: Create a sample Nginx configuration file and use `grep`,
   `awk`, and `sed` to extract: (a) all `server_name` directives, (b) all `listen` ports,
   (c) all `location` blocks.

---

## Knowledge Check

**Q1: What is the difference between `grep "pattern" file` and `grep -E "pattern" file`?**

A1: Regular `grep` uses Basic Regular Expressions (BRE), where metacharacters like `+`,
`?`, `|`, and `()` must be escaped with backslashes to have special meaning. `grep -E`
(extended grep, equivalent to `egrep`) uses Extended Regular Expressions (ERE), where these
characters have special meaning without escaping. Use `-E` when your patterns use
alternation (`|`), one-or-more (`+`), or grouping (`()`).

**Q2: How would you find the top 10 most frequently occurring IP addresses in a log file?**

A2: `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10`. This pipeline:
extracts the first column (IP), sorts alphabetically (required for `uniq`), counts
consecutive identical lines, sorts numerically in reverse (highest count first), and shows
the top 10. This is one of the most commonly used pipelines in DevOps.

**Q3: What does `sed -i 's/old/new/g' file` do, and what does each part mean?**

A3: `sed` is the stream editor. `-i` means edit in-place (modify the actual file). `s` is
the substitution command. `old` is the pattern to find. `new` is the replacement. `g` means
global -- replace ALL occurrences on each line, not just the first. Without `g`, only the
first occurrence on each line is replaced. Without `-i`, the changes are displayed but the
file is not modified.

**Q4: Why must you `sort` before using `uniq`?**

A4: `uniq` only removes consecutive duplicate lines. If identical lines are scattered
throughout the file, `uniq` will not detect them as duplicates. `sort` groups identical
lines together, making them consecutive, so that `uniq` can properly detect and count them.
The `sort | uniq -c` pipeline is so common it is worth memorizing.

**Q5: How would you monitor a log file for errors in real time and trigger an alert?**

A5: Use `tail -f /var/log/app.log | grep --line-buffered "ERROR"`. The `tail -f` follows
the file as new lines are added, and `grep --line-buffered` ensures each matching line is
output immediately rather than buffered. To trigger an action, pipe to a while-read loop:
`tail -f logfile | grep --line-buffered "ERROR" | while read line; do echo "$line" |
mail -s "Alert" admin@company.com; done`.
