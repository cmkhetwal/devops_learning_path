# Ansible Templates and File Management

## Why This Matters in DevOps

Configuration files are the nervous system of your infrastructure. Every service — Nginx, PostgreSQL, Redis, application servers — is driven by configuration files. When those files are wrong, services fail. When they are inconsistent across servers, debugging becomes a nightmare.

Templates let you generate configuration files dynamically based on variables, server facts, and environment. Instead of maintaining 50 slightly different Nginx configs for 50 servers, you maintain one template that produces the correct config for each server based on its role, environment, and resources. This is where Ansible becomes truly powerful — turning abstract infrastructure intent into concrete, server-specific configuration.

---

## Core Concepts

### Jinja2 Templates

Ansible uses Jinja2, the same template engine used by Flask and Django. Template files use the `.j2` extension.

**Variable substitution:**

```jinja
# templates/app.conf.j2
server_name = {{ server_name }}
listen_port = {{ app_port }}
workers = {{ ansible_processor_vcpus * 2 }}
log_file = {{ log_directory }}/{{ app_name }}.log
```

**Comments:**

```jinja
{# This is a Jinja2 comment — not included in output #}
# This is a config file comment — included in output
```

**Whitespace control:**

```jinja
{# Default — preserves whitespace #}
{% if ssl_enabled %}
listen 443 ssl;
{% endif %}

{# Trim whitespace with minus signs #}
{%- if ssl_enabled %}
listen 443 ssl;
{%- endif %}
```

### The Template Module

```yaml
- name: Deploy application configuration
  template:
    src: app.conf.j2              # Relative to templates/ in the role
    dest: /etc/myapp/app.conf     # Absolute path on the remote host
    owner: root
    group: root
    mode: '0644'
    backup: true                   # Create backup of existing file
    validate: '/usr/sbin/nginx -t -c %s'  # Validate before deploying
  notify: Restart application
```

The `validate` parameter is critical — it runs a validation command using the generated file. If validation fails, the old file is kept. The `%s` is replaced with the path to the temporary generated file.

### Filters

Filters transform values. They are used with the pipe `|` syntax:

```jinja
{# Default values #}
{{ database_port | default(5432) }}
{{ feature_flag | default(false) }}

{# String manipulation #}
{{ hostname | upper }}                    {# WEBSERVER01 #}
{{ hostname | lower }}                    {# webserver01 #}
{{ hostname | capitalize }}               {# Webserver01 #}
{{ hostname | replace('.', '-') }}        {# web-server-01 #}
{{ "  hello  " | trim }}                 {# hello #}

{# List operations #}
{{ servers | join(', ') }}               {# server1, server2, server3 #}
{{ servers | first }}                     {# server1 #}
{{ servers | last }}                      {# server3 #}
{{ servers | length }}                    {# 3 #}
{{ servers | sort }}                      {# sorted list #}
{{ servers | unique }}                    {# deduplicated list #}

{# Data format conversion #}
{{ config_dict | to_json }}              {# JSON string #}
{{ config_dict | to_nice_json(indent=2) }} {# Pretty JSON #}
{{ config_dict | to_yaml }}              {# YAML string #}
{{ config_dict | to_nice_yaml }}         {# Pretty YAML #}

{# Math #}
{{ memory_mb | int / 1024 }}             {# Convert MB to GB #}
{{ ansible_memtotal_mb * 0.75 | int }}   {# 75% of total memory #}

{# Type conversions #}
{{ "42" | int }}
{{ 42 | string }}
{{ "true" | bool }}

{# Path operations #}
{{ "/etc/nginx/nginx.conf" | basename }} {# nginx.conf #}
{{ "/etc/nginx/nginx.conf" | dirname }}  {# /etc/nginx #}

{# Regular expressions #}
{{ hostname | regex_replace('\..*$', '') }} {# Strip domain #}
{{ version | regex_search('(\d+\.\d+)') }} {# Extract major.minor #}

{# Hashing and encoding #}
{{ password | hash('sha256') }}
{{ data | b64encode }}
{{ encoded_data | b64decode }}

{# IP address operations #}
{{ '192.168.1.0/24' | ipaddr('network') }}   {# 192.168.1.0 #}
{{ '192.168.1.0/24' | ipaddr('netmask') }}   {# 255.255.255.0 #}
```

### Conditionals in Templates

```jinja
{# Simple if/else #}
{% if environment == 'production' %}
log_level = warn
debug = false
{% elif environment == 'staging' %}
log_level = info
debug = false
{% else %}
log_level = debug
debug = true
{% endif %}

{# Inline conditional (ternary) #}
ssl_enabled = {{ 'true' if enable_ssl else 'false' }}
workers = {{ 4 if environment == 'production' else 1 }}

{# Check if variable is defined #}
{% if custom_dns is defined %}
nameserver {{ custom_dns }}
{% endif %}

{# Check if variable is truthy #}
{% if monitoring_enabled %}
include /etc/monitoring/agent.conf
{% endif %}
```

### Loops in Templates

```jinja
{# Simple loop #}
{% for server in upstream_servers %}
server {{ server }};
{% endfor %}

{# Loop with index #}
{% for server in upstream_servers %}
server {{ server }} weight={{ loop.index }};
{% endfor %}

{# Loop with conditional #}
{% for user in users %}
{% if user.active %}
{{ user.name }}:x:{{ user.uid }}:{{ user.gid }}:{{ user.comment }}:{{ user.home }}:{{ user.shell }}
{% endif %}
{% endfor %}

{# Loop over dictionary #}
{% for key, value in environment_vars.items() %}
{{ key }}={{ value }}
{% endfor %}

{# Loop with else (when list is empty) #}
{% for server in backend_servers %}
server {{ server.host }}:{{ server.port }};
{% else %}
# No backend servers configured
server 127.0.0.1:8080 backup;
{% endfor %}

{# Nested loops #}
{% for vhost in virtual_hosts %}
server {
    listen {{ vhost.port }};
    server_name {{ vhost.name }};
{% for location in vhost.locations %}
    location {{ location.path }} {
        proxy_pass {{ location.backend }};
    }
{% endfor %}
}
{% endfor %}
```

**Loop variables:**

| Variable | Description |
|----------|-------------|
| `loop.index` | Current iteration (1-indexed) |
| `loop.index0` | Current iteration (0-indexed) |
| `loop.first` | True if first iteration |
| `loop.last` | True if last iteration |
| `loop.length` | Total number of items |
| `loop.revindex` | Iterations remaining (1-indexed) |

### Template vs Copy

```yaml
# template — processes Jinja2 syntax, generates dynamic content
- name: Deploy Nginx config (dynamic)
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf

# copy — copies file as-is, no template processing
- name: Deploy SSL certificate (static)
  copy:
    src: files/ssl/cert.pem
    dest: /etc/nginx/ssl/cert.pem
    mode: '0600'

# copy with inline content (small files, no template needed)
- name: Create maintenance page
  copy:
    content: |
      <html>
      <body>
      <h1>Under Maintenance</h1>
      </body>
      </html>
    dest: /var/www/html/maintenance.html
```

**When to use which:**
- `template` — configuration files that vary per host/environment
- `copy` — static files (certificates, binaries, images)
- `copy` with `content` — small, simple files where a template is overkill

---

## Step-by-Step Practical

### Generating Nginx Configurations from Templates

```bash
mkdir -p ~/ansible-lab/templates-demo/{templates,group_vars}
cd ~/ansible-lab/templates-demo
```

**group_vars/all.yml:**

```yaml
---
nginx_worker_processes: "{{ ansible_processor_vcpus | default(1) }}"
nginx_worker_connections: 1024

virtual_hosts:
  - name: api.example.com
    port: 80
    ssl_port: 443
    enable_ssl: true
    root: /var/www/api
    locations:
      - path: /
        backend: "http://127.0.0.1:8080"
      - path: /health
        backend: "http://127.0.0.1:8080"
        cache_ttl: 5
      - path: /static
        root: /var/www/api/static
        static: true

  - name: admin.example.com
    port: 80
    ssl_port: 443
    enable_ssl: false
    root: /var/www/admin
    locations:
      - path: /
        backend: "http://127.0.0.1:9090"

upstream_servers:
  api:
    - { host: "10.0.1.10", port: 8080, weight: 5 }
    - { host: "10.0.1.11", port: 8080, weight: 5 }
    - { host: "10.0.1.12", port: 8080, weight: 3 }
  admin:
    - { host: "10.0.2.10", port: 9090 }

rate_limiting:
  enabled: true
  requests_per_second: 10
  burst: 20

security_headers:
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: "1; mode=block"
  Strict-Transport-Security: "max-age=31536000; includeSubDomains"
```

**templates/nginx.conf.j2:**

```nginx
# Managed by Ansible — DO NOT EDIT MANUALLY
# Host: {{ inventory_hostname }}
# Generated: {{ ansible_date_time.iso8601 | default('unknown') }}

worker_processes {{ nginx_worker_processes }};
pid /run/nginx.pid;

events {
    worker_connections {{ nginx_worker_connections }};
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;

{% if rate_limiting.enabled | default(false) %}
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate={{ rate_limiting.requests_per_second }}r/s;
{% endif %}

    # Upstream definitions
{% for name, servers in upstream_servers.items() %}
    upstream {{ name }}_backend {
{% for server in servers %}
        server {{ server.host }}:{{ server.port }}{{ ' weight=' ~ server.weight if server.weight is defined else '' }};
{% endfor %}
    }

{% endfor %}
    # Virtual hosts
{% for vhost in virtual_hosts %}
    server {
        listen {{ vhost.port }};
        server_name {{ vhost.name }};
{% if vhost.enable_ssl | default(false) %}

        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen {{ vhost.ssl_port }} ssl http2;
        server_name {{ vhost.name }};

        ssl_certificate /etc/nginx/ssl/{{ vhost.name }}.crt;
        ssl_certificate_key /etc/nginx/ssl/{{ vhost.name }}.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
{% endif %}

        root {{ vhost.root }};

        # Security headers
{% for header, value in security_headers.items() %}
        add_header {{ header }} "{{ value }}" always;
{% endfor %}

{% for location in vhost.locations %}
        location {{ location.path }} {
{% if location.static | default(false) %}
            root {{ location.root }};
            expires 30d;
            add_header Cache-Control "public, immutable";
{% else %}
            proxy_pass {{ location.backend }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
{% if rate_limiting.enabled | default(false) %}
            limit_req zone=api burst={{ rate_limiting.burst }} nodelay;
{% endif %}
{% if location.cache_ttl is defined %}
            proxy_cache_valid 200 {{ location.cache_ttl }}s;
{% endif %}
{% endif %}
        }

{% endfor %}
    }

{% endfor %}
}
```

**templates/docker-compose.yml.j2:**

```yaml
# Managed by Ansible
# Generated: {{ ansible_date_time.iso8601 | default('unknown') }}
version: "3.8"

services:
{% for vhost in virtual_hosts %}
  {{ vhost.name | replace('.', '-') }}:
    image: nginx:latest
    ports:
      - "{{ vhost.port }}:{{ vhost.port }}"
{% if vhost.enable_ssl | default(false) %}
      - "{{ vhost.ssl_port }}:{{ vhost.ssl_port }}"
{% endif %}
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - {{ vhost.root }}:{{ vhost.root }}:ro
    restart: unless-stopped

{% endfor %}
```

**site.yml:**

```yaml
---
- name: Generate configurations from templates
  hosts: local
  gather_facts: true

  tasks:
    - name: Create output directory
      file:
        path: /tmp/ansible-templates-demo
        state: directory
        mode: '0755'

    - name: Generate Nginx configuration
      template:
        src: templates/nginx.conf.j2
        dest: /tmp/ansible-templates-demo/nginx.conf
        mode: '0644'

    - name: Generate Docker Compose file
      template:
        src: templates/docker-compose.yml.j2
        dest: /tmp/ansible-templates-demo/docker-compose.yml
        mode: '0644'

    - name: Display generated Nginx config
      command: cat /tmp/ansible-templates-demo/nginx.conf
      register: nginx_config
      changed_when: false

    - name: Show Nginx config
      debug:
        var: nginx_config.stdout_lines
```

**inventory.ini:**

```ini
[local]
localhost ansible_connection=local
```

**Run:**

```bash
ansible-playbook site.yml -i inventory.ini
cat /tmp/ansible-templates-demo/nginx.conf
cat /tmp/ansible-templates-demo/docker-compose.yml
```

---

## Exercises

### Exercise 1: Multi-Environment Templates
Create a template for a database configuration file that changes significantly between environments: dev uses SQLite, staging uses PostgreSQL with 10 connections, production uses PostgreSQL with 100 connections and replication. Use conditionals and variables to generate the correct config for each environment.

### Exercise 2: Dynamic Upstream Configuration
Create an Nginx upstream template where the list of backend servers comes from inventory groups. Use `groups['webservers']` and `hostvars` to dynamically list all web server IPs as upstream backends.

### Exercise 3: Filter Practice
Write a template that takes a list of users (with name, email, department) and generates: (a) a CSV file using `join`, (b) a JSON file using `to_nice_json`, (c) a summary text file counting users per department using `selectattr` and `groupby`.

### Exercise 4: Complex Nested Template
Create a template for a monitoring configuration (like Prometheus) that generates scrape targets from a dictionary of services, each with multiple instances, different ports, and optional labels. Use nested loops and conditionals.

### Exercise 5: Configuration Validation
Write a playbook that generates a configuration file from a template and validates it before deploying. Use the `validate` parameter of the `template` module. Create a deliberate error in the template and observe how validation prevents a bad config from being deployed.

---

## Knowledge Check

### Question 1
What is the difference between the `template` and `copy` modules?

<details>
<summary>Answer</summary>

The `template` module processes files through the Jinja2 template engine, resolving variables (`{{ var }}`), evaluating conditionals (`{% if %}`), and executing loops (`{% for %}`). It generates dynamic content based on variables and facts. The `copy` module transfers files as-is without any processing. Use `template` for configuration files that need to vary per host, environment, or role. Use `copy` for static files (SSL certificates, binary files, scripts that do not need variable substitution). Both modules are idempotent — they check if the destination file matches before making changes.
</details>

### Question 2
What are Jinja2 filters and why are they important?

<details>
<summary>Answer</summary>

Jinja2 filters are functions that transform values using the pipe (`|`) syntax. They are important because they let you manipulate data within templates without writing custom code. Common uses: `default()` provides fallback values for undefined variables (preventing errors), `join()` converts lists to strings, `to_json` and `to_yaml` serialize data structures, `int` and `string` convert types, `regex_replace` transforms strings, and `ipaddr` manipulates IP addresses. Filters enable templates to be self-contained — all data transformation happens in the template rather than requiring preprocessing in tasks. They also make templates more readable than equivalent Jinja2 code using built-in functions.
</details>

### Question 3
How do you handle a list of items in a Jinja2 template that needs commas between items but not after the last one?

<details>
<summary>Answer</summary>

Use `loop.last` to conditionally add the comma: `{{ item }}{{ ',' if not loop.last else '' }}`. For example, in a JSON array: `{% for server in servers %}"{{ server }}"{{ "," if not loop.last }}{% endfor %}`. Alternatively, use the `join` filter for simple cases: `{{ servers | join(', ') }}`. For complex structures, use the `to_json` or `to_nice_json` filter on the entire data structure rather than manually formatting JSON in templates, which avoids comma issues entirely.
</details>

### Question 4
What does the `validate` parameter do in the template module and why should you use it?

<details>
<summary>Answer</summary>

The `validate` parameter runs a command to check the generated file before deploying it to the destination. The `%s` placeholder is replaced with the path to the temporary file. For example, `validate: 'nginx -t -c %s'` runs nginx's configuration test on the generated file. If validation fails, the old file at the destination is kept unchanged, preventing a bad configuration from breaking the service. You should use it whenever a validation command exists: `nginx -t`, `named-checkconf`, `apache2ctl configtest`, `python -m py_compile %s`, `visudo -c -f %s`. This is a critical safety net that prevents configuration errors from causing outages.
</details>

### Question 5
How do you manage configuration files that differ across environments (dev/staging/prod) using templates?

<details>
<summary>Answer</summary>

The recommended approach is to use the same template for all environments but drive the differences through variables. Store environment-specific variables in `group_vars/` (e.g., `group_vars/dev.yml`, `group_vars/prod.yml`). The template uses conditionals and variables to produce the correct output: `{% if environment == 'production' %}` for environment-specific blocks, `{{ database_host }}` for values that differ by environment. This is better than maintaining separate templates per environment because: (1) there is one source of truth for the configuration structure, (2) structural changes are made once, not N times, (3) the differences between environments are explicit in the variable files, and (4) you can compare environments by diffing their variable files.
</details>
