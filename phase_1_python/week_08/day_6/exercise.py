"""
Week 8, Day 6: Practice Day - OOP Mini-Projects

Build 5 mini-projects combining everything from Week 8.

DevOps Context: These projects model real infrastructure management
patterns used in production DevOps environments.
"""

# ===========================================================
# PROJECT 1: ServerManager Class
# ===========================================================
# Create a ServerManager that manages a fleet of servers.
#
# Inner class (or just define before ServerManager):
#   Server: name (str), ip (str), role (str, default "web"),
#     status starts as "stopped".
#     Methods: start(), stop(), __str__()
#
# ServerManager:
#   Constructor: self.servers = {} (name -> Server)
#   Methods:
#     - add_server(name, ip, role="web"): create Server, add to dict.
#       Return "Added {name}". If name exists, return "{name} already exists".
#     - remove_server(name): remove from dict.
#       Return "Removed {name}" or "{name} not found".
#     - start_server(name): start specific server.
#       Return start() result or "{name} not found".
#     - stop_server(name): stop specific server. Same pattern.
#     - start_all(): start all servers, return count started.
#     - stop_all(): stop all servers, return count stopped.
#     - get_status(): return dict:
#       {"total": int, "running": int, "stopped": int,
#        "servers": {name: status for each server}}
#     - get_servers_by_role(role): return list of server names with that role.

class Server:
    # YOUR CODE HERE
    pass

class ServerManager:
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 2: DeploymentPipeline Class
# ===========================================================
# Create a deployment pipeline that runs stages in order.
#
# Stage class:
#   __init__(self, name, action):
#     - name (str), action (callable that returns True/False)
#     - self.status = "pending"
#     - self.result = None
#   run(): call self.action(), store result, set status to
#     "passed" if True, "failed" if False.
#     Return self.status.
#
# DeploymentPipeline:
#   __init__(self, name):
#     - self.name, self.stages = [], self.status = "pending"
#   add_stage(name, action): create Stage, append to stages.
#     Return "Stage '{name}' added"
#   run(): run stages in order. If a stage fails, stop and set
#     pipeline status to "failed". If all pass, set to "completed".
#     Return dict: {"pipeline": name, "status": status,
#       "stages_run": number run, "stages_total": total,
#       "failed_stage": name of failed stage or None}
#   get_report(): return list of dicts for each stage:
#     [{"name": str, "status": str}, ...]

class Stage:
    # YOUR CODE HERE
    pass

class DeploymentPipeline:
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 3: ConfigManager with Inheritance
# ===========================================================
# Create a base ConfigManager and specialized config managers.
#
# ConfigManager (base):
#   __init__(self): self._config = {}
#   set(key, value): store in _config. Return "Set {key}"
#   get(key, default=None): return value or default.
#   delete(key): remove from _config. Return "Deleted {key}" or
#     "{key} not found".
#   get_all(): return a copy of _config dict.
#   has(key): return True/False.
#   count(): return number of keys.
#
# EnvironmentConfig(ConfigManager):
#   __init__(self, env_name): call super, self.env_name = env_name
#   set(key, value): prefix key with env_name + "."
#     e.g., env_name="prod", key="port" -> stores "prod.port"
#     Call super().set() with prefixed key.
#   get(key, default=None): prefix key, call super().get()
#   get_env_keys(): return list of keys that start with env_name
#
# SecureConfig(ConfigManager):
#   __init__(self): call super, self._secrets = set()
#   set_secret(key, value): store in _config AND add key to _secrets.
#     Return "Secret {key} set"
#   get(key, default=None): if key in _secrets, return "***REDACTED***"
#     Otherwise return normal value.
#   get_real(key, default=None): return actual value even for secrets.
#     Use super().get(key, default).
#   list_secrets(): return sorted list of secret key names.

class ConfigManager:
    # YOUR CODE HERE
    pass

class EnvironmentConfig(ConfigManager):
    # YOUR CODE HERE
    pass

class SecureConfig(ConfigManager):
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 4: Test Suite (write test functions)
# ===========================================================
# Write test functions for the classes above.
# Each function should use assert statements.
# Return "all tests passed" if everything works.
#
# test_server_manager(): Test add, start, stop, get_status.
#   At least 5 assertions.
#
# test_deployment_pipeline(): Test add_stage, run with passing
#   and failing stages. At least 5 assertions.
#
# test_config_manager(): Test set, get, delete, has, count.
#   At least 5 assertions.

def test_server_manager():
    # YOUR CODE HERE - write assertions, return "all tests passed"
    pass

def test_deployment_pipeline():
    # YOUR CODE HERE - write assertions, return "all tests passed"
    pass

def test_config_manager():
    # YOUR CODE HERE - write assertions, return "all tests passed"
    pass


# ===========================================================
# PROJECT 5: Mini-Project Registry
# ===========================================================
# Create a ProjectRegistry class that tracks all components
# in a mini DevOps project.
#
# __init__(self, project_name):
#   - self.project_name
#   - self.components = {} (type -> list of names)
#     types: "server", "pipeline", "config"
#   - self.created_at = "2024-01-01" (just a placeholder string)
#
# Methods:
#   - register(component_type, name): add name to components[type].
#     Create the list if type doesn't exist.
#     Return "Registered {name} as {component_type}"
#   - unregister(component_type, name): remove name from list.
#     Return "Unregistered {name}" or "{name} not found"
#   - list_components(component_type=None): if type given, return
#     list of names for that type. If None, return all components
#     dict (copy).
#   - get_summary(): return dict:
#     {"project": project_name, "total_components": int (total across all types),
#      "component_types": sorted list of types,
#      "breakdown": {type: count for each type}}
#   - __str__(): return "Project({project_name}: {total} components)"

class ProjectRegistry:
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Project 1
    print("=== Project 1: ServerManager ===")
    mgr = ServerManager()
    mgr.add_server("web-01", "10.0.1.10")
    mgr.add_server("web-02", "10.0.1.11")
    mgr.add_server("db-01", "10.0.2.10", role="database")
    mgr.start_all()
    print(mgr.get_status())
    print()

    # Project 2
    print("=== Project 2: DeploymentPipeline ===")
    pipe = DeploymentPipeline("deploy-v2")
    pipe.add_stage("build", lambda: True)
    pipe.add_stage("test", lambda: True)
    pipe.add_stage("deploy", lambda: True)
    print(pipe.run())
    print()

    # Project 3
    print("=== Project 3: ConfigManager ===")
    cfg = EnvironmentConfig("prod")
    cfg.set("port", 8080)
    cfg.set("host", "0.0.0.0")
    print(cfg.get("port"))
    print(cfg.get_all())
    sec = SecureConfig()
    sec.set("app_name", "myapp")
    sec.set_secret("db_password", "secret123")
    print(sec.get("app_name"), sec.get("db_password"))
    print()

    # Project 4
    print("=== Project 4: Tests ===")
    print(test_server_manager())
    print(test_deployment_pipeline())
    print(test_config_manager())
    print()

    # Project 5
    print("=== Project 5: ProjectRegistry ===")
    reg = ProjectRegistry("infra-tool")
    reg.register("server", "web-01")
    reg.register("server", "db-01")
    reg.register("pipeline", "deploy-v2")
    reg.register("config", "prod-config")
    print(reg.get_summary())
    print(reg)
