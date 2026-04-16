# Week 7, Day 5: SSH with Paramiko

## What You'll Learn
- What SSH is and why it matters for DevOps
- The `paramiko` library for SSH in Python
- SSHClient: connecting and running commands
- SFTPClient: transferring files
- Writing SSH automation functions
- Building simulated/mock SSH patterns (no server needed)

## What is SSH?

SSH (Secure Shell) is the standard protocol for remote server management.
Every DevOps engineer uses SSH daily to:
- Connect to remote servers
- Run commands remotely
- Transfer files
- Manage infrastructure

```bash
# On the command line:
ssh user@server.example.com          # Connect
ssh user@server.example.com "uptime" # Run command remotely
scp file.txt user@server.example.com:/tmp/  # Copy file
```

## Installing Paramiko

```bash
pip install paramiko
```

## SSHClient Basics

```python
import paramiko

# Create SSH client
client = paramiko.SSHClient()

# Auto-add unknown host keys (for learning only!)
# In production, use known_hosts file
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to server
client.connect(
    hostname="server.example.com",
    port=22,
    username="admin",
    password="secretpassword"    # Or use key_filename for SSH keys
)

# Run a command
stdin, stdout, stderr = client.exec_command("uptime")
output = stdout.read().decode()
errors = stderr.read().decode()
exit_code = stdout.channel.recv_exit_status()

print(f"Output: {output}")
print(f"Errors: {errors}")
print(f"Exit code: {exit_code}")

# Always close the connection
client.close()
```

## Using SSH Keys (Preferred)

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect with private key
client.connect(
    hostname="server.example.com",
    port=22,
    username="admin",
    key_filename="/home/user/.ssh/id_rsa"  # Path to private key
)

stdin, stdout, stderr = client.exec_command("hostname")
print(stdout.read().decode())
client.close()
```

## Running Multiple Commands

```python
import paramiko

def run_commands(host, username, password, commands):
    """Run multiple commands on a remote server."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results = []

    try:
        client.connect(hostname=host, username=username, password=password)

        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            results.append({
                "command": cmd,
                "stdout": stdout.read().decode().strip(),
                "stderr": stderr.read().decode().strip(),
                "exit_code": stdout.channel.recv_exit_status()
            })

    finally:
        client.close()

    return results

# Usage:
# results = run_commands("server.example.com", "admin", "pass", [
#     "hostname",
#     "uptime",
#     "df -h",
#     "free -m"
# ])
```

## SFTP File Transfer

```python
import paramiko

def upload_file(host, username, password, local_path, remote_path):
    """Upload a file via SFTP."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, username=username, password=password)
        sftp = client.open_sftp()

        sftp.put(local_path, remote_path)
        print(f"Uploaded {local_path} -> {remote_path}")

        sftp.close()
    finally:
        client.close()

def download_file(host, username, password, remote_path, local_path):
    """Download a file via SFTP."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, username=username, password=password)
        sftp = client.open_sftp()

        sftp.get(remote_path, local_path)
        print(f"Downloaded {remote_path} -> {local_path}")

        sftp.close()
    finally:
        client.close()
```

## Simulated SSH Pattern (For Practice)

Since you may not have an SSH server available, here is a simulation
pattern that mimics real SSH behavior:

```python
class MockSSHClient:
    """Simulates SSH client behavior for learning."""

    def __init__(self):
        self.connected = False
        self.hostname = None
        self.username = None

    def connect(self, hostname, username, password=None, key_filename=None):
        """Simulate connecting to a server."""
        if not hostname or not username:
            raise ValueError("hostname and username required")
        self.hostname = hostname
        self.username = username
        self.connected = True
        return True

    def exec_command(self, command):
        """Simulate command execution with realistic output."""
        if not self.connected:
            raise RuntimeError("Not connected")

        # Simulate common DevOps commands
        responses = {
            "hostname": self.hostname,
            "whoami": self.username,
            "uptime": " 10:30:00 up 45 days, 3:22, 1 user, load average: 0.15, 0.10, 0.05",
            "df -h": "Filesystem  Size  Used Avail Use% Mounted on\n/dev/sda1   50G   23G   25G  48% /",
            "free -m": "       total   used   free\nMem:    8192   4096   4096\nSwap:   2048    128   1920",
            "cat /etc/os-release": 'NAME="Ubuntu"\nVERSION="22.04 LTS"',
            "docker ps": "CONTAINER ID  IMAGE        STATUS       NAMES\nabc123       nginx:latest Up 2 hours   web-01",
            "systemctl status nginx": "nginx.service - A high performance web server\n   Active: active (running)",
        }

        output = responses.get(command, f"Command executed: {command}")
        return {"stdout": output, "stderr": "", "exit_code": 0}

    def close(self):
        """Close the connection."""
        self.connected = False
        self.hostname = None
```

## Real-World SSH Automation Pattern

```python
class ServerManager:
    """Manage remote servers via SSH."""

    def __init__(self, host, username, password=None, key_file=None):
        self.host = host
        self.username = username
        self.password = password
        self.key_file = key_file

    def _get_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_args = {
            "hostname": self.host,
            "username": self.username,
        }
        if self.key_file:
            connect_args["key_filename"] = self.key_file
        if self.password:
            connect_args["password"] = self.password
        client.connect(**connect_args)
        return client

    def run_command(self, command):
        client = self._get_client()
        try:
            stdin, stdout, stderr = client.exec_command(command)
            return {
                "stdout": stdout.read().decode().strip(),
                "stderr": stderr.read().decode().strip(),
                "exit_code": stdout.channel.recv_exit_status()
            }
        finally:
            client.close()

    def get_system_info(self):
        return {
            "hostname": self.run_command("hostname")["stdout"],
            "uptime": self.run_command("uptime")["stdout"],
            "disk": self.run_command("df -h /")["stdout"],
            "memory": self.run_command("free -m")["stdout"],
        }

    def deploy_file(self, local_path, remote_path):
        client = self._get_client()
        try:
            sftp = client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        finally:
            client.close()
```

## DevOps Connection

SSH automation with Paramiko enables:
- **Configuration Management**: Push configs to multiple servers
- **Deployment**: Deploy code to remote servers
- **Monitoring**: Collect system metrics from servers
- **Maintenance**: Run updates, restart services across fleet
- **Troubleshooting**: Gather logs from multiple servers
- **Automation**: Replace manual SSH sessions with scripts

While tools like Ansible and Terraform are preferred for large-scale automation,
understanding Paramiko helps you build custom tools and understand what those
higher-level tools do under the hood.
