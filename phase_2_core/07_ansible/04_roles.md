# Ansible Roles

## Why This Matters in DevOps

As your Ansible automation grows, you face the same problem that hit your Terraform code: everything in one massive file becomes unmaintainable. A 500-line playbook that installs packages, templates configurations, manages services, and handles deployments is hard to read, hard to test, and impossible to reuse.

Roles solve this by packaging related tasks, handlers, variables, templates, and files into a structured, reusable unit. When you need an Nginx setup, you use the nginx role. When you need PostgreSQL, you use the postgresql role. When a new team member joins, they understand the directory structure immediately because every role follows the same convention. Roles are how professional Ansible automation is organized.

---

## Core Concepts

### Why Roles Exist

Without roles:

```yaml
# site.yml — 500 lines, everything mixed together
- name: Configure everything
  hosts: all
  tasks:
    # 50 tasks for nginx
    # 30 tasks for postgresql
    # 40 tasks for monitoring
    # 20 tasks for security hardening
    # 25 tasks for log rotation
    # ...impossible to maintain
```

With roles:

```yaml
# site.yml — clean, readable, reusable
- name: Configure web servers
  hosts: webservers
  roles:
    - common
    - nginx
    - monitoring

- name: Configure database servers
  hosts: databases
  roles:
    - common
    - postgresql
    - monitoring
    - backup
```

Each role is a self-contained unit. You can develop, test, version, and share roles independently.

### Role Directory Structure

```
roles/
  nginx/
    tasks/
      main.yml           # Entry point — task list
    handlers/
      main.yml           # Handlers (service restarts, etc.)
    templates/
      nginx.conf.j2      # Jinja2 templates
      site.conf.j2
    files/
      ssl/               # Static files to copy (certs, scripts)
    vars/
      main.yml           # Role variables (high precedence)
    defaults/
      main.yml           # Default variables (easily overridden)
    meta/
      main.yml           # Role metadata (dependencies, info)
    tests/
      inventory          # Test inventory
      test.yml           # Test playbook
    README.md            # Documentation
```

**Which directory for what:**

| Directory | Purpose | Example |
|-----------|---------|---------|
| `tasks/` | The main list of tasks | Install packages, configure services |
| `handlers/` | Event-triggered tasks | Restart nginx, reload firewall |
| `templates/` | Jinja2 template files | nginx.conf.j2, app.conf.j2 |
| `files/` | Static files to copy | SSL certificates, scripts |
| `vars/` | High-precedence variables | Calculated values, internal constants |
| `defaults/` | Default values (user-overridable) | Port numbers, feature flags |
| `meta/` | Role metadata | Dependencies, minimum Ansible version |

### Creating a Role

```bash
# Create role scaffolding
ansible-galaxy role init roles/nginx
# Creates the entire directory structure

# Or create manually
mkdir -p roles/nginx/{tasks,handlers,templates,files,vars,defaults,meta}
```

**defaults/main.yml — the role's interface:**

```yaml
---
# defaults/main.yml — these values CAN be overridden by the user
nginx_worker_processes: auto
nginx_worker_connections: 1024
nginx_listen_port: 80
nginx_server_name: "_"
nginx_root: /var/www/html
nginx_log_directory: /var/log/nginx
nginx_enable_ssl: false
nginx_ssl_certificate: ""
nginx_ssl_certificate_key: ""
nginx_extra_server_blocks: []
```

**vars/main.yml — internal role constants:**

```yaml
---
# vars/main.yml — these values SHOULD NOT be overridden
nginx_package_name: nginx
nginx_service_name: nginx
nginx_config_path: /etc/nginx/nginx.conf
nginx_sites_available: /etc/nginx/sites-available
nginx_sites_enabled: /etc/nginx/sites-enabled
```

**tasks/main.yml — the role's work:**

```yaml
---
# tasks/main.yml
- name: Install nginx
  apt:
    name: "{{ nginx_package_name }}"
    state: present
    update_cache: true
  tags: [nginx, packages]

- name: Create log directory
  file:
    path: "{{ nginx_log_directory }}"
    state: directory
    owner: www-data
    group: www-data
    mode: '0755'
  tags: [nginx]

- name: Deploy nginx.conf
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_config_path }}"
    owner: root
    group: root
    mode: '0644'
    validate: nginx -t -c %s
  notify: Restart nginx
  tags: [nginx, configuration]

- name: Deploy default site configuration
  template:
    src: default-site.conf.j2
    dest: "{{ nginx_sites_available }}/default"
    owner: root
    group: root
    mode: '0644'
  notify: Reload nginx
  tags: [nginx, configuration]

- name: Enable default site
  file:
    src: "{{ nginx_sites_available }}/default"
    dest: "{{ nginx_sites_enabled }}/default"
    state: link
  notify: Reload nginx
  tags: [nginx, configuration]

- name: Deploy SSL configuration
  include_tasks: ssl.yml
  when: nginx_enable_ssl
  tags: [nginx, ssl]

- name: Ensure nginx is started and enabled
  service:
    name: "{{ nginx_service_name }}"
    state: started
    enabled: true
  tags: [nginx]
```

**handlers/main.yml:**

```yaml
---
- name: Restart nginx
  service:
    name: "{{ nginx_service_name }}"
    state: restarted

- name: Reload nginx
  service:
    name: "{{ nginx_service_name }}"
    state: reloaded
```

**templates/nginx.conf.j2:**

```
# Managed by Ansible — DO NOT EDIT
# Role: nginx
# Host: {{ inventory_hostname }}

user www-data;
worker_processes {{ nginx_worker_processes }};
pid /run/nginx.pid;

events {
    worker_connections {{ nginx_worker_connections }};
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log {{ nginx_log_directory }}/access.log;
    error_log {{ nginx_log_directory }}/error.log;

    gzip on;

    include {{ nginx_sites_enabled }}/*;
}
```

**meta/main.yml:**

```yaml
---
galaxy_info:
  author: Platform Team
  description: Install and configure Nginx web server
  license: MIT
  min_ansible_version: "2.14"
  platforms:
    - name: Ubuntu
      versions:
        - jammy
        - focal
    - name: Debian
      versions:
        - bookworm
        - bullseye

dependencies:
  - role: common
    vars:
      common_packages:
        - curl
        - ca-certificates
```

### Calling Roles

```yaml
# Method 1: roles section (classic)
- name: Configure web servers
  hosts: webservers
  become: true
  roles:
    - common
    - nginx
    - { role: monitoring, monitoring_port: 9090 }

# Method 2: include_role (dynamic, can be conditional)
- name: Configure servers
  hosts: all
  become: true
  tasks:
    - name: Apply common configuration
      include_role:
        name: common

    - name: Apply nginx role for web servers
      include_role:
        name: nginx
      when: "'webservers' in group_names"

# Method 3: import_role (static, processed at parse time)
- name: Configure servers
  hosts: webservers
  become: true
  tasks:
    - name: Import nginx role
      import_role:
        name: nginx
      vars:
        nginx_listen_port: 8080
```

### Ansible Galaxy

Ansible Galaxy is the community repository for roles and collections.

```bash
# Search for roles
ansible-galaxy search nginx --platforms Ubuntu

# Install a role from Galaxy
ansible-galaxy install geerlingguy.nginx
# Installed to ~/.ansible/roles/geerlingguy.nginx

# Install with a specific version
ansible-galaxy install geerlingguy.nginx,3.1.0

# Install from a requirements file
cat > requirements.yml << 'EOF'
---
roles:
  - name: geerlingguy.nginx
    version: "3.1.0"
  - name: geerlingguy.postgresql
    version: "3.4.0"
  - name: geerlingguy.docker
    version: "6.1.0"

collections:
  - name: community.general
    version: "8.0.0"
  - name: amazon.aws
    version: "7.0.0"
EOF

ansible-galaxy install -r requirements.yml
ansible-galaxy collection install -r requirements.yml

# List installed roles
ansible-galaxy list
```

### Role Dependencies

Roles can declare dependencies in `meta/main.yml`:

```yaml
# roles/webapp/meta/main.yml
dependencies:
  - role: common
  - role: nginx
    vars:
      nginx_listen_port: 80
  - role: postgresql
    vars:
      postgresql_version: 15
    when: database_required | default(true)
```

Dependencies are executed before the dependent role. If the same dependency appears multiple times, it runs only once (unless `allow_duplicates: true` is set).

---

## Step-by-Step Practical

### Building a Reusable Application Configuration Role

```bash
mkdir -p ~/ansible-lab/roles-demo
cd ~/ansible-lab/roles-demo

# Create project structure
mkdir -p roles/app_config/{tasks,handlers,templates,defaults,vars,meta}
```

**roles/app_config/defaults/main.yml:**

```yaml
---
app_name: myapp
app_port: 8080
app_env: development
app_user: app
app_directory: "/tmp/ansible-roles-demo/{{ app_name }}"
app_log_level: info
app_database:
  host: localhost
  port: 5432
  name: "{{ app_name }}_db"
app_features:
  cache_enabled: false
  rate_limiting: false
  debug_mode: true
```

**roles/app_config/vars/main.yml:**

```yaml
---
app_config_file: "{{ app_directory }}/config/application.json"
app_env_file: "{{ app_directory }}/config/.env"
app_systemd_file: "{{ app_directory }}/config/{{ app_name }}.service"
```

**roles/app_config/tasks/main.yml:**

```yaml
---
- name: Create application directories
  file:
    path: "{{ item }}"
    state: directory
    mode: '0755'
  loop:
    - "{{ app_directory }}"
    - "{{ app_directory }}/config"
    - "{{ app_directory }}/logs"
    - "{{ app_directory }}/data"
  tags: [setup]

- name: Generate application configuration
  template:
    src: application.json.j2
    dest: "{{ app_config_file }}"
    mode: '0644'
  notify: Application config changed
  tags: [configure]

- name: Generate environment file
  template:
    src: env.j2
    dest: "{{ app_env_file }}"
    mode: '0600'
  notify: Application config changed
  tags: [configure]

- name: Generate systemd service file
  template:
    src: systemd.service.j2
    dest: "{{ app_systemd_file }}"
    mode: '0644'
  tags: [configure]

- name: Generate deployment manifest
  template:
    src: deploy-manifest.txt.j2
    dest: "{{ app_directory }}/DEPLOY_MANIFEST"
    mode: '0644'
  tags: [deploy]
```

**roles/app_config/templates/application.json.j2:**

```json
{
  "app": {
    "name": "{{ app_name }}",
    "port": {{ app_port }},
    "environment": "{{ app_env }}"
  },
  "logging": {
    "level": "{{ app_log_level }}",
    "directory": "{{ app_directory }}/logs"
  },
  "database": {
    "host": "{{ app_database.host }}",
    "port": {{ app_database.port }},
    "name": "{{ app_database.name }}"
  },
  "features": {
{% for feature, enabled in app_features.items() %}
    "{{ feature }}": {{ enabled | lower }}{{ "," if not loop.last else "" }}
{% endfor %}
  }
}
```

**roles/app_config/templates/env.j2:**

```
# Generated by Ansible — DO NOT EDIT
# Role: app_config
# Date: {{ ansible_date_time.iso8601 }}

APP_NAME={{ app_name }}
APP_PORT={{ app_port }}
APP_ENV={{ app_env }}
LOG_LEVEL={{ app_log_level }}
DB_HOST={{ app_database.host }}
DB_PORT={{ app_database.port }}
DB_NAME={{ app_database.name }}
{% for feature, enabled in app_features.items() %}
FEATURE_{{ feature | upper }}={{ enabled | lower }}
{% endfor %}
```

**roles/app_config/templates/systemd.service.j2:**

```ini
# Generated by Ansible
[Unit]
Description={{ app_name }} service
After=network.target

[Service]
Type=simple
User={{ app_user }}
WorkingDirectory={{ app_directory }}
EnvironmentFile={{ app_env_file }}
ExecStart=/usr/bin/{{ app_name }} --config {{ app_config_file }}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**roles/app_config/templates/deploy-manifest.txt.j2:**

```
Deployment Manifest
===================
Application: {{ app_name }}
Environment: {{ app_env }}
Host:        {{ inventory_hostname }}
Date:        {{ ansible_date_time.iso8601 }}
Ansible:     {{ ansible_version.full }}

Configuration:
  Port:      {{ app_port }}
  Log Level: {{ app_log_level }}
  Database:  {{ app_database.host }}:{{ app_database.port }}/{{ app_database.name }}

Features:
{% for feature, enabled in app_features.items() %}
  {{ feature }}: {{ 'enabled' if enabled else 'disabled' }}
{% endfor %}
```

**roles/app_config/handlers/main.yml:**

```yaml
---
- name: Application config changed
  debug:
    msg: "Configuration changed for {{ app_name }} — would restart service in production"
```

**roles/app_config/meta/main.yml:**

```yaml
---
galaxy_info:
  author: DevOps Team
  description: Configure application settings and generate config files
  license: MIT
  min_ansible_version: "2.14"
dependencies: []
```

**site.yml — the main playbook calling the role:**

```yaml
---
- name: Deploy applications
  hosts: local
  gather_facts: true

  roles:
    # Deploy API service with defaults overridden
    - role: app_config
      vars:
        app_name: payments-api
        app_port: 8080
        app_env: development
        app_log_level: debug
        app_database:
          host: localhost
          port: 5432
          name: payments_dev
        app_features:
          cache_enabled: true
          rate_limiting: false
          debug_mode: true

    # Deploy worker service with different settings
    - role: app_config
      vars:
        app_name: payments-worker
        app_port: 9090
        app_env: development
        app_log_level: info
        app_database:
          host: localhost
          port: 5432
          name: payments_dev
        app_features:
          async_processing: true
          retry_failed: true
```

**inventory.ini:**

```ini
[local]
localhost ansible_connection=local
```

**Run it:**

```bash
ansible-playbook site.yml -i inventory.ini

# Verify
cat /tmp/ansible-roles-demo/payments-api/config/application.json | python3 -m json.tool
cat /tmp/ansible-roles-demo/payments-worker/config/.env
cat /tmp/ansible-roles-demo/payments-api/DEPLOY_MANIFEST
```

---

## Exercises

### Exercise 1: Create a Database Role
Create a role called `db_config` that generates PostgreSQL configuration files (postgresql.conf, pg_hba.conf) from templates. Use defaults for port (5432), max_connections (100), shared_buffers (128MB). Call the role from a playbook with custom values.

### Exercise 2: Role with Dependencies
Create a `webapp` role that depends on your `app_config` role. The webapp role should add additional tasks (generate a Dockerfile, create a docker-compose.yml). Declare the dependency in meta/main.yml.

### Exercise 3: Galaxy Role Exploration
Install `geerlingguy.docker` from Galaxy. Read its defaults/main.yml, tasks/main.yml, and README. Without running it, explain: what variables control its behavior, what handlers it defines, and what platforms it supports.

### Exercise 4: Multi-Role Playbook
Create three roles (base_security, webserver, monitoring) and a playbook that applies all three to a group of servers. The base_security role should set up firewall rules, the webserver role should configure nginx, and the monitoring role should set up a monitoring agent configuration. Use tags so each role can be applied independently.

### Exercise 5: Role Testing
Write a test playbook for your app_config role that applies the role with specific variables and then uses assert tasks to verify the generated files contain the expected content. This is manual testing — we will cover Molecule (automated testing) in a later lesson.

---

## Knowledge Check

### Question 1
What is the difference between `defaults/main.yml` and `vars/main.yml` in a role?

<details>
<summary>Answer</summary>

`defaults/main.yml` contains default variable values with the LOWEST precedence — they are easily overridden by inventory variables, play vars, or command-line vars. They represent the role's "interface" — the knobs users should turn. `vars/main.yml` contains variables with HIGHER precedence — they are internal to the role and difficult to override. They typically contain computed values, internal constants, or platform-specific paths that users should not change. Best practice: put user-configurable values in defaults (ports, feature flags, resource limits) and internal constants in vars (package names, config file paths, service names).
</details>

### Question 2
When would you use `include_role` vs `import_role` vs the `roles:` section?

<details>
<summary>Answer</summary>

The `roles:` section is the classic, simplest method — roles run before any tasks in the play. Use it when you want a clean separation between roles and tasks. `import_role` is static — it is processed at playbook parse time, so tags and conditions are applied to every task in the role. Use it when you want the role's tasks to be fully integrated into the play's task list. `include_role` is dynamic — it is processed at runtime, so it can be used inside loops, with runtime variables, and with conditions that are evaluated during execution. Use it when you need conditional role inclusion based on runtime facts or registered variables. The key tradeoff: `import_role` gives better --list-tags and --list-tasks visibility; `include_role` gives more runtime flexibility.
</details>

### Question 3
How do role dependencies work and what are their limitations?

<details>
<summary>Answer</summary>

Role dependencies are declared in `meta/main.yml` and specify roles that must run before the current role. When Ansible encounters a role with dependencies, it runs the dependency roles first. Limitations: (1) by default, a dependency role runs only once even if declared by multiple roles — set `allow_duplicates: true` in the dependency's meta to override; (2) dependency variables are scoped to the dependency execution, not inherited by the parent role; (3) deeply nested dependencies can be hard to debug and can create unexpected execution orders; (4) circular dependencies cause errors. Best practice: keep dependencies shallow (1 level), use dependencies for genuine prerequisites (not just convenience), and document them clearly.
</details>

### Question 4
What is Ansible Galaxy and how does it fit into a team's workflow?

<details>
<summary>Answer</summary>

Ansible Galaxy is both a public repository of community roles/collections (galaxy.ansible.com) and a command-line tool for managing them. In a team workflow: (1) use `requirements.yml` to declare role and collection dependencies with pinned versions; (2) run `ansible-galaxy install -r requirements.yml` in CI/CD pipelines to install dependencies; (3) use well-maintained community roles (geerlingguy's roles are industry-standard) instead of writing everything from scratch; (4) publish internal roles to a private Galaxy server or Git repository for cross-team sharing; (5) always pin versions to prevent unexpected changes. Galaxy accelerates development but requires vetting — check download counts, last update date, and review the code before using community roles in production.
</details>
