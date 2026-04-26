# Linux Administration & Troubleshooting - Complete Guide
## For Managing 1000+ Server Farms | All Distros: CentOS/RHEL, Ubuntu/Debian, Amazon Linux

---

## Document Structure

This guide is split into multiple files for easy navigation:

| # | File | Topics |
|---|------|--------|
| 01 | [System Performance Troubleshooting](01-system-performance.md) | CPU, RAM, Disk, Network, Process analysis, Slow server diagnosis |
| 02 | [Infrastructure Monitoring](02-monitoring.md) | Nagios, Zabbix, Prometheus+Grafana, ELK Stack, CloudWatch |
| 03 | [Web Servers - Apache & Nginx](03-web-servers.md) | Install, Configure, Virtual Hosts, SSL, Performance Tuning |
| 04 | [HAProxy & Load Balancing](04-haproxy-loadbalancing.md) | Setup, Algorithms, Health Checks, SSL Termination |
| 05 | [Mail Server Setup](05-mail-server.md) | Postfix, Dovecot, SPF, DKIM, DMARC, Troubleshooting |
| 06 | [DNS Server Setup](06-dns-server.md) | BIND, Zone files, Forward/Reverse, Troubleshooting |
| 07 | [Firewall & Security](07-firewall-security.md) | iptables, firewalld, nftables, SELinux, AppArmor, Fail2ban |
| 08 | [SSL/TLS Certificates](08-certificates.md) | Self-signed, Let's Encrypt, Custom CA, Wildcard, Renewal |
| 09 | [Performance Tuning](09-performance-tuning.md) | Kernel, Nginx, Apache, MySQL, Network Stack tuning |
| 10 | [Text Processing - grep, sed, awk](10-text-processing.md) | Filtering, Pattern matching, Log analysis, One-liners |
| 11 | [Log Management & Analysis](11-log-management.md) | journalctl, rsyslog, logrotate, centralized logging |
| 12 | [Storage & Filesystem](12-storage-filesystem.md) | LVM, RAID, NFS, disk management, filesystem repair |
| 13 | [Networking Deep Dive](13-networking.md) | Bonding, VLAN, Routing, tcpdump, ss, troubleshooting |
| 14 | [Automation & Config Management](14-automation.md) | Ansible, Shell scripting, Cron, Systemd timers |
| 15 | [Container & Virtualization](15-containers.md) | Docker, Podman, KVM, basics for server admins |
| 16 | [Backup & Disaster Recovery](16-backup-dr.md) | rsync, tar, snapshots, DR planning |
| 17 | [User & Access Management](17-user-access.md) | LDAP, sudo, PAM, SSH hardening, key management |
| 18 | [Practical Exercises](18-practicals.md) | 50+ hands-on labs from beginner to expert |
| 19 | [Quick Reference & Cheat Sheets](19-cheat-sheets.md) | One-page references, emergency procedures |
| 20 | [Large-Scale Farm Management](20-farm-management.md) | Strategies for 1000+ servers, patching, compliance |
| 21 | [PHP & PHP-FPM Troubleshooting](21-php-fpm-troubleshooting.md) | Install, Pool Tuning, OPcache, Nginx/Apache, RDS, Redis |

---

## Package Manager Quick Reference (Used Throughout)

| Action | CentOS/RHEL 7 | CentOS/RHEL 8+/Amazon Linux 2023 | Ubuntu/Debian |
|--------|---------------|-----------------------------------|---------------|
| Install | `yum install pkg` | `dnf install pkg` | `apt install pkg` |
| Remove | `yum remove pkg` | `dnf remove pkg` | `apt remove pkg` |
| Update all | `yum update` | `dnf update` | `apt update && apt upgrade` |
| Search | `yum search pkg` | `dnf search pkg` | `apt search pkg` |
| Info | `yum info pkg` | `dnf info pkg` | `apt show pkg` |
| List installed | `yum list installed` | `dnf list installed` | `dpkg -l` |
| File owner | `rpm -qf /path` | `rpm -qf /path` | `dpkg -S /path` |
| Repo list | `yum repolist` | `dnf repolist` | `cat /etc/apt/sources.list` |

## Service Management (systemd - All Modern Distros)

```bash
systemctl start|stop|restart|reload SERVICE
systemctl enable|disable SERVICE
systemctl status SERVICE
systemctl is-active SERVICE
systemctl is-enabled SERVICE
systemctl list-units --type=service --state=running
systemctl list-units --type=service --state=failed
journalctl -u SERVICE -f          # Follow logs
journalctl -u SERVICE --since "1 hour ago"
```
