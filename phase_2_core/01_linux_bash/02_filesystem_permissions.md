# Lesson 2: Filesystem Hierarchy and Permissions

## Why This Matters in DevOps

Security in DevOps begins with file permissions. Every data breach post-mortem you will ever
read includes the same recurring theme: something had more access than it should have. A web
server that can read the database credentials file. A deployment script running as root when
it only needed to restart a service. A log directory writable by every user on the system. In
DevOps, the **principle of least privilege** is not a suggestion -- it is a survival strategy.

Linux permissions are the first line of defense on any server. They determine who can read a
file, who can modify it, and who can execute it. When you deploy an application, you must
think carefully about which user the application runs as and what files that user can access.
A misconfigured permission on a single file can expose secrets, allow unauthorized code
execution, or let an attacker escalate their privileges to full root access.

The Linux filesystem hierarchy is equally important to understand. Unlike Windows, where
programs scatter files across `C:\Program Files`, `C:\Users`, and the registry, Linux
organizes files into a predictable, standardized directory structure. When you SSH into any
Linux server anywhere in the world, you know that configuration files are in `/etc`, logs are
in `/var/log`, and temporary files are in `/tmp`. This predictability is what makes it
possible to manage thousands of servers consistently.

Understanding the filesystem hierarchy also helps you make critical decisions during
deployments. Should your application live in `/opt` or `/usr/local`? Should its configuration
go in `/etc` or alongside the binary? Where should it write temporary files? These decisions
affect security, maintenance, and how well your deployment integrates with the operating
system's existing tools (like package managers and backup scripts).

As you progress into containerization and infrastructure as code, permissions and filesystem
knowledge become even more critical. Docker containers, Kubernetes pods, and Ansible
playbooks all require you to specify ownership, permission modes, and file paths. If you do
not understand these fundamentals deeply, your automated deployments will fail in ways that
are difficult to debug.

---

## Core Concepts

### The Linux Filesystem Hierarchy

Every Linux system follows the **Filesystem Hierarchy Standard (FHS)**:

| Directory  | Purpose                                              | DevOps Relevance                    |
|------------|------------------------------------------------------|-------------------------------------|
| `/`        | Root of the entire filesystem                        | Everything branches from here       |
| `/etc`     | System-wide configuration files                      | Nginx configs, SSH settings, cron   |
| `/var`     | Variable data (logs, databases, mail)                | `/var/log` is where you troubleshoot|
| `/home`    | User home directories                                | Each user gets `/home/username`     |
| `/tmp`     | Temporary files (cleared on reboot)                  | Scratch space, never store data here|
| `/opt`     | Optional/third-party software                        | Common for custom applications      |
| `/usr`     | User system resources (binaries, libraries)          | System-installed programs live here |
| `/usr/local`| Locally compiled software                           | Software you install manually       |
| `/proc`    | Virtual filesystem for process/kernel info           | Read CPU, memory, process details   |
| `/dev`     | Device files                                         | Disks, terminals, hardware          |
| `/root`    | Home directory for the root user                     | Separate from `/home`               |
| `/srv`     | Data served by the system                            | Web content, FTP files              |
| `/boot`    | Boot loader files                                    | Kernel images, GRUB config          |
| `/mnt`     | Temporary mount points                               | Mounting external drives            |

### Understanding Ownership

Every file and directory in Linux has three ownership attributes:

- **User (owner)**: The person who created the file (or was assigned ownership)
- **Group**: A collection of users who share access
- **Other**: Everyone else on the system

### Permission Types

Each ownership level has three permission types:

| Permission | Symbol | On Files                | On Directories            | Octal |
|------------|--------|-------------------------|---------------------------|-------|
| Read       | `r`    | Can view file contents  | Can list directory entries | 4     |
| Write      | `w`    | Can modify file contents| Can create/delete files   | 2     |
| Execute    | `x`    | Can run as a program    | Can enter the directory   | 1     |

### Reading Permission Strings

When you run `ls -l`, you see a 10-character permission string:

```
-rwxr-xr-- 1 deploy webteam 4096 Apr 16 10:00 deploy.sh
```

Breaking down `-rwxr-xr--`:

| Position | Characters | Meaning                                    |
|----------|------------|--------------------------------------------|
| 1        | `-`        | File type (`-` = file, `d` = directory, `l` = link) |
| 2-4      | `rwx`      | Owner permissions (read, write, execute)   |
| 5-7      | `r-x`      | Group permissions (read, execute)          |
| 8-10     | `r--`      | Other permissions (read only)              |

### Octal (Numeric) Permissions

Permissions can be expressed as a three-digit number where each digit is the sum of its
permission values (read=4, write=2, execute=1):

| Octal | Permissions | Meaning                    |
|-------|-------------|----------------------------|
| 755   | rwxr-xr-x   | Owner full, others read+exec |
| 644   | rw-r--r--   | Owner read+write, others read |
| 700   | rwx------   | Owner full, no one else      |
| 600   | rw-------   | Owner read+write, no one else|
| 777   | rwxrwxrwx   | Everyone full (DANGEROUS)    |

### Special Permissions

| Permission  | Octal | Effect                                                    |
|-------------|-------|-----------------------------------------------------------|
| SUID        | 4000  | File executes as the file owner, not the calling user     |
| SGID        | 2000  | File executes as the group; new files in dir inherit group|
| Sticky Bit  | 1000  | Only file owner can delete files in the directory         |

The `/tmp` directory uses the sticky bit: everyone can write files there, but only the owner
of a file can delete it.

---

## Step-by-Step Practical

### 1. Explore the Filesystem Hierarchy

```bash
ls -la /etc/ | head -15
```

Expected output:
```
total 832
drwxr-xr-x 92 root root  4096 Apr 16 10:00 .
drwxr-xr-x 19 root root  4096 Apr 10 08:00 ..
-rw-r--r--  1 root root  3028 Apr 10 08:00 adduser.conf
drwxr-xr-x  2 root root  4096 Apr 10 08:00 alternatives
-rw-r--r--  1 root root   411 Apr 10 08:00 apt
```

Notice that `/etc` is owned by `root` -- only the administrator can modify system configs.

```bash
ls -la /var/log/ | head -10
```

Expected output:
```
total 2456
drwxrwxr-x 10 root   syslog  4096 Apr 16 00:00 .
-rw-r-----  1 syslog adm    98234 Apr 16 10:15 syslog
-rw-r-----  1 syslog adm    45621 Apr 16 00:00 auth.log
-rw-r--r--  1 root   root   32198 Apr 15 12:00 dpkg.log
```

Notice the different owners and groups for log files. The `syslog` user owns system logs.

### 2. View File Permissions

```bash
mkdir -p ~/permissions_lab
cd ~/permissions_lab
touch myfile.txt
ls -la myfile.txt
```

Expected output:
```
-rw-rw-r-- 1 ubuntu ubuntu 0 Apr 16 10:30 myfile.txt
```

The default permissions `664` (`rw-rw-r--`) mean the owner and group can read and write,
others can only read.

### 3. Change Permissions with chmod

Using **octal notation**:

```bash
chmod 755 myfile.txt
ls -la myfile.txt
```

Expected output:
```
-rwxr-xr-x 1 ubuntu ubuntu 0 Apr 16 10:30 myfile.txt
```

Using **symbolic notation**:

```bash
chmod u=rw,g=r,o= myfile.txt
ls -la myfile.txt
```

Expected output:
```
-rw-r----- 1 ubuntu ubuntu 0 Apr 16 10:30 myfile.txt
```

Adding and removing specific permissions:

```bash
chmod +x myfile.txt        # Add execute for all
chmod o-r myfile.txt       # Remove read from others
chmod g+w myfile.txt       # Add write to group
ls -la myfile.txt
```

### 4. Change Ownership with chown

```bash
sudo chown root:root myfile.txt
ls -la myfile.txt
```

Expected output:
```
-rw-r----- 1 root root 0 Apr 16 10:30 myfile.txt
```

Change both user and group at once:

```bash
sudo chown ubuntu:ubuntu myfile.txt
```

Change only the group:

```bash
sudo chgrp www-data myfile.txt
ls -la myfile.txt
```

Expected output:
```
-rw-r----- 1 ubuntu www-data 0 Apr 16 10:30 myfile.txt
```

### 5. Recursive Permission Changes

```bash
mkdir -p ~/permissions_lab/project/{src,config,logs}
touch ~/permissions_lab/project/src/app.py
touch ~/permissions_lab/project/config/settings.ini
touch ~/permissions_lab/project/logs/app.log

chmod -R 750 ~/permissions_lab/project/
ls -laR ~/permissions_lab/project/
```

The `-R` flag applies permissions recursively to all files and subdirectories.

### 6. Observe the Sticky Bit on /tmp

```bash
ls -ld /tmp
```

Expected output:
```
drwxrwxrwt 12 root root 4096 Apr 16 10:00 /tmp
```

Notice the `t` at the end -- this is the sticky bit. It means any user can create files in
`/tmp`, but only the owner of a file can delete it.

### 7. Practice with a Realistic Scenario

Set up permissions as you would for a web application:

```bash
sudo mkdir -p /opt/myapp/{bin,config,logs,data}
sudo chown -R ubuntu:www-data /opt/myapp
sudo chmod 750 /opt/myapp/bin
sudo chmod 640 /opt/myapp/config/*  2>/dev/null
sudo chmod 770 /opt/myapp/logs
sudo chmod 750 /opt/myapp/data
ls -laR /opt/myapp/
```

This demonstrates least privilege: the app owner has full access, the web group has limited
access, and others have no access at all.

---

## Exercises

1. **Permission Decoding**: Create five files and set their permissions to `644`, `755`,
   `600`, `444`, and `711`. Use `ls -l` to view each one, and write down in plain English
   what each permission set allows.

2. **Web Server Simulation**: Create a directory structure at `~/webserver/` with
   subdirectories `html/`, `cgi-bin/`, and `logs/`. Set `html/` files to `644` (readable by
   all), `cgi-bin/` scripts to `750` (executable by owner and group), and `logs/` to `770`
   (writable by owner and group only). Verify with `ls -laR`.

3. **Ownership Chain**: Create a file, then use `chown` to transfer ownership to `root`,
   then back to yourself. Observe what happens when you try to read or write the file when
   it is owned by root but has permissions `600`.

4. **Sticky Bit Experiment**: Create a directory with `chmod 1777`. Create files inside it as
   your user. Explain why the sticky bit is necessary for directories like `/tmp` where
   multiple users create files.

---

## Knowledge Check

**Q1: A file has permissions `-rw-r-----`. Who can read it? Who can write to it? Who cannot
access it at all?**

A1: The owner can read and write. Members of the file's group can read only. Everyone else
(other) has no access at all. In octal, this is `640`.

**Q2: Why should you almost never set permissions to `777` on a production server?**

A2: `777` means every user on the system can read, write, and execute the file. This
completely violates the principle of least privilege. An attacker who gains access as any
user could modify the file, inject malicious code, or delete it. Configuration files with
`777` could be tampered with, and executable files with `777` could be replaced with
malware.

**Q3: What is the difference between `/opt` and `/usr/local` for installing software?**

A3: `/opt` is intended for self-contained third-party software packages (each application
gets its own subdirectory like `/opt/myapp`). `/usr/local` follows the standard Unix
directory structure (`bin`, `lib`, `etc`) and is meant for locally compiled software that
integrates with the system. In practice, many DevOps teams use `/opt` for application
deployments.

**Q4: You need to deploy an application config file that contains database passwords. What
permissions and ownership would you set?**

A4: Set ownership to the application's service account user and group (`chown appuser:appgroup
config.ini`). Set permissions to `640` or even `600` so only the owner (and optionally the
group) can read it. Never set it to world-readable. Store secrets in a vault when possible,
but when they must exist on disk, restrictive permissions are essential.

**Q5: What does the SUID bit do, and why is it a security concern?**

A5: The SUID (Set User ID) bit causes a program to execute with the permissions of the file
owner rather than the user who runs it. For example, `/usr/bin/passwd` has SUID set so that
any user can change their password (which requires writing to `/etc/shadow`, a root-owned
file). It is a security concern because if a SUID program has a vulnerability, an attacker
can exploit it to gain the file owner's privileges, often root.
