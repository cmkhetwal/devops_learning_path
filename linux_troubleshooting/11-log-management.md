# 11 - Log Management & Analysis
## journalctl, rsyslog, logrotate, Centralized Logging

---

## SECTION 1: journalctl (systemd Journal)

```bash
# View all logs
journalctl

# Follow logs in real-time
journalctl -f                              # -f = follow (like tail -f, stream new entries)

# Logs for a specific service
journalctl -u nginx                        # -u = filter by systemd unit name
journalctl -u nginx -f                     # Follow
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx --since "2024-01-15 10:00" --until "2024-01-15 12:00"
journalctl -u nginx --since today
journalctl -u nginx --since yesterday

# Filter by priority
journalctl -p err                           # -p = filter by priority level (and above)
journalctl -p warning                       # Warnings and above
journalctl -p crit                          # Critical
# Priorities: emerg(0), alert(1), crit(2), err(3), warning(4), notice(5), info(6), debug(7)

# Kernel messages
journalctl -k                               # -k = show only kernel messages (like dmesg)
journalctl -k -p err                        # Kernel errors

# Boot logs
journalctl -b                               # -b = show logs from current boot only
journalctl -b -1                            # -b -1 = show logs from previous boot
journalctl --list-boots                     # --list-boots = show all recorded boot sessions

# Output formats
journalctl -u nginx -o json-pretty          # -o = output format (json-pretty = human-readable JSON)
journalctl -u nginx -o short-iso            # short-iso = default format with ISO 8601 timestamps
journalctl -u nginx -o verbose              # verbose = show all stored metadata fields

# Disk usage
journalctl --disk-usage                     # --disk-usage = show journal disk space used
journalctl --vacuum-size=500M               # --vacuum-size = delete old entries until under size limit
journalctl --vacuum-time=30d                # --vacuum-time = delete entries older than duration

# Filter by PID, UID, executable (journal field filters)
journalctl _PID=1234                        # _PID = filter by process ID
journalctl _UID=1000                        # _UID = filter by user ID
journalctl _COMM=sshd                       # _COMM = filter by command name
journalctl _EXE=/usr/sbin/nginx             # _EXE = filter by executable path

# Multiple service logs
journalctl -u nginx -u php-fpm -u mysql
```

---

## SECTION 2: rsyslog Configuration

```bash
# Main config: /etc/rsyslog.conf
# Additional configs: /etc/rsyslog.d/*.conf

# Install (usually pre-installed)
# CentOS: dnf install rsyslog
# Ubuntu: apt install rsyslog
```

```bash
# /etc/rsyslog.d/custom.conf

# Log format
$template CustomFormat,"%timegenerated% %HOSTNAME% %syslogtag%%msg%\n"

# Separate log files by facility
auth,authpriv.*             /var/log/auth.log
*.*;auth,authpriv.none      /var/log/syslog
kern.*                      /var/log/kern.log
mail.*                      /var/log/mail.log
cron.*                      /var/log/cron.log
local0.*                    /var/log/custom-app.log

# Forward logs to remote syslog server (centralized logging)
# UDP:
*.* @syslog-server.example.com:514

# TCP (reliable):
*.* @@syslog-server.example.com:514

# TCP with TLS:
# $DefaultNetstreamDriverCAFile /etc/pki/tls/certs/ca.pem
# $ActionSendStreamDriver gtls
# $ActionSendStreamDriverMode 1
# $ActionSendStreamDriverAuthMode anon
# *.* @@syslog-server.example.com:6514

# Filter and forward specific logs
if $programname == 'nginx' then @@logserver:514
if $msg contains 'error' then /var/log/all-errors.log
```

### Receive Logs on Central Server
```bash
# /etc/rsyslog.d/receive.conf (on log server)

# Enable TCP reception
module(load="imtcp")
input(type="imtcp" port="514")

# Enable UDP reception
module(load="imudp")
input(type="imudp" port="514")

# Store by hostname
$template RemoteLogs,"/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log"
*.* ?RemoteLogs
& stop

systemctl restart rsyslog
```

---

## SECTION 3: logrotate

```bash
# Main config: /etc/logrotate.conf
# App configs: /etc/logrotate.d/

# Test logrotate (dry run)
logrotate -d /etc/logrotate.d/nginx      # -d = debug/dry-run (show what would happen, change nothing)

# Force rotation
logrotate -f /etc/logrotate.d/nginx      # -f = force rotation regardless of schedule

# Verbose run
logrotate -v /etc/logrotate.conf         # -v = verbose output (show processing details)
```

### Custom logrotate Configurations
```bash
# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 nginx adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}

# /etc/logrotate.d/application
/var/log/myapp/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate              # For apps that keep file handle open
    size 100M                 # Also rotate if > 100MB
    maxsize 500M              # Force rotate if > 500MB regardless of interval
    dateext                   # Use date in filename
    dateformat -%Y%m%d
}

# /etc/logrotate.d/syslog
/var/log/syslog
/var/log/messages
/var/log/auth.log
{
    rotate 7
    daily
    missingok
    notifempty
    compress
    delaycompress
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

### logrotate Directives Reference
```
daily/weekly/monthly     Rotation frequency
rotate N                 Keep N rotated files
compress                 Gzip old logs
delaycompress            Compress on next rotation (not current)
missingok                Don't error if log file missing
notifempty               Don't rotate empty files
create MODE OWNER GROUP  Set permissions on new file
copytruncate             Copy then truncate (for apps holding file open)
sharedscripts            Run postrotate once for all matched files
dateext                  Add date to rotated filename
size NM                  Rotate when file exceeds size
maxsize NM               Rotate when file exceeds regardless of time
minsize NM               Don't rotate unless file exceeds size
olddir /path             Move rotated files to directory
postrotate/endscript     Commands to run after rotation
prerotate/endscript      Commands to run before rotation
```

---

## SECTION 4: Quick Log Analysis

```bash
# Find most common errors in syslog
grep -i "error\|fail\|critical" /var/log/syslog | \
    sed 's/.*]: //' | sort | uniq -c | sort -rn | head -20

# Error rate per hour
grep -i "error" /var/log/syslog | \
    awk '{print $1, $2, substr($3,1,2)":00"}' | sort | uniq -c

# Last 100 authentication failures
grep "authentication failure\|Failed password" /var/log/auth.log | tail -100

# Services that restarted recently
journalctl --since "24 hours ago" | grep "Started\|Stopped" | \
    awk '{for(i=5;i<=NF;i++) printf "%s ", $i; print ""}' | sort | uniq -c | sort -rn

# Disk I/O errors
dmesg | grep -i "error\|i/o\|sector\|reset"

# Most active log files (by size)
find /var/log -name "*.log" -exec du -h {} + 2>/dev/null | sort -rh | head -20
```
