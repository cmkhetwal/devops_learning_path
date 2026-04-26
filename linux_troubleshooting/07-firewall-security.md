# 07 - Firewall & Security
## iptables, firewalld, nftables, SELinux, AppArmor, Fail2ban

---

## SECTION 1: firewalld (CentOS/RHEL 7+, Fedora)

### 1.1 Basic Commands
```bash
# Status
systemctl status firewalld
firewall-cmd --state                             # Check if firewalld is running

# Zones (default: public)
firewall-cmd --get-zones                         # List all available zones
firewall-cmd --get-default-zone                  # Show which zone is the default
firewall-cmd --get-active-zones                  # Show zones with assigned interfaces/sources
firewall-cmd --list-all                          # Show all rules in the default zone
firewall-cmd --list-all --zone=public

# Add services (predefined)
firewall-cmd --add-service=http --permanent      # --permanent = persist across reboots (requires --reload)
firewall-cmd --add-service=https --permanent
firewall-cmd --add-service=ssh --permanent
firewall-cmd --add-service=dns --permanent
firewall-cmd --add-service=smtp --permanent
firewall-cmd --add-service=ntp --permanent
firewall-cmd --reload                            # Reload to apply --permanent changes

# Add custom ports
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --add-port=3000-3010/tcp --permanent
firewall-cmd --add-port=161/udp --permanent
firewall-cmd --reload

# Remove rules
firewall-cmd --remove-service=http --permanent
firewall-cmd --remove-port=8080/tcp --permanent
firewall-cmd --reload

# List services/ports
firewall-cmd --list-services
firewall-cmd --list-ports

# Allow specific source IP (rich rules allow complex conditions beyond simple service/port)
firewall-cmd --add-rich-rule='rule family="ipv4" source address="10.0.0.0/8" service name="ssh" accept' --permanent

# Block an IP
firewall-cmd --add-rich-rule='rule family="ipv4" source address="1.2.3.4" reject' --permanent

# Port forwarding
firewall-cmd --add-forward-port=port=80:proto=tcp:toport=8080 --permanent
firewall-cmd --add-forward-port=port=80:proto=tcp:toaddr=192.168.1.10:toport=80 --permanent

# Enable masquerading (NAT)
firewall-cmd --add-masquerade --permanent

# Create custom zone
firewall-cmd --new-zone=webservers --permanent
firewall-cmd --reload
firewall-cmd --zone=webservers --add-source=10.0.1.0/24 --permanent
firewall-cmd --zone=webservers --add-service=http --permanent
firewall-cmd --zone=webservers --add-service=https --permanent
firewall-cmd --reload
```

---

## SECTION 2: iptables (All Distros - Legacy but Important)

### 2.1 Understanding iptables
```
Tables: filter (default), nat, mangle, raw
Chains: INPUT (incoming), OUTPUT (outgoing), FORWARD (routing)
Actions: ACCEPT, DROP, REJECT, LOG, DNAT, SNAT, MASQUERADE
```

### 2.2 Common Rules
```bash
# View current rules
iptables -L -n -v                     # -L = list rules, -n = numeric (no DNS), -v = verbose (counters)
iptables -L -n -v --line-numbers      # --line-numbers = show rule position (for insert/delete)
iptables -t nat -L -n -v              # -t nat = operate on the NAT table instead of default filter

# FLUSH all rules (CAREFUL - locks you out if remote!)
# Always set default ACCEPT before flushing if remote
iptables -P INPUT ACCEPT              # -P = set default policy for chain
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -F                           # -F = flush (delete) all rules in all chains
iptables -X                           # -X = delete all user-defined chains
iptables -t nat -F

# --- Complete Server Firewall Script ---
#!/bin/bash
# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F

# Default policies
iptables -P INPUT DROP                # -P = set default policy; DROP = deny all unmatched inbound
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT    # -A = append rule, -i = match input interface, -j = jump to target action
iptables -A OUTPUT -o lo -j ACCEPT   # -o = match output interface

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# -m state = load connection-tracking module, --state = match connection states

# Allow SSH (rate limited)
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set --name SSH
# -p tcp = match TCP protocol, --dport = destination port
# -m recent --set = add source IP to tracking list, --name = name for the tracking list
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 --name SSH -j DROP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow DNS
iptables -A INPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --dport 53 -j ACCEPT

# Allow SMTP/IMAP
iptables -A INPUT -p tcp --dport 25 -j ACCEPT
iptables -A INPUT -p tcp --dport 587 -j ACCEPT
iptables -A INPUT -p tcp --dport 993 -j ACCEPT

# Allow ICMP (ping)
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# Allow from specific network
iptables -A INPUT -s 10.0.0.0/8 -j ACCEPT

# Block specific IP
iptables -A INPUT -s 1.2.3.4 -j DROP

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "IPTables-Dropped: " --log-level 4
# --log-prefix = string prepended to log messages for easy filtering
iptables -A INPUT -j DROP

# Save rules
# CentOS/RHEL:
iptables-save > /etc/sysconfig/iptables    # iptables-save = dump all current rules to stdout
# Or install iptables-services:
# dnf install iptables-services
# systemctl enable iptables
# service iptables save

# Ubuntu/Debian:
iptables-save > /etc/iptables/rules.v4       # iptables-restore reads this file to reload rules
# Or install:
# apt install iptables-persistent
# netfilter-persistent save
```

### 2.3 NAT and Port Forwarding
```bash
# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
# Permanent: echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf

# SNAT (Source NAT - outbound)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# DNAT (Destination NAT - port forwarding)
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.1.10:80
iptables -A FORWARD -p tcp -d 192.168.1.10 --dport 80 -j ACCEPT

# Redirect local port
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```

---

## SECTION 3: nftables (Modern Replacement for iptables)

```bash
# Install
# CentOS/RHEL 8+: Already default
# Ubuntu 20.04+: apt install nftables

# View rules
nft list ruleset                    # Display all tables, chains, and rules

# Basic server firewall
nft flush ruleset                   # Delete all existing nft rules
nft add table inet filter           # Create table; inet = IPv4+IPv6 family
nft add chain inet filter input { type filter hook input priority 0\; policy drop\; }
# add chain = create chain in table; hook input = attach to incoming packets; policy drop = default deny
nft add chain inet filter forward { type filter hook forward priority 0\; policy drop\; }
nft add chain inet filter output { type filter hook output priority 0\; policy accept\; }

# Allow loopback
nft add rule inet filter input iif lo accept
# add rule [family] [table] [chain] = append a rule; iif = input interface

# Allow established
nft add rule inet filter input ct state established,related accept
# ct state = conntrack state matching

# Allow SSH, HTTP, HTTPS
nft add rule inet filter input tcp dport { 22, 80, 443 } accept
# tcp dport = match TCP destination port; { } = set of ports

# Allow ping
nft add rule inet filter input icmp type echo-request accept

# Allow from subnet
nft add rule inet filter input ip saddr 10.0.0.0/8 accept

# Log and drop
nft add rule inet filter input log prefix \"nft-drop: \" drop

# Save
nft list ruleset > /etc/nftables.conf
systemctl enable nftables
```

---

## SECTION 4: SELinux (CentOS/RHEL/Amazon Linux)

```bash
# Check SELinux status
getenforce                    # Print current SELinux mode (Enforcing, Permissive, or Disabled)
sestatus                      # Detailed status

# Modes
setenforce 0                  # Set Permissive mode (log but don't block); 0 = permissive
setenforce 1                  # Set Enforcing mode (actively block violations); 1 = enforcing
# Permanent: edit /etc/selinux/config
# SELINUX=enforcing|permissive|disabled

# Check for SELinux denials
ausearch -m avc -ts recent    # -m avc = search for SELinux denial messages, -ts recent = last 10 minutes
audit2why < /var/log/audit/audit.log | tail -50    # audit2why = explain why SELinux denied access
sealert -a /var/log/audit/audit.log    # Requires setroubleshoot

# Common SELinux issues and fixes

# Allow httpd to connect to network (for reverse proxy)
setsebool -P httpd_can_network_connect 1    # -P = persistent (survive reboots)

# Allow httpd to send mail
setsebool -P httpd_can_sendmail 1

# Allow httpd to access home directories
setsebool -P httpd_enable_homedirs 1

# Allow Nginx to bind to non-standard port
semanage port -a -t http_port_t -p tcp 8080
# -a = add record, -t = SELinux type label, -p = protocol

# Fix file context (e.g., custom web root)
semanage fcontext -a -t httpd_sys_content_t "/var/www/mysite(/.*)?"
# fcontext -a = add file context rule, -t = SELinux type to assign
restorecon -Rv /var/www/mysite     # -R = recursive, -v = verbose; reapply SELinux contexts from policy

# List booleans related to httpd
getsebool -a | grep httpd              # -a = list all SELinux boolean values

# Generate custom policy from denials
ausearch -m avc -ts recent | audit2allow -M mypolicy
# audit2allow = generate an allow policy from denial logs; -M = create a loadable module
semodule -i mypolicy.pp              # -i = install the compiled SELinux policy module

# List all port labels
semanage port -l | grep http
```

---

## SECTION 5: AppArmor (Ubuntu/Debian)

```bash
# Check status
aa-status                              # Show loaded profiles and their modes (enforce/complain)
apparmor_status                        # Same as aa-status

# List profiles
aa-status | head -30

# Modes:
# enforce  - Block violations
# complain - Log but allow
# disable  - Profile inactive

# Put profile in complain mode
aa-complain /usr/sbin/nginx            # Switch profile to complain mode (log violations, don't block)

# Put profile in enforce mode
aa-enforce /usr/sbin/nginx             # Switch profile to enforce mode (block violations)

# Disable a profile
ln -s /etc/apparmor.d/usr.sbin.nginx /etc/apparmor.d/disable/
apparmor_parser -R /etc/apparmor.d/usr.sbin.nginx

# Check logs for denials
journalctl | grep apparmor | tail -20
grep "apparmor" /var/log/syslog | tail -20

# Reload all profiles
systemctl reload apparmor
```

---

## SECTION 6: Fail2ban (Brute Force Protection)

```bash
# Install
# CentOS/RHEL:
dnf install epel-release -y && dnf install fail2ban -y
# Ubuntu/Debian:
apt install fail2ban -y
```

```ini
# /etc/fail2ban/jail.local (create this file - don't edit jail.conf)
[DEFAULT]
bantime = 3600           # Ban for 1 hour
findtime = 600           # Look at last 10 minutes
maxretry = 5             # 5 failures = ban
ignoreip = 127.0.0.1/8 10.0.0.0/8
banaction = firewallcmd-rich-rules     # CentOS with firewalld
# banaction = iptables-multiport       # iptables
destemail = admin@example.com
sender = fail2ban@example.com
action = %(action_mwl)s                # Ban + mail with logs

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/secure              # CentOS
# logpath = /var/log/auth.log          # Ubuntu
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[apache-auth]
enabled = true
filter = apache-auth
port = http,https
logpath = /var/log/httpd/*error_log    # CentOS
# logpath = /var/log/apache2/*error.log # Ubuntu

[postfix]
enabled = true
filter = postfix
port = smtp,465,587
logpath = /var/log/maillog             # CentOS
# logpath = /var/log/mail.log          # Ubuntu

[dovecot]
enabled = true
filter = dovecot
port = pop3,pop3s,imap,imaps
logpath = /var/log/maillog
```

```bash
systemctl enable --now fail2ban

# Check status
fail2ban-client status
fail2ban-client status sshd            # Show ban stats and banned IPs for the sshd jail

# Unban an IP
fail2ban-client set sshd unbanip 1.2.3.4    # Remove a specific IP from the sshd jail ban list

# Ban an IP manually
fail2ban-client set sshd banip 1.2.3.4

# Check banned IPs
fail2ban-client get sshd banned

# Test filter regex
fail2ban-regex /var/log/secure /etc/fail2ban/filter.d/sshd.conf
# fail2ban-regex = test a filter's regex against a log file to verify matches
```

---

## SECTION 7: SSH Hardening

```bash
# /etc/ssh/sshd_config - Security settings

# Change default port
Port 2222

# Disable root login
PermitRootLogin no

# Use only SSH Protocol 2
Protocol 2

# Disable password authentication (key-only)
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Limit users
AllowUsers admin deployer
# AllowGroups sshusers

# Idle timeout
ClientAliveInterval 300
ClientAliveCountMax 2

# Max authentication attempts
MaxAuthTries 3

# Disable empty passwords
PermitEmptyPasswords no

# Disable X11 forwarding
X11Forwarding no

# Disable TCP forwarding (if not needed)
AllowTcpForwarding no

# Banner
Banner /etc/ssh/banner

# Logging
LogLevel VERBOSE
```

```bash
# Generate strong SSH key
ssh-keygen -t ed25519 -C "admin@example.com"    # -t = key type, -C = comment/label for the key
ssh-keygen -t rsa -b 4096 -C "admin@example.com" # -b = key size in bits

# Copy key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server    # -i = identity file (public key) to copy

# Test config before restarting
sshd -t                                              # -t = test mode; validate config syntax without starting
systemctl restart sshd
```
