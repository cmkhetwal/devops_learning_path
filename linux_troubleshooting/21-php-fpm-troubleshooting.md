# 21 - PHP & PHP-FPM Troubleshooting & Optimization
## Installation, Pool Tuning, OPcache, Web Server Integration, AWS RDS & Redis

---

## 1. PHP & PHP-FPM Installation

### 1a. Install PHP + Common Extensions

```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install php php-fpm php-cli php-common php-mysqlnd php-pdo php-xml \
    php-mbstring php-json php-curl php-zip php-gd php-intl php-bcmath \
    php-opcache php-soap php-redis -y

# --- Ubuntu/Debian ---
apt install php php-fpm php-cli php-common php-mysql php-xml \
    php-mbstring php-curl php-zip php-gd php-intl php-bcmath \
    php-opcache php-soap php-redis -y

# Start and enable PHP-FPM
systemctl enable --now php-fpm          # CentOS/RHEL
systemctl enable --now php8.3-fpm       # Ubuntu (version-specific service name)
```

### 1b. Install Multiple PHP Versions

```bash
# --- CentOS/RHEL: Remi Repository ---
dnf install epel-release -y
dnf install https://rpms.remirepo.net/enterprise/remi-release-$(rpm -E %rhel).rpm -y

# List available PHP versions
dnf module list php

# Enable a specific version
dnf module reset php -y
dnf module enable php:remi-8.3 -y
dnf install php php-fpm php-cli php-common php-mysqlnd php-opcache -y

# --- Ubuntu/Debian: Ondrej PPA ---
add-apt-repository ppa:ondrej/php -y
apt update

# Install specific version alongside default
apt install php8.3 php8.3-fpm php8.3-cli php8.3-mysql php8.3-opcache -y
apt install php8.2 php8.2-fpm php8.2-cli php8.2-mysql php8.2-opcache -y

# Switch default CLI version (Ubuntu)
update-alternatives --set php /usr/bin/php8.3
```

### 1c. Verify Installation

```bash
php -v                    # Show PHP version
php -m                    # -m = list all compiled-in and loaded modules
php -i | grep -i "loaded configuration"    # Show loaded php.ini path
php -r "phpinfo();" | grep -i opcache      # Check OPcache is loaded

php-fpm -t                # -t = test PHP-FPM configuration for syntax errors
php-fpm -tt               # -tt = test and dump parsed configuration

# Check which PHP-FPM service is running
systemctl list-units --type=service | grep php
```

### 1d. Directory Structure Reference

```
# CentOS/RHEL:
/etc/php-fpm.conf                   # Main PHP-FPM config
/etc/php-fpm.d/www.conf             # Default pool config
/etc/php.ini                        # PHP runtime config
/etc/php.d/                         # Module .ini files (opcache, redis, etc.)
/var/log/php-fpm/                   # PHP-FPM logs
/run/php-fpm/www.sock               # Default FPM socket

# Ubuntu/Debian:
/etc/php/8.3/fpm/php-fpm.conf      # Main PHP-FPM config (version-specific)
/etc/php/8.3/fpm/pool.d/www.conf   # Default pool config
/etc/php/8.3/fpm/php.ini           # PHP runtime config (FPM context)
/etc/php/8.3/cli/php.ini           # PHP runtime config (CLI context)
/etc/php/8.3/mods-available/       # Module .ini files
/var/log/php8.3-fpm.log            # PHP-FPM log
/run/php/php8.3-fpm.sock           # Default FPM socket
```

---

## 2. PHP-FPM Configuration & Pool Tuning

### 2a. Main Configuration Files

```ini
# /etc/php-fpm.conf (CentOS) or /etc/php/8.3/fpm/php-fpm.conf (Ubuntu)
# Global PHP-FPM settings

[global]
pid = /run/php-fpm/php-fpm.pid
error_log = /var/log/php-fpm/error.log
;log_level = notice                     # Levels: alert, error, warning, notice, debug
daemonize = yes                         # Run as daemon (systemd manages this)
emergency_restart_threshold = 10        # Restart FPM if this many children crash
emergency_restart_interval = 1m         # ...within this time window
process_control_timeout = 10s           # Timeout for child to react to signals
```

### 2b. Pool Configuration — Process Manager

```ini
# /etc/php-fpm.d/www.conf (CentOS) or /etc/php/8.3/fpm/pool.d/www.conf (Ubuntu)

[www]
user = nginx                            # Process runs as this user (match web server)
group = nginx                           # Process group (match web server)
; Ubuntu: user = www-data / group = www-data

# --- Socket vs TCP ---
; Socket (faster, local only — use for Nginx on same server):
listen = /run/php-fpm/www.sock
listen.owner = nginx                    # Socket file owner (must match web server user)
listen.group = nginx                    # Socket file group
listen.mode = 0660                      # Socket permissions (rw for owner/group)

; TCP (required for remote connections or Docker):
; listen = 127.0.0.1:9000              # Bind to localhost port 9000
; listen = 0.0.0.0:9000               # Bind to all interfaces (use with firewall)

listen.backlog = 511                    # Max pending connections queue (match net.core.somaxconn)
```

### 2c. Process Manager Modes

```ini
# --- pm = dynamic (DEFAULT — recommended for most workloads) ---
# Maintains a variable number of workers based on load
pm = dynamic
pm.max_children = 50                    # Maximum worker processes (hard limit)
pm.start_servers = 10                   # Workers created on startup
pm.min_spare_servers = 5                # Minimum idle workers kept alive
pm.max_spare_servers = 20              # Maximum idle workers (excess are killed)
pm.max_requests = 500                   # Recycle worker after N requests (prevents memory leaks)

# --- pm = static (best for dedicated high-traffic servers) ---
# Fixed number of workers — no overhead from spawning/killing
; pm = static
; pm.max_children = 50                  # All workers created at startup and kept alive
; pm.max_requests = 1000               # Recycle workers to prevent memory leaks

# --- pm = ondemand (best for low-traffic or many idle pools) ---
# Workers are spawned on demand and killed when idle
; pm = ondemand
; pm.max_children = 50                  # Maximum workers that can be spawned
; pm.process_idle_timeout = 10s         # Kill idle workers after this time
; pm.max_requests = 500                 # Recycle worker after N requests
```

### 2d. Calculating max_children

```bash
# Formula: max_children = (Total RAM - OS/DB/Cache overhead) / Average PHP worker memory

# Step 1: Find average PHP-FPM worker memory usage (in MB)
ps -eo rss,comm | grep php-fpm | awk '{sum+=$1; count++} END {print "Avg:", sum/count/1024, "MB", "| Workers:", count}'

# Step 2: Calculate
# Example: 8GB server, ~1.5GB for OS/Nginx/other, workers average 40MB each
#   max_children = (8192 - 1536) / 40 = 166
#   Conservative estimate: set to ~120-140 to leave headroom

# Step 3: Monitor after setting — watch for:
#   - "server reached max_children" in error log = too low
#   - High memory usage / OOM kills = too high or memory_limit too large
```

### 2e. Timeouts and Slow Log

```ini
# Pool config continued
request_terminate_timeout = 300         # Kill worker if request exceeds this (seconds, 0=off)
                                        # Prevents runaway scripts; should match or exceed
                                        # Nginx fastcgi_read_timeout / Apache ProxyTimeout

request_slowlog_timeout = 5s            # Log stack trace if request takes longer than this
slowlog = /var/log/php-fpm/www-slow.log # Path to slow log (invaluable for debugging)

# Access log (per-pool request logging)
access.log = /var/log/php-fpm/www-access.log
access.format = "%R - %u %t \"%m %r%Q%q\" %s %f %{mili}d %{kilo}M %C%%"
# %R=remote IP  %u=user  %t=time  %m=method  %r=URI  %Q=query  %s=status
# %f=script  %d=duration(ms)  %M=memory(KB)  %C=CPU%
```

### 2f. Multiple Pools (Separate Pool Per Site)

```ini
# /etc/php-fpm.d/site1.conf
[site1]
user = site1
group = site1
listen = /run/php-fpm/site1.sock
listen.owner = nginx
listen.group = nginx
listen.mode = 0660
pm = dynamic
pm.max_children = 30
pm.start_servers = 5
pm.min_spare_servers = 3
pm.max_spare_servers = 10
pm.max_requests = 500

# Pool-specific PHP settings (override php.ini per pool)
php_admin_value[memory_limit] = 256M
php_admin_value[max_execution_time] = 120
php_admin_value[error_log] = /var/log/php-fpm/site1-error.log
php_admin_flag[log_errors] = on
php_value[session.save_handler] = redis
php_value[session.save_path] = "tcp://redis.example.com:6379"

# --- Repeat for each site with its own pool ---
# /etc/php-fpm.d/site2.conf
# [site2]
# ...
```

### 2g. Key php.ini Settings

```ini
# /etc/php.ini (CentOS) or /etc/php/8.3/fpm/php.ini (Ubuntu)

# --- Resource Limits ---
memory_limit = 256M                     # Max memory per PHP process (tune per workload)
max_execution_time = 30                 # Max script execution time in seconds (0=unlimited)
max_input_time = 60                     # Max time to parse input data (POST, GET)
max_input_vars = 3000                   # Max number of input variables per request

# --- File Uploads ---
upload_max_filesize = 64M               # Max size of uploaded file
post_max_size = 70M                     # Max size of POST body (must be >= upload_max_filesize)
file_uploads = On

# --- Error Handling ---
display_errors = Off                    # NEVER show errors to users in production
display_startup_errors = Off
log_errors = On
error_log = /var/log/php-fpm/php-errors.log
error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT

# --- Sessions ---
session.save_handler = files            # Default; use 'redis' for distributed sessions
session.save_path = "/var/lib/php/sessions"
session.gc_maxlifetime = 1440           # Session lifetime in seconds (24 minutes)
session.cookie_secure = 1               # Only send session cookie over HTTPS
session.cookie_httponly = 1             # Prevent JavaScript access to session cookie
session.cookie_samesite = Strict        # CSRF protection

# --- Realpath Cache (important for frameworks with many includes) ---
realpath_cache_size = 4096K             # Cache for resolved file paths (default 4K is too low)
realpath_cache_ttl = 600                # Cache TTL in seconds

# --- Timezone ---
date.timezone = UTC
```

### 2h. Systemd Service Management

```bash
# Service names
# CentOS/RHEL: php-fpm
# Ubuntu: php8.3-fpm (version-specific)

systemctl start php-fpm
systemctl stop php-fpm
systemctl restart php-fpm               # Full restart (drops all connections)
systemctl reload php-fpm                # Graceful reload (finish current requests, then reload)
systemctl status php-fpm

# Check configuration before restarting
php-fpm -t && systemctl reload php-fpm

# View FPM logs via journald
journalctl -u php-fpm -f                # -f = follow log output in real time
journalctl -u php-fpm --since "1 hour ago"

# Override systemd settings (e.g., raise file limits)
systemctl edit php-fpm
# Add:
# [Service]
# LimitNOFILE=65535
systemctl daemon-reload
systemctl restart php-fpm
```

---

## 3. OPcache Configuration & Tuning

### 3a. What OPcache Does

OPcache stores precompiled PHP bytecode in shared memory, eliminating the need to parse and compile PHP scripts on every request. This typically improves PHP performance by 2-5x with no code changes.

### 3b. Key OPcache Settings

```ini
# /etc/php.d/10-opcache.ini (CentOS) or /etc/php/8.3/mods-available/opcache.ini (Ubuntu)

[opcache]
zend_extension=opcache

opcache.enable=1                        # Enable OPcache (1=on, 0=off)
opcache.enable_cli=0                    # Disable for CLI (not useful for FPM workloads)

opcache.memory_consumption=256          # Shared memory size in MB for storing bytecode
                                        # Start at 128, increase if cache fills up

opcache.interned_strings_buffer=16      # Memory in MB for interned strings (class/function names)
                                        # 8-32 depending on framework size

opcache.max_accelerated_files=20000     # Max number of PHP files to cache (actual limit is next
                                        # prime >= this value; check with opcache_get_status())
                                        # WordPress: ~4000, Laravel: ~15000, Magento: ~30000+

opcache.validate_timestamps=1           # Check file modification times (1=yes, 0=no)
                                        # Production: set to 0 for best performance
                                        # Development: set to 1 so code changes take effect

opcache.revalidate_freq=2               # How often to check for changes in seconds (when
                                        # validate_timestamps=1); 0=check every request

opcache.save_comments=1                 # Keep docblock comments (needed by many frameworks)
opcache.fast_shutdown=1                 # Use fast shutdown sequence for faster worker recycling

opcache.max_wasted_percentage=10        # Restart OPcache when wasted memory exceeds this %
```

### 3c. Production vs Development Settings

```ini
# --- Production (maximum performance) ---
opcache.validate_timestamps=0           # Never check for file changes (restart FPM to clear)
opcache.revalidate_freq=0
opcache.memory_consumption=256
opcache.max_accelerated_files=30000
opcache.enable_cli=0

# --- Development (auto-detect changes) ---
opcache.validate_timestamps=1           # Check for file changes automatically
opcache.revalidate_freq=0              # Check on every request
opcache.memory_consumption=128
opcache.max_accelerated_files=10000
```

### 3d. Monitoring OPcache

```bash
# Quick CLI check
php -r "var_dump(opcache_get_status(false));"

# Key fields to watch:
# opcache_statistics.num_cached_scripts     — number of cached scripts
# opcache_statistics.opcache_hit_rate       — should be >99% in production
# opcache_statistics.oom_restarts           — out-of-memory restarts (increase memory_consumption)
# memory_usage.used_memory                  — current memory used
# memory_usage.free_memory                  — remaining free memory
# memory_usage.wasted_memory               — fragmented/wasted memory

# Check from CLI if OPcache is loaded
php -m | grep -i opcache

# Create a monitoring script (place behind auth or IP restriction)
cat > /var/www/html/opcache-status.php << 'SCRIPT'
<?php
// IMPORTANT: Restrict access to this file (IP whitelist or auth)
header('Content-Type: application/json');
$status = opcache_get_status(false);
echo json_encode([
    'enabled'    => $status['opcache_enabled'],
    'hit_rate'   => round($status['opcache_statistics']['opcache_hit_rate'], 2) . '%',
    'used_mem'   => round($status['memory_usage']['used_memory'] / 1048576, 2) . ' MB',
    'free_mem'   => round($status['memory_usage']['free_memory'] / 1048576, 2) . ' MB',
    'wasted_mem' => round($status['memory_usage']['wasted_memory'] / 1048576, 2) . ' MB',
    'scripts'    => $status['opcache_statistics']['num_cached_scripts'],
    'max_scripts'=> ini_get('opcache.max_accelerated_files'),
    'oom_restarts' => $status['opcache_statistics']['oom_restarts'],
], JSON_PRETTY_PRINT);
SCRIPT
```

### 3e. Clearing OPcache After Deploys

```bash
# When validate_timestamps=0 (production), cached bytecode persists until cleared

# Option 1: Reload PHP-FPM (graceful — recommended)
systemctl reload php-fpm

# Option 2: Restart PHP-FPM (drops active connections)
systemctl restart php-fpm

# Option 3: Call opcache_reset() from PHP (use in deploy scripts)
php -r "opcache_reset();"
# NOTE: CLI and FPM have separate OPcache instances. To clear FPM's cache,
# hit a PHP script via HTTP that calls opcache_reset(), e.g.:
curl -s http://localhost/opcache-clear.php

# Option 4: CachedTool / deployment hook (Laravel Forge, Deployer, etc.)
# Most deploy tools call opcache_reset() automatically after symlink swap
```

---

## 4. Nginx + PHP-FPM (Production Setup)

### 4a. Optimized FastCGI Configuration

```nginx
# /etc/nginx/conf.d/php-app.conf

server {
    listen 443 ssl http2;
    server_name app.example.com;
    root /var/www/app/public;
    index index.php index.html;

    ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    client_max_body_size 64m;           # Match post_max_size in php.ini

    # --- Main Application ---
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # --- PHP Processing ---
    location ~ \.php$ {
        # Prevent executing PHP in unintended locations
        try_files $uri =404;

        # Pass to PHP-FPM via socket (faster than TCP for local)
        fastcgi_pass unix:/run/php-fpm/www.sock;       # CentOS
        # fastcgi_pass unix:/run/php/php8.3-fpm.sock;  # Ubuntu
        # fastcgi_pass 127.0.0.1:9000;                 # TCP alternative

        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;

        # --- Timeouts ---
        fastcgi_connect_timeout 60s;    # Time to wait for connection to FPM
        fastcgi_send_timeout 300s;      # Time to send request to FPM
        fastcgi_read_timeout 300s;      # Time to wait for FPM response
                                        # Must be >= request_terminate_timeout in pool config

        # --- Buffering ---
        fastcgi_buffer_size 128k;       # Buffer for first part of response (headers)
        fastcgi_buffers 256 16k;        # Number and size of buffers for response body
        fastcgi_busy_buffers_size 256k; # Max size sent to client while still reading from FPM
        fastcgi_temp_file_write_size 256k;  # Max data written to temp file at once

        # --- Keep connections alive to FPM ---
        fastcgi_keep_conn on;           # Reuse connections to PHP-FPM (reduces overhead)
    }

    # --- Static File Bypass (never send to PHP) ---
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif|mp4)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
        try_files $uri =404;
    }

    # --- Security: Block PHP Execution in Uploads ---
    location ~* /(?:uploads|media|files|wp-content/uploads)/.*\.php$ {
        deny all;
    }

    # Deny access to hidden files and directories
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    access_log /var/log/nginx/app.example.com.access.log main;
    error_log /var/log/nginx/app.example.com.error.log;
}
```

### 4b. FastCGI Cache (Full-Page Caching)

```nginx
# Add to http {} block in /etc/nginx/nginx.conf
fastcgi_cache_path /var/cache/nginx/fastcgi
    levels=1:2                          # Directory depth for cache files
    keys_zone=phpcache:100m             # Zone name and shared memory for keys (100MB)
    max_size=2g                         # Max disk space for cached responses
    inactive=60m                        # Remove cached items not accessed in 60 minutes
    use_temp_path=off;                  # Write directly to cache dir (better performance)

# In server {} block:
set $skip_cache 0;

# Don't cache POST requests
if ($request_method = POST) { set $skip_cache 1; }

# Don't cache requests with query strings (or be selective)
if ($query_string != "") { set $skip_cache 1; }

# Don't cache logged-in users (WordPress example)
if ($http_cookie ~* "wordpress_logged_in|comment_author") { set $skip_cache 1; }

location ~ \.php$ {
    # ... (fastcgi_pass and other settings from above) ...

    fastcgi_cache phpcache;
    fastcgi_cache_valid 200 301 60m;    # Cache 200/301 responses for 60 minutes
    fastcgi_cache_valid 404 1m;         # Cache 404 responses for 1 minute
    fastcgi_cache_bypass $skip_cache;   # Bypass cache when $skip_cache = 1
    fastcgi_no_cache $skip_cache;       # Don't store in cache when $skip_cache = 1
    fastcgi_cache_key "$scheme$request_method$host$request_uri";

    add_header X-Cache-Status $upstream_cache_status;  # HIT, MISS, BYPASS (for debugging)
}

# Manual cache purge
# rm -rf /var/cache/nginx/fastcgi/*
```

### 4c. Cross-Reference

> For complete Nginx installation, main configuration, SSL setup, and general performance tuning,
> see [03 - Web Servers: Apache & Nginx](03-web-servers.md) PART A.

---

## 5. Apache + PHP-FPM

### 5a. mod_php vs PHP-FPM

| Feature | mod_php | PHP-FPM |
|---------|---------|---------|
| Architecture | PHP embedded in Apache process | Separate PHP process pool |
| MPM support | Prefork only | Event, Worker, or Prefork |
| Memory usage | Higher (each Apache child loads PHP) | Lower (dedicated PHP workers) |
| Performance | Good for PHP-heavy sites | Better for mixed static/PHP |
| Isolation | None (runs as Apache user) | Per-pool users, separate permissions |
| Config reload | Requires full Apache restart | Reload PHP-FPM independently |
| Recommendation | Legacy setups only | **Use this** (modern best practice) |

### 5b. Apache + PHP-FPM via mod_proxy_fcgi

```bash
# --- Enable required modules ---

# CentOS/RHEL:
# proxy_fcgi is typically included; verify:
httpd -M | grep proxy_fcgi

# Ubuntu/Debian:
a2enmod proxy_fcgi setenvif
a2enconf php8.3-fpm            # Enable FPM config snippet
systemctl restart apache2
```

```apache
# /etc/httpd/conf.d/php-app.conf (CentOS)
# /etc/apache2/sites-available/php-app.conf (Ubuntu)

<VirtualHost *:443>
    ServerName app.example.com
    DocumentRoot /var/www/app/public

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/app.example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/app.example.com/privkey.pem

    <Directory /var/www/app/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # --- Method 1: ProxyPassMatch (all .php requests to FPM) ---
    ProxyPassMatch "^/(.*\.php(/.*)?)$" "unix:/run/php-fpm/www.sock|fcgi://localhost/var/www/app/public"
    # unix:/path = connect via Unix socket
    # fcgi://localhost/path = the document root for SCRIPT_FILENAME

    # --- Method 2: SetHandler (recommended, more flexible) ---
    # <FilesMatch \.php$>
    #     SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost"
    # </FilesMatch>

    # --- Method 3: TCP connection (for remote FPM or Docker) ---
    # ProxyPassMatch "^/(.*\.php(/.*)?)$" "fcgi://127.0.0.1:9000/var/www/app/public"

    # Timeouts
    ProxyTimeout 300                    # Timeout waiting for FPM response (seconds)

    # Block PHP execution in uploads
    <DirectoryMatch "/var/www/app/public/(uploads|media|files)">
        <FilesMatch "\.php$">
            Require all denied
        </FilesMatch>
    </DirectoryMatch>

    ErrorLog /var/log/httpd/app.example.com-error.log
    CustomLog /var/log/httpd/app.example.com-access.log combined
</VirtualHost>
```

### 5c. Event MPM + PHP-FPM (Recommended)

```bash
# Event MPM is the recommended Apache MPM for use with PHP-FPM
# It handles static files with threads (efficient) and proxies PHP to FPM

# --- CentOS/RHEL ---
# Edit /etc/httpd/conf.modules.d/00-mpm.conf
# Comment out:   LoadModule mpm_prefork_module modules/mod_mpm_prefork.so
# Uncomment:     LoadModule mpm_event_module modules/mod_mpm_event.so

# --- Ubuntu/Debian ---
a2dismod mpm_prefork               # Disable prefork MPM
a2enmod mpm_event                  # Enable event MPM
systemctl restart apache2

# Verify active MPM
httpd -V | grep -i mpm             # CentOS
apache2ctl -V | grep -i mpm       # Ubuntu
# Should show: Server MPM: event
```

### 5d. Cross-Reference

> For complete Apache installation, MPM tuning, virtual host setup, and SSL configuration,
> see [03 - Web Servers: Apache & Nginx](03-web-servers.md) PART B.

---

## 6. AWS RDS & Redis Integration

### 6a. PHP Connecting to AWS RDS

```bash
# Ensure PHP database extensions are installed
php -m | grep -iE "mysql|pgsql|pdo"

# Required extensions:
# MySQL/MariaDB: php-mysqlnd, php-pdo
# PostgreSQL:    php-pgsql, php-pdo
```

```bash
# Test RDS connectivity from the server
# Replace with your RDS endpoint from the AWS console

# MySQL/MariaDB
php -r "
try {
    \$pdo = new PDO(
        'mysql:host=mydb.abc123xyz.us-east-1.rds.amazonaws.com;port=3306;dbname=myapp',
        'dbuser',
        'dbpassword',
        [PDO::ATTR_TIMEOUT => 5]
    );
    echo 'Connected successfully. Server: ' . \$pdo->getAttribute(PDO::ATTR_SERVER_INFO) . PHP_EOL;
} catch (PDOException \$e) {
    echo 'Connection failed: ' . \$e->getMessage() . PHP_EOL;
}
"

# PostgreSQL
php -r "
try {
    \$pdo = new PDO(
        'pgsql:host=mydb.abc123xyz.us-east-1.rds.amazonaws.com;port=5432;dbname=myapp',
        'dbuser',
        'dbpassword'
    );
    echo 'Connected successfully' . PHP_EOL;
} catch (PDOException \$e) {
    echo 'Connection failed: ' . \$e->getMessage() . PHP_EOL;
}
"
```

### 6b. RDS SSL Connections

```bash
# Download Amazon RDS CA bundle
curl -o /etc/pki/tls/certs/rds-combined-ca-bundle.pem \
    https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

```ini
# php.ini — force SSL for all MySQL connections
mysqli.default_socket =
pdo_mysql.default_socket =

# Or configure per-connection in your application:
# $pdo = new PDO($dsn, $user, $pass, [
#     PDO::MYSQL_ATTR_SSL_CA => '/etc/pki/tls/certs/rds-combined-ca-bundle.pem',
#     PDO::MYSQL_ATTR_SSL_VERIFY_SERVER_CERT => true,
# ]);
```

### 6c. Common RDS Connection Issues

```bash
# 1. Security group not allowing access
#    - RDS security group must allow inbound on port 3306 (MySQL) or 5432 (PostgreSQL)
#      from the EC2 instance's security group or private IP
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx \
    --query "SecurityGroups[].IpPermissions[]"            # Check inbound rules

# 2. VPC / subnet issues
#    - EC2 and RDS must be in the same VPC (or connected via peering/Transit Gateway)
#    - RDS in private subnet? EC2 must also be in same VPC

# 3. DNS resolution
nslookup mydb.abc123xyz.us-east-1.rds.amazonaws.com      # Verify RDS endpoint resolves
dig +short mydb.abc123xyz.us-east-1.rds.amazonaws.com

# 4. Max connections exhausted
#    - Check in RDS: "DatabaseConnections" CloudWatch metric
#    - Default max_connections varies by instance class
#    - Fix: increase instance size, use connection pooling (ProxySQL/RDS Proxy), or
#      reduce PHP pm.max_children (each PHP worker can hold a connection)

# 5. Network connectivity test
nc -zv mydb.abc123xyz.us-east-1.rds.amazonaws.com 3306   # -z = scan only, -v = verbose
# Should show: Connection ... succeeded

# 6. RDS Proxy (managed connection pooling)
#    - Reduces connection churn from PHP-FPM workers
#    - Endpoint looks the same; drop-in replacement for direct RDS endpoint
```

### 6d. RDS Monitoring

```bash
# Key CloudWatch metrics to watch:
# CPUUtilization          — sustained >80% means instance is undersized
# DatabaseConnections     — approaching max = need pooling or larger instance
# FreeableMemory          — low = queries not using indexes, or instance too small
# ReadIOPS / WriteIOPS    — high = storage bottleneck, consider provisioned IOPS
# ReadLatency / WriteLatency  — >5ms sustained indicates storage pressure
# ReplicaLag              — for read replicas, high lag means reads may be stale

# Enable slow query log on RDS (via parameter group)
# slow_query_log = 1
# long_query_time = 1                  # Log queries taking >1 second
# log_output = FILE                    # Write to RDS log files

# View slow query log
aws rds download-db-log-file-portion \
    --db-instance-identifier mydb \
    --log-file-name slowquery/mysql-slowquery.log \
    --output text

# RDS Performance Insights (AWS Console)
# - Top SQL queries by load
# - Wait events breakdown
# - Per-query statistics
```

### 6e. PHP + Redis

```bash
# Install phpredis extension
# CentOS/RHEL:
dnf install php-redis -y

# Ubuntu/Debian:
apt install php-redis -y

# Verify
php -m | grep redis
php -r "echo 'phpredis version: ' . phpversion('redis') . PHP_EOL;"

# Restart PHP-FPM after installing extension
systemctl restart php-fpm
```

### 6f. Redis for PHP Sessions

```ini
# php.ini or pool config (php_value in pool .conf)

session.save_handler = redis
session.save_path = "tcp://127.0.0.1:6379"

# With authentication:
; session.save_path = "tcp://127.0.0.1:6379?auth=yourpassword"

# With Redis database number:
; session.save_path = "tcp://127.0.0.1:6379?auth=yourpassword&database=2"

# ElastiCache endpoint:
; session.save_path = "tcp://my-redis.abc123.0001.use1.cache.amazonaws.com:6379"

# Cluster mode (ElastiCache cluster):
; session.save_path = "tcp://my-redis.abc123.clustercfg.use1.cache.amazonaws.com:6379"

# Session locking (prevent race conditions)
redis.session.locking_enabled = 1
redis.session.lock_retries = -1         # Retry until lock_wait_time expires
redis.session.lock_wait_time = 10000    # Lock wait time in microseconds
```

### 6g. Testing Redis from PHP

```bash
# Test basic Redis connectivity
php -r "
\$redis = new Redis();
try {
    \$redis->connect('127.0.0.1', 6379);
    // \$redis->auth('yourpassword');    # Uncomment if auth is enabled
    \$redis->set('test_key', 'hello from php');
    echo 'SET: OK' . PHP_EOL;
    echo 'GET: ' . \$redis->get('test_key') . PHP_EOL;
    echo 'PING: ' . \$redis->ping() . PHP_EOL;
    echo 'INFO server: ' . substr(\$redis->info('server')['redis_version'], 0, 10) . PHP_EOL;
} catch (Exception \$e) {
    echo 'Redis error: ' . \$e->getMessage() . PHP_EOL;
}
"

# Test session handling via Redis
php -r "
ini_set('session.save_handler', 'redis');
ini_set('session.save_path', 'tcp://127.0.0.1:6379');
session_start();
\$_SESSION['test'] = 'session works';
echo 'Session ID: ' . session_id() . PHP_EOL;
echo 'Session data: ' . \$_SESSION['test'] . PHP_EOL;
"
```

### 6h. Redis CLI Troubleshooting

```bash
# Check Redis is running and responsive
redis-cli ping                          # Should return PONG

# Server info overview
redis-cli info server                   # Version, uptime, config file
redis-cli info memory                   # Memory usage, fragmentation ratio
redis-cli info clients                  # Connected clients count
redis-cli info stats                    # Hits, misses, evictions

# Key metrics to watch:
# used_memory_human         — total memory used by Redis
# connected_clients         — number of client connections
# evicted_keys             — keys removed due to maxmemory (should be 0 for sessions)
# keyspace_hits/misses     — cache hit ratio

# Monitor live commands (WARNING: impacts performance, use briefly)
redis-cli monitor | head -50            # Watch real-time commands hitting Redis

# Slow log (commands exceeding slowlog-log-slower-than)
redis-cli slowlog get 10                # Show last 10 slow commands
redis-cli slowlog len                   # Total number of slow log entries
redis-cli slowlog reset                 # Clear slow log

# Check session keys
redis-cli keys "PHPREDIS_SESSION:*" | head -10    # List PHP session keys
redis-cli ttl "PHPREDIS_SESSION:<session-id>"      # Check TTL on a session

# ElastiCache: same commands, just specify the endpoint
redis-cli -h my-redis.abc123.0001.use1.cache.amazonaws.com -p 6379 ping
```

---

## 7. PHP-FPM Troubleshooting

### 7a. Enable the Status Page

```ini
# /etc/php-fpm.d/www.conf (or pool config)
pm.status_path = /fpm-status            # URL path for status page
ping.path = /fpm-ping                   # Health check endpoint
ping.response = pong                    # Response body for ping
```

```nginx
# Nginx: expose status page (restrict by IP)
location ~ ^/(fpm-status|fpm-ping)$ {
    allow 127.0.0.1;                    # Localhost only
    allow 10.0.0.0/8;                   # Internal network
    deny all;
    fastcgi_pass unix:/run/php-fpm/www.sock;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
}
```

```bash
# Fetch status (plain text)
curl -s http://localhost/fpm-status

# Fetch full status with per-process details
curl -s "http://localhost/fpm-status?full"

# JSON format
curl -s "http://localhost/fpm-status?json" | python3 -m json.tool

# Health check
curl -s http://localhost/fpm-ping
# Returns: pong
```

### 7b. Reading the Status Page

```
pool:                 www
process manager:      dynamic
start time:           25/Apr/2026 10:00:00
start since:          86400               # Seconds since FPM started
accepted conn:        150000              # Total requests handled
listen queue:         0                   # Requests waiting for a free worker (should be 0)
max listen queue:     12                  # Highest queue length since start
listen queue len:     511                 # Socket backlog size (listen.backlog)
idle processes:       8                   # Workers waiting for requests
active processes:     2                   # Workers currently handling requests
total processes:      10                  # idle + active
max active processes: 45                  # Peak concurrent workers since start
max children reached: 0                   # Times max_children limit was hit (>0 = increase it)
slow requests:        3                   # Requests exceeding request_slowlog_timeout
```

### 7c. Common Problems and Diagnosis

#### Problem 1: "502 Bad Gateway"

```bash
# Cause: Nginx/Apache can't connect to PHP-FPM

# Check if PHP-FPM is running
systemctl status php-fpm
ps aux | grep php-fpm

# Check socket exists and has correct permissions
ls -la /run/php-fpm/www.sock
# Should be owned by the web server user (nginx:nginx or www-data:www-data)

# Check socket path matches Nginx/Apache config
grep -r "fastcgi_pass\|proxy:unix" /etc/nginx/conf.d/ /etc/httpd/conf.d/ 2>/dev/null
grep "listen " /etc/php-fpm.d/www.conf

# Check PHP-FPM error log
tail -50 /var/log/php-fpm/error.log

# SELinux blocking socket access (CentOS/RHEL)
ausearch -m AVC -ts recent | grep php    # Check for SELinux denials
setsebool -P httpd_can_network_connect on
```

#### Problem 2: "504 Gateway Timeout"

```bash
# Cause: PHP script takes longer than configured timeout

# Check which timeout is too low:
# 1. PHP-FPM: request_terminate_timeout in pool config
grep request_terminate_timeout /etc/php-fpm.d/www.conf

# 2. php.ini: max_execution_time
php -r "echo ini_get('max_execution_time');"

# 3. Nginx: fastcgi_read_timeout
grep fastcgi_read_timeout /etc/nginx/conf.d/*.conf

# 4. Apache: ProxyTimeout
grep -i proxytimeout /etc/httpd/conf.d/*.conf

# Check the slow log for the offending script
tail -100 /var/log/php-fpm/www-slow.log

# All four timeouts should be aligned:
# max_execution_time <= request_terminate_timeout <= fastcgi_read_timeout
```

#### Problem 3: "503 Service Unavailable" / All Workers Busy

```bash
# Cause: All PHP-FPM workers are occupied, new requests are queued/rejected

# Check status page for listen_queue > 0 and max_children_reached > 0
curl -s http://localhost/fpm-status

# Check error log for "server reached max_children setting"
grep "max_children" /var/log/php-fpm/error.log

# Solutions:
# 1. Increase pm.max_children (if server has RAM headroom)
# 2. Reduce average request time (optimize slow PHP code/queries)
# 3. Enable fastcgi_cache for cacheable pages
# 4. Check for stuck/slow processes
curl -s "http://localhost/fpm-status?full" | grep -A5 "state: Running"
```

#### Problem 4: High Memory Usage

```bash
# Check per-worker memory usage
ps -eo pid,rss,comm | grep php-fpm | sort -k2 -rn | head -20
# rss = resident set size in KB

# Total PHP-FPM memory
ps -eo rss,comm | grep php-fpm | awk '{sum+=$1} END {print sum/1024, "MB total"}'

# Check memory_limit setting
php -r "echo ini_get('memory_limit');"

# Check pm.max_requests (if 0, workers never recycle — memory leaks accumulate)
grep max_requests /etc/php-fpm.d/www.conf

# Solutions:
# 1. Set pm.max_requests = 500 (recycle workers after 500 requests)
# 2. Lower memory_limit if scripts don't need it
# 3. Profile application for memory leaks (use Xdebug or Blackfire)
# 4. Check for large data loaded into memory (unbuffered queries, large file reads)
```

#### Problem 5: Slow PHP Performance

```bash
# 1. Check if OPcache is enabled
php -r "echo 'OPcache: ' . (ini_get('opcache.enable') ? 'ON' : 'OFF') . PHP_EOL;"

# 2. Check for missing/unloaded extensions
php -m | grep -iE "opcache|redis|apcu"

# 3. Check slow log for recurring slow scripts
cat /var/log/php-fpm/www-slow.log | grep "script_filename" | sort | uniq -c | sort -rn | head -10

# 4. Check if database queries are the bottleneck
#    Enable MySQL slow query log (see Section 6d)
#    Check query times in application logs

# 5. Check realpath_cache (too small causes excessive stat() calls)
php -r "print_r(realpath_cache_size());"      # Current usage
php -r "echo ini_get('realpath_cache_size');"  # Configured limit
```

#### Problem 6: "Connection Refused" to PHP-FPM

```bash
# Socket vs TCP mismatch between web server and PHP-FPM
# Nginx says fastcgi_pass 127.0.0.1:9000 but FPM listens on socket, or vice versa

# Check what FPM is listening on
grep "^listen " /etc/php-fpm.d/www.conf
ss -tlnp | grep php-fpm                # -t=TCP -l=listening -n=numeric -p=show process

# Check what Nginx/Apache is trying to connect to
grep -r "fastcgi_pass\|proxy:unix\|fcgi://" /etc/nginx/ /etc/httpd/ 2>/dev/null

# Fix: ensure both sides match (both socket or both TCP with same address:port)
```

#### Problem 7: "Primary script unknown" / "File not found"

```bash
# Cause: SCRIPT_FILENAME points to wrong path

# Check Nginx is sending correct SCRIPT_FILENAME
# In Nginx config, ensure:
#   fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
# NOT:
#   fastcgi_param SCRIPT_FILENAME /wrong/path$fastcgi_script_name;

# Verify the document root exists and contains PHP files
ls -la /var/www/app/public/index.php

# Check Nginx root directive matches the actual file path
grep -A2 "root " /etc/nginx/conf.d/*.conf

# Check PHP-FPM error log for the exact path it's trying
tail -20 /var/log/php-fpm/error.log
# Look for: "Unable to open primary script: /wrong/path/index.php"

# SELinux context (CentOS)
ls -Z /var/www/app/public/index.php
# Should be: httpd_sys_content_t
# Fix: restorecon -Rv /var/www/app/
```

#### Problem 8: Blank Pages (White Screen of Death)

```bash
# 1. Check PHP error log (errors are hidden when display_errors=Off)
tail -50 /var/log/php-fpm/php-errors.log
tail -50 /var/log/php-fpm/www-error.log

# 2. Temporarily enable error display (development only!)
php -d display_errors=1 -d error_reporting=E_ALL -r "include '/var/www/app/public/index.php';"

# 3. Check error_log location in php.ini
php -r "echo ini_get('error_log');"

# 4. Check for syntax errors
php -l /var/www/app/public/index.php    # -l = lint (check syntax without executing)

# 5. Check for memory exhaustion
grep "Allowed memory size" /var/log/php-fpm/*.log

# 6. Check for missing extensions
php -m    # Compare with application requirements
```

### 7d. Log Analysis

```bash
# PHP-FPM error log locations:
# CentOS: /var/log/php-fpm/error.log
# Ubuntu: /var/log/php8.3-fpm.log
# Custom: check error_log directive in php-fpm.conf and pool config

# Follow error log in real time
tail -f /var/log/php-fpm/error.log

# Search for specific errors
grep -i "fatal\|error\|warning" /var/log/php-fpm/error.log | tail -30

# Check for out-of-memory errors
grep -i "allowed memory\|out of memory\|oom" /var/log/php-fpm/error.log

# Analyze slow log — find most frequent slow scripts
awk '/^\[/{script=""} /script_filename/{script=$NF} script && /^$/{print script}' \
    /var/log/php-fpm/www-slow.log | sort | uniq -c | sort -rn | head -10

# Check for segfaults / child crashes
grep -i "segfault\|signal 11\|SIGSEGV\|child.*exited" /var/log/php-fpm/error.log
journalctl -u php-fpm | grep -i "segfault\|signal"
```

### 7e. Process Monitoring

```bash
# List all PHP-FPM processes with memory and CPU
ps -eo pid,ppid,%mem,%cpu,rss,etime,comm | grep php-fpm | sort -k5 -rn

# Count master vs worker processes
ps aux | grep php-fpm | grep -c "master"     # Should be 1 (or 1 per version)
ps aux | grep php-fpm | grep -c "pool"       # Worker count

# Per-pool worker count
ps aux | grep php-fpm | grep "pool" | awk '{print $NF}' | sort | uniq -c
# Output example:
#   10 www
#    5 site1
#    3 site2

# Memory usage per pool
for pool in $(ps aux | grep "php-fpm: pool" | awk '{print $NF}' | sort -u); do
    mem=$(ps aux | grep "php-fpm: pool $pool" | awk '{sum+=$6} END {printf "%.0f", sum/1024}')
    count=$(ps aux | grep -c "php-fpm: pool $pool")
    echo "Pool: $pool | Workers: $count | Memory: ${mem}MB"
done

# Watch process count over time
watch -n 5 'ps aux | grep "php-fpm: pool" | wc -l'
```

### 7f. Quick Diagnostic Script

```bash
#!/bin/bash
# php-fpm-diag.sh — Quick PHP-FPM health check

echo "=== PHP Version ==="
php -v | head -1

echo -e "\n=== PHP-FPM Service ==="
systemctl is-active php-fpm 2>/dev/null || systemctl is-active php8.*-fpm 2>/dev/null

echo -e "\n=== PHP-FPM Processes ==="
master=$(ps aux | grep "php-fpm: master" | grep -v grep | wc -l)
workers=$(ps aux | grep "php-fpm: pool" | grep -v grep | wc -l)
echo "Master: $master | Workers: $workers"

echo -e "\n=== Memory Usage ==="
ps -eo rss,comm | grep php-fpm | awk '{sum+=$1; count++} END {
    printf "Total: %.0f MB | Workers: %d | Avg: %.0f MB\n", sum/1024, count, sum/count/1024
}'

echo -e "\n=== OPcache ==="
php -r "echo ini_get('opcache.enable') ? 'Enabled' : 'DISABLED'; echo PHP_EOL;"

echo -e "\n=== Pool Config ==="
grep -E "^(pm |pm\.|listen |user |group )" /etc/php-fpm.d/*.conf 2>/dev/null || \
grep -E "^(pm |pm\.|listen |user |group )" /etc/php/*/fpm/pool.d/*.conf 2>/dev/null

echo -e "\n=== Socket/Port Check ==="
ls -la /run/php-fpm/*.sock 2>/dev/null || ls -la /run/php/*.sock 2>/dev/null
ss -tlnp | grep php-fpm

echo -e "\n=== Recent Errors (last 10) ==="
tail -10 /var/log/php-fpm/error.log 2>/dev/null || \
tail -10 /var/log/php*-fpm.log 2>/dev/null

echo -e "\n=== Slow Log (last 5 entries) ==="
tail -25 /var/log/php-fpm/www-slow.log 2>/dev/null || echo "No slow log found"
```

---

## 8. Performance Monitoring & Optimization Checklist

### 8a. Key Metrics to Monitor

```
Metric                      Healthy Range           Alert Threshold
─────────────────────────   ─────────────────────   ────────────────────
Active processes            < 80% of max_children   > 90% of max_children
Listen queue                0                       > 0 sustained
Idle processes              > 20% of total          0 (all workers busy)
Slow requests               0                       Increasing trend
Max children reached        0                       > 0 (must increase)
OPcache hit rate            > 99%                   < 95%
OPcache free memory         > 20% of total          < 10%
Worker RSS memory           Stable over time        Growing (memory leak)
```

### 8b. Prometheus php-fpm_exporter Setup

```bash
# Install php-fpm_exporter (exports FPM status as Prometheus metrics)
# Download from https://github.com/hipages/php-fpm_exporter/releases

wget https://github.com/hipages/php-fpm_exporter/releases/latest/download/php-fpm_exporter_linux_amd64 \
    -O /usr/local/bin/php-fpm_exporter
chmod +x /usr/local/bin/php-fpm_exporter

# Run (connects to FPM status page)
/usr/local/bin/php-fpm_exporter server \
    --phpfpm.scrape-uri "unix:///run/php-fpm/www.sock;/fpm-status" \
    --web.listen-address ":9253"

# Create systemd service
cat > /etc/systemd/system/php-fpm-exporter.service << 'EOF'
[Unit]
Description=PHP-FPM Exporter for Prometheus
After=php-fpm.service

[Service]
ExecStart=/usr/local/bin/php-fpm_exporter server \
    --phpfpm.scrape-uri "unix:///run/php-fpm/www.sock;/fpm-status" \
    --web.listen-address ":9253"
Restart=always
User=nobody

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now php-fpm-exporter

# Verify metrics endpoint
curl -s http://localhost:9253/metrics | grep phpfpm

# Add to Prometheus scrape config:
# - job_name: 'php-fpm'
#   static_configs:
#     - targets: ['localhost:9253']
```

### 8c. Optimization Checklist

```
[  ] OPcache enabled and properly sized
     - opcache.enable=1, memory_consumption >= 128MB
     - opcache.validate_timestamps=0 in production
     - Hit rate > 99%, no OOM restarts

[  ] Process manager mode appropriate
     - Dedicated server with steady traffic: pm = static
     - Shared server or variable traffic: pm = dynamic
     - Low-traffic or many pools: pm = ondemand

[  ] max_children calculated correctly
     - Based on available RAM / average worker memory
     - Never hitting max_children limit in status page
     - No OOM kills in dmesg or journalctl

[  ] max_requests set to prevent memory leaks
     - pm.max_requests = 500-1000 (NOT 0)
     - Workers recycle periodically

[  ] Redis sessions instead of file-based
     - session.save_handler = redis
     - Eliminates file locking and NFS issues for multi-server setups

[  ] RDS connections managed
     - pm.max_children does not exceed RDS max_connections
     - Consider RDS Proxy for high-connection environments
     - SSL enabled for RDS connections

[  ] Slow log enabled and reviewed
     - request_slowlog_timeout = 5s
     - Regularly review for recurring slow scripts

[  ] Timeouts aligned across stack
     - max_execution_time <= request_terminate_timeout <= fastcgi_read_timeout

[  ] php.ini tuned for workload
     - memory_limit appropriate (not excessively high)
     - realpath_cache_size = 4096K
     - upload_max_filesize / post_max_size set correctly

[  ] Security hardened
     - display_errors = Off in production
     - PHP execution blocked in upload directories
     - session.cookie_secure = 1, cookie_httponly = 1
     - expose_php = Off in php.ini
```

### 8d. Benchmarking

```bash
# Apache Bench — quick load test
ab -n 1000 -c 50 https://app.example.com/
# -n 1000 = total number of requests to perform
# -c 50   = number of concurrent requests

# wrk — more advanced HTTP benchmarking
wrk -t4 -c100 -d30s https://app.example.com/
# -t4   = use 4 threads
# -c100 = maintain 100 open connections
# -d30s = test duration 30 seconds

# wrk with POST request (simulate form submission)
wrk -t2 -c50 -d10s -s post.lua https://app.example.com/api/endpoint

# Monitor PHP-FPM during load test (in another terminal)
watch -n 1 'curl -s http://localhost/fpm-status | grep -E "active|idle|queue|slow"'

# Compare before/after optimization
# Record baseline:
ab -n 5000 -c 100 https://app.example.com/ 2>&1 | tee baseline.txt
# Make changes, then:
ab -n 5000 -c 100 https://app.example.com/ 2>&1 | tee optimized.txt
# Compare: Requests per second, Time per request, Failed requests
```
