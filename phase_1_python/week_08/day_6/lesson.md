# Week 8, Day 6: Practice Day - OOP Mini-Projects

## What You'll Build Today
Five mini-projects combining OOP concepts:
1. ServerManager class with fleet management
2. DeploymentPipeline class
3. ConfigManager with inheritance
4. Test suite for all classes
5. Complete mini-project structure

## Tips for Today
- Use classes with proper `__init__`, methods, and properties
- Apply inheritance where it makes sense
- Think about real DevOps workflows
- Each project builds on skills from the entire week

## Quick Reference

```python
# Class basics
class MyClass:
    class_var = 0                    # Class attribute

    def __init__(self, name):        # Constructor
        self.name = name             # Instance attribute

    def method(self):                # Instance method
        return self.name

    @classmethod
    def from_config(cls, config):    # Alternative constructor
        return cls(config["name"])

    @staticmethod
    def validate(value):             # Utility function
        return isinstance(value, str)

    @property
    def upper_name(self):            # Computed property
        return self.name.upper()

# Inheritance
class Child(Parent):
    def __init__(self, name, extra):
        super().__init__(name)       # Call parent init
        self.extra = extra

    def method(self):                # Override parent method
        result = super().method()    # Extend parent method
        return f"{result} + extra"
```

Good luck with the projects!
