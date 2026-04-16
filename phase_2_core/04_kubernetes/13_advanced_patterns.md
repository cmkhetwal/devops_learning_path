# Lesson 13: Advanced Patterns -- Init Containers, Sidecars, and Autoscaling

## Why This Matters in DevOps

Production applications rarely consist of a single container doing everything.
Real-world architectures use init containers for setup tasks, sidecars for cross-
cutting concerns (logging, monitoring, proxying), and autoscalers to handle variable
load. These patterns are the building blocks of production-grade Kubernetes
deployments.

As a DevOps engineer, you will implement these patterns to build resilient,
observable, and cost-effective systems. Understanding Pod Disruption Budgets
ensures your applications survive planned maintenance.

The CKA exam tests init containers, resource management for autoscaling, and
Pod Disruption Budgets.

---

## Core Concepts

### Multi-Container Patterns

```
+--- Init Container Pattern ---+
|                              |
| Init containers run BEFORE   |
| the main container starts.   |
| They run to completion,      |
| sequentially.                |
|                              |
| Use for:                     |
| - Wait for dependencies     |
| - Clone a git repo          |
| - Generate config files     |
| - Run database migrations   |
+------------------------------+

+--- Sidecar Pattern ----------+
|                              |
| A helper container runs      |
| alongside the main app.      |
|                              |
| Use for:                     |
| - Log shipping               |
| - Monitoring agent           |
| - TLS proxy (Envoy/istio)   |
| - File sync                  |
+------------------------------+

+--- Ambassador Pattern -------+
|                              |
| A proxy container handles    |
| outbound connections for     |
| the main app.                |
|                              |
| App --> Ambassador --> DB    |
|                              |
| Use for:                     |
| - Connection pooling         |
| - Service mesh proxying      |
| - Multi-environment routing  |
+------------------------------+

+--- Adapter Pattern ----------+
|                              |
| A container transforms the   |
| output of the main app into  |
| a standard format.           |
|                              |
| App --> Adapter --> Monitor  |
|                              |
| Use for:                     |
| - Metrics format conversion  |
| - Log format normalization   |
| - Protocol translation       |
+------------------------------+
```

### Autoscaling Overview

```
+--- Horizontal Pod Autoscaler (HPA) ---+
| Adjusts the NUMBER of Pod replicas    |
| based on CPU, memory, or custom       |
| metrics.                              |
|                                       |
| Low load:  [Pod] [Pod]               |
| High load: [Pod] [Pod] [Pod] [Pod]   |
+---------------------------------------+

+--- Vertical Pod Autoscaler (VPA) -----+
| Adjusts the RESOURCE REQUESTS of     |
| individual Pods.                      |
|                                       |
| Initial: Pod (CPU: 100m, Mem: 128Mi) |
| Adjusted: Pod (CPU: 500m, Mem: 512Mi)|
+---------------------------------------+

HPA and VPA should NOT be used together on the same metric (CPU/memory).
HPA scales OUT (more pods). VPA scales UP (bigger pods).
```

### Pod Disruption Budgets

```
Without PDB:
  Node drain --> ALL 3 pods evicted at once --> DOWNTIME

With PDB (minAvailable: 2):
  Node drain --> Evict 1 pod (2 remain, meets PDB)
             --> Wait for replacement to be Ready
             --> Evict next pod (2 remain, meets PDB)
             --> No downtime
```

---

## Step-by-Step Practical

### 1. Init Containers

```yaml
# Save as /tmp/init-containers.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  # Init container 1: Wait for a service to be available
  - name: wait-for-db
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      echo "Waiting for database service..."
      # In real usage: until nslookup db-service.default.svc; do sleep 2; done
      sleep 3
      echo "Database service is available!"

  # Init container 2: Download configuration
  - name: download-config
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      echo "Downloading configuration..."
      echo '{"db_host": "postgres", "db_port": 5432}' > /config/app.json
      echo "Configuration ready!"
    volumeMounts:
    - name: config-volume
      mountPath: /config

  # Init container 3: Run database migrations
  - name: run-migrations
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      echo "Running database migrations..."
      sleep 2
      echo "CREATE TABLE users (id INT, name TEXT);" > /data/migration.log
      echo "Migrations complete!"
    volumeMounts:
    - name: data-volume
      mountPath: /data

  # Main application container (starts AFTER all init containers complete)
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      echo "App starting with config:"
      cat /config/app.json
      echo ""
      echo "Migration log:"
      cat /data/migration.log
      sleep 3600
    volumeMounts:
    - name: config-volume
      mountPath: /config
      readOnly: true
    - name: data-volume
      mountPath: /data
      readOnly: true

  volumes:
  - name: config-volume
    emptyDir: {}
  - name: data-volume
    emptyDir: {}
```

```bash
kubectl apply -f /tmp/init-containers.yaml

# Watch init containers run sequentially
kubectl get pod init-demo -w
# Init:0/3 -> Init:1/3 -> Init:2/3 -> Running

# Check init container logs
kubectl logs init-demo -c wait-for-db
kubectl logs init-demo -c download-config
kubectl logs init-demo -c run-migrations

# Check main container logs
kubectl logs init-demo -c app

kubectl delete pod init-demo
```

### 2. Sidecar Pattern -- Log Shipping

```yaml
# Save as /tmp/sidecar-logging.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-logging
spec:
  containers:
  # Main application
  - name: app
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      while true; do
        echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"level\":\"INFO\",\"message\":\"Processing request\"}" >> /var/log/app/app.log
        sleep 3
      done
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/app

  # Sidecar: log shipper
  - name: log-shipper
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      echo "Log shipper started. Monitoring /var/log/app/app.log..."
      tail -f /var/log/app/app.log | while read line; do
        echo "[SHIPPED] $line"
      done
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/app
      readOnly: true

  volumes:
  - name: log-volume
    emptyDir: {}
```

```bash
kubectl apply -f /tmp/sidecar-logging.yaml

# View the shipped logs
kubectl logs sidecar-logging -c log-shipper -f
# [SHIPPED] {"timestamp":"...","level":"INFO","message":"Processing request"}

kubectl delete pod sidecar-logging
```

### 3. Adapter Pattern -- Metrics Conversion

```yaml
# Save as /tmp/adapter-pattern.yaml
apiVersion: v1
kind: Pod
metadata:
  name: adapter-demo
  labels:
    app: adapter-demo
spec:
  containers:
  # Main app: writes custom metrics format
  - name: app
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      while true; do
        # App writes metrics in its own format
        echo "requests_total=$(shuf -i 100-500 -n 1)" > /metrics/app-metrics.txt
        echo "errors_total=$(shuf -i 0-10 -n 1)" >> /metrics/app-metrics.txt
        echo "latency_ms=$(shuf -i 10-200 -n 1)" >> /metrics/app-metrics.txt
        sleep 10
      done
    volumeMounts:
    - name: metrics-volume
      mountPath: /metrics

  # Adapter: converts to Prometheus format
  - name: metrics-adapter
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      while true; do
        if [ -f /metrics/app-metrics.txt ]; then
          echo "# Prometheus format output:"
          while IFS='=' read key value; do
            echo "app_${key} ${value}"
          done < /metrics/app-metrics.txt
        fi
        sleep 10
      done
    volumeMounts:
    - name: metrics-volume
      mountPath: /metrics
      readOnly: true

  volumes:
  - name: metrics-volume
    emptyDir: {}
```

```bash
kubectl apply -f /tmp/adapter-pattern.yaml
kubectl logs adapter-demo -c metrics-adapter
# # Prometheus format output:
# app_requests_total 342
# app_errors_total 3
# app_latency_ms 87

kubectl delete pod adapter-demo
```

### 4. Horizontal Pod Autoscaler (HPA)

```bash
# Prerequisite: metrics-server must be installed
minikube addons enable metrics-server
# or: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

```yaml
# Save as /tmp/hpa-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hpa-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hpa-demo
  template:
    metadata:
      labels:
        app: hpa-demo
    spec:
      containers:
      - name: app
        image: registry.k8s.io/hpa-example
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m"        # HPA REQUIRES resource requests
          limits:
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: hpa-demo-svc
spec:
  selector:
    app: hpa-demo
  ports:
  - port: 80
    targetPort: 80
```

```bash
kubectl apply -f /tmp/hpa-deployment.yaml

# Create HPA imperatively
kubectl autoscale deployment hpa-demo \
  --cpu-percent=50 \
  --min=1 \
  --max=10

# Or declaratively
cat <<'EOF' | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hpa-demo
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hpa-demo
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300    # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50                        # Scale down max 50% at once
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0      # Scale up immediately
      policies:
      - type: Pods
        value: 4                         # Add max 4 pods at once
        periodSeconds: 60
EOF

# Check HPA status
kubectl get hpa
# NAME       REFERENCE             TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
# hpa-demo   Deployment/hpa-demo   0%/50%    1         10        1          30s

# Generate load to trigger scaling
kubectl run load-generator --image=busybox:1.36 --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://hpa-demo-svc; done"

# Watch the HPA scale up
kubectl get hpa -w
# CPU% will increase, replicas will increase

# Stop the load
kubectl delete pod load-generator

# Watch it scale back down (after stabilization window)
kubectl get hpa -w
```

### 5. Vertical Pod Autoscaler (VPA) -- concepts

```yaml
# Note: VPA requires the VPA controller to be installed separately
# It is not part of the standard Kubernetes installation
# This is for reference:

# Save as /tmp/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-demo
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"       # Auto, Off, or Initial
    # Auto: VPA evicts pods and recreates with new resources
    # Off: VPA only recommends (does not change pods)
    # Initial: VPA sets resources only on pod creation
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: "100m"
        memory: "50Mi"
      maxAllowed:
        cpu: "2"
        memory: "2Gi"
```

### 6. Pod Disruption Budget (PDB)

```yaml
# Save as /tmp/pdb.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-ha
spec:
  replicas: 5
  selector:
    matchLabels:
      app: web-ha
  template:
    metadata:
      labels:
        app: web-ha
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        resources:
          requests:
            cpu: "50m"
            memory: "32Mi"
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-ha-pdb
spec:
  # Use ONE of the following:
  minAvailable: 3              # At least 3 pods must always be running
  # maxUnavailable: 2          # At most 2 pods can be down at once
  selector:
    matchLabels:
      app: web-ha
```

```bash
kubectl apply -f /tmp/pdb.yaml

# Check PDB status
kubectl get pdb
# NAME         MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
# web-ha-pdb   3               N/A               2                     5s

# ALLOWED DISRUPTIONS = 5 (current) - 3 (minAvailable) = 2

# Test: drain the node (PDB will be respected)
kubectl drain minikube --ignore-daemonsets --delete-emptydir-data --dry-run=client
# dry-run shows what would happen without actually doing it

kubectl describe pdb web-ha-pdb
```

### 7. PDB with maxUnavailable

```yaml
# Save as /tmp/pdb-maxunavailable.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  maxUnavailable: 1            # At most 1 pod can be down
  selector:
    matchLabels:
      app: api
```

```bash
# Percentage-based PDB
cat <<'EOF' | kubectl apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: pct-pdb
spec:
  maxUnavailable: "30%"        # At most 30% of pods can be down
  selector:
    matchLabels:
      app: web-ha
EOF
```

### 8. Native Sidecar Containers (K8s 1.28+)

```yaml
# Save as /tmp/native-sidecar.yaml
# Kubernetes 1.28+ supports native sidecar containers via restartPolicy: Always
apiVersion: v1
kind: Pod
metadata:
  name: native-sidecar-demo
spec:
  initContainers:
  # This is a sidecar, not a traditional init container
  # restartPolicy: Always makes it behave as a sidecar
  - name: log-agent
    image: busybox:1.36
    restartPolicy: Always        # This makes it a sidecar container
    command: ['sh', '-c']
    args:
    - |
      echo "Sidecar log agent started"
      tail -f /var/log/app/app.log 2>/dev/null || sleep infinity
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      while true; do
        echo "$(date) App running" >> /var/log/app/app.log
        sleep 5
      done
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  volumes:
  - name: logs
    emptyDir: {}
```

```bash
kubectl apply -f /tmp/native-sidecar.yaml
kubectl get pod native-sidecar-demo
kubectl logs native-sidecar-demo -c log-agent

kubectl delete pod native-sidecar-demo
```

### 9. HPA with custom metrics (concept)

```yaml
# Custom metrics HPA example (requires custom metrics adapter)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: custom-metrics-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  # Scale based on CPU
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  # Scale based on a custom metric (e.g., queue length)
  - type: Pods
    pods:
      metric:
        name: queue_messages_waiting
      target:
        type: AverageValue
        averageValue: "30"
  # Scale based on an external metric
  - type: External
    external:
      metric:
        name: sqs_queue_depth
        selector:
          matchLabels:
            queue: "orders"
      target:
        type: Value
        value: "100"
```

### 10. Clean up

```bash
kubectl delete deployment hpa-demo web-ha
kubectl delete svc hpa-demo-svc
kubectl delete hpa hpa-demo
kubectl delete pdb web-ha-pdb api-pdb pct-pdb 2>/dev/null
kubectl delete pod load-generator native-sidecar-demo 2>/dev/null
```

---

## Exercises

1. **Init Container Chain**: Create a Pod with 3 init containers: (1) writes a
   config file, (2) reads the config file and writes a modified version, (3) validates
   the final config. The main container reads the final config. Verify each init
   container runs in order.

2. **Sidecar Logging**: Create a Deployment where the main container writes
   structured JSON logs to a shared volume, and a sidecar container reads and
   forwards them. Verify by checking the sidecar logs.

3. **HPA in Action**: Deploy a CPU-intensive application with resource requests.
   Create an HPA targeting 50% CPU utilization. Generate load and observe the
   autoscaler adding replicas. Stop the load and observe scale-down.

4. **Pod Disruption Budget**: Create a Deployment with 4 replicas and a PDB with
   `minAvailable: 3`. Try to drain the node. Verify the PDB limits how many pods
   can be evicted at once. Check `ALLOWED DISRUPTIONS` with `kubectl get pdb`.

5. **Pattern Identification**: For each scenario, identify which pattern (init
   container, sidecar, ambassador, adapter) is most appropriate:
   - Waiting for a database to be ready before starting the app
   - Converting application metrics to Prometheus format
   - Running an Envoy proxy alongside every microservice
   - Downloading ML model files before the inference server starts
   - Proxying database connections through a connection pooler

---

## Knowledge Check

**Q1**: What is the difference between an init container and a sidecar container?
<details>
<summary>Answer</summary>
Init containers run to completion BEFORE the main containers start. They run
sequentially (init-1 finishes, then init-2, etc.). Sidecar containers run
alongside the main container for the entire lifetime of the Pod. Init containers
are for setup tasks (waiting for dependencies, downloading config, running
migrations). Sidecars are for ongoing support tasks (log shipping, monitoring,
proxying).
</details>

**Q2**: What happens if an init container fails?
<details>
<summary>Answer</summary>
The Pod restarts according to its restartPolicy. If restartPolicy is Always or
OnFailure, the init containers are re-run from the beginning (the first init
container runs again, even if it succeeded before). The main container will not
start until all init containers complete successfully. This can lead to
CrashLoopBackOff if the init container keeps failing.
</details>

**Q3**: What resource must be defined on a Deployment for HPA to work with CPU metrics?
<details>
<summary>Answer</summary>
CPU requests. The HPA calculates utilization as a percentage of the requested
CPU. Without a CPU request defined in the container spec, the HPA cannot calculate
utilization and will report `<unknown>` for the target. Memory HPA requires memory
requests. A metrics-server must also be installed.
</details>

**Q4**: What is the difference between `minAvailable` and `maxUnavailable` in a PDB?
<details>
<summary>Answer</summary>
`minAvailable` specifies the minimum number (or percentage) of Pods that must
remain available during a voluntary disruption. `maxUnavailable` specifies the
maximum number (or percentage) of Pods that can be unavailable. They are two ways
of expressing the same constraint. With 5 replicas, `minAvailable: 3` is equivalent
to `maxUnavailable: 2`. You specify one or the other, not both.
</details>

**Q5**: When would you use VPA instead of HPA?
<details>
<summary>Answer</summary>
Use VPA when scaling horizontally (adding more pods) does not help or is not possible
-- for example, a single-replica stateful application that needs more resources, or
when you want to right-size resource requests based on actual usage to reduce waste.
Use HPA when the workload can be parallelized across multiple Pods (web servers,
API servers). Do not use both HPA and VPA on the same CPU/memory metric.
</details>
