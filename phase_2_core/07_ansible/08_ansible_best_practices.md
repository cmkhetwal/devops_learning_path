# Ansible Best Practices

## Why This Matters in DevOps

Ansible is easy to start but hard to do well at scale. A single playbook for one server works fine. Fifty playbooks managing 500 servers across three environments, maintained by a team of eight, requires discipline. Without best practices, your Ansible codebase becomes what your shell scripts were — unmaintainable, untested, and unreliable.

These best practices are the accumulated wisdom of the Ansible community and battle-tested organizations. Following them means your automation is testable, maintainable, and trustworthy. Ignoring them means every change is a risk and every team member's Ansible is slightly different.

---

## Core Concepts

### Directory Layout for Large Projects

```
ansible-automation/
├── ansible.cfg                    # Ansible configuration
├── requirements.yml               # Galaxy role/collection dependencies
├── inventory/
│   ├── production/
│   │   ├── hosts.yml              # Production inventory
│   │   ├── group_vars/
│   │   │   ├── all.yml            # Variables for all production hosts
│   │   │   ├── webservers.yml     # Variables for production web servers
│   │   │   └── databases.yml
│   │   └── host_vars/
│   │       ├── web1.example.com.yml
│   │       └── db1.example.com.yml
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       └── all.yml
│   └── dev/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── playbooks/
│   ├── site.yml                   # Master playbook (includes all)
│   ├── webservers.yml             # Web server playbook
│   ├── databases.yml              # Database playbook
│   └── deploy.yml                 # Application deployment
├── roles/
│   ├── common/                    # Base configuration (all servers)
│   ├── nginx/                     # Nginx web server
│   ├── postgresql/                # PostgreSQL database
│   ├── monitoring/                # Monitoring agent
│   ├── security/                  # Security hardening
│   └── app_deploy/                # Application deployment
├── library/                       # Custom modules
├── filter_plugins/                # Custom Jinja2 filters
├── callback_plugins/              # Custom callback plugins
├── files/                         # Global static files
├── templates/                     # Global templates
└── Makefile                       # Common commands
```

**Key principles:**
- Environment-specific data lives in `inventory/<env>/group_vars/`
- Playbooks are thin — they call roles
- Roles are reusable units with their own tests
- One `site.yml` to rule them all, with include statements

### Testing with Molecule

Molecule is the standard framework for testing Ansible roles. It creates test instances (Docker containers, VMs), runs your role, and verifies the results.

```bash
# Install Molecule with Docker driver
pip install "molecule[docker]" molecule-plugins

# Initialize a new role with Molecule test setup
molecule init role my_role --driver-name docker

# Or add Molecule to an existing role
cd roles/nginx
molecule init scenario --driver-name docker
```

**Molecule directory structure:**

```
roles/nginx/
  molecule/
    default/
      molecule.yml         # Test configuration
      converge.yml         # Playbook to test the role
      verify.yml           # Verification tests
      prepare.yml          # Pre-test setup (optional)
```

**molecule/default/molecule.yml:**

```yaml
---
dependency:
  name: galaxy
  options:
    requirements-file: requirements.yml

driver:
  name: docker

platforms:
  - name: ubuntu-test
    image: ubuntu:22.04
    pre_build_image: true
    command: /bin/bash
    tmpfs:
      - /run
      - /tmp

  - name: debian-test
    image: debian:12
    pre_build_image: true
    command: /bin/bash

provisioner:
  name: ansible
  config_options:
    defaults:
      interpreter_python: auto_silent

verifier:
  name: ansible
```

**molecule/default/converge.yml:**

```yaml
---
- name: Converge
  hosts: all
  become: true
  vars:
    nginx_listen_port: 8080
    nginx_server_name: test.local
  roles:
    - role: nginx
```

**molecule/default/verify.yml:**

```yaml
---
- name: Verify
  hosts: all
  become: true
  gather_facts: false

  tasks:
    - name: Check nginx is installed
      command: dpkg -l nginx
      register: nginx_installed
      changed_when: false

    - name: Assert nginx is installed
      assert:
        that:
          - nginx_installed.rc == 0
        fail_msg: "Nginx is not installed"

    - name: Check nginx config exists
      stat:
        path: /etc/nginx/nginx.conf
      register: nginx_conf

    - name: Assert nginx config exists
      assert:
        that:
          - nginx_conf.stat.exists
          - nginx_conf.stat.mode == '0644'

    - name: Check nginx is listening on configured port
      wait_for:
        port: 8080
        timeout: 10
      register: port_check
      ignore_errors: true

    - name: Verify nginx config syntax
      command: nginx -t
      register: nginx_syntax
      changed_when: false

    - name: Assert config syntax is valid
      assert:
        that:
          - nginx_syntax.rc == 0
```

**Molecule commands:**

```bash
# Run the full test sequence
molecule test
# Sequence: dependency → lint → cleanup → destroy → create →
#           prepare → converge → idempotence → verify → cleanup → destroy

# Run individual stages
molecule create      # Create test instances
molecule converge    # Run the role
molecule verify      # Run verification tests
molecule idempotence # Run again to verify idempotency
molecule destroy     # Destroy test instances

# Debug: keep instances running
molecule converge    # Apply role
molecule login       # SSH into test instance
# Inspect the instance, debug issues
molecule destroy     # Clean up when done
```

### Linting with ansible-lint

```bash
# Install
pip install ansible-lint

# Run on a playbook
ansible-lint playbooks/site.yml

# Run on a role
ansible-lint roles/nginx/

# Example output:
# WARNING  Listing 5 violation(s) that are fatal
# name[missing]: All tasks should be named.
# roles/nginx/tasks/main.yml:12 Task/Handler: apt
#
# yaml[truthy]: Truthy value should be one of [false, true]
# roles/nginx/defaults/main.yml:5
#
# no-changed-when: Commands should not change things if nothing needs doing.
# roles/nginx/tasks/main.yml:25 Task/Handler: Run nginx -t
```

**ansible-lint configuration (.ansible-lint):**

```yaml
---
profile: production           # Strictest profile

skip_list:
  - role-name                 # Allow role names with underscores

warn_list:
  - experimental              # Treat experimental rules as warnings

exclude_paths:
  - .github/
  - molecule/
```

### Idempotency Testing

The gold standard: running your playbook twice should produce zero changes on the second run.

```bash
# Method 1: Manual
ansible-playbook site.yml          # First run: changes expected
ansible-playbook site.yml          # Second run: ZERO changes expected

# Method 2: Molecule (automated)
molecule test
# The "idempotence" stage runs the role twice and fails if
# the second run reports any changes

# Method 3: In CI/CD
- name: Run playbook
  run: ansible-playbook site.yml

- name: Test idempotency
  run: |
    ansible-playbook site.yml 2>&1 | tee output.txt
    if grep -q "changed=" output.txt && ! grep -q "changed=0" output.txt; then
      echo "IDEMPOTENCY FAILURE: Second run made changes"
      exit 1
    fi
```

### CI/CD Integration

```yaml
# .github/workflows/ansible-ci.yml
name: Ansible CI

on:
  push:
    paths: ['ansible/**']
  pull_request:
    paths: ['ansible/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ansible ansible-lint yamllint
      - run: yamllint ansible/
      - run: ansible-lint ansible/playbooks/ ansible/roles/

  molecule-test:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role:
          - common
          - nginx
          - postgresql
          - monitoring
      fail-fast: false

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ansible "molecule[docker]" molecule-plugins
      - run: cd ansible/roles/${{ matrix.role }} && molecule test

  deploy-staging:
    needs: molecule-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ansible boto3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.ANSIBLE_ROLE_ARN }}
          aws-region: us-east-1
      - run: |
          cd ansible
          ansible-galaxy install -r requirements.yml
          ansible-playbook -i inventory/staging/hosts.yml playbooks/site.yml
```

### When Ansible Is the Wrong Tool

| Scenario | Better Tool | Why |
|----------|-------------|-----|
| Creating cloud infrastructure | Terraform | State management, plan/apply, lifecycle |
| Building container images | Dockerfile | Layers, caching, portability |
| Deploying to Kubernetes | Helm/Kustomize | K8s-native, declarative, rollbacks |
| Continuous configuration enforcement | Puppet | Agent-based, automatic drift correction |
| Application-level config | Feature flags | Runtime config without deployments |
| Secrets management | HashiCorp Vault | Dynamic secrets, fine-grained access |
| Simple file sync | rsync | Faster for bulk file transfers |

### Migrating from Shell Scripts to Ansible

**Before (shell script):**

```bash
#!/bin/bash
set -e
apt-get update
apt-get install -y nginx
cp /opt/config/nginx.conf /etc/nginx/nginx.conf
systemctl restart nginx
useradd -m -s /bin/bash deploy
mkdir -p /opt/app
chown deploy:deploy /opt/app
```

**After (Ansible playbook):**

```yaml
- name: Configure web server
  hosts: webservers
  become: true

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: true

    - name: Deploy nginx configuration
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        mode: '0644'
        validate: nginx -t -c %s
      notify: Restart nginx

    - name: Create deploy user
      user:
        name: deploy
        shell: /bin/bash
        create_home: true

    - name: Create application directory
      file:
        path: /opt/app
        state: directory
        owner: deploy
        group: deploy
        mode: '0755'

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

**Migration benefits:**
- Idempotent (safe to run multiple times)
- Self-documenting (clear task names)
- Error handling (automatic failure detection)
- Dry run support (`--check`)
- Targets multiple hosts simultaneously
- Configuration validation before deployment
- Change tracking (changed vs ok)

### Common Mistakes

**1. Using shell/command when modules exist:**

```yaml
# BAD
- name: Install nginx
  shell: apt-get install -y nginx

# GOOD
- name: Install nginx
  apt:
    name: nginx
    state: present
```

**2. Not using handlers for restarts:**

```yaml
# BAD — restarts every time, even when config did not change
- template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
- service:
    name: nginx
    state: restarted

# GOOD — restarts only when config changes
- template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart nginx
```

**3. Hardcoding values instead of using variables:**

```yaml
# BAD
- apt:
    name: nginx=1.18.0-0ubuntu1
- template:
    src: site.conf.j2
    dest: /etc/nginx/sites-available/mysite.conf

# GOOD
- apt:
    name: "nginx={{ nginx_version }}"
- template:
    src: site.conf.j2
    dest: "/etc/nginx/sites-available/{{ site_name }}.conf"
```

**4. Not setting `changed_when` for informational commands:**

```yaml
# BAD — shows "changed" every time
- name: Check disk space
  command: df -h

# GOOD
- name: Check disk space
  command: df -h
  register: disk_space
  changed_when: false
```

**5. Not testing idempotency:**

```yaml
# Always run your playbook twice and verify zero changes on second run
```

---

## Step-by-Step Practical

### Complete Project Setup

```bash
mkdir -p ~/ansible-lab/best-practices
cd ~/ansible-lab/best-practices

# Create the Makefile
cat > Makefile << 'EOF'
.PHONY: lint test deploy-dev deploy-prod

ANSIBLE_DIR = .
INVENTORY_DEV = inventory/dev/hosts.ini
INVENTORY_PROD = inventory/prod/hosts.ini

lint:
	yamllint .
	ansible-lint playbooks/ roles/

test:
	@for role in roles/*/; do \
		if [ -d "$$role/molecule" ]; then \
			echo "Testing $$role..."; \
			cd $$role && molecule test && cd ../..; \
		fi \
	done

syntax-check:
	ansible-playbook --syntax-check -i $(INVENTORY_DEV) playbooks/site.yml

dry-run-dev:
	ansible-playbook --check --diff -i $(INVENTORY_DEV) playbooks/site.yml

deploy-dev:
	ansible-playbook -i $(INVENTORY_DEV) playbooks/site.yml

deploy-prod:
	ansible-playbook -i $(INVENTORY_PROD) playbooks/site.yml --ask-vault-pass

check-idempotency:
	ansible-playbook -i $(INVENTORY_DEV) playbooks/site.yml
	@echo "Running again to check idempotency..."
	ansible-playbook -i $(INVENTORY_DEV) playbooks/site.yml 2>&1 | tee /tmp/idempotency.txt
	@grep -q "changed=0" /tmp/idempotency.txt && echo "PASS: Idempotent" || echo "FAIL: Not idempotent"
EOF

echo "Project structure created. Use 'make lint', 'make test', 'make deploy-dev'."
```

### Ansible-Lint Configuration

```yaml
# .ansible-lint
---
profile: production

skip_list:
  - name[casing]              # Allow mixed case in names

warn_list:
  - experimental

exclude_paths:
  - .github/
  - molecule/
  - .cache/

use_default_rules: true

enable_list:
  - empty-string-compare
  - no-log-password
  - no-same-owner
```

### yamllint Configuration

```yaml
# .yamllint
---
extends: default

rules:
  line-length:
    max: 120
    level: warning
  truthy:
    allowed-values: ['true', 'false', 'yes', 'no']
  comments:
    require-starting-space: true
    min-spaces-from-content: 1
  document-start: disable
  indentation:
    spaces: 2
    indent-sequences: consistent
```

---

## Exercises

### Exercise 1: Project Structure
Create a complete Ansible project following the recommended directory layout. Include: 3 environments (dev/staging/prod), 4 roles (common, webserver, database, monitoring), environment-specific variables, and a master playbook that ties everything together.

### Exercise 2: Molecule Testing
Add Molecule tests to one of your roles. The tests should: (a) create a Docker container, (b) apply the role, (c) verify idempotency (second run has zero changes), (d) verify the expected files exist with correct content. Run `molecule test` and fix any failures.

### Exercise 3: Linting Cleanup
Run ansible-lint on your playbooks and roles. Fix all errors and warnings. Add a `.ansible-lint` config file that skips only the rules you have a documented reason to skip.

### Exercise 4: CI/CD Pipeline
Create a GitHub Actions workflow for your Ansible project that runs: yamllint, ansible-lint, syntax check, and Molecule tests for each role. The pipeline should fail on any linting error.

### Exercise 5: Shell Script Migration
Take the following shell script and convert it to an Ansible playbook with proper roles, variables, templates, and handlers:

```bash
#!/bin/bash
apt-get update && apt-get install -y nginx postgresql redis-server
cp /opt/configs/nginx.conf /etc/nginx/nginx.conf
cp /opt/configs/pg_hba.conf /etc/postgresql/14/main/pg_hba.conf
systemctl restart nginx postgresql redis-server
useradd -m app && mkdir -p /opt/app && chown app:app /opt/app
echo "deploy_time=$(date)" >> /opt/app/metadata.txt
```

---

## Knowledge Check

### Question 1
What is Molecule and why is it important for Ansible automation?

<details>
<summary>Answer</summary>

Molecule is a testing framework for Ansible roles. It automates the process of creating test instances (Docker containers, VMs, or cloud instances), running the role against them, verifying the results, and cleaning up. It is important because: (1) it tests roles in isolation, catching errors before they reach production; (2) the idempotency test automatically verifies that running the role twice produces zero changes; (3) verification tests assert that the expected state was achieved (files exist, services running, ports listening); (4) it tests across multiple platforms (Ubuntu, Debian, CentOS) simultaneously; (5) it integrates with CI/CD for automated testing on every commit. Without Molecule, testing Ansible roles requires manual effort — create a VM, run the role, check the results, destroy the VM — which is slow and error-prone.
</details>

### Question 2
What are the most common Ansible anti-patterns and how do you fix them?

<details>
<summary>Answer</summary>

Common anti-patterns: (1) Using `shell` or `command` when a module exists — fix by using the appropriate module (apt, copy, service, user) which provides idempotency and structured output. (2) Not using handlers — fix by using `notify` to trigger service restarts only when configuration actually changes. (3) Monolithic playbooks — fix by extracting reusable roles with clear interfaces (defaults/main.yml). (4) Not testing idempotency — fix by running playbooks twice and verifying zero changes, or using Molecule. (5) Hardcoded values — fix by using variables with sensible defaults. (6) Not setting `changed_when: false` on informational commands — fix by explicitly marking commands that do not change state. (7) Storing secrets in plain text — fix by using Ansible Vault.
</details>

### Question 3
When should you choose Ansible over alternative tools?

<details>
<summary>Answer</summary>

Choose Ansible when: (1) you need to configure existing servers (install packages, manage configs, deploy applications) — this is Ansible's sweet spot; (2) you need agentless automation — SSH-based access with no agent installation; (3) you manage diverse infrastructure (Linux, Windows, network devices) that cannot run agents; (4) you need quick adoption — YAML playbooks have a lower learning curve than Puppet DSL or Chef Ruby; (5) you are bridging the gap between Terraform (provisioning) and application deployment; (6) you need ad-hoc task execution across many servers. Choose alternatives when: containers handle your configuration (Dockerfile), you need continuous enforcement (Puppet), you are deploying to Kubernetes (Helm/ArgoCD), or you are provisioning cloud infrastructure (Terraform).
</details>

### Question 4
How should you structure variables across environments in a large Ansible project?

<details>
<summary>Answer</summary>

The recommended structure: (1) `group_vars/all.yml` for values shared across all environments (NTP servers, monitoring endpoints, standard packages); (2) `inventory/<env>/group_vars/all.yml` for environment-wide overrides (log level, database endpoints, feature flags); (3) `inventory/<env>/group_vars/<role>.yml` for role-specific values per environment (webserver port, database max_connections); (4) `inventory/<env>/host_vars/<host>.yml` for host-specific values (only when a single host truly differs); (5) `roles/<name>/defaults/main.yml` for role defaults that users override; (6) sensitive values encrypted with Vault in dedicated secrets files. The principle is: defaults cascade from general to specific, and the most specific value wins. Never put environment-specific values in role defaults — those belong in inventory group_vars.
</details>

### Question 5
How do you ensure Ansible playbooks are safe to run in production?

<details>
<summary>Answer</summary>

Production safety requires multiple layers: (1) always run `--check --diff` (dry run) before applying to production; (2) use `serial` for rolling updates to maintain availability; (3) implement block/rescue/always for error handling and rollback; (4) test with Molecule in CI before deployment; (5) use `validate` on template modules to catch config errors before deployment; (6) run ansible-lint to catch common mistakes; (7) test idempotency — second run must have zero changes; (8) use `max_fail_percentage` to abort if too many hosts fail; (9) encrypt secrets with Vault; (10) pin Galaxy role versions in requirements.yml; (11) use branch protection and PR reviews for playbook changes; (12) implement `--limit` when targeting specific hosts to prevent accidental wide-scope runs.
</details>
