# 17 - User & Access Management
## LDAP, sudo, PAM, SSH, Key Management

---

## SECTION 1: User Management

```bash
# Add user
useradd -m -s /bin/bash -c "John Doe" john
# -m = create home directory
# -s = set login shell
# -c = comment/description (usually full name)
useradd -m -s /bin/bash -G wheel,developers john   # With groups
# -G = supplementary groups (comma-separated)

# Set password
passwd john
echo "john:SecurePass123!" | chpasswd               # Non-interactive (reads user:password pairs from stdin)

# Modify user
usermod -aG wheel john               # Add to sudo group (CentOS)
# -a = append (don't remove existing groups)
# -G = supplementary groups to add
usermod -aG sudo john                # Add to sudo group (Ubuntu)
usermod -aG docker,developers john   # Add to multiple groups
usermod -s /sbin/nologin john        # -s = set login shell (nologin disables interactive access)
usermod -L john                      # -L = lock account (prepends ! to password hash)
usermod -U john                      # -U = unlock account (removes ! from password hash)
usermod -e 2025-12-31 john           # -e = set account expiry date (YYYY-MM-DD)

# Delete user
userdel john                         # Delete user (keep home)
userdel -r john                      # -r = remove home directory and mail spool

# Groups
groupadd developers
groupdel developers
gpasswd -a john developers           # -a = add user to group
gpasswd -d john developers           # -d = delete user from group
groups john                          # Show user's groups
id john                              # Show UID, GID, groups

# Password policies
chage -l john                        # -l = list password aging info for user
chage -M 90 john                     # -M = set maximum password age (days)
chage -m 7 john                      # -m = set minimum password age (days)
chage -W 14 john                     # -W = set warning days before password expiry
chage -E 2025-12-31 john             # -E = set account expiration date
chage -d 0 john                      # -d = set last password change date (0 = force change on next login)

# Find users
getent passwd john                   # getent = query name service databases (passwd, group, etc.)
getent group developers              # Look up group entry including members
awk -F: '$3 >= 1000 && $3 < 65534' /etc/passwd  # Regular users
lastlog                              # Show last login time for all users
last                                 # Show recent login sessions from wtmp
last -f /var/log/wtmp               # -f = read from specific log file
lastb                                # Show failed login attempts (from /var/log/btmp)
who                                  # Currently logged in
w                                    # Who + what they're doing
```

---

## SECTION 2: sudo Configuration

```bash
# Edit sudoers (ALWAYS use visudo!)
visudo                               # Safe sudoers editor (validates syntax before saving, prevents lockout)

# Or use drop-in files (recommended)
# /etc/sudoers.d/developers
%developers ALL=(ALL) /usr/bin/systemctl restart nginx, /usr/bin/systemctl restart php-fpm

# /etc/sudoers.d/deploy
deploy ALL=(ALL) NOPASSWD: ALL                    # Full sudo, no password (deployment user)

# /etc/sudoers.d/dbadmins
%dbadmins ALL=(ALL) /usr/bin/systemctl * mysql, /usr/bin/mysql, /usr/bin/mysqldump

# Sudo syntax:
# WHO WHERE=(AS_WHOM) WHAT
# user host=(runas) command

# Examples:
john ALL=(ALL) ALL                                # Full sudo (with password)
john ALL=(ALL) NOPASSWD: ALL                      # Full sudo (no password)
john ALL=(ALL) /usr/bin/systemctl restart nginx    # Specific command only
%wheel ALL=(ALL) ALL                              # Group with sudo
%developers ALL=(ALL) NOPASSWD: /usr/bin/docker *  # Group, specific commands, no password

# Command aliases
Cmnd_Alias WEB_CMDS = /usr/bin/systemctl restart nginx, /usr/bin/systemctl reload nginx, /usr/bin/nginx -t
%webadmins ALL=(ALL) NOPASSWD: WEB_CMDS

# Audit sudo usage
grep sudo /var/log/secure        # CentOS
grep sudo /var/log/auth.log      # Ubuntu
journalctl _COMM=sudo

# Test sudo config
sudo -l                          # -l = list allowed (and forbidden) commands for current user
sudo -l -U john                  # -U = specify which user to check permissions for
visudo -c                        # -c = check sudoers syntax without editing
```

---

## SECTION 3: SSH Key Management

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "admin@example.com"                    # Best algorithm
# -t = key type (algorithm)
# -C = comment (label for the key)
ssh-keygen -t rsa -b 4096 -C "admin@example.com"                # RSA alternative
# -b = key size in bits
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N "" -C "deploy"    # Non-interactive
# -f = output file path
# -N = passphrase ("" = no passphrase)

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server
# -i = identity file (public key to copy)
ssh-copy-id -i ~/.ssh/id_ed25519.pub -p 2222 user@server
# -p = remote SSH port

# SSH config for multiple servers
cat > ~/.ssh/config << 'EOF'
# Default settings
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes

Host web-prod
    HostName 10.0.1.10
    User deploy
    IdentityFile ~/.ssh/deploy_key
    Port 2222

Host db-*
    User dbadmin
    IdentityFile ~/.ssh/db_key
    ProxyJump bastion

Host bastion
    HostName bastion.example.com
    User admin
    IdentityFile ~/.ssh/bastion_key

Host *.internal
    ProxyJump bastion
    User admin
EOF

# Usage:
ssh web-prod                     # Uses config automatically
ssh db-master                    # Goes through bastion

# SSH Agent
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
ssh-add -l                       # -l = list fingerprints of loaded keys

# SSH tunneling
# Local port forward (access remote service locally)
ssh -L 3306:localhost:3306 user@dbserver          # -L = local port forward (local:remote_host:remote_port)
ssh -L 8080:internal-web:80 user@bastion          # Access internal web via bastion

# Remote port forward (expose local service on remote)
ssh -R 9090:localhost:9090 user@remote             # -R = remote port forward (expose local service on remote)

# Dynamic SOCKS proxy
ssh -D 1080 user@remote                            # -D = dynamic SOCKS proxy on specified local port

# Manage authorized_keys
# ~/.ssh/authorized_keys - restrict specific keys:
command="/usr/local/bin/backup-only.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAA... backup-key
from="10.0.0.0/8",no-pty ssh-ed25519 AAAA... restricted-key
```

---

## SECTION 4: PAM (Pluggable Authentication Modules)

```bash
# PAM config location:
# /etc/pam.d/               # Per-service configs
# /etc/security/             # Security configs

# Common PAM files:
# /etc/pam.d/sshd           # SSH authentication
# /etc/pam.d/login          # Console login
# /etc/pam.d/su             # su command
# /etc/pam.d/sudo           # sudo command
# /etc/pam.d/system-auth    # System-wide (CentOS)
# /etc/pam.d/common-auth    # System-wide (Ubuntu)

# Password complexity (/etc/security/pwquality.conf)
minlen = 12                  # Minimum length
dcredit = -1                 # At least 1 digit
ucredit = -1                 # At least 1 uppercase
lcredit = -1                 # At least 1 lowercase
ocredit = -1                 # At least 1 special character
maxrepeat = 3                # Max repeated characters

# Account lockout (/etc/pam.d/system-auth or /etc/pam.d/common-auth)
# Add BEFORE pam_unix.so:
auth required pam_faillock.so preauth deny=5 unlock_time=900
auth required pam_faillock.so authfail deny=5 unlock_time=900
# deny=5 → Lock after 5 failures
# unlock_time=900 → Unlock after 15 minutes

# Check locked accounts
faillock --user john                 # Show failed login attempts for user

# Unlock account
faillock --user john --reset         # --reset = clear failed login counter (unlock account)

# Restrict su to wheel group
# /etc/pam.d/su
auth required pam_wheel.so use_uid

# Login time restrictions
# /etc/security/time.conf
# service;ttys;users;times
sshd;*;john;!SaSu0000-2400     # Deny SSH on weekends
```

---

## SECTION 5: LDAP Client Configuration

```bash
# Install LDAP client
# CentOS/RHEL:
dnf install openldap-clients sssd sssd-ldap oddjob-mkhomedir -y
# Ubuntu:
apt install sssd sssd-ldap ldap-utils oddjob-mkhomedir -y
```

```ini
# /etc/sssd/sssd.conf
[sssd]
services = nss, pam
config_file_version = 2
domains = example.com

[domain/example.com]
id_provider = ldap
auth_provider = ldap
ldap_uri = ldaps://ldap.example.com
ldap_search_base = dc=example,dc=com
ldap_id_use_start_tls = true
ldap_tls_reqcert = demand
ldap_tls_cacert = /etc/ssl/certs/ca-certificates.crt
cache_credentials = true
enumerate = false

# User/group mapping
ldap_user_search_base = ou=People,dc=example,dc=com
ldap_group_search_base = ou=Groups,dc=example,dc=com

# Home directory
override_homedir = /home/%u
default_shell = /bin/bash
```

```bash
chmod 600 /etc/sssd/sssd.conf
systemctl enable --now sssd oddjobd

# Enable mkhomedir (auto-create home on first login)
authselect select sssd with-mkhomedir --force   # authselect = configure auth profiles; --force = overwrite existing config
pam-auth-update --enable mkhomedir               # Ubuntu

# Test LDAP
ldapsearch -x -H ldaps://ldap.example.com -b "dc=example,dc=com" "(uid=john)"
# -x = use simple authentication (not SASL)
# -H = LDAP server URI
# -b = search base DN (starting point for search)
getent passwd john
id john
```

---

## SECTION 6: File Permissions & ACLs

```bash
# Standard permissions
chmod 755 directory/        # rwxr-xr-x (owner=rwx, group=r-x, others=r-x)
chmod 644 file.txt          # rw-r--r-- (owner=rw, group=r, others=r)
chmod 600 private.key       # rw------- (owner=rw, no access for group/others)
chmod u+x script.sh         # u = owner, + = add, x = execute permission
chmod g+w file.txt           # g = group, + = add, w = write permission
chmod o-r file.txt           # o = others, - = remove, r = read permission

# Ownership
chown user:group file.txt
chown -R www-data:www-data /var/www/    # -R = recursive (apply to all files/subdirectories)

# Special permissions
chmod u+s /usr/bin/program   # SUID (Set User ID) - process runs as file owner, not executing user
chmod g+s /shared/dir/       # SGID (Set Group ID) - new files inherit directory's group
chmod +t /tmp/               # Sticky bit - only file owner (or root) can delete files in directory

# ACLs (Advanced permissions)
# Install: dnf/apt install acl
setfacl -m u:john:rwx /shared/project/          # -m = modify ACL; u:user:perms syntax
setfacl -m g:developers:rx /shared/project/      # g:group:perms = set ACL for a group
setfacl -m d:g:developers:rwx /shared/project/   # d: = default ACL (inherited by new files)
getfacl /shared/project/                          # getfacl = display ACL entries for file/directory
setfacl -x u:john /shared/project/               # -x = remove specific ACL entry
setfacl -b /shared/project/                       # -b = remove all ACL entries

# Find files with specific permissions
find / -perm -4000 -type f 2>/dev/null           # -perm -4000 = find files with SUID bit set
find / -perm -2000 -type f 2>/dev/null           # -perm -2000 = find files with SGID bit set
find / -perm -o+w -type f 2>/dev/null            # -perm -o+w = find files writable by others (world-writable)
find /home -nouser -o -nogroup 2>/dev/null       # -nouser = no matching user; -o = OR; -nogroup = no matching group
```
