# Lesson 05: Workloads -- StatefulSets, DaemonSets, Jobs, and CronJobs

## Why This Matters in DevOps

Not every workload is a stateless web server. Databases need stable identities.
Log collectors need to run on every node. Backup scripts need to run on a schedule.
Kubernetes provides specialized workload controllers for each of these patterns.
Choosing the wrong controller leads to data loss, missed logs, or unreliable batch
processing.

The CKA exam tests your ability to create and manage all four workload types.
Understanding when to use each one is as important as knowing the YAML.

---

## Core Concepts

### When to Use Each Workload Type

```
+--------------------+-----------------------------------+------------------+
| Workload Type      | Use When                          | Example          |
+--------------------+-----------------------------------+------------------+
| Deployment         | Stateless, interchangeable Pods   | Web servers, APIs|
| StatefulSet        | Ordered startup, stable identity  | Databases, Kafka |
| DaemonSet          | One Pod per node, always          | Log agents, CNI  |
| Job                | Run to completion, then stop      | Data migration   |
| CronJob            | Run on a schedule                 | Backups, reports |
+--------------------+-----------------------------------+------------------+
```

### StatefulSets: Stable Identity

```
Deployment Pods (interchangeable):
  nginx-deploy-abc123-xxxxx  (random name, any order, shared storage)
  nginx-deploy-abc123-yyyyy
  nginx-deploy-abc123-zzzzz

StatefulSet Pods (stable identity):
  postgres-0  (always first, gets pvc-postgres-0)
  postgres-1  (starts after 0 is ready, gets pvc-postgres-1)
  postgres-2  (starts after 1 is ready, gets pvc-postgres-2)

  Scale down: postgres-2 removed first, then 1, then 0 (reverse order)
  Scale up:   postgres-0 starts first, then 1, then 2 (forward order)
```

StatefulSet guarantees:
- **Stable network identity**: `pod-name.service-name.namespace.svc.cluster.local`
- **Ordered deployment and scaling**: Pods created/deleted in order
- **Stable persistent storage**: Each Pod gets its own PVC that survives rescheduling
- **Ordinal index**: Pods are named `<statefulset-name>-0`, `-1`, `-2`, etc.

### DaemonSets: One Per Node

```
+--- Node 1 ---+  +--- Node 2 ---+  +--- Node 3 ---+
| +----------+ |  | +----------+ |  | +----------+ |
| | fluentd  | |  | | fluentd  | |  | | fluentd  | |
| | (DaemonS)| |  | | (DaemonS)| |  | | (DaemonS)| |
| +----------+ |  | +----------+ |  | +----------+ |
+---------------+  +---------------+  +---------------+

New Node 4 added to cluster:
+--- Node 4 ---+
| +----------+ |
| | fluentd  | |  <-- Automatically scheduled
| | (DaemonS)| |
| +----------+ |
+---------------+
```

Common DaemonSet workloads:
- **Log collectors**: fluentd, filebeat, promtail
- **Monitoring agents**: node-exporter, datadog-agent
- **Network plugins**: calico-node, kube-proxy
- **Storage daemons**: glusterd, ceph

### Jobs and CronJobs: Batch Processing

```
Job: Run a task to completion
  +--- Job (db-migrate) -----+
  |                          |
  | Pod: db-migrate-xxxxx    |
  |   Status: Completed      |
  |   Exit code: 0           |
  |                          |
  | completions: 1           |
  | parallelism: 1           |
  | backoffLimit: 4          |
  +---------------------------+

CronJob: Create Jobs on a schedule
  +--- CronJob (nightly-backup) ---+
  |                                |
  | schedule: "0 2 * * *"          |  <-- 2:00 AM every day
  | concurrencyPolicy: Forbid      |
  |                                |
  | Creates a Job at each trigger: |
  |   nightly-backup-28345600      |
  |   nightly-backup-28345601      |
  +--------------------------------+
```

---

## Step-by-Step Practical

### 1. StatefulSet with a headless service

A StatefulSet requires a headless Service (ClusterIP: None) for stable DNS.

```yaml
# Save as /tmp/statefulset.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
  labels:
    app: postgres
spec:
  ports:
  - port: 5432
    name: postgres
  clusterIP: None          # Headless service
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: "postgres-headless"   # Must match the headless Service
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          value: "mysecretpassword"    # Use Secrets in production!
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

```bash
kubectl apply -f /tmp/statefulset.yaml

# Watch pods come up IN ORDER (0, then 1, then 2)
kubectl get pods -w -l app=postgres

# Each pod has a stable DNS name
# postgres-0.postgres-headless.default.svc.cluster.local
# postgres-1.postgres-headless.default.svc.cluster.local
# postgres-2.postgres-headless.default.svc.cluster.local

# Check the PVCs -- each pod gets its own
kubectl get pvc

# Scale down -- pods removed in REVERSE order (2, then 1, then 0)
kubectl scale statefulset postgres --replicas=1

# PVCs are preserved (data is not lost)
kubectl get pvc

# Scale back up -- pods recreated with the SAME PVC
kubectl scale statefulset postgres --replicas=3
```

### 2. DaemonSet for log collection

```yaml
# Save as /tmp/daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-collector
  labels:
    app: log-collector
spec:
  selector:
    matchLabels:
      app: log-collector
  template:
    metadata:
      labels:
        app: log-collector
    spec:
      containers:
      - name: log-collector
        image: busybox:1.36
        command: ['sh', '-c']
        args:
        - |
          while true; do
            echo "$(date) Collecting logs from $(hostname)"
            sleep 30
          done
        resources:
          requests:
            cpu: "50m"
            memory: "32Mi"
          limits:
            cpu: "100m"
            memory: "64Mi"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      tolerations:
      # Allow scheduling on control plane nodes too
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
```

```bash
kubectl apply -f /tmp/daemonset.yaml

# Check -- one pod per node
kubectl get pods -l app=log-collector -o wide
# Notice each pod runs on a different node

# See the DaemonSet status
kubectl get daemonset log-collector
# DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE
# 1         1         1       1            1          (for a single-node cluster)

# View logs
kubectl logs -l app=log-collector

# DaemonSet updates -- uses RollingUpdate by default
kubectl set image daemonset/log-collector log-collector=busybox:1.36.1
kubectl rollout status daemonset/log-collector
```

### 3. Job: one-time task

```yaml
# Save as /tmp/job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  completions: 1           # How many successful completions needed
  parallelism: 1           # How many pods run at once
  backoffLimit: 4           # Retry up to 4 times on failure
  activeDeadlineSeconds: 60 # Fail after 60 seconds total
  template:
    spec:
      containers:
      - name: migrate
        image: busybox:1.36
        command: ['sh', '-c']
        args:
        - |
          echo "Starting database migration..."
          echo "Applying schema changes..."
          sleep 5
          echo "Migration completed successfully!"
      restartPolicy: Never   # Jobs require Never or OnFailure
```

```bash
kubectl apply -f /tmp/job.yaml

# Watch the job
kubectl get jobs -w
kubectl get pods -l job-name=db-migration

# Wait for completion
kubectl wait --for=condition=complete job/db-migration --timeout=120s

# View the output
kubectl logs job/db-migration

# Check job status
kubectl describe job db-migration
```

### 4. Job with parallelism

```yaml
# Save as /tmp/parallel-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-processor
spec:
  completions: 5     # Need 5 successful completions
  parallelism: 2     # Run 2 pods at a time
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: worker
        image: busybox:1.36
        command: ['sh', '-c']
        args:
        - |
          echo "Processing task on $(hostname)..."
          sleep $(shuf -i 3-8 -n 1)  # Random sleep 3-8 seconds
          echo "Task completed!"
      restartPolicy: Never
```

```bash
kubectl apply -f /tmp/parallel-job.yaml

# Watch -- 2 pods run at a time until all 5 complete
kubectl get pods -l job-name=parallel-processor -w

kubectl get job parallel-processor
# COMPLETIONS   DURATION
# 5/5           25s
```

### 5. CronJob: scheduled tasks

```yaml
# Save as /tmp/cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "*/5 * * * *"          # Every 5 minutes (for testing)
  # schedule: "0 2 * * *"          # 2:00 AM daily (production)
  concurrencyPolicy: Forbid        # Don't start new if previous still running
  successfulJobsHistoryLimit: 3    # Keep last 3 successful job records
  failedJobsHistoryLimit: 1        # Keep last 1 failed job record
  startingDeadlineSeconds: 60      # If missed by 60s, skip this run
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: busybox:1.36
            command: ['sh', '-c']
            args:
            - |
              echo "$(date) Starting backup..."
              echo "Backing up database..."
              sleep 3
              echo "$(date) Backup completed!"
          restartPolicy: OnFailure
```

```bash
kubectl apply -f /tmp/cronjob.yaml

# Check the CronJob
kubectl get cronjobs
kubectl get cj   # shorthand

# Wait for a run (up to 5 minutes)
kubectl get jobs -w

# View completed job logs
kubectl get pods -l job-name=$(kubectl get jobs -o jsonpath='{.items[0].metadata.name}')
kubectl logs $(kubectl get pods -l job-name -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

# Trigger a job manually (don't wait for schedule)
kubectl create job --from=cronjob/nightly-backup manual-backup-001

# Suspend a CronJob (prevent new runs)
kubectl patch cronjob nightly-backup -p '{"spec":{"suspend":true}}'

# Resume
kubectl patch cronjob nightly-backup -p '{"spec":{"suspend":false}}'
```

### 6. CronJob schedule syntax

```
# Cron schedule format
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6, Sunday = 0)
# │ │ │ │ │
# * * * * *

# Examples:
# "0 2 * * *"       Every day at 2:00 AM
# "*/15 * * * *"    Every 15 minutes
# "0 0 * * 0"       Every Sunday at midnight
# "0 9 1 * *"       First of every month at 9:00 AM
# "30 6 * * 1-5"    Weekdays at 6:30 AM
```

### 7. Clean up

```bash
kubectl delete statefulset postgres
kubectl delete service postgres-headless
kubectl delete pvc -l app=postgres
kubectl delete daemonset log-collector
kubectl delete job db-migration parallel-processor
kubectl delete cronjob nightly-backup
kubectl delete job manual-backup-001
```

---

## Exercises

1. **StatefulSet Ordering**: Create a StatefulSet with 3 replicas. Watch the pods
   come up one by one. Scale down to 1 and observe the reverse ordering. Scale
   back to 3 and verify PVCs are reused.

2. **DaemonSet Scope**: Create a DaemonSet. Use nodeSelector to limit it to nodes
   with a specific label. Add the label to your node and watch the pod appear.
   Remove the label and watch the pod disappear.

3. **Job Failure Handling**: Create a Job that intentionally fails (e.g., `exit 1`).
   Set `backoffLimit: 3` and `restartPolicy: Never`. Watch the retry behavior and
   see that 3 failed pods are created before the Job is marked as Failed.

4. **CronJob Control**: Create a CronJob that runs every 2 minutes. Watch it create
   Jobs. Suspend it, wait, and verify no new Jobs are created. Resume it and verify
   it starts running again.

5. **Workload Selection**: For each scenario, choose the correct workload type and
   explain why:
   - A Redis cache cluster with 3 nodes
   - A Node.js API that handles HTTP requests
   - Sending a weekly email report
   - Installing a monitoring agent on every server
   - Processing a one-time data import of 10 million records

---

## Knowledge Check

**Q1**: What makes a StatefulSet different from a Deployment?
<details>
<summary>Answer</summary>
StatefulSets provide: (1) stable, unique network identifiers (pod-0, pod-1, etc.),
(2) stable persistent storage (each Pod gets its own PVC), (3) ordered deployment
and scaling (pods are created sequentially and deleted in reverse order), and
(4) ordered rolling updates. Deployments treat all Pods as interchangeable.
</details>

**Q2**: What does `concurrencyPolicy: Forbid` mean on a CronJob?
<details>
<summary>Answer</summary>
It means Kubernetes will not start a new Job if the previous Job is still running.
The scheduled run is skipped. Other options are `Allow` (run concurrently, which
is the default) and `Replace` (stop the running Job and start a new one).
</details>

**Q3**: Why does a StatefulSet require a headless Service?
<details>
<summary>Answer</summary>
A headless Service (ClusterIP: None) creates individual DNS records for each Pod
instead of a single virtual IP. This allows StatefulSet Pods to be addressed by
stable DNS names like `pod-0.service-name.namespace.svc.cluster.local`. Without
this, individual Pods cannot be addressed by name, which defeats the purpose of
stable identity.
</details>

**Q4**: What is the difference between `restartPolicy: Never` and `OnFailure` for Jobs?
<details>
<summary>Answer</summary>
With `Never`, if the container fails, a new Pod is created (up to backoffLimit).
Failed pods are kept for log inspection. With `OnFailure`, the same Pod is restarted
(the container restarts within the same Pod). `Never` is useful for debugging (you
can see logs of each failed attempt). `OnFailure` uses fewer Pod resources.
</details>

**Q5**: What happens to DaemonSet Pods when a new node is added to the cluster?
<details>
<summary>Answer</summary>
The DaemonSet controller automatically schedules a Pod on the new node. This is
one of the key features of DaemonSets -- they ensure coverage across all nodes
(or a subset of nodes if nodeSelector or tolerations are configured). When a node
is removed, the Pod on that node is also removed.
</details>
