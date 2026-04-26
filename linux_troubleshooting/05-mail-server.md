# 05 - Mail Server Setup
## Postfix + Dovecot + SPF + DKIM + DMARC

---

## SECTION 1: Postfix (SMTP - Sending/Receiving Mail)

### 1.1 Installation
```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install postfix cyrus-sasl cyrus-sasl-plain -y

# --- Ubuntu/Debian ---
apt install postfix libsasl2-modules -y
# Choose "Internet Site" during install

systemctl enable --now postfix
```

### 1.2 Main Configuration
```bash
# /etc/postfix/main.cf

# Basic settings
myhostname = mail.example.com
mydomain = example.com
myorigin = $mydomain
inet_interfaces = all
inet_protocols = ipv4
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain

# Network settings
mynetworks = 127.0.0.0/8, 10.0.0.0/8, 192.168.0.0/16
relay_domains =
relayhost =

# Mailbox settings
home_mailbox = Maildir/
# Or use Dovecot LDA:
# mailbox_transport = lmtp:unix:private/dovecot-lmtp

# Size limits
message_size_limit = 52428800       # 50MB max message
mailbox_size_limit = 1073741824     # 1GB max mailbox

# TLS/SSL Configuration
smtpd_use_tls = yes
smtpd_tls_cert_file = /etc/letsencrypt/live/mail.example.com/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/mail.example.com/privkey.pem
smtpd_tls_security_level = may
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_security_level = may
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# SASL Authentication
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_auth_enable = yes
smtpd_sasl_security_options = noanonymous
smtpd_sasl_local_domain = $myhostname

# Restrictions (anti-spam)
smtpd_helo_required = yes
smtpd_helo_restrictions =
    permit_mynetworks,
    reject_non_fqdn_helo_hostname,
    reject_invalid_helo_hostname

smtpd_sender_restrictions =
    permit_mynetworks,
    reject_non_fqdn_sender,
    reject_unknown_sender_domain

smtpd_recipient_restrictions =
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination,
    reject_non_fqdn_recipient,
    reject_unknown_recipient_domain,
    reject_rbl_client zen.spamhaus.org,
    reject_rbl_client bl.spamcop.net

# Milter (for DKIM)
milter_protocol = 6
milter_default_action = accept
smtpd_milters = inet:127.0.0.1:8891
non_smtpd_milters = inet:127.0.0.1:8891
```

### 1.3 Submission Port (587) for Mail Clients
```bash
# /etc/postfix/master.cf - Uncomment/add:
submission inet n       -       n       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_tls_auth_only=yes
  -o smtpd_reject_unlisted_recipient=no
  -o smtpd_recipient_restrictions=permit_sasl_authenticated,reject
  -o milter_macro_daemon_name=ORIGINATING

# Also enable smtps (465) for legacy clients:
smtps     inet  n       -       n       -       -       smtpd
  -o syslog_name=postfix/smtps
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_reject_unlisted_recipient=no
  -o smtpd_recipient_restrictions=permit_sasl_authenticated,reject
```

---

## SECTION 2: Dovecot (IMAP/POP3 - Reading Mail)

### 2.1 Installation
```bash
# --- CentOS/RHEL ---
dnf install dovecot -y

# --- Ubuntu/Debian ---
apt install dovecot-core dovecot-imapd dovecot-pop3d dovecot-lmtpd -y

systemctl enable --now dovecot
```

### 2.2 Configuration
```bash
# /etc/dovecot/dovecot.conf
protocols = imap pop3 lmtp

# /etc/dovecot/conf.d/10-mail.conf
mail_location = maildir:~/Maildir
namespace inbox {
    inbox = yes
}

# /etc/dovecot/conf.d/10-auth.conf
disable_plaintext_auth = yes
auth_mechanisms = plain login

# /etc/dovecot/conf.d/10-ssl.conf
ssl = required
ssl_cert = </etc/letsencrypt/live/mail.example.com/fullchain.pem
ssl_key = </etc/letsencrypt/live/mail.example.com/privkey.pem
ssl_min_protocol = TLSv1.2

# /etc/dovecot/conf.d/10-master.conf
# SASL auth for Postfix
service auth {
    unix_listener /var/spool/postfix/private/auth {
        mode = 0660
        user = postfix
        group = postfix
    }
}

service lmtp {
    unix_listener /var/spool/postfix/private/dovecot-lmtp {
        mode = 0600
        user = postfix
        group = postfix
    }
}
```

---

## SECTION 3: DKIM (DomainKeys Identified Mail)

```bash
# Install OpenDKIM
# CentOS/RHEL:
dnf install opendkim opendkim-tools -y
# Ubuntu/Debian:
apt install opendkim opendkim-tools -y

# Generate DKIM key
mkdir -p /etc/opendkim/keys/example.com
opendkim-genkey -b 2048 -d example.com -D /etc/opendkim/keys/example.com -s mail -v
# -b 2048 = key size in bits
# -d = domain the key is for
# -D = directory to store the generated key files
# -s = selector name (used in DNS record lookup)
# -v = verbose output
chown -R opendkim:opendkim /etc/opendkim
```

```bash
# /etc/opendkim.conf
Mode                sv
Syslog              yes
SyslogSuccess       yes
LogWhy              yes
Canonicalization    relaxed/simple
Domain              example.com
Selector            mail
KeyFile             /etc/opendkim/keys/example.com/mail.private
Socket              inet:8891@127.0.0.1
PidFile             /run/opendkim/opendkim.pid
UserID              opendkim:opendkim
TrustAnchorFile     /usr/share/dns/root.key
```

```bash
systemctl enable --now opendkim

# Get DNS TXT record to add:
cat /etc/opendkim/keys/example.com/mail.txt
# Add this as a TXT record: mail._domainkey.example.com
```

---

## SECTION 4: SPF, DKIM, DMARC DNS Records

```bash
# SPF Record (TXT record on example.com)
# Allows mail from your server IP and MX servers
v=spf1 mx a ip4:YOUR_SERVER_IP -all

# DKIM Record (TXT record on mail._domainkey.example.com)
# (content from opendkim-genkey output above)

# DMARC Record (TXT record on _dmarc.example.com)
v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com; ruf=mailto:dmarc@example.com; fo=1; adkim=s; aspf=s; pct=100

# Reverse DNS (PTR record)
# Set PTR for your mail server IP to mail.example.com
# (Done through your hosting provider / ISP)

# MX Record
# example.com  MX  10  mail.example.com
```

---

## SECTION 5: Mail Troubleshooting

```bash
# Check mail queue
postqueue -p               # -p = print/display the mail queue
mailq                      # Same as above
postqueue -f               # -f = flush queue (retry delivery of all queued mail)
postsuper -d ALL           # -d = delete; ALL removes every queued message (careful!)
postsuper -d QUEUE_ID      # -d QUEUE_ID = delete a specific message by its queue ID

# View message in queue
postcat -q QUEUE_ID        # -q = look up and display a message by queue ID

# Check mail logs
tail -f /var/log/maillog          # CentOS/RHEL
tail -f /var/log/mail.log         # Ubuntu

# Test SMTP connection
telnet mail.example.com 25
# EHLO test.com
# MAIL FROM:<test@test.com>
# RCPT TO:<user@example.com>
# DATA
# Subject: Test
# This is a test
# .
# QUIT

# Test with openssl (TLS)
openssl s_client -connect mail.example.com:587 -starttls smtp
# -connect = server:port to connect to
# -starttls smtp = upgrade plain connection to TLS using SMTP protocol
openssl s_client -connect mail.example.com:993    # IMAPS (port 993 = IMAP over SSL/TLS)

# Check DNS records
dig example.com MX +short          # MX = query mail exchange records, +short = concise output
dig example.com TXT +short         # TXT = query text records (SPF, DKIM, etc.)
dig mail._domainkey.example.com TXT +short
dig _dmarc.example.com TXT +short

# Test DKIM
opendkim-testkey -d example.com -s mail -vvv
# -d = domain to test
# -s = selector to look up
# -vvv = maximum verbosity (triple verbose)

# Send test mail
echo "Test body" | mail -s "Test Subject" user@example.com    # -s = subject line

# Check Postfix configuration
postconf -n    # -n = show only settings that differ from defaults
postconf -d    # -d = show all default parameter values

# Common issues:
# 1. Port 25 blocked → Check firewall, cloud provider (AWS blocks 25 by default)
# 2. Mail rejected → Check SPF/DKIM/DMARC records
# 3. Relay denied → Check mynetworks and smtpd_recipient_restrictions
# 4. TLS errors → Check certificate paths and permissions
# 5. Authentication failed → Check SASL config and Dovecot auth socket
```
