# Week 8, Day 1: Classes & Objects

## What You'll Learn
- What Object-Oriented Programming (OOP) is and why it matters
- The `class` keyword and how to define classes
- The `__init__` method (constructor)
- The `self` parameter
- Creating objects (instances)
- Instance attributes vs class attributes

## Why OOP for DevOps?

DevOps is full of "things" - servers, containers, deployments, pipelines,
configurations. OOP lets you model these as objects with properties and
behaviors, making your automation code organized and reusable.

## Defining a Class

```python
class Server:
    """Represents a server in our infrastructure."""

    def __init__(self, name, ip_address, role="web"):
        """Initialize a new Server.

        __init__ is the constructor - it runs when you create a new object.
        'self' refers to the instance being created.
        """
        self.name = name              # Instance attribute
        self.ip_address = ip_address  # Instance attribute
        self.role = role              # Instance attribute with default
        self.status = "stopped"       # Always starts stopped

# Create objects (instances)
web1 = Server("web-01", "10.0.1.10")
web2 = Server("web-02", "10.0.1.11")
db1 = Server("db-01", "10.0.2.10", role="database")

# Access attributes
print(web1.name)        # web-01
print(web1.ip_address)  # 10.0.1.10
print(web1.role)        # web
print(db1.role)         # database
print(web1.status)      # stopped
```

## Understanding self

`self` is a reference to the current instance. It's how each object
knows about its own data.

```python
class Container:
    def __init__(self, name, image):
        # self.name stores 'name' on THIS specific object
        self.name = name
        self.image = image
        self.running = False

# When we create two containers:
c1 = Container("web", "nginx:latest")
c2 = Container("api", "python:3.11")

# Each has its own data:
print(c1.name)  # web
print(c2.name)  # api
# self.name refers to different data for each object
```

## Adding Methods

Methods are functions that belong to a class:

```python
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

    def start(self):
        """Start the server."""
        self.status = "running"
        return f"{self.name} started"

    def stop(self):
        """Stop the server."""
        self.status = "stopped"
        return f"{self.name} stopped"

    def get_info(self):
        """Return server info as a dictionary."""
        return {
            "name": self.name,
            "ip": self.ip_address,
            "status": self.status
        }

# Use methods
server = Server("web-01", "10.0.1.10")
print(server.start())      # web-01 started
print(server.status)       # running
print(server.get_info())   # {"name": "web-01", "ip": "10.0.1.10", "status": "running"}
print(server.stop())       # web-01 stopped
```

## Class Attributes vs Instance Attributes

```python
class Server:
    # Class attribute - shared by ALL instances
    server_count = 0
    max_servers = 100

    def __init__(self, name, ip_address):
        # Instance attributes - unique to EACH instance
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

        # Modify class attribute
        Server.server_count += 1

# Class attributes are shared:
s1 = Server("web-01", "10.0.1.10")
s2 = Server("web-02", "10.0.1.11")
print(Server.server_count)  # 2  (shared across all instances)
print(s1.server_count)      # 2  (accessed through instance too)
```

## The __str__ Method

`__str__` controls what happens when you print an object:

```python
class Server:
    def __init__(self, name, ip_address, role="web"):
        self.name = name
        self.ip_address = ip_address
        self.role = role
        self.status = "stopped"

    def __str__(self):
        return f"Server({self.name}, {self.ip_address}, {self.role}, {self.status})"

server = Server("web-01", "10.0.1.10")
print(server)  # Server(web-01, 10.0.1.10, web, stopped)
```

## The __repr__ Method

`__repr__` is for developers - it should show how to recreate the object:

```python
class Server:
    def __init__(self, name, ip_address, role="web"):
        self.name = name
        self.ip_address = ip_address
        self.role = role

    def __repr__(self):
        return f'Server("{self.name}", "{self.ip_address}", role="{self.role}")'

server = Server("web-01", "10.0.1.10")
print(repr(server))  # Server("web-01", "10.0.1.10", role="web")
```

## Complete Example: Container Class

```python
class Container:
    """Represents a Docker container."""

    container_count = 0

    def __init__(self, name, image, ports=None):
        self.name = name
        self.image = image
        self.ports = ports or []
        self.status = "created"
        self.container_id = f"cnt_{Container.container_count:04d}"
        Container.container_count += 1

    def start(self):
        if self.status == "running":
            return f"{self.name} is already running"
        self.status = "running"
        return f"{self.name} started"

    def stop(self):
        if self.status != "running":
            return f"{self.name} is not running"
        self.status = "stopped"
        return f"{self.name} stopped"

    def get_info(self):
        return {
            "id": self.container_id,
            "name": self.name,
            "image": self.image,
            "status": self.status,
            "ports": self.ports
        }

    def __str__(self):
        return f"Container({self.name}, {self.image}, {self.status})"

# Usage
web = Container("web-app", "nginx:latest", ports=[80, 443])
api = Container("api-server", "python:3.11", ports=[8080])

print(web.start())           # web-app started
print(web.get_info())        # {...}
print(web)                   # Container(web-app, nginx:latest, running)
print(Container.container_count)  # 2
```

## DevOps Connection

OOP maps perfectly to DevOps concepts:
- **Server** class -> represents a physical or virtual server
- **Container** class -> represents a Docker container
- **Deployment** class -> represents a deployment process
- **Pipeline** class -> represents a CI/CD pipeline
- **Config** class -> represents configuration data

By modeling infrastructure as objects, you can:
- Write cleaner, more organized automation code
- Reuse patterns across different projects
- Build tools that other team members can easily understand
- Create libraries that scale with your infrastructure
