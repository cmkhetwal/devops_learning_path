# Lesson 3: Users and Groups

## Why This Matters in DevOps

Every process running on a Linux server executes under a specific user account. Every file
is owned by a specific user and group. The entire security model of Linux is built around
the question: "Who are you, and what are you allowed to do?" As a DevOps engineer, user and
group management is not administrative busywork -- it is the mechanism by which you enforce
security boundaries, isolate applications from each other, and prevent a compromised service
from taking down your entire infrastructure.

In a production environment, you will encounter two fundamentally different types of users:
human users (people who log in via SSH to maintain servers) and service accounts (non-human
users under which applications run). A web server like Nginx runs as the `www-data` user. A
database like PostgreSQL runs as the `postgres` user. These service accounts typically cannot
log in interactively and have no password. They exist solely to provide an identity and
permission boundary for the application. If Nginx is compromised through a vulnerability,
the attacker gains the privileges of `www-data` -- not root. This containment is the entire
point.

The `sudo` command is the gateway between normal user privileges and administrator (root)
access. In modern Linux, you almost never log in as root directly. Instead, you log in as
your personal account and use `sudo` to elevate privileges only when necessary. This creates
an audit trail (every sudo command is logged), enforces the principle of least privilege, and
prevents accidental catastrophic mistakes. Configuring sudo access correctly through the
`/etc/sudoers` file is one of the most security-critical tasks on any server.

Server hardening -- the process of securing a server against attack -- begins with user
management. You disable root SSH login, remove unnecessary user accounts, enforce strong
authentication (SSH keys over passwords), and ensure that each application runs under its own
dedicated service account. These are not theoretical concerns; they are requirements in every
security audit and compliance framework (SOC2, PCI-DSS, HIPAA). As a DevOps engineer, you
will be expected to implement and automate these practices.

Understanding the files that underpin user management (`/etc/passwd`, `/etc/shadow`,
`/etc/group`) gives you the ability to debug authentication problems, write automation
scripts that create users consistently across servers, and understand exactly what happens
when you run commands like `useradd` or `usermod`. This knowledge is foundational for
configuration management tools like Ansible, which automate user creation across fleets of
servers.

---

## Core Concepts

### User Identity Files

Linux stores user information in plain-text files:

**`/etc/passwd`** -- Contains user account information (readable by all users):

```
username:x:UID:GID:comment:home_directory:shell
ubuntu:x:1000:1000:Ubuntu User:/home/ubuntu:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
```

| Field           | Example           | Meaning                             |
|-----------------|-------------------|-------------------------------------|
| username        | `ubuntu`          | Login name                          |
| password        | `x`               | Placeholder (actual hash in shadow) |
| UID             | `1000`            | Numeric user ID                     |
| GID             | `1000`            | Primary group ID                    |
| comment         | `Ubuntu User`     | Full name or description            |
| home_directory  | `/home/ubuntu`    | User's home directory               |
| shell           | `/bin/bash`       | Default shell at login              |

**`/etc/shadow`** -- Contains password hashes (readable only by root):

```
ubuntu:$6$abc...xyz:19000:0:99999:7:::
```

**`/etc/group`** -- Contains group definitions:

```
groupname:x:GID:member1,member2
docker:x:999:ubuntu,deploy
```

### UID Ranges

| UID Range   | Purpose                                    |
|-------------|--------------------------------------------|
| 0           | Root (superuser)                           |
| 1-999       | System/service accounts                    |
| 1000+       | Regular human user accounts                |

### Service Accounts vs Human Accounts

| Attribute         | Human Account            | Service Account           |
|-------------------|--------------------------|---------------------------|
| Shell             | `/bin/bash`              | `/usr/sbin/nologin`       |
| Home directory    | `/home/username`         | `/var/lib/service` or none|
| Password          | Set (or SSH key)         | Locked (no login)         |
| Purpose           | Interactive administration| Run an application        |
| Example           | `ubuntu`, `admin`        | `www-data`, `postgres`    |

### The sudo System

`sudo` allows permitted users to run commands as root (or another user). Configuration is
stored in `/etc/sudoers` and files in `/etc/sudoers.d/`.

Common sudoers entries:

```
# Full root access for the admin group
%admin ALL=(ALL:ALL) ALL

# Allow deploy user to restart nginx without a password
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx

# Allow the ops group to run any command as root
%ops ALL=(ALL:ALL) ALL
```

**Never edit `/etc/sudoers` directly.** Always use `visudo`, which validates the syntax
before saving. A syntax error in sudoers can lock you out of root access entirely.

---

## Step-by-Step Practical

### 1. Examine Existing Users

```bash
cat /etc/passwd | head -10
```

Expected output:
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
...
```

Count all users on the system:

```bash
wc -l /etc/passwd
```

Expected output:
```
35 /etc/passwd
```

List only human users (UID 1000+):

```bash
awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $3, $7}' /etc/passwd
```

Expected output:
```
ubuntu 1000 /bin/bash
```

### 2. View Groups

```bash
cat /etc/group | head -10
```

See which groups your user belongs to:

```bash
groups
```

Expected output:
```
ubuntu adm cdrom sudo dip plugdev
```

```bash
id
```

Expected output:
```
uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),27(sudo)
```

### 3. Create a New User

```bash
sudo useradd -m -s /bin/bash -c "Deploy User" deploy
```

Flags explained:
- `-m` -- Create a home directory
- `-s /bin/bash` -- Set the default shell
- `-c "Deploy User"` -- Set the comment/description

Verify the user was created:

```bash
grep deploy /etc/passwd
```

Expected output:
```
deploy:x:1001:1001:Deploy User:/home/deploy:/bin/bash
```

Set a password for the user:

```bash
sudo passwd deploy
```

### 4. Create a Service Account

```bash
sudo useradd -r -s /usr/sbin/nologin -d /var/lib/myapp -c "MyApp Service" myapp
```

Flags explained:
- `-r` -- Create a system account (UID below 1000)
- `-s /usr/sbin/nologin` -- Prevent interactive login
- `-d /var/lib/myapp` -- Set a non-standard home directory

Verify:

```bash
grep myapp /etc/passwd
```

Expected output:
```
myapp:x:998:998:MyApp Service:/var/lib/myapp:/usr/sbin/nologin
```

### 5. Manage Groups

Create a new group:

```bash
sudo groupadd webteam
```

Add a user to the group:

```bash
sudo usermod -aG webteam deploy
```

The `-aG` flag is critical: `-a` means **append** (add to the group without removing from
other groups), and `-G` specifies the supplementary group. Forgetting `-a` will remove the
user from all other groups.

Verify:

```bash
groups deploy
```

Expected output:
```
deploy : deploy webteam
```

### 6. Configure sudo Access

```bash
sudo visudo -f /etc/sudoers.d/deploy
```

Add this line to the file:

```
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx, /usr/bin/systemctl status nginx
```

This gives the `deploy` user permission to restart and check Nginx without entering a
password -- but nothing else as root.

### 7. Test User Switching

```bash
sudo su - deploy
whoami
pwd
exit
```

Expected output:
```
deploy
/home/deploy
```

### 8. Modify and Delete Users

Modify a user's shell:

```bash
sudo usermod -s /bin/sh deploy
```

Lock a user account (disable login without deleting):

```bash
sudo usermod -L deploy
```

Unlock:

```bash
sudo usermod -U deploy
```

Delete a user and their home directory:

```bash
sudo userdel -r deploy
```

---

## Exercises

1. **Create a Team**: Create three users (`dev1`, `dev2`, `dev3`) and a group called
   `developers`. Add all three users to the `developers` group. Create a shared directory
   `/opt/project` owned by `root:developers` with permissions `770`. Verify that the group
   members can create files in the shared directory.

2. **Service Account Setup**: Create a proper service account for a hypothetical Redis
   installation. The account should have no login shell, a home directory at
   `/var/lib/redis`, and belong to a `redis` group. Create the home directory and set
   appropriate ownership and permissions.

3. **sudo Audit**: Run `sudo cat /var/log/auth.log | grep sudo | tail -20` to see recent
   sudo usage on your system. Note the username, timestamp, and command for each entry.
   Understand why this audit trail is important for security.

4. **Password Policy**: Examine `/etc/login.defs` to find the default password aging
   policies. What is the maximum password age? Minimum password length? Use `sudo chage -l
   ubuntu` to see the password aging information for your user.

5. **Lockdown Exercise**: Create a user called `contractor`, give them sudo access to only
   `cat` and `ls` commands, verify it works, then lock the account and verify they cannot
   log in. Finally, delete the account.

---

## Knowledge Check

**Q1: Why should applications run under dedicated service accounts rather than as root?**

A1: Running as root means a compromised application has unlimited access to the entire
system -- it can read any file, modify any configuration, and even destroy the operating
system. A dedicated service account limits the blast radius: if the application is
compromised, the attacker only gains the limited privileges of that service account. This
containment is a fundamental security principle.

**Q2: What is the difference between `useradd -aG docker deploy` and
`usermod -aG docker deploy`?**

A2: `useradd` creates a new user, so this command would fail if `deploy` already exists.
`usermod` modifies an existing user. The `-aG` flag appends the user to the specified group
without removing them from other groups. You almost always want `usermod -aG` when adding
an existing user to a new group.

**Q3: Why should you never edit `/etc/sudoers` with a regular text editor?**

A3: A syntax error in `/etc/sudoers` can make `sudo` completely unusable, effectively
locking you out of administrator access. The `visudo` command validates the syntax before
saving, preventing this catastrophic mistake. Always use `visudo` or write to a file in
`/etc/sudoers.d/`.

**Q4: You see this line in `/etc/passwd`: `nginx:x:101:101::/var/lib/nginx:/usr/sbin/nologin`.
Explain each field.**

A4: Username is `nginx`, password is stored in `/etc/shadow` (indicated by `x`), UID is
`101` (a system account since it is below 1000), GID is `101`, there is no comment field,
the home directory is `/var/lib/nginx`, and the shell is `/usr/sbin/nologin` which prevents
interactive login. This is a classic service account for the Nginx web server.

**Q5: What catastrophic mistake does forgetting the `-a` flag in `usermod -G` cause?**

A5: Without the `-a` (append) flag, `usermod -G groupname user` sets the user's
supplementary groups to ONLY the specified group, removing them from all other groups. If
the user was in the `sudo` group, they lose sudo access. If they were in the `docker`
group, they lose Docker access. This is one of the most common and dangerous mistakes in
Linux user management. Always use `-aG` together.
