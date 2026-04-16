# Lesson 1: Linux Fundamentals

## Why This Matters in DevOps

Linux is the operating system that runs the vast majority of the internet. When you visit a
website, stream a video, or send a message through an app, the servers handling your request
are almost certainly running Linux. As a DevOps engineer, Linux is not optional -- it is the
foundation upon which nearly everything else is built. Understanding Linux is the single most
important technical skill you will develop on this path.

The reason Linux dominates the server world comes down to philosophy. Linux is open source,
meaning anyone can inspect, modify, and distribute the code. This matters enormously in
DevOps because it means you can understand exactly what your operating system is doing, you
can customize it for your workload, and you never have to pay per-server licensing fees. When
you are managing hundreds or thousands of servers, these factors are decisive.

DevOps engineers interact with Linux differently than desktop users interact with Windows or
macOS. We work primarily through the command line -- a text-based interface where you type
commands rather than clicking buttons. This is not because we enjoy making things difficult.
The command line is superior for automation, remote management, and repeatability. You cannot
easily script a sequence of mouse clicks, but you can absolutely script a sequence of
terminal commands. Everything you do manually today, you will automate tomorrow.

There is a famous Unix philosophy that has shaped Linux: "Everything is a file." In Linux,
hardware devices, running processes, network connections, and system configuration are all
represented as files. This means that once you learn how to read, write, and manipulate
files, you have a universal toolkit for interacting with every aspect of the system. This
elegance is why Linux has endured for over 30 years while other operating systems have come
and gone.

Finally, understand that learning Linux is a career investment that compounds over time.
The commands you learn today are the same commands that were used 20 years ago and will still
be used 20 years from now. Linux skills do not become obsolete. Every cloud provider (AWS,
Azure, GCP), every container (Docker), every orchestration platform (Kubernetes), and every
CI/CD pipeline assumes you are comfortable in a Linux environment.

---

## Core Concepts

### What Is Linux?

Linux is an operating system kernel created by Linus Torvalds in 1991. The kernel is the
core software that manages hardware resources -- CPU, memory, disk, network -- and provides
an interface for applications to use them. When people say "Linux," they usually mean a
complete operating system built around the Linux kernel, which includes utilities, a package
manager, and a shell (command-line interpreter).

### Linux Distributions

A Linux distribution (distro) is a complete operating system built on the Linux kernel. Each
distro packages the kernel with different software, configurations, and philosophies.

| Distribution    | Family       | Used In                        | Package Manager |
|-----------------|--------------|--------------------------------|-----------------|
| Ubuntu          | Debian       | Cloud servers, development     | apt             |
| CentOS / Rocky  | Red Hat      | Enterprise servers             | yum / dnf       |
| Amazon Linux    | Red Hat      | AWS EC2 instances              | yum / dnf       |
| Debian          | Debian       | Stable servers, containers     | apt             |
| Alpine          | Independent  | Docker containers (minimal)    | apk             |

As a DevOps engineer, you will most commonly encounter **Ubuntu** and **Amazon Linux / CentOS**.
You do not need to master every distro. The core commands are identical across all of them.

### The Terminal and the Shell

The **terminal** is the application that provides a window for text input and output. The
**shell** is the program running inside the terminal that interprets your commands. The
default shell on most Linux systems is **Bash** (Bourne Again Shell).

When you open a terminal, you see a **prompt** that looks something like this:

```
ubuntu@devops-server:~$
```

This tells you: `username@hostname:current_directory$`. The `$` means you are a normal user.
If you see `#`, you are the root (administrator) user.

### Everything Is a File

In Linux, the phrase "everything is a file" means that the system exposes hardware, processes,
and configuration through a unified file interface:

- `/dev/sda` -- your hard disk
- `/proc/cpuinfo` -- your CPU information
- `/etc/hostname` -- your machine's name
- `/dev/null` -- a "black hole" that discards anything written to it

This is a powerful abstraction. You can read CPU info the same way you read a text file.

### Ways to Access a Linux Machine

| Method          | When to Use                                    |
|-----------------|------------------------------------------------|
| WSL (Windows)   | Local development on a Windows machine         |
| SSH             | Connecting to remote servers (most common)     |
| Virtual Machine | Running Linux inside VirtualBox or VMware      |
| Cloud Instance  | AWS EC2, Azure VM, GCP Compute Engine          |
| Docker          | Running a Linux container on any host OS       |

---

## Step-by-Step Practical

### 1. Open Your Terminal

If you are on WSL, open Windows Terminal and select your Ubuntu profile. If you are on a
Mac, open Terminal.app. If you are SSH-ing into a remote server:

```bash
ssh username@your-server-ip
```

### 2. Find Out Who and Where You Are

```bash
whoami
```

Expected output:
```
ubuntu
```

This tells you which user account you are logged in as.

```bash
hostname
```

Expected output:
```
devops-server
```

This tells you the name of the machine you are on. In a DevOps environment with many
servers, knowing which machine you are connected to prevents costly mistakes.

```bash
pwd
```

Expected output:
```
/home/ubuntu
```

`pwd` stands for "print working directory." It shows your current location in the
filesystem. You always start in your **home directory**.

### 3. Look Around

```bash
ls
```

Expected output:
```
Desktop  Documents  Downloads  Music  Pictures
```

`ls` lists the contents of the current directory. To see more detail:

```bash
ls -la
```

Expected output:
```
total 32
drwxr-xr-x 5 ubuntu ubuntu 4096 Apr 16 10:00 .
drwxr-xr-x 3 root   root   4096 Apr 10 08:00 ..
-rw-r--r-- 1 ubuntu ubuntu  220 Apr 10 08:00 .bash_logout
-rw-r--r-- 1 ubuntu ubuntu 3771 Apr 10 08:00 .bashrc
drwxr-xr-x 2 ubuntu ubuntu 4096 Apr 16 10:00 Documents
drwxr-xr-x 2 ubuntu ubuntu 4096 Apr 16 10:00 Downloads
```

The `-l` flag shows a long listing with permissions, ownership, size, and date. The `-a`
flag shows hidden files (those starting with a dot).

### 4. Navigate the Filesystem

```bash
cd /
ls
```

Expected output:
```
bin  boot  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

You are now at the **root** of the filesystem. Every directory on the system branches from
here.

```bash
cd /etc
ls | head -20
```

This shows the first 20 entries in `/etc`, where system configuration files live.

```bash
cd ~
pwd
```

Expected output:
```
/home/ubuntu
```

The tilde `~` is a shortcut for your home directory. `cd` without arguments also takes you
home.

### 5. Explore System Information

```bash
uname -a
```

Expected output:
```
Linux devops-server 5.15.0-1041-aws #46-Ubuntu SMP ... x86_64 GNU/Linux
```

This shows the kernel version, architecture, and hostname. Useful for verifying what OS
version a server is running.

```bash
cat /etc/os-release
```

Expected output:
```
NAME="Ubuntu"
VERSION="22.04.3 LTS (Jammy Jellyfish)"
ID=ubuntu
ID_LIKE=debian
```

This tells you exactly which distribution and version you are running.

### 6. Essential Navigation Shortcuts

```bash
cd -       # Go back to the previous directory
cd ..      # Go up one level
cd ../..   # Go up two levels
clear      # Clear the terminal screen
history    # Show command history
```

---

## Exercises

1. **System Discovery**: Log into your Linux environment, find out your username, hostname,
   current directory, kernel version, and distribution name. Write all five pieces of
   information down.

2. **Filesystem Exploration**: Starting from `/`, navigate into at least five different
   top-level directories (`/etc`, `/var`, `/tmp`, `/home`, `/usr`) and list their contents.
   Note which directories contain many files and which are nearly empty.

3. **Hidden Files**: Navigate to your home directory and list all hidden files (those starting
   with `.`). Read the contents of `.bashrc` using `cat ~/.bashrc`. This file controls your
   shell environment. Count how many lines it contains using `wc -l ~/.bashrc`.

4. **Command History**: Run `history` and examine the last 20 commands you have executed. Use
   `history | tail -20` to see just the recent ones. Try re-running a previous command using
   `!` followed by the command number from the history output.

5. **Machine Comparison**: If you have access to both WSL and a cloud instance (or two
   different machines), run `uname -a` and `cat /etc/os-release` on both. Compare the
   differences in kernel version, hostname, and distribution.

---

## Knowledge Check

**Q1: Why does Linux dominate the server and DevOps world rather than Windows?**

A1: Linux is open source (free, customizable, inspectable), has no per-server licensing
costs, is highly stable and secure, excels at command-line automation, and has been the
standard for servers for decades. The ability to automate everything through the command
line makes it ideal for DevOps practices.

**Q2: What does "everything is a file" mean in Linux, and why is this useful?**

A2: Linux represents hardware devices, processes, network sockets, and system configuration
as files in the filesystem. This means you can use the same tools (read, write, redirect)
to interact with a disk drive, a running process, or a config file. It provides a universal
and consistent interface for system administration.

**Q3: What is the difference between a terminal and a shell?**

A3: The terminal is the application that provides the text-based window (the visual
interface). The shell is the program running inside the terminal that actually interprets
and executes your commands. Bash is the most common shell. You can run different shells
inside the same terminal.

**Q4: You see the prompt `root@prod-db-01:/var/log#`. What can you determine from this?**

A4: You are logged in as the `root` user (administrator, indicated by both the username and
the `#` prompt), on a machine named `prod-db-01` (likely a production database server),
and your current working directory is `/var/log` (the system log directory). The `#` symbol
at the end confirms root access, as opposed to `$` for normal users.

**Q5: Why do DevOps engineers prefer the command line over graphical interfaces?**

A5: The command line is scriptable (you can automate sequences of commands), works over
remote SSH connections with minimal bandwidth, is reproducible (you can document and repeat
exact steps), is faster for experienced users, and scales to managing many servers
simultaneously. GUIs require manual interaction that cannot be reliably automated.
