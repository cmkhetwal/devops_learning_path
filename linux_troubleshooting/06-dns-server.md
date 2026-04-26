# 06 - DNS Server Setup (BIND)
## Complete DNS Configuration and Troubleshooting

---

## SECTION 1: BIND Installation

```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install bind bind-utils -y

# --- Ubuntu/Debian ---
apt install bind9 bind9utils dnsutils -y

systemctl enable --now named     # CentOS/RHEL
systemctl enable --now bind9     # Ubuntu
```

---

## SECTION 2: Main Configuration

```bash
# CentOS/RHEL: /etc/named.conf
# Ubuntu: /etc/bind/named.conf.options + named.conf.local

# /etc/named.conf (CentOS/RHEL full config)
options {
    listen-on port 53 { any; };
    listen-on-v6 port 53 { any; };
    directory "/var/named";
    dump-file "/var/named/data/cache_dump.db";
    statistics-file "/var/named/data/named_stats.txt";
    memstatistics-file "/var/named/data/named_mem_stats.txt";

    # Allow queries from trusted networks
    allow-query { localhost; 10.0.0.0/8; 192.168.0.0/16; 172.16.0.0/12; };

    # Allow recursive queries (for caching DNS)
    recursion yes;
    allow-recursion { localhost; 10.0.0.0/8; 192.168.0.0/16; };

    # Forwarders (upstream DNS)
    forwarders {
        8.8.8.8;
        8.8.4.4;
        1.1.1.1;
    };
    forward first;

    # Security
    dnssec-validation auto;
    auth-nxdomain no;

    # Rate limiting (DDoS protection)
    rate-limit {
        responses-per-second 10;
        window 5;
    };

    # Hide version
    version "not available";
};

# Logging
logging {
    channel default_log {
        file "/var/log/named/default.log" versions 5 size 50m;
        severity info;
        print-time yes;
        print-category yes;
    };
    channel query_log {
        file "/var/log/named/queries.log" versions 5 size 100m;
        severity info;
        print-time yes;
    };
    category default { default_log; };
    category queries { query_log; };
};

# Zone definitions
zone "." IN {
    type hint;
    file "named.ca";
};

zone "example.com" IN {
    type master;
    file "zones/example.com.zone";
    allow-update { none; };
    allow-transfer { 10.0.0.2; };    # Secondary DNS server
    also-notify { 10.0.0.2; };
};

# Reverse DNS zone
zone "1.168.192.in-addr.arpa" IN {
    type master;
    file "zones/192.168.1.rev";
    allow-update { none; };
    allow-transfer { 10.0.0.2; };
};
```

---

## SECTION 3: Zone Files

### 3.1 Forward Zone
```bash
# /var/named/zones/example.com.zone (CentOS)
# /etc/bind/zones/example.com.zone (Ubuntu)

$TTL 86400
$ORIGIN example.com.

@       IN  SOA     ns1.example.com. admin.example.com. (
                    2024010101  ; Serial (YYYYMMDDNN - increment on changes!)
                    3600        ; Refresh (1 hour)
                    1800        ; Retry (30 min)
                    604800      ; Expire (1 week)
                    86400       ; Minimum TTL (1 day)
)

; Nameservers
@           IN  NS      ns1.example.com.
@           IN  NS      ns2.example.com.

; A Records (IPv4)
@           IN  A       192.168.1.10
ns1         IN  A       192.168.1.1
ns2         IN  A       192.168.1.2
mail        IN  A       192.168.1.20
www         IN  A       192.168.1.10
app         IN  A       192.168.1.30
db          IN  A       192.168.1.40
monitoring  IN  A       192.168.1.50
vpn         IN  A       192.168.1.60

; AAAA Records (IPv6)
@           IN  AAAA    2001:db8::10

; CNAME Records (aliases)
ftp         IN  CNAME   www.example.com.
blog        IN  CNAME   www.example.com.
api         IN  CNAME   app.example.com.
webmail     IN  CNAME   mail.example.com.

; MX Records (Mail)
@           IN  MX  10  mail.example.com.
@           IN  MX  20  mail2.example.com.

; TXT Records
@           IN  TXT     "v=spf1 mx a ip4:192.168.1.20 -all"
_dmarc      IN  TXT     "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"
mail._domainkey IN TXT  "v=DKIM1; k=rsa; p=MIIBIjAN..."

; SRV Records
_sip._tcp   IN  SRV     10 60 5060 sip.example.com.

; CAA Record (Certificate Authority Authorization)
@           IN  CAA     0 issue "letsencrypt.org"
```

### 3.2 Reverse Zone
```bash
# /var/named/zones/192.168.1.rev

$TTL 86400
@   IN  SOA     ns1.example.com. admin.example.com. (
                2024010101
                3600
                1800
                604800
                86400
)

@   IN  NS      ns1.example.com.
@   IN  NS      ns2.example.com.

1   IN  PTR     ns1.example.com.
2   IN  PTR     ns2.example.com.
10  IN  PTR     www.example.com.
20  IN  PTR     mail.example.com.
30  IN  PTR     app.example.com.
40  IN  PTR     db.example.com.
```

```bash
# Set permissions
chown named:named /var/named/zones/*     # CentOS
chown bind:bind /etc/bind/zones/*        # Ubuntu

# Create log directory
mkdir -p /var/log/named
chown named:named /var/log/named

# Validate zone files
named-checkconf                                          # Validate BIND config syntax (/etc/named.conf)
named-checkzone example.com /var/named/zones/example.com.zone   # Check zone file; args: zone-name zone-file
named-checkzone 1.168.192.in-addr.arpa /var/named/zones/192.168.1.rev

systemctl restart named
```

---

## SECTION 4: Secondary (Slave) DNS Server

```bash
# On secondary server's named.conf
zone "example.com" IN {
    type slave;
    masters { 192.168.1.1; };    # Primary DNS IP
    file "slaves/example.com.zone";
};

zone "1.168.192.in-addr.arpa" IN {
    type slave;
    masters { 192.168.1.1; };
    file "slaves/192.168.1.rev";
};

# Force zone transfer
rndc retransfer example.com    # Force re-download of zone from master (ignores serial number)
```

---

## SECTION 5: DNS Troubleshooting

```bash
# Check BIND status
systemctl status named
journalctl -u named -f

# Query local DNS
dig @localhost example.com        # @localhost = query the local DNS server
dig @localhost example.com MX     # MX = query mail exchange records
dig @localhost example.com NS     # NS = query nameserver records
dig @localhost example.com ANY    # ANY = request all record types

# Reverse lookup
dig @localhost -x 192.168.1.10    # -x = reverse DNS lookup (IP to hostname)

# Trace full resolution
dig example.com +trace            # +trace = show each step of DNS resolution from root servers down

# Check zone transfer
dig @ns1.example.com example.com AXFR    # AXFR = request full zone transfer (all records)

# DNS response time
dig example.com | grep "Query time"

# Check cache
rndc dumpdb -cache              # Dump the DNS cache to file; -cache = dump cache (vs. -zones)
cat /var/named/data/cache_dump.db

# Flush cache
rndc flush                      # Clear all cached DNS records from memory

# Reload zone without restart
rndc reload example.com         # Reload a single zone's data without restarting BIND

# Statistics
rndc stats                      # Write server query/response statistics to stats file
cat /var/named/data/named_stats.txt

# Common issues:
# 1. SERVFAIL → Check zone file syntax: named-checkzone
# 2. REFUSED  → Check allow-query and allow-recursion
# 3. Slow     → Check forwarders, enable query logging
# 4. Zone not updating → Increment serial number!
# 5. Transfer failed → Check allow-transfer and firewall (port 53 TCP)
```

---

## SECTION 6: DNS Performance Tuning

```bash
# Increase cache size (default is based on RAM)
options {
    max-cache-size 512m;      # Set explicit cache size
    max-cache-ttl 86400;      # Max time to cache (1 day)
    max-ncache-ttl 3600;      # Max time to cache NXDOMAIN (1 hour)
};

# Enable Response Rate Limiting
rate-limit {
    responses-per-second 10;
    errors-per-second 5;
    nxdomains-per-second 5;
    slip 2;
    window 15;
};

# Worker threads (for high-traffic DNS)
options {
    recursive-clients 10000;
    tcp-clients 1000;
};

# Use unbound as a caching resolver in front of BIND
# (for very high query volume)
# CentOS: dnf install unbound
# Ubuntu: apt install unbound
```
