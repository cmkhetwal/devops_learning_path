# 08 - SSL/TLS Certificates
## Self-Signed, Let's Encrypt, Custom CA, Wildcard

---

## SECTION 1: Understanding Certificates

```
Certificate Chain:
  Root CA (trusted by browsers/OS)
    └── Intermediate CA
          └── Server Certificate (your cert)

Files you work with:
  .key  = Private key (KEEP SECRET!)
  .csr  = Certificate Signing Request (sent to CA)
  .crt  = Certificate (public)
  .pem  = Base64 encoded (can contain cert, key, or chain)
  .p12/.pfx = PKCS#12 bundle (cert + key, password protected)
  .ca-bundle = Intermediate + Root certificates
```

---

## SECTION 2: Self-Signed Certificates

### 2.1 Quick Self-Signed (Development/Internal)
```bash
# Generate private key + self-signed certificate (1 command)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/selfsigned.key \
    -out /etc/ssl/certs/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Company/OU=IT/CN=server.example.com"
# req = certificate request / generation command
# -x509 = output a self-signed cert instead of a CSR
# -nodes = no DES; don't encrypt the private key with a passphrase
# -days 365 = certificate validity period
# -newkey rsa:2048 = generate a new 2048-bit RSA key
# -keyout = file path to write the private key
# -out = file path to write the certificate
# -subj = subject fields inline (skip interactive prompts)

# Set permissions
chmod 600 /etc/ssl/private/selfsigned.key
chmod 644 /etc/ssl/certs/selfsigned.crt
```

### 2.2 Self-Signed with SAN (Subject Alternative Names)
```bash
# Create config file for SAN
cat > /tmp/san.cnf << 'EOF'
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C = US
ST = State
L = City
O = Company
OU = IT
CN = server.example.com

[v3_req]
subjectAltName = @alt_names
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = server.example.com
DNS.2 = www.example.com
DNS.3 = *.example.com
IP.1 = 192.168.1.10
IP.2 = 10.0.0.10
EOF

# Generate key and certificate with SAN
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/server.key \
    -out /etc/ssl/certs/server.crt \
    -config /tmp/san.cnf \
    -extensions v3_req

# Verify SAN is included
openssl x509 -in /etc/ssl/certs/server.crt -text -noout | grep -A 5 "Subject Alternative"
# -text = display certificate in human-readable form, -noout = suppress PEM output
```

---

## SECTION 3: Let's Encrypt (Free, Automated, Trusted)

### 3.1 Install Certbot
```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install epel-release -y
dnf install certbot python3-certbot-nginx python3-certbot-apache -y

# --- Ubuntu/Debian ---
apt install certbot python3-certbot-nginx python3-certbot-apache -y
```

### 3.2 Obtain Certificates

```bash
# --- Method 1: Nginx plugin (easiest) ---
certbot --nginx -d example.com -d www.example.com
# --nginx = use Nginx plugin to auto-configure SSL, -d = domain name(s)

# --- Method 2: Apache plugin ---
certbot --apache -d example.com -d www.example.com

# --- Method 3: Standalone (no web server running) ---
certbot certonly --standalone -d example.com -d www.example.com
# certonly = obtain cert without installing it, --standalone = spin up a temp web server on port 80

# --- Method 4: Webroot (web server already running) ---
certbot certonly --webroot -w /var/www/html -d example.com -d www.example.com
# --webroot = place challenge files in existing web root, -w = web root directory path

# --- Method 5: DNS challenge (for wildcard certs) ---
certbot certonly --manual --preferred-challenges dns \
    -d "*.example.com" -d example.com
# --manual = interactive mode (prompts for action), --preferred-challenges dns = verify via DNS TXT record

# --- Method 6: DNS challenge with API (automated wildcard) ---
# Example with Cloudflare:
dnf install python3-certbot-dns-cloudflare -y  # or apt install

cat > /etc/letsencrypt/cloudflare.ini << 'EOF'
dns_cloudflare_api_token = your-cloudflare-api-token
EOF
chmod 600 /etc/letsencrypt/cloudflare.ini

certbot certonly --dns-cloudflare \
    --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
    -d "*.example.com" -d example.com

# Example with Route53 (AWS):
pip3 install certbot-dns-route53
certbot certonly --dns-route53 -d "*.example.com" -d example.com
```

### 3.3 Certificate Locations
```bash
# Let's Encrypt stores certs here:
/etc/letsencrypt/live/example.com/
├── cert.pem       # Server certificate only
├── chain.pem      # Intermediate certificate(s)
├── fullchain.pem  # cert.pem + chain.pem (use this!)
└── privkey.pem    # Private key

# For Nginx/Apache use:
ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
```

### 3.4 Auto-Renewal
```bash
# Test renewal
certbot renew --dry-run                # --dry-run = simulate renewal without making changes

# Certbot auto-installs a timer/cron:
systemctl list-timers | grep certbot

# Manual cron (if needed):
# /etc/cron.d/certbot
0 0,12 * * * root certbot renew --quiet --deploy-hook "systemctl reload nginx"

# Renewal hooks (run after renewal):
# /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
#!/bin/bash
systemctl reload nginx

# List certificates
certbot certificates

# Revoke a certificate
certbot revoke --cert-path /etc/letsencrypt/live/example.com/cert.pem
# revoke = notify CA the cert is no longer valid, --cert-path = path to the cert to revoke

# Delete a certificate
certbot delete --cert-name example.com    # delete = remove cert files from disk, --cert-name = name to delete
```

---

## SECTION 4: Custom Certificate Authority (Internal CA)

### 4.1 Create Root CA
```bash
mkdir -p /etc/ssl/CA/{certs,crl,newcerts,private}
touch /etc/ssl/CA/index.txt
echo 1000 > /etc/ssl/CA/serial

# Generate Root CA private key
openssl genrsa -aes256 -out /etc/ssl/CA/private/ca.key 4096
# genrsa = generate RSA private key, -aes256 = encrypt key with AES-256 passphrase, 4096 = key size in bits
chmod 400 /etc/ssl/CA/private/ca.key

# Generate Root CA certificate (10 years)
openssl req -x509 -new -nodes -key /etc/ssl/CA/private/ca.key \
    -sha256 -days 3650 \
    -out /etc/ssl/CA/certs/ca.crt \
    -subj "/C=US/ST=State/L=City/O=MyCompany/OU=IT/CN=MyCompany Root CA"
```

### 4.2 Create Intermediate CA (Recommended)
```bash
# Generate Intermediate CA key
openssl genrsa -aes256 -out /etc/ssl/CA/private/intermediate.key 4096

# Generate Intermediate CA CSR
openssl req -new -key /etc/ssl/CA/private/intermediate.key \
    -out /etc/ssl/CA/certs/intermediate.csr \
    -subj "/C=US/ST=State/L=City/O=MyCompany/OU=IT/CN=MyCompany Intermediate CA"
# -new = create a new CSR, -key = use this existing private key

# Sign Intermediate with Root CA (5 years)
openssl x509 -req -in /etc/ssl/CA/certs/intermediate.csr \
    -CA /etc/ssl/CA/certs/ca.crt \
    -CAkey /etc/ssl/CA/private/ca.key \
    -CAcreateserial -out /etc/ssl/CA/certs/intermediate.crt \
    -days 1825 -sha256 \
    -extfile <(printf "basicConstraints=CA:TRUE,pathlen:0\nkeyUsage=critical,digitalSignature,keyCertSign,cRLSign")
# -req = input is a CSR (not a cert)
# -CA = CA certificate to sign with
# -CAkey = CA private key for signing
# -CAcreateserial = auto-create serial number file if missing

# Create chain file
cat /etc/ssl/CA/certs/intermediate.crt /etc/ssl/CA/certs/ca.crt > /etc/ssl/CA/certs/ca-chain.crt
```

### 4.3 Issue Server Certificates
```bash
# Generate server private key
openssl genrsa -out /etc/ssl/private/server.key 2048

# Generate CSR with SAN
cat > /tmp/server_san.cnf << 'EOF'
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C = US
ST = State
L = City
O = MyCompany
OU = Web
CN = server.internal.example.com

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = server.internal.example.com
DNS.2 = *.internal.example.com
IP.1 = 192.168.1.10
EOF

openssl req -new -key /etc/ssl/private/server.key \
    -out /etc/ssl/certs/server.csr \
    -config /tmp/server_san.cnf
# -new = generate a new CSR, -key = private key to embed in the CSR

# Sign with Intermediate CA (1 year)
openssl x509 -req -in /etc/ssl/certs/server.csr \
    -CA /etc/ssl/CA/certs/intermediate.crt \
    -CAkey /etc/ssl/CA/private/intermediate.key \
    -CAcreateserial -out /etc/ssl/certs/server.crt \
    -days 365 -sha256 \
    -extfile /tmp/server_san.cnf -extensions v3_req
# -req = sign a CSR input, -CA/-CAkey = signing CA cert and key, -CAcreateserial = auto-create serial file

# Create full chain for server
cat /etc/ssl/certs/server.crt /etc/ssl/CA/certs/ca-chain.crt > /etc/ssl/certs/server-fullchain.crt
```

### 4.4 Distribute Root CA to Clients
```bash
# --- CentOS/RHEL ---
cp /etc/ssl/CA/certs/ca.crt /etc/pki/ca-trust/source/anchors/mycompany-ca.crt
update-ca-trust

# --- Ubuntu/Debian ---
cp /etc/ssl/CA/certs/ca.crt /usr/local/share/ca-certificates/mycompany-ca.crt
update-ca-certificates

# Verify trust
openssl verify -CAfile /etc/ssl/CA/certs/ca-chain.crt /etc/ssl/certs/server.crt
# -CAfile = CA certificate chain to verify against
curl https://server.internal.example.com    # Should work without -k
```

---

## SECTION 5: Certificate Management & Troubleshooting

### 5.1 Inspection Commands
```bash
# View certificate details
openssl x509 -in cert.crt -text -noout    # -text = human-readable output, -noout = suppress raw PEM

# Check expiration date
openssl x509 -in cert.crt -enddate -noout    # -enddate = show only the expiry date

# Check certificate on a remote server
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -text -noout
# -servername = set SNI hostname (needed when server hosts multiple certs)

# Check expiration of remote certificate
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -enddate -noout

# Verify certificate matches private key
openssl x509 -noout -modulus -in cert.crt | md5sum    # -modulus = output the modulus of the public key
openssl rsa -noout -modulus -in cert.key | md5sum
# Both MD5 hashes should match!

# Verify certificate chain
openssl verify -CAfile ca-chain.crt server.crt    # -CAfile = trusted CA chain for verification

# View CSR contents
openssl req -in server.csr -text -noout    # req -in = read a CSR, -text/-noout = readable output only

# Check SSL/TLS configuration
openssl s_client -connect example.com:443 -tls1_2    # -tls1_2 = force TLS 1.2 only
openssl s_client -connect example.com:443 -tls1_3    # -tls1_3 = force TLS 1.3 only
```

### 5.2 Convert Between Formats
```bash
# PEM to DER
openssl x509 -in cert.pem -outform DER -out cert.der    # -outform DER = output in binary DER format

# DER to PEM
openssl x509 -in cert.der -inform DER -outform PEM -out cert.pem    # -inform DER = input is DER format

# PEM to PKCS#12 (for Windows/Java)
openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem -certfile ca-chain.pem
# -export = create a PKCS#12 file, -inkey = private key, -certfile = additional CA certs to include

# PKCS#12 to PEM
openssl pkcs12 -in cert.pfx -out cert.pem -nodes    # -nodes = don't encrypt extracted private key

# Extract key from PKCS#12
openssl pkcs12 -in cert.pfx -nocerts -out key.pem -nodes    # -nocerts = output only the private key

# Extract cert from PKCS#12
openssl pkcs12 -in cert.pfx -clcerts -nokeys -out cert.pem
# -clcerts = output only client certs (not CA), -nokeys = don't output private key
```

### 5.3 Certificate Expiry Monitoring Script
```bash
#!/bin/bash
# /usr/local/bin/check-certs.sh
# Check SSL certificate expiration

DOMAINS="example.com www.example.com api.example.com mail.example.com"
WARN_DAYS=30
CRIT_DAYS=7

for domain in $DOMAINS; do
    expiry=$(echo | openssl s_client -connect ${domain}:443 -servername ${domain} 2>/dev/null | \
             openssl x509 -enddate -noout 2>/dev/null | cut -d= -f2)

    if [ -z "$expiry" ]; then
        echo "CRITICAL: Cannot connect to ${domain}:443"
        continue
    fi

    expiry_epoch=$(date -d "$expiry" +%s)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))

    if [ $days_left -le $CRIT_DAYS ]; then
        echo "CRITICAL: ${domain} cert expires in ${days_left} days (${expiry})"
    elif [ $days_left -le $WARN_DAYS ]; then
        echo "WARNING: ${domain} cert expires in ${days_left} days (${expiry})"
    else
        echo "OK: ${domain} cert valid for ${days_left} days (${expiry})"
    fi
done
```

### 5.4 Common Certificate Issues
```bash
# 1. "certificate has expired"
# → Renew the certificate
certbot renew --force-renewal

# 2. "certificate is not yet valid"
# → Check server time: date, timedatectl
# → Sync time: systemctl restart chronyd (or ntpd)

# 3. "unable to get local issuer certificate" / "self signed certificate in chain"
# → Missing intermediate certificate in chain
# → Use fullchain.pem not just cert.pem

# 4. "certificate verify failed"
# → Update CA trust store:
#   CentOS: update-ca-trust
#   Ubuntu: update-ca-certificates

# 5. "key values mismatch"
# → Certificate and private key don't match
# → Regenerate CSR with correct key

# 6. SSL handshake timeout
# → Check firewall allows port 443
# → Check no other service on port 443: ss -tlnp | grep :443

# 7. Mixed content warnings
# → Ensure all resources use HTTPS
```
