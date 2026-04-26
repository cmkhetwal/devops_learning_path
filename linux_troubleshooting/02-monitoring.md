# 02 - Infrastructure Monitoring Setup
## End-to-End Linux Infrastructure Monitoring

---

## SECTION 1: Prometheus + Grafana (Industry Standard - Recommended)

### 1.1 Install Prometheus (Monitoring Server)

```bash
# --- All Distros ---
# Create user
useradd --no-create-home --shell /bin/false prometheus
# --no-create-home = skip creating a home directory for this user
# --shell /bin/false = prevent interactive login (service account only)
mkdir -p /etc/prometheus /var/lib/prometheus
chown prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Download latest Prometheus
cd /tmp
PROM_VER="2.51.0"  # Check latest at https://prometheus.io/download/
wget https://github.com/prometheus/prometheus/releases/download/v${PROM_VER}/prometheus-${PROM_VER}.linux-amd64.tar.gz
tar xzf prometheus-${PROM_VER}.linux-amd64.tar.gz
cd prometheus-${PROM_VER}.linux-amd64

cp prometheus promtool /usr/local/bin/
cp -r consoles console_libraries /etc/prometheus/
chown -R prometheus:prometheus /etc/prometheus
```

#### Prometheus Configuration
```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets:
        - 'server1:9100'
        - 'server2:9100'
        - 'server3:9100'
    # For large farms, use file-based discovery:
    # file_sd_configs:
    #   - files:
    #     - '/etc/prometheus/targets/*.json'
    #     refresh_interval: 5m

  - job_name: 'nginx'
    static_configs:
      - targets: ['webserver1:9113']

  - job_name: 'apache'
    static_configs:
      - targets: ['webserver2:9117']

  - job_name: 'haproxy'
    static_configs:
      - targets: ['lb1:8404']

  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://example.com
        - https://api.example.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
```

#### Prometheus Systemd Service
```ini
# /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --storage.tsdb.retention.time=30d \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.enable-lifecycle
# --config.file = path to prometheus config file
# --storage.tsdb.path = directory for time-series database storage
# --storage.tsdb.retention.time=30d = keep metrics data for 30 days
# --web.enable-lifecycle = allow config reload via HTTP POST to /-/reload
ExecReload=/bin/kill -HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now prometheus
# Access: http://server:9090
```

### 1.2 Install Node Exporter (On Every Server)
```bash
# Create user
useradd --no-create-home --shell /bin/false node_exporter
# --no-create-home = no home directory, --shell /bin/false = no login shell

# Download
NODE_VER="1.7.0"
wget https://github.com/prometheus/node_exporter/releases/download/v${NODE_VER}/node_exporter-${NODE_VER}.linux-amd64.tar.gz
tar xzf node_exporter-${NODE_VER}.linux-amd64.tar.gz
cp node_exporter-${NODE_VER}.linux-amd64/node_exporter /usr/local/bin/
chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

```ini
# /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --collector.systemd \
    --collector.processes \
    --collector.tcpstat
# --collector.systemd = enable systemd service state metrics
# --collector.processes = enable process count and state metrics
# --collector.tcpstat = enable TCP connection state metrics
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now node_exporter
# Verify: curl http://localhost:9100/metrics
```

### 1.3 Install Grafana
```bash
# --- CentOS/RHEL/Amazon Linux ---
cat > /etc/yum.repos.d/grafana.repo << 'EOF'
[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF
dnf install grafana -y

# --- Ubuntu/Debian ---
apt install -y apt-transport-https software-properties-common
wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" > /etc/apt/sources.list.d/grafana.list
apt update && apt install grafana -y

# Start
systemctl enable --now grafana-server
# Access: http://server:3000 (admin/admin)

# Add Prometheus as data source in Grafana UI:
# Configuration → Data Sources → Add → Prometheus → URL: http://localhost:9090
# Import dashboards: Dashboard → Import → ID: 1860 (Node Exporter Full)
```

### 1.4 Alertmanager Setup
```bash
# Download and install Alertmanager
ALERT_VER="0.27.0"
wget https://github.com/prometheus/alertmanager/releases/download/v${ALERT_VER}/alertmanager-${ALERT_VER}.linux-amd64.tar.gz
tar xzf alertmanager-${ALERT_VER}.linux-amd64.tar.gz
cp alertmanager-${ALERT_VER}.linux-amd64/alertmanager /usr/local/bin/
cp alertmanager-${ALERT_VER}.linux-amd64/amtool /usr/local/bin/
mkdir -p /etc/alertmanager
```

```yaml
# /etc/alertmanager/alertmanager.yml
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'email-team'

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      repeat_interval: 1h

    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'email-team'
    email_configs:
      - to: 'team@example.com'

  - name: 'slack-warnings'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/xxx/yyy/zzz'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
```

#### Prometheus Alert Rules
```yaml
# /etc/prometheus/alerts/node_alerts.yml
groups:
  - name: node_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}%"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory on {{ $labels.instance }}"
          description: "Memory usage is {{ $value }}%"

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "{{ $labels.mountpoint }} is {{ $value }}% full"

      - alert: DiskSpaceCritical
        expr: (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes)) * 100 > 95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: Disk almost full on {{ $labels.instance }}"

      - alert: InstanceDown
        expr: up == 0
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is DOWN"

      - alert: HighSwapUsage
        expr: (1 - (node_memory_SwapFree_bytes / node_memory_SwapTotal_bytes)) * 100 > 50
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High swap usage on {{ $labels.instance }}"

      - alert: SystemdServiceFailed
        expr: node_systemd_unit_state{state="failed"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.name }} failed on {{ $labels.instance }}"
```

---

## SECTION 2: ELK Stack (Centralized Logging)

### 2.1 Elasticsearch Setup
```bash
# --- CentOS/RHEL/Amazon Linux ---
rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
cat > /etc/yum.repos.d/elasticsearch.repo << 'EOF'
[elasticsearch]
name=Elasticsearch repository
baseurl=https://artifacts.elastic.co/packages/8.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF
dnf install elasticsearch -y

# --- Ubuntu/Debian ---
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list
apt update && apt install elasticsearch -y
```

```yaml
# /etc/elasticsearch/elasticsearch.yml (key settings)
cluster.name: my-cluster
node.name: node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
discovery.type: single-node    # For single server; remove for cluster
xpack.security.enabled: true
```

```bash
# JVM Heap - Set to 50% of RAM (max 32GB)
# /etc/elasticsearch/jvm.options.d/heap.options
echo "-Xms4g" > /etc/elasticsearch/jvm.options.d/heap.options
echo "-Xmx4g" >> /etc/elasticsearch/jvm.options.d/heap.options

systemctl enable --now elasticsearch
# Generate passwords:
/usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

### 2.2 Kibana Setup
```bash
# Install (same repo as Elasticsearch)
# CentOS/RHEL:
dnf install kibana -y
# Ubuntu/Debian:
apt install kibana -y
```

```yaml
# /etc/kibana/kibana.yml
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
elasticsearch.username: "kibana_system"
elasticsearch.password: "your-password"
```

```bash
systemctl enable --now kibana
# Access: http://server:5601
```

### 2.3 Filebeat (Log Shipper - Install on All Servers)
```bash
# CentOS/RHEL:
dnf install filebeat -y
# Ubuntu/Debian:
apt install filebeat -y
```

```yaml
# /etc/filebeat/filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/syslog
      - /var/log/messages
      - /var/log/auth.log
      - /var/log/secure
    fields:
      server_type: linux
      environment: production

  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.log
    fields:
      service: nginx
      log_type: access

  - type: log
    enabled: true
    paths:
      - /var/log/nginx/error.log
    fields:
      service: nginx
      log_type: error

output.elasticsearch:
  hosts: ["elk-server:9200"]
  username: "elastic"
  password: "your-password"
  index: "filebeat-%{+yyyy.MM.dd}"

setup.kibana:
  host: "elk-server:5601"
```

```bash
# Enable modules for common services
filebeat modules enable system nginx apache mysql
# modules enable = activate built-in parsers for these log formats
filebeat setup    # Load Kibana dashboards, index templates, and index patterns
systemctl enable --now filebeat
```

---

## SECTION 3: Nagios (Classic Monitoring)

### 3.1 Nagios Server Setup
```bash
# --- CentOS/RHEL ---
dnf install -y gcc glibc glibc-common gd gd-devel make net-snmp \
    openssl-devel xinetd unzip httpd php php-fpm

useradd nagios
groupadd nagcmd
usermod -aG nagcmd nagios
usermod -aG nagcmd apache

# Download and compile
cd /tmp
wget https://github.com/NagiosEnterprises/nagioscore/releases/download/nagios-4.5.1/nagios-4.5.1.tar.gz
tar xzf nagios-4.5.1.tar.gz
cd nagios-4.5.1
./configure --with-command-group=nagcmd
make all
make install
make install-init
make install-config
make install-commandmode
make install-webconf

# Set admin password
htpasswd -c /usr/local/nagios/etc/htpasswd.users nagiosadmin

# Install plugins
cd /tmp
wget https://github.com/nagios-plugins/nagios-plugins/releases/download/release-2.4.8/nagios-plugins-2.4.8.tar.gz
tar xzf nagios-plugins-2.4.8.tar.gz
cd nagios-plugins-2.4.8
./configure
make && make install

systemctl enable --now nagios httpd
# Access: http://server/nagios
```

### 3.2 NRPE (Remote Monitoring Agent)
```bash
# Install on monitored servers
# CentOS/RHEL:
dnf install -y epel-release && dnf install -y nrpe nagios-plugins-all

# Ubuntu/Debian:
apt install -y nagios-nrpe-server nagios-plugins

# /etc/nagios/nrpe.cfg (key settings)
allowed_hosts=127.0.0.1,NAGIOS_SERVER_IP
command[check_disk]=/usr/lib64/nagios/plugins/check_disk -w 20% -c 10% -p /
command[check_load]=/usr/lib64/nagios/plugins/check_load -w 5,4,3 -c 10,8,6
command[check_mem]=/usr/lib64/nagios/plugins/check_mem -w 80 -c 90
command[check_swap]=/usr/lib64/nagios/plugins/check_swap -w 30% -c 15%
command[check_zombie_procs]=/usr/lib64/nagios/plugins/check_procs -w 5 -c 10 -s Z
command[check_total_procs]=/usr/lib64/nagios/plugins/check_procs -w 250 -c 400

systemctl enable --now nrpe
```

---

## SECTION 4: Zabbix (Enterprise Monitoring)

### 4.1 Quick Zabbix Server Setup
```bash
# --- CentOS/RHEL 8+ ---
rpm -Uvh https://repo.zabbix.com/zabbix/7.0/rhel/8/x86_64/zabbix-release-7.0-1.el8.noarch.rpm
dnf install zabbix-server-mysql zabbix-web-mysql zabbix-apache-conf zabbix-sql-scripts zabbix-agent -y

# --- Ubuntu 22.04 ---
wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-1+ubuntu22.04_all.deb
dpkg -i zabbix-release_7.0-1+ubuntu22.04_all.deb
apt update
apt install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent -y

# Create database
mysql -u root -p <<EOF
CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER 'zabbix'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
SET GLOBAL log_bin_trust_function_creators = 1;
EOF

# Import schema
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql -u zabbix -p zabbix

# Configure
sed -i 's/# DBPassword=/DBPassword=StrongPassword123!/' /etc/zabbix/zabbix_server.conf

systemctl enable --now zabbix-server zabbix-agent httpd php-fpm
# Complete setup via web: http://server/zabbix
```

### 4.2 Zabbix Agent (On All Servers)
```bash
# Install agent
# CentOS/RHEL:
dnf install zabbix-agent -y
# Ubuntu/Debian:
apt install zabbix-agent -y

# /etc/zabbix/zabbix_agentd.conf
Server=ZABBIX_SERVER_IP
ServerActive=ZABBIX_SERVER_IP
Hostname=this-server-hostname
EnableRemoteCommands=0

systemctl enable --now zabbix-agent
```

---

## SECTION 5: CloudWatch Agent (AWS/Amazon Linux)

```bash
# Install CloudWatch Agent
# Amazon Linux / CentOS:
dnf install amazon-cloudwatch-agent -y
# Or download directly:
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U amazon-cloudwatch-agent.rpm

# Run wizard
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Or use manual config:
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
  "metrics": {
    "namespace": "CustomLinuxMetrics",
    "metrics_collected": {
      "cpu": { "measurement": ["cpu_usage_idle","cpu_usage_user","cpu_usage_system"], "totalcpu": true },
      "disk": { "measurement": ["used_percent","inodes_free"], "resources": ["*"] },
      "diskio": { "measurement": ["io_time","reads","writes"] },
      "mem": { "measurement": ["mem_used_percent","mem_available"] },
      "swap": { "measurement": ["swap_used_percent"] },
      "net": { "measurement": ["bytes_sent","bytes_recv","packets_sent","packets_recv"] }
    },
    "append_dimensions": { "InstanceId": "${aws:InstanceId}" },
    "aggregation_dimensions": [["InstanceId"]]
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          { "file_path": "/var/log/messages", "log_group_name": "/linux/messages" },
          { "file_path": "/var/log/secure", "log_group_name": "/linux/secure" },
          { "file_path": "/var/log/nginx/error.log", "log_group_name": "/nginx/error" }
        ]
      }
    }
  }
}
EOF

# Start agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
```
