# Week 11, Day 7: Quiz Day - CI/CD & Infrastructure as Code

## Week 11 Cheat Sheet

### Git with Python (GitPython)
```python
from git import Repo
repo = Repo("/path")              # Open repo
repo.is_dirty()                   # Uncommitted changes?
repo.branches                     # List branches
repo.active_branch                # Current branch
repo.iter_commits("main", max_count=10)  # Commit history
commit.diff(other_commit)         # View diffs
repo.index.add(["file.py"])       # Stage files
repo.index.commit("message")      # Commit
```

### Jenkins API
```python
# Base endpoints
GET  /api/json                    # Server info
GET  /job/{name}/api/json         # Job details
POST /job/{name}/build            # Trigger build
GET  /job/{name}/{num}/api/json   # Build status
# Colors: blue=SUCCESS, red=FAILURE, *_anime=RUNNING, disabled=DISABLED
```

### GitHub Actions
```yaml
name: CI
on:
  push: {branches: [main]}
  pull_request: {branches: [main]}
  schedule: [{cron: "0 0 * * *"}]
  workflow_dispatch: {}
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix: {python-version: ["3.10", "3.11"]}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pytest
    needs: [build]             # Job dependencies
    if: github.ref == 'refs/heads/main'  # Conditional
```

### Jinja2 Templates
```python
from jinja2 import Template
t = Template("Hello {{ name }}!")
t.render(name="World")

# Loops:    {% for item in list %}...{% endfor %}
# Conditions: {% if x %}...{% elif y %}...{% else %}...{% endif %}
# Filters:  {{ var | upper }}, {{ var | default("x") }}
```

### Ansible
```yaml
# Inventory (INI):
[webservers]
web1 ansible_host=10.0.1.1

# Playbook:
- name: Setup
  hosts: webservers
  become: yes
  tasks:
    - name: Install
      apt: {name: nginx, state: present}
  handlers:
    - name: Restart nginx
      service: {name: nginx, state: restarted}
```

---

## Key Concepts Summary

| Topic | Key Takeaway |
|-------|-------------|
| GitPython | Programmatic Git operations via Repo object |
| Jenkins API | REST API + Basic Auth for CI/CD automation |
| GitHub Actions | YAML workflows with jobs, steps, matrix, artifacts |
| Jinja2 | Template engine for config generation |
| Ansible | Agentless automation with YAML playbooks |
| IaC | Infrastructure defined as code, version controlled |
