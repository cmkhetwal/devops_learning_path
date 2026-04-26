# 01 - System Performance Troubleshooting
## "The Server is Slow" - Complete Diagnosis Guide

---

## FIRST RESPONSE: Quick Health Check (Run These First)

```bash
# 1. System uptime and load average
uptime
# Output: 14:23:01 up 45 days, load average: 4.50, 3.20, 2.10
# Load average: 1min, 5min, 15min
# Rule: If load > number of CPU cores, system is overloaded
# Check CPU count: nproc  or  lscpu | grep "^CPU(s):"

# 2. Quick overview of everything
top -bn1 | head -20
# -b = batch mode (non-interactive output for scripts)
# -n1 = run 1 iteration only
# head -20 = show first 20 lines

# 3. Who is logged in and what are they doing
w

# 4. Check disk space immediately
df -hT

# 5. Check memory
free -h

# 6. Check for OOM (Out of Memory) kills
dmesg | grep -i "oom\|killed process" | tail -20

# 7. Check failed services
systemctl list-units --state=failed
```

---

## SECTION 1: CPU Troubleshooting

### 1.1 Understanding Load Average
```bash
# Get load average
uptime
cat /proc/loadavg

# Get number of CPUs (load should be < this number)
nproc
lscpu | grep "^CPU(s):"
grep -c processor /proc/cpuinfo    # -c = count matching lines

# RULE OF THUMB:
# Load < CPU count = OK
# Load = CPU count = Fully utilized
# Load > CPU count = Overloaded (processes waiting)
# If 15min > 5min > 1min = Load is decreasing (recovering)
# If 1min > 5min > 15min = Load is increasing (getting worse)
```

### 1.2 Real-Time CPU Monitoring
```bash
# top - The classic tool
top
# Inside top:
#   Press '1' = Show individual CPUs
#   Press 'c' = Show full command path
#   Press 'M' = Sort by memory
#   Press 'P' = Sort by CPU
#   Press 'k' = Kill a process
#   Press 'H' = Show threads
#   Press 'f' = Select display fields
#   Press 'z' = Color display
#   Press 'V' = Tree/forest view

# Batch mode (for scripts/logging)
top -bn1 -o %CPU | head -20          # -o %CPU = sort output by CPU usage
top -bn1 -o %MEM | head -20          # -o %MEM = sort output by memory usage
top -bn5 -d2 > /tmp/top_output.txt   # -n5 = 5 iterations, -d2 = 2-second delay between updates

# htop - Better interactive viewer
# Install: yum/dnf install htop  OR  apt install htop
htop
# Features: Mouse support, tree view, search, filter, easy kill

# mpstat - Per-CPU statistics
# Install: yum/dnf install sysstat  OR  apt install sysstat
mpstat -P ALL 2 5
# -P ALL = report stats for ALL individual CPUs
# 2 = interval in seconds between reports
# 5 = number of reports to generate
# Key columns:
# %usr = User space  |  %sys = Kernel  |  %iowait = Waiting for I/O
# %idle = Available   |  %steal = Stolen by hypervisor (VM/Cloud)

# HIGH %iowait = Disk bottleneck (not CPU!)
# HIGH %steal  = Noisy neighbor on shared host / undersized VM
# HIGH %sys    = Kernel overhead, too many context switches
# HIGH %usr    = Application consuming CPU
```

### 1.3 Process-Level CPU Analysis
```bash
# Find top CPU consuming processes
ps aux --sort=-%cpu | head -20
# a = show processes for all users
# u = display user-oriented format (user, %CPU, %MEM, etc.)
# x = include processes without a controlling terminal

# Find top CPU consuming processes with thread count
ps -eLf | awk '{print $2}' | sort | uniq -c | sort -rn | head -20
# -e = select every process
# -L = show threads (one line per thread)
# -f = full-format listing

# Watch a specific process CPU usage
pidstat -p <PID> 1
# -p <PID> = monitor specific process ID
# 1 = report interval in seconds
pidstat -p <PID> -t 1     # -t = also display stats for threads

# CPU usage by specific user
ps -u username -o pid,pcpu,pmem,comm --sort=-%cpu
# -u username = show only processes owned by username
# -o = custom output format (select specific columns)

# Find processes in D state (uninterruptible sleep - usually I/O wait)
ps aux | awk '$8 ~ /D/'
# D state processes are STUCK waiting for I/O - indicates disk/NFS issue

# Context switches (high number = possible issue)
vmstat 1 5
# 1 = interval in seconds between reports
# 5 = number of reports to generate
# 'cs' column = context switches per second
# 'r'  column = processes waiting for CPU
# 'b'  column = processes in uninterruptible sleep

# Per-process context switches
pidstat -w 1 5
# -w = report task switching (context switch) activity
# 1 = interval in seconds, 5 = number of reports
# cswch/s  = voluntary (process waiting for I/O)
# nvcswch/s = involuntary (process forced off CPU - too many processes)

# strace - Trace what a slow process is doing
strace -p <PID> -c              # -p = attach to running PID, -c = summary count of calls
strace -p <PID> -e trace=open   # -e trace=open = filter to only open() system calls
strace -p <PID> -e trace=network # -e trace=network = filter to network-related calls
strace -p <PID> -T              # -T = show time spent in each system call
```

### 1.4 CPU Frequency and Throttling
```bash
# Check CPU frequency (may be throttled for power saving)
cat /proc/cpuinfo | grep "MHz"
lscpu | grep MHz
cpupower frequency-info

# Check if CPU governor is limiting performance
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
# 'powersave' = slower, saves power
# 'performance' = full speed

# Set to performance mode (all CPUs)
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > $cpu
done

# Or using cpupower
cpupower frequency-set -g performance
```

---

## SECTION 2: Memory Troubleshooting

### 2.1 Understanding Memory Usage
```bash
# Quick memory check
free -h
# total    = Total physical RAM
# used     = Currently in use
# free     = Completely unused
# buff/cache = Used for disk cache (can be freed)
# available = Memory that CAN be used (free + reclaimable cache)

# IMPORTANT: "free" being low is NORMAL
# Linux uses free memory for disk cache (good thing!)
# Check "available" column - THIS is what matters
# Problem: When "available" is very low

# Detailed memory info
cat /proc/meminfo

# Key values from /proc/meminfo:
grep -E "MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree|Dirty|Slab" /proc/meminfo
# -E = use extended regex (allows | for alternation)
```

### 2.2 Finding Memory-Hungry Processes
```bash
# Top memory consumers
ps aux --sort=-%mem | head -20

# Memory usage with more detail
ps -eo pid,ppid,user,%mem,%cpu,rss,vsz,comm --sort=-%mem | head -20
# -e = select every process, -o = custom output format (specify columns)
# RSS  = Resident Set Size (actual physical memory used)
# VSZ  = Virtual Size (total virtual memory allocated - usually much larger)

# Detailed memory map of a process
pmap -x <PID>    # -x = show extended format (address, size, RSS, dirty pages)
cat /proc/<PID>/smaps | grep -E "^Size|^Rss|^Pss"

# Total RSS by process name (useful for multi-process apps like Apache)
ps -eo comm,rss | awk '{arr[$1]+=$2} END {for (i in arr) printf "%s\t%d MB\n", i, arr[i]/1024}' | sort -t$'\t' -k2 -rn | head -20

# Watch memory usage over time
vmstat 1 10
# Key columns:
# si = Swap in (from disk to memory) - should be 0
# so = Swap out (from memory to disk) - should be 0
# If si/so are non-zero, system is swapping = VERY SLOW

# Memory usage trending
sar -r 1 10     # -r = report memory utilization; 1 10 = every 1s, 10 times
```

### 2.3 Swap Analysis
```bash
# Check swap usage
swapon --show
free -h | grep Swap

# Which processes are using swap
for pid in /proc/[0-9]*; do
    swap=$(awk '/VmSwap/{print $2}' $pid/status 2>/dev/null)
    name=$(awk '/Name/{print $2}' $pid/status 2>/dev/null)
    if [ -n "$swap" ] && [ "$swap" -gt 0 ] 2>/dev/null; then
        echo "$swap KB - PID: $(basename $pid) - $name"
    fi
done | sort -rn | head -20

# Alternative using smaps
for pid in $(ls /proc/ | grep -E '^[0-9]+$'); do
    swap=$(awk '/Swap:/{s+=$2} END{print s}' /proc/$pid/smaps 2>/dev/null)
    if [ -n "$swap" ] && [ "$swap" -gt 0 ] 2>/dev/null; then
        name=$(cat /proc/$pid/comm 2>/dev/null)
        echo "${swap} KB - PID: $pid - $name"
    fi
done | sort -rn | head -20

# Check swappiness (how aggressively kernel swaps)
cat /proc/sys/vm/swappiness
# Default: 60 (0=avoid swap, 100=swap aggressively)
# For servers: Set to 10
sysctl vm.swappiness=10                          # Temporary
echo "vm.swappiness = 10" >> /etc/sysctl.conf    # Persistent

# Clear swap (WARNING: only if enough RAM available)
# Check available RAM first: free -h
swapoff -a && swapon -a
```

### 2.4 OOM Killer Investigation
```bash
# Check for OOM kills
dmesg | grep -i "oom\|killed process\|out of memory"
journalctl -k | grep -i "oom\|killed"

# Check OOM score of processes (higher = more likely to be killed)
for pid in $(ps -eo pid --no-headers); do
    score=$(cat /proc/$pid/oom_score 2>/dev/null)
    name=$(cat /proc/$pid/comm 2>/dev/null)
    if [ -n "$score" ] && [ "$score" -gt 0 ]; then
        echo "$score $pid $name"
    fi
done | sort -rn | head -20

# Protect a critical process from OOM killer
echo -1000 > /proc/<PID>/oom_score_adj    # Never kill this process
echo 1000  > /proc/<PID>/oom_score_adj    # Kill this first

# Check historical OOM events
grep -i "oom" /var/log/messages      # CentOS/RHEL
grep -i "oom" /var/log/kern.log      # Ubuntu/Debian
```

---

## SECTION 3: Disk I/O Troubleshooting

### 3.1 Disk Space Issues
```bash
# Check disk space on all filesystems
df -hT
# -h = human readable, -T = show filesystem type

# Find large files (top 20 largest files)
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20
# -type f = only regular files, -size +100M = larger than 100 megabytes

# Find large directories
du -sh /* 2>/dev/null | sort -rh | head -20
# -s = summarize (total per argument, not per subdirectory)
# -h = human-readable sizes (K, M, G)
du -sh /var/* 2>/dev/null | sort -rh | head -10
du -sh /home/* 2>/dev/null | sort -rh | head -10

# Find what's using space in /var (common culprit)
du -sh /var/log/* 2>/dev/null | sort -rh | head -10
du -sh /var/cache/* 2>/dev/null | sort -rh | head -10

# Check inode usage (can run out even with disk space available!)
df -i    # -i = show inode usage instead of block usage
# If inodes are at 100%, you have too many small files
# Find directory with most files:
find / -xdev -printf '%h\n' 2>/dev/null | sort | uniq -c | sort -rn | head -20

# Find deleted files still holding space (process has file open)
lsof +L1    # +L1 = list files with link count < 1 (deleted but still open)
# To reclaim: restart the process holding the deleted file

# ncdu - Interactive disk usage explorer
# Install: yum/dnf install ncdu  OR  apt install ncdu
ncdu /
```

### 3.2 Disk I/O Performance
```bash
# iostat - Disk I/O statistics
# Install: yum/dnf install sysstat  OR  apt install sysstat
iostat -xz 2 5
# -x = show extended statistics
# -z = omit devices with no activity
# 2 = interval in seconds, 5 = number of reports
# Key columns:
# %util   = How busy the disk is (>80% = bottleneck)
# await   = Average wait time in ms (>10ms for SSD = issue)
# r_await = Read wait time
# w_await = Write wait time
# avgqu-sz = Queue depth (>1 means requests are queuing)
# r/s, w/s = Reads/writes per second

# iotop - Top for I/O (shows per-process I/O)
# Install: yum/dnf install iotop  OR  apt install iotop
iotop -oP
# -o = Only show processes doing I/O
# -P = Show processes not threads
# Press 'a' for accumulated I/O

# Per-process I/O stats
pidstat -d 1 5
# -d = report I/O statistics per process
# 1 = interval in seconds, 5 = number of reports
# kB_rd/s = KB read per second
# kB_wr/s = KB written per second

# Find which process is doing heavy I/O
iotop -boPn 5
# -b = batch mode (non-interactive, for logging)
# -o = only show processes doing I/O
# -P = show processes instead of threads
# -n 5 = run 5 iterations then exit

# Check for processes stuck in I/O wait (D state)
ps aux | awk '$8 ~ /D/ {print}'
# These are processes stuck waiting for disk

# Check disk health
smartctl -a /dev/sda                    # -a = show all SMART info (health, attributes, logs)
smartctl -H /dev/sda                    # -H = show only SMART health status (PASSED/FAILED)
# Install: yum/dnf install smartmontools  OR  apt install smartmontools
```

### 3.3 Disk Performance Testing
```bash
# Test sequential write speed
dd if=/dev/zero of=/tmp/testfile bs=1G count=1 oflag=direct 2>&1
# if=/dev/zero = read from /dev/zero (infinite null bytes)
# of=/tmp/testfile = write to this output file
# bs=1G = block size of 1 gigabyte per read/write operation
# count=1 = copy only 1 block
# oflag=direct = bypass filesystem write cache for true disk speed

# Test sequential read speed
dd if=/tmp/testfile of=/dev/null bs=1G count=1 iflag=direct 2>&1
# iflag=direct = bypass filesystem read cache

# fio - Professional I/O benchmarking
# Install: yum/dnf install fio  OR  apt install fio

# Random read test
fio --name=randread --ioengine=libaio --iodepth=32 --rw=randread \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=30 \
    --filename=/tmp/fio_test
# --ioengine=libaio = use Linux native async I/O
# --iodepth=32 = keep 32 I/O requests in-flight at once
# --rw=randread = random read workload pattern
# --bs=4k = block size of 4 kilobytes per I/O operation
# --direct=1 = bypass OS page cache (O_DIRECT)
# --size=1G = total size of test file
# --numjobs=4 = spawn 4 parallel workers
# --runtime=30 = stop after 30 seconds

# Random write test
fio --name=randwrite --ioengine=libaio --iodepth=32 --rw=randwrite \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=30 \
    --filename=/tmp/fio_test

# Mixed read/write (70/30)
fio --name=mixed --ioengine=libaio --iodepth=32 --rw=randrw \
    --rwmixread=70 --bs=4k --direct=1 --size=1G --numjobs=4 \
    --runtime=30 --filename=/tmp/fio_test

# Clean up
rm -f /tmp/testfile /tmp/fio_test
```

---

## SECTION 4: Network Troubleshooting

### 4.1 Quick Network Checks
```bash
# Check all interfaces and IPs
ip addr show
ip -4 addr show        # -4 = show only IPv4 addresses
ip -brief addr show    # -brief = concise one-line-per-interface output

# Check routing table
ip route show
ip route get 8.8.8.8   # How would traffic reach Google DNS

# Check DNS resolution
cat /etc/resolv.conf
nslookup google.com
dig google.com
host google.com

# Check connectivity
ping -c 4 8.8.8.8              # -c 4 = send 4 packets then stop
ping -c 4 google.com           # DNS + connectivity
traceroute google.com           # Path to destination
mtr google.com                  # Better traceroute (combines ping + traceroute)

# Check listening ports
ss -tlnp                       # TCP listening ports with process
# -t = TCP sockets, -l = listening only, -n = numeric (no DNS), -p = show process
ss -ulnp                       # -u = UDP sockets (l, n, p same as above)
ss -tlnp | grep :80            # Who's listening on port 80
netstat -tlnp                  # Alternative (older tool)
```

### 4.2 Connection Analysis
```bash
# Count connections by state
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn

# Count connections per IP
ss -tn | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -20

# Check for too many TIME_WAIT connections
ss -tan state time-wait | wc -l

# Check for too many CLOSE_WAIT (application not closing connections)
ss -tan state close-wait | wc -l
ss -tanp state close-wait    # Show which process

# Check for SYN flood
ss -tan state syn-recv | wc -l

# Connection count per port
ss -tn | awk '{print $4}' | rev | cut -d: -f1 | rev | sort | uniq -c | sort -rn | head -10

# Check network errors and drops
ip -s link show          # All interfaces with statistics
cat /proc/net/dev        # Network device statistics
ethtool -S eth0          # Detailed NIC statistics

# Check for dropped packets
netstat -i
# If RX-DRP or TX-DRP > 0, packets are being dropped
```

### 4.3 Bandwidth and Traffic Analysis
```bash
# Real-time bandwidth per interface
# Install: yum/dnf install iftop  OR  apt install iftop
iftop -i eth0

# nload - Simple bandwidth monitor
# Install: yum/dnf install nload  OR  apt install nload
nload eth0

# sar network statistics
sar -n DEV 1 5          # -n DEV = network device stats; 1 5 = every 1s, 5 times
sar -n SOCK 1 5         # -n SOCK = socket usage stats
sar -n TCP 1 5          # -n TCP = TCP traffic stats

# nethogs - Bandwidth per process
# Install: yum/dnf install nethogs  OR  apt install nethogs
nethogs eth0

# Check interface speed and duplex
ethtool eth0 | grep -i "speed\|duplex\|link detected"

# tcpdump - Packet capture
tcpdump -i eth0 -nn port 80                    # HTTP traffic
# -i eth0 = capture on interface eth0
# -nn = don't resolve hostnames or port names (faster output)
tcpdump -i eth0 -nn host 192.168.1.100         # Traffic to/from specific host
tcpdump -i eth0 -nn port 443 -c 100            # -c 100 = stop after 100 packets
tcpdump -i eth0 -nn -w /tmp/capture.pcap       # -w = write raw packets to file
tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-syn != 0'  # SYN packets only

# Check for packet loss
ping -c 100 -i 0.2 <target_ip>   # -i 0.2 = 0.2-second interval between packets
mtr -rw -c 100 <target_ip>
# -r = report mode (non-interactive, run then print results)
# -w = wide report (show full hostnames)
# -c 100 = send 100 probes per hop
```

### 4.4 DNS Troubleshooting
```bash
# Check DNS configuration
cat /etc/resolv.conf
cat /etc/nsswitch.conf | grep hosts

# DNS lookup tests
dig example.com                  # Full query
dig example.com +short           # +short = show only the answer, no extra info
dig @8.8.8.8 example.com        # @server = query a specific DNS server
dig example.com MX               # Mail records
dig example.com NS               # Nameservers
dig -x 1.2.3.4                   # -x = reverse DNS lookup (IP to hostname)
dig example.com +trace            # +trace = trace full delegation path from root

# Test DNS response time
dig example.com | grep "Query time"
time nslookup example.com

# Flush DNS cache
# systemd-resolved (Ubuntu 18+)
systemd-resolve --flush-caches
resolvectl flush-caches

# nscd cache
nscd -i hosts

# Check if DNS is causing slowness
time curl -o /dev/null -s -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" https://example.com
# -o /dev/null = discard response body
# -s = silent mode (no progress bar)
# -w = write out timing variables after completion
```

---

## SECTION 5: Process Troubleshooting

### 5.1 Process Investigation
```bash
# List all processes - tree view
ps auxf                    # f = forest/tree view showing parent-child hierarchy
pstree -p                  # Process tree with PIDs

# Find specific process
ps aux | grep nginx
pgrep -a nginx             # -a = show PID and full command line
pidof nginx                # Just PIDs

# Detailed process info
ls -la /proc/<PID>/
cat /proc/<PID>/status     # Process status
cat /proc/<PID>/cmdline    # Full command line
ls -la /proc/<PID>/fd      # Open file descriptors
cat /proc/<PID>/limits     # Resource limits
cat /proc/<PID>/io         # I/O statistics

# Count open files per process
lsof -p <PID> | wc -l     # -p = list open files for specific PID
ls /proc/<PID>/fd | wc -l

# Check file descriptor limits
ulimit -n                          # Current shell limit
cat /proc/<PID>/limits | grep "open files"

# Find processes by open file
lsof /var/log/syslog               # Who has this file open
lsof -i :80                        # -i = list files matching internet address/port
lsof -u username                   # -u = list files opened by specified user
lsof -c nginx                      # -c = list files opened by processes starting with name

# Zombie processes
ps aux | awk '$8 == "Z"'           # Find zombies
# To fix: kill the PARENT process (PPID), not the zombie
ps -eo pid,ppid,stat,comm | awk '$3 ~ /Z/ {print "Zombie PID:", $1, "Parent PID:", $2, $4}'
# -e = every process, -o = custom output columns
```

### 5.2 Process Signals and Management
```bash
# Signal reference
# SIGHUP  (1)  = Reload configuration
# SIGINT  (2)  = Interrupt (Ctrl+C)
# SIGKILL (9)  = Force kill (cannot be caught)
# SIGTERM (15) = Graceful termination (default)
# SIGUSR1 (10) = User-defined (log rotation in nginx)
# SIGUSR2 (12) = User-defined

kill -15 <PID>              # Graceful stop (try this first!)
kill -9 <PID>               # Force kill (last resort)
kill -1 <PID>               # Reload config (HUP)
killall nginx               # Kill all nginx processes
pkill -f "pattern"          # Kill by command pattern

# Process priority (nice)
nice -n 10 command           # -n 10 = set niceness to 10 (lower priority)
renice -n 5 -p <PID>        # -n 5 = new niceness value, -p = target process ID
# -20 = highest priority, 19 = lowest priority

# CPU affinity (pin process to specific CPUs)
taskset -p <PID>             # -p = show/set affinity for existing PID
taskset -cp 0,1 <PID>       # -c = specify CPU list, -p = target PID
taskset -c 0-3 command       # -c 0-3 = restrict to CPUs 0 through 3
```

---

## SECTION 6: Historical Performance Analysis

### 6.1 Using sar (System Activity Reporter)
```bash
# Install sysstat
# CentOS/RHEL: yum install sysstat && systemctl enable --now sysstat
# Ubuntu/Debian: apt install sysstat && sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat && systemctl restart sysstat

# CPU history
sar -u                     # -u = CPU utilization report
sar -u -f /var/log/sa/sa25 # -f = read from specific data file (25th)
sar -u -s 09:00:00 -e 17:00:00  # -s = start time, -e = end time

# Memory history
sar -r                     # -r = memory utilization report
sar -S                     # -S = swap space utilization report

# Disk I/O history
sar -b                     # -b = I/O transfer rate statistics
sar -d                     # -d = per block device I/O activity

# Network history
sar -n DEV                 # -n DEV = network device statistics
sar -n TCP                 # -n TCP = TCP connection statistics

# Load average history
sar -q                     # -q = run queue length and load averages

# All-in-one report
sar -A                     # -A = report all collected statistics
```

### 6.2 Quick Diagnostic Script
```bash
#!/bin/bash
# Save as: /usr/local/bin/syshealth.sh
# Quick system health check

echo "=========================================="
echo "SYSTEM HEALTH CHECK - $(date)"
echo "=========================================="
echo ""

echo "--- SYSTEM INFO ---"
hostname
uname -r
uptime
echo ""

echo "--- CPU LOAD ---"
echo "CPUs: $(nproc)"
cat /proc/loadavg
mpstat 1 1 2>/dev/null || echo "Install sysstat for detailed CPU stats"
echo ""

echo "--- MEMORY ---"
free -h
echo ""

echo "--- SWAP USAGE ---"
swapon --show 2>/dev/null
echo ""

echo "--- DISK SPACE ---"
df -hT | grep -v tmpfs
echo ""

echo "--- DISK I/O ---"
iostat -x 1 1 2>/dev/null || echo "Install sysstat for I/O stats"
echo ""

echo "--- TOP 10 CPU PROCESSES ---"
ps aux --sort=-%cpu | head -11
echo ""

echo "--- TOP 10 MEMORY PROCESSES ---"
ps aux --sort=-%mem | head -11
echo ""

echo "--- NETWORK CONNECTIONS ---"
echo "ESTABLISHED: $(ss -tn state established | wc -l)"
echo "TIME_WAIT:   $(ss -tn state time-wait | wc -l)"
echo "CLOSE_WAIT:  $(ss -tn state close-wait | wc -l)"
echo ""

echo "--- FAILED SERVICES ---"
systemctl list-units --state=failed --no-pager
echo ""

echo "--- RECENT ERRORS (last 30 min) ---"
journalctl --since "30 min ago" -p err --no-pager | tail -20
echo ""

echo "--- OOM KILLS ---"
dmesg | grep -i "oom\|killed process" | tail -5
echo ""

echo "=========================================="
echo "HEALTH CHECK COMPLETE"
echo "=========================================="
```

---

## SECTION 7: "Server is Slow" - Complete Flowchart

```
Step 1: uptime → Check load average
  ├─ Load HIGH → Go to Step 2
  └─ Load OK → Go to Step 4

Step 2: mpstat -P ALL 1 3 → Check CPU breakdown
  ├─ HIGH %usr     → Application issue → ps aux --sort=-%cpu → Profile app
  ├─ HIGH %sys     → Kernel issue → Check context switches (vmstat)
  ├─ HIGH %iowait  → Disk bottleneck → Go to Step 3
  ├─ HIGH %steal   → VM/hypervisor issue → Contact cloud provider or move VM
  └─ HIGH %soft    → Network interrupt issue → Check network

Step 3: iostat -xz 1 3 → Check disk I/O
  ├─ HIGH %util    → Disk saturated → iotop → Find I/O heavy process
  ├─ HIGH await    → Slow disk → Check SMART / disk health
  └─ Check: df -h  → Disk full? → Find large files/logs → Clean up

Step 4: free -h → Check memory
  ├─ LOW available → Memory pressure → Go to Step 5
  └─ Memory OK → Go to Step 6

Step 5: Memory issue
  ├─ Check swap: swapon --show → HIGH swap use → Find swapping processes
  ├─ Check OOM: dmesg | grep oom → Processes being killed?
  └─ Top memory: ps aux --sort=-%mem → Identify memory hog

Step 6: Network check
  ├─ ss -s → Connection count → Too many? → Check for DDoS/connection leak
  ├─ iftop → Bandwidth check → Saturated? → Find heavy traffic source
  └─ Check DNS: dig example.com → Slow DNS? → Check /etc/resolv.conf

Step 7: Application-level
  ├─ Check logs: journalctl -u SERVICE → Errors?
  ├─ Check config: Has anything changed recently?
  ├─ Check connections: Can app reach DB/API/dependencies?
  └─ strace -p PID → What is the process actually doing?
```
