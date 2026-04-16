# Advanced Ansible

## Why This Matters in DevOps

Production Ansible automation deals with problems that tutorials skip: encrypting secrets, discovering infrastructure dynamically, handling errors gracefully, managing thousands of servers with rolling updates, and extending Ansible's capabilities with custom code.

These advanced features separate a working playbook from a production-ready one. Vault keeps your secrets out of Git. Dynamic inventory discovers servers automatically instead of maintaining static lists. Error handling ensures a failed task does not leave your infrastructure in an inconsistent state. These are the skills that distinguish a junior DevOps engineer from a senior one.

---

## Core Concepts

### Ansible Vault — Encrypting Secrets

Vault encrypts sensitive data so it can live safely in version control.

```bash
# Create an encrypted file
ansible-vault create secrets.yml
# Opens your editor — type your secrets in YAML format

# Encrypt an existing file
ansible-vault encrypt group_vars/prod/secrets.yml

# Decrypt a file (for editing)
ansible-vault decrypt group_vars/prod/secrets.yml

# Edit an encrypted file (decrypt, edit, re-encrypt)
ansible-vault edit group_vars/prod/secrets.yml

# View an encrypted file without editing
ansible-vault view group_vars/prod/secrets.yml

# Change the vault password
ansible-vault rekey group_vars/prod/secrets.yml

# Encrypt a single string (for embedding in a regular file)
ansible-vault encrypt_string 'SuperSecret123!' --name 'db_password'
# Output:
# db_password: !vault |
#   $ANSIBLE_VAULT;1.1;AES256
#   6132356137613062363163363...
```

**Using vault in playbooks:**

```yaml
# group_vars/prod/secrets.yml (encrypted)
db_password: SuperSecret123!
api_key: sk-abc123def456
ssl_private_key: |
  -----BEGIN PRIVATE KEY-----
  MIIEvQIBADANBg...
  -----END PRIVATE KEY-----
```

```bash
# Run a playbook with vault
ansible-playbook site.yml --ask-vault-pass
# Enter password when prompted

# Or use a password file (for CI/CD)
echo "my-vault-password" > .vault-pass
chmod 600 .vault-pass
ansible-playbook site.yml --vault-password-file .vault-pass

# Configure in ansible.cfg
# [defaults]
# vault_password_file = .vault-pass
```

**Multiple vault passwords (for different security levels):**

```bash
# Encrypt with a specific vault ID
ansible-vault encrypt --vault-id dev@prompt group_vars/dev/secrets.yml
ansible-vault encrypt --vault-id prod@prod-vault-pass group_vars/prod/secrets.yml

# Run with multiple vault IDs
ansible-playbook site.yml \
  --vault-id dev@prompt \
  --vault-id prod@prod-vault-pass
```

### Dynamic Inventory

Static inventory files become unmanageable when your infrastructure changes frequently. Dynamic inventory discovers hosts from cloud APIs, CMDBs, or other sources.

**AWS EC2 dynamic inventory:**

```yaml
# inventory_aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2

keyed_groups:
  # Create groups from EC2 tags
  - key: tags.Environment
    prefix: env
    separator: "_"
  - key: tags.Role
    prefix: role
    separator: "_"
  - key: instance_type
    prefix: type
    separator: "_"

filters:
  instance-state-name: running
  "tag:ManagedBy": ansible

hostnames:
  - private-ip-address          # Use private IP as hostname

compose:
  ansible_host: private_ip_address
  ansible_user: "'ubuntu'"
```

```bash
# Install the AWS collection
ansible-galaxy collection install amazon.aws

# Test the dynamic inventory
ansible-inventory -i inventory_aws_ec2.yml --list
ansible-inventory -i inventory_aws_ec2.yml --graph

# Output:
# @all:
#   |--@env_production:
#   |  |--10.0.1.10
#   |  |--10.0.1.11
#   |--@env_staging:
#   |  |--10.0.2.10
#   |--@role_webserver:
#   |  |--10.0.1.10
#   |  |--10.0.2.10
#   |--@role_database:
#   |  |--10.0.1.11

# Use in playbooks
ansible-playbook -i inventory_aws_ec2.yml site.yml
```

### Blocks and Error Handling

Blocks group tasks and provide try/catch/finally error handling:

```yaml
tasks:
  - name: Deployment with error handling
    block:
      # Try: main deployment tasks
      - name: Pull latest code
        git:
          repo: https://github.com/org/app.git
          dest: /opt/app
          version: "{{ app_version }}"

      - name: Install dependencies
        pip:
          requirements: /opt/app/requirements.txt
          virtualenv: /opt/app/venv

      - name: Run database migrations
        command: /opt/app/venv/bin/python manage.py migrate
        args:
          chdir: /opt/app

      - name: Restart application
        service:
          name: myapp
          state: restarted

    rescue:
      # Catch: runs if any task in block fails
      - name: Rollback to previous version
        command: /opt/app/rollback.sh
        args:
          chdir: /opt/app

      - name: Send failure notification
        uri:
          url: "{{ slack_webhook }}"
          method: POST
          body_format: json
          body:
            text: "Deployment FAILED on {{ inventory_hostname }}: {{ ansible_failed_task.name }}"

    always:
      # Finally: runs regardless of success or failure
      - name: Clean up temp files
        file:
          path: /tmp/deploy-staging
          state: absent

      - name: Log deployment attempt
        lineinfile:
          path: /var/log/deployments.log
          line: "{{ ansible_date_time.iso8601 }} - {{ app_version }} - {{ 'SUCCESS' if ansible_failed_task is not defined else 'FAILED' }}"
          create: true
```

### Async Tasks

For long-running tasks that would otherwise time out:

```yaml
tasks:
  - name: Run database backup (takes 30 minutes)
    command: /opt/scripts/full-backup.sh
    async: 3600                      # Allow up to 1 hour
    poll: 0                          # Do not wait (fire and forget)
    register: backup_job

  - name: Do other work while backup runs
    apt:
      name: htop
      state: present

  - name: Wait for backup to complete
    async_status:
      jid: "{{ backup_job.ansible_job_id }}"
    register: backup_result
    until: backup_result.finished
    retries: 60
    delay: 30                        # Check every 30 seconds
```

### Delegation

Run a task on a different host than the play's target:

```yaml
tasks:
  # Run this task on the load balancer, not the web server
  - name: Remove server from load balancer
    uri:
      url: "http://{{ lb_host }}/api/deregister"
      method: POST
      body_format: json
      body:
        server: "{{ inventory_hostname }}"
    delegate_to: "{{ lb_host }}"

  - name: Deploy application
    copy:
      src: app.tar.gz
      dest: /opt/app/

  # Run locally (on the control machine)
  - name: Update deployment tracker
    uri:
      url: "https://deploy-tracker.internal/api/deployments"
      method: POST
      body_format: json
      body:
        server: "{{ inventory_hostname }}"
        version: "{{ app_version }}"
    delegate_to: localhost
    run_once: true                   # Only run once, not per host
```

### Serial Execution and Rolling Updates

Deploy to a subset of servers at a time to maintain availability:

```yaml
- name: Rolling update web servers
  hosts: webservers
  serial: 2                          # Deploy to 2 servers at a time
  # serial: "30%"                    # Or use percentage
  # serial: [1, 5, 10]              # Increasing batches (canary)
  max_fail_percentage: 25            # Abort if >25% of hosts fail

  tasks:
    - name: Remove from load balancer
      uri:
        url: "http://lb/api/deregister/{{ inventory_hostname }}"
        method: POST
      delegate_to: localhost

    - name: Deploy new version
      copy:
        src: "app-{{ version }}.tar.gz"
        dest: /opt/app/

    - name: Restart application
      service:
        name: myapp
        state: restarted

    - name: Wait for health check
      uri:
        url: "http://{{ inventory_hostname }}:8080/health"
        status_code: 200
      register: health
      until: health.status == 200
      retries: 10
      delay: 5

    - name: Re-register with load balancer
      uri:
        url: "http://lb/api/register/{{ inventory_hostname }}"
        method: POST
      delegate_to: localhost
```

With `serial: [1, 5, "100%"]`:

```
Batch 1: Deploy to 1 server (canary)
  → If success, proceed
Batch 2: Deploy to 5 servers
  → If success, proceed
Batch 3: Deploy to remaining servers (100%)
```

---

## Step-by-Step Practical

### Vault Workflow

```bash
mkdir -p ~/ansible-lab/advanced/{group_vars/prod,templates}
cd ~/ansible-lab/advanced

# Create vault password file
echo "training-vault-pass" > .vault-pass
chmod 600 .vault-pass

# Create ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
inventory = inventory.ini
vault_password_file = .vault-pass
stdout_callback = yaml
EOF

# Create inventory
cat > inventory.ini << 'EOF'
[local]
localhost ansible_connection=local
EOF

# Create encrypted secrets
ansible-vault create group_vars/prod/secrets.yml
# In the editor, enter:
# db_password: "MyS3cretP@ssw0rd"
# api_key: "sk-prod-abc123def456"
# smtp_password: "mail-p@ss-789"

# View the encrypted file (raw)
cat group_vars/prod/secrets.yml
# $ANSIBLE_VAULT;1.1;AES256
# 613235613... (encrypted content)

# View decrypted
ansible-vault view group_vars/prod/secrets.yml

# Use in a playbook
cat > site.yml << 'YAML'
---
- name: Demonstrate vault
  hosts: local
  vars_files:
    - group_vars/prod/secrets.yml

  tasks:
    - name: Show that secrets are usable
      debug:
        msg: "DB password length: {{ db_password | length }} characters"

    - name: Generate app config with secrets
      template:
        src: templates/app-secrets.conf.j2
        dest: /tmp/ansible-vault-demo.conf
        mode: '0600'
YAML

cat > templates/app-secrets.conf.j2 << 'TEMPLATE'
# Application configuration (contains secrets)
[database]
password = {{ db_password }}

[api]
key = {{ api_key }}

[smtp]
password = {{ smtp_password }}
TEMPLATE

# Run the playbook (vault is decrypted automatically via .vault-pass)
ansible-playbook site.yml

# The output shows the password LENGTH, not the actual password
# The generated file contains the actual passwords
```

### Error Handling Demonstration

```yaml
# error-handling.yml
---
- name: Demonstrate error handling
  hosts: local
  gather_facts: false

  tasks:
    - name: Deployment simulation
      block:
        - name: Step 1 — Check prerequisites
          debug:
            msg: "Prerequisites OK"

        - name: Step 2 — Deploy (simulated failure)
          command: /bin/false           # This will fail
          # change to /bin/true to see success path

        - name: Step 3 — Verify (skipped on failure)
          debug:
            msg: "Verification passed"

      rescue:
        - name: Rollback — revert changes
          debug:
            msg: "ROLLING BACK due to failure in: {{ ansible_failed_task.name }}"

        - name: Notify team of failure
          debug:
            msg: "ALERT: Deployment failed on {{ inventory_hostname }}"

      always:
        - name: Cleanup — remove temp files
          debug:
            msg: "Cleanup completed (runs regardless of outcome)"

        - name: Log result
          debug:
            msg: "Deployment {{ 'FAILED' if ansible_failed_task is defined else 'SUCCEEDED' }}"
```

```bash
ansible-playbook error-handling.yml
```

---

## Exercises

### Exercise 1: Vault Practice
Create an encrypted variables file containing database credentials, API keys, and an SSH private key. Write a playbook that uses these secrets to generate a configuration file. Verify that the playbook works with both `--ask-vault-pass` and `--vault-password-file`.

### Exercise 2: Error Handling
Write a playbook that simulates a multi-step deployment: download code, install dependencies, run migrations, restart service. Use block/rescue/always to handle failures. In the rescue section, implement a rollback that reverses each step. In the always section, send a notification (simulated with debug).

### Exercise 3: Rolling Update Simulation
Create an inventory with 6 hosts (use localhost aliases). Write a playbook with `serial: 2` that simulates a rolling update by creating timestamped files. Verify that servers are updated in batches of 2 and that the total update takes 3 rounds.

### Exercise 4: Delegation
Write a playbook where the main play targets "webservers" but delegates a task to "localhost" to update a central registry. Use `delegate_to` and `run_once` to ensure the registry update happens only once, not once per host.

### Exercise 5: Async Long-Running Task
Write a playbook that starts a long-running background task (use `sleep 30` as a simulation), performs other work while it runs, and then waits for completion using `async_status`. Verify that the total playbook runtime is less than 30 seconds (because the sleep runs in background).

---

## Knowledge Check

### Question 1
How does Ansible Vault work and what are the best practices for managing vault passwords?

<details>
<summary>Answer</summary>

Ansible Vault encrypts files or strings using AES-256 encryption with a password you provide. The encrypted content can be safely committed to Git since it is unreadable without the password. Best practices: (1) use a vault password file (`--vault-password-file`) in CI/CD rather than interactive prompts, (2) never commit the vault password file to Git (add to .gitignore), (3) use vault IDs to separate passwords by environment (dev vault password vs prod vault password), (4) encrypt only the files that contain secrets, not entire playbooks, (5) use `ansible-vault encrypt_string` for individual values within otherwise unencrypted files, (6) store vault passwords in a secrets manager (HashiCorp Vault, AWS Secrets Manager) and fetch them during CI/CD runs.
</details>

### Question 2
What is the difference between block/rescue/always and ignore_errors?

<details>
<summary>Answer</summary>

`ignore_errors: true` on a task simply suppresses the error and continues to the next task — the failure is silently ignored, which can leave the system in an inconsistent state. `block/rescue/always` provides structured error handling: the `block` section contains the main tasks, `rescue` runs when any block task fails (like a catch block), and `always` runs regardless (like a finally block). `rescue` gives you the opportunity to roll back changes, send notifications, or clean up. Use `ignore_errors` only when a failure is genuinely expected and harmless (e.g., checking if a process exists). Use block/rescue/always when you need to respond to failures with corrective action.
</details>

### Question 3
How does `serial` enable zero-downtime deployments?

<details>
<summary>Answer</summary>

`serial` limits how many hosts are updated simultaneously. Without serial, Ansible updates all hosts in parallel — if the deployment breaks the application, all servers go down at once. With `serial: 2`, only 2 servers are updated at a time while the rest continue serving traffic. The workflow typically: (1) removes servers from the load balancer, (2) deploys the new version, (3) runs health checks, (4) re-registers with the load balancer, then moves to the next batch. Using `serial: [1, 5, "100%"]` implements a canary pattern: deploy to 1 server first (canary), verify it works, then expand to 5, then all remaining. Combined with `max_fail_percentage`, this ensures deployment stops if too many hosts fail.
</details>

### Question 4
When should you use dynamic inventory instead of static inventory files?

<details>
<summary>Answer</summary>

Use dynamic inventory when: (1) your infrastructure changes frequently (auto-scaling groups, container orchestration) — static files become stale immediately; (2) you manage hundreds or thousands of servers — manual inventory maintenance is impractical; (3) your infrastructure is defined in a cloud provider (AWS, Azure, GCP) — the cloud API is the source of truth; (4) you want group membership derived from metadata (EC2 tags, labels) rather than manually maintained; (5) you use multiple environments that share the same playbooks but target different infrastructure. Dynamic inventory plugins query cloud APIs in real-time, ensuring your inventory always reflects the current state of your infrastructure.
</details>

### Question 5
What does `delegate_to` do and what is a common pitfall?

<details>
<summary>Answer</summary>

`delegate_to` runs a task on a different host than the play's current target. The task still has access to the target host's variables (facts, host_vars, etc.) but executes on the delegated host. Common uses: registering/deregistering servers from load balancers (delegate to the LB), updating a central database or API (delegate to localhost), running checks from a specific network location. The common pitfall is variable scope confusion: `inventory_hostname` still refers to the play's target host, not the delegated host. If you need the delegated host's facts, use `hostvars[delegated_host]`. Also, `delegate_to: localhost` runs on the control machine with local connection, which may have different permissions and paths than expected.
</details>
