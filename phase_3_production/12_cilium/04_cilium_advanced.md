# Advanced Cilium: Observability, Service Mesh, and Multi-Cluster

## Why This Matters in DevOps

Cilium is not just a CNI plugin. It is a comprehensive platform for networking,
observability, and security. Once Cilium is managing your pod networking, it has
visibility into every packet flowing through the cluster. This visibility powers
Hubble (flow observability and service maps), enables sidecar-free service mesh
capabilities, connects multiple clusters with Cluster Mesh, and provides runtime
security through Tetragon.

Understanding these advanced features transforms Cilium from "the thing that gives
pods IP addresses" into the operational backbone of your platform. Hubble replaces
the need for tcpdump and ad-hoc debugging. Service mesh without sidecars reduces
resource overhead and operational complexity. Cluster Mesh enables multi-cluster
architectures. Tetragon provides kernel-level runtime security.

---

## Core Concepts

### Hubble Observability

Hubble is Cilium's observability layer. It collects flow data from the eBPF data
plane and presents it through multiple interfaces:

```
eBPF Data Plane (kernel)
    │
    │ Flow events (packet metadata)
    ▼
Hubble Server (per-node, in cilium-agent)
    │
    │ gRPC stream
    ▼
Hubble Relay (cluster-wide aggregation)
    │
    ├──▶ Hubble CLI (real-time flow queries)
    ├──▶ Hubble UI (service map visualization)
    ├──▶ Prometheus metrics (hubble_*)
    └──▶ OpenTelemetry export
```

#### Flow Data

Every network flow is recorded with rich metadata:

```bash
# View flows in real time
hubble observe --follow
# TIMESTAMP             SOURCE                        DESTINATION                   TYPE     VERDICT     SUMMARY
# 10:30:00.001          bookstore/frontend-abc12      bookstore/api-def34          l7       FORWARDED   HTTP/1.1 GET /api/books
# 10:30:00.015          bookstore/api-def34           bookstore/database-ghi56     l4       FORWARDED   TCP SYN
# 10:30:00.100          bookstore/api-def34           world                        l4       DROPPED     TCP SYN -> 93.184.216.34:443

# Filter by label
hubble observe --from-label "app=frontend" --to-label "app=api"

# Filter by HTTP status code
hubble observe --http-status 500

# Filter by protocol
hubble observe --protocol tcp --port 5432

# Filter by verdict
hubble observe --verdict DROPPED

# View as JSON for programmatic analysis
hubble observe -o json | jq '.flow.source.labels'

# Get flow statistics
hubble observe --last 1000 -o json | jq -r '.flow.verdict' | sort | uniq -c
#   850 FORWARDED
#   120 DROPPED
#    30 ERROR
```

#### Prometheus Metrics

Hubble exports metrics to Prometheus:

```yaml
# Cilium Helm values to enable Hubble metrics
hubble:
  enabled: true
  metrics:
    enabled:
      - dns
      - drop
      - tcp
      - flow
      - port-distribution
      - icmp
      - httpV2:exemplars=true;labelsContext=source_ip,source_namespace,source_workload,destination_ip,destination_namespace,destination_workload,traffic_direction
    serviceMonitor:
      enabled: true
```

Key metrics:

```promql
# Dropped packets by reason
hubble_drop_total{reason="POLICY_DENIED"}

# HTTP request rate by source and destination
rate(hubble_http_requests_total{
  source_workload="frontend",
  destination_workload="api"
}[5m])

# HTTP error rate
rate(hubble_http_requests_total{status=~"5.."}[5m])
/ rate(hubble_http_requests_total[5m])

# DNS query latency
histogram_quantile(0.99, rate(hubble_dns_response_types_total[5m]))

# TCP connection duration
histogram_quantile(0.95, rate(hubble_tcp_flags_total[5m]))

# Flow rate per namespace
rate(hubble_flows_processed_total{destination_namespace="production"}[5m])
```

### Cilium Service Mesh (Sidecar-Free)

Traditional service meshes (Istio, Linkerd) inject sidecar proxy containers
into every pod. This adds:
- 50-100MB memory per sidecar
- Additional CPU overhead per request
- Increased latency (extra network hops through the sidecar)
- Operational complexity (sidecar injection, upgrades, debugging)

Cilium implements service mesh features directly in eBPF, eliminating sidecars:

```
Traditional Service Mesh:
  Pod A → [Sidecar] → Network → [Sidecar] → Pod B
  (4 context switches, 2 TCP connections)

Cilium Service Mesh:
  Pod A → [eBPF] → Network → [eBPF] → Pod B
  (kernel-level, zero additional TCP connections)
```

Cilium service mesh features:

```yaml
# Traffic shifting (canary deployments)
apiVersion: cilium.io/v2
kind: CiliumEnvoyConfig
metadata:
  name: canary-routing
  namespace: production
spec:
  services:
    - name: api
      namespace: production
  resources:
    - "@type": type.googleapis.com/envoy.config.route.v3.RouteConfiguration
      name: api-route
      virtual_hosts:
        - name: api
          domains: ["*"]
          routes:
            - match:
                prefix: "/"
              route:
                weighted_clusters:
                  clusters:
                    - name: "production/api:8080"
                      weight: 90
                    - name: "production/api-canary:8080"
                      weight: 10
```

```yaml
# Retry policy
apiVersion: cilium.io/v2
kind: CiliumEnvoyConfig
metadata:
  name: retry-policy
  namespace: production
spec:
  services:
    - name: api
      namespace: production
  resources:
    - "@type": type.googleapis.com/envoy.config.route.v3.RouteConfiguration
      name: retry-route
      virtual_hosts:
        - name: api
          domains: ["*"]
          routes:
            - match:
                prefix: "/"
              route:
                cluster: "production/api:8080"
                retry_policy:
                  retry_on: "5xx,reset,connect-failure"
                  num_retries: 3
                  per_try_timeout: "3s"
```

### Cilium Cluster Mesh (Multi-Cluster)

Cluster Mesh connects multiple Kubernetes clusters, enabling:
- Cross-cluster service discovery
- Global load balancing
- Shared network policies
- High availability across clusters

```
┌─────────────────────┐    ┌─────────────────────┐
│  Cluster 1 (US-East)│    │  Cluster 2 (US-West)│
│                     │    │                     │
│  ┌───────────┐      │    │      ┌───────────┐ │
│  │ Cilium    │◄─────┼────┼─────►│ Cilium    │ │
│  │ ClusterMesh│      │    │      │ ClusterMesh│ │
│  └───────────┘      │    │      └───────────┘ │
│                     │    │                     │
│  ┌───┐ ┌───┐       │    │       ┌───┐ ┌───┐ │
│  │API│ │API│       │    │       │API│ │API│ │
│  └───┘ └───┘       │    │       └───┘ └───┘ │
│                     │    │                     │
│  Service: api ──────┼────┼──── Service: api   │
│  (endpoints: local  │    │  (endpoints: local  │
│   + remote cluster) │    │   + remote cluster) │
└─────────────────────┘    └─────────────────────┘
```

```bash
# Enable Cluster Mesh
cilium clustermesh enable --service-type LoadBalancer

# Connect two clusters
cilium clustermesh connect --destination-context cluster2

# Verify connectivity
cilium clustermesh status
# Cluster Mesh:      OK
# Global services:   15

# Annotate a service for global load balancing
kubectl annotate service api \
  service.cilium.io/global="true" \
  service.cilium.io/shared="true"
```

### Bandwidth Management

Cilium provides eBPF-based bandwidth management using Earliest Departure Time
(EDT) instead of traditional token bucket queuing:

```yaml
# Pod annotation for bandwidth limits
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubernetes.io/egress-bandwidth: "10M"   # 10 Mbps egress limit
    kubernetes.io/ingress-bandwidth: "20M"   # 20 Mbps ingress limit
spec:
  containers:
    - name: app
      image: myapp:latest
```

Enable in Cilium configuration:

```yaml
# Helm values
bandwidthManager:
  enabled: true
  bbr: true  # BBR congestion control
```

### Transparent Encryption

Cilium supports transparent, pod-to-pod encryption using WireGuard or IPsec:

```bash
# Enable WireGuard encryption (recommended over IPsec)
cilium install \
  --set encryption.enabled=true \
  --set encryption.type=wireguard

# Verify encryption is active
cilium status | grep Encryption
# Encryption:   Wireguard   [NodeEncryption: Disabled, cilium_wg0 (Pubkey: xxx, Port 51871, Peers: 2)]

# Check WireGuard peers
kubectl exec -n kube-system ds/cilium -- cilium encrypt status
# Encryption:       Enabled
# Type:             WireGuard
# Listening port:   51871
# Peers:
#   Node 1 (10.0.0.1): endpoint-count=15, pubkey=xxx
#   Node 2 (10.0.0.2): endpoint-count=12, pubkey=xxx
```

All pod-to-pod traffic across nodes is now encrypted transparently, without
any application changes.

### BGP Integration

Cilium can peer with external BGP routers to advertise Kubernetes service and
pod CIDRs:

```yaml
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPPeeringPolicy
metadata:
  name: rack-bgp
spec:
  virtualRouters:
    - localASN: 65001
      exportPodCIDR: true
      serviceSelector:
        matchExpressions:
          - key: bgp-announce
            operator: In
            values: ["true"]
      neighbors:
        - peerAddress: "10.0.0.1/32"
          peerASN: 65000
          connectRetryTimeSeconds: 120
          holdTimeSeconds: 90
          keepAliveTimeSeconds: 30
          gracefulRestart:
            enabled: true
            restartTimeSeconds: 120
```

### Tetragon (Runtime Security)

Tetragon is Cilium's runtime security enforcement and observability tool. It
uses eBPF to monitor and enforce policies on process execution, file access,
and network activity:

```yaml
# Detect and alert on suspicious process execution
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: detect-shell-exec
spec:
  kprobes:
    - call: "security_bprm_check"
      syscall: false
      args:
        - index: 0
          type: "linux_binprm"
      selectors:
        - matchBinaries:
            - operator: "In"
              values:
                - "/bin/sh"
                - "/bin/bash"
                - "/bin/dash"
          matchNamespaces:
            - namespace: Mnt
              operator: NotIn
              values:
                - "host_mnt"
      matchActions:
        - action: Sigkill    # Kill the process immediately
```

```yaml
# Monitor file access to sensitive paths
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: monitor-sensitive-files
spec:
  kprobes:
    - call: "security_file_open"
      syscall: false
      return: true
      args:
        - index: 0
          type: "file"
      selectors:
        - matchArgs:
            - index: 0
              operator: "Prefix"
              values:
                - "/etc/shadow"
                - "/etc/passwd"
                - "/etc/kubernetes/pki"
                - "/var/run/secrets/kubernetes.io"
```

```bash
# Install Tetragon
helm install tetragon cilium/tetragon -n kube-system

# View security events
kubectl logs -n kube-system ds/tetragon -c export-stdout -f | \
  tetra getevents -o compact

# Example output:
# process kube-system/coredns /bin/sh -c "echo test"
#   ALERT: Shell execution in container
#   ACTION: Sigkill
```

---

## Step-by-Step Practical

### Setting Up Hubble Observability and Service Map

```bash
# 1. Ensure Hubble is enabled
cilium status | grep Hubble
# Hubble Relay:   OK
# Hubble UI:      OK

# 2. Install the Hubble CLI (if not already installed)
HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/main/stable.txt)
curl -L --fail --remote-name-all \
  https://github.com/cilium/hubble/releases/download/$HUBBLE_VERSION/hubble-linux-amd64.tar.gz
sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin
rm hubble-linux-amd64.tar.gz

# 3. Port-forward Hubble Relay
cilium hubble port-forward &

# 4. Verify Hubble connectivity
hubble status
# Healthcheck (via localhost:4245): Ok
# Current/Max Flows: 8190/8190 (100.00%)
# Flows/s: 45.67

# 5. Deploy a multi-service application to generate traffic
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: ecommerce
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.25
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: ecommerce
spec:
  selector:
    app: web
  ports:
    - port: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ecommerce
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: nginx:1.25
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: ecommerce
spec:
  selector:
    app: api
  ports:
    - port: 8080
      targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders
  namespace: ecommerce
spec:
  replicas: 1
  selector:
    matchLabels:
      app: orders
  template:
    metadata:
      labels:
        app: orders
    spec:
      containers:
        - name: orders
          image: nginx:1.25
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: orders
  namespace: ecommerce
spec:
  selector:
    app: orders
  ports:
    - port: 8080
      targetPort: 8080
EOF

# 6. Generate traffic between services
kubectl run traffic-gen --namespace ecommerce --image=busybox:1.36 --restart=Never -- \
  sh -c 'while true; do
    wget -q -O- http://web/ > /dev/null 2>&1
    wget -q -O- http://api:8080/ > /dev/null 2>&1
    wget -q -O- http://orders:8080/ > /dev/null 2>&1
    sleep 1
  done'

# 7. Observe flows in real time
hubble observe --namespace ecommerce --follow
# TIMESTAMP             SOURCE                          DESTINATION                      TYPE   VERDICT    SUMMARY
# 10:30:00.001          ecommerce/traffic-gen           ecommerce/web-abc12             l7     FORWARDED  HTTP/1.1 GET /
# 10:30:00.050          ecommerce/traffic-gen           ecommerce/api-def34             l7     FORWARDED  HTTP/1.1 GET /
# 10:30:00.100          ecommerce/traffic-gen           ecommerce/orders-ghi56          l7     FORWARDED  HTTP/1.1 GET /

# 8. Open the Hubble UI for service map visualization
cilium hubble ui
# Opens browser to http://localhost:12000
# Shows a visual graph of service-to-service communication

# 9. Query flow statistics
hubble observe --namespace ecommerce --last 100 -o json | \
  jq -r '[.flow.source.labels[], .flow.destination.labels[]] | join(" -> ")' | \
  sort | uniq -c | sort -rn
#   35 k8s:app=traffic-gen -> k8s:app=web
#   33 k8s:app=traffic-gen -> k8s:app=api
#   32 k8s:app=traffic-gen -> k8s:app=orders

# 10. Export flows to Grafana via Prometheus
# The hubble_http_requests_total metric is available for dashboarding
kubectl port-forward -n monitoring svc/prometheus 9090 &
curl -s 'localhost:9090/api/v1/query?query=hubble_http_requests_total' | jq .
```

### Creating a Grafana Dashboard for Hubble

```json
{
  "dashboard": {
    "title": "Hubble Network Observability",
    "panels": [
      {
        "title": "HTTP Request Rate by Service",
        "targets": [
          {
            "expr": "sum(rate(hubble_http_requests_total[5m])) by (destination_workload)"
          }
        ]
      },
      {
        "title": "HTTP Error Rate",
        "targets": [
          {
            "expr": "sum(rate(hubble_http_requests_total{status=~\"5..\"}[5m])) by (destination_workload) / sum(rate(hubble_http_requests_total[5m])) by (destination_workload)"
          }
        ]
      },
      {
        "title": "Dropped Packets by Reason",
        "targets": [
          {
            "expr": "sum(rate(hubble_drop_total[5m])) by (reason)"
          }
        ]
      },
      {
        "title": "DNS Query Rate",
        "targets": [
          {
            "expr": "sum(rate(hubble_dns_queries_total[5m])) by (source_workload, query)"
          }
        ]
      }
    ]
  }
}
```

---

## Exercises

### Exercise 1: Hubble Deep Dive
Deploy a three-tier application and generate traffic between all tiers. Use
Hubble CLI to: list all flows, filter by namespace, filter by HTTP method,
filter by verdict, and export flows as JSON. Pipe the JSON output to `jq`
to calculate: total flows, error rate, and top source-destination pairs.

### Exercise 2: Service Map Analysis
Use the Hubble UI to visualize a service map. Identify all communication paths.
Then add a network policy that blocks one path. Observe how the service map
updates in real time. Screenshot and document the before and after states.

### Exercise 3: Transparent Encryption
Enable WireGuard encryption on a Cilium cluster. Verify encryption is active
with `cilium encrypt status`. Use `tcpdump` on the node to capture traffic
between two pods on different nodes. Verify the traffic is encrypted (you should
see WireGuard packets, not plaintext HTTP).

### Exercise 4: Tetragon Security Policy
Install Tetragon and create a TracingPolicy that detects shell execution in
containers. Deploy a test pod and try to exec into it with `kubectl exec`. Verify
that Tetragon detects and logs the shell execution event. Configure the policy
to kill the shell process automatically.

### Exercise 5: Multi-Cluster Setup
Create two Kubernetes clusters (minikube profiles or kind clusters). Install
Cilium with Cluster Mesh on both. Connect them and deploy a service in both
clusters. Annotate it for global load balancing. From a client pod in cluster 1,
verify that requests are load-balanced across pods in both clusters.

---

## Knowledge Check

### Question 1
What are the components of the Hubble observability stack, and what role does
each play?

**Answer:** Hubble has four components: (1) **Hubble Server**, embedded in the
Cilium Agent on each node, collects flow data from the eBPF data plane and
stores it in a per-node ring buffer. (2) **Hubble Relay**, a cluster-wide
aggregation service that connects to all Hubble servers via gRPC and provides
a unified view of flows across the cluster. (3) **Hubble CLI**, a command-line
tool that queries Hubble Relay for real-time flow observation, filtering, and
export. (4) **Hubble UI**, a web interface that visualizes service-to-service
communication as a service dependency map, showing flow verdicts, protocols,
and policy enforcement status.

### Question 2
How does Cilium's sidecar-free service mesh differ from traditional service
meshes like Istio?

**Answer:** Traditional service meshes inject a sidecar proxy (Envoy) into every
pod. Each request traverses two additional Envoy instances (source and
destination sidecars), adding latency, memory (50-100MB per sidecar), and CPU
overhead. Cilium implements service mesh features directly in eBPF at the kernel
level, eliminating sidecars entirely. For L4 features (load balancing, retries,
circuit breaking), eBPF handles everything in-kernel. For L7 features (HTTP
routing, traffic splitting), Cilium uses a per-node Envoy instance (not
per-pod) shared by all pods on that node. This reduces resource overhead from
O(n) sidecars to O(nodes) Envoy instances.

### Question 3
What is Cluster Mesh and what problems does it solve?

**Answer:** Cluster Mesh connects multiple Kubernetes clusters so pods can
discover and communicate with services in other clusters. It solves several
problems: (1) High availability across regions -- if one cluster fails, traffic
automatically shifts to the other. (2) Data locality -- requests can be routed
to the nearest cluster. (3) Shared services -- a central database or API can
be accessed from multiple clusters without VPN configuration. (4) Migration --
workloads can be gradually moved between clusters. Cluster Mesh works by
synchronizing service and endpoint information between clusters through the
Cilium ClusterMesh API server.

### Question 4
How does Cilium's WireGuard encryption work, and why is it preferred over IPsec?

**Answer:** Cilium's WireGuard encryption creates a WireGuard tunnel interface
(cilium_wg0) on each node. Pod-to-pod traffic crossing node boundaries is
automatically encrypted through the WireGuard tunnel. No application changes
are needed; encryption is transparent. WireGuard is preferred over IPsec
because: it is significantly simpler (fewer configuration options, smaller
codebase), it has better performance (modern cryptography, less overhead), it
uses a fixed set of modern cryptographic primitives (no negotiation), and the
key exchange is automatic (managed by the Cilium agent). IPsec requires
managing security associations and is more complex to troubleshoot.

### Question 5
What is Tetragon and how does it complement Cilium's network policies?

**Answer:** Tetragon is Cilium's runtime security enforcement and observability
tool. While Cilium network policies control network communication between pods,
Tetragon monitors and enforces policies on process execution, file access, and
system calls within pods. For example, Tetragon can detect and kill shell
processes spawned inside containers, alert when sensitive files are accessed,
or block processes from making certain system calls. It uses eBPF kprobes and
tracepoints to hook into kernel functions, providing deep visibility into
container runtime behavior. Together, Cilium (network) and Tetragon (runtime)
provide defense in depth: even if an attacker bypasses network policies, Tetragon
can detect and stop malicious activity inside the container.
