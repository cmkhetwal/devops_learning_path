# Week 11, Day 5: Ansible Basics with Python

## What You'll Learn

- Ansible concepts: playbooks, tasks, inventory, roles
- Ansible playbook and inventory file structure (YAML/INI)
- Generating Ansible playbooks and inventories using Python
- How Python and Ansible work together

## Why This Matters for DevOps

Ansible is one of the most popular configuration management and automation
tools. It uses YAML playbooks to define desired system state and Python
under the hood for its modules. Generating playbooks programmatically
enables dynamic infrastructure automation at scale.

---

## 1. What is Ansible?

Ansible automates:
- **Configuration management**: Install packages, edit files, manage services
- **Application deployment**: Deploy code to servers
- **Orchestration**: Coordinate multi-server workflows
- **Provisioning**: Set up new servers

Key features:
- **Agentless**: Uses SSH, no agent needed on managed nodes
- **Idempotent**: Running the same playbook twice produces the same result
- **YAML-based**: Human-readable configuration

## 2. Inventory Files

Inventory defines the hosts Ansible manages:

### INI Format
```ini
[webservers]
web1.example.com ansible_host=10.0.1.10 ansible_user=deploy
web2.example.com ansible_host=10.0.1.11 ansible_user=deploy

[databases]
db1.example.com ansible_host=10.0.2.10 ansible_user=admin
db2.example.com ansible_host=10.0.2.11 ansible_user=admin

[webservers:vars]
http_port=80
max_clients=200

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

### YAML Format
```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 10.0.1.10
          ansible_user: deploy
        web2.example.com:
          ansible_host: 10.0.1.11
          ansible_user: deploy
      vars:
        http_port: 80
    databases:
      hosts:
        db1.example.com:
          ansible_host: 10.0.2.10
```

## 3. Playbook Structure

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars:
    http_port: 80
    app_version: "2.1.0"

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Copy configuration
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

## 4. Common Ansible Modules

| Module | Purpose | Example |
|--------|---------|---------|
| `apt/yum` | Install packages | `apt: name=nginx state=present` |
| `service` | Manage services | `service: name=nginx state=started` |
| `copy` | Copy files | `copy: src=app.conf dest=/etc/` |
| `template` | Render templates | `template: src=nginx.j2 dest=/etc/nginx/nginx.conf` |
| `file` | Manage files/dirs | `file: path=/app state=directory` |
| `command` | Run commands | `command: /usr/bin/make install` |
| `docker_container` | Manage Docker | `docker_container: name=web image=app:latest` |
| `git` | Clone repos | `git: repo=url dest=/app` |

## 5. Generating Playbooks with Python

```python
def generate_playbook(name, hosts, tasks):
    """Generate an Ansible playbook as a Python dict."""
    playbook = [{
        "name": name,
        "hosts": hosts,
        "become": True,
        "tasks": tasks,
    }]
    return playbook

# Example usage
tasks = [
    {
        "name": "Install packages",
        "apt": {"name": ["nginx", "python3"], "state": "present"},
    },
    {
        "name": "Start nginx",
        "service": {"name": "nginx", "state": "started", "enabled": True},
    },
]

playbook = generate_playbook("Setup Web Server", "webservers", tasks)
```

## 6. Generating Inventory with Python

```python
def generate_inventory(groups):
    """Generate INI-format inventory."""
    lines = []
    for group_name, group_data in groups.items():
        lines.append(f"[{group_name}]")
        for host in group_data["hosts"]:
            parts = [host["name"]]
            if "ansible_host" in host:
                parts.append(f"ansible_host={host['ansible_host']}")
            if "ansible_user" in host:
                parts.append(f"ansible_user={host['ansible_user']}")
            lines.append(" ".join(parts))
        lines.append("")

        if "vars" in group_data:
            lines.append(f"[{group_name}:vars]")
            for key, value in group_data["vars"].items():
                lines.append(f"{key}={value}")
            lines.append("")

    return "\n".join(lines)
```

## 7. Ansible Roles Structure

```
roles/
  webserver/
    tasks/
      main.yml
    handlers/
      main.yml
    templates/
      nginx.conf.j2
    vars/
      main.yml
    defaults/
      main.yml
```

## 8. Python + Ansible Integration

```python
import subprocess

def run_playbook(playbook_path, inventory_path, extra_vars=None):
    """Run an Ansible playbook using subprocess."""
    cmd = [
        "ansible-playbook",
        playbook_path,
        "-i", inventory_path,
    ]
    if extra_vars:
        for key, value in extra_vars.items():
            cmd.extend(["-e", f"{key}={value}"])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout
```

## DevOps Connection

Ansible + Python is used for:
- **Dynamic inventory**: Python scripts that query AWS/GCP for current servers
- **Custom modules**: Write Ansible modules in Python
- **Playbook generation**: Create playbooks for new services automatically
- **CI/CD integration**: Run Ansible from Jenkins/GitHub Actions
- **Compliance**: Generate playbooks that enforce security standards

---

## Key Takeaways

| Concept | Description |
|---------|-------------|
| Inventory | Defines managed hosts and groups |
| Playbook | YAML file defining automation tasks |
| Task | Single action (install, copy, restart) |
| Module | Built-in operation (apt, service, file) |
| Handler | Task triggered by notification |
| Role | Reusable collection of tasks |
| Idempotent | Safe to run multiple times |
