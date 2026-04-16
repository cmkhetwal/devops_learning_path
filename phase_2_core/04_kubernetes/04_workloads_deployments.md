# Lesson 04: Workloads -- Deployments and ReplicaSets

## Why This Matters in DevOps

Deployments are the workhorse of Kubernetes. They handle the vast majority of
stateless application workloads. As a DevOps engineer, you will create Deployments
dozens of times a week. Understanding rolling updates, rollbacks, and scaling is
critical for zero-downtime deployments -- the standard that modern organizations
expect.

The CKA exam tests Deployment creation, scaling, rolling updates, and rollbacks.
These are high-value topics to master.

---

## Core Concepts

### Why Not Bare Pods?

```
Bare Pod:
  You create Pod --> Node dies --> Pod is GONE forever.
  No self-healing. No scaling. No updates.

Deployment manages ReplicaSet manages Pods:
  Deployment --> ReplicaSet --> Pod, Pod, Pod
                                  |
                            Node dies, Pod lost
                                  |
                            ReplicaSet detects 2/3
                                  |
                            Creates replacement Pod
                                  |
                            3/3 again. Self-healed.
```

### The Deployment Hierarchy

```
+--- Deployment (nginx-deploy) --------+
| strategy: RollingUpdate              |
| replicas: 3                          |
|                                      |
| +--- ReplicaSet (nginx-abc123) ----+ |
| | replicas: 3                      | |
| |                                  | |
| | +-- Pod 1 --+ +-- Pod 2 --+     | |
| | | nginx:1.25| | nginx:1.25|     | |
| | +-----------+ +-----------+     | |
| |                                  | |
| | +-- Pod 3 --+                   | |
| | | nginx:1.25|                   | |
| | +-----------+                   | |
| +----------------------------------+ |
+--------------------------------------+
```

**Deployment**: Declares the desired state (image, replicas, strategy).
**ReplicaSet**: Ensures the correct number of Pod replicas exist.
**Pod**: The actual running container(s).

You interact with the Deployment. The Deployment manages the ReplicaSet. The
ReplicaSet manages the Pods. You rarely interact with ReplicaSets directly.

### Rolling Update Mechanics

When you change the Pod template (e.g., update the image version):

```
Step 1: New ReplicaSet created with 0 replicas
+--- Deployment ----------------------------+
| +--- RS-old (3/3) ---+  +--- RS-new ---+ |
| | Pod Pod Pod        |  | (0/3)        | |
| +--------------------+  +--------------+ |
+-------------------------------------------+

Step 2: Scale up new, scale down old (controlled by maxSurge/maxUnavailable)
+--- Deployment ----------------------------+
| +--- RS-old (2/3) ---+  +--- RS-new ---+ |
| | Pod Pod            |  | Pod (1/3)    | |
| +--------------------+  +--------------+ |
+-------------------------------------------+

Step 3: Continue rolling
+--- Deployment ----------------------------+
| +--- RS-old (1/3) ---+  +--- RS-new ---+ |
| | Pod                |  | Pod Pod (2/3)| |
| +--------------------+  +--------------+ |
+-------------------------------------------+

Step 4: Complete
+--- Deployment ----------------------------+
| +--- RS-old (0/3) ---+  +--- RS-new ---+ |
| | (kept for rollback)|  | Pod Pod Pod  | |
| +--------------------+  | (3/3)        | |
|                          +--------------+ |
+-------------------------------------------+
```

### Deployment Strategies

**RollingUpdate** (default):
- Gradually replaces old Pods with new ones
- `maxSurge`: How many extra Pods can exist during update (default 25%)
- `maxUnavailable`: How many Pods can be down during update (default 25%)
- Zero downtime if configured correctly

**Recreate**:
- Kills ALL old Pods first, then creates new ones
- Causes downtime
- Use when the app cannot run two versions simultaneously (e.g., database schema conflict)

---

## Step-by-Step Practical

### 1. Create a Deployment imperatively

```bash
# Create a deployment
kubectl create deployment nginx-deploy --image=nginx:1.24 --replicas=3

# Check the deployment
kubectl get deployments
kubectl get deploy  # shorthand

# See the ReplicaSet it created
kubectl get replicasets
kubectl get rs  # shorthand

# See the Pods it created
kubectl get pods

# All together
kubectl get deploy,rs,pods
```

### 2. Create a Deployment declaratively

```yaml
# Save as /tmp/web-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
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
        image: nginx:1.24
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "64Mi"
          limits:
            cpu: "200m"
            memory: "128Mi"
```

```bash
kubectl apply -f /tmp/web-deploy.yaml

# Watch the rollout
kubectl rollout status deployment/web-app

# Expected output:
# deployment "web-app" successfully rolled out
```

**Important**: The `selector.matchLabels` MUST match `template.metadata.labels`.
This is how the Deployment knows which Pods belong to it.

### 3. Scaling

```bash
# Scale imperatively
kubectl scale deployment web-app --replicas=5
kubectl get pods  # should see 5 pods

# Scale back down
kubectl scale deployment web-app --replicas=3

# Scale via edit (opens in editor)
kubectl edit deployment web-app
# Change replicas: to desired number, save and exit

# Scale via patch
kubectl patch deployment web-app -p '{"spec":{"replicas":4}}'
```

### 4. Rolling update

```bash
# Update the image (triggers a rolling update)
kubectl set image deployment/web-app nginx=nginx:1.25

# Watch the rollout in real time
kubectl rollout status deployment/web-app

# See the update happening
kubectl get pods -w  # watch mode, Ctrl+C to exit

# Check rollout history
kubectl rollout history deployment/web-app

# See details of a specific revision
kubectl rollout history deployment/web-app --revision=2
```

### 5. Rollback

```bash
# Intentionally deploy a bad image
kubectl set image deployment/web-app nginx=nginx:nonexistent

# Watch it fail
kubectl rollout status deployment/web-app
# Pods will be stuck in ErrImagePull / ImagePullBackOff

kubectl get pods
# Some pods will have ImagePullBackOff status

# Rollback to the previous version
kubectl rollout undo deployment/web-app

# Rollback to a specific revision
kubectl rollout undo deployment/web-app --to-revision=1

# Verify
kubectl rollout status deployment/web-app
kubectl get pods  # all should be Running
```

### 6. Deployment with strategy configuration

```yaml
# Save as /tmp/rolling-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-demo
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # At most 5 pods during update (4 + 1)
      maxUnavailable: 0     # All 4 must stay available (zero downtime)
  selector:
    matchLabels:
      app: rolling-demo
  template:
    metadata:
      labels:
        app: rolling-demo
    spec:
      containers:
      - name: app
        image: nginx:1.24
        ports:
        - containerPort: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

```bash
kubectl apply -f /tmp/rolling-deploy.yaml
kubectl rollout status deployment/rolling-demo

# Trigger an update
kubectl set image deployment/rolling-demo app=nginx:1.25

# Watch carefully: you should see one new pod start and become ready
# before any old pod is terminated (because maxUnavailable: 0)
kubectl get pods -w
```

### 7. Recreate strategy

```yaml
# Save as /tmp/recreate-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recreate-demo
spec:
  replicas: 3
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: recreate-demo
  template:
    metadata:
      labels:
        app: recreate-demo
    spec:
      containers:
      - name: app
        image: nginx:1.24
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f /tmp/recreate-deploy.yaml
kubectl rollout status deployment/recreate-demo

# Update -- all pods will be killed first, then new ones created
kubectl set image deployment/recreate-demo app=nginx:1.25
kubectl get pods -w
# You will see all old pods Terminating before new ones start
```

### 8. Record changes and annotate

```bash
# Record the cause of the change (adds annotation)
kubectl set image deployment/web-app nginx=nginx:1.25 --record
# Note: --record is deprecated but still in the CKA exam scope
# Alternative: use annotations manually
kubectl annotate deployment/web-app kubernetes.io/change-cause="Updated to nginx 1.25"

# View history with change causes
kubectl rollout history deployment/web-app
```

### 9. Pause and resume rollouts

```bash
# Pause the deployment (prevents any rollout)
kubectl rollout pause deployment/web-app

# Make multiple changes without triggering multiple rollouts
kubectl set image deployment/web-app nginx=nginx:1.25
kubectl set resources deployment/web-app -c nginx --limits=cpu=200m,memory=256Mi

# Resume to trigger a single rollout with all changes
kubectl rollout resume deployment/web-app
kubectl rollout status deployment/web-app
```

### 10. Clean up

```bash
kubectl delete deployment web-app rolling-demo recreate-demo nginx-deploy
```

---

## Exercises

1. **Full Lifecycle**: Create a Deployment named `api-server` with image `httpd:2.4`
   and 3 replicas. Scale it to 5. Update the image to `httpd:2.4.58`. Roll back to
   the original version. Delete the Deployment.

2. **Zero Downtime**: Create a Deployment with `maxSurge: 1` and `maxUnavailable: 0`.
   Use `kubectl get pods -w` while updating the image. Verify that available pod
   count never drops below the desired count.

3. **Strategy Comparison**: Create two Deployments with the same app image -- one
   with RollingUpdate strategy and one with Recreate. Update both at the same time.
   Observe the difference in behavior using `kubectl get pods -w` in two terminals.

4. **YAML Generation**: Use `kubectl create deployment --dry-run=client -o yaml` to
   generate a Deployment manifest. Redirect it to a file. Add resource limits,
   a readiness probe, and custom strategy settings. Apply it.

5. **Rollback Investigation**: Create a Deployment and perform 4 image updates.
   Use `kubectl rollout history` to see all revisions. Roll back to revision 2
   specifically. Check which image is now running with `kubectl describe`.

---

## Knowledge Check

**Q1**: What is the relationship between a Deployment, ReplicaSet, and Pod?
<details>
<summary>Answer</summary>
A Deployment manages ReplicaSets, and a ReplicaSet manages Pods. When you create
a Deployment, it creates a ReplicaSet, which in turn creates the Pods. When you
update a Deployment, it creates a new ReplicaSet and scales it up while scaling
the old one down. The old ReplicaSet is kept (with 0 replicas) for rollback.
</details>

**Q2**: What is the difference between RollingUpdate and Recreate strategies?
<details>
<summary>Answer</summary>
RollingUpdate gradually replaces old Pods with new ones, maintaining availability
throughout the process. It is controlled by maxSurge and maxUnavailable. Recreate
kills all old Pods first, then creates new ones, causing a period of downtime. Use
Recreate only when two versions of the app cannot run simultaneously.
</details>

**Q3**: How do you roll back a Deployment to a specific revision?
<details>
<summary>Answer</summary>
`kubectl rollout undo deployment/<name> --to-revision=<number>`. Use
`kubectl rollout history deployment/<name>` first to see available revisions.
Without `--to-revision`, it rolls back to the immediately previous revision.
</details>

**Q4**: What does `maxSurge: 1` and `maxUnavailable: 0` mean?
<details>
<summary>Answer</summary>
maxSurge: 1 means at most 1 extra Pod can exist above the desired replica count
during an update. maxUnavailable: 0 means no Pod can be unavailable during the
update. Combined, this ensures zero-downtime updates: a new Pod must be ready
before an old Pod is terminated.
</details>

**Q5**: Why must `selector.matchLabels` match `template.metadata.labels`?
<details>
<summary>Answer</summary>
The selector tells the Deployment (and its ReplicaSet) which Pods it owns.
The template labels are applied to the Pods when they are created. If these
do not match, the Deployment cannot find its own Pods and will keep creating
new ones indefinitely. Kubernetes validates this at creation time and rejects
mismatches.
</details>
