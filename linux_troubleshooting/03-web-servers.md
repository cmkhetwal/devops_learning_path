# 03 - Web Servers: Apache & Nginx
## Complete Setup, Configuration, and Performance Tuning

---

## PART A: NGINX

### 1. Installation

```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install nginx -y

# Or install latest from official repo:
cat > /etc/yum.repos.d/nginx.repo << 'EOF'
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
EOF
dnf install nginx -y

# --- Ubuntu/Debian ---
apt install nginx -y

# Start and enable
systemctl enable --now nginx
nginx -t    # -t = test configuration for syntax errors without starting
nginx -V    # -V = show version plus compile-time configuration options
```

### 2. Directory Structure
```
/etc/nginx/
├── nginx.conf              # Main configuration
├── conf.d/                 # Additional configs (CentOS)
│   └── default.conf
├── sites-available/        # Available vhosts (Ubuntu)
├── sites-enabled/          # Enabled vhosts (Ubuntu)
├── mime.types
├── modules-enabled/        # Loaded modules
└── snippets/               # Reusable config snippets

/var/log/nginx/
├── access.log
└── error.log

/usr/share/nginx/html/      # Default web root (CentOS)
/var/www/html/              # Default web root (Ubuntu)
```

### 3. Main Configuration - Optimized
```nginx
# /etc/nginx/nginx.conf

# Run as: match to system user
user nginx;                                    # CentOS
# user www-data;                               # Ubuntu

# Worker processes = number of CPU cores
worker_processes auto;

# Max open files per worker
worker_rlimit_nofile 65535;

error_log /var/log/nginx/error.log warn;
pid /run/nginx.pid;

events {
    # Max simultaneous connections per worker
    worker_connections 4096;
    # Accept multiple connections at once
    multi_accept on;
    # Best method for Linux
    use epoll;
}

http {
    # --- Basic Settings ---
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    charset utf-8;

    # --- Logging ---
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time $upstream_response_time';

    access_log /var/log/nginx/access.log main buffer=16k flush=2m;
    # Disable access log for high-traffic (use sampling instead)
    # access_log off;

    # --- Performance ---
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;

    # --- Buffers ---
    client_body_buffer_size 16k;
    client_header_buffer_size 1k;
    client_max_body_size 100m;
    large_client_header_buffers 4 8k;

    # --- Timeouts ---
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # --- Gzip Compression ---
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 4;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        text/javascript
        application/json
        application/javascript
        application/xml
        application/xml+rss
        image/svg+xml;

    # --- Security Headers ---
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # --- Hide Nginx Version ---
    server_tokens off;

    # --- Rate Limiting ---
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=3r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    # --- File Cache ---
    open_file_cache max=10000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # Include virtual hosts
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;    # Ubuntu
}
```

### 4. Virtual Host Configurations

#### 4a. Basic HTTP Site
```nginx
# /etc/nginx/conf.d/example.com.conf

server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/example.com/html;
    index index.html index.htm;

    access_log /var/log/nginx/example.com.access.log main;
    error_log /var/log/nginx/example.com.error.log;

    location / {
        try_files $uri $uri/ =404;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Static file caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2|svg)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
```

#### 4b. HTTPS Site with SSL
```nginx
# /etc/nginx/conf.d/secure.example.com.conf

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;
    root /var/www/example.com/html;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

#### 4c. Reverse Proxy (for Node.js, Python, etc.)
```nginx
# /etc/nginx/conf.d/app.example.com.conf

upstream app_backend {
    least_conn;    # Load balancing method
    server 127.0.0.1:3000 weight=3;
    server 127.0.0.1:3001 weight=2;
    server 127.0.0.1:3002 backup;

    keepalive 32;  # Keep connections to backend alive
}

server {
    listen 443 ssl http2;
    server_name app.example.com;

    ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    location / {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 16k;
    }

    # Rate limiting on login
    location /api/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://app_backend;
    }

    # Static files served directly
    location /static/ {
        alias /var/www/app/static/;
        expires 30d;
        access_log off;
    }
}
```

#### 4d. PHP Site (WordPress, etc.)
```nginx
server {
    listen 443 ssl http2;
    server_name wordpress.example.com;
    root /var/www/wordpress;
    index index.php index.html;

    ssl_certificate /etc/letsencrypt/live/wordpress.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wordpress.example.com/privkey.pem;

    client_max_body_size 64m;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/run/php-fpm/www.sock;   # CentOS
        # fastcgi_pass unix:/run/php/php-fpm.sock;  # Ubuntu
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_read_timeout 300;
        fastcgi_buffer_size 128k;
        fastcgi_buffers 256 16k;
    }

    # Block access to sensitive files
    location ~* /(?:uploads|files)/.*\.php$ { deny all; }
    location ~ /\.ht { deny all; }
    location = /wp-config.php { deny all; }

    # Cache static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 30d;
        access_log off;
    }
}
```

### 5. Nginx Troubleshooting
```bash
# Test configuration
nginx -t

# Check error log
tail -f /var/log/nginx/error.log

# Check who's using most bandwidth
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Check for errors by status code
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Check slow requests (>2s)
awk '$NF > 2' /var/log/nginx/access.log | tail -20

# Check active connections
curl http://localhost/nginx_status
# (requires stub_status module enabled)

# Reload without downtime
nginx -s reload    # -s reload = send reload signal to running master process

# Check worker process count and connections
ps aux | grep nginx | grep -c worker    # -c = count matching lines
ss -tnp | grep nginx | wc -l
```

---

## PART B: APACHE (httpd)

### 1. Installation
```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install httpd mod_ssl -y
systemctl enable --now httpd

# --- Ubuntu/Debian ---
apt install apache2 -y
systemctl enable --now apache2

# Check version and modules
httpd -v          # -v = show version string
apache2 -v        # Ubuntu
httpd -M          # -M = list all loaded modules (static and shared)
apache2ctl -M     # Ubuntu
```

### 2. Directory Structure
```
# CentOS/RHEL:
/etc/httpd/
├── conf/httpd.conf          # Main config
├── conf.d/                  # Additional configs
│   ├── ssl.conf
│   └── vhost.conf
├── conf.modules.d/          # Module configs
└── logs -> /var/log/httpd

# Ubuntu/Debian:
/etc/apache2/
├── apache2.conf             # Main config
├── sites-available/         # Available vhosts
├── sites-enabled/           # Enabled vhosts (symlinks)
├── mods-available/
├── mods-enabled/
├── conf-available/
└── conf-enabled/
```

### 3. Apache Performance Configuration
```apache
# --- MPM Configuration ---
# CentOS: /etc/httpd/conf.modules.d/00-mpm.conf
# Ubuntu: /etc/apache2/mods-available/mpm_event.conf

# Use Event MPM (best for modern workloads)
# Disable prefork: comment out LoadModule mpm_prefork_module
# Enable event: uncomment LoadModule mpm_event_module

<IfModule mpm_event_module>
    ServerLimit          16
    StartServers         4
    MinSpareThreads      75
    MaxSpareThreads      250
    ThreadLimit          64
    ThreadsPerChild      64
    MaxRequestWorkers    1024
    MaxConnectionsPerChild 10000
</IfModule>

# If stuck with Prefork (for mod_php):
<IfModule mpm_prefork_module>
    StartServers         5
    MinSpareServers      5
    MaxSpareServers      10
    MaxRequestWorkers    256
    MaxConnectionsPerChild 5000
</IfModule>
```

### 4. Apache Virtual Hosts

#### 4a. Basic Virtual Host
```apache
# CentOS: /etc/httpd/conf.d/example.com.conf
# Ubuntu: /etc/apache2/sites-available/example.com.conf

<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com
    DocumentRoot /var/www/example.com/html
    ServerAdmin admin@example.com

    <Directory /var/www/example.com/html>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/example.com-error.log
    CustomLog /var/log/httpd/example.com-access.log combined
</VirtualHost>
```

#### 4b. HTTPS Virtual Host
```apache
<VirtualHost *:80>
    ServerName example.com
    Redirect permanent / https://example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName example.com
    DocumentRoot /var/www/example.com/html

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

    # Modern SSL configuration
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    SSLHonorCipherOrder off

    Header always set Strict-Transport-Security "max-age=63072000"
    Header always set X-Content-Type-Options "nosniff"

    <Directory /var/www/example.com/html>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # Enable compression
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css
        AddOutputFilterByType DEFLATE application/javascript application/json
    </IfModule>

    # Cache static files
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType image/jpeg "access plus 1 month"
        ExpiresByType image/png "access plus 1 month"
        ExpiresByType text/css "access plus 1 week"
        ExpiresByType application/javascript "access plus 1 week"
    </IfModule>

    ErrorLog /var/log/httpd/example.com-ssl-error.log
    CustomLog /var/log/httpd/example.com-ssl-access.log combined
</VirtualHost>
```

#### 4c. Reverse Proxy with Apache
```apache
# Enable required modules
# CentOS: Already included
# Ubuntu: a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests headers

<VirtualHost *:443>
    ServerName app.example.com
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/app.example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/app.example.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/

    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Real-IP "%{REMOTE_ADDR}s"

    # Load balancing to multiple backends
    # <Proxy "balancer://myapp">
    #     BalancerMember http://127.0.0.1:3000
    #     BalancerMember http://127.0.0.1:3001
    #     ProxySet lbmethod=byrequests
    # </Proxy>
    # ProxyPass / balancer://myapp/
</VirtualHost>
```

### 5. Ubuntu-Specific Commands
```bash
# Enable/disable sites
a2ensite example.com.conf    # a2ensite = Apache2 Enable Site (symlink to sites-enabled)
a2dissite example.com.conf   # a2dissite = Apache2 Disable Site (remove symlink)

# Enable/disable modules
a2enmod ssl rewrite headers proxy proxy_http deflate expires    # a2enmod = Apache2 Enable Module
a2dismod status              # a2dismod = Apache2 Disable Module

# Test and reload
apachectl configtest         # configtest = test configuration syntax without restarting
systemctl reload apache2
```

### 6. Apache Troubleshooting
```bash
# Test configuration
httpd -t            # -t = test configuration syntax for errors
apachectl configtest  # Ubuntu

# Check error logs
tail -f /var/log/httpd/error_log          # CentOS
tail -f /var/log/apache2/error.log        # Ubuntu

# Check Apache status (enable mod_status)
curl http://localhost/server-status?auto

# Check connections to Apache
ss -tnp | grep httpd | wc -l
ss -tnp | grep apache2 | wc -l

# Find heavy IPs
awk '{print $1}' /var/log/httpd/access_log | sort | uniq -c | sort -rn | head -20

# Check for 500 errors
grep " 500 " /var/log/httpd/access_log | tail -20
grep -c " 500 " /var/log/httpd/access_log    # Count

# Apache vs Nginx resource usage
ps -eo pid,ppid,%mem,%cpu,rss,comm | grep -E "httpd|apache2|nginx"
```
