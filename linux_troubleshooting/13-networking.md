# 13 - Networking Deep Dive
## Bonding, VLAN, Routing, tcpdump, Troubleshooting

---

## SECTION 1: Network Configuration

### 1.1 NetworkManager (Modern - All Distros)
```bash
# Check status
nmcli general status        # Show overall NetworkManager status
nmcli device status         # Show all network interfaces and their state
nmcli connection show       # List all connection profiles

# Configure static IP
nmcli connection modify eth0 \
    ipv4.addresses 192.168.1.10/24 \
    ipv4.gateway 192.168.1.1 \
    ipv4.dns "8.8.8.8 8.8.4.4" \
    ipv4.method manual
# modify = change connection profile properties (saved to disk)
nmcli connection up eth0
# up = activate (or reactivate) the named connection profile

# Configure DHCP
nmcli connection modify eth0 ipv4.method auto
nmcli connection up eth0

# Add secondary IP
nmcli connection modify eth0 +ipv4.addresses 192.168.1.11/24

# Add DNS
nmcli connection modify eth0 +ipv4.dns 1.1.1.1

# Create new connection
nmcli connection add type ethernet con-name office ifname eth0 \
    ipv4.addresses 10.0.1.10/24 ipv4.gateway 10.0.1.1 ipv4.method manual

# Disable IPv6
nmcli connection modify eth0 ipv6.method disabled

# Set MTU
nmcli connection modify eth0 802-3-ethernet.mtu 9000   # Jumbo frames
```

### 1.2 Network Configuration Files

```bash
# --- CentOS/RHEL 7-8 (ifcfg) ---
# /etc/sysconfig/network-scripts/ifcfg-eth0
TYPE=Ethernet
DEVICE=eth0
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.1.10
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4

# --- CentOS/RHEL 9+ (NetworkManager key files) ---
# /etc/NetworkManager/system-connections/eth0.nmconnection
[connection]
id=eth0
type=ethernet
interface-name=eth0
autoconnect=true

[ipv4]
method=manual
addresses=192.168.1.10/24
gateway=192.168.1.1
dns=8.8.8.8;8.8.4.4;

# --- Ubuntu 18+ (Netplan) ---
# /etc/netplan/01-config.yaml
network:
  version: 2
  renderer: networkd    # or NetworkManager
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.1.10/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4

# Apply netplan
netplan apply              # Apply network config permanently
netplan try                # Apply with 120s rollback timer (reverts if not confirmed)
```

---

## SECTION 2: Network Bonding / Teaming

### NIC Bonding (Link Aggregation)
```bash
# Using NetworkManager
nmcli connection add type bond con-name bond0 ifname bond0 \
    bond.options "mode=802.3ad,miimon=100,lacp_rate=fast"
# miimon=100 = check link state every 100ms
# lacp_rate=fast = send LACP packets every 1s (default "slow" = 30s)

nmcli connection add type ethernet con-name bond0-slave1 ifname eth0 master bond0
nmcli connection add type ethernet con-name bond0-slave2 ifname eth1 master bond0

nmcli connection modify bond0 \
    ipv4.addresses 192.168.1.10/24 \
    ipv4.gateway 192.168.1.1 \
    ipv4.method manual

nmcli connection up bond0

# Bond modes:
# mode=0 (balance-rr)    = Round-robin
# mode=1 (active-backup) = Failover (most common for servers)
# mode=2 (balance-xor)   = XOR hash
# mode=4 (802.3ad)       = LACP (requires switch support)
# mode=5 (balance-tlb)   = Adaptive transmit
# mode=6 (balance-alb)   = Adaptive load balancing

# Check bond status
cat /proc/net/bonding/bond0
```

---

## SECTION 3: VLANs

```bash
# Create VLAN interface
nmcli connection add type vlan con-name vlan100 ifname eth0.100 \
    dev eth0 id 100 \
    ipv4.addresses 10.100.0.10/24 \
    ipv4.method manual

nmcli connection up vlan100

# Manual (ip command)
ip link add link eth0 name eth0.100 type vlan id 100
# link eth0 = parent interface | name = virtual interface name | id 100 = VLAN tag
ip addr add 10.100.0.10/24 dev eth0.100
ip link set eth0.100 up

# Verify
cat /proc/net/vlan/config
ip -d link show eth0.100    # -d = show detailed/driver info (includes VLAN id)
```

---

## SECTION 4: Routing

```bash
# View routing table
ip route show
ip route show table all      # table all = show all routing tables (main, local, custom)
route -n                     # Legacy; -n = show numeric IPs (skip DNS resolution)

# Add static route
ip route add 10.10.0.0/16 via 192.168.1.1 dev eth0
ip route add default via 192.168.1.1

# Delete route
ip route del 10.10.0.0/16

# Persistent routes
# CentOS (ifcfg): /etc/sysconfig/network-scripts/route-eth0
10.10.0.0/16 via 192.168.1.1 dev eth0

# Ubuntu (Netplan):
# Add under ethernets.eth0:
routes:
  - to: 10.10.0.0/16
    via: 192.168.1.1

# nmcli:
nmcli connection modify eth0 +ipv4.routes "10.10.0.0/16 192.168.1.1"

# Enable IP forwarding (for routers/gateways)
sysctl -w net.ipv4.ip_forward=1    # -w = write/set a kernel parameter at runtime
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf

# Policy-based routing
ip rule add from 10.0.1.0/24 table 100
ip route add default via 10.0.1.1 table 100

# Trace route to destination
traceroute -n 8.8.8.8       # -n = numeric output (skip DNS lookups, faster)
mtr -rw 8.8.8.8             # Better traceroute with stats
# -r = report mode (non-interactive, runs then prints summary)
# -w = wide report (show full hostnames, no truncation)
ip route get 10.0.0.1       # get = show which route the kernel would use for a destination
```

---

## SECTION 5: tcpdump & Packet Analysis

```bash
# Basic capture
tcpdump -i eth0                          # -i = capture on specified interface
tcpdump -i any                           # any = capture on all interfaces at once
tcpdump -i eth0 -nn                      # -nn = don't resolve hostnames or port names (faster output)

# Filter by host
tcpdump -i eth0 -nn host 192.168.1.100
tcpdump -i eth0 -nn src 192.168.1.100    # src = match source IP only
tcpdump -i eth0 -nn dst 192.168.1.100    # dst = match destination IP only

# Filter by port
tcpdump -i eth0 -nn port 80             # port = match src or dst port
tcpdump -i eth0 -nn port 443
tcpdump -i eth0 -nn portrange 8000-9000  # portrange = match a range of ports

# Filter by protocol
tcpdump -i eth0 -nn tcp                  # tcp/udp/icmp = filter by protocol type
tcpdump -i eth0 -nn udp
tcpdump -i eth0 -nn icmp

# Complex filters
tcpdump -i eth0 -nn 'host 10.0.0.1 and port 80'
tcpdump -i eth0 -nn 'src net 10.0.0.0/8 and dst port 443'
tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-syn != 0'          # SYN packets
tcpdump -i eth0 -nn 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0' # SYN or FIN
tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-rst != 0'          # RST packets

# Save to file (analyze in Wireshark)
tcpdump -i eth0 -nn -w /tmp/capture.pcap -c 1000
# -w = write raw packets to file (pcap format, open in Wireshark)
# -c 1000 = stop capture after 1000 packets
tcpdump -i eth0 -nn -w /tmp/capture.pcap -G 60 -W 5
# -G 60 = rotate capture file every 60 seconds
# -W 5 = keep at most 5 rotated files (oldest deleted)

# Read capture file
tcpdump -nn -r /tmp/capture.pcap                       # -r = read packets from file
tcpdump -nn -r /tmp/capture.pcap 'port 80'            # Filter on read

# Show packet content
tcpdump -i eth0 -nn -X port 80      # -X = show packet data in hex + ASCII
tcpdump -i eth0 -nn -A port 80      # -A = show packet data in ASCII only (good for HTTP)

# Useful captures:
# DNS queries
tcpdump -i eth0 -nn port 53

# HTTP headers
tcpdump -i eth0 -nn -A -s0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'
# -s0 = capture full packet (no truncation; default snaplength may cut large packets)

# Find who's connecting to specific port
tcpdump -i eth0 -nn 'dst port 22 and tcp[tcpflags] & tcp-syn != 0'
```

---

## SECTION 6: Network Troubleshooting Toolkit

```bash
# ss (Socket Statistics - replacement for netstat)
ss -tlnp                    # TCP listening
# -t = TCP sockets only
# -l = show listening sockets only
# -n = numeric (don't resolve service names)
# -p = show process using the socket
ss -ulnp                    # UDP listening (-u = UDP sockets only)
ss -tnp                     # TCP established (no -l = connected/established sockets)
ss -s                       # -s = summary statistics (socket counts by type/state)
ss -tn state established    # state filter = show only sockets in specified TCP state
ss -tn state time-wait      # TIME_WAIT connections
ss -tnp dst :3306           # dst :3306 = filter by destination port (connections TO MySQL)
ss -tnp sport = :80         # sport = :80 = filter by source port (connections FROM port 80)

# nmap (Network Scanner)
nmap -sP 192.168.1.0/24         # -sP = ping scan (host discovery only, no port scan)
nmap -sT 192.168.1.10           # -sT = TCP connect scan (full 3-way handshake)
nmap -sV 192.168.1.10           # -sV = probe open ports to detect service versions
nmap -p 1-65535 192.168.1.10    # -p = specify port range (here: all 65535 ports)
nmap -A 192.168.1.10            # -A = aggressive (OS detection + version + scripts + traceroute)

# curl (HTTP testing)
curl -v https://example.com                    # -v = verbose (show request/response headers + TLS handshake)
curl -I https://example.com                    # -I = fetch HTTP headers only (HEAD request)
curl -o /dev/null -s -w "HTTP: %{http_code}\nDNS: %{time_namelookup}\nConnect: %{time_connect}\nTTFB: %{time_starttransfer}\nTotal: %{time_total}\n" https://example.com
# -o /dev/null = discard response body
# -s = silent (no progress bar)
# -w = print custom output using format variables after transfer

# Test specific port connectivity
nc -zv hostname 80          # -z = scan only (don't send data) | -v = verbose
nc -zvu hostname 53         # -u = use UDP instead of TCP
timeout 3 bash -c "echo >/dev/tcp/hostname/80" && echo "Open" || echo "Closed"

# ARP table
ip neigh show                # neigh show = display ARP/neighbor cache entries
ip neigh flush all           # neigh flush all = clear entire ARP cache

# MTU testing
ping -M do -s 1472 192.168.1.1   # Test MTU (1472 + 28 header = 1500)
# -M do = set DF (Don't Fragment) bit — packet is dropped if too large
# -s 1472 = set payload size in bytes
```
