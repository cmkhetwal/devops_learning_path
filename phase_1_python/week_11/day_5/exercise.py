"""
Week 11, Day 5: Exercise - Ansible Playbook & Inventory Generator

Build functions that generate Ansible playbooks and inventory files
as strings. No Ansible installation needed -- we produce text output.

TASKS:
    1. generate_inventory_ini()    - INI-format inventory
    2. generate_inventory_yaml()   - YAML-format inventory string
    3. generate_playbook()         - Basic playbook structure
    4. generate_role_playbook()    - Playbook with role tasks
    5. generate_full_stack()       - Complete playbook for a web stack
    6. generate_deployment_plan()  - Multi-play deployment playbook
"""

# ============================================================
# SAMPLE SERVER DATA
# ============================================================

SERVERS = {
    "webservers": {
        "hosts": [
            {"name": "web1.example.com", "ansible_host": "10.0.1.10",
             "ansible_user": "deploy", "ansible_port": 22},
            {"name": "web2.example.com", "ansible_host": "10.0.1.11",
             "ansible_user": "deploy", "ansible_port": 22},
            {"name": "web3.example.com", "ansible_host": "10.0.1.12",
             "ansible_user": "deploy", "ansible_port": 22},
        ],
        "vars": {"http_port": 80, "max_clients": 200},
    },
    "databases": {
        "hosts": [
            {"name": "db1.example.com", "ansible_host": "10.0.2.10",
             "ansible_user": "dbadmin", "ansible_port": 22},
            {"name": "db2.example.com", "ansible_host": "10.0.2.11",
             "ansible_user": "dbadmin", "ansible_port": 22},
        ],
        "vars": {"db_port": 5432, "max_connections": 100},
    },
    "monitoring": {
        "hosts": [
            {"name": "mon1.example.com", "ansible_host": "10.0.3.10",
             "ansible_user": "admin", "ansible_port": 22},
        ],
        "vars": {"prometheus_port": 9090},
    },
}


# ============================================================
# TASK 1: generate_inventory_ini(server_groups)
#
# Given a dict like SERVERS, generate an INI-format inventory string.
#
# Format:
# [webservers]
# web1.example.com ansible_host=10.0.1.10 ansible_user=deploy ansible_port=22
# web2.example.com ansible_host=10.0.1.11 ansible_user=deploy ansible_port=22
#
# [webservers:vars]
# http_port=80
# max_clients=200
#
# [databases]
# db1.example.com ansible_host=10.0.2.10 ansible_user=dbadmin ansible_port=22
# ...
#
# Rules:
# - Group header: [group_name]
# - Host line: name key=value key=value ...
# - Vars section: [group_name:vars]  (only if vars exist)
# - Groups in alphabetical order
# - Blank line between groups
# ============================================================

def generate_inventory_ini(server_groups):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: generate_inventory_yaml(server_groups)
#
# Given a dict like SERVERS, generate a YAML-format inventory string.
#
# Format:
# all:
#   children:
#     databases:
#       hosts:
#         db1.example.com:
#           ansible_host: 10.0.2.10
#           ansible_user: dbadmin
#           ansible_port: 22
#       vars:
#         db_port: 5432
#         max_connections: 100
#     webservers:
#       hosts:
#         web1.example.com:
#           ansible_host: 10.0.1.10
#           ...
#
# Rules:
# - Top level: all: -> children:
# - Groups sorted alphabetically
# - Hosts in order from list
# - Each host has its vars indented under it
# - Group vars in vars: section
# - 2-space indentation
# ============================================================

def generate_inventory_yaml(server_groups):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: generate_playbook(name, hosts, become, tasks)
#
# Generate a single-play Ansible playbook as a string.
#
# name: play name (string)
# hosts: target host group (string)
# become: whether to use sudo (bool)
# tasks: list of dicts, each with:
#   - "name": task name
#   - "module": ansible module name (e.g., "apt", "service")
#   - "args": dict of module arguments
#
# Output format (YAML string):
# ---
# - name: Configure web servers
#   hosts: webservers
#   become: yes
#   tasks:
#     - name: Install nginx
#       apt:
#         name: nginx
#         state: present
#     - name: Start nginx
#       service:
#         name: nginx
#         state: started
#         enabled: yes
# ============================================================

def generate_playbook(name, hosts, become, tasks):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: generate_role_playbook(role_name, packages, services,
#                                 config_files, handlers)
#
# Generate a complete playbook that mimics a "role" -- installs
# packages, copies configs, manages services, and defines handlers.
#
# role_name: string (e.g., "nginx")
# packages: list of package names to install
# services: list of dicts with "name" and "state" and "enabled"
# config_files: list of dicts with "src", "dest", "notify" (handler name)
# handlers: list of dicts with "name", "module", "args"
#
# Output: YAML-formatted playbook string with tasks AND handlers.
#
# ---
# - name: Configure nginx role
#   hosts: all
#   become: yes
#   tasks:
#     - name: Install packages
#       apt:
#         name:
#           - nginx
#           - python3
#         state: present
#         update_cache: yes
#     - name: Copy nginx.conf
#       copy:
#         src: nginx.conf
#         dest: /etc/nginx/nginx.conf
#       notify: Restart nginx
#     - name: Ensure nginx is started
#       service:
#         name: nginx
#         state: started
#         enabled: yes
#   handlers:
#     - name: Restart nginx
#       service:
#         name: nginx
#         state: restarted
# ============================================================

def generate_role_playbook(role_name, packages, services, config_files, handlers):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: generate_full_stack(app_name, components)
#
# Generate a multi-play playbook for a full application stack.
#
# app_name: string
# components: list of dicts, each with:
#   - "name": component name (e.g., "web", "database", "cache")
#   - "hosts": target group
#   - "packages": list of packages to install
#   - "services": list of service names to start
#   - "env_vars": dict of environment variables
#   - "port": port number
#
# Generate ONE playbook string with MULTIPLE plays (one per component).
# Each play should:
#   1. Install the packages
#   2. Set up environment (write to /etc/environment)
#   3. Start the services
#   4. Verify the port is listening (use wait_for module)
#
# Format:
# ---
# # Full Stack Deployment: my-app
#
# - name: Deploy web component
#   hosts: webservers
#   become: yes
#   tasks:
#     - name: Install packages
#       apt:
#         name:
#           - nginx
#           - python3
#         state: present
#     - name: Set environment variables
#       lineinfile:
#         path: /etc/environment
#         line: "APP_ENV=production"
#       loop:
#         - "APP_ENV=production"
#         - "PORT=8080"
#     - name: Start services
#       service:
#         name: nginx
#         state: started
#         enabled: yes
#       loop:
#         - nginx
#     - name: Verify port 8080 is listening
#       wait_for:
#         port: 8080
#         timeout: 30
# ============================================================

def generate_full_stack(app_name, components):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 6: generate_deployment_plan(app_name, version,
#                                   environments, rollback=True)
#
# Generate a deployment playbook that:
# 1. Backs up current version
# 2. Deploys new version
# 3. Runs health checks
# 4. Optionally includes rollback tasks
#
# environments: list of dicts with "name", "hosts", "verify_url"
# rollback: whether to include rollback block
#
# Return a string playbook with plays for each environment.
# Each environment play should have tasks:
#   1. Backup current version
#   2. Pull new version (using git module)
#   3. Install dependencies
#   4. Restart application
#   5. Health check (using uri module)
#   6. Rollback tasks (if rollback=True, using block/rescue)
#
# Format:
# ---
# # Deployment Plan: my-app v2.0.0
#
# - name: Deploy to staging
#   hosts: staging
#   become: yes
#   vars:
#     app_name: my-app
#     app_version: "2.0.0"
#   tasks:
#     - name: Backup current version
#       command: cp -r /opt/my-app /opt/my-app.backup
#     - name: Pull new version
#       git:
#         repo: "https://github.com/org/my-app.git"
#         dest: /opt/my-app
#         version: "v2.0.0"
#     - name: Install dependencies
#       command: pip install -r /opt/my-app/requirements.txt
#     - name: Restart application
#       service:
#         name: my-app
#         state: restarted
#     - name: Health check
#       uri:
#         url: "https://staging.example.com/health"
#         status_code: 200
#       retries: 5
#       delay: 10
#
# Note: If rollback=True, add an additional task at the end:
#     - name: Rollback on failure
#       command: cp -r /opt/my-app.backup /opt/my-app
#       when: health_check is failed
# ============================================================

def generate_deployment_plan(app_name, version, environments, rollback=True):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Task 1: INI Inventory ===")
    ini = generate_inventory_ini(SERVERS)
    if ini:
        print(ini[:400])

    print("\n=== Task 2: YAML Inventory ===")
    yml = generate_inventory_yaml(SERVERS)
    if yml:
        print(yml[:400])

    print("\n=== Task 3: Simple Playbook ===")
    pb = generate_playbook("Setup Web", "webservers", True, [
        {"name": "Install nginx", "module": "apt",
         "args": {"name": "nginx", "state": "present"}},
        {"name": "Start nginx", "module": "service",
         "args": {"name": "nginx", "state": "started"}},
    ])
    if pb:
        print(pb[:400])

    print("\n=== Task 4: Role Playbook ===")
    role = generate_role_playbook(
        "nginx",
        ["nginx", "python3"],
        [{"name": "nginx", "state": "started", "enabled": True}],
        [{"src": "nginx.conf", "dest": "/etc/nginx/nginx.conf", "notify": "Restart nginx"}],
        [{"name": "Restart nginx", "module": "service", "args": {"name": "nginx", "state": "restarted"}}],
    )
    if role:
        print(role[:500])

    print("\n=== Task 5: Full Stack ===")
    stack = generate_full_stack("my-app", [
        {"name": "web", "hosts": "webservers", "packages": ["nginx"],
         "services": ["nginx"], "env_vars": {"APP_ENV": "prod"}, "port": 80},
        {"name": "database", "hosts": "databases", "packages": ["postgresql"],
         "services": ["postgresql"], "env_vars": {"DB_PORT": "5432"}, "port": 5432},
    ])
    if stack:
        print(stack[:500])

    print("\n=== Task 6: Deployment Plan ===")
    plan = generate_deployment_plan("my-app", "2.0.0", [
        {"name": "staging", "hosts": "staging", "verify_url": "https://staging.example.com/health"},
        {"name": "production", "hosts": "production", "verify_url": "https://example.com/health"},
    ])
    if plan:
        print(plan[:500])
