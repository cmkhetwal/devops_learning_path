# 10 - Text Processing: grep, sed, awk & More
## Filtering, Pattern Matching, Log Analysis

---

## SECTION 1: grep (Global Regular Expression Print)

### 1.1 Basic grep
```bash
# Search for pattern in file
grep "error" /var/log/syslog
grep "ERROR" /var/log/application.log

# Case insensitive
grep -i "error" /var/log/syslog              # -i = ignore case

# Recursive search in directory
grep -r "password" /etc/                # -r = recursive search through directories
grep -rn "password" /etc/               # -n = show line numbers
grep -rl "password" /etc/               # -l = list only filenames with matches

# Invert match (lines NOT containing)
grep -v "INFO" /var/log/app.log          # -v = invert match (exclude matching lines)
grep -v "^#" /etc/nginx/nginx.conf       # Exclude comments
grep -v "^$" config.conf                 # Exclude empty lines
grep -v "^#\|^$" config.conf             # Exclude both

# Count matches
grep -c "error" /var/log/syslog              # -c = count matching lines

# Show only matching part
grep -o "error[^ ]*" /var/log/syslog        # -o = print only the matched portion

# Context (lines around match)
grep -B 3 "error" log.txt               # -B N = show N lines Before each match
grep -A 3 "error" log.txt               # -A N = show N lines After each match
grep -C 3 "error" log.txt               # -C N = show N lines of Context (before + after)

# Multiple patterns
grep -E "error|warning|critical" /var/log/syslog   # -E = extended regex (enables | for OR)
grep -e "error" -e "warning" /var/log/syslog       # -e = specify multiple patterns

# Fixed strings (no regex, faster for literal search)
grep -F "192.168.1.100" /var/log/access.log        # -F = treat pattern as fixed string, not regex

# Word boundary (match whole word only)
grep -w "error" log.txt                  # -w = match whole words only (not "errors")
```

### 1.2 grep with Regex
```bash
# Basic regex
grep "^root" /etc/passwd                 # Lines starting with "root"
grep "bash$" /etc/passwd                 # Lines ending with "bash"
grep "^$" config.txt                     # Empty lines
grep "^[A-Z]" file.txt                   # Lines starting with uppercase

# Extended regex (-E or egrep)
grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" access.log   # IP addresses
grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}" log.txt                          # Date YYYY-MM-DD
grep -E "(error|fail|critical)" /var/log/syslog                         # OR pattern
grep -E "status=[4-5][0-9]{2}" access.log                              # 4xx and 5xx status

# Perl-compatible regex (-P)
grep -P "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" access.log   # -P = Perl-compatible regex (\d, lookahead, etc.)
grep -P "(?<=status=)\d+" log.txt                            # Lookahead/behind
grep -oP '(?<=src=)\S+' firewall.log                         # -o -P = extract only matched text using Perl regex
```

### 1.3 Practical grep Examples
```bash
# Find failed SSH logins
grep "Failed password" /var/log/secure | tail -20
grep "Failed password" /var/log/secure | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn

# Find specific HTTP errors in Nginx
grep " 500 " /var/log/nginx/access.log | tail -20
grep -E " (500|502|503|504) " /var/log/nginx/access.log | wc -l

# Find errors in last hour
grep "$(date '+%d/%b/%Y:%H' -d '1 hour ago')" /var/log/nginx/access.log | grep " 500 "

# Search for config values
grep -rn "listen" /etc/nginx/                # Find all listen directives
grep -rn "server_name" /etc/nginx/conf.d/

# Find large log entries
grep -c "" /var/log/syslog                   # Total line count
grep "error" /var/log/syslog | wc -l         # Error count

# Find processes
ps aux | grep "[n]ginx"                      # [n] trick avoids matching grep itself

# Search compressed logs
zgrep "error" /var/log/syslog.*.gz       # zgrep = grep through gzip-compressed files
zcat /var/log/syslog.1.gz | grep "error"
```

---

## SECTION 2: sed (Stream Editor)

### 2.1 Basic sed Operations
```bash
# Substitute (replace) first occurrence per line
sed 's/old/new/' file.txt

# Substitute all occurrences per line
sed 's/old/new/g' file.txt               # g = global (replace all matches on the line, not just first)

# Substitute in-place (modify file)
sed -i 's/old/new/g' file.txt            # -i = edit file in-place (no backup)

# Substitute with backup
sed -i.bak 's/old/new/g' file.txt       # -i.bak = edit in-place, saving original as file.txt.bak

# Case insensitive substitution
sed 's/error/ERROR/gi' file.txt          # g = global, i = case-insensitive match

# Delete lines
sed '/pattern/d' file.txt                # Delete lines matching pattern
sed '/^#/d' config.conf                  # Delete comments
sed '/^$/d' config.conf                  # Delete empty lines
sed '/^#/d; /^$/d' config.conf           # Delete both
sed '1,5d' file.txt                      # Delete lines 1-5
sed '$d' file.txt                        # Delete last line

# Print specific lines
sed -n '5p' file.txt                     # -n = suppress auto-print, p = print matched line
sed -n '5,10p' file.txt                  # Print lines 5-10
sed -n '/error/p' file.txt              # Print matching lines (like grep)

# Insert/Append
sed '3i\New line before line 3' file.txt  # Insert before line 3
sed '3a\New line after line 3' file.txt   # Append after line 3
sed '/pattern/i\Insert before match' file.txt
sed '/pattern/a\Append after match' file.txt

# Multiple operations
sed -e 's/foo/bar/g' -e 's/baz/qux/g' file.txt   # -e = add a sed expression (chain multiple edits)
sed 's/foo/bar/g; s/baz/qux/g' file.txt
```

### 2.2 Practical sed Examples
```bash
# Change SSH port
sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config
sed -i 's/^Port 22/Port 2222/' /etc/ssh/sshd_config

# Uncomment a line
sed -i 's/^#\(PermitRootLogin\)/\1/' /etc/ssh/sshd_config

# Comment a line
sed -i 's/^\(PermitRootLogin\)/#\1/' /etc/ssh/sshd_config

# Change value in config
sed -i 's/^worker_processes.*/worker_processes auto;/' /etc/nginx/nginx.conf

# Add line after match
sed -i '/\[mysqld\]/a\max_connections = 500' /etc/my.cnf

# Replace IP address
sed -i 's/192\.168\.1\.10/10.0.0.10/g' /etc/nginx/conf.d/app.conf

# Remove trailing whitespace
sed -i 's/[[:space:]]*$//' file.txt

# Extract between two patterns
sed -n '/START/,/END/p' file.txt

# Print config without comments and empty lines
sed '/^#/d; /^$/d; /^;/d' /etc/php.ini

# Replace in multiple files
sed -i 's/old-server/new-server/g' /etc/nginx/conf.d/*.conf

# Add prefix to lines
sed 's/^/PREFIX: /' file.txt

# Extract email addresses
sed -n 's/.*\([a-zA-Z0-9._-]*@[a-zA-Z0-9._-]*\).*/\1/p' file.txt
```

---

## SECTION 3: awk (Pattern Scanning & Processing)

### 3.1 Basic awk
```bash
# Print specific columns (space/tab separated)
# $1, $2... = field by position, $NF = last field, NR = current line number, NF = number of fields
awk '{print $1}' file.txt               # First column
awk '{print $1, $3}' file.txt           # First and third columns
awk '{print $NF}' file.txt              # Last column ($NF = last field)
awk '{print $(NF-1)}' file.txt          # Second to last

# Custom field separator
awk -F: '{print $1, $7}' /etc/passwd     # -F = field separator (here : instead of whitespace)
awk -F, '{print $2}' data.csv            # Second column of CSV
awk -F'[ :]+' '{print $1}' file.txt      # Multiple delimiters

# Print with formatting
awk '{printf "%-20s %s\n", $1, $2}' file.txt   # Formatted output
awk -F: '{printf "User: %-15s Shell: %s\n", $1, $7}' /etc/passwd

# Pattern matching (only print matching lines)
awk '/error/' file.txt                    # Lines containing "error"
awk '!/comment/' file.txt                 # Lines NOT containing "comment"
awk '/^root/' /etc/passwd                 # Lines starting with "root"

# Conditional
awk '$3 > 1000' /etc/passwd              # 3rd field > 1000 (by default separator)
awk -F: '$3 >= 1000 {print $1}' /etc/passwd  # Users with UID >= 1000
awk '$9 == 500 {print $0}' access.log    # Lines where 9th field is 500

# Built-in variables
# NR = line Number of Record
# NF = Number of Fields
# $0 = entire line
# FS = Field Separator
# OFS = Output Field Separator
awk '{print NR, $0}' file.txt            # Add line numbers
awk 'NR >= 10 && NR <= 20' file.txt      # Print lines 10-20
awk 'END {print NR}' file.txt            # Total line count
```

### 3.2 awk Aggregation & Math
```bash
# Sum a column
awk '{sum += $1} END {print sum}' file.txt

# Average
awk '{sum += $1; count++} END {print sum/count}' file.txt

# Min/Max
awk 'NR==1 || $1 > max {max=$1} END {print max}' file.txt
awk 'NR==1 || $1 < min {min=$1} END {print min}' file.txt

# Count occurrences (like sort | uniq -c)
awk '{count[$1]++} END {for (i in count) print count[i], i}' file.txt | sort -rn

# Sum by group
awk '{sum[$1] += $2} END {for (i in sum) print i, sum[i]}' file.txt

# Calculate percentages
awk '{count[$1]++; total++} END {for (i in count) printf "%s: %.1f%%\n", i, count[i]/total*100}' file.txt
```

### 3.3 Practical awk Examples
```bash
# Top IPs from Nginx access log
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Requests per second
awk '{print $4}' /var/log/nginx/access.log | cut -d: -f1-3 | sort | uniq -c | sort -rn | head -20

# HTTP status code distribution
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Average response time (last field is response time)
awk '{sum += $NF; count++} END {printf "Average: %.3f seconds\n", sum/count}' /var/log/nginx/access.log

# Bandwidth per IP
awk '{bytes[$1] += $10} END {for (ip in bytes) printf "%s\t%.2f MB\n", ip, bytes[ip]/1024/1024}' /var/log/nginx/access.log | sort -t$'\t' -k2 -rn | head -20

# Find URLs returning 500
awk '$9 == 500 {print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Memory usage per process (from ps)
ps -eo comm,rss --no-headers | awk '{mem[$1] += $2} END {for (p in mem) printf "%-20s %d MB\n", p, mem[p]/1024}' | sort -k2 -rn | head -20

# Disk usage report
df -h | awk 'NR>1 {print $5, $6}' | sort -rn

# Parse /etc/passwd - list users with bash shell
awk -F: '$7 ~ /bash/ {print $1}' /etc/passwd

# Connections per state from ss
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn

# Find slow queries in MySQL slow log
awk '/Query_time/{print $0}' /var/log/mysql/slow.log | sort -k3 -rn | head -10
```

---

## SECTION 4: Powerful Combinations

### 4.1 Pipeline Recipes
```bash
# Find top 10 error-producing IPs
grep " 500 " /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# Real-time error rate monitoring
tail -f /var/log/nginx/access.log | awk '$9 >= 500 {print strftime("%H:%M:%S"), $1, $9, $7}'

# Extract unique error messages
grep -i "error" /var/log/syslog | sed 's/.*]: //' | sort -u

# Find config differences between servers
diff <(ssh server1 "cat /etc/nginx/nginx.conf") <(ssh server2 "cat /etc/nginx/nginx.conf")

# Process log and create report
awk '{
    status[$9]++
    total++
    if ($9 >= 500) errors++
    bytes += $10
}
END {
    printf "Total Requests: %d\n", total
    printf "5xx Errors: %d (%.2f%%)\n", errors, errors/total*100
    printf "Total Bandwidth: %.2f GB\n", bytes/1024/1024/1024
    printf "\nStatus Code Breakdown:\n"
    for (s in status) printf "  %s: %d\n", s, status[s]
}' /var/log/nginx/access.log

# Extract and sort by timestamp
grep "error" /var/log/app.log | awk -F'[][]' '{print $2}' | sort | tail -20

# Monitor file changes in real-time
tail -f /var/log/syslog | grep --line-buffered "error" | while read line; do
    echo "$(date '+%H:%M:%S') ALERT: $line"
done

# CSV to formatted table
awk -F, '{printf "%-15s %-10s %-20s\n", $1, $2, $3}' data.csv

# Replace field in specific column
awk -F: 'BEGIN{OFS=":"} $7=="/bin/bash" {$7="/bin/zsh"} {print}' /etc/passwd
```

### 4.2 Other Useful Tools
```bash
# cut - Extract columns
cut -d: -f1,7 /etc/passwd               # -d = delimiter, -f = field numbers to extract
cut -c1-10 file.txt                      # -c = character positions to extract

# tr - Translate/delete characters (translates SET1 chars to SET2 chars)
echo "HELLO" | tr 'A-Z' 'a-z'           # Translate uppercase to lowercase
echo "hello world" | tr ' ' '\n'         # Replace spaces with newlines
echo "extra   spaces" | tr -s ' '        # -s = squeeze repeated characters into one
cat file.txt | tr -d '\r'                # -d = delete specified characters

# sort - Sort lines
sort file.txt                             # Alphabetical
sort -n file.txt                          # -n = numeric sort (2 before 10)
sort -rn file.txt                         # -r = reverse order, -n = numeric
sort -t: -k3 -n /etc/passwd              # -t = delimiter, -k = sort by field number
sort -u file.txt                          # -u = unique (remove duplicate lines)
sort -h file.txt                          # -h = human-readable numbers (1K, 2M, 3G)

# uniq - Unique lines (requires sorted input)
sort file.txt | uniq                      # Remove duplicates
sort file.txt | uniq -c                   # -c = prefix lines with occurrence count
sort file.txt | uniq -d                   # -d = show only duplicate lines
sort file.txt | uniq -u                   # -u = show only lines that appear once

# wc - Word count
wc -l file.txt                            # -l = count lines
wc -w file.txt                            # -w = count words
wc -c file.txt                            # -c = count bytes

# tee - Write to file AND stdout
command | tee output.log                  # Write and display
command | tee -a output.log               # -a = append to file instead of overwriting

# xargs - Build commands from stdin
find /tmp -name "*.log" -mtime +7 | xargs rm -f
cat servers.txt | xargs -I {} ssh {} "uptime"    # -I {} = replace {} with each input line
cat urls.txt | xargs -n1 -P4 curl -s     # -n1 = one arg per command, -P4 = 4 parallel processes

# column - Format into columns
mount | column -t                         # -t = auto-detect columns and align into table
cat /etc/passwd | column -t -s:           # -s = specify input delimiter

# jq - JSON processing (lightweight command-line JSON processor)
curl -s api.example.com/data | jq '.'                    # '.' = pretty-print entire JSON
curl -s api.example.com/data | jq '.results[].name'      # Extract 'name' from each item in 'results' array
curl -s api.example.com/data | jq '.results | length'    # Count results
```
