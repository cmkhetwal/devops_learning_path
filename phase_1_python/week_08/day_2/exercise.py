"""
Week 8, Day 2: Methods & Properties - Exercise

Practice instance methods, class methods, static methods, and properties.

DevOps Context: These patterns are used in every DevOps SDK and tool.
Building a Server class with proper methods and properties teaches
you how real infrastructure libraries work.
"""

# ===========================================================
# TASK 1: Enhanced Server Class with All Method Types
# ===========================================================
# Create a Server class with the following:
#
# Class attributes:
#   - _fleet (dict): stores all servers by name, starts as {}
#   - total_created (int): starts at 0
#
# Constructor (__init__):
#   - name (str), ip_address (str), role (str, default "web")
#   - Set self._status = "stopped"
#   - Set self._cpu_usage = 0.0
#   - Set self._memory_usage = 0.0
#   - Add self to Server._fleet[name]
#   - Increment Server.total_created
#
# Instance methods:
#   - start(): set _status to "running", return "{name} started"
#   - stop(): set _status to "stopped", set _cpu_usage and _memory_usage to 0.0
#     return "{name} stopped"
#   - health_check(): return dict with "name", "status", "healthy"
#     healthy is True if status=="running" and cpu < 90 and memory < 90
#
# Class methods:
#   - from_config(cls, config): create from dict {"name":..., "ip":..., "role":...}
#     role defaults to "web" if missing
#   - get_fleet(cls): return dict of all servers {name: server_obj}
#   - find(cls, name): return server from _fleet by name or None
#   - fleet_size(cls): return number of servers in _fleet
#
# Static methods:
#   - validate_ip(ip_address): return True if valid IPv4 format
#     (4 dot-separated numbers, each 0-255)
#   - generate_name(role, number): return "{role}-{number:02d}"
#     e.g., generate_name("web", 3) -> "web-03"
#
# Properties:
#   - status (getter only): return self._status
#   - cpu_usage (getter + setter): setter validates 0-100, raises ValueError
#   - memory_usage (getter + setter): setter validates 0-100, raises ValueError
#   - is_healthy (getter only, computed): True if running and cpu<90 and mem<90

class Server:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Container Class with Factory Methods
# ===========================================================
# Create a Container class with:
#
# Class attributes:
#   - _all_containers (list): starts as []
#
# Constructor:
#   - name (str), image (str), tag (str, default "latest")
#   - self._status = "created"
#   - self._ports = []
#   - Append self to Container._all_containers
#
# Instance methods:
#   - start(): set _status to "running", return "{name} started"
#   - stop(): set _status to "stopped", return "{name} stopped"
#   - add_port(port): append port to _ports, return "Port {port} added to {name}"
#
# Class methods:
#   - from_image_string(cls, image_string): parse "image:tag" string.
#     Name is auto-generated as image name (before colon) with tag.
#     e.g., "nginx:1.25" -> Container("nginx-1.25", "nginx", "1.25")
#     If no colon, use "latest" as tag.
#   - get_all(cls): return list of all containers
#   - running_count(cls): return count of containers with status "running"
#
# Static methods:
#   - validate_image(image_string): return True if format is "name:tag"
#     where both name and tag are non-empty. "nginx:latest" -> True.
#     "nginx" -> False (no tag). ":latest" -> False (no name).
#
# Properties:
#   - status (getter only)
#   - ports (getter only): return a copy of _ports list
#   - full_image (getter only, computed): return "{image}:{tag}"

class Container:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: Metrics Collector with Properties
# ===========================================================
# Create a MetricsCollector class for server monitoring.
#
# Constructor:
#   - server_name (str)
#   - Set self._metrics = [] (list of float values)
#   - Set self._threshold = 80.0
#
# Instance methods:
#   - add_metric(value): append float value to _metrics.
#     Return "Metric added: {value}"
#   - clear(): reset _metrics to empty list. Return "Metrics cleared"
#
# Properties:
#   - threshold (getter + setter): setter must validate > 0 and <= 100
#     Raise ValueError if invalid.
#   - count (getter only): return len(_metrics)
#   - average (getter only): return average of _metrics rounded to 2 places.
#     Return 0.0 if no metrics.
#   - maximum (getter only): return max of _metrics. Return 0.0 if empty.
#   - minimum (getter only): return min of _metrics. Return 0.0 if empty.
#   - above_threshold (getter only): return list of metrics > self._threshold
#   - alert_status (getter only, computed):
#     "critical" if average > threshold
#     "warning" if any metric > threshold but average <= threshold
#     "ok" otherwise

class MetricsCollector:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: ConfigEntry with Validation Properties
# ===========================================================
# Create a ConfigEntry class for managing configuration settings.
#
# Constructor:
#   - key (str): config key
#   - value: the config value (any type)
#   - config_type (str): one of "string", "integer", "boolean", "list"
#
# Properties:
#   - key (getter only): return self._key
#   - value (getter + setter): setter must validate against config_type:
#     "string" -> must be str
#     "integer" -> must be int
#     "boolean" -> must be bool
#     "list" -> must be list
#     Raise TypeError with message "Expected {config_type}, got {actual_type}"
#     where actual_type is type(value).__name__
#   - config_type (getter only)
#   - as_string (getter only): convert value to string representation
#     string -> return value as-is
#     integer -> return str(value)
#     boolean -> return "true" or "false" (lowercase)
#     list -> return comma-joined string, e.g., "a,b,c"
#
# Instance methods:
#   - to_dict(): return {"key": key, "value": value, "type": config_type}
#   - __str__(): return "{key}={as_string}"

class ConfigEntry:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: ServiceMonitor with All Method Types
# ===========================================================
# Create a ServiceMonitor class.
#
# Class attributes:
#   - _monitors (dict): stores all monitors by service_name, starts as {}
#
# Constructor:
#   - service_name (str), port (int), protocol (str, default "http")
#   - self._checks = [] (list of bools: True=up, False=down)
#   - Store self in ServiceMonitor._monitors[service_name]
#
# Instance methods:
#   - record_check(is_up): append bool to _checks. Return "Check recorded"
#   - get_report(): return dict with "service_name", "port", "protocol",
#     "total_checks", "uptime_percent" (rounded to 1), "last_status"
#     uptime_percent = (true_count / total * 100) or 0.0 if no checks
#     last_status = "up" or "down" based on last check, or "unknown"
#
# Class methods:
#   - get_all_monitors(cls): return dict of all monitors
#   - get_monitor(cls, name): return monitor by service_name or None
#
# Static methods:
#   - is_valid_port(port): return True if port is int and 1 <= port <= 65535
#
# Properties:
#   - uptime_percent (getter only): calculated from _checks
#   - is_up (getter only): True if last check was True, False otherwise.
#     Return False if no checks recorded.
#   - total_checks (getter only): return len of _checks

class ServiceMonitor:
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Task 1
    Server._fleet = {}
    Server.total_created = 0
    s = Server("web-01", "10.0.1.10")
    s.start()
    s.cpu_usage = 45.0
    print("Task 1:", s.health_check())
    print("Task 1:", Server.validate_ip("10.0.1.10"))
    print("Task 1:", Server.generate_name("web", 5))
    s2 = Server.from_config({"name": "db-01", "ip": "10.0.2.10", "role": "database"})
    print("Task 1:", Server.fleet_size())
    print()

    # Task 2
    Container._all_containers = []
    c = Container("web", "nginx", "1.25")
    c.start()
    print("Task 2:", c.full_image)
    c2 = Container.from_image_string("redis:7")
    print("Task 2:", c2.name, c2.full_image)
    print("Task 2:", Container.validate_image("nginx:latest"))
    print()

    # Task 3
    m = MetricsCollector("web-01")
    for v in [45.0, 62.0, 85.0, 91.0, 30.0]:
        m.add_metric(v)
    print("Task 3:", m.average, m.maximum, m.alert_status)
    print()

    # Task 4
    cfg = ConfigEntry("max_workers", 4, "integer")
    print("Task 4:", cfg.to_dict())
    print("Task 4:", str(cfg))
    print()

    # Task 5
    ServiceMonitor._monitors = {}
    mon = ServiceMonitor("nginx", 80)
    mon.record_check(True)
    mon.record_check(True)
    mon.record_check(False)
    print("Task 5:", mon.get_report())
