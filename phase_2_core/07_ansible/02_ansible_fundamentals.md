# Ansible Fundamentals

## Why This Matters in DevOps

Ansible is the tool you reach for when you need to configure servers at scale. Whether it is installing packages on 50 machines, deploying application code across a fleet, or rotating credentials on every server in your infrastructure, Ansible lets you do it from a single command on your laptop.

The fundamentals — inventory, ad-hoc commands, modules, and the ansible.cfg configuration — are the building blocks for everything else. You cannot write effective playbooks without understanding how Ansible finds its targets, connects to them, and executes tasks. This lesson gives you hands-on experience with the mechanics before you start building complex automation.

---

## Core Concepts

### Installing Ansible

Ansible runs on the control machine only. Nothing is installed on managed hosts.

```bash
# Using pip (recommended — gives you the latest version)
python3 -m pip install --user ansible

# Using system package manager (Ubuntu/Debian)
sudo apt update
sudo apt install ansible

# Using pipx (isolated environment)
pipx install ansible

# Verify installation
ansible --version
# ansible [core 2.17.x]
#   config file = None
#   configured module search path = ['/home/user/.ansible/plugins/modules']
#   ansible python module location = /home/user/.local/lib/python3.11/site-packages/ansible
#   python version = 3.11.x
```

### Inventory File

The inventory tells Ansible which servers to manage. It can be INI format, YAML format, or a dynamic script.

**INI format (simple, traditional):**

```ini
# inventory.ini

# Ungrouped hosts
bastion.example.com

# Grouped hosts
[webservers]
web1.example.com
web2.example.com
web3.example.com

[databases]
db1.example.com ansible_port=5432
db2.example.com

[loadbalancers]
lb1.example.com

# Group of groups
[production:children]
webservers
databases
loadbalancers

# Variables for a group
[webservers:vars]
http_port=80
max_clients=200
ansible_user=deploy

# Variables for a single host
[databases:vars]
ansible_user=dbadmin
ansible_python_interpreter=/usr/bin/python3
```

**YAML format (more structured, preferred for complex inventories):**

```yaml
# inventory.yml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          http_port: 80
        web2.example.com:
          http_port: 8080
        web3.example.com:
      vars:
        ansible_user: deploy
        max_clients: 200

    databases:
      hosts:
        db1.example.com:
          ansible_port: 5432
        db2.example.com:
      vars:
        ansible_user: dbadmin

    loadbalancers:
      hosts:
        lb1.example.com:

    production:
      children:
        webservers:
        databases:
        loadbalancers:
```

**Local testing inventory (using localhost):**

```ini
# inventory-local.ini
[local]
localhost ansible_connection=local

# Or using IP addresses with SSH
[dev]
192.168.1.10
192.168.1.11
192.168.1.12
```

### Ansible Ad-Hoc Commands

Ad-hoc commands are one-off Ansible commands for quick tasks. They use the `ansible` command (not `ansible-playbook`).

```bash
# Syntax: ansible <pattern> -m <module> -a "<arguments>" -i <inventory>

# Ping all hosts (verify connectivity)
ansible all -m ping -i inventory.ini
# web1.example.com | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }

# Run a command on all web servers
ansible webservers -m command -a "uptime" -i inventory.ini

# Run a shell command (supports pipes and redirects)
ansible webservers -m shell -a "df -h | head -5" -i inventory.ini

# Copy a file to all servers
ansible all -m copy -a "src=./config.txt dest=/tmp/config.txt mode=0644" -i inventory.ini

# Install a package
ansible webservers -m apt -a "name=nginx state=present" -i inventory.ini --become
# --become runs with sudo (equivalent to -b)

# Manage a service
ansible webservers -m service -a "name=nginx state=started enabled=yes" -i inventory.ini --become

# Create a directory
ansible all -m file -a "path=/opt/myapp state=directory mode=0755 owner=deploy" -i inventory.ini --become

# Gather facts about servers
ansible web1.example.com -m setup -i inventory.ini
# Returns detailed system information: OS, IP, memory, CPU, etc.

# Gather specific facts
ansible web1.example.com -m setup -a "filter=ansible_os_family" -i inventory.ini
```

### Essential Modules

Ansible has thousands of modules. These are the ones you will use most:

**Package management:**

```bash
# apt (Debian/Ubuntu)
ansible servers -m apt -a "name=nginx state=present update_cache=yes" --become

# yum/dnf (RedHat/CentOS/Fedora)
ansible servers -m dnf -a "name=httpd state=present" --become

# pip (Python)
ansible servers -m pip -a "name=flask version=2.3.0" --become

# package (auto-detects package manager)
ansible servers -m package -a "name=git state=present" --become
```

**File management:**

```bash
# copy — copy file from control to managed
ansible servers -m copy -a "src=./app.conf dest=/etc/app/app.conf mode=0644 owner=root group=root" --become

# file — manage file/directory properties
ansible servers -m file -a "path=/var/log/myapp state=directory mode=0755" --become

# file — create a symlink
ansible servers -m file -a "src=/opt/app/current dest=/opt/app/latest state=link" --become

# lineinfile — ensure a line exists in a file
ansible servers -m lineinfile -a "path=/etc/hosts line='10.0.1.50 db.internal' state=present" --become
```

**Service management:**

```bash
# Start and enable a service
ansible servers -m service -a "name=nginx state=started enabled=yes" --become

# Restart a service
ansible servers -m service -a "name=nginx state=restarted" --become

# systemd (more options)
ansible servers -m systemd -a "name=nginx state=started enabled=yes daemon_reload=yes" --become
```

**User management:**

```bash
# Create a user
ansible servers -m user -a "name=deploy shell=/bin/bash groups=sudo append=yes" --become

# Add SSH key for a user
ansible servers -m authorized_key -a "user=deploy key='ssh-rsa AAAA... user@host'" --become
```

### ansible.cfg

The Ansible configuration file controls default behavior. Ansible looks for it in this order:

```
1. ANSIBLE_CONFIG environment variable
2. ./ansible.cfg (current directory)
3. ~/.ansible.cfg (home directory)
4. /etc/ansible/ansible.cfg (system default)
```

**Common ansible.cfg:**

```ini
# ansible.cfg
[defaults]
inventory = ./inventory.ini
remote_user = deploy
private_key_file = ~/.ssh/id_ed25519
host_key_checking = False              # Disable for dynamic environments
timeout = 30
forks = 20                             # Parallel connections (default: 5)
retry_files_enabled = False
stdout_callback = yaml                 # More readable output
interpreter_python = auto_silent

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True                      # Speeds up execution significantly
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o StrictHostKeyChecking=no
```

### SSH Key Setup

```bash
# Generate an SSH key pair (if you do not have one)
ssh-keygen -t ed25519 -C "ansible@control-machine"

# Copy public key to managed servers
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@web1.example.com
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@web2.example.com

# Test SSH access
ssh deploy@web1.example.com "hostname"

# Test Ansible connectivity
ansible all -m ping -i inventory.ini
```

### Understanding the Ansible Execution Model

When you run an Ansible command, here is what happens:

```
1. Ansible reads the inventory → determines target hosts
2. Ansible reads the task → determines which module to run
3. For each host (in parallel, up to 'forks' count):
   a. Ansible generates a Python script on the control machine
   b. Ansible connects to the remote host via SSH
   c. Ansible copies the Python script to a temp directory on the remote host
   d. Ansible executes the Python script on the remote host
   e. The script runs, makes changes, and returns JSON results
   f. Ansible deletes the temp script
   g. Ansible receives the JSON results and displays them
4. Ansible aggregates results and shows summary

With pipelining=True (recommended):
  Steps c and f are eliminated — the script is piped directly
  through the SSH connection, significantly faster.
```

---

## Step-by-Step Practical

### Setting Up a Local Lab Environment

You can practice Ansible without remote servers by using `localhost`:

```bash
# Create project directory
mkdir -p ~/ansible-lab/fundamentals
cd ~/ansible-lab/fundamentals

# Create a local inventory
cat > inventory.ini << 'EOF'
[local]
localhost ansible_connection=local
EOF

# Create ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
inventory = ./inventory.ini
stdout_callback = yaml
retry_files_enabled = False
EOF

# Test connectivity
ansible local -m ping
```

Expected output:

```yaml
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Running Ad-Hoc Commands

```bash
# Gather facts about your machine
ansible local -m setup -a "filter=ansible_distribution*"
# Shows your OS distribution name and version

# Create a directory
ansible local -m file -a "path=/tmp/ansible-demo state=directory mode=0755"

# Create a file with content
ansible local -m copy -a "content='Hello from Ansible\n' dest=/tmp/ansible-demo/hello.txt mode=0644"

# Verify
cat /tmp/ansible-demo/hello.txt
# Hello from Ansible

# Run it again (idempotent — no changes)
ansible local -m copy -a "content='Hello from Ansible\n' dest=/tmp/ansible-demo/hello.txt mode=0644"
# localhost | SUCCESS => {
#     "changed": false    ← nothing changed!
# }

# Manage a line in a file
ansible local -m lineinfile -a "path=/tmp/ansible-demo/hello.txt line='Added by Ansible' state=present"
cat /tmp/ansible-demo/hello.txt
# Hello from Ansible
# Added by Ansible

# Run again (idempotent)
ansible local -m lineinfile -a "path=/tmp/ansible-demo/hello.txt line='Added by Ansible' state=present"
# "changed": false

# Collect system info
ansible local -m setup -a "filter=ansible_memtotal_mb"
ansible local -m setup -a "filter=ansible_processor_vcpus"
ansible local -m setup -a "filter=ansible_default_ipv4"
```

### Using Docker Containers as Practice Targets

For a more realistic multi-host experience:

```bash
# Create a docker-compose.yml for practice hosts
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  web1:
    image: python:3.11-slim
    container_name: ansible-web1
    command: >
      bash -c "apt-get update && apt-get install -y openssh-server sudo &&
      mkdir /run/sshd &&
      echo 'root:ansible' | chpasswd &&
      sed -i 's/#PermitRootLogin/PermitRootLogin/' /etc/ssh/sshd_config &&
      /usr/sbin/sshd -D"
    ports:
      - "2221:22"

  web2:
    image: python:3.11-slim
    container_name: ansible-web2
    command: >
      bash -c "apt-get update && apt-get install -y openssh-server sudo &&
      mkdir /run/sshd &&
      echo 'root:ansible' | chpasswd &&
      sed -i 's/#PermitRootLogin/PermitRootLogin/' /etc/ssh/sshd_config &&
      /usr/sbin/sshd -D"
    ports:
      - "2222:22"
EOF

# Start containers
docker-compose up -d

# Create inventory for containers
cat > inventory-docker.ini << 'EOF'
[webservers]
web1 ansible_host=127.0.0.1 ansible_port=2221 ansible_user=root ansible_password=ansible
web2 ansible_host=127.0.0.1 ansible_port=2222 ansible_user=root ansible_password=ansible

[webservers:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF

# Test connectivity
ansible webservers -m ping -i inventory-docker.ini

# Run commands on both servers simultaneously
ansible webservers -m command -a "hostname" -i inventory-docker.ini

# Install a package on both servers
ansible webservers -m apt -a "name=curl state=present" -i inventory-docker.ini
```

### Understanding Ansible Output

```
TASK [Install nginx] *****************************************************
changed: [web1.example.com]     ← Package was installed (changed)
ok: [web2.example.com]          ← Package already installed (no change)
failed: [web3.example.com]      ← Something went wrong

PLAY RECAP ****************************************************************
web1.example.com    : ok=3  changed=1  unreachable=0  failed=0  skipped=0
web2.example.com    : ok=3  changed=0  unreachable=0  failed=0  skipped=0
web3.example.com    : ok=1  changed=0  unreachable=0  failed=1  skipped=0
```

Status meanings:
- **ok**: Task ran, no changes needed (already in desired state)
- **changed**: Task ran and made changes (brought to desired state)
- **unreachable**: Cannot connect to the host (SSH failure)
- **failed**: Task ran but encountered an error
- **skipped**: Task was skipped due to a condition (when: clause)
- **rescued**: Task failed but was rescued by a rescue block

---

## Exercises

### Exercise 1: Inventory Practice
Create an inventory file with 3 groups: webservers (3 hosts), databases (2 hosts), and monitoring (1 host). Add a parent group called "production" that includes all three groups. Set group-level variables for ansible_user and a custom variable called env=prod. Write the inventory in both INI and YAML formats.

### Exercise 2: Ad-Hoc Command Series
Using localhost, perform these tasks with ad-hoc commands: (a) create a directory /tmp/ansible-exercise, (b) create a file in it with your name, (c) set the file permissions to 0600, (d) add a line "ansible_managed = true" to the file, (e) verify by reading the file with the command module. Run each command twice to verify idempotency.

### Exercise 3: Module Exploration
Use `ansible-doc` to explore 5 modules: `ansible-doc apt`, `ansible-doc copy`, `ansible-doc file`, `ansible-doc service`, `ansible-doc user`. For each, identify: required parameters, optional parameters, and an example usage.

### Exercise 4: Fact Gathering
Run the setup module against localhost and find: (a) your OS distribution and version, (b) total memory in MB, (c) number of CPU cores, (d) default IPv4 address, (e) Python version. Use the filter parameter to narrow results.

### Exercise 5: Multi-Host Lab
Set up the Docker-based lab from the practical section. Install `curl` and `vim` on both containers using ad-hoc commands. Create a user called `deploy` on both containers. Verify the user exists using the command module.

---

## Knowledge Check

### Question 1
What are the two inventory formats Ansible supports, and when would you choose each?

<details>
<summary>Answer</summary>

Ansible supports INI and YAML inventory formats. INI format is simpler and more readable for small, straightforward inventories — it works well when you have a flat list of hosts in a few groups with minimal variables. YAML format is better for complex inventories with deeply nested groups, structured variables, and when you want consistency with playbooks (which are also YAML). YAML also handles complex data types (lists, nested maps) more naturally. In practice, small teams and simple environments use INI; larger organizations with complex hierarchies prefer YAML. Both formats support the same features (groups, host variables, group variables, children groups).
</details>

### Question 2
Why should you prefer Ansible modules over shell/command modules?

<details>
<summary>Answer</summary>

Ansible modules are idempotent — they check the current state before making changes. The `apt` module checks if a package is installed before installing it. The `copy` module checks if the destination file matches before copying. The `service` module checks if the service is already running before starting it. Shell and command modules are NOT idempotent — they run every time regardless of state, which can cause duplicate entries, errors on existing resources, or unnecessary restarts. Modules also: (1) provide structured return values (JSON) for error handling, (2) handle platform differences (apt vs yum), (3) support check mode (dry run), and (4) produce accurate "changed" status for reporting.
</details>

### Question 3
What does `ansible_connection=local` do and when would you use it?

<details>
<summary>Answer</summary>

`ansible_connection=local` tells Ansible to execute tasks directly on the control machine instead of connecting via SSH. Ansible runs the module Python code in a local subprocess rather than copying it to a remote host. Use it when: (1) managing the control machine itself, (2) testing and learning Ansible without remote servers, (3) running tasks that only need to happen locally (generating files, making API calls), (4) using Ansible as a local automation tool. It eliminates the SSH overhead, making execution faster for local tasks. Other connection types include `ssh` (default), `docker` (for containers), and `winrm` (for Windows hosts).
</details>

### Question 4
What is pipelining in Ansible and why should you enable it?

<details>
<summary>Answer</summary>

Pipelining (`pipelining = True` in ansible.cfg under `[ssh_connection]`) changes how Ansible executes modules on remote hosts. Without pipelining, Ansible: (1) copies the module script to a temp file on the remote host, (2) executes it, (3) deletes the temp file. With pipelining, Ansible pipes the module script directly through the SSH connection and executes it without writing to disk. This eliminates two file operations per task, significantly improving performance — especially noticeable when running many tasks across many hosts. The only requirement is that `requiretty` must not be set in sudoers on the managed hosts (most modern distributions do not set it). Always enable pipelining in production.
</details>

### Question 5
How does Ansible determine which Python interpreter to use on managed hosts?

<details>
<summary>Answer</summary>

Ansible needs Python on managed hosts to execute modules. By default, it uses `auto_silent` or `auto` discovery, which searches for Python in standard locations (`/usr/bin/python3`, `/usr/bin/python`, etc.) on the remote host. You can override this with: (1) `ansible_python_interpreter` variable in inventory (per host or group), (2) `interpreter_python` in ansible.cfg, (3) setting the environment variable. This matters because some systems have Python in non-standard locations, some have only Python 2 or Python 3, and some (minimal container images) may not have Python at all. If Python is missing on a managed host, you can use the `raw` module (which does not require Python) to install it first.
</details>
