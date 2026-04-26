# 14 - Automation & Configuration Management
## Ansible, Shell Scripting, Cron, Systemd Timers

---

## SECTION 1: Ansible (Configuration Management at Scale)

### 1.1 Installation
```bash
# Control node only (not on managed servers)
# CentOS/RHEL:
dnf install ansible-core -y
# Ubuntu:
apt install ansible -y
# Or via pip:
pip3 install ansible
```

### 1.2 Inventory
```ini
# /etc/ansible/hosts (or custom inventory file)

[webservers]
web1.example.com
web2.example.com
web3.example.com ansible_host=10.0.1.13

[dbservers]
db1.example.com
db2.example.com

[loadbalancers]
lb1.example.com
lb2.example.com

[monitoring]
monitor.example.com

[production:children]
webservers
dbservers
loadbalancers

[all:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/deploy_key
ansible_python_interpreter=/usr/bin/python3
```

### 1.3 Ad-hoc Commands
```bash
# Ping all servers
ansible all -m ping              # -m = module to execute (ping tests connectivity)

# Run command on all web servers
ansible webservers -m shell -a "uptime"
# -m shell = use the shell module (runs arbitrary commands)
# -a = module arguments (the command to run)
ansible webservers -m shell -a "df -h"
ansible webservers -m shell -a "free -h"

# Copy file to all servers
ansible all -m copy -a "src=/etc/motd dest=/etc/motd"
# -m copy = use the copy module (transfer files to remote hosts)

# Install package
ansible webservers -m yum -a "name=nginx state=present"   # CentOS
ansible webservers -m apt -a "name=nginx state=present"    # Ubuntu

# Restart service
ansible webservers -m service -a "name=nginx state=restarted"

# Gather facts
ansible web1 -m setup           # -m setup = gather all system facts (hardware, OS, network, etc.)
ansible web1 -m setup -a "filter=ansible_memtotal_mb"
# -a "filter=..." = return only facts matching the filter pattern
```

### 1.4 Playbooks
```yaml
# deploy-webserver.yml
---
- name: Configure Web Servers
  hosts: webservers
  become: yes
  vars:
    nginx_worker_processes: auto
    nginx_worker_connections: 4096

  tasks:
    - name: Install Nginx
      package:
        name: nginx
        state: present

    - name: Deploy Nginx config
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        backup: yes
      notify: Reload Nginx

    - name: Deploy virtual host
      template:
        src: templates/vhost.conf.j2
        dest: /etc/nginx/conf.d/{{ domain }}.conf
      notify: Reload Nginx

    - name: Ensure Nginx is running
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Open firewall ports
      firewalld:
        service: "{{ item }}"
        permanent: yes
        state: enabled
        immediate: yes
      loop:
        - http
        - https

  handlers:
    - name: Reload Nginx
      service:
        name: nginx
        state: reloaded
```

```yaml
# system-hardening.yml
---
- name: System Hardening
  hosts: all
  become: yes

  tasks:
    - name: Update all packages
      package:
        name: "*"
        state: latest

    - name: Install security tools
      package:
        name:
          - fail2ban
          - aide
          - chrony
        state: present

    - name: Configure sysctl
      sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        reload: yes
      loop:
        - { key: "net.ipv4.tcp_syncookies", value: "1" }
        - { key: "net.ipv4.conf.all.rp_filter", value: "1" }
        - { key: "vm.swappiness", value: "10" }

    - name: Set file limits
      pam_limits:
        domain: "*"
        limit_type: "{{ item.type }}"
        limit_item: nofile
        value: "65535"
      loop:
        - { type: soft }
        - { type: hard }

    - name: Harden SSH
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: "{{ item.regexp }}"
        line: "{{ item.line }}"
      loop:
        - { regexp: "^#?PermitRootLogin", line: "PermitRootLogin no" }
        - { regexp: "^#?PasswordAuthentication", line: "PasswordAuthentication no" }
        - { regexp: "^#?MaxAuthTries", line: "MaxAuthTries 3" }
      notify: Restart SSHD

  handlers:
    - name: Restart SSHD
      service:
        name: sshd
        state: restarted
```

```bash
# Run playbooks
ansible-playbook deploy-webserver.yml
ansible-playbook deploy-webserver.yml --check          # --check = dry run (show changes without applying)
ansible-playbook deploy-webserver.yml --limit web1     # --limit = run only on matching hosts
ansible-playbook deploy-webserver.yml --tags "config"  # --tags = run only tasks with specified tags
ansible-playbook deploy-webserver.yml -e "domain=example.com"  # -e = pass extra variables to playbook
```

### 1.5 Ansible Roles (Organized Structure)
```bash
# Create role structure
ansible-galaxy init roles/nginx    # init = create role directory skeleton from template

# Structure:
roles/nginx/
├── tasks/main.yml
├── handlers/main.yml
├── templates/
│   └── nginx.conf.j2
├── files/
├── vars/main.yml
├── defaults/main.yml
└── meta/main.yml

# Use role in playbook:
---
- hosts: webservers
  become: yes
  roles:
    - nginx
    - { role: ssl, domain: "example.com" }
    - { role: monitoring, tags: ["monitoring"] }
```

---

## SECTION 2: Shell Scripting Patterns

### 2.1 Production Script Template
```bash
#!/bin/bash
# Description: Server health check script
# Usage: ./health-check.sh [options]
# Author: Admin Team

set -euo pipefail
# -e = exit immediately on any command failure
# -u = treat unset variables as errors
# -o pipefail = fail pipe if any command in pipeline fails (not just last)
# set -x             # Debug mode (uncomment to trace)

# --- Configuration ---
LOG_FILE="/var/log/health-check.log"
ALERT_EMAIL="admin@example.com"
THRESHOLD_CPU=80
THRESHOLD_MEM=85
THRESHOLD_DISK=90

# --- Functions ---
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$1] $2" | tee -a "$LOG_FILE"
}

check_cpu() {
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print int($2)}')
    if [ "$cpu_usage" -gt "$THRESHOLD_CPU" ]; then
        log "WARN" "CPU usage is ${cpu_usage}% (threshold: ${THRESHOLD_CPU}%)"
        return 1
    fi
    log "OK" "CPU usage: ${cpu_usage}%"
    return 0
}

check_memory() {
    local mem_usage
    mem_usage=$(free | awk '/Mem:/{printf "%.0f", $3/$2*100}')
    if [ "$mem_usage" -gt "$THRESHOLD_MEM" ]; then
        log "WARN" "Memory usage is ${mem_usage}% (threshold: ${THRESHOLD_MEM}%)"
        return 1
    fi
    log "OK" "Memory usage: ${mem_usage}%"
    return 0
}

check_disk() {
    local issues=0
    while IFS= read -r line; do
        local usage mount
        usage=$(echo "$line" | awk '{print int($5)}')
        mount=$(echo "$line" | awk '{print $6}')
        if [ "$usage" -gt "$THRESHOLD_DISK" ]; then
            log "WARN" "Disk ${mount} is ${usage}% full"
            issues=$((issues + 1))
        fi
    done < <(df -h | grep "^/dev")

    [ "$issues" -eq 0 ] && log "OK" "All disks below ${THRESHOLD_DISK}%"
    return $issues
}

send_alert() {
    local subject="$1"
    local body="$2"
    echo "$body" | mail -s "$subject" "$ALERT_EMAIL" 2>/dev/null || true
}

# --- Main ---
main() {
    log "INFO" "Starting health check on $(hostname)"

    local alerts=""
    check_cpu  || alerts+="CPU issue detected\n"
    check_memory || alerts+="Memory issue detected\n"
    check_disk || alerts+="Disk issue detected\n"

    if [ -n "$alerts" ]; then
        log "ALERT" "Issues found!"
        send_alert "[ALERT] $(hostname) health issues" "$(echo -e "$alerts")"
    else
        log "INFO" "All checks passed"
    fi
}

main "$@"
```

### 2.2 Useful Script Patterns
```bash
# Loop through servers
while IFS= read -r server; do
    echo "--- $server ---"
    ssh "$server" "uptime; df -h | grep '/$'" 2>/dev/null || echo "FAILED: $server"
done < servers.txt

# Parallel execution
cat servers.txt | xargs -I{} -P10 ssh {} "uptime" 2>/dev/null
# -I{} = replace {} with each input line
# -P10 = run up to 10 processes in parallel

# Retry logic
retry() {
    local max_attempts=$1; shift
    local attempt=1
    until "$@"; do
        if [ "$attempt" -ge "$max_attempts" ]; then
            echo "Failed after $max_attempts attempts"
            return 1
        fi
        echo "Attempt $attempt failed, retrying..."
        attempt=$((attempt + 1))
        sleep 5
    done
}
retry 3 curl -sf http://example.com/health

# Lock file (prevent concurrent runs)
LOCKFILE="/tmp/myscript.lock"
exec 200>"$LOCKFILE"       # open file descriptor 200 pointing to the lock file
flock -n 200 || { echo "Already running"; exit 1; }
# -n = non-blocking (fail immediately if lock is already held)

# Cleanup on exit
cleanup() {
    rm -f "$LOCKFILE" "$TMPFILE"
    echo "Cleaned up"
}
trap cleanup EXIT
```

---

## SECTION 3: Cron & Systemd Timers

### Cron
```bash
# Edit crontab
crontab -e              # -e = edit crontab for current user
crontab -e -u username  # -u = specify which user's crontab to edit
crontab -l              # -l = list current crontab entries

# Format: minute hour day month weekday command
# Minute: 0-59 | Hour: 0-23 | Day: 1-31 | Month: 1-12 | Weekday: 0-7 (0,7=Sun)

# Examples:
*/5 * * * * /usr/local/bin/health-check.sh        # Every 5 minutes
0 */2 * * * /usr/local/bin/backup.sh               # Every 2 hours
0 2 * * * /usr/local/bin/cleanup.sh                # Daily at 2 AM
0 3 * * 0 /usr/local/bin/weekly-report.sh          # Sunday 3 AM
0 0 1 * * /usr/local/bin/monthly-report.sh         # 1st of month
30 6 * * 1-5 /usr/local/bin/workday-task.sh        # Weekdays 6:30 AM

# System cron directories (drop scripts here, no crontab needed):
/etc/cron.d/          # Custom cron files
/etc/cron.hourly/     # Run every hour
/etc/cron.daily/      # Run daily
/etc/cron.weekly/     # Run weekly
/etc/cron.monthly/    # Run monthly

# Log cron output
*/5 * * * * /usr/local/bin/script.sh >> /var/log/script.log 2>&1
```

### Systemd Timers (Modern Alternative)
```ini
# /etc/systemd/system/health-check.service
[Unit]
Description=System Health Check

[Service]
Type=oneshot
ExecStart=/usr/local/bin/health-check.sh
```

```ini
# /etc/systemd/system/health-check.timer
[Unit]
Description=Run health check every 5 minutes

[Timer]
OnBootSec=60
OnUnitActiveSec=5min
AccuracySec=1s

[Install]
WantedBy=timers.target
```

```bash
systemctl daemon-reload
systemctl enable --now health-check.timer
systemctl list-timers --all     # List all timers
```
