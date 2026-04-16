# Ansible Playbooks

## Why This Matters in DevOps

Ad-hoc commands are useful for one-off tasks — checking disk space, restarting a service. But real configuration management requires coordinated, multi-step automation: install packages, deploy configurations, start services, and verify health — all in the right order, with error handling, and across hundreds of servers.

Playbooks are Ansible's automation language. They are YAML files that define a series of tasks to execute on specified hosts. Every Ansible automation in production — from configuring web servers to deploying applications to rotating secrets — is a playbook. Mastering playbooks is mastering Ansible itself.

---

## Core Concepts

### Playbook Structure

A playbook contains one or more plays. Each play targets a group of hosts and defines tasks to execute.

```yaml
# site.yml — a playbook with two plays
---
- name: Configure web servers
  hosts: webservers
  become: true

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: true

    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: true

- name: Configure database servers
  hosts: databases
  become: true

  tasks:
    - name: Install PostgreSQL
      apt:
        name: postgresql
        state: present

    - name: Start PostgreSQL
      service:
        name: postgresql
        state: started
        enabled: true
```

**Key elements:**
- `---` — YAML document start
- `name` — Human-readable description (always use descriptive names)
- `hosts` — Which inventory group(s) to target
- `become` — Whether to use privilege escalation (sudo)
- `tasks` — Ordered list of tasks to execute

### Plays and Tasks

A play maps a group of hosts to a list of tasks. Tasks call modules with specific parameters.

```yaml
- name: Deploy web application
  hosts: webservers
  become: true
  gather_facts: true              # Collect system facts (default: true)
  serial: 2                       # Deploy 2 servers at a time (rolling)

  vars:
    app_version: "2.3.1"
    app_user: deploy
    app_directory: /opt/myapp

  tasks:
    - name: Create application user
      user:
        name: "{{ app_user }}"
        shell: /bin/bash
        system: true

    - name: Create application directory
      file:
        path: "{{ app_directory }}"
        state: directory
        owner: "{{ app_user }}"
        mode: '0755'

    - name: Download application
      get_url:
        url: "https://releases.example.com/app-{{ app_version }}.tar.gz"
        dest: "/tmp/app-{{ app_version }}.tar.gz"
        checksum: "sha256:abc123..."

    - name: Extract application
      unarchive:
        src: "/tmp/app-{{ app_version }}.tar.gz"
        dest: "{{ app_directory }}"
        remote_src: true
        owner: "{{ app_user }}"
```

### Handlers (notify/handler)

Handlers are tasks that only run when notified by another task. They run once at the end of the play, regardless of how many tasks notify them. The classic use case: restart a service only if its configuration changed.

```yaml
- name: Configure nginx
  hosts: webservers
  become: true

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Deploy nginx configuration
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        mode: '0644'
      notify: Restart nginx              # Notify the handler

    - name: Deploy site configuration
      template:
        src: templates/site.conf.j2
        dest: /etc/nginx/sites-available/mysite.conf
        mode: '0644'
      notify: Restart nginx              # Same handler, runs only once

    - name: Enable site
      file:
        src: /etc/nginx/sites-available/mysite.conf
        dest: /etc/nginx/sites-enabled/mysite.conf
        state: link
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted

    - name: Reload nginx
      service:
        name: nginx
        state: reloaded
```

Important behavior:
- Handlers run only if notified (if the notifying task reports "changed")
- Handlers run once at the end of the play, not immediately
- If multiple tasks notify the same handler, it still runs only once
- Handlers run in the order they are defined in the handlers section
- Use `meta: flush_handlers` to run handlers immediately if needed

### Variables

Ansible provides many ways to define variables. Understanding the precedence order is critical.

```yaml
# Method 1: vars in the play
- name: Deploy app
  hosts: webservers
  vars:
    app_port: 8080
    app_env: production

# Method 2: vars_files (external YAML files)
- name: Deploy app
  hosts: webservers
  vars_files:
    - vars/common.yml
    - vars/{{ environment }}.yml

# Method 3: host_vars (per-host variables)
# host_vars/web1.example.com.yml
app_port: 8080
ssl_cert: /etc/ssl/web1.crt

# Method 4: group_vars (per-group variables)
# group_vars/webservers.yml
http_port: 80
max_connections: 1000
nginx_worker_processes: auto

# group_vars/all.yml (applies to all hosts)
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org
monitoring_enabled: true

# Method 5: Registered variables (capture task output)
- name: Check disk space
  command: df -h /
  register: disk_output

- name: Show disk space
  debug:
    var: disk_output.stdout_lines

# Method 6: Facts (automatically gathered)
- name: Show OS info
  debug:
    msg: "Running {{ ansible_distribution }} {{ ansible_distribution_version }}"
```

**Variable precedence (lowest to highest):**

```
1.  role defaults (defaults/main.yml)
2.  inventory file or script group vars
3.  inventory group_vars/all
4.  inventory group_vars/*
5.  inventory host_vars/*
6.  playbook group_vars/all
7.  playbook group_vars/*
8.  playbook host_vars/*
9.  host facts / registered vars
10. play vars
11. play vars_prompt
12. play vars_files
13. role vars (vars/main.yml)
14. block vars
15. task vars
16. include_vars
17. set_facts / registered vars
18. role params
19. include params
20. extra vars (-e) ← ALWAYS WIN
```

The practical rule: `-e` (extra vars on command line) always wins. Role defaults are the easiest to override.

### Conditionals (when)

```yaml
tasks:
  # Simple condition
  - name: Install Apache on Debian
    apt:
      name: apache2
      state: present
    when: ansible_os_family == "Debian"

  - name: Install Apache on RedHat
    dnf:
      name: httpd
      state: present
    when: ansible_os_family == "RedHat"

  # Multiple conditions (AND)
  - name: Install monitoring agent
    apt:
      name: datadog-agent
      state: present
    when:
      - ansible_os_family == "Debian"
      - monitoring_enabled | default(false)

  # OR condition
  - name: Restart nginx
    service:
      name: nginx
      state: restarted
    when: nginx_config_changed or ssl_cert_changed

  # Check variable is defined
  - name: Configure custom DNS
    template:
      src: resolv.conf.j2
      dest: /etc/resolv.conf
    when: custom_dns_servers is defined

  # Check registered variable
  - name: Check if app is running
    command: pgrep -f myapp
    register: app_status
    ignore_errors: true

  - name: Start app if not running
    command: /opt/myapp/start.sh
    when: app_status.rc != 0
```

### Loops

```yaml
tasks:
  # Simple loop
  - name: Install packages
    apt:
      name: "{{ item }}"
      state: present
    loop:
      - nginx
      - git
      - curl
      - vim
      - htop

  # Better — pass a list to the module directly (more efficient)
  - name: Install packages
    apt:
      name:
        - nginx
        - git
        - curl
        - vim
        - htop
      state: present

  # Loop over a dictionary
  - name: Create users
    user:
      name: "{{ item.name }}"
      groups: "{{ item.groups }}"
      shell: "{{ item.shell }}"
    loop:
      - { name: 'alice', groups: 'developers', shell: '/bin/bash' }
      - { name: 'bob',   groups: 'operators',  shell: '/bin/bash' }
      - { name: 'ci',    groups: 'deploy',     shell: '/bin/false' }

  # Loop with index
  - name: Create numbered config files
    copy:
      content: "server_id={{ ansible_loop.index }}"
      dest: "/etc/myapp/node-{{ ansible_loop.index }}.conf"
    loop: "{{ groups['webservers'] }}"
    loop_control:
      extended: true

  # Nested loops with subelements
  - name: Add SSH keys for users
    authorized_key:
      user: "{{ item.0.name }}"
      key: "{{ item.1 }}"
    with_subelements:
      - "{{ users }}"
      - ssh_keys
```

### Tags

Tags let you run specific parts of a playbook:

```yaml
tasks:
  - name: Install packages
    apt:
      name: nginx
      state: present
    tags:
      - packages
      - setup

  - name: Deploy configuration
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    tags:
      - configuration

  - name: Deploy application
    copy:
      src: app/
      dest: /opt/app/
    tags:
      - deploy
```

```bash
# Run only tasks tagged "configuration"
ansible-playbook site.yml --tags configuration

# Run everything EXCEPT "deploy"
ansible-playbook site.yml --skip-tags deploy

# List available tags
ansible-playbook site.yml --list-tags
```

---

## Step-by-Step Practical

### Building a Web Server Playbook

```bash
mkdir -p ~/ansible-lab/webserver/{templates,files,vars}
cd ~/ansible-lab/webserver
```

**inventory.ini:**

```ini
[local]
localhost ansible_connection=local
```

**vars/main.yml:**

```yaml
---
app_name: mywebapp
app_port: 8080
app_user: www-data
server_name: localhost
worker_processes: auto
worker_connections: 1024
log_directory: /tmp/ansible-demo/logs
config_directory: /tmp/ansible-demo/config
app_directory: /tmp/ansible-demo/app
```

**templates/nginx.conf.j2:**

```
# Managed by Ansible — DO NOT EDIT MANUALLY
# Generated for {{ server_name }}

worker_processes {{ worker_processes }};

events {
    worker_connections {{ worker_connections }};
}

http {
    server {
        listen {{ app_port }};
        server_name {{ server_name }};

        access_log {{ log_directory }}/access.log;
        error_log {{ log_directory }}/error.log;

        location / {
            root {{ app_directory }};
            index index.html;
        }
    }
}
```

**templates/index.html.j2:**

```html
<!DOCTYPE html>
<html>
<head><title>{{ app_name }}</title></head>
<body>
    <h1>{{ app_name }}</h1>
    <p>Deployed by Ansible</p>
    <p>Server: {{ ansible_hostname }}</p>
    <p>OS: {{ ansible_distribution }} {{ ansible_distribution_version }}</p>
    <p>Port: {{ app_port }}</p>
</body>
</html>
```

**site.yml:**

```yaml
---
- name: Configure web server
  hosts: local
  gather_facts: true
  vars_files:
    - vars/main.yml

  tasks:
    - name: Create directories
      file:
        path: "{{ item }}"
        state: directory
        mode: '0755'
      loop:
        - "{{ log_directory }}"
        - "{{ config_directory }}"
        - "{{ app_directory }}"
      tags: [setup]

    - name: Deploy nginx configuration
      template:
        src: templates/nginx.conf.j2
        dest: "{{ config_directory }}/nginx.conf"
        mode: '0644'
      notify: Configuration changed
      tags: [configuration]

    - name: Deploy application
      template:
        src: templates/index.html.j2
        dest: "{{ app_directory }}/index.html"
        mode: '0644'
      tags: [deploy]

    - name: Create deployment info
      copy:
        content: |
          Deployment Info
          ===============
          App: {{ app_name }}
          Port: {{ app_port }}
          Server: {{ ansible_hostname }}
          Date: {{ ansible_date_time.iso8601 }}
          Ansible Version: {{ ansible_version.full }}
        dest: "{{ app_directory }}/deploy-info.txt"
        mode: '0644'
      tags: [deploy]

    - name: Verify deployment
      command: cat {{ app_directory }}/deploy-info.txt
      register: deploy_info
      changed_when: false
      tags: [verify]

    - name: Show deployment info
      debug:
        var: deploy_info.stdout_lines
      tags: [verify]

  handlers:
    - name: Configuration changed
      debug:
        msg: "Configuration was updated — in production, this would restart nginx"
```

**Run the playbook:**

```bash
# Full run
ansible-playbook site.yml

# Expected output:
# PLAY [Configure web server] *****************************
#
# TASK [Gathering Facts] **********************************
# ok: [localhost]
#
# TASK [Create directories] *******************************
# changed: [localhost] => (item=/tmp/ansible-demo/logs)
# changed: [localhost] => (item=/tmp/ansible-demo/config)
# changed: [localhost] => (item=/tmp/ansible-demo/app)
#
# TASK [Deploy nginx configuration] ***********************
# changed: [localhost]
#
# TASK [Deploy application] *******************************
# changed: [localhost]
#
# ... (more tasks)
#
# RUNNING HANDLER [Configuration changed] *****************
# ok: [localhost]
#
# PLAY RECAP **********************************************
# localhost: ok=7  changed=5  unreachable=0  failed=0

# Run again (idempotent)
ansible-playbook site.yml
# All tasks should show "ok" instead of "changed"

# Run only specific tags
ansible-playbook site.yml --tags deploy

# Dry run (check mode)
ansible-playbook site.yml --check --diff

# Verify files were created
cat /tmp/ansible-demo/config/nginx.conf
cat /tmp/ansible-demo/app/index.html
cat /tmp/ansible-demo/app/deploy-info.txt
```

---

## Exercises

### Exercise 1: Multi-Service Playbook
Write a playbook that creates local configuration files for three services: nginx, redis, and PostgreSQL. Each service should have its own configuration file generated from variables. Use handlers to print a message when each configuration changes.

### Exercise 2: Conditional Package Installation
Write a playbook that installs different packages based on the OS family. Use `ansible_os_family` to conditionally install packages for Debian vs RedHat systems. Test on localhost using a `when` clause.

### Exercise 3: Loop Mastery
Write a playbook that creates 5 user configuration files from a list variable. Each user has a name, role, and email. Use loops to create a config file for each user with their details. Then use a second loop to create a summary file listing all users.

### Exercise 4: Tag-Based Execution
Write a playbook with 10 tasks divided into 4 tags: setup, configure, deploy, verify. Run the playbook with each tag individually and verify only the correct tasks execute. Use `--list-tags` to confirm.

### Exercise 5: Handler Chaining
Write a playbook where updating a configuration file notifies a handler to "reload service," and that handler notifies another handler to "verify health." Demonstrate that handlers run in order and only when notified.

---

## Knowledge Check

### Question 1
What is the difference between a play and a task in Ansible?

<details>
<summary>Answer</summary>

A play is a top-level element in a playbook that maps a group of hosts to a set of tasks. It defines which hosts to target (`hosts`), whether to use privilege escalation (`become`), variables (`vars`), and other play-level settings. A task is a single action within a play — it calls one module with specific parameters to achieve a specific state (e.g., "install nginx," "start a service," "copy a file"). A play contains multiple tasks that run sequentially on the specified hosts. A playbook can contain multiple plays, each targeting different host groups.
</details>

### Question 2
How do handlers differ from regular tasks?

<details>
<summary>Answer</summary>

Handlers differ from regular tasks in three key ways: (1) they only run when notified by a task that reported "changed" — if no task notifies them, they do not run at all; (2) they run at the end of the play, not at the point of notification — this prevents unnecessary multiple restarts; (3) no matter how many tasks notify the same handler, it runs only once. This makes handlers ideal for service restarts: if three tasks modify nginx configuration files, you want nginx restarted once after all changes are made, not three times. Regular tasks always run (unless skipped by a condition) and run at their defined position in the task list.
</details>

### Question 3
Why should you always use descriptive names for plays and tasks?

<details>
<summary>Answer</summary>

Descriptive names serve multiple purposes: (1) the output of `ansible-playbook` displays task names, making it easy to follow execution and identify where failures occur; (2) names serve as documentation — anyone reading the playbook understands what each task does without reading the module parameters; (3) when a task fails, the name tells you immediately what was being attempted; (4) names appear in logs, making troubleshooting easier; (5) the `--start-at-task` flag uses task names to resume execution from a specific point. A task named "Install nginx" is immediately clear; a task with no name shows only the module name and parameters, which is much harder to parse quickly.
</details>

### Question 4
What does `--check --diff` do and when should you use it?

<details>
<summary>Answer</summary>

`--check` runs the playbook in "dry run" mode — it simulates changes without actually making them. Each task reports what it would do (create, modify, delete) without doing it. `--diff` shows the specific changes that would be made to files (like a unified diff). Together, `--check --diff` lets you preview exactly what a playbook run would change before committing to it. Use it: (1) before running playbooks on production servers for the first time, (2) when reviewing someone else's playbook changes, (3) as a compliance check — run periodically to detect drift (non-zero changes means drift). Note: not all modules support check mode (shell/command do not), and some tasks may fail in check mode if they depend on previous tasks that were only simulated.
</details>

### Question 5
What is the practical significance of Ansible's variable precedence order?

<details>
<summary>Answer</summary>

Understanding variable precedence prevents unexpected behavior. The most common practical implications are: (1) `extra vars` (-e on the command line) always win, making them useful for overriding any variable in CI/CD pipelines; (2) `role defaults` are the easiest to override, so module authors should put default values there (users can override with group_vars, host_vars, or play vars); (3) `host_vars` override `group_vars`, allowing you to set a group default but customize specific hosts; (4) `play vars` override inventory vars, allowing the playbook to have the final say; (5) `set_fact` and `register` override almost everything because they set runtime values. The general principle: more specific scopes override more general ones, and runtime values override static definitions.
</details>
