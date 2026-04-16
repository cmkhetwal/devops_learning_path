# Configuration Management Philosophy

## Why This Matters in DevOps

You have learned how to provision infrastructure with Terraform — creating servers, networks, and databases. But a freshly provisioned server is useless. It has no applications installed, no services configured, no users set up, no security hardening applied. The gap between "server exists" and "server is useful" is configuration management.

Before configuration management tools, sysadmins would SSH into servers one by one, running commands, editing files, and hoping they remembered every step. This approach fails catastrophically at scale. When you have 200 servers, you cannot SSH into each one. When you need to rotate a TLS certificate across your fleet, you need it done in minutes, not days. When you need to prove to auditors that every server meets security baselines, you need evidence, not promises.

Configuration management is how you turn a fleet of blank servers into a functioning, consistent, auditable, and reproducible infrastructure.

---

## Core Concepts

### What Is Configuration Management?

Configuration management is the practice of automating the setup, configuration, and ongoing maintenance of servers and systems. It ensures that every server is configured identically, every time, regardless of who or what set it up.

What it manages:
- **Packages**: Installing, updating, and removing software
- **Files**: Creating, modifying, and managing configuration files
- **Services**: Starting, stopping, enabling, and configuring daemons
- **Users and groups**: Creating accounts, setting permissions
- **Security**: Firewall rules, SSH configuration, audit policies
- **Monitoring**: Installing and configuring monitoring agents
- **Application deployment**: Deploying code, managing environments

### Why Manual Server Configuration Fails

**The snowflake server problem:**

```
Day 1:   Admin installs Apache 2.4.51 on Server A
Day 5:   Admin installs Apache 2.4.51 on Server B (forgets a module)
Day 30:  Security patch updates Apache to 2.4.52 on Server A only
Day 60:  New admin installs Apache 2.4.54 on Server C
Day 90:  Server A crashes, rebuild attempt fails (nobody remembers the config)

Result: Three servers running the same application with different
        Apache versions, different modules, different configurations.
        Nobody knows what the "correct" setup is anymore.
```

**Manual process at scale:**

```
Task: Rotate TLS certificate on all web servers

Manual approach:
  1. SSH to server 1, replace cert, reload nginx    → 5 minutes
  2. SSH to server 2, replace cert, reload nginx    → 5 minutes
  ...
  50. SSH to server 50, replace cert, reload nginx  → 5 minutes
  Total: 250 minutes (4+ hours), error-prone, inconsistent

With Ansible:
  1. Run: ansible-playbook rotate-certs.yml         → 5 minutes
  Total: 5 minutes, consistent, auditable, repeatable
```

### Push vs Pull Models

Configuration management tools use one of two models:

**Push model (Ansible):**
The control machine pushes configuration to target servers on demand.

```
Control Machine ──push──▶ Server A
                ──push──▶ Server B
                ──push──▶ Server C

Characteristics:
  - No agent required on target servers
  - Runs when you execute it (on-demand)
  - Uses SSH for communication
  - Simple architecture
  - You control exactly when changes happen
```

**Pull model (Puppet, Chef):**
An agent on each server periodically pulls its configuration from a central server.

```
Server A (agent) ──pull──▶ Config Server
Server B (agent) ──pull──▶ Config Server
Server C (agent) ──pull──▶ Config Server

Characteristics:
  - Agent software required on every server
  - Runs on a schedule (every 30 minutes by default)
  - Continuously enforces desired state
  - More complex architecture (server + agents + certificates)
  - Self-healing (drift is corrected automatically)
```

**Comparison:**

| Aspect | Push (Ansible) | Pull (Puppet/Chef) |
|--------|---------------|-------------------|
| Agent required | No | Yes |
| Communication | SSH | Agent → Server (HTTPS) |
| When it runs | On-demand | Scheduled (every N minutes) |
| Drift correction | Manual re-run | Automatic |
| Complexity | Lower | Higher |
| Setup time | Minutes | Hours/days |
| Learning curve | Lower (YAML) | Higher (DSL/Ruby) |
| Scale ceiling | ~5000 nodes | ~50000 nodes |

### Agentless Architecture (Ansible's Advantage)

Ansible's agentless approach means:

```
Requirements on managed servers:
  - SSH access (already exists on every Linux server)
  - Python (already installed on most Linux distributions)
  - That is it. No agent to install, configure, update, or monitor.

Requirements on control machine:
  - Ansible installed (pip install ansible)
  - SSH key access to managed servers
  - Inventory file listing your servers
```

This is why Ansible adoption is so rapid. There is nothing to install on your servers. If you can SSH to it, you can manage it with Ansible.

### Idempotency in Configuration Management

Just like Terraform, configuration management must be idempotent — running the same configuration multiple times should produce the same result.

```yaml
# Idempotent: Ansible checks if nginx is installed before installing
- name: Install nginx
  apt:
    name: nginx
    state: present
# Run 1: nginx not installed → installs nginx → changed
# Run 2: nginx already installed → does nothing → ok
# Run 3: nginx already installed → does nothing → ok

# NOT idempotent: shell commands
- name: Add config line
  shell: echo "server_name example.com;" >> /etc/nginx/conf.d/default.conf
# Run 1: adds the line → changed
# Run 2: adds the line AGAIN (duplicate!) → changed
# Run 3: adds the line AGAIN (triple!) → changed
```

This is why Ansible provides modules instead of raw shell commands. The `apt` module knows how to check if a package is installed. The `lineinfile` module knows how to check if a line exists. The `template` module knows how to check if a file matches. Use modules, not shell commands.

### Desired State Configuration

Configuration management tools work by defining the desired state — what you want, not how to get there:

```yaml
# Desired state: I want nginx installed, configured, and running
- name: Ensure nginx is installed
  apt:
    name: nginx
    state: present        # "I want this package to exist"

- name: Ensure nginx config exists
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'          # "I want this file with these contents and permissions"

- name: Ensure nginx is running
  service:
    name: nginx
    state: started        # "I want this service running"
    enabled: true         # "I want this service to start on boot"
```

Ansible determines the current state, compares it to the desired state, and makes only the changes needed to reach the desired state. If the system already matches, nothing happens.

### Convergence

Convergence is the process of bringing a system from its current state to the desired state. Each run of a configuration management tool moves the system closer to (or maintains) the desired state.

```
Run 1: Server is blank
  → Install packages  (changed)
  → Create configs    (changed)
  → Start services    (changed)
  → 3 changes

Run 2: Server is configured
  → Check packages    (ok)
  → Check configs     (ok)
  → Check services    (ok)
  → 0 changes (converged!)

Run 3: Someone manually changed a config
  → Check packages    (ok)
  → Fix config        (changed - drift corrected)
  → Restart service   (changed - because config changed)
  → 2 changes (re-converged)
```

A system is "converged" when the actual state matches the desired state. A well-written playbook should show zero changes on a second run.

### When to Use Ansible vs Terraform

This is a critical distinction:

```
Terraform: PROVISIONING (creating infrastructure)
  → Create a server
  → Create a network
  → Create a database
  → Create a load balancer
  "What infrastructure exists?"

Ansible: CONFIGURATION (setting up infrastructure)
  → Install packages on a server
  → Configure services
  → Deploy application code
  → Manage users and permissions
  "How is the infrastructure configured?"

The workflow:
  1. Terraform creates an EC2 instance
  2. Ansible configures the EC2 instance (installs software, deploys app)

They complement each other, not compete.
```

| Question | Use Terraform | Use Ansible |
|----------|--------------|-------------|
| Create a VPC? | Yes | No |
| Install nginx? | No | Yes |
| Create an EC2 instance? | Yes | Possible, but Terraform is better |
| Configure nginx? | No | Yes |
| Create an S3 bucket? | Yes | Possible, but Terraform is better |
| Deploy application code? | No | Yes |
| Create a database? | Yes | No |
| Set up database users? | No | Yes |

---

## Step-by-Step Practical

### Mapping the Configuration Management Workflow

```
1. Write inventory (list of servers)
   ┌─────────────────────────────┐
   │ [webservers]                │
   │ web1.example.com            │
   │ web2.example.com            │
   │                             │
   │ [databases]                 │
   │ db1.example.com             │
   └─────────────────────────────┘

2. Write playbook (desired configuration)
   ┌─────────────────────────────┐
   │ - hosts: webservers         │
   │   tasks:                    │
   │     - install nginx         │
   │     - configure nginx       │
   │     - start nginx           │
   └─────────────────────────────┘

3. Run playbook
   $ ansible-playbook -i inventory site.yml

4. Ansible connects to each server via SSH
   Control Machine ──SSH──▶ web1 ──▶ runs tasks
                   ──SSH──▶ web2 ──▶ runs tasks

5. Ansible reports results
   web1: ok=3  changed=3  failed=0
   web2: ok=3  changed=3  failed=0
```

### Understanding the Tool Ecosystem

```
Era 1: Shell Scripts (2000s)
  - Custom bash scripts per server
  - Worked for 1-5 servers
  - Broke at scale

Era 2: CFEngine (2003) / Puppet (2005) / Chef (2009)
  - First-generation config management
  - Pull-based, agent-required
  - Domain-specific languages
  - Complex setup but powerful

Era 3: Ansible (2012) / Salt (2011)
  - Second-generation
  - Ansible: agentless, YAML, push-based
  - Salt: both push and pull, Python
  - Simpler setup, faster adoption

Era 4: Containers + Immutable (2013+)
  - Docker + Kubernetes
  - Build once, run anywhere
  - Configuration baked into images
  - Less need for traditional config management

Today's Reality:
  - Containers for stateless application servers
  - Ansible for configuring infrastructure that cannot be containerized
    (databases, legacy systems, network devices, bare metal)
  - Terraform for provisioning
  - All three working together
```

### Decision Framework: Do You Need Ansible?

```
Is the server containerized?
  ├── Yes → Dockerfile handles configuration, Ansible not needed
  └── No
      ├── Is it a one-time setup?
      │   ├── Yes → Ansible playbook (or even a shell script)
      │   └── No → Ansible with regular re-runs (drift correction)
      │
      ├── Is it a cloud VM?
      │   ├── Yes → Terraform creates it, Ansible configures it
      │   └── No (bare metal / on-prem)
      │       └── Ansible is the primary tool
      │
      └── Does it need ongoing configuration management?
          ├── Yes → Ansible with scheduled runs or Puppet/Chef
          └── No → Ansible as one-time provisioner
```

---

## Exercises

### Exercise 1: Manual Configuration Audit
Document the steps to manually set up a web server from scratch (install OS packages, configure nginx, set up firewall, create users, deploy an application). Count the steps. Estimate how long it would take. Now estimate the error rate if 3 different people did this independently.

### Exercise 2: Push vs Pull Analysis
For each of the following scenarios, determine whether push (Ansible) or pull (Puppet) would be more appropriate and explain why: (a) 10 web servers that rarely change configuration, (b) 5000 servers that must enforce security baselines continuously, (c) a fleet of developer workstations, (d) network devices (routers, switches) that do not support agents.

### Exercise 3: Tool Boundary Mapping
For a typical web application deployment, list 15 infrastructure tasks and categorize each as "Terraform," "Ansible," "Dockerfile," or "Kubernetes manifest." Justify each categorization.

### Exercise 4: Idempotency Testing
Write a bash script that installs nginx and configures a virtual host. Run it twice and identify what breaks (duplicate config entries, errors on existing packages, etc.). Then describe how Ansible modules would handle each step idempotently.

### Exercise 5: Migration Planning
Your company has 50 servers managed by a combination of shell scripts and manual SSH sessions. Create a migration plan to move to Ansible. Address: which servers to start with, how to build the inventory, how to test playbooks safely, and how to handle the transition period.

---

## Knowledge Check

### Question 1
What is the fundamental difference between the push and pull models of configuration management?

<details>
<summary>Answer</summary>

In the push model (Ansible), a control machine initiates connections to target servers and pushes configuration changes on demand. The operator decides when to run it. In the pull model (Puppet, Chef), an agent running on each server periodically connects to a central server and pulls its configuration, typically every 30 minutes. Push is simpler (no agent, on-demand) but does not self-heal drift automatically. Pull is more complex (agents, certificates, central server) but continuously enforces the desired state without human intervention. Push requires SSH access from the control machine; pull requires the agent to reach the central server.
</details>

### Question 2
Why is Ansible's agentless architecture significant?

<details>
<summary>Answer</summary>

Ansible's agentless architecture is significant because: (1) there is nothing to install on managed servers — if you can SSH to it and it has Python, you can manage it, reducing setup time from hours to minutes; (2) no agent means no agent to update, secure, monitor, or troubleshoot across your fleet; (3) it works with devices that cannot run agents (network devices, IoT, minimal embedded systems) via SSH or API; (4) there is no persistent service consuming resources on managed hosts; (5) there is no central server infrastructure to maintain (no Puppet Server, no Chef Server). The tradeoff is that Ansible does not continuously enforce state — you must run it (manually or via cron/CI) to detect and correct drift.
</details>

### Question 3
When should you use Terraform versus Ansible?

<details>
<summary>Answer</summary>

Use Terraform for provisioning infrastructure — creating, modifying, and destroying cloud resources like VPCs, EC2 instances, S3 buckets, databases, and load balancers. Use Ansible for configuring infrastructure — installing packages, deploying applications, managing configuration files, creating users, and setting up services on existing servers. The typical workflow is: Terraform creates the server, Ansible configures it. While there is overlap (Ansible can create cloud resources, Terraform can run provisioners), each tool excels in its domain. Terraform has superior state management for infrastructure lifecycle; Ansible has superior module library for server configuration. Using both together gives you the best of both worlds.
</details>

### Question 4
What does "idempotent" mean in the context of configuration management, and why does it matter?

<details>
<summary>Answer</summary>

An idempotent operation produces the same result whether you run it once or a hundred times. In configuration management, this means running a playbook on an already-configured server makes zero changes. It matters because: (1) you can safely re-run playbooks without fear of breaking things (duplicate entries, failed installs), (2) you can use regular scheduled runs to detect and correct configuration drift, (3) interrupted runs can be safely retried, (4) you can verify compliance by running the playbook in check mode — zero changes means the server is compliant. Ansible modules (apt, template, service) are idempotent by design. Shell/command modules are NOT idempotent, which is why they should be avoided when a module exists for the task.
</details>

### Question 5
Is Ansible still relevant in the age of containers and Kubernetes?

<details>
<summary>Answer</summary>

Yes, but its role has narrowed. For stateless applications, Docker and Kubernetes have largely replaced Ansible for application deployment and configuration (configuration is baked into container images via Dockerfiles). However, Ansible remains essential for: (1) configuring the infrastructure that runs containers (Kubernetes nodes, Docker hosts), (2) managing stateful systems that cannot be containerized (databases, legacy applications, mainframes), (3) managing network devices (routers, switches, firewalls), (4) bare-metal server provisioning, (5) initial setup of cloud VMs before they join a Kubernetes cluster, (6) organizations that are not yet containerized. Ansible's role has shifted from "configure everything" to "configure the things that containers cannot."
</details>
