# Cilium Fundamentals: eBPF-Powered Kubernetes Networking

## Why This Matters in DevOps

Cilium is the CNI (Container Network Interface) plugin that replaces kube-proxy,
traditional CNIs (Calico with iptables, Flannel), and even sidecar-based service
meshes with a single eBPF-powered data plane. It has been adopted as the default
or recommended CNI by Google (GKE Dataplane V2), AWS (EKS), and Microsoft
(Azure CNI powered by Cilium).

As a DevOps engineer, understanding Cilium means understanding the networking
layer that connects every pod in your cluster. It determines how services
discover each other, how traffic is load-balanced, how network policies are
enforced, and how you observe network flows. Getting this right is the
foundation of a secure, performant, and observable Kubernetes platform.

---

## Core Concepts

### What Is Cilium?

Cilium is an open-source networking, observability, and security platform for
Kubernetes and other container orchestrators. It uses eBPF to implement:

- **Pod networking** (CNI) - Assigns IPs to pods and routes traffic
- **Service load balancing** - Replaces kube-proxy
- **Network policy** - L3/L4 and L7 policy enforcement
- **Observability** - Flow logs, service maps, and metrics via Hubble
- **Encryption** - Transparent WireGuard or IPsec encryption
- **Service mesh** - Sidecar-free L7 traffic management
- **Multi-cluster** - Cluster Mesh for cross-cluster connectivity

### Cilium Architecture

```
┌─────────────────────────────────────────────────┐
│                  Kubernetes Cluster              │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │           Cilium Operator                 │   │
│  │  (Manages CRDs, IP allocation, cleanup)  │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │  Node 1      │  │  Node 2      │             │
│  │              │  │              │             │
│  │ ┌──────────┐ │  │ ┌──────────┐ │             │
│  │ │ Cilium   │ │  │ │ Cilium   │ │             │
│  │ │ Agent    │ │  │ │ Agent    │ │             │
│  │ │(DaemonSet)│ │  │ │(DaemonSet)│ │             │
│  │ └────┬─────┘ │  │ └────┬─────┘ │             │
│  │      │       │  │      │       │             │
│  │ ┌────▼─────┐ │  │ ┌────▼─────┐ │             │
│  │ │ eBPF     │ │  │ │ eBPF     │ │             │
│  │ │ Programs │ │  │ │ Programs │ │             │
│  │ │ (kernel) │ │  │ │ (kernel) │ │             │
│  │ └──────────┘ │  │ └──────────┘ │             │
│  │              │  │              │             │
│  │ ┌───┐ ┌───┐ │  │ ┌───┐ ┌───┐ │             │
│  │ │Pod│ │Pod│ │  │ │Pod│ │Pod│ │             │
│  │ └───┘ └───┘ │  │ └───┘ └───┘ │             │
│  └──────────────┘  └──────────────┘             │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │            Hubble (Observability)         │   │
│  │  ┌────────────┐  ┌──────────────────┐    │   │
│  │  │ Hubble     │  │ Hubble UI        │    │   │
│  │  │ Relay      │  │ (Service Map)    │    │   │
│  │  └────────────┘  └──────────────────┘    │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**Cilium Agent** (DaemonSet) - Runs on every node. Compiles and loads eBPF
programs into the kernel, manages pod networking, enforces policies, and
provides a local Hubble observer.

**Cilium Operator** (Deployment) - Handles cluster-wide operations: IP
allocation (IPAM), garbage collection, CRD management, and interaction with
cloud provider APIs.

**Hubble** - Observability layer built on top of Cilium. Consists of:
- **Hubble Server** - Embedded in the Cilium Agent, collects flow data from eBPF
- **Hubble Relay** - Aggregates data from all Hubble servers across the cluster
- **Hubble UI** - Web interface showing service maps and flow data
- **Hubble CLI** - Command-line tool for querying flows

### Identity-Based Networking

Traditional network policies use IP addresses to identify workloads. This is
problematic in Kubernetes where pod IPs are ephemeral and reused.

Cilium uses **identity-based networking**: each pod is assigned a numeric
identity based on its Kubernetes labels. Network policy decisions are made
based on these identities, not IP addresses.

```
Traditional (IP-based):
  Pod A (10.0.1.5) --> allow 10.0.2.0/24 --> Pod B (10.0.2.3)
  Problem: What if Pod C gets IP 10.0.2.4? It is also allowed.
  Problem: What if Pod B restarts with IP 10.0.3.1? It is now denied.

Cilium (identity-based):
  Pod A (identity: app=frontend) --> allow identity: app=backend --> Pod B
  Pod B can restart with any IP - the identity follows it.
  Pod C with different labels gets a different identity - automatically denied.
```

Identity mapping is stored in an eBPF map:

```
IP Address    →  Cilium Identity
10.0.1.5      →  12345 (app=frontend, ns=web)
10.0.2.3      →  54321 (app=backend, ns=api)
```

### Cilium Endpoints

Every pod managed by Cilium is a **Cilium endpoint**. An endpoint has:

- An IP address
- A Cilium identity (based on labels)
- Policy enforcement state (enabled/disabled, ingress/egress)
- An eBPF program attached to its virtual network interface

```bash
# List all endpoints
cilium endpoint list
# ENDPOINT   POLICY (ingress)   POLICY (egress)   IDENTITY   LABELS
# 1234       Enabled            Enabled            12345      k8s:app=frontend
# 5678       Enabled            Enabled            54321      k8s:app=backend
```

### Replacing kube-proxy

Cilium can completely replace kube-proxy by implementing Kubernetes Service
load balancing in eBPF:

```
kube-proxy path:
  Pod → iptables DNAT → endpoint Pod
  (iptables rules updated by kube-proxy watching Service/Endpoint changes)

Cilium path:
  Pod → eBPF program (BPF map lookup) → endpoint Pod
  (BPF maps updated by Cilium agent watching Service/Endpoint changes)
```

Benefits of replacing kube-proxy:
- O(1) service lookup instead of O(n) iptables traversal
- Maglev consistent hashing for better load distribution
- DSR (Direct Server Return) for reduced latency
- Socket-level load balancing (connect-time instead of per-packet)
- No iptables rules to manage or debug

---

## Step-by-Step Practical

### Installing Cilium on Minikube

```bash
# Start minikube without a CNI (Cilium will provide it)
minikube start \
  --network-plugin=cni \
  --cni=false \
  --kubernetes-version=v1.29.0 \
  --memory=4096 \
  --cpus=2

# Install the Cilium CLI
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
CLI_ARCH=amd64
curl -L --fail --remote-name-all \
  https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz
sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CLI_ARCH}.tar.gz

# Install Cilium with kube-proxy replacement
cilium install \
  --version 1.15.0 \
  --set kubeProxyReplacement=true \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true

# Expected output:
# 🔮 Auto-detected Kubernetes kind: minikube
# ✨ Running "minikube" validation checks
# ✅ Detected minikube version "1.32.0"
# ℹ️  Using Cilium version 1.15.0
# 🔮 Auto-detected cluster name: minikube
# 🔮 Auto-detected kube-proxy has been installed
# ℹ️  Cilium will fully replace kube-proxy
# 🔑 Created CA in secret cilium-ca
# 🔑 Generating certificates for Hubble...
# ✅ Certificate stored in secret hubble-server-certs
# ✅ Certificate stored in secret hubble-relay-client-certs
# 🚀 Creating Service accounts...
# 🚀 Creating Cluster roles...
# 🚀 Creating ConfigMap for Cilium version 1.15.0...
# 🚀 Creating Agent DaemonSet...
# 🚀 Creating Operator Deployment...
# ⌛ Waiting for Cilium to be installed and ready...
# ✅ Cilium was successfully installed!

# Wait for Cilium to be fully ready
cilium status --wait
# Output:
#     /¯¯\
#  /¯¯\__/¯¯\    Cilium:             OK
#  \__/¯¯\__/    Operator:           OK
#  /¯¯\__/¯¯\    Envoy DaemonSet:    disabled
#  \__/¯¯\__/    Hubble Relay:       OK
#     \__/       ClusterMesh:        disabled
#
# Deployment             cilium-operator    Desired: 1, Ready: 1/1
# DaemonSet              cilium             Desired: 1, Ready: 1/1
# Deployment             hubble-relay       Desired: 1, Ready: 1/1
# Deployment             hubble-ui          Desired: 1, Ready: 1/1
# Containers:            cilium             Running: 1
#                        cilium-operator    Running: 1
#                        hubble-relay       Running: 1
#                        hubble-ui          Running: 1
```

### Running the Connectivity Test

```bash
# Run Cilium's built-in connectivity test suite
cilium connectivity test
# This creates test namespaces, deploys test workloads, and validates:
# - Pod-to-pod connectivity (same node and cross-node)
# - Pod-to-Service connectivity
# - Pod-to-external connectivity
# - Network policy enforcement
# - L7 policy enforcement
# - DNS resolution

# Expected output (abbreviated):
# ✅ [cilium-test] All 46 tests (306 actions) successful, 0 tests skipped, 0 scenarios skipped.
```

### Deploying Test Workloads

```bash
# Create a test namespace
kubectl create namespace demo

# Deploy a frontend and backend application
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: demo
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: nginx:1.25
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: demo
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: demo
  labels:
    app: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: nginx:1.25
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: demo
spec:
  selector:
    app: backend
  ports:
    - port: 80
      targetPort: 80
EOF

# Verify pods are running
kubectl get pods -n demo -o wide
# NAME                        READY   STATUS    RESTARTS   AGE   IP
# frontend-6d4f5b7c8-abc12   1/1     Running   0          30s   10.0.0.5
# frontend-6d4f5b7c8-def34   1/1     Running   0          30s   10.0.0.6
# backend-7e5f6c8d9-ghi56    1/1     Running   0          30s   10.0.0.7
# backend-7e5f6c8d9-jkl78    1/1     Running   0          30s   10.0.0.8
```

### Examining Cilium Endpoints and Identities

```bash
# View Cilium endpoints
kubectl exec -n kube-system -it ds/cilium -- cilium endpoint list
# ENDPOINT   POLICY (ingress)   POLICY (egress)   IDENTITY   LABELS (source:key[=value])
# 1234       Disabled           Disabled          45678      k8s:app=frontend
#                                                            k8s:io.kubernetes.pod.namespace=demo
# 5678       Disabled           Disabled          91234      k8s:app=backend
#                                                            k8s:io.kubernetes.pod.namespace=demo

# View identity to labels mapping
kubectl exec -n kube-system -it ds/cilium -- cilium identity list
# ID      LABELS
# 45678   k8s:app=frontend
#         k8s:io.kubernetes.pod.namespace=demo
# 91234   k8s:app=backend
#         k8s:io.kubernetes.pod.namespace=demo

# Test connectivity from frontend to backend
kubectl exec -n demo deploy/frontend -- curl -s http://backend/
# <!DOCTYPE html>
# <html>
# <head><title>Welcome to nginx!</title></head>
# ...

# View Cilium's service load balancing
kubectl exec -n kube-system -it ds/cilium -- cilium service list
# ID   Frontend              Service Type   Backend
# 1    10.96.0.1:443         ClusterIP      172.18.0.2:6443
# 2    10.96.0.10:53         ClusterIP      10.0.0.2:53
# 3    10.96.100.50:80       ClusterIP      10.0.0.7:80, 10.0.0.8:80
```

### Observing with Hubble

```bash
# Install the Hubble CLI
HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/main/stable.txt)
curl -L --fail --remote-name-all \
  https://github.com/cilium/hubble/releases/download/$HUBBLE_VERSION/hubble-linux-amd64.tar.gz
sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin
rm hubble-linux-amd64.tar.gz

# Port-forward to Hubble Relay
cilium hubble port-forward &

# Observe all flows
hubble observe
# TIMESTAMP             SOURCE                    DESTINATION               TYPE     VERDICT   SUMMARY
# Mar 14 10:30:00.000   demo/frontend-abc12       demo/backend              L4       FORWARDED TCP SYN
# Mar 14 10:30:00.001   demo/backend-ghi56        demo/frontend-abc12       L4       FORWARDED TCP SYN-ACK

# Filter flows for a specific pod
hubble observe --namespace demo --pod frontend

# Filter by verdict (dropped packets)
hubble observe --verdict DROPPED

# View flows as JSON
hubble observe -o json

# Open Hubble UI (service map visualization)
cilium hubble ui
# Opens browser to http://localhost:12000
```

---

## Exercises

### Exercise 1: Cilium Installation
Install Cilium on a local Kubernetes cluster (minikube, kind, or k3s) with
Hubble enabled and kube-proxy replacement. Verify the installation with
`cilium status` and run the full connectivity test with `cilium connectivity test`.

### Exercise 2: Endpoint Investigation
Deploy three microservices (frontend, backend, database) and examine their Cilium
endpoints and identities. Verify that each service has a unique identity. Use
`cilium endpoint list` and `cilium identity list` to map the relationships.

### Exercise 3: Service Load Balancing
Deploy a Service with 3 backend pods. Use `cilium service list` to see how
Cilium load-balances traffic. Send 100 requests from a client pod and verify
that requests are distributed across all backends.

### Exercise 4: Hubble Flow Observation
Generate traffic between services and use `hubble observe` to watch the flows
in real time. Filter by namespace, pod, protocol, and verdict. Export flows
as JSON and count the number of connections per source-destination pair.

### Exercise 5: kube-proxy Comparison
On a cluster with kube-proxy, count the iptables rules. Remove kube-proxy and
install Cilium as the kube-proxy replacement. Verify that services still work
and compare the iptables rule count before and after.

---

## Knowledge Check

### Question 1
What are the three main components of the Cilium architecture?

**Answer:** The three main components are: (1) **Cilium Agent**, a DaemonSet
running on every node that compiles and loads eBPF programs, manages pod
networking, enforces policies, and provides Hubble flow data. (2) **Cilium
Operator**, a Deployment that handles cluster-wide operations like IPAM (IP
Address Management), garbage collection, and CRD management. (3) **Hubble**,
the observability layer consisting of a server (embedded in the agent), a relay
(aggregates data from all nodes), a UI (service map visualization), and a CLI
(flow queries).

### Question 2
How does identity-based networking differ from IP-based networking, and why is
it better for Kubernetes?

**Answer:** IP-based networking identifies workloads by their IP addresses and
enforces policies using CIDR ranges. In Kubernetes, pod IPs are ephemeral --
they change on restart and are reused by different pods. This makes IP-based
policies unreliable and requires constant rule updates. Identity-based networking
assigns a numeric identity to each pod based on its Kubernetes labels. Policies
reference identities, not IPs. When a pod restarts with a new IP, its identity
stays the same (same labels), so policies continue to work without changes.
This is fundamentally more reliable in dynamic environments.

### Question 3
How does Cilium replace kube-proxy, and what are the benefits?

**Answer:** Cilium replaces kube-proxy by implementing Kubernetes Service load
balancing in eBPF instead of iptables. The Cilium agent watches the Kubernetes
API for Service and Endpoint changes and updates BPF maps instead of iptables
rules. Benefits include: O(1) service lookup via hash maps instead of O(n)
iptables traversal, Maglev consistent hashing for better load distribution,
Direct Server Return (DSR) for reduced latency, socket-level load balancing
(resolving at connect time rather than per-packet NAT), and elimination of
the iptables rule sprawl that makes debugging difficult.

### Question 4
What is a Cilium endpoint?

**Answer:** A Cilium endpoint represents a networked entity managed by Cilium,
typically a Kubernetes pod. Each endpoint has: an IP address, a Cilium identity
(derived from Kubernetes labels), policy enforcement state (ingress/egress
enabled or disabled), and an eBPF program attached to its virtual network
interface (veth pair). The Cilium agent manages endpoints on its node, loading
appropriate eBPF programs for each one based on the applicable network policies.

### Question 5
What does the `cilium connectivity test` validate?

**Answer:** The connectivity test deploys test workloads in dedicated namespaces
and validates end-to-end networking functionality including: pod-to-pod
connectivity on the same node and across nodes, pod-to-Service connectivity
(ClusterIP and NodePort), pod-to-external connectivity (egress to the internet),
DNS resolution, Kubernetes network policy enforcement, Cilium L7 policy
enforcement, and host networking. It runs dozens of test scenarios and reports
pass/fail for each, making it the definitive way to verify a Cilium
installation is working correctly.
