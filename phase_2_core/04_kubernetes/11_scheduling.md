# Lesson 11: Scheduling -- Controlling Where Pods Land

## Why This Matters in DevOps

The Kubernetes scheduler assigns Pods to nodes automatically, but default behavior
is not always sufficient. You may need GPU workloads on GPU nodes, databases on
SSD-backed nodes, frontend pods spread across availability zones, or certain pods
kept away from each other for high availability. Understanding scheduling constraints
lets you optimize resource utilization, ensure availability, and meet compliance
requirements.

The CKA exam tests nodeSelector, node affinity, taints/tolerations, and Pod
affinity/anti-affinity. These are high-value topics because they involve writing
YAML from scratch under time pressure.

---

## Core Concepts

### How the Scheduler Works

```
New Pod created (no node assigned)
         |
         v
+--- kube-scheduler ---------------------+
|                                        |
| Step 1: FILTERING (which nodes CAN?)   |
|   - Enough CPU/memory?                |
|   - Does it match nodeSelector?        |
|   - Does it tolerate node taints?      |
|   - Does it satisfy affinity rules?    |
|   Result: List of feasible nodes       |
|                                        |
| Step 2: SCORING (which node is BEST?)  |
|   - Least resource usage               |
|   - Topology spread                    |
|   - Affinity preferences               |
|   Result: Highest-scoring node wins    |
|                                        |
| Step 3: BINDING                        |
|   - Assigns Pod to the selected node   |
|   - Updates Pod spec via API server    |
+----------------------------------------+
         |
         v
kubelet on selected node starts the Pod
```

### Scheduling Tools Overview

```
+-------------------------------------------+---------------------------+
| Tool                                      | Purpose                   |
+-------------------------------------------+---------------------------+
| nodeSelector                              | Simple: "run on nodes     |
|                                           |  with this label"         |
+-------------------------------------------+---------------------------+
| Node Affinity                             | Advanced: required or     |
|                                           |  preferred node labels    |
+-------------------------------------------+---------------------------+
| Node Anti-Affinity                        | "Avoid nodes with this    |
|                                           |  label"                   |
+-------------------------------------------+---------------------------+
| Pod Affinity                              | "Run near pods with this  |
|                                           |  label" (same node/zone)  |
+-------------------------------------------+---------------------------+
| Pod Anti-Affinity                         | "Run away from pods with  |
|                                           |  this label"              |
+-------------------------------------------+---------------------------+
| Taints & Tolerations                      | Node repels pods unless   |
|                                           |  they tolerate the taint  |
+-------------------------------------------+---------------------------+
| Topology Spread Constraints               | Even distribution across  |
|                                           |  zones/nodes              |
+-------------------------------------------+---------------------------+
```

### Taints and Tolerations

```
Node with taint:
+--- Node: gpu-node-1 --------------------+
| Taint: gpu=true:NoSchedule              |
|                                          |
| Regular pods: REJECTED (no toleration)   |
| GPU pods:     ACCEPTED (have toleration) |
+------------------------------------------+

Think of it as:
  Taint  = "I'm special, stay away unless you know how to handle me"
  Toleration = "I know how to handle you, let me in"
```

Taint effects:
| Effect | Behavior |
|---|---|
| `NoSchedule` | Pods without toleration are not scheduled on the node. Existing pods stay. |
| `PreferNoSchedule` | Scheduler tries to avoid the node but may use it if necessary. |
| `NoExecute` | Pods without toleration are evicted (removed) from the node. |

---

## Step-by-Step Practical

### 1. nodeSelector (simplest scheduling)

```bash
# First, label a node
kubectl label node minikube disktype=ssd

# Verify the label
kubectl get nodes --show-labels | grep disktype
```

```yaml
# Save as /tmp/nodeselector-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-pod
spec:
  nodeSelector:
    disktype: ssd           # Only schedule on nodes with disktype=ssd
  containers:
  - name: app
    image: nginx:1.25
```

```bash
kubectl apply -f /tmp/nodeselector-pod.yaml
kubectl get pod ssd-pod -o wide  # Check which node it landed on

# Remove the label and try again
kubectl delete pod ssd-pod
kubectl label node minikube disktype-
kubectl apply -f /tmp/nodeselector-pod.yaml
kubectl get pod ssd-pod
# STATUS: Pending (no node matches the selector)

kubectl describe pod ssd-pod | grep -A3 Events
# "0/1 nodes are available: 1 node(s) didn't match Pod's node affinity/selector"

# Fix by re-adding the label
kubectl label node minikube disktype=ssd
# Pod will be scheduled automatically

kubectl delete pod ssd-pod
```

### 2. Node Affinity

```yaml
# Save as /tmp/node-affinity.yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-demo
spec:
  affinity:
    nodeAffinity:
      # REQUIRED: Pod MUST be scheduled on matching nodes
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
            - nvme
      # PREFERRED: Scheduler TRIES to pick matching nodes
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80               # 1-100, higher = stronger preference
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - us-east-1a
  containers:
  - name: app
    image: nginx:1.25
```

```bash
kubectl apply -f /tmp/node-affinity.yaml
kubectl get pod affinity-demo -o wide
kubectl delete pod affinity-demo
```

Operators available for matchExpressions:
- `In` -- value is in the list
- `NotIn` -- value is not in the list
- `Exists` -- key exists (no value check)
- `DoesNotExist` -- key does not exist
- `Gt` -- value is greater than (numeric comparison)
- `Lt` -- value is less than

### 3. Pod Affinity (co-locate Pods)

```yaml
# Save as /tmp/pod-affinity.yaml
# Schedule the cache pod near the web pod
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
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
      - name: nginx
        image: nginx:1.25
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cache
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cache
  template:
    metadata:
      labels:
        app: cache
    spec:
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web
            topologyKey: kubernetes.io/hostname
            # "Schedule me on the SAME NODE as pods with app=web"
      containers:
      - name: redis
        image: redis:7
```

```bash
kubectl apply -f /tmp/pod-affinity.yaml
kubectl get pods -o wide -l 'app in (web,cache)'
# Cache pods should be on the same node(s) as web pods

kubectl delete deploy web-app cache
```

### 4. Pod Anti-Affinity (spread Pods apart)

```yaml
# Save as /tmp/pod-anti-affinity.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-spread
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-spread
  template:
    metadata:
      labels:
        app: web-spread
    spec:
      affinity:
        podAntiAffinity:
          # REQUIRED: no two pods with app=web-spread on the same node
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web-spread
            topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.25
```

```bash
kubectl apply -f /tmp/pod-anti-affinity.yaml
kubectl get pods -l app=web-spread -o wide
# On a single-node cluster, only 1 pod can be scheduled (others Pending)
# On a multi-node cluster, each pod lands on a different node

kubectl delete deploy web-spread
```

### 5. Taints and Tolerations

```bash
# Add a taint to a node
kubectl taint nodes minikube dedicated=gpu:NoSchedule

# Try to schedule a regular pod
kubectl run no-toleration --image=nginx:1.25
kubectl get pod no-toleration
# STATUS: Pending (tainted node is the only node)

kubectl describe pod no-toleration | grep -A5 Events
# "0/1 nodes are available: 1 node(s) had untolerable taint"
```

```yaml
# Save as /tmp/toleration-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
  containers:
  - name: app
    image: nginx:1.25
```

```bash
kubectl apply -f /tmp/toleration-pod.yaml
kubectl get pod gpu-pod -o wide
# This pod is scheduled because it tolerates the taint

# Remove the taint
kubectl taint nodes minikube dedicated=gpu:NoSchedule-
# Note the minus sign at the end

# Now the no-toleration pod can be scheduled too
kubectl get pods
kubectl delete pod no-toleration gpu-pod
```

### 6. Tolerate all taints

```yaml
# Tolerate ANY taint (used by DaemonSets that must run everywhere)
spec:
  tolerations:
  - operator: "Exists"    # Matches any taint key
    effect: ""             # Matches any effect
```

### 7. Topology Spread Constraints

```yaml
# Save as /tmp/topology-spread.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spread-demo
spec:
  replicas: 6
  selector:
    matchLabels:
      app: spread-demo
  template:
    metadata:
      labels:
        app: spread-demo
    spec:
      topologySpreadConstraints:
      - maxSkew: 1                              # Max difference between zones
        topologyKey: topology.kubernetes.io/zone # Spread across zones
        whenUnsatisfiable: DoNotSchedule         # or ScheduleAnyway
        labelSelector:
          matchLabels:
            app: spread-demo
      containers:
      - name: nginx
        image: nginx:1.25
```

```bash
kubectl apply -f /tmp/topology-spread.yaml
kubectl get pods -l app=spread-demo -o wide
# In a multi-zone cluster, pods are evenly distributed across zones

kubectl delete deploy spread-demo
```

### 8. Priority Classes

```yaml
# Save as /tmp/priority.yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "High priority for critical workloads"
preemptionPolicy: PreemptLowerPriority    # Can evict lower-priority pods
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
globalDefault: false
description: "Low priority for batch workloads"
---
apiVersion: v1
kind: Pod
metadata:
  name: high-priority-pod
spec:
  priorityClassName: high-priority
  containers:
  - name: app
    image: nginx:1.25
    resources:
      requests:
        cpu: "100m"
        memory: "64Mi"
```

```bash
kubectl apply -f /tmp/priority.yaml
kubectl get priorityclasses
kubectl get pod high-priority-pod -o yaml | grep priority

kubectl delete pod high-priority-pod
kubectl delete priorityclass high-priority low-priority
```

### 9. Manual scheduling (nodeName)

```yaml
# Save as /tmp/manual-schedule.yaml
# Bypasses the scheduler entirely
apiVersion: v1
kind: Pod
metadata:
  name: manual-pod
spec:
  nodeName: minikube          # Directly assign to this node
  containers:
  - name: app
    image: nginx:1.25
```

```bash
kubectl apply -f /tmp/manual-schedule.yaml
kubectl get pod manual-pod -o wide

kubectl delete pod manual-pod
```

### 10. Practical: control placement for a real workload

```yaml
# Save as /tmp/production-scheduling.yaml
# A production-grade scheduling setup
apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: production-api
  template:
    metadata:
      labels:
        app: production-api
    spec:
      # Prefer nodes with SSD storage
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: disktype
                operator: In
                values:
                - ssd
        # Spread pods across nodes for HA
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - production-api
              topologyKey: kubernetes.io/hostname
      # Tolerate a specific taint
      tolerations:
      - key: "workload"
        operator: "Equal"
        value: "production"
        effect: "NoSchedule"
      containers:
      - name: api
        image: nginx:1.25
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

```bash
kubectl apply -f /tmp/production-scheduling.yaml
kubectl get pods -l app=production-api -o wide
kubectl delete deploy production-api
```

---

## Exercises

1. **nodeSelector**: Label one node with `tier=frontend`. Create a Pod with a
   nodeSelector for that label. Verify it schedules. Remove the label and create
   a second Pod. Observe it stays Pending. Re-add the label and watch it schedule.

2. **Taints and Tolerations**: Taint a node with `environment=production:NoSchedule`.
   Deploy a Pod without a toleration (stays Pending). Deploy another with the
   toleration (schedules). Remove the taint and observe what happens.

3. **Pod Anti-Affinity**: Create a Deployment with 3 replicas and required Pod
   anti-affinity on `kubernetes.io/hostname`. On a single-node cluster, observe
   that only 1 Pod can schedule. Change to `preferred` and observe all 3 schedule.

4. **Combined Scheduling**: Create a Deployment that uses nodeSelector (specific
   node label), Pod anti-affinity (spread across nodes), and a toleration (for a
   tainted node). Verify the scheduling behavior.

5. **Topology Spread**: In a multi-node cluster (use kind with 3 nodes), create a
   Deployment with 6 replicas and a topology spread constraint on
   `kubernetes.io/hostname` with `maxSkew: 1`. Verify pods are evenly distributed.

---

## Knowledge Check

**Q1**: What is the difference between nodeSelector and node affinity?
<details>
<summary>Answer</summary>
nodeSelector is simple key-value matching -- the Pod must go on a node with that
exact label. Node affinity is more expressive: it supports operators (In, NotIn,
Exists, etc.), multiple terms (OR logic between terms), and has both "required"
(hard constraint) and "preferred" (soft constraint) variants. Node affinity
replaces nodeSelector for complex scheduling needs.
</details>

**Q2**: What is the difference between taints/tolerations and node affinity?
<details>
<summary>Answer</summary>
Node affinity attracts Pods TO specific nodes ("I want to run here"). Taints
repel Pods FROM specific nodes ("Stay away unless you tolerate me"). They work
in opposite directions. A taint on a node prevents all Pods from scheduling
unless they have a matching toleration. Node affinity on a Pod makes it prefer
or require specific nodes. They are often used together.
</details>

**Q3**: What does `topologyKey: kubernetes.io/hostname` mean in a Pod anti-affinity rule?
<details>
<summary>Answer</summary>
It means "do not schedule two matching Pods on the same hostname (node)." The
topologyKey defines the scope of the affinity/anti-affinity rule. Other common
values are `topology.kubernetes.io/zone` (spread across availability zones) and
`topology.kubernetes.io/region` (spread across regions).
</details>

**Q4**: A Pod is stuck in Pending state. The describe output shows "0/3 nodes are
available: 1 node(s) had untolerable taint, 2 node(s) didn't match Pod's node
affinity." What should you check?
<details>
<summary>Answer</summary>
Check two things: (1) One node has a taint that the Pod does not tolerate -- either
add a toleration to the Pod or remove the taint from the node. (2) Two nodes do
not have the labels required by the Pod's node affinity -- either add the required
labels to those nodes or adjust the Pod's affinity rules.
</details>

**Q5**: What is the effect of `NoExecute` vs `NoSchedule` on a taint?
<details>
<summary>Answer</summary>
`NoSchedule` prevents new Pods without tolerations from being scheduled on the
node, but existing Pods are not affected. `NoExecute` is more aggressive -- it
evicts existing Pods that do not tolerate the taint AND prevents new ones from
scheduling. NoExecute can also specify a `tolerationSeconds` to give Pods a
grace period before eviction.
</details>
