# Week 11, Day 4: Jinja2 Templates for DevOps

## What You'll Learn

- Jinja2 templating engine basics
- Variables, loops, conditions, and filters in templates
- Generating configuration files from templates
- Template inheritance and reuse

## Why This Matters for DevOps

Infrastructure configuration often follows patterns. Jinja2 lets you
write templates for nginx configs, Dockerfiles, Kubernetes manifests,
and more -- then generate environment-specific versions automatically.
Ansible, SaltStack, and many DevOps tools use Jinja2 natively.

---

## 1. Installing Jinja2

```bash
pip install jinja2
```

## 2. Basic Usage

```python
from jinja2 import Template

# Simple variable substitution
template = Template("Hello, {{ name }}!")
result = template.render(name="DevOps Engineer")
print(result)  # Hello, DevOps Engineer!
```

## 3. Variables and Filters

```python
from jinja2 import Template

t = Template("""
Server: {{ server_name | upper }}
Port: {{ port | default(8080) }}
Workers: {{ workers | default(4) }}
Debug: {{ debug | lower }}
""")

result = t.render(server_name="web-prod-01", port=443, debug="False")
print(result)
```

Common filters: `upper`, `lower`, `default`, `int`, `join`, `length`, `trim`

## 4. Loops

```python
from jinja2 import Template

t = Template("""
upstream backend {
{% for server in servers %}
    server {{ server.host }}:{{ server.port }} weight={{ server.weight }};
{% endfor %}
}
""")

servers = [
    {"host": "10.0.1.1", "port": 8080, "weight": 5},
    {"host": "10.0.1.2", "port": 8080, "weight": 3},
    {"host": "10.0.1.3", "port": 8080, "weight": 2},
]

print(t.render(servers=servers))
```

## 5. Conditions

```python
from jinja2 import Template

t = Template("""
server {
    listen {{ port }};
    server_name {{ domain }};

{% if ssl_enabled %}
    ssl_certificate /etc/ssl/{{ domain }}.crt;
    ssl_certificate_key /etc/ssl/{{ domain }}.key;
{% endif %}

{% if environment == "production" %}
    access_log /var/log/nginx/{{ domain }}.log;
{% else %}
    access_log /dev/stdout;
{% endif %}
}
""")

print(t.render(port=443, domain="example.com",
               ssl_enabled=True, environment="production"))
```

## 6. Using Environment for File-based Templates

```python
from jinja2 import Environment, FileSystemLoader

# Load templates from a directory
env = Environment(loader=FileSystemLoader("templates/"))
template = env.get_template("nginx.conf.j2")
result = template.render(domain="example.com", port=80)
```

## 7. Template Strings for Config Generation

```python
NGINX_TEMPLATE = """
server {
    listen {{ port }};
    server_name {{ server_name }};
    root {{ document_root }};

    location / {
        proxy_pass http://{{ upstream_host }}:{{ upstream_port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

{% for location in extra_locations %}
    location {{ location.path }} {
        {{ location.directive }};
    }
{% endfor %}
}
"""
```

## 8. Dockerfile Template

```python
DOCKERFILE_TEMPLATE = """
FROM {{ base_image }}:{{ tag }}

LABEL maintainer="{{ maintainer }}"

WORKDIR /app

{% if system_packages %}
RUN apt-get update && apt-get install -y \\
{% for pkg in system_packages %}
    {{ pkg }}{% if not loop.last %} \\{% endif %}

{% endfor %}
    && rm -rf /var/lib/apt/lists/*
{% endif %}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {{ port }}

CMD ["{{ cmd }}"]
"""
```

## 9. Kubernetes Manifest Template

```python
K8S_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
  namespace: {{ namespace }}
  labels:
    app: {{ app_name }}
    version: "{{ version }}"
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
        version: "{{ version }}"
    spec:
      containers:
      - name: {{ app_name }}
        image: {{ image }}:{{ version }}
        ports:
        - containerPort: {{ port }}
        resources:
          limits:
            cpu: "{{ cpu_limit }}"
            memory: "{{ memory_limit }}"
{% for env_var in env_vars %}
        env:
        - name: {{ env_var.name }}
          value: "{{ env_var.value }}"
{% endfor %}
"""
```

## DevOps Connection

Jinja2 templating is the backbone of:
- **Ansible**: All playbooks and roles use Jinja2 templates
- **Configuration management**: Generate env-specific configs from one template
- **Kubernetes**: Helm charts are essentially Jinja2 (Go templates, similar syntax)
- **Infrastructure as Code**: Generate Terraform files for multiple environments

---

## Key Takeaways

| Feature | Syntax |
|---------|--------|
| Variable | `{{ variable }}` |
| Filter | `{{ var \| upper }}` |
| For loop | `{% for item in list %}...{% endfor %}` |
| Condition | `{% if condition %}...{% endif %}` |
| Default | `{{ var \| default("fallback") }}` |
| Loop index | `{{ loop.index }}` (1-based) |
| Last item | `{{ loop.last }}` |
