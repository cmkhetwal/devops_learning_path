# Cilium Network Policies: Zero-Trust Kubernetes Networking

## Why This Matters in DevOps

By default, Kubernetes allows all pods to communicate with all other pods. This
is a flat network with no segmentation -- any compromised pod can reach every
other pod, every database, and every internal API. This is the networking
equivalent of leaving every door in a building unlocked.

Network policies are how you lock those doors. They define which pods can
communicate with which other pods, on which ports, and at which protocol layers.
Cilium takes this further than standard Kubernetes by offering Layer 7 policies
(HTTP method and path filtering), DNS-based policies, and identity-aware
policies that follow pods across IP changes.

Zero-trust networking means "deny everything, allow explicitly." This lesson
teaches you how to implement that philosophy using Cilium Network Policies.

---

## Core Concepts

### Kubernetes Network Policies vs Cilium Network Policies

Kubernetes has a built-in `NetworkPolicy` resource, but it has significant
limitations:

| Feature | K8s NetworkPolicy | Cilium NetworkPolicy |
|---|---|---|
| L3/L4 filtering | Yes | Yes |
| L7 filtering (HTTP, gRPC) | No | Yes |
| DNS-based filtering | No | Yes |
| Identity-aware | No (IP-based) | Yes (label-based) |
| Cluster-wide policies | No (namespace-scoped) | Yes (CiliumClusterwideNetworkPolicy) |
| Node/host policies | No | Yes |
| Default deny | Must be explicit | Must be explicit |
| CIDR policies | Yes | Yes |
| Named ports | Yes | Yes |
| Policy visualization | No | Yes (Hubble) |

Cilium supports both Kubernetes `NetworkPolicy` resources (for compatibility)
and its own `CiliumNetworkPolicy` CRD (for advanced features). In practice,
you should use `CiliumNetworkPolicy` for its superior capabilities.

### L3/L4 Policies

Layer 3 (IP/identity) and Layer 4 (port/protocol) policies control which
endpoints can communicate on which ports:

```yaml
# Allow frontend to reach backend on port 8080
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: demo
spec:
  endpointSelector:
    matchLabels:
      app: backend           # Apply to pods with app=backend
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend    # Allow from pods with app=frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
```

This policy states: "Pods labeled `app=backend` may receive TCP traffic on
port 8080 only from pods labeled `app=frontend`." All other ingress traffic
to backend pods is denied (because having any ingress rule enables default deny
for ingress on the selected endpoints).

### L7 Policies (HTTP-Aware)

Cilium can inspect HTTP traffic and enforce policies based on method, path,
and headers:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-l7-policy
  namespace: demo
spec:
  endpointSelector:
    matchLabels:
      app: api-server
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: GET
                path: "/api/v1/products"
              - method: GET
                path: "/api/v1/products/[0-9]+"
              - method: POST
                path: "/api/v1/orders"
                headers:
                  - 'Content-Type: application/json'
```

This policy allows the frontend to:
- GET `/api/v1/products` (list products)
- GET `/api/v1/products/{id}` (get a specific product)
- POST `/api/v1/orders` with JSON content type (create an order)

Any other HTTP request (DELETE, PUT, different paths) is denied. This is
dramatically more granular than L3/L4 policies and prevents lateral movement
even if the frontend is compromised.

### DNS-Based Policies

For egress to external services, CIDR-based policies are fragile because cloud
service IPs change. DNS-based policies match on domain names:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-external-apis
  namespace: demo
spec:
  endpointSelector:
    matchLabels:
      app: backend
  egress:
    - toEndpoints:
        - matchLabels:
            io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: ANY
          rules:
            dns:
              - matchPattern: "*.amazonaws.com"
              - matchName: "api.stripe.com"
              - matchName: "api.sendgrid.com"
    - toFQDNs:
        - matchPattern: "*.amazonaws.com"
        - matchName: "api.stripe.com"
        - matchName: "api.sendgrid.com"
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP
```

This policy allows the backend to:
1. Make DNS queries for specific domains
2. Connect to those domains on port 443 (HTTPS)

Cilium intercepts DNS responses, learns the IP addresses for each domain, and
dynamically creates L3/L4 rules. When the IPs change, the rules update
automatically.

### Identity-Aware Policies

Cilium policies use Kubernetes labels as identities, which is more robust than
IP-based policies:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: database-access
  namespace: demo
spec:
  endpointSelector:
    matchLabels:
      app: database
      tier: data
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: backend
            tier: api
        - matchLabels:
            app: migration-job
            tier: maintenance
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP
    - fromEndpoints:
        - matchLabels:
            app: monitoring
            io.kubernetes.pod.namespace: monitoring
      toPorts:
        - ports:
            - port: "9187"   # PostgreSQL exporter metrics
              protocol: TCP
```

Notice how identities cross namespace boundaries: the monitoring pod from
the `monitoring` namespace can reach the database metrics port. This is
specified using the `io.kubernetes.pod.namespace` label.

### Host Policies

Cilium can enforce policies on the host itself (not just pods):

```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: host-ssh-policy
spec:
  nodeSelector:
    matchLabels:
      kubernetes.io/os: linux
  ingress:
    - fromCIDR:
        - "10.0.0.0/8"        # Internal network only
      toPorts:
        - ports:
            - port: "22"
              protocol: TCP
    - fromEntities:
        - health             # Cilium health checks
        - remote-node        # Node-to-node communication
```

### Cluster-Wide Policies

`CiliumClusterwideNetworkPolicy` applies across all namespaces without requiring
per-namespace deployment:

```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: deny-external-by-default
spec:
  endpointSelector: {}    # All pods in all namespaces
  egress:
    - toEntities:
        - cluster          # Allow all in-cluster traffic
    - toEndpoints:
        - matchLabels:
            io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: ANY
  egressDeny:
    - toEntities:
        - world            # Deny all external traffic by default
```

Individual namespaces can then add specific egress allowances for their needs.

### Zero-Trust Networking Methodology

The zero-trust approach follows these steps:

```
1. Audit   → Map all communication flows (Hubble)
2. Deny    → Apply default-deny policies
3. Allow   → Add specific allow rules for each flow
4. Monitor → Watch for dropped traffic (legitimate flows you missed)
5. Refine  → Add missing allow rules
6. L7      → Tighten L4 rules to L7 where possible
7. Repeat  → Continuously audit and refine
```

---

## Step-by-Step Practical

### Implementing Zero-Trust Between Microservices

```bash
# Deploy a microservices application
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: bookstore
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: bookstore
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        tier: web
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
  namespace: bookstore
spec:
  selector:
    app: frontend
  ports:
    - port: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: bookstore
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
        tier: backend
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
  namespace: bookstore
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
  name: database
  namespace: bookstore
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
        tier: data
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_PASSWORD
              value: "demo-password"
---
apiVersion: v1
kind: Service
metadata:
  name: database
  namespace: bookstore
spec:
  selector:
    app: database
  ports:
    - port: 5432
EOF

# Step 1: Verify all pods are running
kubectl get pods -n bookstore
# NAME                        READY   STATUS    RESTARTS   AGE
# frontend-xxx                1/1     Running   0          30s
# api-xxx                     1/1     Running   0          30s
# api-yyy                     1/1     Running   0          30s
# database-xxx                1/1     Running   0          30s
```

### Step 2: Audit Current Communication

```bash
# Before applying policies, observe current flows
hubble observe --namespace bookstore
# All traffic is allowed - any pod can reach any other pod

# Test connectivity (all should work before policies)
kubectl exec -n bookstore deploy/frontend -- curl -s http://api:8080/
kubectl exec -n bookstore deploy/frontend -- curl -s http://database:5432/ || echo "Connection attempted"
kubectl exec -n bookstore deploy/api -- curl -s http://database:5432/ || echo "Connection attempted"
```

### Step 3: Apply Default-Deny Policy

```yaml
# default-deny.yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny-all
  namespace: bookstore
spec:
  endpointSelector: {}   # Selects all pods in the namespace
  ingress:
    - fromEndpoints:
        - matchLabels: {}  # Deny all ingress (empty selector matches nothing)
          # This is a trick: an empty ingress rule enables default deny
  egress:
    - toEndpoints:
        - matchLabels:
            io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: ANY
```

```bash
# Apply default deny
kubectl apply -f default-deny.yaml

# Test connectivity (all should fail now except DNS)
kubectl exec -n bookstore deploy/frontend -- curl -s --connect-timeout 3 http://api:8080/
# curl: (28) Connection timed out

kubectl exec -n bookstore deploy/api -- curl -s --connect-timeout 3 http://database:5432/
# curl: (28) Connection timed out

# Observe dropped flows in Hubble
hubble observe --namespace bookstore --verdict DROPPED
# TIMESTAMP   SOURCE                DESTINATION           TYPE   VERDICT   SUMMARY
# ...         bookstore/frontend    bookstore/api         L4     DROPPED   TCP SYN
```

### Step 4: Add Allow Rules

```yaml
# allow-frontend-to-api.yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: bookstore
spec:
  endpointSelector:
    matchLabels:
      app: api
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: GET
                path: "/api/.*"
              - method: POST
                path: "/api/orders"
```

```yaml
# allow-api-to-database.yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-api-to-database
  namespace: bookstore
spec:
  endpointSelector:
    matchLabels:
      app: database
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: api
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP
```

```yaml
# allow-api-egress.yaml - API needs to reach database and external APIs
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-api-egress
  namespace: bookstore
spec:
  endpointSelector:
    matchLabels:
      app: api
  egress:
    - toEndpoints:
        - matchLabels:
            app: database
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP
    - toEndpoints:
        - matchLabels:
            io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: ANY
          rules:
            dns:
              - matchName: "api.stripe.com"
    - toFQDNs:
        - matchName: "api.stripe.com"
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP
```

```bash
# Apply all allow rules
kubectl apply -f allow-frontend-to-api.yaml
kubectl apply -f allow-api-to-database.yaml
kubectl apply -f allow-api-egress.yaml

# Test: frontend -> api (should work for allowed paths)
kubectl exec -n bookstore deploy/frontend -- \
  curl -s http://api:8080/api/books
# 200 OK (or appropriate response)

# Test: frontend -> database (should still be blocked)
kubectl exec -n bookstore deploy/frontend -- \
  curl -s --connect-timeout 3 http://database:5432/
# curl: (28) Connection timed out

# Test: api -> database (should work)
kubectl exec -n bookstore deploy/api -- \
  curl -s --connect-timeout 3 http://database:5432/ || echo "TCP connection works (protocol mismatch expected)"
```

### Step 5: Monitor and Verify

```bash
# View all policies
kubectl get cnp -n bookstore
# NAME                     AGE
# default-deny-all         5m
# allow-frontend-to-api    2m
# allow-api-to-database    2m
# allow-api-egress         2m

# Check policy enforcement on endpoints
kubectl exec -n kube-system ds/cilium -- cilium endpoint list
# ENDPOINT   POLICY (ingress)   POLICY (egress)   IDENTITY   LABELS
# ...        Enabled            Enabled           ...        k8s:app=frontend
# ...        Enabled            Enabled           ...        k8s:app=api
# ...        Enabled            Enabled           ...        k8s:app=database

# Monitor for drops (indicates blocked traffic)
hubble observe --namespace bookstore --verdict DROPPED --follow

# View policy verdict for specific traffic
hubble observe --namespace bookstore \
  --from-label "app=frontend" \
  --to-label "app=api"
# Should show FORWARDED verdicts

hubble observe --namespace bookstore \
  --from-label "app=frontend" \
  --to-label "app=database"
# Should show DROPPED verdicts
```

### Using the Cilium Policy Editor

```bash
# Visualize policies using cilium CLI
kubectl exec -n kube-system ds/cilium -- cilium policy get

# Get policy selectors for a specific endpoint
kubectl exec -n kube-system ds/cilium -- cilium endpoint get <endpoint-id> \
  -o jsonpath='{.status.policy}'

# Check which identities are allowed
kubectl exec -n kube-system ds/cilium -- cilium identity list
```

---

## Exercises

### Exercise 1: Default Deny Implementation
Deploy three pods (client, server, database) in a namespace. Verify they can
all communicate. Apply a default-deny policy and verify all communication is
blocked. Then selectively allow client-to-server and server-to-database.
Document the Hubble flow output at each stage.

### Exercise 2: L7 Policy Enforcement
Create an API server pod (use nginx with custom config to serve different paths).
Write a Cilium L7 policy that allows GET requests to `/api/public` but blocks
POST requests and access to `/api/admin`. Verify with curl from a client pod.

### Exercise 3: DNS-Based Egress Policy
Create a pod that needs to access `api.github.com` and `pypi.org` but no other
external services. Write a Cilium DNS policy that allows only these domains.
Verify that the pod can reach the allowed domains and is blocked from reaching
others like `example.com`.

### Exercise 4: Cross-Namespace Policy
Deploy a monitoring stack in the `monitoring` namespace and an application in the
`app` namespace. Write Cilium policies that allow the monitoring namespace to
scrape metrics from the application namespace on port 9090, but block all other
cross-namespace traffic.

### Exercise 5: Policy Migration
Take an existing set of Kubernetes `NetworkPolicy` resources and convert them to
`CiliumNetworkPolicy` equivalents. Add L7 rules where appropriate. Compare the
expressiveness and identify what was not possible with standard NetworkPolicies.

---

## Knowledge Check

### Question 1
What is the difference between a Kubernetes NetworkPolicy and a CiliumNetworkPolicy?

**Answer:** Kubernetes NetworkPolicy operates at L3/L4 only (IP addresses and
ports). CiliumNetworkPolicy adds L7 filtering (HTTP method/path, gRPC, Kafka
topic), DNS-based egress policies (match on domain names instead of IPs),
identity-aware policies (using Kubernetes labels resolved via Cilium identities
instead of raw IPs), cluster-wide policies (CiliumClusterwideNetworkPolicy for
cross-namespace rules), and host-level policies. CiliumNetworkPolicy also
provides better visibility through Hubble integration, showing policy verdicts
for every flow.

### Question 2
How does a default-deny policy work in Cilium?

**Answer:** When a CiliumNetworkPolicy selects an endpoint and defines an
ingress or egress section, Cilium automatically enables default deny for that
direction on those endpoints. Any traffic not explicitly allowed by a rule is
dropped. To create a default-deny for all pods in a namespace, you create a
policy with `endpointSelector: {}` (selects all pods) and empty or restrictive
ingress/egress rules. This is the foundation of zero-trust networking: start
by denying everything, then add specific allow rules.

### Question 3
Why are DNS-based egress policies better than CIDR-based policies for external
services?

**Answer:** Cloud services (AWS, Stripe, SendGrid) use dynamic IP addresses
that change without notice. CIDR-based policies require knowing and maintaining
these IP ranges, which is impractical. DNS-based policies specify domain names
(e.g., `api.stripe.com`), and Cilium intercepts DNS responses to learn the
current IPs. When IPs change, the rules update automatically. Additionally,
DNS policies are human-readable (domain names are meaningful) while CIDR blocks
are opaque. This makes auditing and maintaining policies much easier.

### Question 4
What does a Cilium L7 HTTP policy enforce, and how does it work technically?

**Answer:** An L7 HTTP policy enforces rules based on HTTP method (GET, POST,
DELETE), path (regex matching), and headers. Technically, Cilium redirects
matching traffic through an Envoy proxy running as part of the Cilium agent.
Envoy inspects the HTTP request, applies the policy rules, and either forwards
or drops the request. This means Cilium can allow `GET /api/products` while
blocking `DELETE /api/products` from the same source, providing application-level
access control without modifying the application code.

### Question 5
What is the zero-trust networking implementation methodology with Cilium?

**Answer:** The methodology follows these steps: (1) Audit existing communication
patterns using Hubble to observe all flows and build a communication map.
(2) Apply default-deny policies to block all traffic. (3) Add specific allow
rules for each legitimate communication path identified in the audit.
(4) Monitor for DROPPED flows in Hubble to find legitimate traffic that was
not covered by the allow rules. (5) Refine by adding missing rules and
tightening overly broad rules. (6) Layer on L7 policies where possible to
restrict not just which pods communicate but what operations they can perform.
(7) Continuously audit as applications evolve.
