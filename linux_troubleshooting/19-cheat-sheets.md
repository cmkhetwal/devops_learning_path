# 19 - Quick Reference & Cheat Sheets
## One-Page References and Emergency Procedures

---

## EMERGENCY: SERVER DOWN CHECKLIST

```
□ Can you ping the server?                          → ping server_ip
□ Can you SSH in?                                   → ssh user@server
□ If no SSH, check console (IPMI/iDRAC/cloud console)
□ Is the server powered on?                         → Check cloud/physical
□ Is the network up?                                → ip link show
□ Check system logs:                                → journalctl -xb
□ Check if disk is full:                            → df -h
□ Check if OOM killed anything:                     → dmesg | grep -i oom
□ Check failed services:                            → systemctl --failed
□ Check if panic/crash occurred:                    → dmesg | head -50
□ Can you reach the gateway?                        → ping $(ip route | head -1 | awk '{print $3}')
```

## EMERGENCY: SERVICE DOWN CHECKLIST

```
□ Is the service running?         → systemctl status SERVICE
□ Try starting it:                → systemctl start SERVICE
□ Check the logs:                 → journalctl -u SERVICE -n 50
□ Check config syntax:            → nginx -t / httpd -t / named-checkconf
□ Check port is listening:        → ss -tlnp | grep PORT
□ Check firewall:                 → firewall-cmd --list-all / iptables -L -n
□ Check disk space:               → df -h
□ Check permissions:              → ls -la /path/to/config
□ Check SELinux:                  → getenforce; ausearch -m avc -ts recent
□ Check dependencies:             → Can service reach DB/DNS/API?
��� Check resource limits:          → cat /proc/PID/limits
□ Has config changed?             → git diff (if tracked) / rpm -V package
```

---

## QUICK REFERENCE: Most Used Commands

### System Info
```bash
uname -a                    # Kernel info
cat /etc/os-release         # OS version
hostname -f                 # FQDN
uptime                      # Uptime + load
nproc                       # CPU count
free -h                     # Memory
df -hT                      # Disk space
lsblk                       # Block devices
ip -brief addr              # IP addresses
```

### Process Management
```bash
ps auxf                     # Process tree
top -bn1 | head -20         # -b = batch mode (non-interactive), -n1 = one iteration only
kill -15 PID                # -15 = SIGTERM (graceful stop)
kill -9 PID                 # -9 = SIGKILL (force kill, cannot be caught)
pkill -f "pattern"          # -f = match against full command line, not just process name
lsof -p PID                 # Open files by process
lsof -i :80                 # Who's on port 80
strace -p PID -c            # -p = attach to running PID, -c = summary of syscall counts/times
```

### Service Management
```bash
systemctl start|stop|restart|reload|status SERVICE
systemctl enable|disable SERVICE
systemctl list-units --type=service --state=running
systemctl list-units --state=failed
journalctl -u SERVICE -f
journalctl -u SERVICE --since "1 hour ago"
```

### Network
```bash
ip addr show                # All interfaces
ip route show               # Routing table
ss -tlnp                    # -t = TCP, -l = listening, -n = numeric (no DNS), -p = show process
ss -tn state established    # -t = TCP, -n = numeric; filter to established connections only
dig domain.com              # DNS lookup
curl -I https://site.com    # -I = fetch HTTP headers only (HEAD request)
tcpdump -i eth0 -nn port 80 # -i = interface, -nn = no DNS/port name resolution, port 80 = filter
ping -c 4 host              # Connectivity test
traceroute host             # Path trace
mtr host                    # Better traceroute
```

### File Operations
```bash
find / -name "file" -type f     # -name = match filename, -type f = regular files only
find / -size +100M -type f      # -size +100M = files larger than 100 megabytes
find / -mtime -1 -type f        # -mtime -1 = modified within last 1 day
du -sh /path/*                   # -s = summary (total per argument), -h = human-readable
tar -czf archive.tar.gz /path   # -c = create, -z = gzip compress, -f = output filename
tar -xzf archive.tar.gz         # -x = extract, -z = gzip decompress, -f = input filename
rsync -avzP src/ dst/            # -a = archive (recursive + preserve attrs), -v = verbose, -z = compress, -P = progress + partial
```

### Text Processing
```bash
grep -rn "pattern" /path        # -r = recursive, -n = show line numbers
grep -v "exclude" file           # -v = invert match (show lines NOT matching)
sed -i 's/old/new/g' file       # -i = edit file in-place; g = global (replace all occurrences per line)
awk '{print $1, $NF}' file      # Print first and last column
sort | uniq -c | sort -rn       # Count and sort
tail -f /var/log/syslog         # Follow log
wc -l file                      # Count lines
```

---

## LOG FILE LOCATIONS

| Log | CentOS/RHEL | Ubuntu/Debian |
|-----|-------------|---------------|
| System | /var/log/messages | /var/log/syslog |
| Auth | /var/log/secure | /var/log/auth.log |
| Kernel | /var/log/dmesg | /var/log/kern.log |
| Cron | /var/log/cron | /var/log/syslog |
| Mail | /var/log/maillog | /var/log/mail.log |
| Boot | /var/log/boot.log | /var/log/boot.log |
| Nginx | /var/log/nginx/ | /var/log/nginx/ |
| Apache | /var/log/httpd/ | /var/log/apache2/ |
| MySQL | /var/log/mysqld.log | /var/log/mysql/ |
| Audit | /var/log/audit/audit.log | /var/log/audit/audit.log |
| Journal | `journalctl` | `journalctl` |

---

## DEFAULT PORTS

| Service | Port | Protocol |
|---------|------|----------|
| SSH | 22 | TCP |
| DNS | 53 | TCP/UDP |
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| SMTP | 25 | TCP |
| SMTP Submission | 587 | TCP |
| SMTPS | 465 | TCP |
| POP3 | 110 | TCP |
| POP3S | 995 | TCP |
| IMAP | 143 | TCP |
| IMAPS | 993 | TCP |
| MySQL | 3306 | TCP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| MongoDB | 27017 | TCP |
| NFS | 2049 | TCP/UDP |
| SNMP | 161 | UDP |
| Syslog | 514 | UDP/TCP |
| HAProxy Stats | 8404 | TCP |
| Prometheus | 9090 | TCP |
| Node Exporter | 9100 | TCP |
| Grafana | 3000 | TCP |
| Elasticsearch | 9200 | TCP |
| Kibana | 5601 | TCP |

---

## IMPORTANT CONFIG FILES

```
/etc/hostname                    # Hostname
/etc/hosts                       # Static host resolution
/etc/resolv.conf                 # DNS configuration
/etc/fstab                       # Filesystem mount table
/etc/sysctl.conf                 # Kernel parameters
/etc/security/limits.conf        # Resource limits
/etc/crontab                     # System cron
/etc/ssh/sshd_config             # SSH server config
/etc/sudoers                     # sudo configuration
/etc/passwd                      # User accounts
/etc/shadow                      # Password hashes
/etc/group                       # Groups
/etc/nginx/nginx.conf            # Nginx main config
/etc/httpd/conf/httpd.conf       # Apache config (CentOS)
/etc/apache2/apache2.conf        # Apache config (Ubuntu)
/etc/haproxy/haproxy.cfg         # HAProxy config
/etc/postfix/main.cf             # Postfix config
/etc/named.conf                  # BIND DNS config
/etc/my.cnf                      # MySQL config
/etc/selinux/config              # SELinux mode
```

---

## PERFORMANCE QUICK CHECKS (Run In This Order)

```bash
# 1. What's the load?
uptime

# 2. CPU breakdown
mpstat -P ALL 1 1              # -P ALL = show all CPUs; 1 1 = 1-second interval, 1 sample

# 3. Memory status
free -h

# 4. Disk space
df -hT

# 5. Disk I/O
iostat -xz 1 1                 # -x = extended stats, -z = omit idle devices; 1 1 = 1-sec interval, 1 sample

# 6. Top processes
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# 7. Network connections
ss -s

# 8. Recent errors
journalctl -p err --since "30 min ago" --no-pager | tail -20
# -p err = filter by priority (errors and above), --since = time filter, --no-pager = output directly (no less)

# 9. Failed services
systemctl --failed

# 10. OOM events
dmesg | grep -i "oom\|killed" | tail -5
```

---

## SIGNAL REFERENCE

| Signal | Number | Action | Use |
|--------|--------|--------|-----|
| SIGHUP | 1 | Reload | Reload configuration |
| SIGINT | 2 | Interrupt | Ctrl+C |
| SIGQUIT | 3 | Quit + core | Ctrl+\ |
| SIGKILL | 9 | Kill | Force kill (cannot be caught) |
| SIGTERM | 15 | Terminate | Graceful shutdown (default) |
| SIGUSR1 | 10 | User-defined | Log reopen (nginx) |
| SIGUSR2 | 12 | User-defined | Upgrade (nginx) |
| SIGSTOP | 19 | Pause | Freeze process |
| SIGCONT | 18 | Continue | Resume paused process |
