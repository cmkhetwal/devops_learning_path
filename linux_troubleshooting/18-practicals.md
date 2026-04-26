# 18 - Practical Exercises
## 50+ Hands-On Labs: Beginner to Expert

---

## LEVEL 1: BEGINNER (Linux Fundamentals)

### Lab 1: System Exploration
```
TASK: Gather complete information about your system
DO:
  1. Find your OS version, kernel version, hostname
  2. Check total RAM, CPU count, disk space
  3. List all running services
  4. Find your IP address, gateway, DNS servers
  5. Check who is logged in and system uptime

COMMANDS TO PRACTICE:
  cat /etc/os-release, uname -a, hostname
  free -h, nproc, lscpu, df -hT, lsblk
  # free -h = human-readable memory info; df -h = human-readable, -T = show filesystem type
  systemctl list-units --type=service --state=running
  ip addr, ip route, cat /etc/resolv.conf
  w, uptime, who, last

VERIFY: Create a single script that outputs all of the above
```

### Lab 2: User Management
```
TASK: Set up users and groups for a development team
DO:
  1. Create group "developers" and "testers"
  2. Create users: dev1, dev2, test1, test2
  3. Add dev1, dev2 to developers group; test1, test2 to testers
  4. Set password policies: min 8 chars, expire in 90 days
  5. Give developers group sudo access to restart nginx
  6. Create a shared directory /project accessible by both groups
  7. Set SGID on /project so new files inherit the group

VERIFY: Login as dev1, test if sudo, group access, and file permissions work
```

### Lab 3: File Permissions Deep Dive
```
TASK: Understand and fix permission issues
DO:
  1. Create directory structure: /data/public, /data/private, /data/shared
  2. /data/public → readable by everyone
  3. /data/private → only root can access
  4. /data/shared → read/write by "developers" group, read by "testers"
  5. Use ACLs: give user "auditor" read-only access to /data/private
  6. Set sticky bit on /data/shared (users can only delete own files)
  7. Find all SUID files on the system and document why they need SUID

VERIFY: Test access as different users, verify ACLs with getfacl
```

### Lab 4: Package Management
```
TASK: Practice package management across distros
DO:
  1. Search for, install, and verify: htop, nginx, vim
  2. Find which package provides the file /usr/bin/dig
  3. List all installed packages and save to a file
  4. Downgrade a package to a previous version
  5. Add a third-party repository (EPEL or a PPA)
  6. Remove a package and its dependencies
  7. Check for available security updates

COMMANDS: yum/dnf/apt install/remove/search, rpm -qf, dpkg -S
# rpm -qf = query which package owns a file; dpkg -S = search for package owning a file
```

### Lab 5: Process Management
```
TASK: Master process management
DO:
  1. Start a background process: sleep 3600 &
  2. Find its PID three different ways
  3. Check its resource usage, open files, and limits
  4. Change its priority (renice)
  5. Send different signals: SIGSTOP (pause), SIGCONT (resume), SIGTERM
  6. Write a script that monitors a process and restarts it if it dies
  7. Create a zombie process and clean it up

VERIFY: Use ps, top, /proc/<PID>/ to verify each step
```

---

## LEVEL 2: INTERMEDIATE (Services & Networking)

### Lab 6: Nginx Web Server
```
TASK: Deploy a multi-site Nginx server
DO:
  1. Install Nginx
  2. Create two virtual hosts: site-a.local, site-b.local
  3. Each site has different HTML content
  4. Enable gzip compression
  5. Set up access logging in custom format
  6. Add rate limiting (10 req/s)
  7. Configure a reverse proxy for a backend app (use python3 -m http.server 8080)
  8. Add basic auth on one location (/admin)
  9. Test all configurations

VERIFY: curl each site, check headers, test rate limiting, check logs
```

### Lab 7: Apache Web Server
```
TASK: Deploy Apache with PHP
DO:
  1. Install Apache and PHP-FPM
  2. Create a virtual host serving a PHP info page
  3. Switch from prefork to event MPM
  4. Configure mod_rewrite for clean URLs
  5. Set up .htaccess with directory-level settings
  6. Enable mod_status and view server stats
  7. Configure mod_security basic rules (if available)
  8. Set up reverse proxy to a Node.js app

VERIFY: Test PHP works, check MPM, verify rewrites, check status page
```

### Lab 8: Firewall Configuration
```
TASK: Secure a web server with firewall rules
DO:
  1. Configure firewalld (CentOS) or iptables:
     - Allow SSH from specific subnet only (e.g., 10.0.0.0/8)
     - Allow HTTP/HTTPS from anywhere
     - Allow MySQL only from app servers (specific IPs)
     - Block all other incoming traffic
     - Allow all outgoing traffic
  2. Add rate limiting for SSH (max 3 connections in 60 seconds)
  3. Enable logging of dropped packets
  4. Set up port forwarding: external:8080 → internal:80
  5. Test each rule

VERIFY: Use nmap from another machine to verify open/closed ports
```

### Lab 9: DNS Server
```
TASK: Build a DNS server for your lab network
DO:
  1. Install and configure BIND
  2. Create forward zone for lab.local
  3. Add A, CNAME, MX, and TXT records
  4. Create reverse zone
  5. Set up a secondary (slave) DNS server
  6. Configure a client to use your DNS server
  7. Test zone transfers
  8. Enable query logging and analyze

VERIFY: dig/nslookup for all record types, test failover
```

### Lab 10: Mail Server
```
TASK: Set up a basic mail server
DO:
  1. Install and configure Postfix
  2. Set up Dovecot for IMAP
  3. Create mail users
  4. Configure TLS for SMTP and IMAP
  5. Set up SPF, DKIM (OpenDKIM)
  6. Send test email between local users
  7. Test with a mail client (Thunderbird or mustringing)
  8. Check mail queue, view mail logs

VERIFY: Send/receive mail, verify TLS, check DKIM signatures
```

### Lab 11: SSL Certificates
```
TASK: Master certificate management
DO:
  1. Generate a self-signed certificate with SAN (multiple domains)
  2. Create your own Certificate Authority (CA)
  3. Issue a server certificate signed by your CA
  4. Install the CA cert on client machines
  5. Verify the certificate chain works
  6. Set up Let's Encrypt on a public server (or use staging)
  7. Configure auto-renewal
  8. Convert between PEM, DER, and PKCS12 formats

VERIFY: openssl verify, curl without -k flag, browser shows trusted
```

### Lab 12: Storage Management
```
TASK: Manage storage with LVM
DO:
  1. Add two virtual disks (or loop devices)
  2. Create physical volumes, volume group, logical volumes
  3. Create ext4 and xfs filesystems
  4. Mount and add to /etc/fstab
  5. Extend LV online (no downtime)
  6. Create and restore an LVM snapshot
  7. Add a third disk and extend the VG
  8. Set up NFS server and client between two machines

VERIFY: df -h shows correct sizes, fstab survives reboot, NFS mount works
```

---

## LEVEL 3: ADVANCED (Performance & Scale)

### Lab 13: Performance Troubleshooting Simulation
```
TASK: Diagnose and fix simulated performance issues
DO:
  1. Install stress tool: dnf/apt install stress stress-ng
  2. Simulate CPU overload: stress --cpu 4 --timeout 120
     → Use top, mpstat, ps to identify the issue
  3. Simulate memory pressure: stress --vm 2 --vm-bytes 1G --timeout 120
     → Use free, vmstat, ps --sort=-%mem to diagnose
  4. Simulate disk I/O: stress --io 4 --hdd 2 --timeout 120
     → Use iostat, iotop, pidstat -d to find I/O hog
  5. Simulate fork bomb (in VM only!): :(){ :|:& };:
     → How would you prevent this? (hint: limits.conf)
  6. Create a script that generates the health report from Section 01

VERIFY: Document each scenario: symptoms → diagnosis → resolution
```

### Lab 14: HAProxy Load Balancer
```
TASK: Build a load-balanced web environment
DO:
  1. Set up 2-3 backend web servers (Nginx with different content)
  2. Install HAProxy
  3. Configure round-robin load balancing
  4. Add health checks
  5. Set up the stats page
  6. Test failover by stopping one backend
  7. Configure sticky sessions
  8. Set up SSL termination at HAProxy
  9. Configure rate limiting
  10. Set up Keepalived for HAProxy HA (if 2 HAProxy servers)

VERIFY: curl shows different backends, stats page shows healthy servers
```

### Lab 15: Monitoring Stack
```
TASK: Deploy Prometheus + Grafana monitoring
DO:
  1. Install Prometheus
  2. Install Node Exporter on all servers
  3. Configure Prometheus to scrape all exporters
  4. Install Grafana
  5. Add Prometheus as data source in Grafana
  6. Import Node Exporter dashboard (ID: 1860)
  7. Create custom dashboard for:
     - CPU, Memory, Disk per server
     - Network traffic
     - Service status
  8. Set up Alertmanager with email notifications
  9. Create alerts: High CPU, Low Disk, Service Down

VERIFY: Dashboard shows all servers, trigger a test alert
```

### Lab 16: ELK Stack
```
TASK: Set up centralized logging
DO:
  1. Install Elasticsearch (single node)
  2. Install Kibana
  3. Install Filebeat on 2+ servers
  4. Configure Filebeat to ship syslog and nginx logs
  5. Create index patterns in Kibana
  6. Build a dashboard showing:
     - Error count over time
     - Top error sources
     - HTTP status code distribution
  7. Create a visualization for SSH login failures

VERIFY: Logs appear in Kibana, dashboards show real data
```

### Lab 17: Ansible Automation
```
TASK: Automate a complete server setup
DO:
  1. Set up Ansible control node
  2. Create inventory with 3+ servers (use VMs/containers)
  3. Write playbook to:
     - Update all packages
     - Install common tools (htop, vim, curl, wget)
     - Configure sysctl tuning
     - Set file descriptor limits
     - Configure NTP
     - Harden SSH
     - Set up firewall rules
     - Deploy Nginx with custom config
     - Deploy Node Exporter
  4. Use roles for organization
  5. Use variables and templates
  6. Run playbook and verify all servers are configured

VERIFY: ansible all -m shell -a "nginx -v" should work on all servers
```

### Lab 18: Docker in Production
```
TASK: Deploy a multi-container application
DO:
  1. Create a Docker Compose application with:
     - Nginx (reverse proxy)
     - Application (Node.js or Python)
     - Database (MySQL or PostgreSQL)
     - Redis (cache)
  2. Configure Docker networking
  3. Use Docker volumes for persistent data
  4. Implement health checks
  5. Set up log aggregation
  6. Configure resource limits
  7. Write a deployment script with zero-downtime update
  8. Set up Docker monitoring (cAdvisor + Prometheus)

VERIFY: Application works, survives container restarts, logs centralized
```

---

## LEVEL 4: EXPERT (Production & Scale)

### Lab 19: Full Infrastructure Build
```
TASK: Build complete production-like infrastructure
DO:
  Set up the following (use VMs, containers, or cloud instances):
  1. HAProxy x2 (with Keepalived VIP)
  2. Nginx web servers x3
  3. Application servers x2
  4. MySQL primary + replica
  5. NFS shared storage
  6. Prometheus + Grafana monitoring
  7. ELK centralized logging
  8. Ansible for deployment
  9. Backup system with rsync
  10. Proper firewall rules between tiers

  Architecture:
  Internet → HAProxy (VIP) → Nginx → App Server → MySQL
                                ↓
                        NFS (shared files)

VERIFY: Full end-to-end test, failover scenarios, monitoring alerts
```

### Lab 20: Incident Response Drill
```
TASK: Practice handling production incidents
SCENARIOS:
  1. "The website is down" → Diagnose and fix
     (Stop nginx, corrupt config, full disk, etc.)

  2. "The server is slow" → Run full diagnostic
     (CPU spike, memory leak, disk I/O, too many connections)

  3. "Users can't login" → Investigate authentication issues
     (LDAP down, PAM misconfigured, SSH key issues)

  4. "Disk is full" → Find and resolve
     (Large logs, deleted-but-open files, inode exhaustion)

  5. "Network issues" → Troubleshoot connectivity
     (DNS failure, routing issue, firewall blocking, MTU mismatch)

  6. "Database is slow" → Analyze and optimize
     (Missing indexes, slow queries, connection pool exhaustion)

FOR EACH: Document timeline, diagnosis steps, root cause, resolution, prevention
```

### Lab 21: Kernel Tuning Challenge
```
TASK: Optimize a server for 10,000+ concurrent connections
DO:
  1. Benchmark baseline with ab or wrk
  2. Tune sysctl (network buffers, connections, TCP stack)
  3. Tune file descriptor limits
  4. Tune Nginx for high concurrency
  5. Enable TCP BBR
  6. Tune I/O scheduler
  7. Benchmark after each change
  8. Document percentage improvement for each tuning

VERIFY: wrk -t12 -c10000 -d30s http://server/ shows improvement
```

### Lab 22: Security Audit
```
TASK: Perform a security audit on a Linux server
DO:
  1. Check for unnecessary services
  2. Scan for open ports (nmap)
  3. Check SSH configuration
  4. Review sudo permissions
  5. Check file permissions (SUID, world-writable)
  6. Review firewall rules
  7. Check for unpatched vulnerabilities
  8. Review password policies
  9. Check log monitoring is in place
  10. Verify backup procedures
  11. Run Lynis security audit: lynis audit system
  12. Document findings and remediation plan

VERIFY: Lynis score improves after remediation
```

### Lab 23: Write Your Own Monitoring Scripts
```
TASK: Create a comprehensive monitoring toolkit
DO:
  1. Script that monitors CPU, RAM, Disk, Network every minute
  2. Script that detects and alerts on anomalies (spike detection)
  3. Script that monitors SSL certificate expiry for 20+ domains
  4. Script that monitors service health (HTTP check, port check)
  5. Script that generates a daily system report (email + HTML)
  6. Script that monitors log files for error patterns
  7. Set up all scripts with cron/systemd timers
  8. Send alerts via email and/or Slack webhook

VERIFY: Scripts catch simulated issues within 1 minute
```

---

## PRACTICE SCHEDULE

```
Week 1-2:  Labs 1-5   (Fundamentals)
Week 3-4:  Labs 6-8   (Web & Security)
Week 5-6:  Labs 9-12  (Services & Storage)
Week 7-8:  Labs 13-16 (Performance & Monitoring)
Week 9-10: Labs 17-18 (Automation & Containers)
Week 11-12: Labs 19-23 (Production & Expert)

Daily Practice:
- SSH into a server and run diagnostics
- Read logs and find errors
- Practice grep/sed/awk one-liners
- Break something on purpose, then fix it
```
