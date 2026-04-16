# Lesson 6: Package Management

## Why This Matters in DevOps

Package management is the discipline of installing, updating, and removing software on Linux
servers in a controlled, repeatable, and auditable way. In DevOps, this discipline is what
separates a well-managed infrastructure from a chaotic one. When every server is built using
the same package manager commands and the same repository sources, you get consistency. When
engineers SSH into servers and install software manually using random methods -- compiling
from source here, downloading a binary there, using `pip install --user` somewhere else --
you get what the industry calls **snowflake servers**: machines that are each unique and
impossible to reproduce or maintain.

The concept of snowflake servers is one of the most important anti-patterns in DevOps. If a
server goes down and you cannot rebuild it identically because nobody remembers exactly what
was installed on it or how it was configured, your infrastructure is fragile. Package
management is the first defense against this fragility. Every piece of software on a
production server should be installed through the package manager, so that you can list
exactly what is installed (`dpkg -l` or `rpm -qa`), reproduce the installation on another
machine, and roll back to a previous version if an update causes problems.

Understanding package management also means understanding **repositories**: centralized
collections of software packages maintained by the Linux distribution or third-party
vendors. When you run `apt install nginx`, you are not downloading software from a random
website -- you are pulling a vetted, signed package from Ubuntu's official repository. This
trust model is critical for security. Adding untrusted repositories or installing packages
from unknown sources is equivalent to downloading `.exe` files from random websites on
Windows.

Dependency management is another key concept. Software rarely exists in isolation. Nginx
depends on OpenSSL for encryption. Python applications depend on specific library versions.
When you install a package, the package manager automatically resolves and installs all
dependencies. When you remove a package, it can clean up dependencies that are no longer
needed. This automated dependency resolution prevents the "works on my machine" problem and
ensures that software has everything it needs to function.

As you progress into configuration management (Ansible, Puppet, Chef) and containerization
(Docker), package management commands become the building blocks of your automation. An
Ansible playbook that deploys a web server will include `apt` tasks. A Dockerfile will
include `apt-get install` commands. Understanding what these commands do, how repositories
work, and how to manage package versions is essential for writing reliable automation.

---

## Core Concepts

### Package Management Systems

Linux distributions use different package managers based on their family:

| Distribution Family | Package Format | Low-Level Tool | High-Level Tool  |
|---------------------|---------------|----------------|------------------|
| Debian/Ubuntu       | `.deb`        | `dpkg`         | `apt` / `apt-get`|
| Red Hat/CentOS      | `.rpm`        | `rpm`          | `yum` / `dnf`   |
| Alpine              | `.apk`        | `apk`          | `apk`            |
| Arch                | `.pkg.tar.zst`| `pacman`       | `pacman`         |

The **low-level tool** installs individual package files. The **high-level tool** handles
repository management, dependency resolution, and downloading.

### What Is a Repository?

A repository is a server hosting a collection of packages. Your system is configured to know
which repositories to use:

- **Debian/Ubuntu**: Configured in `/etc/apt/sources.list` and `/etc/apt/sources.list.d/`
- **Red Hat/CentOS**: Configured in `/etc/yum.repos.d/`

### Package Lifecycle

```
Search -> Install -> Configure -> Update -> Remove
```

Every step should be intentional and documented. In production, you should know exactly which
version of every package is installed and why.

### Version Pinning

In production, you often want to install a specific version of a package to ensure
consistency:

```bash
# Debian/Ubuntu
apt install nginx=1.18.0-6ubuntu1

# Red Hat/CentOS
yum install nginx-1.18.0
```

You can also prevent a package from being automatically updated:

```bash
# Debian/Ubuntu
apt-mark hold nginx

# Red Hat/CentOS
yum versionlock nginx
```

---

## Step-by-Step Practical

### 1. Update Package Lists (Debian/Ubuntu)

```bash
sudo apt update
```

Expected output:
```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [119 kB]
Get:3 http://security.ubuntu.com/ubuntu jammy-security InRelease [110 kB]
...
Reading package lists... Done
Building dependency tree... Done
45 packages can be upgraded. Run 'apt list --upgradable' to see them.
```

This downloads the latest package lists from repositories. It does NOT install or update
anything -- it only refreshes the list of available packages and versions.

### 2. Search for Packages

```bash
apt search nginx
```

Expected output:
```
nginx/jammy-updates 1.18.0-6ubuntu14.4 amd64
  small, powerful, scalable web/proxy server

nginx-full/jammy-updates 1.18.0-6ubuntu14.4 amd64
  nginx web/proxy server (standard version)

nginx-light/jammy-updates 1.18.0-6ubuntu14.4 amd64
  nginx web/proxy server (basic version)
```

Get detailed information about a package:

```bash
apt show nginx
```

Expected output:
```
Package: nginx
Version: 1.18.0-6ubuntu14.4
Priority: optional
Section: httpd
Maintainer: Ubuntu Developers
Depends: nginx-core (= 1.18.0-6ubuntu14.4) | nginx-full | nginx-light | nginx-extras
Description: small, powerful, scalable web/proxy server
```

### 3. Install a Package

```bash
sudo apt install -y tree
```

Expected output:
```
Reading package lists... Done
Building dependency tree... Done
The following NEW packages will be installed:
  tree
0 upgraded, 1 newly installed, 0 to remove and 45 not upgraded.
Need to get 48.3 kB of archives.
Get:1 http://archive.ubuntu.com/ubuntu jammy/universe amd64 tree amd64 2.0.2-1 [48.3 kB]
Setting up tree (2.0.2-1) ...
```

The `-y` flag automatically answers "yes" to confirmation prompts. Use this in scripts but
be cautious with it interactively.

Verify installation:

```bash
which tree
tree --version
```

Expected output:
```
/usr/bin/tree
tree v2.0.2 (c) 1996-2022
```

### 4. List Installed Packages

```bash
dpkg -l | head -20
```

Expected output:
```
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait
||/ Name                Version          Architecture Description
+++-===================-================-============-======================
ii  adduser             3.118ubuntu5     all          add and remove users
ii  apt                 2.4.11           amd64        commandline package manager
ii  base-files          12ubuntu4.4      amd64        Debian base system
```

Search for a specific installed package:

```bash
dpkg -l | grep nginx
```

List files installed by a package:

```bash
dpkg -L tree
```

Expected output:
```
/.
/usr
/usr/bin
/usr/bin/tree
/usr/share/doc/tree
/usr/share/man/man1/tree.1.gz
```

### 5. Upgrade Packages

View available upgrades:

```bash
apt list --upgradable
```

Upgrade all packages:

```bash
sudo apt upgrade -y
```

Upgrade a specific package:

```bash
sudo apt install --only-upgrade nginx
```

### 6. Remove a Package

Remove the package but keep configuration files:

```bash
sudo apt remove tree
```

Remove the package AND its configuration files:

```bash
sudo apt purge tree
```

Clean up unused dependencies:

```bash
sudo apt autoremove -y
```

### 7. Add a Third-Party Repository

Example: Adding the Docker repository on Ubuntu:

```bash
# Install prerequisites
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package lists to include Docker
sudo apt update
```

### 8. Red Hat/CentOS Equivalents

For environments using Red Hat, CentOS, or Amazon Linux:

```bash
# Update package lists and install
sudo yum check-update          # Equivalent to apt update
sudo yum install nginx -y      # Install a package
sudo yum update -y             # Upgrade all packages
sudo yum remove nginx          # Remove a package
sudo yum list installed        # List installed packages
rpm -qa                        # List all installed packages
rpm -ql nginx                  # List files in a package
sudo yum info nginx            # Show package details

# On newer systems (Fedora, RHEL 8+, Amazon Linux 2023)
sudo dnf install nginx -y     # dnf replaces yum
```

### 9. Compile from Source (When Necessary)

Sometimes a package is not available in repositories. Compiling from source is the last
resort:

```bash
# Install build tools
sudo apt install -y build-essential

# Typical compile-from-source workflow
# wget https://example.com/software-1.0.tar.gz
# tar xzf software-1.0.tar.gz
# cd software-1.0
# ./configure --prefix=/usr/local
# make
# sudo make install
```

**Warning**: Software compiled from source is not managed by the package manager. It will
not receive automatic updates, and the package manager does not know it exists. Avoid this
in production unless absolutely necessary.

---

## Exercises

1. **Package Audit**: Run `dpkg -l | wc -l` to count how many packages are installed on your
   system. Then use `dpkg -l | grep -i python` to find all Python-related packages. Document
   what you find and consider which ones are essential and which could be removed.

2. **Install and Explore**: Install `htop`, `jq`, and `curl` using `apt`. After installation,
   find where each binary is located using `which`. Then use `dpkg -L` to see all files
   installed by `jq`.

3. **Repository Investigation**: Examine `/etc/apt/sources.list` and list all configured
   repositories. Add the `universe` repository if it is not already present. Understand the
   difference between `main`, `universe`, `restricted`, and `multiverse` in Ubuntu.

4. **Version Management**: Install a specific version of a package (e.g., `sudo apt install
   vim=2:8.2.3995-1ubuntu2`). Then use `apt-mark hold vim` to prevent it from being upgraded.
   Verify the hold with `apt-mark showhold`.

5. **Cleanup**: Run `sudo apt autoremove --dry-run` to see what would be removed without
   actually removing it. Then run `sudo apt clean` to clear the package cache. Check how much
   disk space `/var/cache/apt/archives/` uses before and after with `du -sh`.

---

## Knowledge Check

**Q1: What is the difference between `apt update` and `apt upgrade`?**

A1: `apt update` downloads the latest package lists from the configured repositories -- it
refreshes the catalog of available packages and their versions. It does not install or change
any software. `apt upgrade` actually installs newer versions of packages that are already
installed on the system. You should always run `apt update` before `apt upgrade` to ensure
you are upgrading to the latest available versions.

**Q2: Why is compiling from source problematic in a production environment?**

A2: Software compiled from source is invisible to the package manager. It does not receive
automatic security updates, cannot be easily rolled back, does not have dependency tracking,
and makes the server harder to reproduce. If you compile Nginx from source on one server,
you must manually repeat the exact same process on every other server. This creates snowflake
servers and operational burden. Use distribution packages or containerization instead.

**Q3: What is a "snowflake server" and how does disciplined package management prevent it?**

A3: A snowflake server is a machine that has been configured through ad-hoc manual changes
over time, making it unique and impossible to reproduce. Each one is different, like a
snowflake. Disciplined package management prevents this by ensuring all software is installed
through the package manager with documented commands. You can list exactly what is installed
(`dpkg -l`), reproduce the installation on another machine, and track changes over time.

**Q4: Why should you be cautious about adding third-party repositories?**

A4: Third-party repositories can introduce security risks: the packages may not be audited,
could contain malware, might conflict with system packages, or could stop being maintained.
Each additional repository is a trust decision. In production, only add repositories from
trusted sources (official vendor repositories like Docker's or PostgreSQL's). Always verify
GPG keys and use HTTPS. Unauthorized repositories should be forbidden by your security
policy.

**Q5: What is the equivalent of `apt install nginx` on a CentOS/Amazon Linux system?**

A5: `yum install nginx` (or `dnf install nginx` on newer systems like RHEL 8+, Fedora, and
Amazon Linux 2023). While the syntax is similar, the underlying package format is different:
Debian uses `.deb` packages and `apt`/`dpkg`, while Red Hat uses `.rpm` packages and
`yum`/`dnf`/`rpm`. The concepts (repositories, dependencies, versioning) are the same across
both families.
