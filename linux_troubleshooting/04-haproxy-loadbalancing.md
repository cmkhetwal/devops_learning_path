# 04 - HAProxy & Load Balancing
## Complete Setup, Configuration, and High Availability

---

## SECTION 1: HAProxy Installation

```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install haproxy -y

# --- Ubuntu/Debian ---
apt install haproxy -y

# --- Install Latest Version (from source) ---
dnf install gcc pcre-devel openssl-devel systemd-devel make -y  # CentOS
apt install gcc libpcre3-dev libssl-dev libsystemd-dev make -y  # Ubuntu

cd /tmp
wget https://www.haproxy.org/download/2.9/src/haproxy-2.9.6.tar.gz
tar xzf haproxy-2.9.6.tar.gz && cd haproxy-2.9.6
make -j$(nproc) TARGET=linux-glibc USE_OPENSSL=1 USE_PCRE=1 USE_SYSTEMD=1
# -j$(nproc) = run parallel jobs matching number of CPU cores
# TARGET=linux-glibc = build for Linux with glibc
# USE_OPENSSL=1 = compile with SSL/TLS support
# USE_PCRE=1 = compile with PCRE regex support
# USE_SYSTEMD=1 = compile with systemd integration
make install

systemctl enable --now haproxy
haproxy -v    # -v = display version and build options
```

---

## SECTION 2: HAProxy Configuration

### 2.1 Full Production Configuration
```cfg
# /etc/haproxy/haproxy.cfg

#---------------------------------------------------------------------
# Global settings
#---------------------------------------------------------------------
global
    log         /dev/log local0
    log         /dev/log local1 notice
    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    maxconn     50000
    user        haproxy
    group       haproxy
    daemon

    # SSL tuning
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    tune.ssl.default-dh-param 2048

    # Stats socket for runtime commands
    stats socket /var/run/haproxy.sock mode 660 level admin
    stats timeout 30s

#---------------------------------------------------------------------
# Defaults
#---------------------------------------------------------------------
defaults
    mode                    http
    log                     global
    option                  httplog
    option                  dontlognull
    option                  http-server-close
    option                  forwardfor except 127.0.0.0/8
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         5s
    timeout client          30s
    timeout server          30s
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 30000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

#---------------------------------------------------------------------
# Stats page
#---------------------------------------------------------------------
listen stats
    bind *:8404
    mode http
    stats enable
    stats uri /stats
    stats refresh 10s
    stats admin if TRUE
    stats auth admin:StrongPassword123

#---------------------------------------------------------------------
# Frontend: HTTP (redirect to HTTPS)
#---------------------------------------------------------------------
frontend http_front
    bind *:80
    # Redirect all HTTP to HTTPS
    http-request redirect scheme https unless { ssl_fc }

#---------------------------------------------------------------------
# Frontend: HTTPS
#---------------------------------------------------------------------
frontend https_front
    bind *:443 ssl crt /etc/haproxy/certs/example.com.pem
    mode http

    # Logging
    option httplog
    log-format "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"

    # Security headers
    http-response set-header X-Frame-Options SAMEORIGIN
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header Strict-Transport-Security "max-age=63072000"

    # ACL-based routing
    acl is_api path_beg /api
    acl is_static path_end .css .js .png .jpg .gif .ico .svg .woff2
    acl is_websocket hdr(Upgrade) -i WebSocket
    acl host_blog hdr(host) -i blog.example.com
    acl host_app hdr(host) -i app.example.com

    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }

    # Route to backends
    use_backend api_servers if is_api
    use_backend static_servers if is_static
    use_backend websocket_servers if is_websocket
    use_backend blog_servers if host_blog
    use_backend app_servers if host_app
    default_backend web_servers

#---------------------------------------------------------------------
# Backend: Web Servers
#---------------------------------------------------------------------
backend web_servers
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    cookie SERVERID insert indirect nocache

    # Compression
    compression algo gzip
    compression type text/html text/plain text/css application/javascript application/json

    server web1 192.168.1.11:80 check cookie web1 weight 3 maxconn 3000
    server web2 192.168.1.12:80 check cookie web2 weight 3 maxconn 3000
    server web3 192.168.1.13:80 check cookie web3 weight 2 maxconn 2000
    server web4 192.168.1.14:80 check cookie web4 backup    # Backup server

#---------------------------------------------------------------------
# Backend: API Servers
#---------------------------------------------------------------------
backend api_servers
    balance leastconn
    option httpchk GET /api/health
    http-check expect status 200

    # Timeouts for API
    timeout server 60s
    timeout queue 30s

    server api1 192.168.1.21:8080 check inter 5s fall 3 rise 2 maxconn 500
    server api2 192.168.1.22:8080 check inter 5s fall 3 rise 2 maxconn 500
    # check = enable health checks, inter 5s = check every 5 seconds
    # fall 3 = mark down after 3 failed checks, rise 2 = mark up after 2 passed checks

#---------------------------------------------------------------------
# Backend: Static Content
#---------------------------------------------------------------------
backend static_servers
    balance roundrobin
    option httpchk HEAD /
    http-response set-header Cache-Control "public, max-age=2592000"

    server static1 192.168.1.31:80 check
    server static2 192.168.1.32:80 check

#---------------------------------------------------------------------
# Backend: WebSocket
#---------------------------------------------------------------------
backend websocket_servers
    balance source
    option httpchk GET /ws-health
    timeout tunnel 3600s      # 1 hour for websocket connections

    server ws1 192.168.1.41:8080 check
    server ws2 192.168.1.42:8080 check

#---------------------------------------------------------------------
# TCP Mode: Database Load Balancing
#---------------------------------------------------------------------
listen mysql_cluster
    bind *:3306
    mode tcp
    balance roundrobin
    option mysql-check user haproxy

    server db1 192.168.1.51:3306 check inter 5s fall 3 rise 2
    server db2 192.168.1.52:3306 check inter 5s fall 3 rise 2
    server db3 192.168.1.53:3306 check inter 5s fall 3 rise 2 backup
```

### 2.2 Load Balancing Algorithms
```cfg
# roundrobin  - Equal distribution, good default
balance roundrobin

# leastconn   - Send to server with fewest connections (best for long sessions)
balance leastconn

# source      - Same client always goes to same server (sticky by IP)
balance source

# uri         - Hash the URI (good for caching)
balance uri

# hdr(Host)   - Balance by HTTP header
balance hdr(Host)

# first       - Fill first server before using next (minimize active servers)
balance first

# random      - Random selection with power of two choices
balance random(2)
```

### 2.3 SSL/TLS Termination
```bash
# HAProxy needs cert + key in ONE file
# Combine Let's Encrypt files:
cat /etc/letsencrypt/live/example.com/fullchain.pem \
    /etc/letsencrypt/live/example.com/privkey.pem \
    > /etc/haproxy/certs/example.com.pem
chmod 600 /etc/haproxy/certs/example.com.pem

# Multiple certificates (SNI)
# bind *:443 ssl crt /etc/haproxy/certs/
# HAProxy will auto-match certificates by SNI from the directory
```

---

## SECTION 3: HAProxy High Availability with Keepalived

```bash
# Install on BOTH HAProxy servers
# CentOS/RHEL:
dnf install keepalived -y
# Ubuntu/Debian:
apt install keepalived -y
```

### Master Configuration
```cfg
# /etc/keepalived/keepalived.conf (MASTER)
global_defs {
    router_id HAPROXY_MASTER
    enable_script_security
}

vrrp_script check_haproxy {
    script "/usr/bin/killall -0 haproxy"
    interval 2       # run health check script every 2 seconds
    weight 2         # add/subtract 2 from priority if script succeeds/fails
    fall 3           # require 3 consecutive failures to mark DOWN
    rise 2           # require 2 consecutive successes to mark UP
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 101          # higher priority wins the MASTER election
    advert_int 1          # send VRRP advertisements every 1 second

    authentication {
        auth_type PASS
        auth_pass SecretPass123
    }

    virtual_ipaddress {
        192.168.1.100/24    # Virtual/Floating IP
    }

    track_script {
        check_haproxy
    }

    notify_master "/etc/keepalived/notify.sh MASTER"
    notify_backup "/etc/keepalived/notify.sh BACKUP"
    notify_fault  "/etc/keepalived/notify.sh FAULT"
}
```

### Backup Configuration
```cfg
# /etc/keepalived/keepalived.conf (BACKUP)
global_defs {
    router_id HAPROXY_BACKUP
    enable_script_security
}

vrrp_script check_haproxy {
    script "/usr/bin/killall -0 haproxy"
    interval 2       # run health check script every 2 seconds
    weight 2         # add/subtract 2 from priority if script succeeds/fails
    fall 3           # require 3 consecutive failures to mark DOWN
    rise 2           # require 2 consecutive successes to mark UP
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    virtual_router_id 51
    priority 100          # Lower than master
    advert_int 1          # send VRRP advertisements every 1 second

    authentication {
        auth_type PASS
        auth_pass SecretPass123
    }

    virtual_ipaddress {
        192.168.1.100/24
    }

    track_script {
        check_haproxy
    }
}
```

```bash
systemctl enable --now keepalived
# Test: stop haproxy on master → VIP should move to backup
# ip addr show eth0 | grep 192.168.1.100
```

---

## SECTION 4: HAProxy Management & Troubleshooting

```bash
# Test configuration
haproxy -c -f /etc/haproxy/haproxy.cfg
# -c = check configuration only (don't start)
# -f = path to configuration file

# Reload without dropping connections
systemctl reload haproxy

# Runtime management via socket
echo "show stat" | socat stdio /var/run/haproxy.sock
# socat stdio = connect standard I/O to the unix socket
# "show stat" = HAProxy command to display all backend/server statistics
echo "show info" | socat stdio /var/run/haproxy.sock
# "show info" = HAProxy command to display process-level info (uptime, connections, etc.)

# Disable/enable a backend server (maintenance)
echo "disable server web_servers/web1" | socat stdio /var/run/haproxy.sock
echo "enable server web_servers/web1" | socat stdio /var/run/haproxy.sock

# Set server to drain mode (finish existing, no new connections)
echo "set server web_servers/web1 state drain" | socat stdio /var/run/haproxy.sock

# Check backend health
echo "show servers state" | socat stdio /var/run/haproxy.sock

# View current connections
echo "show sess" | socat stdio /var/run/haproxy.sock

# Check for errors in logs
journalctl -u haproxy -f
grep -E "5[0-9]{2}" /var/log/haproxy.log | tail -20

# Monitor connections per backend
watch -n 1 'echo "show stat" | socat stdio /var/run/haproxy.sock | cut -d, -f1,2,5,8,33 | column -t -s,'
# watch -n 1 = re-run command every 1 second and refresh display
```
