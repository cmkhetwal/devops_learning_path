"""
Week 8, Day 4: Project Structure - Exercise

Practice organizing code into a proper project structure.
Since we're working in a single file, we'll simulate the concepts.

DevOps Context: Well-structured projects are easier to test,
deploy, maintain, and share across your team.
"""

# ===========================================================
# TASK 1: Module Simulation - utils.py
# ===========================================================
# Create utility functions that would belong in a utils module.
#
# Functions:
#   - validate_ip(ip_str): return True if valid IPv4 (4 dot-separated
#     numbers, each 0-255). Return False for any other input.
#   - format_bytes(num_bytes): convert to human-readable string.
#     Use units: B, KB, MB, GB, TB (1024-based).
#     Round to 1 decimal place.
#     Examples: 500 -> "500.0 B", 1536 -> "1.5 KB",
#     1048576 -> "1.0 MB", 1073741824 -> "1.0 GB"
#   - sanitize_name(name): convert to lowercase, replace spaces with
#     hyphens, remove any characters that aren't alphanumeric or hyphens.
#     Examples: "My Server 01" -> "my-server-01",
#     "Web@Server#1" -> "webserver1"
#   - generate_id(prefix, number): return "{prefix}-{number:04d}"
#     Example: generate_id("srv", 42) -> "srv-0042"

def validate_ip(ip_str):
    # YOUR CODE HERE
    pass

def format_bytes(num_bytes):
    # YOUR CODE HERE
    pass

def sanitize_name(name):
    # YOUR CODE HERE
    pass

def generate_id(prefix, number):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Package Structure Knowledge
# ===========================================================
# Create a function that returns the correct file structure for
# a given project name.
#
# Parameter:
#   - project_name (str): e.g., "server_manager"
#
# Return a dictionary representing the file tree:
# {
#     "root": "{project_name}/",
#     "package_dir": "{project_name}/{project_name}/",
#     "required_files": [
#         "{project_name}/{project_name}/__init__.py",
#         "{project_name}/requirements.txt",
#         "{project_name}/setup.py",
#         "{project_name}/README.md",
#         "{project_name}/.gitignore",
#     ],
#     "test_dir": "{project_name}/tests/",
#     "test_init": "{project_name}/tests/__init__.py",
# }

def get_project_structure(project_name):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: Requirements Parser
# ===========================================================
# Create a function that parses a requirements.txt content string
# and returns structured data.
#
# Parameter:
#   - requirements_text (str): contents of a requirements.txt file
#
# Rules:
#   - Skip empty lines and comment lines (starting with #)
#   - Parse "package>=version" into {"name": pkg, "version": ver, "operator": ">="}
#   - Parse "package==version" into {"name": pkg, "version": ver, "operator": "=="}
#   - Parse "package" (no version) into {"name": pkg, "version": None, "operator": None}
#   - Also handle "<=", "!=", "~=" operators
#
# Return a list of dictionaries.
#
# Example:
#   parse_requirements("requests>=2.28.0\nparamiko==3.0.0\n# comment\nclick")
#   -> [
#       {"name": "requests", "version": "2.28.0", "operator": ">="},
#       {"name": "paramiko", "version": "3.0.0", "operator": "=="},
#       {"name": "click", "version": None, "operator": None}
#   ]

def parse_requirements(requirements_text):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: Config File Generator
# ===========================================================
# Create a function that generates a basic setup.py content string
# for a project.
#
# Parameters:
#   - name (str): project name
#   - version (str): version string
#   - description (str): project description
#   - author (str): author name
#   - dependencies (list of str): required packages
#
# Return a string containing valid Python code for setup.py.
# The string should include:
#   - "from setuptools import setup, find_packages"
#   - "setup(" call with name, version, description, author,
#     packages=find_packages(), install_requires=dependencies
#   - Must be syntactically valid Python
#
# Example output (as a string):
#   from setuptools import setup, find_packages
#
#   setup(
#       name="my-tool",
#       version="1.0.0",
#       description="My tool",
#       author="John",
#       packages=find_packages(),
#       install_requires=[
#           "requests",
#           "click",
#       ],
#   )

def generate_setup_py(name, version, description, author, dependencies):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: Import Path Resolver
# ===========================================================
# Create a function that determines the correct import statement
# for a given file in a project structure.
#
# Parameters:
#   - package_name (str): root package name (e.g., "server_manager")
#   - file_path (str): path within the project
#     (e.g., "server_manager/models/server.py")
#   - item_name (str): the class or function to import (e.g., "Server")
#
# Return a dictionary:
#   {
#       "absolute_import": "from {module_path} import {item_name}",
#       "module_path": dot-separated module path (e.g., "server_manager.models.server"),
#   }
#
# Rules:
#   - Convert file path to dot notation (replace / with ., remove .py)
#   - The file_path starts with the package name
#
# Examples:
#   resolve_import("server_manager", "server_manager/models/server.py", "Server")
#   -> {
#       "absolute_import": "from server_manager.models.server import Server",
#       "module_path": "server_manager.models.server"
#   }
#
#   resolve_import("server_manager", "server_manager/utils.py", "validate_ip")
#   -> {
#       "absolute_import": "from server_manager.utils import validate_ip",
#       "module_path": "server_manager.utils"
#   }

def resolve_import(package_name, file_path, item_name):
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Task 1
    print("Task 1:")
    print("  validate_ip:", validate_ip("10.0.1.10"), validate_ip("999.0.1"))
    print("  format_bytes:", format_bytes(1536), format_bytes(1048576))
    print("  sanitize_name:", sanitize_name("My Server 01"))
    print("  generate_id:", generate_id("srv", 42))
    print()

    # Task 2
    print("Task 2:", get_project_structure("server_manager"))
    print()

    # Task 3
    reqs = "requests>=2.28.0\nparamiko==3.0.0\n# comment\n\nclick"
    print("Task 3:", parse_requirements(reqs))
    print()

    # Task 4
    setup = generate_setup_py("my-tool", "1.0.0", "My tool", "Dev", ["requests", "click"])
    print("Task 4:")
    print(setup)
    print()

    # Task 5
    print("Task 5:", resolve_import("server_manager",
                                     "server_manager/models/server.py", "Server"))
