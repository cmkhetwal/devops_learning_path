# Lesson 7: Bash Scripting Basics

## Why This Matters in DevOps

The DevOps philosophy can be distilled to a single mandate: **automate everything**. Every
task you perform manually today is a task that should be scripted for tomorrow. Not because
scripting is inherently superior, but because manual processes do not scale, are error-prone,
and cannot be reliably repeated. When you deploy an application by hand, you might miss a
step. When a Bash script deploys it, every step executes in the same order, every time,
without fatigue or distraction.

Bash scripting is the universal automation language of Linux. Unlike Python or Go, Bash is
available on every Linux system by default with zero installation. It can call any command-
line tool, pipe data between programs, and orchestrate complex workflows. When you write a
Bash script, you are capturing institutional knowledge: the exact steps required to perform
a task, documented in executable form. A new team member can read the script to understand
the process, and more importantly, they can run it to execute the process without needing to
understand every detail.

In DevOps, you will write Bash scripts for deployment pipelines, backup procedures, health
checks, log analysis, server provisioning, and incident response. CI/CD systems like Jenkins,
GitHub Actions, and GitLab CI all execute Bash scripts as their fundamental unit of work.
Even when you use higher-level tools like Ansible or Terraform, understanding Bash is
necessary because those tools often execute shell commands under the hood, and you need Bash
for glue logic that connects different tools together.

The quality of your scripts matters. A script that works on your laptop but fails in
production because of an unhandled error case is worse than no script at all -- it creates
false confidence. Learning to write scripts with proper error handling, input validation, and
clear variable naming is what separates a quick hack from a reliable automation tool. In this
lesson, you will learn the fundamentals of Bash scripting that form the foundation for
writing production-quality automation.

Every Bash script you write is a step toward the DevOps ideal: infrastructure that is
reproducible, self-documenting, and automated. The goal is not to eliminate human judgment
but to eliminate human toil -- the repetitive, manual work that drains time and introduces
errors.

---

## Core Concepts

### Anatomy of a Bash Script

```bash
#!/bin/bash
# This is a comment explaining what the script does

# Variables
NAME="DevOps Engineer"

# Logic
echo "Hello, ${NAME}!"
```

- **Shebang (`#!/bin/bash`)**: The first line tells the system which interpreter to use. Always
  include it. Without it, the script may run with the wrong shell.
- **Comments (`#`)**: Explain WHY, not WHAT. Good scripts are self-documenting.
- **Variables**: Store values for reuse. No spaces around `=`.

### Making a Script Executable

```bash
chmod +x myscript.sh    # Add execute permission
./myscript.sh           # Run from current directory
bash myscript.sh        # Alternative: explicitly call bash
```

### Variable Types

| Type              | Syntax                     | Example                    |
|-------------------|----------------------------|----------------------------|
| String            | `NAME="value"`             | `APP="nginx"`              |
| Number            | `COUNT=5`                  | Used in arithmetic         |
| Command result    | `DATE=$(date)`             | Captures command output    |
| Environment var   | `export PATH="/opt:$PATH"` | Available to child processes|
| Special variables | `$0, $1, $#, $?, $$`       | Script name, args, status  |

### Special Variables

| Variable | Meaning                                    |
|----------|--------------------------------------------|
| `$0`     | Name of the script                         |
| `$1-$9`  | Positional parameters (arguments)          |
| `$#`     | Number of arguments passed                 |
| `$@`     | All arguments as separate strings          |
| `$?`     | Exit code of the last command              |
| `$$`     | Process ID of the current script           |
| `$!`     | PID of the last background process         |

### Exit Codes

Every command returns an exit code: `0` means success, anything else means failure.

```bash
ls /tmp
echo $?     # Prints 0 (success)

ls /nonexistent
echo $?     # Prints 2 (failure)
```

Your scripts should also return meaningful exit codes:

```bash
exit 0    # Success
exit 1    # General error
exit 2    # Misuse of command
```

---

## Step-by-Step Practical

### 1. Your First Script

```bash
mkdir -p ~/scripts
cat > ~/scripts/hello.sh << 'EOF'
#!/bin/bash
# My first DevOps script

echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
echo "Date: $(date)"
echo "Uptime: $(uptime -p)"
echo "Kernel: $(uname -r)"
echo "=========================="
EOF

chmod +x ~/scripts/hello.sh
~/scripts/hello.sh
```

Expected output:
```
=== System Information ===
Hostname: devops-server
User: ubuntu
Date: Wed Apr 16 10:00:00 UTC 2026
Uptime: up 6 days, 2 hours, 35 minutes
Kernel: 5.15.0-1041-aws
==========================
```

### 2. Variables and User Input

```bash
cat > ~/scripts/greet.sh << 'EOF'
#!/bin/bash
# Script demonstrating variables and input

# Static variable
COMPANY="Acme Corp"

# Command substitution
CURRENT_TIME=$(date +%H:%M)

# User input
read -p "Enter your name: " USER_NAME

# Using variables
echo "Welcome to ${COMPANY}, ${USER_NAME}!"
echo "The current time is ${CURRENT_TIME}."
echo "You are logged in as $(whoami) on $(hostname)."
EOF

chmod +x ~/scripts/greet.sh
~/scripts/greet.sh
```

### 3. Conditional Logic (if/else)

```bash
cat > ~/scripts/check_service.sh << 'EOF'
#!/bin/bash
# Check if a service is running

SERVICE=${1:-"ssh"}   # Use first argument, default to "ssh"

if systemctl is-active --quiet "$SERVICE"; then
    echo "[OK] ${SERVICE} is running"
else
    echo "[FAIL] ${SERVICE} is NOT running"
    echo "Attempting to start ${SERVICE}..."
    sudo systemctl start "$SERVICE"

    if systemctl is-active --quiet "$SERVICE"; then
        echo "[OK] ${SERVICE} started successfully"
    else
        echo "[ERROR] Failed to start ${SERVICE}"
        exit 1
    fi
fi
EOF

chmod +x ~/scripts/check_service.sh
~/scripts/check_service.sh ssh
~/scripts/check_service.sh nginx
```

Expected output:
```
[OK] ssh is running
[FAIL] nginx is NOT running
Attempting to start nginx...
```

### 4. Comparison Operators

```bash
cat > ~/scripts/disk_check.sh << 'EOF'
#!/bin/bash
# Check disk usage and warn if above threshold

THRESHOLD=80
USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

echo "Current disk usage: ${USAGE}%"

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "WARNING: Disk usage is above ${THRESHOLD}%!"
    echo "Consider cleaning up /var/log or /tmp"
elif [ "$USAGE" -gt 60 ]; then
    echo "NOTICE: Disk usage is moderate. Monitor closely."
else
    echo "OK: Disk usage is healthy."
fi
EOF

chmod +x ~/scripts/disk_check.sh
~/scripts/disk_check.sh
```

### 5. For Loops

```bash
cat > ~/scripts/server_check.sh << 'EOF'
#!/bin/bash
# Check connectivity to multiple servers

SERVERS=("google.com" "github.com" "8.8.8.8" "nonexistent.invalid")

echo "=== Server Connectivity Check ==="
echo "Date: $(date)"
echo ""

for SERVER in "${SERVERS[@]}"; do
    if ping -c 1 -W 2 "$SERVER" > /dev/null 2>&1; then
        echo "[OK]   ${SERVER} is reachable"
    else
        echo "[FAIL] ${SERVER} is NOT reachable"
    fi
done

echo ""
echo "Check complete."
EOF

chmod +x ~/scripts/server_check.sh
~/scripts/server_check.sh
```

Expected output:
```
=== Server Connectivity Check ===
Date: Wed Apr 16 10:00:00 UTC 2026

[OK]   google.com is reachable
[OK]   github.com is reachable
[OK]   8.8.8.8 is reachable
[FAIL] nonexistent.invalid is NOT reachable

Check complete.
```

### 6. While Loops

```bash
cat > ~/scripts/monitor.sh << 'EOF'
#!/bin/bash
# Simple system monitor that runs for 5 iterations

COUNT=0
MAX=5

while [ $COUNT -lt $MAX ]; do
    COUNT=$((COUNT + 1))
    LOAD=$(cat /proc/loadavg | cut -d' ' -f1)
    MEM=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')

    echo "[$(date +%H:%M:%S)] Iteration ${COUNT}/${MAX} - Load: ${LOAD} - Memory: ${MEM}"
    sleep 2
done

echo "Monitoring complete."
EOF

chmod +x ~/scripts/monitor.sh
~/scripts/monitor.sh
```

### 7. Case Statements

```bash
cat > ~/scripts/service_manager.sh << 'EOF'
#!/bin/bash
# Simple service management wrapper

SERVICE=$1
ACTION=$2

if [ -z "$SERVICE" ] || [ -z "$ACTION" ]; then
    echo "Usage: $0 <service> <start|stop|restart|status>"
    exit 1
fi

case "$ACTION" in
    start)
        echo "Starting ${SERVICE}..."
        sudo systemctl start "$SERVICE"
        ;;
    stop)
        echo "Stopping ${SERVICE}..."
        sudo systemctl stop "$SERVICE"
        ;;
    restart)
        echo "Restarting ${SERVICE}..."
        sudo systemctl restart "$SERVICE"
        ;;
    status)
        systemctl status "$SERVICE" --no-pager
        ;;
    *)
        echo "Unknown action: ${ACTION}"
        echo "Valid actions: start, stop, restart, status"
        exit 1
        ;;
esac
EOF

chmod +x ~/scripts/service_manager.sh
~/scripts/service_manager.sh ssh status
```

### 8. Putting It All Together: Deployment Script

```bash
cat > ~/scripts/deploy_app.sh << 'EOF'
#!/bin/bash
# Simple application deployment script

APP_NAME="myapp"
DEPLOY_DIR="/opt/${APP_NAME}"
LOG_FILE="/var/log/${APP_NAME}-deploy.log"
VERSION=${1:-"latest"}

echo "=== Deploying ${APP_NAME} v${VERSION} ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo ""

# Step 1: Pre-flight checks
echo "[1/4] Running pre-flight checks..."
if [ "$(whoami)" = "root" ]; then
    echo "WARNING: Running as root. Consider using a deploy user."
fi

# Step 2: Create directory structure
echo "[2/4] Setting up directories..."
sudo mkdir -p "${DEPLOY_DIR}"/{bin,config,logs}

# Step 3: Simulate deployment
echo "[3/4] Deploying version ${VERSION}..."
echo "${VERSION}" | sudo tee "${DEPLOY_DIR}/VERSION" > /dev/null
echo "deployed_at=$(date -Is)" | sudo tee "${DEPLOY_DIR}/deploy.info" > /dev/null

# Step 4: Verify
echo "[4/4] Verifying deployment..."
if [ -f "${DEPLOY_DIR}/VERSION" ]; then
    echo ""
    echo "=== Deployment Successful ==="
    echo "Version: $(cat ${DEPLOY_DIR}/VERSION)"
    echo "Location: ${DEPLOY_DIR}"
    exit 0
else
    echo "ERROR: Deployment verification failed!"
    exit 1
fi
EOF

chmod +x ~/scripts/deploy_app.sh
sudo ~/scripts/deploy_app.sh "1.0.0"
```

---

## Exercises

1. **System Report Script**: Write a script called `system_report.sh` that outputs the
   hostname, IP address, disk usage, memory usage, CPU load average, number of running
   processes, and uptime. Format the output neatly with labels.

2. **User Checker**: Write a script that takes a username as an argument and reports whether
   that user exists on the system (check `/etc/passwd`). If the user exists, display their
   UID, home directory, and shell.

3. **File Backup**: Write a script that takes a filename as an argument, verifies the file
   exists, creates a backup copy with a timestamp (e.g., `myfile.txt.2026-04-16_1030.bak`),
   and confirms the backup was created.

4. **Service Monitor Loop**: Write a script that checks if `ssh` is running every 10 seconds
   for one minute (6 iterations). Log each check to a file with a timestamp and the result.

5. **Menu Script**: Write an interactive script using a `case` statement that presents a menu
   with options: (1) Show disk usage, (2) Show memory, (3) Show running processes,
   (4) Show network info, (5) Quit. Loop until the user selects Quit.

---

## Knowledge Check

**Q1: What does the shebang line (`#!/bin/bash`) do, and what happens if you omit it?**

A1: The shebang tells the operating system which interpreter to use when executing the
script. Without it, the system uses the current shell, which might not be Bash (it could be
`sh`, `dash`, `zsh`, or another shell). Since these shells have different features and
syntax, your script might behave unexpectedly or fail. Always include the shebang line for
predictable execution.

**Q2: What is the difference between `$@` and `$*` when handling script arguments?**

A2: `$@` (when quoted as `"$@"`) expands each argument as a separate quoted string,
preserving arguments with spaces. `$*` (when quoted as `"$*"`) combines all arguments into
a single string. Use `"$@"` when passing arguments to other commands to preserve the
original argument boundaries. For example, if called with `"hello world" "foo"`, `"$@"`
gives two arguments while `"$*"` gives one.

**Q3: A script runs successfully when you execute it with `bash myscript.sh` but fails with
`./myscript.sh`. What is likely wrong?**

A3: The file likely does not have execute permission. You need to run `chmod +x myscript.sh`
to make it executable. The `bash myscript.sh` method works because you are explicitly
telling bash to interpret the file -- it does not need execute permission in that case.
The `./` method asks the OS to execute the file directly, which requires the execute bit.

**Q4: What does `${1:-"default"}` mean in a Bash script?**

A4: This is parameter expansion with a default value. It means: use the value of `$1` (the
first argument), but if `$1` is unset or empty, use `"default"` instead. This is essential
for writing robust scripts that work even when arguments are not provided. Other forms
include `${VAR:="default"}` (also assigns the default) and `${VAR:?"error message"}` (exits
with an error if unset).

**Q5: Why is `exit 0` vs `exit 1` important in DevOps scripting?**

A5: Exit codes are how scripts communicate success or failure to the calling process. CI/CD
pipelines, cron jobs, and orchestration tools check the exit code to decide what to do next.
`exit 0` means success -- the pipeline continues. `exit 1` (or any non-zero value) means
failure -- the pipeline stops, alerts are triggered, and the deployment may be rolled back.
A script that fails silently (exits 0 when something went wrong) is dangerous because it
hides problems.
