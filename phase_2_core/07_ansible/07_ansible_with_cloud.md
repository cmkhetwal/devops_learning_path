# Ansible with Cloud Providers

## Why This Matters in DevOps

The line between provisioning and configuration blurs in practice. Terraform creates your EC2 instance, but who installs your application on it? Who configures the monitoring agent? Who sets up the log shipping? The answer, in most organizations, is Ansible.

The Terraform + Ansible combination is the most common pattern in production DevOps: Terraform provisions the infrastructure (creates the server), Ansible configures it (installs software, deploys the application). Understanding how to use Ansible with cloud providers — and specifically how to bridge the gap between Terraform and Ansible — is essential for building complete automation pipelines.

---

## Core Concepts

### AWS Modules

Ansible's AWS modules (in the `amazon.aws` and `community.aws` collections) can create and manage AWS resources:

```bash
# Install AWS collections
ansible-galaxy collection install amazon.aws community.aws

# Install boto3 (AWS Python SDK, required by AWS modules)
pip install boto3 botocore
```

**EC2 Instance Management:**

```yaml
- name: Manage EC2 instances
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    aws_region: us-east-1
    instance_type: t3.micro
    key_name: my-keypair
    ami_id: ami-0c55b159cbfafe1f0

  tasks:
    - name: Create a security group
      amazon.aws.ec2_security_group:
        name: web-sg
        description: Web server security group
        region: "{{ aws_region }}"
        rules:
          - proto: tcp
            ports: [80, 443]
            cidr_ip: 0.0.0.0/0
            rule_desc: HTTP/HTTPS
          - proto: tcp
            ports: [22]
            cidr_ip: 10.0.0.0/8
            rule_desc: SSH from internal
        rules_egress:
          - proto: all
            cidr_ip: 0.0.0.0/0
      register: sg

    - name: Launch EC2 instances
      amazon.aws.ec2_instance:
        name: "web-{{ item }}"
        instance_type: "{{ instance_type }}"
        image_id: "{{ ami_id }}"
        key_name: "{{ key_name }}"
        security_groups:
          - "{{ sg.group_id }}"
        region: "{{ aws_region }}"
        state: running
        wait: true
        tags:
          Environment: production
          Role: webserver
          ManagedBy: ansible
      loop:
        - 1
        - 2
      register: ec2_instances

    - name: Show instance details
      debug:
        msg: "Instance {{ item.instances[0].instance_id }}: {{ item.instances[0].public_ip_address }}"
      loop: "{{ ec2_instances.results }}"
      when: item.instances is defined
```

**S3 Bucket Management:**

```yaml
    - name: Create S3 bucket
      amazon.aws.s3_bucket:
        name: "myapp-assets-{{ ansible_date_time.epoch }}"
        region: "{{ aws_region }}"
        versioning: true
        encryption: AES256
        public_access:
          block_public_acls: true
          block_public_policy: true
          ignore_public_acls: true
          restrict_public_buckets: true
        tags:
          Environment: production

    - name: Upload file to S3
      amazon.aws.s3_object:
        bucket: myapp-assets
        object: config/app.conf
        src: /tmp/app.conf
        mode: put
```

**IAM Role Management:**

```yaml
    - name: Create IAM role for EC2
      amazon.aws.iam_role:
        name: web-server-role
        assume_role_policy_document:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Principal:
                Service: ec2.amazonaws.com
              Action: sts:AssumeRole
        managed_policies:
          - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
        state: present
```

### Combining Terraform and Ansible

The most common pattern: Terraform provisions, Ansible configures.

**Pattern 1: Terraform outputs to Ansible inventory**

```hcl
# Terraform: outputs.tf
output "web_server_ips" {
  value = aws_instance.web[*].public_ip
}

output "db_server_ip" {
  value = aws_instance.db.private_ip
}
```

```bash
# Generate Ansible inventory from Terraform output
terraform output -json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('[webservers]')
for ip in data['web_server_ips']['value']:
    print(ip)
print()
print('[databases]')
print(data['db_server_ip']['value'])
" > inventory-terraform.ini

# Run Ansible with the generated inventory
ansible-playbook -i inventory-terraform.ini site.yml
```

**Pattern 2: Terraform local-exec provisioner (direct integration)**

```hcl
# Terraform calls Ansible after creating instances
resource "aws_instance" "web" {
  count         = 3
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name      = aws_key_pair.deploy.key_name

  tags = {
    Name = "web-${count.index}"
    Role = "webserver"
  }

  provisioner "local-exec" {
    command = <<-EOT
      sleep 30  # Wait for SSH to be ready
      ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook \
        -i '${self.public_ip},' \
        -u ubuntu \
        --private-key ${var.ssh_key_path} \
        ansible/web-server.yml
    EOT
  }
}
```

**Pattern 3: Dynamic inventory with AWS tags (recommended)**

This is the cleanest approach — Terraform tags instances, Ansible discovers them:

```hcl
# Terraform tags instances
resource "aws_instance" "web" {
  count         = 3
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  tags = {
    Name        = "web-${count.index}"
    Role        = "webserver"
    Environment = var.environment
    ManagedBy   = "ansible"           # Tag for Ansible discovery
  }
}
```

```yaml
# inventory_aws.yml — Ansible dynamic inventory
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1

filters:
  "tag:ManagedBy": ansible
  instance-state-name: running

keyed_groups:
  - key: tags.Role
    prefix: role
  - key: tags.Environment
    prefix: env

compose:
  ansible_host: public_ip_address
  ansible_user: "'ubuntu'"
```

```bash
# Ansible discovers instances tagged by Terraform
ansible-inventory -i inventory_aws.yml --graph
# @all:
#   |--@role_webserver:
#   |  |--54.210.1.10
#   |  |--54.210.1.11
#   |  |--54.210.1.12
#   |--@env_production:
#   |  |--54.210.1.10
#   |  |--54.210.1.11
#   |  |--54.210.1.12

ansible-playbook -i inventory_aws.yml site.yml
```

### Cloud Inventory Plugins

**Azure:**

```yaml
# inventory_azure.yml
plugin: azure.azcollection.azure_rm
auth_source: auto

include_vm_resource_groups:
  - production-rg

keyed_groups:
  - prefix: tag
    key: tags
```

**GCP:**

```yaml
# inventory_gcp.yml
plugin: google.cloud.gcp_compute
projects:
  - my-gcp-project
zones:
  - us-central1-a
  - us-central1-b

filters:
  - labels.managed_by = ansible

keyed_groups:
  - key: labels.role
    prefix: role
```

---

## Step-by-Step Practical

### Complete Terraform + Ansible Workflow (Simulated)

Since we may not have cloud accounts, we will simulate the workflow with local files:

```bash
mkdir -p ~/ansible-lab/cloud-demo/{terraform,ansible/{roles/webserver/{tasks,templates,handlers,defaults},group_vars}}
cd ~/ansible-lab/cloud-demo
```

**Step 1: Terraform creates infrastructure (simulated)**

```bash
# Simulate Terraform output
cat > terraform/terraform-output.json << 'EOF'
{
  "web_servers": {
    "value": [
      {"name": "web-0", "ip": "10.0.1.10", "az": "us-east-1a"},
      {"name": "web-1", "ip": "10.0.1.11", "az": "us-east-1b"},
      {"name": "web-2", "ip": "10.0.1.12", "az": "us-east-1a"}
    ]
  },
  "db_server": {
    "value": {"name": "db-0", "ip": "10.0.2.10", "endpoint": "db.internal:5432"}
  },
  "environment": {
    "value": "production"
  },
  "vpc_cidr": {
    "value": "10.0.0.0/16"
  }
}
EOF
```

**Step 2: Generate Ansible inventory from Terraform output**

```bash
cat > generate-inventory.py << 'PYTHON'
#!/usr/bin/env python3
"""Generate Ansible inventory from Terraform output."""
import json

with open("terraform/terraform-output.json") as f:
    tf = json.load(f)

env = tf["environment"]["value"]

# We use localhost with aliases since we do not have real remote servers
inventory = f"""# Auto-generated from Terraform output
# Environment: {env}

[webservers]
"""

for server in tf["web_servers"]["value"]:
    inventory += (
        f"{server['name']} ansible_host=localhost ansible_connection=local "
        f"server_ip={server['ip']} availability_zone={server['az']}\n"
    )

db = tf["db_server"]["value"]
inventory += f"""
[databases]
{db['name']} ansible_host=localhost ansible_connection=local server_ip={db['ip']} db_endpoint={db['endpoint']}

[all:vars]
environment={env}
vpc_cidr={tf['vpc_cidr']['value']}
"""

with open("ansible/inventory-generated.ini", "w") as f:
    f.write(inventory)

print(f"Generated inventory with {len(tf['web_servers']['value'])} web servers and 1 database server")
PYTHON

python3 generate-inventory.py
cat ansible/inventory-generated.ini
```

**Step 3: Create Ansible role for web server configuration**

```yaml
# ansible/roles/webserver/defaults/main.yml
---
app_port: 8080
app_workers: 4
nginx_worker_connections: 1024
log_level: warn
health_check_path: /health
```

```yaml
# ansible/roles/webserver/tasks/main.yml
---
- name: Create application directories
  file:
    path: "/tmp/cloud-demo/{{ inventory_hostname }}/{{ item }}"
    state: directory
    mode: '0755'
  loop:
    - config
    - logs
    - app

- name: Deploy nginx configuration
  template:
    src: nginx-vhost.conf.j2
    dest: "/tmp/cloud-demo/{{ inventory_hostname }}/config/nginx.conf"
    mode: '0644'
  notify: Configuration updated

- name: Deploy application config
  template:
    src: app-config.json.j2
    dest: "/tmp/cloud-demo/{{ inventory_hostname }}/config/app.json"
    mode: '0644'
  notify: Configuration updated

- name: Create deployment marker
  copy:
    content: |
      Deployed: {{ ansible_date_time.iso8601 }}
      Host: {{ inventory_hostname }}
      IP: {{ server_ip }}
      AZ: {{ availability_zone | default('unknown') }}
      Environment: {{ environment }}
    dest: "/tmp/cloud-demo/{{ inventory_hostname }}/DEPLOYED"
    mode: '0644'
```

```yaml
# ansible/roles/webserver/handlers/main.yml
---
- name: Configuration updated
  debug:
    msg: "Configuration updated on {{ inventory_hostname }} ({{ server_ip }})"
```

```jinja
{# ansible/roles/webserver/templates/nginx-vhost.conf.j2 #}
# Nginx configuration for {{ inventory_hostname }}
# Server IP: {{ server_ip }}
# Environment: {{ environment }}

upstream app_backend {
    server 127.0.0.1:{{ app_port }};
}

server {
    listen 80;
    server_name {{ server_ip }};

    access_log /var/log/nginx/{{ inventory_hostname }}-access.log;
    error_log /var/log/nginx/{{ inventory_hostname }}-error.log {{ log_level }};

    location {{ health_check_path }} {
        proxy_pass http://app_backend;
        access_log off;
    }

    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Server-IP {{ server_ip }};
        proxy_set_header X-Server-AZ {{ availability_zone | default('unknown') }};
    }
}
```

```jinja
{# ansible/roles/webserver/templates/app-config.json.j2 #}
{
  "server": {
    "host": "{{ server_ip }}",
    "port": {{ app_port }},
    "workers": {{ app_workers }},
    "environment": "{{ environment }}"
  },
  "database": {
    "endpoint": "{{ hostvars[groups['databases'][0]].db_endpoint | default('localhost:5432') }}"
  },
  "logging": {
    "level": "{{ log_level }}",
    "directory": "/var/log/myapp"
  }
}
```

**Step 4: Create the main playbook**

```yaml
# ansible/site.yml
---
- name: Configure web servers (provisioned by Terraform)
  hosts: webservers
  gather_facts: true

  roles:
    - webserver

  post_tasks:
    - name: Verify deployment
      command: cat /tmp/cloud-demo/{{ inventory_hostname }}/DEPLOYED
      register: deploy_status
      changed_when: false

    - name: Show deployment status
      debug:
        var: deploy_status.stdout_lines

- name: Configure database servers
  hosts: databases
  gather_facts: true

  tasks:
    - name: Create database config directory
      file:
        path: "/tmp/cloud-demo/{{ inventory_hostname }}/config"
        state: directory
        mode: '0755'

    - name: Generate database configuration
      copy:
        content: |
          # Database configuration
          # Host: {{ inventory_hostname }}
          # IP: {{ server_ip }}
          # Endpoint: {{ db_endpoint }}
          # Environment: {{ environment }}

          listen_addresses = '{{ server_ip }}'
          max_connections = {{ '200' if environment == 'production' else '50' }}
          shared_buffers = {{ '2GB' if environment == 'production' else '128MB' }}
        dest: "/tmp/cloud-demo/{{ inventory_hostname }}/config/postgresql.conf"
        mode: '0644'
```

**Step 5: Run the complete workflow**

```bash
cd ~/ansible-lab/cloud-demo

# Step 1: Terraform provisions (simulated)
echo "Terraform: Creating infrastructure..."

# Step 2: Generate inventory
python3 generate-inventory.py

# Step 3: Ansible configures
cd ansible
ansible-playbook -i inventory-generated.ini site.yml

# Step 4: Verify
echo "=== Deployment Results ==="
for host in web-0 web-1 web-2 db-0; do
  echo "--- $host ---"
  cat /tmp/cloud-demo/$host/DEPLOYED 2>/dev/null || echo "Not deployed"
done
```

---

## Exercises

### Exercise 1: Terraform Output Parsing
Write a Python script that takes Terraform JSON output (with mixed resource types: EC2, RDS, ElastiCache) and generates an Ansible inventory with appropriate groups, host variables, and group variables.

### Exercise 2: Dynamic Inventory Script
Write a custom dynamic inventory script in Python that reads from a JSON file (simulating a CMDB) and outputs inventory in the format Ansible expects. Test it with `ansible-inventory --list`.

### Exercise 3: Cloud Resource Playbook
Write a playbook that uses AWS modules to create: a security group, an S3 bucket, and an IAM role. Use check mode to verify what would be created without actually creating anything (requires AWS credentials).

### Exercise 4: End-to-End Simulation
Simulate a complete workflow: (a) Terraform creates 3 web servers and 1 database (use local files), (b) a script generates Ansible inventory from Terraform output, (c) Ansible configures all servers with appropriate roles, (d) Ansible runs a verification playbook to confirm everything is configured correctly.

### Exercise 5: Multi-Cloud Inventory
Create inventory configurations for AWS, Azure, and GCP using their respective dynamic inventory plugins. Even without cloud accounts, document the configuration and explain how each plugin discovers resources.

---

## Knowledge Check

### Question 1
What is the recommended pattern for integrating Terraform and Ansible?

<details>
<summary>Answer</summary>

The recommended pattern is: (1) Terraform provisions infrastructure and tags resources with metadata (role, environment, managed_by), (2) Ansible uses dynamic inventory plugins to discover resources based on those tags, (3) Ansible configures the discovered resources using roles and playbooks. This is preferred over Terraform's `local-exec` provisioner (which couples provisioning and configuration) and over manually maintaining inventory files (which become stale). The tag-based discovery approach is loosely coupled — Terraform and Ansible can run independently, and the inventory always reflects the current state of infrastructure. Alternative approaches include generating static inventory from Terraform output, which is simpler but requires re-generation when infrastructure changes.
</details>

### Question 2
Why should you generally use Terraform instead of Ansible for provisioning cloud resources?

<details>
<summary>Answer</summary>

Terraform is better for provisioning because: (1) it maintains state, so it knows what exists and can compute diffs — Ansible modules often lack this awareness and may try to create duplicates; (2) Terraform's plan shows exactly what will change before anything happens; (3) Terraform handles dependencies automatically (create VPC before subnet); (4) Terraform supports lifecycle management including destroy; (5) Terraform's provider ecosystem is specifically designed for cloud resource management. Ansible's cloud modules work but are procedural in nature — they execute tasks sequentially and do not maintain a state file, making it harder to manage the full lifecycle of cloud resources, handle updates, or perform destroy operations cleanly.
</details>

### Question 3
How does dynamic inventory work with AWS EC2?

<details>
<summary>Answer</summary>

The AWS EC2 dynamic inventory plugin (`amazon.aws.aws_ec2`) queries the EC2 API to discover running instances. You configure it with a YAML file specifying: regions to query, filters (tag values, instance state), how to group instances (by tags, instance type, VPC), and which attribute to use as the hostname (public IP, private IP, DNS name). When Ansible runs, the plugin makes API calls to AWS, receives the list of instances, organizes them into groups based on `keyed_groups`, and provides host variables from instance metadata. This means your inventory is always current — new instances appear automatically, terminated instances disappear, and group membership reflects the latest tags.
</details>

### Question 4
What are the security considerations when using Ansible with cloud providers?

<details>
<summary>Answer</summary>

Key security considerations: (1) never hardcode AWS credentials in playbooks — use environment variables, IAM instance profiles, or AWS SSO; (2) use IAM roles with least-privilege policies for Ansible operations; (3) encrypt sensitive variables with Ansible Vault (database passwords, API keys); (4) use SSH key-based authentication with passphrase-protected keys; (5) restrict SSH access using security groups (only from Ansible control machine); (6) audit Ansible operations with CloudTrail (AWS API calls) and SSH logging; (7) use separate AWS accounts or roles for different environments; (8) rotate credentials regularly; (9) in CI/CD, use OIDC or short-lived credentials rather than long-lived access keys.
</details>
