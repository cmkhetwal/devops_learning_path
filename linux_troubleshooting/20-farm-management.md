# 20 - Large-Scale Server Farm Management
## Strategies for 1000+ Linux Servers

---

## SECTION 1: Architecture & Organization

### 1.1 Server Classification
```
Organize servers by:
├── Environment
│   ├── Production
│   ├── Staging
│   ├── Development
│   └── DR (Disaster Recovery)
├── Role
│   ├── Web servers
│   ├── Application servers
│   ├── Database servers
│   ├── Load balancers
│   ├── Cache servers
│   ├── Queue servers
│   ├── Storage/NFS servers
│   ├── Monitoring servers
│   ├── Log aggregation
│   ├── Build/CI servers
│   └── Bastion/Jump hosts
├── Location/Region
│   ├── US-East
│   ├── US-West
│   └── EU-West
└── Criticality
    ├── Tier 1 (revenue impacting)
    ├── Tier 2 (business critical)
    └── Tier 3 (non-critical)
```

### 1.2 Naming Convention
```
Format: <environment>-<role>-<region>-<number>
Examples:
  prod-web-use1-001    (Production web server, US-East, #001)
  prod-db-use1-001     (Production database)
  stg-app-usw2-001     (Staging application server, US-West)
  prod-lb-use1-001     (Production load balancer)

DNS:
  prod-web-use1-001.internal.example.com
  web.prod.use1.example.com (service CNAME)
```

---

## SECTION 2: Configuration Management at Scale

### 2.1 Ansible for 1000+ Servers

```yaml
# Dynamic Inventory (don't use static files for 1000+ servers)

# AWS EC2 dynamic inventory
# /etc/ansible/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: tags.Environment
    prefix: env
  - key: placement.availability_zone
    prefix: az
filters:
  tag:managed: "ansible"
  instance-state-name: running
compose:
  ansible_host: private_ip_address
```

```bash
# Ansible performance tuning for large inventories
# /etc/ansible/ansible.cfg
[defaults]
forks = 50                    # Max parallel processes (default is 5; raise for large fleets)
strategy = free               # Don't wait for slowest host (each host proceeds independently)
pipelining = True             # Reduce SSH connections by executing modules without temp file transfer
gathering = smart             # Cache facts; only gather if not already cached
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600
host_key_checking = False
callback_whitelist = timer, profile_tasks

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o PreferredAuthentications=publickey
pipelining = True
```

```bash
# Rolling updates (don't update all at once!)
ansible-playbook update.yml --limit "role_webserver" -e "serial_count=10"
# --limit = restrict execution to matching hosts/groups
# -e = set extra variables (key=value pairs passed to playbook)
```

```yaml
# update.yml - Rolling update with 10% at a time
---
- hosts: role_webserver
  serial: "10%"              # Update 10% of servers at a time
  max_fail_percentage: 5     # Stop if > 5% fail
  become: yes

  pre_tasks:
    - name: Remove from load balancer
      uri:
        url: "http://lb/api/backend/{{ inventory_hostname }}/disable"
        method: POST

    - name: Wait for connections to drain
      pause:
        seconds: 30

  tasks:
    - name: Update packages
      package:
        name: "*"
        state: latest

    - name: Restart service
      service:
        name: nginx
        state: restarted

  post_tasks:
    - name: Health check
      uri:
        url: "http://{{ inventory_hostname }}/health"
        status_code: 200
      retries: 5
      delay: 10

    - name: Add back to load balancer
      uri:
        url: "http://lb/api/backend/{{ inventory_hostname }}/enable"
        method: POST
```

---

## SECTION 3: Patching Strategy

### 3.1 Patch Management Workflow
```
1. ASSESS
   - Identify patches available (security, bugfix, enhancement)
   - Classify by severity (Critical, High, Medium, Low)
   - Check CVE databases for active exploits

2. TEST
   - Apply to DEV environment first
   - Run automated tests
   - Apply to STAGING
   - Run integration tests
   - Soak for 24-48 hours

3. PLAN
   - Schedule maintenance window
   - Notify stakeholders
   - Prepare rollback plan
   - Identify dependencies

4. EXECUTE
   - Rolling updates (never all at once!)
   - 10% → verify → 25% → verify → 50% → verify → 100%
   - Monitor closely during rollout
   - Keep spare capacity (don't patch all servers in a pool)

5. VERIFY
   - Health checks pass
   - Monitoring shows normal metrics
   - Application tests pass
   - No increase in error rates
```

### 3.2 Automated Patching Script
```bash
#!/bin/bash
# /usr/local/bin/auto-patch.sh
# Run via Ansible on schedule

LOG="/var/log/patching.log"
REBOOT_REQUIRED=false

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG"; }

log "=== Patching started ==="

# Check which patches are available
if command -v dnf &>/dev/null; then
    UPDATES=$(dnf check-update --security 2>/dev/null | grep -c "^[a-zA-Z]" || true)
    # dnf check-update --security = list available security updates only
    log "Security updates available: $UPDATES"

    if [ "$UPDATES" -gt 0 ]; then
        dnf update --security -y >> "$LOG" 2>&1
        # --security = apply security-classified updates only; -y = assume yes (non-interactive)
        log "Security patches applied"
    fi

    # Check if reboot needed
    # needs-restarting -r = check if full system reboot is required after updates
    if needs-restarting -r 2>/dev/null; [ $? -eq 1 ]; then
        REBOOT_REQUIRED=true
    fi
elif command -v apt &>/dev/null; then
    apt update >> "$LOG" 2>&1
    UPDATES=$(apt list --upgradable 2>/dev/null | grep -c "security" || true)
    log "Security updates available: $UPDATES"

    if [ "$UPDATES" -gt 0 ]; then
        DEBIAN_FRONTEND=noninteractive apt upgrade -y >> "$LOG" 2>&1
        log "Security patches applied"
    fi

    if [ -f /var/run/reboot-required ]; then
        REBOOT_REQUIRED=true
    fi
fi

if [ "$REBOOT_REQUIRED" = true ]; then
    log "REBOOT REQUIRED - flagging for maintenance window"
    touch /var/run/reboot-needed
fi

log "=== Patching complete ==="
```

---

## SECTION 4: Centralized Monitoring Strategy

```
For 1000+ servers, use a tiered monitoring approach:

TIER 1: Infrastructure Metrics (Prometheus + Grafana)
  - CPU, Memory, Disk, Network per server
  - Service health (up/down)
  - Node Exporter on every server
  - Alert on: Down, High CPU, Low Disk, High Memory

TIER 2: Application Metrics (Prometheus + Custom Exporters)
  - Request rates, error rates, latency
  - Queue depths, connection pools
  - Business metrics

TIER 3: Log Aggregation (ELK or Loki)
  - Centralized log collection
  - Error pattern detection
  - Security event monitoring
  - Audit trail

TIER 4: Synthetic Monitoring (Blackbox Exporter)
  - External HTTP checks
  - DNS resolution checks
  - Certificate expiry monitoring
  - End-to-end user journey tests

ALERTING HIERARCHY:
  P1 (Critical) → PagerDuty → On-call engineer (immediate)
  P2 (High)     → Slack #critical + Email (15 min response)
  P3 (Medium)   → Slack #alerts (1 hour response)
  P4 (Low)      → Email + Dashboard (next business day)
```

### Prometheus Federation for Scale
```yaml
# Regional Prometheus instances scrape local servers
# Global Prometheus federates from regional instances

# Global Prometheus config
scrape_configs:
  - job_name: 'federate-us-east'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job=~".+"}'
    static_configs:
      - targets:
        - 'prometheus-us-east:9090'

  - job_name: 'federate-us-west'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job=~".+"}'
    static_configs:
      - targets:
        - 'prometheus-us-west:9090'
```

---

## SECTION 5: Security at Scale

### 5.1 Access Management
```
1. CENTRALIZED AUTHENTICATION
   - LDAP/Active Directory for all servers
   - SSO for web-based tools
   - SSH key management (not passwords)
   - Short-lived SSH certificates (HashiCorp Vault)

2. ROLE-BASED ACCESS (RBAC)
   - Admins: Full sudo
   - Developers: Deploy access only
   - DBAs: Database server access only
   - Monitoring: Read-only access
   - NO shared accounts

3. BASTION/JUMP HOST
   - All SSH traffic through bastion
   - Audit logging on bastion
   - MFA required for bastion access
   - No direct SSH to production servers

4. PRIVILEGED ACCESS
   - Sudo audit logging
   - Just-in-time access (temporary elevated privileges)
   - Break-glass procedures for emergencies
```

### 5.2 Compliance & Auditing
```bash
# Automated compliance check script
#!/bin/bash
# /usr/local/bin/compliance-check.sh

REPORT="/var/log/compliance/$(date +%Y%m%d).json"
ISSUES=0

check() {
    local name=$1 result=$2
    if [ "$result" = "PASS" ]; then
        echo "  PASS: $name"
    else
        echo "  FAIL: $name"
        ISSUES=$((ISSUES + 1))
    fi
}

echo "Compliance Check: $(hostname) - $(date)"

# SSH hardening
check "Root login disabled" $(grep -q "^PermitRootLogin no" /etc/ssh/sshd_config && echo PASS || echo FAIL)
check "Password auth disabled" $(grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config && echo PASS || echo FAIL)

# Firewall
check "Firewall active" $(systemctl is-active firewalld &>/dev/null && echo PASS || echo FAIL)

# Updates
check "No critical updates pending" $(dnf check-update --security 2>/dev/null | grep -q "^[a-zA-Z]" && echo FAIL || echo PASS)

# File permissions
check "No world-writable files in /etc" $([ $(find /etc -perm -o+w -type f 2>/dev/null | wc -l) -eq 0 ] && echo PASS || echo FAIL)

# SELinux
check "SELinux enforcing" $([ "$(getenforce 2>/dev/null)" = "Enforcing" ] && echo PASS || echo FAIL)

# NTP sync
check "Time synchronized" $(timedatectl | grep -q "System clock synchronized: yes" && echo PASS || echo FAIL)
# timedatectl = query and control system time/date and NTP synchronization status

echo ""
echo "Total issues: $ISSUES"
```

---

## SECTION 6: Capacity Planning

```bash
# Track growth metrics over time:
# 1. CPU utilization trends (daily peaks)
# 2. Memory usage trends
# 3. Disk growth rate (GB/month)
# 4. Network bandwidth utilization
# 5. Request/connection counts

# Useful Prometheus queries for capacity planning:

# Average CPU usage over 30 days
avg_over_time(100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)[30d:1h])

# Disk usage growth rate (GB/day)
predict_linear(node_filesystem_avail_bytes[30d], 86400 * 90)
# ↑ Predicts disk space 90 days from now

# Memory trend
avg_over_time((1 - node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes)[30d:1h]) * 100
```

---

## SECTION 7: Runbook Template

```markdown
# Runbook: [Service/Issue Name]

## Overview
Brief description of the service and this runbook's purpose.

## Contacts
| Role | Name | Phone | Email |
|------|------|-------|-------|
| Primary On-call | | | |
| Escalation | | | |
| Service Owner | | | |

## Architecture
Diagram or description of how the service works.

## Alert: [Alert Name]
### Symptoms
What the user/monitoring sees.

### Impact
Who is affected and how.

### Diagnosis Steps
1. Check X: `command here`
2. Check Y: `command here`
3. Look for Z in logs: `command here`

### Resolution Steps
1. If cause is A: `fix command`
2. If cause is B: `fix command`
3. If unclear: Escalate to [team]

### Rollback
Steps to undo changes if fix makes things worse.

### Prevention
What to do to prevent this from happening again.
```

---

## SECTION 8: Key Metrics Dashboard

```
FOR EACH SERVER:
  ├── CPU: Usage %, Load Average, Top Processes
  ├── Memory: Used %, Available, Swap Usage
  ├── Disk: Usage %, I/O Latency, IOPS
  ├── Network: Bandwidth In/Out, Packet Loss, Errors
  └── Services: Status, Response Time, Error Rate

FLEET OVERVIEW:
  ├── Total Servers: Online / Offline / Maintenance
  ├── Alerts: P1 / P2 / P3 active count
  ├── Patches: Up-to-date / Pending / Overdue
  ├── Certificates: Valid / Expiring Soon / Expired
  ├── Compliance: Pass / Fail percentage
  └── Capacity: Servers > 80% CPU/MEM/Disk
```
