# Lesson 03: Pods -- The Smallest Deployable Unit

## Why This Matters in DevOps

Every container you run in Kubernetes runs inside a Pod. Pods are the atom of
Kubernetes -- you cannot go smaller. Understanding Pod lifecycle, resource
management, and multi-container patterns is fundamental to debugging production
issues. When your application is OOMKilled or stuck in CrashLoopBackOff, you need
to understand what happened at the Pod level.

The CKA exam heavily tests Pod creation, both imperatively and declaratively. You
will write Pod YAML from memory under time pressure.

---

## Core Concepts

### What Is a Pod?

A Pod is a group of one or more containers that:
- Share the same network namespace (same IP address, same ports)
- Share the same storage volumes
- Are co-scheduled on the same node
- Have a shared lifecycle (they start and stop together)

```
+--- Pod (10.244.1.5) -----------------------+
|                                             |
| +-- Container 1 --+  +-- Container 2 --+   |
| |   nginx         |  |   log-shipper   |   |
| |   port 80       |  |   port 9090     |   |
| +-------+---------+  +--------+--------+   |
|         |                      |            |
|         +--- Shared Volume ---+             |
|         |   /var/log/nginx    |             |
|         +---------------------+             |
|                                             |
| localhost communication works between       |
| containers in the same Pod                  |
+---------------------------------------------+
```

**Critical rule**: In production, you almost never create Pods directly. You use
Deployments, StatefulSets, or other workload controllers that manage Pods for you.
Bare Pods are not restarted if a node fails.

### Pod Lifecycle

```
+----------+     +--------+     +---------+     +------------+
| Pending  | --> | Running | --> | Succeed | or  | Failed     |
+----------+     +--------+     +---------+     +------------+
     |                |
     |                +--> CrashLoopBackOff (container keeps crashing)
     |
     +--> ImagePullBackOff (cannot pull container image)
```

**Pod Phases**:
- **Pending**: Pod accepted but not yet scheduled or images not yet pulled
- **Running**: At least one container is running
- **Succeeded**: All containers exited with code 0 (common for Jobs)
- **Failed**: At least one container exited with a non-zero code
- **Unknown**: Node communication lost

### Labels and Selectors

Labels are key-value pairs attached to objects. Selectors query objects by labels.
This is how Kubernetes connects things together.

```
Pod with labels:
  metadata:
    labels:
      app: frontend
      env: production
      version: v2

Selector examples:
  app=frontend                    # equality-based
  app in (frontend, backend)      # set-based
  env=production,version=v2       # multiple labels (AND logic)
```

Labels are not just for organization -- Services, Deployments, and other resources
use label selectors to find which Pods they manage.

### Annotations

Annotations are also key-value pairs but are meant for non-identifying metadata:
- Build info, git commit hashes
- Tool configuration (e.g., Prometheus scrape config)
- Timestamps, author information

Annotations cannot be used in selectors.

### Resource Requests and Limits

```
+-- Node (4 CPU, 8 Gi RAM) ---------+
|                                    |
| +-- Pod A -----+  +-- Pod B -----+|
| | Request:     |  | Request:     ||
| |   CPU: 500m  |  |   CPU: 1     ||
| |   RAM: 256Mi |  |   RAM: 512Mi ||
| | Limit:       |  | Limit:       ||
| |   CPU: 1     |  |   CPU: 2     ||
| |   RAM: 512Mi |  |   RAM: 1Gi   ||
| +--------------+  +--------------+|
|                                    |
| Allocatable remaining:            |
|   CPU: 2500m, RAM: ~6.25Gi        |
+------------------------------------+
```

- **Requests**: The guaranteed minimum. The scheduler uses this to place Pods.
- **Limits**: The maximum. Exceeding CPU limit causes throttling. Exceeding memory
  limit causes OOMKill (the container is killed).
- **CPU**: Measured in millicores. 1000m = 1 CPU core. 500m = half a core.
- **Memory**: Measured in bytes. Mi = mebibytes, Gi = gibibytes.

---

## Step-by-Step Practical

### 1. Create a Pod imperatively

```bash
# Simple pod creation
kubectl run nginx-pod --image=nginx:1.25

# Check it is running
kubectl get pods
kubectl get pods -o wide  # see the node and IP

# See detailed info
kubectl describe pod nginx-pod

# View logs
kubectl logs nginx-pod

# Execute a command inside the pod
kubectl exec nginx-pod -- ls /usr/share/nginx/html

# Get an interactive shell
kubectl exec -it nginx-pod -- /bin/bash

# Delete the pod
kubectl delete pod nginx-pod
```

### 2. Create a Pod declaratively

```yaml
# Save as /tmp/simple-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
  labels:
    app: web
    env: dev
  annotations:
    description: "A simple nginx web server for testing"
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
```

```bash
kubectl apply -f /tmp/simple-pod.yaml
kubectl get pod web-server
kubectl get pod web-server --show-labels
kubectl delete pod web-server
```

### 3. Pod with resource requests and limits

```yaml
# Save as /tmp/resource-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
  labels:
    app: demo
spec:
  containers:
  - name: app
    image: nginx:1.25
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    ports:
    - containerPort: 80
```

```bash
kubectl apply -f /tmp/resource-pod.yaml
kubectl describe pod resource-demo | grep -A 6 "Limits\|Requests"
kubectl delete pod resource-demo
```

### 4. Multi-container Pod (sidecar pattern)

```yaml
# Save as /tmp/sidecar-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
  labels:
    app: sidecar-demo
spec:
  containers:
  # Main application container
  - name: app
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      while true; do
        echo "$(date) - Application log entry" >> /var/log/app/app.log
        sleep 5
      done
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app

  # Sidecar: log shipper
  - name: log-shipper
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - tail -f /var/log/app/app.log
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app

  volumes:
  - name: shared-logs
    emptyDir: {}
```

```bash
kubectl apply -f /tmp/sidecar-pod.yaml

# Check both containers are running
kubectl get pod sidecar-demo

# View logs from each container
kubectl logs sidecar-demo -c app          # no output (writes to file)
kubectl logs sidecar-demo -c log-shipper  # shows the log entries

# Exec into a specific container
kubectl exec -it sidecar-demo -c app -- cat /var/log/app/app.log

kubectl delete pod sidecar-demo
```

### 5. Working with labels

```bash
# Add a label to an existing pod
kubectl run labeled-pod --image=nginx:1.25
kubectl label pod labeled-pod team=backend

# Show labels
kubectl get pods --show-labels

# Filter by label
kubectl get pods -l app=labeled-pod
kubectl get pods -l team=backend

# Remove a label (note the minus sign)
kubectl label pod labeled-pod team-

# Overwrite a label
kubectl label pod labeled-pod app=api --overwrite

kubectl delete pod labeled-pod
```

### 6. Generate YAML for CKA speed

```bash
# Generate pod YAML without creating it
kubectl run exam-pod --image=nginx:1.25 \
  --port=80 \
  --labels="app=exam,tier=frontend" \
  --dry-run=client -o yaml

# Save to file and edit
kubectl run exam-pod --image=nginx:1.25 \
  --dry-run=client -o yaml > /tmp/exam-pod.yaml

# Then add resources, volumes, etc. by editing the file
```

### 7. Pod with environment variables

```yaml
# Save as /tmp/env-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'echo "DB_HOST=$DB_HOST DB_PORT=$DB_PORT" && sleep 3600']
    env:
    - name: DB_HOST
      value: "postgres.default.svc.cluster.local"
    - name: DB_PORT
      value: "5432"
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
```

```bash
kubectl apply -f /tmp/env-pod.yaml
kubectl logs env-demo
# Output: DB_HOST=postgres.default.svc.cluster.local DB_PORT=5432

kubectl exec env-demo -- env | grep -E "DB_|POD_"
kubectl delete pod env-demo
```

---

## Exercises

1. **Basic Pod**: Create a Pod named `redis-pod` running `redis:7` with the label
   `app=cache`. Verify it is running, check its IP address, then delete it.

2. **Resource Pod**: Create a Pod with an nginx container that requests 100m CPU
   and 64Mi memory, with limits of 200m CPU and 128Mi memory. Use `kubectl describe`
   to confirm the resource settings.

3. **Multi-Container**: Create a Pod with two containers: one running `nginx:1.25`
   and one running `busybox:1.36` that runs `wget -qO- http://localhost:80` every
   10 seconds. Use a shared emptyDir volume if needed. View the logs of the busybox
   container to see the nginx HTML output.

4. **Label Selection**: Create 5 pods with different combinations of labels
   (`app=web` or `app=api`, `env=dev` or `env=prod`). Practice filtering with
   `-l app=web`, `-l env=prod`, `-l 'app in (web, api)'`, and `-l app=web,env=prod`.
   Clean up all pods when done.

5. **YAML Generation**: Using only `kubectl run --dry-run=client -o yaml`, generate
   a Pod manifest for a `python:3.11` container named `py-app`. Redirect it to a
   file. Edit the file to add resource limits and an environment variable, then
   apply it.

---

## Knowledge Check

**Q1**: Why should you not create bare Pods in production?
<details>
<summary>Answer</summary>
Bare Pods are not managed by a controller. If the node running the Pod fails, the
Pod is lost and not rescheduled. Deployments and other controllers create Pods AND
ensure replacements are created when Pods die. Bare Pods are only useful for
one-off debugging or testing.
</details>

**Q2**: Two containers in the same Pod want to communicate. What address do they use?
<details>
<summary>Answer</summary>
They use `localhost`. Containers within the same Pod share the same network
namespace, so they can reach each other on 127.0.0.1 (localhost) using different
ports. They can also share data through volumes.
</details>

**Q3**: What happens when a container exceeds its memory limit?
<details>
<summary>Answer</summary>
The container is OOMKilled (Out Of Memory Killed). The kubelet terminates the
container. If the Pod is managed by a controller, Kubernetes will restart it
according to the restart policy, potentially leading to CrashLoopBackOff if it
keeps exceeding the limit.
</details>

**Q4**: What is the difference between labels and annotations?
<details>
<summary>Answer</summary>
Labels are key-value pairs used to identify and select objects. Services,
Deployments, and other resources use label selectors to find which Pods they
manage. Annotations are key-value pairs used for non-identifying metadata like
build info, tool configuration, or documentation. Annotations cannot be used
in selectors.
</details>

**Q5**: What does `kubectl run myapp --image=nginx --dry-run=client -o yaml` do?
<details>
<summary>Answer</summary>
It generates the YAML manifest for a Pod named "myapp" with an nginx container,
but does NOT create it in the cluster (dry-run=client means the request never
reaches the API server). The YAML is printed to stdout. This is a critical CKA
exam technique for quickly scaffolding manifests.
</details>
