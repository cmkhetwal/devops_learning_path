"""
Week 11, Day 3: Exercise - GitHub Actions Workflow Generator

Build functions that generate GitHub Actions workflow YAML files
as Python dictionaries (which can be serialized to YAML).

No external libraries needed -- we work with dicts and strings.

TASKS:
    1. generate_basic_ci()         - Basic CI workflow
    2. generate_python_test()      - Python testing with matrix
    3. generate_docker_build()     - Docker build and push workflow
    4. generate_deploy_workflow()  - Multi-stage deployment workflow
    5. generate_scheduled_job()    - Cron-based scheduled workflow
    6. workflow_to_yaml()          - Convert dict to YAML string
"""


# ============================================================
# TASK 1: generate_basic_ci(app_name, python_version="3.11")
#
# Return a dict representing a basic CI workflow:
# {
#   "name": "CI - {app_name}",
#   "on": {
#     "push": {"branches": ["main", "develop"]},
#     "pull_request": {"branches": ["main"]}
#   },
#   "jobs": {
#     "test": {
#       "runs-on": "ubuntu-latest",
#       "steps": [
#         {"uses": "actions/checkout@v4"},
#         {"name": "Set up Python",
#          "uses": "actions/setup-python@v5",
#          "with": {"python-version": python_version}},
#         {"name": "Install dependencies",
#          "run": "pip install -r requirements.txt"},
#         {"name": "Run linter",
#          "run": "pip install flake8 && flake8 ."},
#         {"name": "Run tests",
#          "run": "pytest tests/ -v"}
#       ]
#     }
#   }
# }
# ============================================================

def generate_basic_ci(app_name, python_version="3.11"):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: generate_python_test(app_name, python_versions, os_list=None)
#
# Generate a workflow with a matrix strategy.
# - python_versions: list like ["3.9", "3.10", "3.11"]
# - os_list: list like ["ubuntu-latest", "macos-latest"]
#            default to ["ubuntu-latest"] if None
#
# Return dict with:
# {
#   "name": "Tests - {app_name}",
#   "on": {"push": {"branches": ["main"]},
#          "pull_request": {"branches": ["main"]}},
#   "jobs": {
#     "test": {
#       "runs-on": "${{ matrix.os }}",
#       "strategy": {
#         "matrix": {
#           "python-version": python_versions,
#           "os": os_list
#         },
#         "fail-fast": False
#       },
#       "steps": [
#         {"uses": "actions/checkout@v4"},
#         {"name": "Set up Python ${{ matrix.python-version }}",
#          "uses": "actions/setup-python@v5",
#          "with": {"python-version": "${{ matrix.python-version }}"}},
#         {"name": "Install dependencies",
#          "run": "pip install -r requirements.txt"},
#         {"name": "Run tests",
#          "run": "pytest tests/ -v --tb=short"}
#       ]
#     }
#   }
# }
# ============================================================

def generate_python_test(app_name, python_versions, os_list=None):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: generate_docker_build(image_name, dockerfile="Dockerfile",
#                                registry="ghcr.io")
#
# Generate a Docker build and push workflow:
# {
#   "name": "Docker Build - {image_name}",
#   "on": {
#     "push": {"branches": ["main"],
#              "tags": ["v*"]},
#   },
#   "env": {
#     "REGISTRY": registry,
#     "IMAGE_NAME": image_name,
#   },
#   "jobs": {
#     "build-and-push": {
#       "runs-on": "ubuntu-latest",
#       "permissions": {"contents": "read", "packages": "write"},
#       "steps": [
#         {"uses": "actions/checkout@v4"},
#         {"name": "Log in to registry",
#          "uses": "docker/login-action@v3",
#          "with": {
#            "registry": "${{ env.REGISTRY }}",
#            "username": "${{ github.actor }}",
#            "password": "${{ secrets.GITHUB_TOKEN }}"}},
#         {"name": "Extract metadata",
#          "id": "meta",
#          "uses": "docker/metadata-action@v5",
#          "with": {
#            "images": "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}"}},
#         {"name": "Build and push",
#          "uses": "docker/build-push-action@v5",
#          "with": {
#            "context": ".",
#            "file": dockerfile,
#            "push": True,
#            "tags": "${{ steps.meta.outputs.tags }}",
#            "labels": "${{ steps.meta.outputs.labels }}"}}
#       ]
#     }
#   }
# }
# ============================================================

def generate_docker_build(image_name, dockerfile="Dockerfile", registry="ghcr.io"):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: generate_deploy_workflow(app_name, environments)
#
# Generate a multi-stage deployment workflow.
# environments is a list of dicts like:
#   [{"name": "staging", "url": "https://staging.example.com",
#     "auto": True},
#    {"name": "production", "url": "https://example.com",
#     "auto": False}]
#
# "auto": True means auto-deploy, False means manual approval
#         (use environment protection with the name)
#
# Return dict with:
# {
#   "name": "Deploy - {app_name}",
#   "on": {"push": {"branches": ["main"]}},
#   "jobs": {
#     "build": {
#       "runs-on": "ubuntu-latest",
#       "steps": [
#         {"uses": "actions/checkout@v4"},
#         {"name": "Build application", "run": "echo 'Building...'"},
#         {"name": "Upload artifact",
#          "uses": "actions/upload-artifact@v4",
#          "with": {"name": "app-build", "path": "dist/"}}
#       ]
#     },
#     "deploy-{env_name}": {   # for each environment
#       "needs": "build" (first env) or "deploy-{prev_env}" (others),
#       "runs-on": "ubuntu-latest",
#       "environment": {
#         "name": env_name,
#         "url": env_url
#       },
#       "steps": [
#         {"name": "Download artifact",
#          "uses": "actions/download-artifact@v4",
#          "with": {"name": "app-build"}},
#         {"name": "Deploy to {env_name}",
#          "run": "echo 'Deploying to {env_name}...'"}
#       ]
#     }
#   }
# }
#
# NOTE: Each deploy job "needs" the previous one (chained).
#       First deploy job needs "build".
# ============================================================

def generate_deploy_workflow(app_name, environments):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: generate_scheduled_job(job_name, cron_expr, script,
#                                 python_version="3.11")
#
# Generate a cron-scheduled workflow:
# {
#   "name": "Scheduled - {job_name}",
#   "on": {
#     "schedule": [{"cron": cron_expr}],
#     "workflow_dispatch": {}
#   },
#   "jobs": {
#     "run": {
#       "runs-on": "ubuntu-latest",
#       "steps": [
#         {"uses": "actions/checkout@v4"},
#         {"name": "Set up Python",
#          "uses": "actions/setup-python@v5",
#          "with": {"python-version": python_version}},
#         {"name": "Install dependencies",
#          "run": "pip install -r requirements.txt"},
#         {"name": "Run {job_name}",
#          "run": "python {script}"},
#       ]
#     }
#   }
# }
# ============================================================

def generate_scheduled_job(job_name, cron_expr, script, python_version="3.11"):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 6: workflow_to_yaml(workflow_dict)
#
# Convert a workflow dictionary to a YAML-formatted string.
# Do NOT use the yaml library. Build the string manually.
#
# Rules:
# - Top-level keys on their own line: "key:"
# - Nested dicts indent by 2 spaces per level
# - Lists use "- " prefix
# - Booleans: True -> "true", False -> "false"
# - Strings with special chars get quoted
# - This does NOT need to be perfect YAML -- just readable.
#
# Simplified approach: convert to a readable string format.
# At minimum, produce a string where:
#   - The "name" key and its value appear
#   - The "on" section and triggers appear
#   - The "jobs" section with job names appear
#   - Steps with "name" and "run"/"uses" appear
#
# Return the formatted string.
#
# HINT: Write a recursive helper function.
# ============================================================

def workflow_to_yaml(workflow_dict):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Task 1: Basic CI ===")
    ci = generate_basic_ci("my-webapp")
    if ci:
        print(f"  Name: {ci.get('name')}")
        print(f"  Jobs: {list(ci.get('jobs', {}).keys())}")

    print("\n=== Task 2: Matrix Test ===")
    matrix = generate_python_test("my-api", ["3.10", "3.11", "3.12"],
                                  ["ubuntu-latest", "macos-latest"])
    if matrix:
        strat = matrix.get("jobs", {}).get("test", {}).get("strategy", {})
        print(f"  Matrix: {strat.get('matrix', {})}")

    print("\n=== Task 3: Docker Build ===")
    docker = generate_docker_build("myorg/myapp")
    if docker:
        print(f"  Name: {docker.get('name')}")
        print(f"  Registry: {docker.get('env', {}).get('REGISTRY')}")

    print("\n=== Task 4: Deploy ===")
    envs = [
        {"name": "staging", "url": "https://staging.example.com", "auto": True},
        {"name": "production", "url": "https://example.com", "auto": False},
    ]
    deploy = generate_deploy_workflow("my-app", envs)
    if deploy:
        print(f"  Jobs: {list(deploy.get('jobs', {}).keys())}")

    print("\n=== Task 5: Scheduled ===")
    sched = generate_scheduled_job("health-check", "0 */6 * * *", "health_check.py")
    if sched:
        print(f"  Name: {sched.get('name')}")
        cron = sched.get("on", {}).get("schedule", [{}])[0].get("cron")
        print(f"  Cron: {cron}")

    print("\n=== Task 6: YAML Output ===")
    if ci:
        yaml_str = workflow_to_yaml(ci)
        if yaml_str:
            print(yaml_str[:500])
