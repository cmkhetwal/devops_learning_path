# Lesson 10: Cron Jobs and Scheduled Automation

## Why This Matters in DevOps

Not all automation happens in response to an event. Some tasks need to happen on a regular
schedule regardless of what else is going on: rotating log files before they fill the disk,
creating database backups every night, checking disk space every five minutes, cleaning up
temporary files every week, renewing SSL certificates before they expire. This is **scheduled
automation**, and it is one of the pillars of reliable infrastructure management.

The distinction between scheduled automation and event-driven automation is fundamental to
DevOps thinking. Event-driven automation responds to triggers: a git push triggers a CI/CD
pipeline, a high CPU alert triggers an auto-scaling event, a new user signup triggers a
welcome email. Scheduled automation runs on a clock: every minute, every hour, every day at
midnight. Both are essential, and confusing when to use which approach leads to brittle
systems. Use scheduled automation for recurring maintenance tasks. Use event-driven
automation for workflows that should respond to changes.

Linux provides `cron` as its primary scheduling mechanism. Cron has been running scheduled
tasks on Unix systems since 1975, and its syntax has become a universal standard -- you will
see cron expressions in GitHub Actions, AWS CloudWatch Events, Kubernetes CronJobs, and
dozens of other tools. Learning cron syntax once gives you scheduling capability across the
entire DevOps toolchain.

Production cron jobs require discipline. A cron job that fails silently is worse than no cron
job at all, because it creates false confidence that the task is being performed. Every
production cron job should: log its execution, report failures through monitoring or
alerting, use lock files to prevent overlapping executions, handle errors gracefully, and be
monitored for expected execution. A backup cron job that has been silently failing for three
months is discovered only when you need to restore from backup -- the worst possible time.

As your infrastructure grows, you will move from individual cron jobs to more sophisticated
scheduling systems: systemd timers (which offer better logging and dependency management),
Airflow or Prefect (for complex data pipelines), and Kubernetes CronJobs (for containerized
workloads). But the principles remain the same: define when, define what, handle failure,
monitor execution. Cron is where you learn these principles in their simplest form.

---

## Core Concepts

### Cron Syntax

A cron expression has five fields:

```
 ┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of week (0 - 7, where 0 and 7 are Sunday)
 │ │ │ │ │
 * * * * * command_to_execute
```

### Common Cron Schedules

| Expression          | Meaning                                    |
|---------------------|--------------------------------------------|
| `* * * * *`         | Every minute                               |
| `*/5 * * * *`       | Every 5 minutes                            |
| `0 * * * *`         | Every hour (at minute 0)                   |
| `0 0 * * *`         | Every day at midnight                      |
| `0 2 * * *`         | Every day at 2:00 AM                       |
| `0 0 * * 0`         | Every Sunday at midnight                   |
| `0 0 1 * *`         | First day of every month at midnight       |
| `0 0 * * 1-5`       | Every weekday at midnight                  |
| `30 6 * * 1`        | Every Monday at 6:30 AM                    |
| `0 */4 * * *`       | Every 4 hours                              |
| `0 0 1,15 * *`      | 1st and 15th of each month at midnight     |

### Special Cron Strings

| String      | Equivalent       | Meaning            |
|-------------|------------------|--------------------|
| `@reboot`   | (run at startup) | Once after boot    |
| `@hourly`   | `0 * * * *`      | Once per hour      |
| `@daily`    | `0 0 * * *`      | Once per day       |
| `@weekly`   | `0 0 * * 0`      | Once per week      |
| `@monthly`  | `0 0 1 * *`      | Once per month     |
| `@yearly`   | `0 0 1 1 *`      | Once per year      |

### Cron vs systemd Timers

| Feature              | Cron                          | systemd Timers                |
|----------------------|-------------------------------|-------------------------------|
| Configuration        | Single crontab line           | Two files (.timer + .service) |
| Logging              | Email or manual redirect      | journalctl integration        |
| Dependencies         | None                          | Can depend on other units     |
| Missed runs          | Skipped silently              | Can catch up with Persistent  |
| Randomized delay     | Not built-in                  | RandomizedDelaySec supported  |
| Monitoring           | Manual                        | systemctl list-timers         |

### Best Practices for Production Cron Jobs

1. **Always redirect output** -- Capture both stdout and stderr to a log file
2. **Use lock files** -- Prevent overlapping executions if a job runs longer than expected
3. **Set PATH explicitly** -- Cron runs with a minimal environment, not your shell's PATH
4. **Use absolute paths** -- Never rely on relative paths in cron jobs
5. **Monitor execution** -- Alert if a job fails or does not run when expected
6. **Log timestamps** -- Every action should be timestamped for debugging
7. **Test before scheduling** -- Run the command manually first to verify it works

---

## Step-by-Step Practical

### 1. View and Edit Your Crontab

```bash
crontab -l
```

Expected output (if no cron jobs exist):
```
no crontab for ubuntu
```

Edit your crontab:

```bash
crontab -e
```

This opens your personal crontab in the default editor. Add a test entry:

```
# Test cron job - write timestamp every minute
* * * * * echo "$(date): cron is working" >> /tmp/cron_test.log
```

Save and exit. Verify it was saved:

```bash
crontab -l
```

Wait one minute, then check:

```bash
cat /tmp/cron_test.log
```

Expected output:
```
Wed Apr 16 10:01:00 UTC 2026: cron is working
```

Remove the test entry:

```bash
crontab -e
# Delete the test line, save and exit
```

### 2. System-Wide Cron Jobs

```bash
ls /etc/cron.d/
ls /etc/cron.daily/
ls /etc/cron.hourly/
ls /etc/cron.weekly/
ls /etc/cron.monthly/
```

Scripts placed in these directories run at the corresponding intervals. View the main
system crontab:

```bash
cat /etc/crontab
```

Expected output:
```
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
```

### 3. Write a Production-Quality Cron Script

```bash
sudo mkdir -p /opt/scripts/cron
sudo tee /opt/scripts/cron/disk_monitor.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# ============================================
# Disk Space Monitor
# Runs via cron to check disk usage
# Alerts if usage exceeds threshold
# ============================================

# Configuration
THRESHOLD=80
LOGFILE="/var/log/disk_monitor.log"
LOCKFILE="/tmp/disk_monitor.lock"
HOSTNAME=$(hostname)

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOGFILE"
}

# Cleanup on exit
cleanup() {
    rm -f "$LOCKFILE"
}
trap cleanup EXIT

# Prevent concurrent execution
if [ -f "$LOCKFILE" ]; then
    log "SKIP: Another instance is running (PID: $(cat $LOCKFILE))"
    exit 0
fi
echo $$ > "$LOCKFILE"

# Main logic
log "INFO: Disk monitor starting"

ALERT=false
while IFS= read -r line; do
    USAGE=$(echo "$line" | awk '{print $5}' | tr -d '%')
    MOUNT=$(echo "$line" | awk '{print $6}')
    FILESYSTEM=$(echo "$line" | awk '{print $1}')

    if [ "$USAGE" -gt "$THRESHOLD" ]; then
        log "ALERT: ${MOUNT} is ${USAGE}% full (filesystem: ${FILESYSTEM})"
        ALERT=true
    else
        log "OK: ${MOUNT} is ${USAGE}% full"
    fi
done < <(df -h --output=source,size,used,avail,pcent,target -x tmpfs -x devtmpfs | tail -n +2)

if [ "$ALERT" = true ]; then
    log "ALERT: One or more filesystems exceed ${THRESHOLD}% on ${HOSTNAME}"
    # In production, you would send an alert here:
    # curl -X POST https://hooks.slack.com/webhook -d "{\"text\": \"Disk alert on ${HOSTNAME}\"}"
fi

log "INFO: Disk monitor complete"
EOF

sudo chmod +x /opt/scripts/cron/disk_monitor.sh
sudo /opt/scripts/cron/disk_monitor.sh
sudo cat /var/log/disk_monitor.log
```

### 4. Write a Backup Script

```bash
sudo tee /opt/scripts/cron/backup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# ============================================
# Automated Backup Script
# Creates compressed backups of specified directories
# Rotates old backups (keeps last 7 days)
# ============================================

# Configuration
BACKUP_DIR="/var/backups/automated"
BACKUP_SOURCES=("/etc" "/opt/scripts")
RETENTION_DAYS=7
LOGFILE="/var/log/backup.log"
LOCKFILE="/tmp/backup.lock"
DATE=$(date +%Y-%m-%d_%H%M%S)
HOSTNAME=$(hostname)

# Functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

cleanup() {
    rm -f "$LOCKFILE"
}
trap cleanup EXIT

# Prevent concurrent execution
if [ -f "$LOCKFILE" ]; then
    log "ERROR: Another backup is running (PID: $(cat $LOCKFILE))"
    exit 1
fi
echo $$ > "$LOCKFILE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "INFO: === Backup started on ${HOSTNAME} ==="

# Create backups
for SOURCE in "${BACKUP_SOURCES[@]}"; do
    if [ ! -d "$SOURCE" ]; then
        log "WARN: Source directory ${SOURCE} does not exist, skipping"
        continue
    fi

    SAFE_NAME=$(echo "$SOURCE" | tr '/' '_' | sed 's/^_//')
    BACKUP_FILE="${BACKUP_DIR}/${SAFE_NAME}_${DATE}.tar.gz"

    log "INFO: Backing up ${SOURCE} -> ${BACKUP_FILE}"
    tar czf "$BACKUP_FILE" -C / "${SOURCE#/}" 2>/dev/null || {
        log "ERROR: Failed to backup ${SOURCE}"
        continue
    }

    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "INFO: Backup complete: ${BACKUP_FILE} (${SIZE})"
done

# Rotate old backups
log "INFO: Removing backups older than ${RETENTION_DAYS} days"
REMOVED=$(find "$BACKUP_DIR" -name "*.tar.gz" -mtime +"$RETENTION_DAYS" -print -delete | wc -l)
log "INFO: Removed ${REMOVED} old backup files"

# Summary
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
TOTAL_FILES=$(find "$BACKUP_DIR" -name "*.tar.gz" | wc -l)
log "INFO: === Backup complete. ${TOTAL_FILES} backups using ${TOTAL_SIZE} ==="
EOF

sudo chmod +x /opt/scripts/cron/backup.sh
sudo /opt/scripts/cron/backup.sh
```

### 5. Write a Cleanup Script

```bash
sudo tee /opt/scripts/cron/cleanup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# ============================================
# System Cleanup Script
# Removes temporary files, old logs, and caches
# ============================================

LOGFILE="/var/log/cleanup.log"
DRY_RUN=${1:-"false"}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

log "INFO: Cleanup started (dry_run: ${DRY_RUN})"

# Clean /tmp files older than 7 days
TMP_COUNT=$(find /tmp -type f -mtime +7 2>/dev/null | wc -l)
log "INFO: Found ${TMP_COUNT} files in /tmp older than 7 days"
if [ "$DRY_RUN" != "true" ]; then
    find /tmp -type f -mtime +7 -delete 2>/dev/null || true
fi

# Clean old log files (compressed logs older than 30 days)
OLD_LOGS=$(find /var/log -name "*.gz" -mtime +30 2>/dev/null | wc -l)
log "INFO: Found ${OLD_LOGS} compressed log files older than 30 days"
if [ "$DRY_RUN" != "true" ]; then
    find /var/log -name "*.gz" -mtime +30 -delete 2>/dev/null || true
fi

# Clean apt cache
if command -v apt-get &> /dev/null; then
    CACHE_SIZE=$(du -sh /var/cache/apt/archives/ 2>/dev/null | cut -f1)
    log "INFO: APT cache size: ${CACHE_SIZE}"
    if [ "$DRY_RUN" != "true" ]; then
        apt-get clean -y 2>/dev/null || true
    fi
fi

# Report disk usage after cleanup
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
log "INFO: Current disk usage: ${DISK_USAGE}"
log "INFO: Cleanup complete"
EOF

sudo chmod +x /opt/scripts/cron/cleanup.sh
sudo /opt/scripts/cron/cleanup.sh "true"   # Dry run first
```

### 6. Schedule the Scripts with Cron

```bash
# Edit root's crontab (since scripts need root permissions)
sudo crontab -e
```

Add these entries:

```
# DevOps Automation - Scheduled Tasks
# Maintainer: devops-team@company.com
# Last updated: 2026-04-16

# Environment
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=""

# Disk monitoring - every 5 minutes
*/5 * * * * /opt/scripts/cron/disk_monitor.sh >> /var/log/disk_monitor_cron.log 2>&1

# Daily backup - 2:00 AM every day
0 2 * * * /opt/scripts/cron/backup.sh >> /var/log/backup_cron.log 2>&1

# Weekly cleanup - Sunday at 3:00 AM
0 3 * * 0 /opt/scripts/cron/cleanup.sh >> /var/log/cleanup_cron.log 2>&1
```

Verify the crontab was saved:

```bash
sudo crontab -l
```

### 7. systemd Timers (Modern Alternative)

Create a timer for the disk monitor:

```bash
sudo tee /etc/systemd/system/disk-monitor.service << 'EOF'
[Unit]
Description=Disk Space Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/scripts/cron/disk_monitor.sh
StandardOutput=journal
StandardError=journal
EOF

sudo tee /etc/systemd/system/disk-monitor.timer << 'EOF'
[Unit]
Description=Run Disk Space Monitor every 5 minutes

[Timer]
OnCalendar=*:0/5
Persistent=true
RandomizedDelaySec=30

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable disk-monitor.timer
sudo systemctl start disk-monitor.timer
```

View active timers:

```bash
sudo systemctl list-timers --all
```

Expected output:
```
NEXT                         LEFT          LAST                         PASSED  UNIT
Wed 2026-04-16 10:10:00 UTC  4min 30s left Wed 2026-04-16 10:05:12 UTC 23s ago disk-monitor.timer
...
```

Check the timer's logs:

```bash
sudo journalctl -u disk-monitor.service --since "1 hour ago" --no-pager
```

### 8. Log Rotation with logrotate

```bash
sudo tee /etc/logrotate.d/devops-scripts << 'EOF'
/var/log/disk_monitor.log
/var/log/backup.log
/var/log/cleanup.log
{
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    dateext
    dateformat -%Y%m%d
}
EOF
```

Test the configuration:

```bash
sudo logrotate -d /etc/logrotate.d/devops-scripts
```

The `-d` flag performs a dry run, showing what would happen without making changes.

---

## Exercises

1. **Cron Expression Practice**: Write cron expressions for: (a) Every 15 minutes during
   business hours (9 AM to 5 PM, Monday through Friday). (b) At 11:30 PM on the last day
   of every month. (c) Every 6 hours. (d) At 8 AM on the first Monday of each month
   (hint: this requires a command-level check).

2. **Health Check Cron**: Write a comprehensive health check script that verifies: disk space
   is below 80%, memory usage is below 90%, load average is below the number of CPU cores,
   and critical services (ssh) are running. Schedule it to run every 5 minutes. Log results
   and simulate sending an alert on failure.

3. **Log Rotation Setup**: Create a logrotate configuration for a hypothetical application
   that logs to `/var/log/myapp/`. Rotate daily, keep 30 days, compress rotated files,
   and restart the application after rotation using a `postrotate` script.

4. **systemd Timer**: Convert one of your cron jobs into a systemd timer. Compare the two
   approaches by examining the logging, monitoring, and error handling differences. Use
   `systemctl list-timers` and `journalctl` to inspect the timer.

5. **Backup Verification**: Extend the backup script to include verification: after creating
   each backup, test that the archive is valid using `tar tzf`. Log the number of files in
   each backup. Add a monthly cron job that tests restoring from a backup to a temporary
   directory to verify data integrity.

---

## Knowledge Check

**Q1: What does `*/5 * * * *` mean in cron syntax?**

A1: It means "every 5 minutes." The `*/5` in the minute field means "every 5th minute"
(0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55). The remaining `* * * *` fields mean
"every hour, every day of the month, every month, every day of the week." So this job
runs 288 times per day (12 times per hour, 24 hours per day).

**Q2: Why should production cron jobs use lock files?**

A2: If a cron job takes longer than its scheduled interval, a new instance will start
while the previous one is still running. For example, a backup job scheduled every hour
might take 90 minutes on a particularly large dataset. Without a lock file, you would have
overlapping backups competing for disk I/O, potentially corrupting each other's output. A
lock file ensures only one instance runs at a time -- subsequent invocations detect the
lock and exit gracefully.

**Q3: What is the advantage of systemd timers over traditional cron?**

A3: systemd timers offer several advantages: (1) Automatic logging to the journal
(viewable with `journalctl`), (2) `Persistent=true` catches up on missed runs if the
system was down, (3) `RandomizedDelaySec` prevents thundering herd when many servers run
the same timer, (4) Dependency management (can require network or other services), (5)
Resource controls (memory limits, CPU quotas), (6) Better monitoring with `systemctl
list-timers`. The tradeoff is that they require two files instead of one line.

**Q4: A critical backup cron job has been silently failing for two weeks. How do you prevent
this from happening again?**

A4: Implement multiple safeguards: (1) The script should exit with a non-zero code on
failure. (2) Redirect cron output to a log file and monitor that log. (3) Set up a
monitoring check that verifies a recent backup file exists (e.g., a file less than 25 hours
old in the backup directory). (4) Use a dead man's switch service (like Cronitor or
Healthchecks.io) that alerts if the job does NOT report success within the expected window.
(5) Send a summary notification (Slack, email) on each run with the backup status.

**Q5: When should you use scheduled automation versus event-driven automation?**

A5: Use scheduled automation for: recurring maintenance (backups, cleanup, rotation),
periodic health checks, regular reports, certificate renewal checks, and any task that must
happen regardless of external events. Use event-driven automation for: deployments triggered
by code changes, auto-scaling triggered by load, alerts triggered by errors, and any task
that should happen in response to a specific event. Some tasks benefit from both: run a
security scan nightly (scheduled) AND on every deployment (event-driven).
