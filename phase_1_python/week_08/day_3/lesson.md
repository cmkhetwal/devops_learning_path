# Week 8, Day 3: Inheritance

## What You'll Learn
- What inheritance is and why it matters
- Parent (base) and child (derived) classes
- The `super()` function
- Method overriding
- `isinstance()` and `issubclass()`
- Building class hierarchies for DevOps

## What is Inheritance?

Inheritance lets you create new classes based on existing ones. The child
class gets all methods and attributes from the parent, and can add or
override them.

```
          Server (parent/base)
         /       \
   WebServer    DatabaseServer (children/derived)
```

## Basic Inheritance

```python
class Server:
    """Base class for all servers."""

    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

    def start(self):
        self.status = "running"
        return f"{self.name} started"

    def stop(self):
        self.status = "stopped"
        return f"{self.name} stopped"

    def get_info(self):
        return {
            "name": self.name,
            "ip": self.ip_address,
            "status": self.status,
            "type": "generic"
        }


class WebServer(Server):
    """Web server - inherits everything from Server."""

    def __init__(self, name, ip_address, web_root="/var/www/html"):
        # Call parent __init__ first
        super().__init__(name, ip_address)
        # Add new attributes specific to WebServer
        self.web_root = web_root
        self.sites = []

    def add_site(self, site_name):
        """New method - only WebServer has this."""
        self.sites.append(site_name)
        return f"Added site {site_name}"

    def get_info(self):
        """Override parent method - add more info."""
        info = super().get_info()  # Get parent's info first
        info["type"] = "web"
        info["web_root"] = self.web_root
        info["sites"] = self.sites
        return info


# Usage
web = WebServer("web-01", "10.0.1.10")
print(web.start())      # "web-01 started" (inherited from Server)
web.add_site("example.com")  # New method
print(web.get_info())   # Overridden - includes web_root and sites
```

## The super() Function

`super()` calls the parent class's method. It's essential for:
1. Calling the parent's `__init__` to set up base attributes
2. Extending (not replacing) parent methods

```python
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

    def start(self):
        self.status = "running"
        return f"{self.name} started"


class DatabaseServer(Server):
    def __init__(self, name, ip_address, db_engine="postgresql", port=5432):
        super().__init__(name, ip_address)  # Call Server.__init__
        self.db_engine = db_engine
        self.port = port
        self.connections = 0

    def start(self):
        # Call parent start() first, then add extra behavior
        result = super().start()
        self.connections = 0
        return f"{result} (engine: {self.db_engine}, port: {self.port})"

db = DatabaseServer("db-01", "10.0.2.10")
print(db.start())
# "db-01 started (engine: postgresql, port: 5432)"
print(db.name)        # "db-01" (from parent)
print(db.db_engine)   # "postgresql" (from child)
```

## Method Overriding

When a child class defines a method with the same name as the parent,
it overrides the parent's version:

```python
class Server:
    def describe(self):
        return f"Generic server: {self.name}"

class WebServer(Server):
    def describe(self):
        # This REPLACES the parent's describe()
        return f"Web server: {self.name} serving {len(self.sites)} sites"

class DatabaseServer(Server):
    def describe(self):
        return f"Database server: {self.name} ({self.db_engine})"
```

## isinstance() and issubclass()

```python
web = WebServer("web-01", "10.0.1.10")
db = DatabaseServer("db-01", "10.0.2.10")

# isinstance checks if an object is an instance of a class
print(isinstance(web, WebServer))   # True
print(isinstance(web, Server))      # True (it's also a Server!)
print(isinstance(web, DatabaseServer))  # False

# issubclass checks class relationships
print(issubclass(WebServer, Server))       # True
print(issubclass(DatabaseServer, Server))  # True
print(issubclass(Server, WebServer))       # False
```

## Complete Hierarchy Example

```python
class Server:
    """Base server class."""

    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"
        self._logs = []

    def start(self):
        self.status = "running"
        self._log(f"{self.name} started")
        return f"{self.name} started"

    def stop(self):
        self.status = "stopped"
        self._log(f"{self.name} stopped")
        return f"{self.name} stopped"

    def _log(self, message):
        self._logs.append(message)

    def get_logs(self):
        return list(self._logs)

    def get_type(self):
        return "generic"

    def __str__(self):
        return f"{self.get_type().title()}Server({self.name})"


class WebServer(Server):
    def __init__(self, name, ip_address, port=80):
        super().__init__(name, ip_address)
        self.port = port
        self.sites = []

    def deploy_site(self, site):
        self.sites.append(site)
        self._log(f"Deployed {site}")
        return f"Deployed {site} to {self.name}"

    def get_type(self):
        return "web"


class DatabaseServer(Server):
    def __init__(self, name, ip_address, engine="postgresql", port=5432):
        super().__init__(name, ip_address)
        self.engine = engine
        self.port = port
        self.databases = []

    def create_database(self, db_name):
        self.databases.append(db_name)
        self._log(f"Created database {db_name}")
        return f"Created {db_name} on {self.name}"

    def get_type(self):
        return "database"


class CacheServer(Server):
    def __init__(self, name, ip_address, engine="redis", port=6379):
        super().__init__(name, ip_address)
        self.engine = engine
        self.port = port
        self._cache = {}

    def set_key(self, key, value):
        self._cache[key] = value
        return f"Set {key}"

    def get_key(self, key):
        return self._cache.get(key)

    def get_type(self):
        return "cache"


# Polymorphism - treat all servers the same way:
servers = [
    WebServer("web-01", "10.0.1.10"),
    DatabaseServer("db-01", "10.0.2.10"),
    CacheServer("cache-01", "10.0.3.10"),
]

for server in servers:
    print(server.start())     # All have start() from parent
    print(server.get_type())  # Each returns its own type
    print(server)             # Each has its own __str__ via get_type()
```

## DevOps Connection

Inheritance models real infrastructure hierarchies:
- **Server** -> **WebServer**, **DatabaseServer**, **CacheServer**
- **Deployment** -> **BlueGreenDeployment**, **CanaryDeployment**, **RollingDeployment**
- **Monitor** -> **HTTPMonitor**, **TCPMonitor**, **DNSMonitor**
- **Alert** -> **EmailAlert**, **SlackAlert**, **PagerDutyAlert**

This is how real DevOps tools work:
- Terraform providers inherit from a base provider class
- Ansible modules inherit from a base module class
- Kubernetes resource types share a common structure
