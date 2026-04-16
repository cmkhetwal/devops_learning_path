# Lesson 4: Process Management

## Why This Matters in DevOps

A server is only as reliable as the processes running on it. When your web application goes
down at 3 AM, your ability to diagnose the problem depends entirely on your understanding of
process management. Can you find which process is consuming all the memory? Can you identify
a runaway process that is pegging the CPU at 100%? Can you gracefully restart a service
without dropping user connections? These are not theoretical scenarios -- they are the daily
reality of operating production systems.

In DevOps, you do not just deploy software -- you keep it running. Process management is the
discipline of understanding what is running on a system, how much resources each process
consumes, how processes relate to each other (parent-child relationships), and how to control
their lifecycle (start, stop, restart, reload). A DevOps engineer who cannot navigate `ps`,
`top`, and `systemctl` is like a mechanic who cannot open the hood.

Modern Linux systems use **systemd** as their init system -- the first process that starts
when the machine boots and the parent of all other processes. systemd manages services
(long-running background processes like web servers, databases, and monitoring agents) through
unit files that define how to start, stop, and monitor each service. Understanding systemd is
essential because every application you deploy in production will be managed as a systemd
service.

The concept of **signals** is central to process management. When you press Ctrl+C, you are
sending a SIGINT signal. When you run `kill`, you are sending SIGTERM. When a process refuses
to die, you send SIGKILL. Each signal has a different meaning and a different effect.
Understanding signals allows you to gracefully shut down applications (giving them time to
finish in-progress requests) rather than brutally killing them (which can corrupt data or
leave connections hanging).

Resource limits and monitoring tie process management to capacity planning. If a Java
application is allowed to allocate unlimited memory, it can consume everything available and
crash the entire server (including other applications running on it). Setting resource limits
with `ulimit` and monitoring with tools like `top` and `htop` ensures that no single process
can destabilize the system. This defensive approach is fundamental to operating reliable
infrastructure.

---

## Core Concepts

### What Is a Process?

A process is a running instance of a program. When you run `ls`, a process is created, it
executes, and it terminates. When you start Nginx, a process is created that runs
continuously in the background.

Every process has:

| Attribute   | Description                                      |
|-------------|--------------------------------------------------|
| PID         | Process ID -- unique numeric identifier          |
| PPID        | Parent Process ID -- who started this process    |
| UID         | User ID -- which user owns the process           |
| State       | Running, sleeping, stopped, zombie               |
| CPU %       | Percentage of CPU time being used                |
| MEM %       | Percentage of system memory being used           |

### Process States

| State       | Symbol | Meaning                                        |
|-------------|--------|------------------------------------------------|
| Running     | R      | Currently executing on the CPU                 |
| Sleeping    | S      | Waiting for an event (most common state)       |
| Stopped     | T      | Suspended (e.g., by Ctrl+Z)                    |
| Zombie      | Z      | Finished but parent has not collected exit code |
| Defunct     | D      | Uninterruptible sleep (usually I/O wait)       |

### Signals

| Signal   | Number | Default Action | Use Case                              |
|----------|--------|----------------|---------------------------------------|
| SIGHUP   | 1      | Terminate      | Reload configuration                  |
| SIGINT   | 2      | Terminate      | Ctrl+C -- interrupt                   |
| SIGKILL  | 9      | Terminate      | Force kill (cannot be caught)         |
| SIGTERM  | 15     | Terminate      | Graceful termination (default kill)   |
| SIGSTOP  | 19     | Stop           | Pause process (cannot be caught)      |
| SIGCONT  | 18     | Continue       | Resume a stopped process              |

**Important**: Always try SIGTERM (15) before SIGKILL (9). SIGTERM allows the process to
clean up (close files, finish transactions, release locks). SIGKILL terminates immediately
with no cleanup, which can lead to data corruption.

### systemd and Services

systemd is the init system on modern Linux. It manages services through **unit files**
located in `/etc/systemd/system/` and `/lib/systemd/system/`.

A basic unit file (`/etc/systemd/system/myapp.service`):

```ini
[Unit]
Description=My Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/start.sh
ExecStop=/opt/myapp/bin/stop.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## Step-by-Step Practical

### 1. View Running Processes

```bash
ps aux | head -15
```

Expected output:
```
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 169396 13256 ?        Ss   Apr10   0:12 /lib/systemd/systemd
root         2  0.0  0.0      0     0 ?        S    Apr10   0:00 [kthreadd]
root       432  0.0  0.1  47540 15264 ?        Ss   Apr10   0:05 /lib/systemd/systemd-journald
syslog     587  0.0  0.0 224340  5328 ?        Ssl  Apr10   0:15 /usr/sbin/rsyslogd
www-data  1234  0.1  0.3 143820 28672 ?        S    Apr10   2:30 nginx: worker process
```

Key columns: USER (who owns it), PID (process ID), %CPU, %MEM, COMMAND.

Find a specific process:

```bash
ps aux | grep nginx
```

Expected output:
```
root      1233  0.0  0.1 141312  8192 ?  Ss  Apr10  0:00 nginx: master process
www-data  1234  0.1  0.3 143820 28672 ?  S   Apr10  2:30 nginx: worker process
ubuntu    5678  0.0  0.0  17668  2456 ?  S+  10:30  0:00 grep --color=auto nginx
```

### 2. Monitor Processes in Real Time

```bash
top -bn1 | head -20
```

Expected output:
```
top - 10:35:00 up 6 days,  2:35,  1 user,  load average: 0.15, 0.10, 0.05
Tasks: 128 total,   1 running, 127 sleeping,   0 stopped,   0 zombie
%Cpu(s):  2.3 us,  1.0 sy,  0.0 ni, 96.5 id,  0.2 wa,  0.0 hi,  0.0 si
MiB Mem :   3933.6 total,   1234.5 free,   1567.8 used,   1131.3 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   2123.4 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 1234 www-data  20   0  143820  28672  12048 S   1.3   0.7   2:30.45 nginx
  587 syslog    20   0  224340   5328   4096 S   0.3   0.1   0:15.22 rsyslogd
```

Key indicators:
- **load average**: System load over 1, 5, 15 minutes. Values above your CPU count indicate overload.
- **%Cpu(s)**: `us` = user processes, `sy` = system/kernel, `id` = idle, `wa` = I/O wait.
- **MiB Mem**: Total, free, used, and cached memory.

For an interactive and colorful view, use `htop` (install with `sudo apt install htop`).

### 3. Send Signals to Processes

Start a background process for testing:

```bash
sleep 300 &
echo "Background PID: $!"
```

Expected output:
```
[1] 6789
Background PID: 6789
```

Send SIGTERM (graceful shutdown):

```bash
kill 6789
```

If a process does not respond to SIGTERM:

```bash
kill -9 6789    # SIGKILL -- force kill
```

Kill all processes by name:

```bash
sleep 300 &
sleep 300 &
killall sleep
```

### 4. Manage Services with systemctl

```bash
sudo systemctl status ssh
```

Expected output:
```
 ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-04-10 08:00:00 UTC; 6 days ago
   Main PID: 842 (sshd)
      Tasks: 1 (limit: 4651)
     Memory: 5.2M
     CGroup: /system.slice/ssh.service
             └─842 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
```

Common systemctl commands:

```bash
sudo systemctl start nginx       # Start a service
sudo systemctl stop nginx        # Stop a service
sudo systemctl restart nginx     # Stop then start
sudo systemctl reload nginx      # Reload config without downtime
sudo systemctl enable nginx      # Start automatically on boot
sudo systemctl disable nginx     # Do not start on boot
sudo systemctl is-active nginx   # Check if running
sudo systemctl is-enabled nginx  # Check if enabled on boot
```

### 5. Create a Custom Service

Create a simple script:

```bash
sudo mkdir -p /opt/healthcheck
sudo tee /opt/healthcheck/check.sh << 'SCRIPT'
#!/bin/bash
while true; do
    echo "$(date): System healthy - Load: $(cat /proc/loadavg | cut -d' ' -f1-3)" >> /var/log/healthcheck.log
    sleep 60
done
SCRIPT
sudo chmod +x /opt/healthcheck/check.sh
```

Create the service unit file:

```bash
sudo tee /etc/systemd/system/healthcheck.service << 'EOF'
[Unit]
Description=System Health Check Service
After=network.target

[Service]
Type=simple
ExecStart=/opt/healthcheck/check.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable healthcheck
sudo systemctl start healthcheck
sudo systemctl status healthcheck
```

### 6. View Logs with journalctl

```bash
sudo journalctl -u ssh --since "1 hour ago" --no-pager | tail -10
```

Follow logs in real time (like `tail -f`):

```bash
sudo journalctl -u healthcheck -f
# Press Ctrl+C to stop following
```

Show logs from the current boot only:

```bash
sudo journalctl -b -u ssh --no-pager | tail -20
```

### 7. Check Resource Limits

```bash
ulimit -a
```

Expected output:
```
core file size          (blocks, -c) 0
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
max locked memory       (kbytes, -l) 65536
max memory size         (kbytes, -m) unlimited
open files                      (-n) 1024
...
```

The `open files` limit (1024) is often too low for web servers. To see the limit for a
running process:

```bash
cat /proc/1/limits   # Replace 1 with actual PID
```

---

## Exercises

1. **Process Investigation**: Run `ps aux --sort=-%mem | head -10` to find the top 10
   memory-consuming processes. Then run `ps aux --sort=-%cpu | head -10` for CPU. Document
   what each top process is and whether it looks normal.

2. **Signal Practice**: Start three `sleep 600` background processes. Kill the first with
   SIGTERM, the second with SIGKILL, and the third with SIGHUP. Verify each was terminated
   with `jobs` and `ps`.

3. **Custom Service**: Create a systemd service that runs a script writing the current date
   and disk usage (`df -h`) to a log file every 30 seconds. Start it, verify it is working,
   check its logs with `journalctl`, then stop and disable it.

4. **Zombie Hunt**: Run `ps aux | grep Z` to find any zombie processes on your system.
   Research why zombies occur (hint: the parent process has not called `wait()` to collect
   the child's exit status).

5. **Load Average Analysis**: Run `uptime` and `cat /proc/loadavg`. Research what the three
   load average numbers mean. Determine how many CPU cores your system has with `nproc`.
   Calculate whether your system is currently overloaded (load average > number of cores).

---

## Knowledge Check

**Q1: Why should you try SIGTERM before SIGKILL when stopping a process?**

A1: SIGTERM (signal 15) allows the process to catch the signal and perform cleanup: closing
file handles, finishing database transactions, flushing buffers, and releasing locks. SIGKILL
(signal 9) terminates the process immediately with no chance for cleanup, which can result
in corrupted files, orphaned locks, incomplete transactions, and data loss. Always escalate
from SIGTERM to SIGKILL only if the process does not respond.

**Q2: What does `systemctl enable nginx` do versus `systemctl start nginx`?**

A2: `start` immediately runs the service right now. `enable` configures the service to start
automatically when the system boots, but does not start it immediately. To both start now
and enable on boot, run both commands. This distinction matters because a server reboot
should bring all critical services back up automatically.

**Q3: A system has a load average of 4.50, 3.20, 1.10 and has 2 CPU cores. What does this
tell you?**

A3: The load average shows system load over 1, 5, and 15 minutes. With 2 CPU cores, a load
above 2.0 means processes are waiting for CPU time. The current 1-minute load (4.50) is
significantly above capacity, suggesting the system is overloaded right now. The trend is
increasing (1.10 -> 3.20 -> 4.50), meaning the problem is getting worse, not better.
Immediate investigation is needed.

**Q4: What is the purpose of the `[Install]` section in a systemd unit file?**

A4: The `[Install]` section defines how the service integrates into the boot process. The
`WantedBy=multi-user.target` line means the service should start when the system reaches
multi-user mode (normal operation with networking). Without this section, `systemctl enable`
would not know when to start the service during boot. Other targets include
`graphical.target` for GUI systems.

**Q5: How do you view only the logs for a specific service from the last 30 minutes?**

A5: Use `sudo journalctl -u service-name --since "30 minutes ago"`. The `-u` flag filters
by service unit name, and `--since` filters by time. You can also use `--follow` or `-f`
to watch logs in real time, similar to `tail -f`. This is invaluable for debugging service
startup failures or runtime errors.
