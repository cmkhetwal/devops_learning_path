# Lesson 8: Advanced Bash Scripting

## Why This Matters in DevOps

The difference between a script that works on your laptop and a script that runs reliably in
production at 3 AM is error handling. Basic Bash scripts assume everything will go right:
the file exists, the command succeeds, the network is available, the disk has space. Advanced
Bash scripting is about assuming everything will go wrong and building scripts that handle
failure gracefully. In production, Murphy's Law is not a joke -- it is a design requirement.

Production-quality scripts are the backbone of DevOps automation. Your CI/CD pipeline is a
collection of scripts. Your backup procedure is a script. Your disaster recovery runbook
will be executed as a script when the pressure is highest and the stakes are real. A script
that fails silently, continues past errors, or leaves the system in an inconsistent state
can turn a minor incident into a major outage. The techniques in this lesson -- strict error
modes, signal traps, proper logging -- are what make scripts trustworthy.

Pipes and redirection are the connective tissue of Linux. The Unix philosophy of "do one
thing well" means that complex tasks are accomplished by chaining simple tools together.
`grep` finds lines, `awk` extracts fields, `sort` orders them, `uniq` deduplicates them.
Connected with pipes, these tools can perform data analysis that would take dozens of lines
in Python. Mastering pipes and redirection makes you dramatically more productive at the
command line and in your scripts.

Functions bring modularity to your scripts. A 500-line script without functions is
unmaintainable. Functions let you organize code into logical units, reuse logic, and make
scripts readable. They also enable testing: you can source a script's functions and test
them individually. As your scripts grow in complexity, functions become essential for keeping
them manageable.

Debugging is the final critical skill. When a script fails in production, you need to
quickly understand what went wrong. The `set -x` option shows every command as it executes,
turning your script into a step-by-step trace. Combined with `trap` for cleanup on failure
and proper logging, these debugging techniques let you diagnose and fix problems under
pressure.

---

## Core Concepts

### Strict Mode

Production scripts should always start with strict mode settings:

```bash
#!/bin/bash
set -euo pipefail
```

| Setting           | Effect                                              |
|--------------------|-----------------------------------------------------|
| `set -e`           | Exit immediately if any command fails               |
| `set -u`           | Treat unset variables as an error                   |
| `set -o pipefail`  | A pipeline fails if ANY command in the pipe fails   |

Without `set -e`, a failing command in the middle of your script is ignored, and the script
continues executing subsequent commands in a potentially broken state. Without `set -u`, a
typo in a variable name silently expands to an empty string. Without `pipefail`, only the
last command's exit code matters in a pipeline.

### Pipes and Redirection

| Operator  | Meaning                                              |
|-----------|------------------------------------------------------|
| `\|`      | Send stdout of one command to stdin of the next      |
| `>`       | Redirect stdout to a file (overwrite)                |
| `>>`      | Redirect stdout to a file (append)                   |
| `2>`      | Redirect stderr to a file                            |
| `2>&1`    | Redirect stderr to wherever stdout goes              |
| `&>`      | Redirect both stdout and stderr to a file            |
| `<`       | Read stdin from a file                               |
| `tee`     | Send output to both stdout AND a file                |

### Here Documents

Here documents allow you to embed multi-line text in a script:

```bash
cat << 'EOF'
This is a multi-line
block of text.
Variables are NOT expanded when EOF is quoted.
EOF
```

Without quotes on the delimiter, variables are expanded:

```bash
NAME="World"
cat << EOF
Hello, ${NAME}!
EOF
```

### Signal Trapping

The `trap` command lets you execute code when your script receives a signal or exits:

```bash
trap 'echo "Cleaning up..."; rm -f /tmp/lockfile' EXIT
trap 'echo "Interrupted!"; exit 1' INT TERM
```

---

## Step-by-Step Practical

### 1. Strict Mode in Action

```bash
cat > ~/scripts/strict_demo.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

echo "=== Demonstrating strict mode ==="

# This would fail with set -u (undefined variable)
# echo "Value: $UNDEFINED_VAR"

# This fails with set -e (command returns non-zero)
echo "Checking a directory..."
ls /this/does/not/exist

echo "This line will NEVER execute because the script exits on error."
SCRIPT

chmod +x ~/scripts/strict_demo.sh
~/scripts/strict_demo.sh
echo "Exit code: $?"
```

Expected output:
```
=== Demonstrating strict mode ===
Checking a directory...
ls: cannot access '/this/does/not/exist': No such file or directory
Exit code: 2
```

The script stopped at the failing `ls` command and never reached the final `echo`.

### 2. Functions

```bash
cat > ~/scripts/functions_demo.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

# Logging functions
log_info() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] [INFO]  $*"
}

log_warn() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] [WARN]  $*" >&2
}

log_error() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] [ERROR] $*" >&2
}

# Function with a return value
check_disk_space() {
    local threshold=${1:-80}
    local usage
    usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

    if [ "$usage" -gt "$threshold" ]; then
        log_warn "Disk usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    else
        log_info "Disk usage is ${usage}% (threshold: ${threshold}%)"
        return 0
    fi
}

# Function with output capture
get_system_info() {
    local hostname
    hostname=$(hostname)
    local kernel
    kernel=$(uname -r)
    local uptime_info
    uptime_info=$(uptime -p)

    echo "${hostname}|${kernel}|${uptime_info}"
}

# Main execution
log_info "Starting system checks"

# Call function and handle return value
if check_disk_space 90; then
    log_info "Disk check passed"
else
    log_warn "Disk check failed"
fi

# Capture function output
SYSTEM_INFO=$(get_system_info)
IFS='|' read -r HOST KERN UP <<< "$SYSTEM_INFO"
log_info "Host: ${HOST}, Kernel: ${KERN}, ${UP}"

log_info "All checks complete"
SCRIPT

chmod +x ~/scripts/functions_demo.sh
~/scripts/functions_demo.sh
```

Expected output:
```
[2026-04-16 10:00:00] [INFO]  Starting system checks
[2026-04-16 10:00:00] [INFO]  Disk usage is 35% (threshold: 90%)
[2026-04-16 10:00:00] [INFO]  Disk check passed
[2026-04-16 10:00:00] [INFO]  Host: devops-server, Kernel: 5.15.0-1041-aws, up 6 days
[2026-04-16 10:00:00] [INFO]  All checks complete
```

### 3. Pipes and Redirection

```bash
# Count unique logged-in shells
cat /etc/passwd | awk -F: '{print $7}' | sort | uniq -c | sort -rn
```

Expected output:
```
     18 /usr/sbin/nologin
      1 /bin/sync
      1 /bin/false
      1 /bin/bash
```

```bash
# Redirect stdout and stderr separately
ls /tmp /nonexistent 1> /tmp/stdout.log 2> /tmp/stderr.log
cat /tmp/stdout.log
cat /tmp/stderr.log
```

```bash
# Use tee to see output AND save it
echo "Hello" | tee /tmp/hello.log
cat /tmp/hello.log
```

```bash
# Pipeline with error detection (pipefail)
set -o pipefail
cat /nonexistent 2>/dev/null | grep "pattern"
echo "Exit code: $?"    # Non-zero because cat failed
```

### 4. Arrays and String Manipulation

```bash
cat > ~/scripts/arrays_demo.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

# Declare an array
SERVICES=("nginx" "postgresql" "redis" "ssh")

# Array length
echo "Monitoring ${#SERVICES[@]} services:"

# Iterate over array
for SERVICE in "${SERVICES[@]}"; do
    echo "  - ${SERVICE}"
done

# String manipulation
FILENAME="/var/log/nginx/access.log"
echo ""
echo "Full path: ${FILENAME}"
echo "Directory: ${FILENAME%/*}"           # Remove shortest match from end
echo "Filename:  ${FILENAME##*/}"          # Remove longest match from start
echo "Extension: ${FILENAME##*.}"          # Get extension
echo "No ext:    ${FILENAME%.*}"           # Remove extension
echo "Uppercase: ${FILENAME^^}"            # Convert to uppercase

# Substring
VERSION="nginx/1.18.0"
echo ""
echo "Version string: ${VERSION}"
echo "After slash:    ${VERSION#*/}"       # 1.18.0
echo "Before slash:   ${VERSION%/*}"       # nginx
echo "Replace:        ${VERSION/nginx/apache}"  # apache/1.18.0
SCRIPT

chmod +x ~/scripts/arrays_demo.sh
~/scripts/arrays_demo.sh
```

Expected output:
```
Monitoring 4 services:
  - nginx
  - postgresql
  - redis
  - ssh

Full path: /var/log/nginx/access.log
Directory: /var/log/nginx
Filename:  access.log
Extension: log
No ext:    /var/log/nginx/access
Uppercase: /VAR/LOG/NGINX/ACCESS.LOG

Version string: nginx/1.18.0
After slash:    1.18.0
Before slash:   nginx
Replace:        apache/1.18.0
```

### 5. Error Handling with trap

```bash
cat > ~/scripts/safe_deploy.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

LOCKFILE="/tmp/deploy.lock"
LOGFILE="/tmp/deploy.log"

# Cleanup function runs on exit (success or failure)
cleanup() {
    local exit_code=$?
    echo "[$(date)] Cleanup: removing lockfile" | tee -a "$LOGFILE"
    rm -f "$LOCKFILE"
    if [ $exit_code -ne 0 ]; then
        echo "[$(date)] Deploy FAILED with exit code ${exit_code}" | tee -a "$LOGFILE"
    else
        echo "[$(date)] Deploy completed successfully" | tee -a "$LOGFILE"
    fi
}

trap cleanup EXIT
trap 'echo "Received interrupt signal"; exit 1' INT TERM

# Prevent concurrent deployments
if [ -f "$LOCKFILE" ]; then
    echo "ERROR: Another deployment is in progress (lockfile exists)"
    exit 1
fi

echo $$ > "$LOCKFILE"
echo "[$(date)] Deploy started (PID: $$)" | tee "$LOGFILE"

# Simulate deployment steps
echo "[$(date)] Step 1: Pulling code..." | tee -a "$LOGFILE"
sleep 1

echo "[$(date)] Step 2: Building..." | tee -a "$LOGFILE"
sleep 1

echo "[$(date)] Step 3: Running tests..." | tee -a "$LOGFILE"
sleep 1

echo "[$(date)] Step 4: Deploying..." | tee -a "$LOGFILE"
sleep 1

echo "[$(date)] All steps completed" | tee -a "$LOGFILE"
SCRIPT

chmod +x ~/scripts/safe_deploy.sh
~/scripts/safe_deploy.sh
```

### 6. Debugging with set -x

```bash
cat > ~/scripts/debug_demo.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

# Enable debug output
set -x

GREETING="Hello"
NAME="DevOps"
RESULT="${GREETING}, ${NAME}!"
echo "$RESULT"

# Disable debug output
set +x

echo "Debug output is now off."
echo "This line does not show the trace."
SCRIPT

chmod +x ~/scripts/debug_demo.sh
~/scripts/debug_demo.sh
```

Expected output:
```
+ GREETING=Hello
+ NAME=DevOps
+ RESULT='Hello, DevOps!'
+ echo 'Hello, DevOps!'
Hello, DevOps!
+ set +x
Debug output is now off.
This line does not show the trace.
```

### 7. Here Documents for Configuration Generation

```bash
cat > ~/scripts/generate_config.sh << 'MAINSCRIPT'
#!/bin/bash
set -euo pipefail

APP_NAME=${1:-"myapp"}
APP_PORT=${2:-8080}
APP_ENV=${3:-"production"}

cat << EOF
# Auto-generated configuration for ${APP_NAME}
# Generated on $(date) by $(whoami)
# DO NOT EDIT MANUALLY

[application]
name = ${APP_NAME}
port = ${APP_PORT}
environment = ${APP_ENV}

[logging]
level = $([ "$APP_ENV" = "production" ] && echo "warn" || echo "debug")
file = /var/log/${APP_NAME}/${APP_NAME}.log
max_size = 100M
max_files = 10

[health_check]
enabled = true
path = /health
interval = 30
EOF
MAINSCRIPT

chmod +x ~/scripts/generate_config.sh
~/scripts/generate_config.sh "webapp" 3000 "staging"
```

Expected output:
```
# Auto-generated configuration for webapp
# Generated on Wed Apr 16 10:00:00 UTC 2026 by ubuntu
# DO NOT EDIT MANUALLY

[application]
name = webapp
port = 3000
environment = staging

[logging]
level = debug
file = /var/log/webapp/webapp.log
max_size = 100M
max_files = 10

[health_check]
enabled = true
path = /health
interval = 30
```

---

## Exercises

1. **Robust Script Template**: Create a script template with strict mode, a `log()` function,
   a `cleanup()` function with a trap, lockfile management, and argument parsing. Use this
   as your starting point for all future scripts.

2. **Log Analyzer**: Write a function-based script that reads a log file (create a sample one
   first), counts the occurrences of "ERROR", "WARN", and "INFO" levels, and prints a
   summary. Use pipes and `grep -c`.

3. **Configuration Validator**: Write a script that reads an INI-style config file and
   validates that required keys exist. Use `grep` and conditional logic. Exit with code 1
   if any required key is missing.

4. **Parallel Ping**: Write a script that pings 10 hosts simultaneously (using `&` for
   background execution), waits for all to complete (using `wait`), and reports results.
   Use arrays to store the host list and results.

5. **Debug Mode Script**: Write a script that accepts a `--debug` flag. When present, enable
   `set -x`. When absent, run normally. Parse the flag using a `case` statement or argument
   loop.

---

## Knowledge Check

**Q1: What does `set -euo pipefail` do, and why is it called "strict mode"?**

A1: `set -e` exits on any command failure, `set -u` exits on any unset variable reference,
and `set -o pipefail` ensures a pipeline fails if any command in it fails (not just the
last). Together, they prevent scripts from silently ignoring errors. It is called strict mode
because it makes Bash behave strictly about errors, rather than the default behavior of
continuing past failures and treating unset variables as empty strings.

**Q2: What is the difference between `>` and `>>` for file redirection?**

A2: `>` overwrites the file completely, replacing any existing content with the new output.
`>>` appends to the end of the file, preserving existing content. In DevOps, `>>` is
typically used for logging (you want to add to the log, not replace it), while `>` is used
when generating a new configuration file (you want a fresh file each time).

**Q3: How does `trap cleanup EXIT` work, and why is it important?**

A3: `trap` registers a handler that executes when the script receives a specific signal. The
`EXIT` signal fires whenever the script ends, regardless of whether it succeeded, failed, or
was interrupted. This guarantees cleanup runs (removing temp files, releasing locks, closing
connections) even if the script crashes partway through. Without trap, a script that fails
before its cleanup section leaves resources in an inconsistent state.

**Q4: What is the purpose of `local` when declaring variables inside functions?**

A4: `local` restricts a variable's scope to the function. Without `local`, variables are
global -- a variable set inside a function is visible everywhere in the script, which can
cause unexpected side effects when different functions use the same variable name. Using
`local` prevents functions from accidentally modifying each other's variables and makes
scripts easier to reason about.

**Q5: How would you redirect both stdout and stderr to the same log file?**

A5: Use `command &> /path/to/logfile` or equivalently `command > /path/to/logfile 2>&1`.
The `2>&1` syntax means "redirect file descriptor 2 (stderr) to wherever file descriptor 1
(stdout) is currently going." The order matters: `2>&1 > file` does NOT work as expected
because the stderr redirect happens before stdout is redirected to the file. Always put the
stdout redirect first.
