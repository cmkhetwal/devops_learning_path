# Lesson 5: Networking Basics

## Why This Matters in DevOps

Networking is the circulatory system of modern infrastructure. Every deployment you perform,
every monitoring check, every API call, every database query -- all of it flows over a
network. When a user reports that "the site is slow," the problem could be anywhere in a
chain of network hops between the user's browser and your backend server. A DevOps engineer
who does not understand networking is blind to an entire category of problems that will
dominate their on-call rotations.

In DevOps, you will constantly work with networking concepts. You will configure load
balancers that distribute traffic across servers. You will set up DNS records so that
`api.yourcompany.com` resolves to the correct IP address. You will debug connectivity issues
where one service cannot reach another. You will open and close firewall ports as you deploy
new applications. You will trace network paths to diagnose latency issues. Every one of these
tasks requires a solid understanding of IP addressing, DNS, ports, protocols, and the tools
Linux provides for network diagnostics.

Cloud infrastructure has made networking even more central to the DevOps role. In AWS, Azure,
and GCP, you design Virtual Private Clouds (VPCs), configure subnets, set up security groups
(cloud firewalls), and manage routing tables. These are all networking concepts applied at
the cloud layer. Without a foundation in Linux networking, cloud networking concepts will
feel abstract and confusing. With that foundation, they become natural extensions of what you
already understand.

Security also depends heavily on networking knowledge. Firewalls control which traffic is
allowed in and out of your servers. Understanding the difference between TCP and UDP, knowing
which ports your applications listen on, and being able to verify that only the intended
ports are exposed -- these are critical security skills. Many breaches occur because a
database port was accidentally exposed to the internet, or because an internal service was
reachable from an untrusted network.

The tools you learn in this lesson -- `ip`, `ss`, `curl`, `ping`, `traceroute` -- will become
reflexive diagnostics that you reach for every time something goes wrong. They are the
equivalent of a doctor's stethoscope: basic instruments that reveal what is happening inside
the system.

---

## Core Concepts

### IP Addressing

Every device on a network has an IP address. IPv4 addresses look like `192.168.1.100` and
consist of four octets (numbers 0-255) separated by dots.

| Address Range        | Type              | Use Case                          |
|----------------------|-------------------|-----------------------------------|
| 10.0.0.0/8           | Private           | Internal networks, cloud VPCs     |
| 172.16.0.0/12        | Private           | Internal networks                 |
| 192.168.0.0/16       | Private           | Home networks, small offices      |
| 127.0.0.1            | Loopback          | Refers to the local machine       |
| 0.0.0.0              | All interfaces    | Listen on all network interfaces  |
| 169.254.0.0/16       | Link-local        | Auto-assigned when no DHCP        |

The `/24` notation (CIDR) defines the subnet size. `/24` means 256 addresses (e.g.,
`10.0.1.0` to `10.0.1.255`).

### Ports and Protocols

Ports are logical endpoints on a machine. An IP address identifies the machine; a port
identifies the service on that machine.

| Port  | Protocol | Service                              |
|-------|----------|--------------------------------------|
| 22    | TCP      | SSH (remote access)                  |
| 80    | TCP      | HTTP (web traffic)                   |
| 443   | TCP      | HTTPS (encrypted web traffic)        |
| 3306  | TCP      | MySQL                                |
| 5432  | TCP      | PostgreSQL                           |
| 6379  | TCP      | Redis                                |
| 8080  | TCP      | Common alternative HTTP port         |
| 53    | TCP/UDP  | DNS                                  |

### TCP vs UDP

| Feature          | TCP                              | UDP                             |
|------------------|----------------------------------|---------------------------------|
| Connection       | Connection-oriented (handshake)  | Connectionless                  |
| Reliability      | Guaranteed delivery, ordering    | No guarantee                    |
| Speed            | Slower (overhead for reliability)| Faster (no overhead)            |
| Use Cases        | Web, SSH, databases, email       | DNS queries, streaming, gaming  |

### DNS Resolution

DNS (Domain Name System) translates human-readable names to IP addresses. When you type
`google.com`, DNS resolves it to something like `142.250.80.46`.

Resolution order on Linux:
1. `/etc/hosts` -- Local static mappings (checked first)
2. `/etc/resolv.conf` -- Specifies which DNS servers to query
3. DNS servers -- Recursive lookup through the DNS hierarchy

### Key Configuration Files

| File                 | Purpose                                        |
|----------------------|------------------------------------------------|
| `/etc/hosts`         | Static hostname-to-IP mappings                 |
| `/etc/resolv.conf`   | DNS server configuration                       |
| `/etc/hostname`      | This machine's hostname                        |
| `/etc/network/`      | Network interface configuration (Debian)       |
| `/etc/sysconfig/network-scripts/` | Network config (Red Hat/CentOS)  |

---

## Step-by-Step Practical

### 1. View Your Network Configuration

```bash
ip addr show
```

Expected output:
```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536
    inet 127.0.0.1/8 scope host lo
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001
    inet 10.0.1.55/24 brd 10.0.1.255 scope global dynamic eth0
```

Key information:
- `lo` -- Loopback interface (127.0.0.1, always present)
- `eth0` -- Primary network interface with IP `10.0.1.55` on the `10.0.1.0/24` subnet

Show only IPv4 addresses concisely:

```bash
ip -4 addr show | grep inet
```

Expected output:
```
    inet 127.0.0.1/8 scope host lo
    inet 10.0.1.55/24 brd 10.0.1.255 scope global dynamic eth0
```

### 2. Check DNS Configuration

```bash
cat /etc/resolv.conf
```

Expected output:
```
nameserver 10.0.0.2
nameserver 8.8.8.8
search us-east-1.compute.internal
```

View local host mappings:

```bash
cat /etc/hosts
```

Expected output:
```
127.0.0.1 localhost
127.0.1.1 devops-server
::1       localhost ip6-localhost
```

### 3. Test Connectivity with ping

```bash
ping -c 4 google.com
```

Expected output:
```
PING google.com (142.250.80.46) 56(84) bytes of data.
64 bytes from lax17s61-in-f14.1e100.net: icmp_seq=1 ttl=116 time=1.23 ms
64 bytes from lax17s61-in-f14.1e100.net: icmp_seq=2 ttl=116 time=1.18 ms
64 bytes from lax17s61-in-f14.1e100.net: icmp_seq=3 ttl=116 time=1.21 ms
64 bytes from lax17s61-in-f14.1e100.net: icmp_seq=4 ttl=116 time=1.19 ms

--- google.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 1.180/1.202/1.230/0.019 ms
```

Key metrics: `time` (latency in milliseconds), `packet loss` (should be 0%).

### 4. Trace the Network Path

```bash
traceroute -n google.com
```

Expected output:
```
traceroute to google.com (142.250.80.46), 30 hops max
 1  10.0.1.1  0.456 ms  0.432 ms  0.410 ms
 2  100.65.0.1  1.234 ms  1.198 ms  1.210 ms
 3  52.93.28.45  1.567 ms  1.543 ms  1.556 ms
 ...
 8  142.250.80.46  1.230 ms  1.215 ms  1.220 ms
```

Each line is a network hop between your server and the destination. If a hop shows `* * *`,
that router is blocking traceroute packets.

### 5. DNS Lookup

```bash
nslookup google.com
```

Expected output:
```
Server:     10.0.0.2
Address:    10.0.0.2#53

Non-authoritative answer:
Name:   google.com
Address: 142.250.80.46
```

More detailed DNS query:

```bash
dig google.com +short
```

Expected output:
```
142.250.80.46
```

### 6. Check Open Ports and Listening Services

```bash
sudo ss -tlnp
```

Expected output:
```
State  Recv-Q Send-Q Local Address:Port  Peer Address:Port Process
LISTEN 0      128    0.0.0.0:22          0.0.0.0:*         users:(("sshd",pid=842,fd=3))
LISTEN 0      511    0.0.0.0:80          0.0.0.0:*         users:(("nginx",pid=1233,fd=6))
LISTEN 0      128    127.0.0.1:5432      0.0.0.0:*         users:(("postgres",pid=956,fd=5))
```

Flags explained:
- `-t` -- TCP connections only
- `-l` -- Listening sockets only
- `-n` -- Show port numbers (not service names)
- `-p` -- Show the process using each port

Notice that PostgreSQL listens on `127.0.0.1:5432` (localhost only) while SSH and Nginx
listen on `0.0.0.0` (all interfaces). This is a security best practice: databases should
not be directly accessible from the internet.

### 7. Make HTTP Requests with curl

```bash
curl -I https://httpbin.org/get
```

Expected output:
```
HTTP/2 200
content-type: application/json
content-length: 256
server: gunicorn/19.9.0
```

The `-I` flag fetches only headers. For the full response:

```bash
curl -s https://httpbin.org/ip
```

Expected output:
```json
{
  "origin": "54.123.45.67"
}
```

Test connectivity to a specific port:

```bash
curl -v telnet://localhost:22
```

Download a file:

```bash
wget -O /tmp/testfile https://httpbin.org/robots.txt
```

### 8. Basic Firewall with ufw

```bash
sudo ufw status
```

Expected output:
```
Status: inactive
```

Enable and configure the firewall:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp       # Allow SSH
sudo ufw allow 80/tcp       # Allow HTTP
sudo ufw allow 443/tcp      # Allow HTTPS
sudo ufw --force enable
sudo ufw status verbose
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## Exercises

1. **Network Discovery**: Run `ip addr show`, `ip route show`, and `cat /etc/resolv.conf`
   on your machine. Document your IP address, subnet mask, default gateway, and DNS servers.
   Explain what each one does.

2. **DNS Investigation**: Use `dig` or `nslookup` to find the IP addresses for five different
   websites. Then add a custom entry to `/etc/hosts` that maps `myapp.local` to `127.0.0.1`.
   Verify it works with `ping myapp.local`.

3. **Port Audit**: Run `sudo ss -tlnp` and document every listening port on your system.
   For each port, identify what service is using it and whether it should be accessible from
   the internet or only from localhost.

4. **Connectivity Debugging**: Use `ping`, `traceroute`, and `curl` to diagnose connectivity
   to a website. If ping fails but curl works, explain why (hint: some servers block ICMP).

5. **Firewall Configuration**: Set up `ufw` to allow only SSH (22), HTTP (80), and HTTPS
   (443). Verify that the rules are correct. Then add a rule to allow PostgreSQL (5432) only
   from a specific IP address: `sudo ufw allow from 10.0.1.100 to any port 5432`.

---

## Knowledge Check

**Q1: What is the difference between `0.0.0.0` and `127.0.0.1` when a service listens on
these addresses?**

A1: `0.0.0.0` means the service listens on ALL network interfaces -- it is accessible from
the local machine, the local network, and potentially the internet. `127.0.0.1` (localhost)
means the service listens only on the loopback interface -- it is accessible only from the
same machine. Databases should typically listen on `127.0.0.1` to prevent direct internet
access, while web servers listen on `0.0.0.0` to serve external traffic.

**Q2: A developer says "I cannot connect to the database on the new server." What steps
would you take to diagnose the problem?**

A2: Systematic diagnosis: (1) Verify the database service is running: `systemctl status
postgresql`. (2) Check what address and port it listens on: `ss -tlnp | grep 5432`. (3)
Check if the firewall allows the connection: `ufw status`. (4) Test connectivity from the
developer's machine: `telnet db-server 5432` or `curl -v telnet://db-server:5432`. (5) Check
DNS resolution: `nslookup db-server`. (6) Check network routing: `traceroute db-server`.
(7) Check the database's authentication configuration (`pg_hba.conf` for PostgreSQL).

**Q3: Why does Linux check `/etc/hosts` before querying DNS servers?**

A3: `/etc/hosts` provides local overrides that take precedence over DNS. This is useful for
development (mapping `myapp.local` to `127.0.0.1`), for servers in environments without DNS,
for blocking domains (mapping them to `127.0.0.1`), and for ensuring critical hostname
resolution works even if DNS servers are unavailable. The resolution order is defined in
`/etc/nsswitch.conf`.

**Q4: What is the security risk of a database listening on `0.0.0.0` instead of `127.0.0.1`?**

A4: When a database listens on `0.0.0.0`, it accepts connections from any network interface,
including the public internet if the server has a public IP and the firewall allows the
database port. This exposes the database to brute-force attacks, exploitation of database
vulnerabilities, and potential data exfiltration. Databases should listen on `127.0.0.1`
(or a private network interface) and be accessed through application servers, SSH tunnels,
or VPN connections.

**Q5: What is the difference between TCP and UDP, and when would you choose each?**

A5: TCP provides reliable, ordered delivery through a connection handshake -- data is
guaranteed to arrive and arrive in order. This reliability has overhead (slower). UDP sends
packets without guarantees -- faster but packets can be lost or arrive out of order. Use TCP
for anything requiring reliability: web traffic (HTTP/HTTPS), SSH, database connections,
file transfers. Use UDP for real-time applications where speed matters more than perfection:
DNS queries, video streaming, VoIP, monitoring metrics (StatsD).
