# Lesson 12: Monitoring and Debugging

## Why This Matters in DevOps

Applications fail. Containers crash, images are not found, nodes run out of memory,
and network connections break. Your job as a DevOps engineer is to find the root
cause fast. Kubernetes provides a rich set of debugging tools, but only if you know
where to look and what the error messages mean.

The CKA exam includes troubleshooting scenarios where you must diagnose and fix
failing workloads under time pressure. A systematic debugging methodology is worth
more than memorized commands.

---

## Core Concepts

### The Debugging Methodology

```
Pod is not working
       |
       v
+--- Step 1: What is the Pod status? ---+
| kubectl get pod <name>                |
|                                       |
| Pending?      --> Scheduling problem  |
| ImagePull*?   --> Image problem       |
| CrashLoop*?   --> Application crash   |
| Running but   --> Readiness probe     |
|   not Ready?      failing             |
| Completed?    --> Normal for Jobs     |
+---------------------------------------+
       |
       v
+--- Step 2: Describe the Pod ----------+
| kubectl describe pod <name>          |
| Look at:                             |
|   Events (bottom of output)          |
|   Conditions                         |
|   Container states                   |
+---------------------------------------+
       |
       v
+--- Step 3: Check logs ----------------+
| kubectl logs <name>                  |
| kubectl logs <name> --previous       |
| kubectl logs <name> -c <container>   |
+---------------------------------------+
       |
       v
+--- Step 4: Get inside ----------------+
| kubectl exec -it <name> -- /bin/sh   |
| Check: network, files, env vars,     |
|        DNS resolution, processes     |
+---------------------------------------+
```

### Common Error States

```
+--- CrashLoopBackOff ---+
| Container starts, crashes, restarts, crashes again.
| Kubernetes applies exponential backoff between restarts.
| Causes: application error, missing config, wrong command,
|         OOM, exit code non-zero.
|
| Debug: kubectl logs <pod> --previous
|        kubectl describe pod <pod> (check exit code)
+-------------------------+

+--- ImagePullBackOff / ErrImagePull ---+
| Cannot pull the container image.
| Causes: wrong image name, wrong tag, private registry
|         without imagePullSecret, registry down.
|
| Debug: kubectl describe pod <pod> (check Events)
|        Verify image name and tag exist
|        Check imagePullSecrets configuration
+---------------------------------------+

+--- Pending ---+
| Pod cannot be scheduled to any node.
| Causes: insufficient CPU/memory, no matching nodeSelector,
|         untolerated taints, PVC not bound, no nodes available.
|
| Debug: kubectl describe pod <pod> (check Events)
|        kubectl get nodes (check node status)
|        kubectl describe node <node> (check allocatable)
+----------------+

+--- OOMKilled ---+
| Container exceeded its memory limit.
| Exit code: 137
| Causes: memory leak, limit set too low, JVM heap too large.
|
| Debug: kubectl describe pod <pod> (Last State: OOMKilled)
|        Increase memory limit or fix the application
+-----------------+

+--- CreateContainerConfigError ---+
| Cannot create the container due to config issues.
| Causes: referenced ConfigMap/Secret does not exist,
|         invalid volume mount configuration.
|
| Debug: kubectl describe pod <pod>
|        kubectl get configmap/secret <name>
+----------------------------------+
```

### Health Probes

```
+--- Startup Probe ---+     +--- Liveness Probe ---+     +--- Readiness Probe ---+
| "Has the app       |     | "Is the app still    |     | "Can the app handle  |
|  started yet?"     |     |  alive?"             |     |  traffic?"           |
|                    |     |                      |     |                      |
| Runs FIRST.        |     | Runs AFTER startup.  |     | Runs continuously.   |
| Disables liveness  |     | If it fails:         |     | If it fails:         |
| and readiness      |     |   Container is       |     |   Pod removed from   |
| until it succeeds. |     |   KILLED and         |     |   Service endpoints  |
|                    |     |   restarted.         |     |   (no traffic sent). |
| Use for: slow-     |     |                      |     |   Container NOT      |
| starting apps.     |     | Use for: detecting   |     |   killed.            |
+--------------------+     | deadlocks.           |     |                      |
                           +----------------------+     | Use for: temporary   |
                                                        | unavailability.      |
                                                        +----------------------+
```

---

## Step-by-Step Practical

### 1. Basic inspection commands

```bash
# Deploy a test application
kubectl create deployment web --image=nginx:1.25 --replicas=3

# Get pod status
kubectl get pods
kubectl get pods -o wide            # Node, IP, status
kubectl get pods -o yaml            # Full YAML
kubectl get pods --show-labels      # See labels

# Describe a pod (the most useful debugging command)
kubectl describe pod <pod-name>
# Key sections to read:
#   Status, Conditions, Containers (State, Last State, Restart Count),
#   Events (at the bottom -- most recent events last)

# Get events cluster-wide
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events -n default --field-selector reason=Failed

# Watch events in real-time
kubectl get events -w
```

### 2. Logs

```bash
# View logs
kubectl logs <pod-name>

# Follow logs (like tail -f)
kubectl logs <pod-name> -f

# View previous container logs (after a crash)
kubectl logs <pod-name> --previous

# Multi-container pod: specify the container
kubectl logs <pod-name> -c <container-name>

# View last N lines
kubectl logs <pod-name> --tail=50

# View logs since a time
kubectl logs <pod-name> --since=1h
kubectl logs <pod-name> --since=5m

# View logs from all pods in a deployment
kubectl logs deployment/web

# View logs from all pods with a label
kubectl logs -l app=web --all-containers=true
```

### 3. Exec into a running container

```bash
# Get a shell
kubectl exec -it <pod-name> -- /bin/bash
# or
kubectl exec -it <pod-name> -- /bin/sh

# Run a single command
kubectl exec <pod-name> -- ls /etc/nginx/conf.d/
kubectl exec <pod-name> -- cat /etc/resolv.conf
kubectl exec <pod-name> -- env

# Multi-container pod
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh

# Common debugging inside a container:
# Check DNS
kubectl exec <pod-name> -- nslookup kubernetes.default
# Check connectivity
kubectl exec <pod-name> -- wget -qO- http://service-name:80
# Check processes
kubectl exec <pod-name> -- ps aux
# Check network
kubectl exec <pod-name> -- netstat -tlnp
```

### 4. Resource monitoring (kubectl top)

```bash
# Install metrics-server (required for kubectl top)
# minikube:
minikube addons enable metrics-server

# Or install manually:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Wait for metrics-server to be ready (may take 1-2 minutes)
kubectl get pods -n kube-system -l k8s-app=metrics-server

# Node resource usage
kubectl top nodes
# NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
# minikube   250m         12%    1200Mi          62%

# Pod resource usage
kubectl top pods
kubectl top pods -A                         # All namespaces
kubectl top pods --sort-by=memory           # Sort by memory
kubectl top pods --sort-by=cpu              # Sort by CPU
kubectl top pods -l app=web                 # Filter by label
kubectl top pod <pod-name> --containers     # Per-container breakdown
```

### 5. Debug CrashLoopBackOff

```yaml
# Save as /tmp/crashloop-pod.yaml
# Intentionally broken pod
apiVersion: v1
kind: Pod
metadata:
  name: crashloop-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'echo "Starting..." && exit 1']
```

```bash
kubectl apply -f /tmp/crashloop-pod.yaml

# Wait and observe
kubectl get pod crashloop-demo -w
# STATUS will cycle: Running -> Error -> CrashLoopBackOff

# Debug step 1: Describe
kubectl describe pod crashloop-demo
# Look at:
#   State: Waiting (Reason: CrashLoopBackOff)
#   Last State: Terminated (Exit Code: 1)
#   Restart Count: increasing

# Debug step 2: Logs
kubectl logs crashloop-demo
# "Starting..."
# Exit code 1 means the application returned an error

kubectl logs crashloop-demo --previous
# Shows logs from the PREVIOUS crashed container

kubectl delete pod crashloop-demo
```

### 6. Debug ImagePullBackOff

```bash
# Create a pod with a non-existent image
kubectl run imagepull-demo --image=nginx:nonexistent-tag

kubectl get pod imagepull-demo -w
# STATUS: ErrImagePull -> ImagePullBackOff

kubectl describe pod imagepull-demo
# Events:
#   Failed to pull image "nginx:nonexistent-tag": ...
#   Error: ImagePullBackOff

# Fix: correct the image
kubectl set image pod/imagepull-demo imagepull-demo=nginx:1.25
# Wait... this does not work because you cannot change a pod's image
# Delete and recreate with the correct image

kubectl delete pod imagepull-demo
kubectl run imagepull-demo --image=nginx:1.25
```

### 7. Debug Pending pods

```yaml
# Save as /tmp/pending-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pending-demo
spec:
  containers:
  - name: app
    image: nginx:1.25
    resources:
      requests:
        cpu: "100"           # 100 CPU cores -- way too much
        memory: "1000Gi"     # 1 TB of RAM -- impossible
```

```bash
kubectl apply -f /tmp/pending-pod.yaml
kubectl get pod pending-demo
# STATUS: Pending

kubectl describe pod pending-demo
# Events:
#   0/1 nodes are available: 1 Insufficient cpu, 1 Insufficient memory

kubectl delete pod pending-demo
```

### 8. Debug OOMKilled

```yaml
# Save as /tmp/oom-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: oom-demo
spec:
  containers:
  - name: app
    image: python:3.11-slim
    command: ['python', '-c']
    args:
    - |
      data = []
      while True:
          data.append('x' * 10000000)  # Allocate ~10MB each iteration
    resources:
      limits:
        memory: "50Mi"        # Will be exceeded quickly
```

```bash
kubectl apply -f /tmp/oom-pod.yaml
kubectl get pod oom-demo -w
# STATUS: Running -> OOMKilled -> CrashLoopBackOff

kubectl describe pod oom-demo
# Last State: Terminated
#   Reason: OOMKilled
#   Exit Code: 137

kubectl delete pod oom-demo
```

### 9. Health probes in practice

```yaml
# Save as /tmp/probes-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: probes-demo
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports:
    - containerPort: 80

    # Startup probe: wait for slow apps to start
    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 30       # 30 * 10s = 300s max startup time
      periodSeconds: 10

    # Liveness probe: restart if the app is stuck
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 0     # Start immediately after startup probe passes
      periodSeconds: 10          # Check every 10 seconds
      failureThreshold: 3        # Restart after 3 consecutive failures
      timeoutSeconds: 1          # Timeout per check

    # Readiness probe: stop sending traffic if not ready
    readinessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 5
      failureThreshold: 3
      successThreshold: 1
```

```bash
kubectl apply -f /tmp/probes-pod.yaml
kubectl describe pod probes-demo | grep -A5 "Liveness\|Readiness\|Startup"

kubectl delete pod probes-demo
```

### 10. Probe types

```yaml
# HTTP GET probe (most common for web apps)
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    httpHeaders:
    - name: Custom-Header
      value: "probe"

# TCP Socket probe (for non-HTTP services like databases)
livenessProbe:
  tcpSocket:
    port: 3306

# Command probe (run a command inside the container)
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
```

### 11. Debug a node

```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Key sections in describe output:
#   Conditions: Ready, MemoryPressure, DiskPressure, PIDPressure
#   Capacity vs Allocatable: total vs available resources
#   Allocated resources: what is currently used
#   Events: recent issues

# Check kubelet logs (on the node)
journalctl -u kubelet -n 100 --no-pager

# Cordon a node (prevent new pods from scheduling)
kubectl cordon <node-name>

# Drain a node (evict all pods for maintenance)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Uncordon (allow scheduling again)
kubectl uncordon <node-name>
```

### 12. Comprehensive debugging session

```bash
# Full debugging workflow for a broken deployment
# Step 1: Overview
kubectl get deploy,rs,pods -l app=myapp

# Step 2: Check deployment status
kubectl rollout status deployment/myapp

# Step 3: Describe the deployment
kubectl describe deployment myapp

# Step 4: Check ReplicaSet
kubectl get rs -l app=myapp
kubectl describe rs <rs-name>

# Step 5: Check Pod
kubectl describe pod <pod-name>

# Step 6: Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Step 7: Check events
kubectl get events --sort-by=.metadata.creationTimestamp

# Step 8: Check services and endpoints
kubectl get svc,endpoints -l app=myapp

# Step 9: Check connectivity from a debug pod
kubectl run debug --image=busybox:1.36 --rm -it --restart=Never -- \
  wget -qO- http://myapp-svc:80

# Step 10: Check DNS
kubectl run debug --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup myapp-svc.default.svc.cluster.local
```

### 13. Clean up

```bash
kubectl delete deployment web
kubectl delete pod crashloop-demo imagepull-demo pending-demo oom-demo probes-demo 2>/dev/null
```

---

## Exercises

1. **CrashLoopBackOff**: Deploy a Pod with `command: ['sh', '-c', 'exit 1']`.
   Use describe and logs to identify the problem. Fix it by changing the command
   to `sleep 3600`. Verify the Pod recovers.

2. **ImagePullBackOff**: Deploy a Pod with a deliberately wrong image tag. Use
   describe to find the exact error message. Delete and redeploy with the correct image.

3. **Probe Debugging**: Deploy an nginx Pod with a liveness probe pointing to
   `/healthz` (which does not exist on nginx). Watch the Pod get repeatedly
   restarted. Check the describe output for probe failure details. Fix by
   changing the probe path to `/`.

4. **Resource Investigation**: Install metrics-server and use `kubectl top pods`
   and `kubectl top nodes` to find the most resource-hungry pods and nodes in
   your cluster. Identify any pods that are using significantly more than their
   resource requests.

5. **Full Debugging**: Have a partner (or create yourself) deploy a broken
   application (wrong image, missing ConfigMap, insufficient resources, wrong
   port in service, etc.). Use the systematic debugging methodology to identify
   and fix all issues.

---

## Knowledge Check

**Q1**: A Pod is in CrashLoopBackOff. What commands do you run first?
<details>
<summary>Answer</summary>
First, `kubectl describe pod <name>` to check the exit code, restart count, and
events. Then `kubectl logs <name> --previous` to see the logs from the crashed
container (--previous is critical because the current container may have already
restarted and have empty logs). Common causes: application errors, missing
environment variables, wrong command, or OOMKill (exit code 137).
</details>

**Q2**: What is the difference between a liveness probe and a readiness probe?
<details>
<summary>Answer</summary>
A liveness probe determines if the container is alive. If it fails, the container
is killed and restarted. Use it to detect deadlocks or unrecoverable states. A
readiness probe determines if the container can handle traffic. If it fails, the
Pod is removed from Service endpoints (no traffic is sent) but the container is NOT
killed. Use it for temporary unavailability like loading a cache or waiting for a
dependency.
</details>

**Q3**: How do you view logs from a container that has already crashed?
<details>
<summary>Answer</summary>
Use `kubectl logs <pod-name> --previous`. This shows logs from the previous
container instance. Without --previous, you see logs from the current container,
which may be empty if it just restarted. For multi-container pods, add
`-c <container-name>`.
</details>

**Q4**: A Pod is stuck in Pending state. What are the possible causes?
<details>
<summary>Answer</summary>
Common causes: (1) Insufficient resources -- no node has enough CPU or memory to
satisfy the Pod's requests. (2) No matching nodeSelector or node affinity. (3)
All feasible nodes have taints that the Pod does not tolerate. (4) PersistentVolumeClaim
is not bound (no available PV). (5) Resource quota exceeded in the namespace. Check
with `kubectl describe pod` to see the specific scheduling failure message.
</details>

**Q5**: What does exit code 137 mean?
<details>
<summary>Answer</summary>
Exit code 137 = 128 + 9, meaning the process was killed by signal 9 (SIGKILL).
In Kubernetes, this almost always means OOMKilled -- the container exceeded its
memory limit and was terminated by the kernel. Fix by increasing the memory limit
or reducing the application's memory usage.
</details>
