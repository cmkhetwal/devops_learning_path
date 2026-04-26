# 09 - Performance Tuning
## Kernel, Nginx, Apache, MySQL/MariaDB, Network Stack

---

## SECTION 1: Linux Kernel Tuning

### 1.1 sysctl.conf - Core System Tuning
```bash
# /etc/sysctl.d/99-performance.conf
# Apply with: sysctl -p /etc/sysctl.d/99-performance.conf
# -p = load settings from the specified file (default: /etc/sysctl.conf)

# --- Memory ---
vm.swappiness = 10                           # Reduce swap tendency (default 60)
vm.dirty_ratio = 15                          # % of RAM for dirty pages before forced write
vm.dirty_background_ratio = 5                # % of RAM for dirty pages before background write
vm.overcommit_memory = 0                     # 0=heuristic, 1=always allow, 2=never overcommit
vm.vfs_cache_pressure = 50                   # Reduce inode/dentry cache reclaim

# --- Network - Connection Handling ---
net.core.somaxconn = 65535                   # Max listen() backlog
net.core.netdev_max_backlog = 65535          # Max packets queued on input
net.ipv4.tcp_max_syn_backlog = 65535         # Max SYN queue
net.ipv4.tcp_max_tw_buckets = 2000000        # Max TIME_WAIT sockets
net.ipv4.tcp_tw_reuse = 1                    # Reuse TIME_WAIT sockets
net.ipv4.ip_local_port_range = 1024 65535    # More ephemeral ports
net.ipv4.tcp_fin_timeout = 15                # Reduce FIN_WAIT2 timeout (default 60)

# --- Network - Performance ---
net.core.rmem_max = 16777216                 # Max receive buffer
net.core.wmem_max = 16777216                 # Max send buffer
net.core.rmem_default = 1048576
net.core.wmem_default = 1048576
net.ipv4.tcp_rmem = 4096 1048576 16777216    # TCP receive buffer (min, default, max)
net.ipv4.tcp_wmem = 4096 1048576 16777216    # TCP send buffer
net.ipv4.tcp_window_scaling = 1              # Enable window scaling
net.ipv4.tcp_timestamps = 1                  # Enable timestamps

# --- Network - Keepalive ---
net.ipv4.tcp_keepalive_time = 600            # Start keepalive after 10min idle
net.ipv4.tcp_keepalive_intvl = 60            # Keepalive interval
net.ipv4.tcp_keepalive_probes = 5            # Keepalive retries before drop

# --- Network - Security ---
net.ipv4.tcp_syncookies = 1                  # SYN flood protection
net.ipv4.conf.all.rp_filter = 1              # Reverse path filtering
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1     # Ignore broadcast pings
net.ipv4.conf.all.accept_redirects = 0       # Don't accept ICMP redirects
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# --- File System ---
fs.file-max = 2097152                        # Max open files system-wide
fs.inotify.max_user_watches = 524288         # For file watchers
fs.aio-max-nr = 1048576                      # Async I/O events
```

### 1.2 Limits Configuration
```bash
# /etc/security/limits.d/99-nofile.conf
# Increase open file limits for all users

*    soft    nofile    65535
*    hard    nofile    65535
*    soft    nproc     65535
*    hard    nproc     65535
root soft    nofile    65535
root hard    nofile    65535

# For specific service users:
nginx    soft    nofile    65535
nginx    hard    nofile    65535
mysql    soft    nofile    65535
mysql    hard    nofile    65535

# Verify:
ulimit -n       # Current shell
cat /proc/<PID>/limits | grep "open files"  # Specific process
```

### 1.3 Systemd Service Limits
```bash
# For specific services, override in systemd unit:
systemctl edit nginx    # edit = open an editor to create a drop-in override file for the unit
# Add:
[Service]
LimitNOFILE=65535
LimitNPROC=65535

# Or create drop-in manually:
mkdir -p /etc/systemd/system/nginx.service.d/
cat > /etc/systemd/system/nginx.service.d/limits.conf << 'EOF'
[Service]
LimitNOFILE=65535
EOF
systemctl daemon-reload
systemctl restart nginx
```

---

## SECTION 2: Nginx Performance Tuning

```nginx
# /etc/nginx/nginx.conf

worker_processes auto;                  # = CPU cores
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;            # Per worker (total = workers × connections)
    multi_accept on;
    use epoll;                          # Linux-specific high-performance event method
}

http {
    # --- Connection Handling ---
    keepalive_timeout 65;
    keepalive_requests 1000;            # Requests per keepalive connection
    reset_timedout_connection on;       # Free memory from timed-out connections

    # --- Buffers (reduce disk I/O) ---
    client_body_buffer_size 16k;        # POST body buffer
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    proxy_buffer_size 8k;
    proxy_buffers 32 16k;
    proxy_busy_buffers_size 64k;

    # --- Proxy Performance ---
    proxy_http_version 1.1;
    proxy_set_header Connection "";     # Enable keepalive to backend

    upstream backend {
        keepalive 64;                   # Keep connections to backend alive
        server 127.0.0.1:8080;
    }

    # --- Caching ---
    # Proxy cache
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m
                     max_size=10g inactive=60m use_temp_path=off;

    server {
        location / {
            proxy_cache my_cache;
            proxy_cache_valid 200 302 10m;
            proxy_cache_valid 404 1m;
            proxy_cache_use_stale error timeout updating http_500 http_502 http_503;
            add_header X-Cache-Status $upstream_cache_status;
        }

        # Static file optimization
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
            access_log off;
            tcp_nodelay off;
            open_file_cache max=3000 inactive=120s;
            open_file_cache_valid 45s;
            open_file_cache_min_uses 2;
            open_file_cache_errors off;
        }
    }

    # --- Gzip ---
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 4;                  # 4 is sweet spot (higher = more CPU)
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript
               image/svg+xml;

    # --- Rate Limiting ---
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            limit_conn addr 10;
        }
    }

    # --- Logging Optimization ---
    access_log /var/log/nginx/access.log main buffer=32k flush=5m;
    # Or conditional logging (skip health checks):
    map $request_uri $loggable {
        /health 0;
        /ping   0;
        default 1;
    }
    access_log /var/log/nginx/access.log main if=$loggable;
}
```

---

## SECTION 3: Apache Performance Tuning

```apache
# Use Event MPM (best for modern workloads)
# /etc/httpd/conf.modules.d/00-mpm.conf
LoadModule mpm_event_module modules/mod_mpm_event.so
# Comment out: LoadModule mpm_prefork_module ...

# /etc/httpd/conf.d/performance.conf
<IfModule mpm_event_module>
    ServerLimit         16
    StartServers        4
    MinSpareThreads     75
    MaxSpareThreads     250
    ThreadLimit         64
    ThreadsPerChild     64
    MaxRequestWorkers   1024
    MaxConnectionsPerChild 10000
</IfModule>

# KeepAlive
KeepAlive On
MaxKeepAliveRequests 100
KeepAliveTimeout 5

# Timeouts
Timeout 60
RequestReadTimeout header=20-40,MinRate=500 body=20-60,MinRate=500

# Disable unnecessary modules
# Comment out in /etc/httpd/conf.modules.d/:
# mod_autoindex, mod_cgi, mod_status (if not needed), mod_userdir

# Compression
<IfModule mod_deflate.c>
    SetOutputFilter DEFLATE
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css
    AddOutputFilterByType DEFLATE application/javascript application/json
    DeflateCompressionLevel 4
    SetEnvIfNoCase Request_URI \.(?:gif|jpe?g|png|ico)$ no-gzip
</IfModule>

# Caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresDefault "access plus 1 day"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>

# ETag - remove for load-balanced setups
FileETag None

# Disable .htaccess lookups where not needed
<Directory /var/www/html/static>
    AllowOverride None
</Directory>

# Security
ServerTokens Prod
ServerSignature Off
TraceEnable Off
```

---

## SECTION 4: MySQL/MariaDB Performance Tuning

```ini
# /etc/my.cnf.d/performance.cnf (CentOS)
# /etc/mysql/mysql.conf.d/performance.cnf (Ubuntu)

[mysqld]
# --- InnoDB (most important) ---
innodb_buffer_pool_size = 4G          # 60-70% of RAM for dedicated DB server
innodb_buffer_pool_instances = 4       # 1 per GB of buffer pool
innodb_log_file_size = 256M           # Larger = better write performance
innodb_flush_log_at_trx_commit = 2    # 1=safest, 2=fast (1s data loss risk)
innodb_flush_method = O_DIRECT        # Skip OS cache for data files
innodb_file_per_table = 1             # Each table gets own file
innodb_io_capacity = 2000             # IOPS for background tasks (SSD: 2000+)
innodb_io_capacity_max = 4000
innodb_read_io_threads = 8
innodb_write_io_threads = 8

# --- Connections ---
max_connections = 500
max_connect_errors = 100
wait_timeout = 600                     # Close idle connections after 10 min
interactive_timeout = 600
thread_cache_size = 50

# --- Query Cache (MariaDB) ---
# Disabled in MySQL 8+
query_cache_type = 0                   # Disable (often causes contention)
query_cache_size = 0

# --- Buffers ---
sort_buffer_size = 4M
read_buffer_size = 2M
read_rnd_buffer_size = 8M
join_buffer_size = 4M
tmp_table_size = 64M
max_heap_table_size = 64M

# --- Logging ---
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2                    # Log queries taking > 2 seconds
log_queries_not_using_indexes = 1

# --- Binary Logging (for replication/backup) ---
log_bin = /var/lib/mysql/mysql-bin
binlog_expire_logs_seconds = 604800    # 7 days
max_binlog_size = 256M
```

```bash
# Check current settings
mysql -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';"
mysql -e "SHOW GLOBAL STATUS LIKE 'Threads_connected';"

# Check buffer pool hit rate (should be >99%)
mysql -e "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';"

# Check slow queries
mysql -e "SHOW GLOBAL STATUS LIKE 'Slow_queries';"
mysqldumpslow /var/log/mysql/slow.log | head -20

# Check connections
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW GLOBAL STATUS LIKE 'Max_used_connections';"
```

---

## SECTION 5: Network Stack Tuning for High-Traffic Servers

```bash
# /etc/sysctl.d/99-network-tuning.conf

# Increase socket buffers for 10Gbps+
net.core.rmem_max = 67108864
net.core.wmem_max = 67108864
net.ipv4.tcp_rmem = 4096 1048576 67108864
net.ipv4.tcp_wmem = 4096 1048576 67108864

# Enable TCP BBR congestion control (better than cubic for WAN)
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Connection optimization
net.ipv4.tcp_fastopen = 3              # Enable TCP Fast Open (client+server)
net.ipv4.tcp_slow_start_after_idle = 0 # Don't reset cwnd after idle
net.ipv4.tcp_mtu_probing = 1           # Auto MTU discovery
net.ipv4.tcp_max_syn_backlog = 65535
net.core.somaxconn = 65535

# Reduce TIME_WAIT accumulation
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_max_tw_buckets = 2000000
net.ipv4.ip_local_port_range = 1024 65535

# Apply
sysctl -p /etc/sysctl.d/99-network-tuning.conf
# -p = load settings from the specified file

# Verify BBR is active
sysctl net.ipv4.tcp_congestion_control
```

---

## SECTION 6: I/O Scheduler Tuning

```bash
# Check current scheduler
cat /sys/block/sda/queue/scheduler

# For SSDs/NVMe: none (noop) or mq-deadline
echo "none" > /sys/block/sda/queue/scheduler        # NVMe
echo "mq-deadline" > /sys/block/sda/queue/scheduler  # SATA SSD

# For HDDs: mq-deadline or bfq
echo "mq-deadline" > /sys/block/sda/queue/scheduler

# Persistent (udev rule):
cat > /etc/udev/rules.d/60-io-scheduler.rules << 'EOF'
# SSD/NVMe
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="none"
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
# HDD
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="mq-deadline"
EOF

# Tune read-ahead for sequential workloads
blockdev --setra 4096 /dev/sda        # 2MB read-ahead
# --setra = set read-ahead sectors (4096 sectors x 512 bytes = 2MB)
```
