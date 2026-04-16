# Week 8, Day 2: Methods & Properties

## What You'll Learn
- Instance methods (regular methods)
- Class methods (`@classmethod`)
- Static methods (`@staticmethod`)
- Properties (`@property`) for controlled attribute access
- When to use each type

## Instance Methods (Review)

Instance methods are the most common. They take `self` as the first
parameter and can access/modify instance data.

```python
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "stopped"

    def start(self):
        """Instance method - operates on self (this specific server)."""
        self.status = "running"
        return f"{self.name} started"

    def stop(self):
        self.status = "stopped"
        return f"{self.name} stopped"
```

## Class Methods (@classmethod)

Class methods take `cls` as the first parameter instead of `self`.
They can access and modify class-level data, and are often used as
alternative constructors.

```python
class Server:
    server_count = 0

    def __init__(self, name, ip_address, role="web"):
        self.name = name
        self.ip_address = ip_address
        self.role = role
        self.status = "stopped"
        Server.server_count += 1

    @classmethod
    def from_config(cls, config_dict):
        """Alternative constructor from a config dictionary."""
        return cls(
            name=config_dict["name"],
            ip_address=config_dict["ip"],
            role=config_dict.get("role", "web")
        )

    @classmethod
    def from_string(cls, server_string):
        """Alternative constructor from 'name:ip:role' string."""
        parts = server_string.split(":")
        name = parts[0]
        ip = parts[1]
        role = parts[2] if len(parts) > 2 else "web"
        return cls(name, ip, role)

    @classmethod
    def get_server_count(cls):
        """Access class-level data."""
        return cls.server_count

# Usage:
s1 = Server("web-01", "10.0.1.10")

# Alternative constructors
s2 = Server.from_config({"name": "web-02", "ip": "10.0.1.11"})
s3 = Server.from_string("db-01:10.0.2.10:database")

print(Server.get_server_count())  # 3
```

## Static Methods (@staticmethod)

Static methods don't take `self` or `cls`. They're utility functions
that logically belong to the class but don't need instance or class data.

```python
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address

    @staticmethod
    def validate_ip(ip_address):
        """Check if an IP address is valid format."""
        parts = ip_address.split(".")
        if len(parts) != 4:
            return False
        return all(
            part.isdigit() and 0 <= int(part) <= 255
            for part in parts
        )

    @staticmethod
    def generate_hostname(role, number):
        """Generate a standard hostname."""
        return f"{role}-{number:02d}"

# Can be called without creating an instance:
print(Server.validate_ip("10.0.1.10"))     # True
print(Server.validate_ip("999.999.999"))    # False
print(Server.generate_hostname("web", 3))   # web-03

# Can also be called on an instance:
s = Server("web-01", "10.0.1.10")
print(s.validate_ip("10.0.1.10"))  # True
```

## Properties (@property)

Properties let you define methods that are accessed like attributes.
This gives you control over getting, setting, and validating data.

```python
class Server:
    def __init__(self, name, ip_address):
        self.name = name
        self._ip_address = ip_address   # Note the underscore (private convention)
        self._status = "stopped"
        self._cpu_usage = 0.0

    @property
    def ip_address(self):
        """Getter - called when you access server.ip_address."""
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        """Setter - called when you do server.ip_address = '...'."""
        # Validate before setting
        parts = value.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            raise ValueError(f"Invalid IP address: {value}")
        self._ip_address = value

    @property
    def status(self):
        """Read-only property (no setter defined)."""
        return self._status

    @property
    def cpu_usage(self):
        return self._cpu_usage

    @cpu_usage.setter
    def cpu_usage(self, value):
        """Setter with validation."""
        if not 0 <= value <= 100:
            raise ValueError("CPU usage must be between 0 and 100")
        self._cpu_usage = value

    @property
    def is_healthy(self):
        """Computed property - calculated on the fly."""
        return self._status == "running" and self._cpu_usage < 90

# Usage:
server = Server("web-01", "10.0.1.10")

# Access like an attribute (calls getter):
print(server.ip_address)  # 10.0.1.10

# Set like an attribute (calls setter with validation):
server.ip_address = "10.0.1.20"  # Works
# server.ip_address = "999.999"  # Raises ValueError!

# Read-only property:
print(server.status)  # stopped
# server.status = "running"  # ERROR! No setter defined

# Computed property:
print(server.is_healthy)  # False (not running)
```

## Combining All Method Types

```python
class Container:
    _registry = {}  # Class-level registry of all containers

    def __init__(self, name, image):
        self.name = name
        self.image = image
        self._status = "created"
        self._cpu_percent = 0.0
        Container._registry[name] = self

    # --- Instance Methods ---
    def start(self):
        self._status = "running"
        return f"{self.name} started"

    def stop(self):
        self._status = "stopped"
        return f"{self.name} stopped"

    # --- Class Methods ---
    @classmethod
    def from_image(cls, image):
        """Create container with auto-generated name from image."""
        name = image.replace(":", "-").replace("/", "-")
        return cls(name, image)

    @classmethod
    def get_all(cls):
        """Get all registered containers."""
        return list(cls._registry.values())

    @classmethod
    def find_by_name(cls, name):
        """Find a container by name."""
        return cls._registry.get(name)

    # --- Static Methods ---
    @staticmethod
    def validate_image_name(image):
        """Check if image name is valid."""
        if ":" not in image:
            return False
        name, tag = image.rsplit(":", 1)
        return len(name) > 0 and len(tag) > 0

    # --- Properties ---
    @property
    def status(self):
        return self._status

    @property
    def cpu_percent(self):
        return self._cpu_percent

    @cpu_percent.setter
    def cpu_percent(self, value):
        if not 0 <= value <= 100:
            raise ValueError("CPU must be 0-100")
        self._cpu_percent = value

    @property
    def is_running(self):
        return self._status == "running"
```

## When to Use Each

```python
# INSTANCE METHOD: When the method needs to access/modify instance data
# Example: server.start(), container.stop()
# Uses: self

# CLASS METHOD: When the method needs class-level data or is an
# alternative constructor
# Example: Server.from_config(), Server.get_count()
# Uses: cls

# STATIC METHOD: When the method is a utility that belongs to the class
# but doesn't need instance or class data
# Example: Server.validate_ip(), Container.validate_image()
# Uses: neither self nor cls

# PROPERTY: When you want attribute-like access with validation or
# computed values
# Example: server.ip_address (with validation), server.is_healthy (computed)
# Uses: self (internally)
```

## DevOps Connection

- **Instance methods**: Operations on specific resources (start/stop a server)
- **Class methods**: Factory patterns for creating resources from configs
- **Static methods**: Validation utilities (IP validation, name formatting)
- **Properties**: Safe access to resource state with validation

These patterns appear in every DevOps SDK:
- AWS boto3: `EC2.Instance.start()`, `EC2.Instance.state` (property)
- Docker SDK: `Container.start()`, `Image.pull()` (class method)
- Kubernetes client: Resource objects with properties and methods
