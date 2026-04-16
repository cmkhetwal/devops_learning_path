# eBPF Philosophy: The Programmable Kernel Revolution

## Why This Matters in DevOps

Every packet that enters or leaves a container traverses the Linux kernel's
networking stack. Every system call an application makes passes through the kernel.
Every file access, every socket connection, every process creation -- the kernel
sees all of it.

Traditionally, modifying kernel behavior meant writing kernel modules: a slow,
dangerous, and complex process that required deep kernel expertise and risked
crashing the entire system. eBPF (extended Berkeley Packet Filter) changes this
fundamentally. It allows you to run custom programs inside the kernel safely,
without modifying kernel source code or loading kernel modules.

For DevOps engineers, eBPF is the foundation of next-generation networking
(Cilium), observability (Hubble, Pixie), and security (Tetragon, Falco). Understanding
eBPF is understanding why these tools are architecturally superior to their
predecessors, and why the industry is rapidly moving toward eBPF-based
infrastructure.

---

## Core Concepts

### What Is eBPF?

eBPF stands for **extended Berkeley Packet Filter**. The original BPF was created
in 1992 for packet filtering (used by `tcpdump`). It was a simple virtual machine
that could evaluate whether a network packet matched a filter expression.

eBPF (introduced in Linux 3.18, 2014) extended this concept dramatically. It is
now a general-purpose, in-kernel virtual machine that can:

- Inspect and modify network packets at wire speed
- Trace kernel and user-space functions
- Monitor system calls in real time
- Enforce security policies
- Collect performance metrics with near-zero overhead

```
Traditional approach:
  Application --> System Call --> Kernel --> Hardware
  (No visibility, no control between these layers)

eBPF approach:
  Application --> System Call --> [eBPF program] --> Kernel --> Hardware
  (Custom logic at every critical point)
```

### Why eBPF Is Revolutionary

#### 1. Safety

eBPF programs are verified before execution by the **eBPF verifier**, a static
analysis engine in the kernel. The verifier ensures:

- No infinite loops (programs must terminate)
- No out-of-bounds memory access
- No use of uninitialized variables
- Stack size is bounded (512 bytes)
- Program complexity is bounded

If verification fails, the program is rejected. It never runs. This makes eBPF
fundamentally safer than kernel modules, which can crash the kernel with a single
null pointer dereference.

#### 2. Performance

eBPF programs are JIT-compiled to native machine code. They run at near-native
speed without the overhead of context switches between user space and kernel
space. This is critical for networking:

```
iptables (traditional):
  Packet --> netfilter hooks --> iptables rules (linear scan) --> forward/drop
  Latency: O(n) where n = number of rules
  With 10,000 rules: significant latency

eBPF/Cilium:
  Packet --> eBPF program (hash lookup) --> forward/drop
  Latency: O(1) regardless of policy count
  With 10,000 rules: same latency as 10 rules
```

#### 3. Programmability

Unlike static kernel features (iptables, netfilter), eBPF programs can implement
arbitrary logic:

- Parse application-layer protocols (HTTP, gRPC, DNS, Kafka)
- Make forwarding decisions based on Kubernetes identities
- Collect custom metrics without modifying applications
- Enforce security policies based on process context

### eBPF vs Traditional Networking (iptables)

Kubernetes traditionally uses **kube-proxy** with iptables for service routing:

```
kube-proxy + iptables:
  - Creates iptables rules for every Service endpoint
  - 100 Services x 10 endpoints = 1,000+ iptables rules
  - Rules are evaluated linearly (O(n) per packet)
  - No Layer 7 awareness (cannot inspect HTTP headers)
  - No identity awareness (uses IP addresses only)
  - Connection tracking overhead
  - Difficult to debug (iptables -L produces unreadable output)

eBPF (Cilium):
  - Uses BPF hash maps for service routing
  - O(1) lookup regardless of number of services
  - Full Layer 7 protocol awareness
  - Identity-based policies (Kubernetes labels, not IPs)
  - Efficient connection tracking in BPF maps
  - Rich observability through Hubble
```

At scale, the difference is dramatic. A cluster with 5,000 services and iptables
can have 25,000+ rules, causing measurable latency and CPU overhead. Cilium with
eBPF handles the same scale with constant-time lookups.

### The Linux Kernel Data Path

Understanding where eBPF programs attach is key to understanding their power:

```
                    User Space
  ─────────────────────────────────────────
                    Kernel Space

  Network Interface Card (NIC)
       │
       ▼
  [XDP] ─── eBPF programs at the driver level (fastest)
       │
       ▼
  Traffic Control (tc)
       │
       ▼
  [tc ingress] ─── eBPF programs on ingress
       │
       ▼
  Netfilter / iptables
       │
       ▼
  Socket Layer
       │
       ▼
  [socket ops] ─── eBPF programs on socket operations
       │
       ▼
  Application

  Plus: kprobes, tracepoints, perf events, LSM hooks, cgroup hooks...
```

**XDP (eXpress Data Path)** - Runs before the kernel allocates a socket buffer.
Can process millions of packets per second per core. Used for DDoS mitigation
and load balancing.

**TC (Traffic Control)** - Runs after socket buffer allocation. Has access to
full packet metadata. Used by Cilium for pod networking.

**Socket operations** - Runs on socket events (connect, accept, sendmsg). Used
for socket-level load balancing and acceleration.

**Kprobes/Tracepoints** - Attach to kernel functions for tracing and observability.
Used by Tetragon for runtime security.

**LSM (Linux Security Modules)** - Attach to security hooks. Used for mandatory
access control.

### eBPF Use Cases

| Domain | Use Case | Tool |
|---|---|---|
| Networking | Container networking, service mesh | Cilium |
| Networking | Load balancing | Cilium, Katran (Facebook) |
| Networking | DDoS mitigation | XDP-based filters |
| Observability | Network flow logs | Hubble |
| Observability | Application performance | Pixie, bpftrace |
| Observability | CPU profiling | BCC tools, bpftrace |
| Security | Runtime threat detection | Tetragon, Falco |
| Security | Network policy enforcement | Cilium |
| Security | Syscall filtering | seccomp-bpf |
| Storage | I/O tracing | BCC biosnoop |

### eBPF Program Lifecycle

```
1. Write    - Program written in restricted C (or generated by tools)
2. Compile  - Compiled to eBPF bytecode (using LLVM/Clang)
3. Load     - Loaded into the kernel via bpf() syscall
4. Verify   - Kernel verifier checks safety properties
5. JIT      - Bytecode JIT-compiled to native machine code
6. Attach   - Attached to a hook point (XDP, tc, kprobe, etc.)
7. Execute  - Runs on every event at the hook point
8. Detach   - Removed when no longer needed
```

```bash
# View loaded eBPF programs
bpftool prog list
# 42: cgroup_device  tag abc123def456  gpl
#     loaded_at 2024-03-14T10:00:00+0000  uid 0
#     xlated 296B  jited 192B  memlock 4096B

# View eBPF maps (shared data structures)
bpftool map list
# 15: hash  name cilium_ipcache  flags 0x1
#     key 20B  value 24B  max_entries 512000  memlock 32768000B
```

### BPF Maps

BPF maps are key-value data structures shared between eBPF programs and user
space. They are how eBPF programs store state and communicate:

```
User Space (cilium-agent)
    │
    │ read/write via bpf() syscall
    ▼
┌───────────────────┐
│    BPF Map        │
│  (key → value)    │
│                   │
│  Pod IP → Identity│
│  Service → Backend│
│  Flow → Metrics   │
└───────────────────┘
    ▲
    │ read/write from eBPF program
    │
Kernel Space (eBPF program on tc hook)
```

Common map types:

| Type | Description | Use Case |
|---|---|---|
| Hash | Key-value hash table | IP to identity mapping |
| Array | Fixed-size array | Per-CPU counters |
| LRU Hash | Hash with LRU eviction | Connection tracking |
| Ring Buffer | Efficient event streaming | Flow logs to user space |
| Per-CPU Hash | One hash per CPU core | High-performance counters |
| LPM Trie | Longest prefix match | CIDR-based routing |

### Why eBPF Is the Future of Cloud-Native

The industry is converging on eBPF for three reasons:

1. **Performance at scale** - As clusters grow to thousands of services, O(1)
   lookups versus O(n) iptables rules makes a measurable difference in latency
   and CPU usage.

2. **Protocol awareness** - Modern microservices use HTTP/2, gRPC, and Kafka.
   eBPF can parse these protocols in the kernel, enabling Layer 7 network
   policies, protocol-aware load balancing, and application-level observability
   without sidecars.

3. **Unified platform** - Instead of separate tools for networking (kube-proxy),
   security (iptables + network policies), observability (sidecar proxies), and
   runtime security (audit daemon), eBPF provides a single programmable layer
   that handles all of these from one place in the kernel.

Major adopters: Google (GKE Dataplane V2 uses Cilium), AWS (EKS supports Cilium),
Microsoft (Azure CNI powered by Cilium), Meta (Katran load balancer), Netflix
(bpftrace for performance analysis), Cloudflare (XDP for DDoS protection).

---

## Step-by-Step Practical

### Exploring eBPF on Your System

```bash
# Check kernel version (eBPF requires 4.15+, ideally 5.10+)
uname -r
# 5.15.0-91-generic

# Check if BPF is enabled
cat /boot/config-$(uname -r) | grep CONFIG_BPF
# CONFIG_BPF=y
# CONFIG_BPF_SYSCALL=y
# CONFIG_BPF_JIT=y
# CONFIG_BPF_JIT_ALWAYS_ON=y

# Install bpftool
sudo apt install linux-tools-common linux-tools-$(uname -r)

# List currently loaded eBPF programs
sudo bpftool prog list
# (Output varies based on what is running)

# List eBPF maps
sudo bpftool map list

# View program details
sudo bpftool prog show id 42
# 42: sched_cls  name handle_xgress  tag a1b2c3d4e5f6
#     loaded_at 2024-03-14T10:00:00+0000  uid 0
#     xlated 5368B  jited 3072B  memlock 8192B  map_ids 15,16,17

# Dump a map's contents
sudo bpftool map dump id 15
```

### Tracing with bpftrace

```bash
# Install bpftrace
sudo apt install bpftrace

# Count system calls by process
sudo bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'
# Press Ctrl+C to stop
# @[nginx]: 15234
# @[python]: 8921
# @[node]: 12456

# Trace TCP connections
sudo bpftrace -e '
kprobe:tcp_connect {
    printf("%-6d %-16s -> %s\n", pid, comm,
        ntop(((struct sock *)arg0)->__sk_common.skc_daddr));
}'
# 1234   curl             -> 93.184.216.34
# 5678   python           -> 10.96.0.1

# Histogram of read() sizes
sudo bpftrace -e '
tracepoint:syscalls:sys_exit_read /args->ret > 0/ {
    @bytes = hist(args->ret);
}'
```

### Observing eBPF in Kubernetes

```bash
# On a cluster with Cilium installed, observe the eBPF programs
kubectl exec -n kube-system -it ds/cilium -- bpftool prog list
# Shows all Cilium eBPF programs

# View Cilium's BPF maps
kubectl exec -n kube-system -it ds/cilium -- bpftool map list

# Monitor eBPF events in real time
kubectl exec -n kube-system -it ds/cilium -- cilium monitor
# <- endpoint 1234 flow 0x0 identity 12345->54321 ...
```

---

## Exercises

### Exercise 1: Kernel Capabilities Check
Check your kernel version and BPF configuration. List all CONFIG_BPF options
and explain what each one enables. Determine whether your kernel supports XDP,
BTF (BPF Type Format), and BPF ring buffer.

### Exercise 2: bpftool Exploration
Install bpftool and list all loaded eBPF programs and maps on your system. If
Cilium or another eBPF tool is running, examine its programs. For each program,
note the type, tag, JIT status, and attached maps.

### Exercise 3: bpftrace Scripting
Write three bpftrace one-liners: one that counts file opens by process, one that
traces DNS queries (UDP port 53), and one that shows a histogram of process
execution times. Run each and interpret the output.

### Exercise 4: iptables vs eBPF Analysis
On a Kubernetes cluster with kube-proxy, run `iptables -L -n | wc -l` to count
iptables rules. Then calculate how many rules would exist for 100 Services with
10 endpoints each. Explain why this scaling behavior is problematic and how eBPF
solves it.

### Exercise 5: eBPF Architecture Diagram
Draw a diagram of the Linux kernel networking data path showing where XDP, TC,
netfilter, and socket-level eBPF programs attach. For each hook point, list one
real-world use case and the tool that uses it.

---

## Knowledge Check

### Question 1
What is the eBPF verifier and why is it critical for safety?

**Answer:** The eBPF verifier is a static analysis engine in the Linux kernel
that validates every eBPF program before it is allowed to run. It checks that
the program terminates (no infinite loops), does not access out-of-bounds
memory, does not use uninitialized variables, stays within the stack size limit
(512 bytes), and does not exceed complexity bounds. If any check fails, the
program is rejected and never executes. This is critical because eBPF programs
run inside the kernel with kernel privileges. Without the verifier, a buggy
program could crash the kernel, corrupt memory, or create security
vulnerabilities.

### Question 2
Why does eBPF-based networking (Cilium) scale better than iptables-based
networking (kube-proxy)?

**Answer:** iptables evaluates rules linearly, meaning packet processing time
is O(n) where n is the number of rules. In a large cluster, thousands of
services create tens of thousands of iptables rules, adding measurable latency
to every packet. eBPF uses hash map lookups for service routing, which are O(1)
regardless of the number of services. Additionally, eBPF programs are
JIT-compiled to native machine code, while iptables interpretation has overhead.
The performance gap grows with cluster size.

### Question 3
What are BPF maps and why are they important?

**Answer:** BPF maps are kernel-resident key-value data structures that serve
two purposes: they allow eBPF programs to maintain state across invocations
(since eBPF programs are stateless by default), and they provide a communication
channel between eBPF programs running in the kernel and user-space applications
(like the Cilium agent). Without maps, eBPF programs could only make per-packet
decisions without context. With maps, they can track connections, maintain
identity mappings, accumulate metrics, and share policy tables, enabling
complex networking and security functionality.

### Question 4
What is XDP and why is it faster than other eBPF hook points?

**Answer:** XDP (eXpress Data Path) is the earliest possible eBPF hook point
in the Linux networking stack. It runs at the network driver level, before the
kernel allocates a socket buffer (skb) for the packet. Because it avoids skb
allocation and the rest of the networking stack, XDP can process packets at line
rate (millions of packets per second per core). This makes it ideal for DDoS
mitigation and high-performance load balancing where most packets are either
dropped or redirected without needing full stack processing.

### Question 5
Why is eBPF considered a unified platform for networking, observability, and
security?

**Answer:** Traditionally, these concerns required separate tools: kube-proxy
for networking, sidecar proxies for observability, iptables for security, and
audit daemons for runtime monitoring. Each tool adds overhead, complexity, and
its own failure modes. eBPF programs can be attached to the same kernel hook
points to handle all of these simultaneously. A single eBPF program on a TC
hook can route packets (networking), log flow data (observability), and enforce
policies (security) in one pass. This reduces overhead, simplifies operations,
and provides consistent data across all three concerns.
