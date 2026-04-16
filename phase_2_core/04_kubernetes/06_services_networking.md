# Lesson 06: Services and Networking

## Why This Matters in DevOps

Pods are ephemeral. They get new IP addresses every time they restart. If your
frontend cannot reliably reach your backend because the backend Pod IP changed,
your application is broken. Services solve this by providing a stable network
endpoint that routes traffic to healthy Pods regardless of their IPs.

As a DevOps engineer, you will configure Services daily. Understanding Service
types, DNS resolution, and kube-proxy is essential for debugging connectivity
issues -- one of the most common production problems.

The CKA exam heavily tests Service creation and troubleshooting.

---

## Core Concepts

### The Problem Services Solve

```
Without Services:
  Frontend Pod --> Backend Pod (IP: 10.244.1.5)
                   Backend Pod dies, restarts
                   New IP: 10.244.2.8
  Frontend Pod --> 10.244.1.5 --> CONNECTION REFUSED

With Services:
  Frontend Pod --> backend-svc (ClusterIP: 10.96.0.100)
                   |
                   +--> Backend Pod (10.244.1.5) [healthy]
                   +--> Backend Pod (10.244.2.8) [healthy]
                   +--> Backend Pod (10.244.3.2) [healthy]

  Pod dies and restarts with new IP?
  Service automatically updates its endpoint list.
  Frontend never notices.
```

### Service Types

```
+------- ClusterIP (default) --------+
| Internal only. No external access. |
| Good for: backend services,        |
|           databases, caches        |
|                                    |
| frontend-pod --> my-svc:80         |
|                  (10.96.0.100)     |
|                  |                 |
|                  +--> pod-1        |
|                  +--> pod-2        |
+------------------------------------+

+------- NodePort ---------+--------+
| Exposes on every node's  |        |
| IP at a static port      |        |
| (30000-32767)            |        |
|                          |        |
| External:                |        |
| curl node-ip:30080 ---+  |        |
|                       |  |        |
| +--- ClusterIP ------+| |        |
| |                    ||| |        |
| | +--> pod-1        ||  |        |
| | +--> pod-2        ||  |        |
| +--------------------+|  |        |
+---------------------------+--------+

+------- LoadBalancer ------+--------+
| Cloud provider creates an |        |
| external load balancer    |        |
|                           |        |
| Internet --> Cloud LB     |        |
|              (public IP)  |        |
|              |            |        |
| +--- NodePort ----------+|        |
| | +--- ClusterIP ------+||        |
| | |                    |||        |
| | | +--> pod-1        |||        |
| | | +--> pod-2        |||        |
| | +--------------------+||        |
| +------------------------+|        |
+----------------------------+--------+

+------- ExternalName ------+
| DNS alias to an external  |
| service. No proxying.     |
|                           |
| my-db.default.svc -->     |
|   CNAME: db.example.com   |
+---------------------------+
```

### Service Discovery via DNS

Kubernetes runs CoreDNS, which provides DNS resolution for all Services:

```
Service: my-service in namespace: default
DNS names that resolve to it:

  my-service                                    (from same namespace)
  my-service.default                            (from any namespace)
  my-service.default.svc                        (fully qualified within cluster)
  my-service.default.svc.cluster.local          (FQDN)
```

### kube-proxy Modes

kube-proxy runs on every node and implements Service networking:

| Mode | How It Works | Performance |
|---|---|---|
| **iptables** (default) | Creates iptables rules for each Service/endpoint | Good for < 5000 Services |
| **IPVS** | Uses Linux IPVS (IP Virtual Server) kernel module | Better for large clusters |

### Endpoints

When you create a Service with a selector, Kubernetes automatically creates an
Endpoints object that lists the IP addresses of all matching Pods:

```
Service (selector: app=web) --> Endpoints (10.244.1.5, 10.244.2.8, 10.244.3.2)
                                             |             |             |
                                           Pod-1         Pod-2         Pod-3
```

---

## Step-by-Step Practical

### 1. Create a Deployment to expose

```yaml
# Save as /tmp/web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f /tmp/web-deployment.yaml
kubectl get pods -l app=web-app -o wide
# Note the individual Pod IPs
```

### 2. ClusterIP Service

```yaml
# Save as /tmp/clusterip-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP            # Default, can be omitted
  selector:
    app: web-app              # Matches pods with this label
  ports:
  - port: 80                  # Port the Service listens on
    targetPort: 80             # Port on the Pod to forward to
    protocol: TCP
```

```bash
kubectl apply -f /tmp/clusterip-svc.yaml

# Check the service
kubectl get svc web-service
# NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
# web-service   ClusterIP   10.96.23.145   <none>        80/TCP    5s

# See the endpoints (Pod IPs that the Service routes to)
kubectl get endpoints web-service
# NAME          ENDPOINTS                                      AGE
# web-service   10.244.0.5:80,10.244.0.6:80,10.244.0.7:80     5s

# Test from within the cluster
kubectl run test-pod --image=busybox:1.36 --rm -it --restart=Never -- \
  wget -qO- http://web-service
# Should return nginx welcome page HTML

# DNS resolution test
kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup web-service
# Should resolve to the ClusterIP
```

### 3. Create Service imperatively

```bash
# Expose an existing deployment
kubectl expose deployment web-app --name=web-svc-imperative \
  --port=80 --target-port=80 --type=ClusterIP

kubectl get svc web-svc-imperative
kubectl delete svc web-svc-imperative
```

### 4. NodePort Service

```yaml
# Save as /tmp/nodeport-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  selector:
    app: web-app
  ports:
  - port: 80                  # ClusterIP port
    targetPort: 80             # Pod port
    nodePort: 30080            # External port (30000-32767)
    protocol: TCP
```

```bash
kubectl apply -f /tmp/nodeport-svc.yaml

kubectl get svc web-nodeport
# NAME           TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
# web-nodeport   NodePort   10.96.45.200   <none>        80:30080/TCP   5s

# Access via node IP
# For minikube:
minikube service web-nodeport --url
# Or:
curl $(minikube ip):30080

# For any cluster:
kubectl get nodes -o wide  # get node IP
curl <node-ip>:30080
```

### 5. LoadBalancer Service

```yaml
# Save as /tmp/loadbalancer-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  type: LoadBalancer
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
```

```bash
kubectl apply -f /tmp/loadbalancer-svc.yaml

# In cloud environments, EXTERNAL-IP will be provisioned
# In minikube, it stays <pending> unless you run:
minikube tunnel  # in a separate terminal

kubectl get svc web-lb
# NAME     TYPE           CLUSTER-IP    EXTERNAL-IP    PORT(S)        AGE
# web-lb   LoadBalancer   10.96.78.34   192.168.49.2   80:31234/TCP   5s
```

### 6. ExternalName Service

```yaml
# Save as /tmp/externalname-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: database.example.com
```

```bash
kubectl apply -f /tmp/externalname-svc.yaml

# Applications can connect to "external-db" and it resolves
# to database.example.com via CNAME
kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup external-db
```

### 7. Multi-port Service

```yaml
# Save as /tmp/multiport-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port-svc
spec:
  selector:
    app: web-app
  ports:
  - name: http         # Names required when multiple ports
    port: 80
    targetPort: 80
  - name: https
    port: 443
    targetPort: 443
```

### 8. Service without a selector (manual endpoints)

```yaml
# Save as /tmp/manual-endpoints.yaml
apiVersion: v1
kind: Service
metadata:
  name: external-service
spec:
  ports:
  - port: 3306
    targetPort: 3306
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-service     # Must match Service name
subsets:
  - addresses:
    - ip: 192.168.1.100       # External database IP
    - ip: 192.168.1.101
    ports:
    - port: 3306
```

```bash
kubectl apply -f /tmp/manual-endpoints.yaml

# Now pods can connect to "external-service:3306"
# and traffic is routed to 192.168.1.100 or 192.168.1.101
```

### 9. Debugging service connectivity

```bash
# Check service exists
kubectl get svc web-service

# Check endpoints are populated
kubectl get endpoints web-service
# If endpoints are empty, the selector does not match any running pods

# Check pod labels match the service selector
kubectl get pods --show-labels
kubectl get svc web-service -o yaml | grep -A3 selector

# Test DNS resolution
kubectl run dns-debug --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup web-service.default.svc.cluster.local

# Test connectivity
kubectl run curl-debug --image=curlimages/curl --rm -it --restart=Never -- \
  curl -v http://web-service:80

# Check kube-proxy is running
kubectl get pods -n kube-system -l k8s-app=kube-proxy
```

### 10. Clean up

```bash
kubectl delete deployment web-app
kubectl delete svc web-service web-nodeport web-lb external-db multi-port-svc external-service
```

---

## Exercises

1. **Full Service Setup**: Create a Deployment with 3 nginx replicas. Create a
   ClusterIP Service for it. From a temporary pod, verify you can curl the
   Service name and get a response. Scale the Deployment to 1 and verify the
   Service still works.

2. **NodePort Access**: Create a NodePort Service for the same Deployment.
   Access it from outside the cluster using the node IP and NodePort.

3. **Service Debugging**: Create a Service with a deliberate selector mismatch
   (Service selects `app=wrong`, Pods have `app=web`). Check the endpoints and
   observe they are empty. Fix the selector and verify endpoints populate.

4. **DNS Exploration**: Deploy two applications in different namespaces (`app-a`
   in `ns-a`, `app-b` in `ns-b`). Create Services for each. From a pod in `ns-a`,
   try to reach `app-b` using short name, then fully qualified name. Which works?

5. **Multi-Port Service**: Deploy an application that listens on two ports
   (e.g., nginx on 80 and a sidecar on 9090). Create a single Service that
   exposes both ports. Verify both are reachable.

---

## Knowledge Check

**Q1**: What are the four Service types and when would you use each?
<details>
<summary>Answer</summary>
- **ClusterIP** (default): Internal-only access. Use for backend services that
  only need to be reached by other pods in the cluster.
- **NodePort**: Exposes the Service on a static port on every node. Use for
  development/testing when you need external access without a cloud load balancer.
- **LoadBalancer**: Provisions a cloud load balancer with a public IP. Use in
  cloud environments for production external access.
- **ExternalName**: Maps a Service to a DNS CNAME. Use to reference external
  services (outside the cluster) by a Kubernetes-internal name.
</details>

**Q2**: How does Kubernetes DNS work for Services?
<details>
<summary>Answer</summary>
CoreDNS runs as pods in kube-system and provides DNS for the cluster. Every Service
gets a DNS entry: `<service-name>.<namespace>.svc.cluster.local`. From within the
same namespace, you can use just the service name. From other namespaces, use
`<service-name>.<namespace>`. Pods resolve these names automatically because
kubelet configures each Pod's /etc/resolv.conf to point to the CoreDNS ClusterIP.
</details>

**Q3**: A Service has no endpoints. What is the most likely cause?
<details>
<summary>Answer</summary>
The most likely cause is that the Service's selector does not match any running
Pod's labels. Check with `kubectl get svc <name> -o yaml` to see the selector,
then `kubectl get pods --show-labels` to see Pod labels. Other causes: no Pods
exist, or all matching Pods are not in Ready state (failing readiness probes).
</details>

**Q4**: What is the difference between `port` and `targetPort` in a Service spec?
<details>
<summary>Answer</summary>
`port` is the port that the Service listens on (what clients connect to).
`targetPort` is the port on the Pod that traffic is forwarded to. They can be
different. For example, a Service might listen on port 80 but forward to a Pod
running on port 8080. If targetPort is omitted, it defaults to the same value
as port.
</details>

**Q5**: What is a headless Service and when is it used?
<details>
<summary>Answer</summary>
A headless Service has `clusterIP: None`. Instead of providing a single virtual IP,
DNS queries return the IP addresses of all individual Pods. This is required for
StatefulSets where each Pod needs to be individually addressable (e.g., database
replicas). DNS returns A records for each Pod:
`pod-0.svc-name.namespace.svc.cluster.local`.
</details>
