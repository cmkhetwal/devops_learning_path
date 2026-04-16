# Karpenter Advanced

## Why This Matters in DevOps

Production Kubernetes clusters have diverse workloads: machine learning models needing GPUs, cost-sensitive batch jobs on ARM64, latency-critical services requiring on-demand instances, and everything in between. Advanced Karpenter configuration lets you handle all of these with a single tool while maximizing cost efficiency. This lesson covers multi-architecture support, GPU workloads, drift detection, monitoring, and the mixed spot/on-demand strategies that production clusters require.

---

## Core Concepts

### Multi-Architecture Support (AMD64 + ARM64)

ARM64 (Graviton) instances on AWS are 20-40% cheaper than equivalent AMD64 instances for the same performance. Karpenter makes multi-architecture clusters practical by automatically selecting the cheapest architecture that satisfies pod requirements.

```
Price Comparison (us-east-1, on-demand):
─────────────────────────────────────────
Instance      Arch    vCPU   RAM     $/hr
m5.xlarge     amd64   4      16GB    $0.192
m6g.xlarge    arm64   4      16GB    $0.154  ← 20% cheaper
m7g.xlarge    arm64   4      16GB    $0.163  ← 15% cheaper

c5.2xlarge    amd64   8      16GB    $0.340
c6g.2xlarge   arm64   8      16GB    $0.272  ← 20% cheaper
c7g.2xlarge   arm64   8      16GB    $0.290  ← 15% cheaper
```

To enable multi-architecture, your container images must support both architectures:

```dockerfile
# Build multi-arch images
# Dockerfile
FROM --platform=$TARGETPLATFORM python:3.12-slim
COPY app.py /app/
CMD ["python", "/app/app.py"]
```

```bash
# Build and push multi-arch image
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag mycompany/myapp:v1.0.0 \
  --push .
```

### GPU Workloads

Karpenter can provision GPU instances on-demand for ML/AI workloads:

```yaml
# nodepool-gpu.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: gpu
spec:
  template:
    metadata:
      labels:
        workload-type: gpu
    spec:
      requirements:
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["g", "p"]  # GPU instance families
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["4"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: gpu
      taints:
        - key: nvidia.com/gpu
          value: "true"
          effect: NoSchedule
  limits:
    cpu: "96"
    nvidia.com/gpu: "8"
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 5m
```

```yaml
# ec2nodeclass-gpu.yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: gpu
spec:
  amiSelectorTerms:
    - alias: al2023@latest
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
  role: "KarpenterNodeRole-my-cluster"
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 200Gi  # Larger for ML models
        volumeType: gp3
        iops: 6000
        throughput: 250
        encrypted: true
```

Deploying a GPU workload:

```yaml
# ml-training-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
spec:
  template:
    spec:
      nodeSelector:
        workload-type: gpu
      tolerations:
        - key: nvidia.com/gpu
          operator: Equal
          value: "true"
          effect: NoSchedule
      containers:
        - name: trainer
          image: mycompany/ml-trainer:v2.0
          resources:
            requests:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
            limits:
              nvidia.com/gpu: "1"
      restartPolicy: Never
```

### Custom AMIs

For organizations requiring hardened or custom AMIs:

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: custom-ami
spec:
  amiSelectorTerms:
    # Use a specific AMI ID
    - id: ami-0abc123def456789
    # Or use tags to find AMIs
    - tags:
        Name: "eks-hardened-*"
        Environment: production
  # When using custom AMIs, you may need custom userData
  userData: |
    #!/bin/bash
    # Custom bootstrap script
    /etc/eks/bootstrap.sh my-cluster \
      --container-runtime containerd \
      --kubelet-extra-args '--node-labels=custom-ami=true'
```

### Drift Detection and Remediation

Karpenter automatically detects when nodes have drifted from their desired configuration and replaces them:

```
Drift Types:
─────────────
1. AMI Drift    → New AMI available, node running old one
2. Subnet Drift → Subnet list changed in EC2NodeClass
3. SG Drift     → Security groups changed in EC2NodeClass
4. NodePool Drift → Requirements changed in NodePool
```

```bash
# Check for drifted nodes
kubectl get nodeclaims -o custom-columns=\
NAME:.metadata.name,\
NODE:.status.nodeName,\
READY:.status.conditions[?(@.type==\"Ready\")].status,\
DRIFTED:.status.conditions[?(@.type==\"Drifted\")].status
```

Expected output:
```
NAME              NODE                            READY   DRIFTED
default-abc123    ip-10-0-1-50.ec2.internal      True    True
default-def456    ip-10-0-2-100.ec2.internal     True    False
```

### Karpenter Metrics and Monitoring

Karpenter exposes Prometheus metrics for comprehensive monitoring:

```yaml
# prometheus-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: karpenter
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: karpenter
  endpoints:
    - port: http-metrics
      interval: 30s
```

Key metrics to monitor:

```
# Node provisioning
karpenter_nodeclaims_created_total         # Total nodes provisioned
karpenter_nodeclaims_terminated_total      # Total nodes terminated
karpenter_nodeclaims_launched_total        # Nodes launched by instance type
karpenter_nodeclaims_disrupted_total       # Nodes disrupted (consolidation, drift, expiry)

# Scheduling
karpenter_pods_startup_duration_seconds    # Time from pod creation to running
karpenter_provisioner_scheduling_duration_seconds  # Time to make scheduling decision

# Consolidation
karpenter_disruption_consolidation_evaluation_duration_seconds
karpenter_disruption_actions_performed_total{action="delete|replace"}

# Costs (approximate)
karpenter_nodeclaims_instance_type_price_estimate  # Estimated hourly cost per node
```

**Grafana Dashboard Queries:**

```promql
# Total cluster cost per hour (approximate)
sum(karpenter_nodeclaims_instance_type_price_estimate)

# Nodes by capacity type
count(karpenter_nodeclaims_launched_total) by (capacity_type)

# Average pod startup latency
histogram_quantile(0.99, rate(karpenter_pods_startup_duration_seconds_bucket[5m]))

# Consolidation actions in last hour
increase(karpenter_disruption_actions_performed_total[1h])
```

### Cost Optimization Strategies

**Strategy 1: Maximize Spot Usage**

```yaml
# nodepool-spot-preferred.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: spot-preferred
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        # Wide instance diversity reduces spot interruption risk
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r", "c", "i"]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["4"]
        - key: karpenter.k8s.aws/instance-size
          operator: In
          values: ["large", "xlarge", "2xlarge", "4xlarge"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  # Karpenter will prefer spot (cheapest) when both are available
  weight: 100  # Higher weight = preferred
```

**Strategy 2: Dedicated On-Demand for Critical Workloads**

```yaml
# nodepool-critical.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: critical
spec:
  template:
    metadata:
      labels:
        workload-type: critical
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]  # Never spot for critical workloads
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["m", "r"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      taints:
        - key: workload-type
          value: critical
          effect: NoSchedule
  disruption:
    consolidationPolicy: WhenEmpty  # Conservative consolidation
    consolidateAfter: 10m
  weight: 10  # Lower weight = less preferred (use only when needed)
```

---

## Step-by-Step Practical

### Configure Karpenter for Mixed Spot/On-Demand with Fallback

**Step 1: Create Multiple NodePools with Priority**

```yaml
# nodepool-spot-general.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: spot-general
spec:
  template:
    metadata:
      labels:
        capacity: spot
        tier: general
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["4"]
        - key: karpenter.k8s.aws/instance-size
          operator: In
          values: ["medium", "large", "xlarge", "2xlarge"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      expireAfter: 336h  # 14 days (spot nodes rotate faster)
  limits:
    cpu: "200"
    memory: 800Gi
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
  weight: 100  # Highest priority - try spot first
---
# nodepool-ondemand-fallback.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: ondemand-fallback
spec:
  template:
    metadata:
      labels:
        capacity: on-demand
        tier: fallback
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["4"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      expireAfter: 720h  # 30 days
  limits:
    cpu: "100"
    memory: 400Gi
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 2m
  weight: 10  # Lower priority - used when spot unavailable
---
# nodepool-critical-ondemand.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: critical-ondemand
spec:
  template:
    metadata:
      labels:
        capacity: on-demand
        tier: critical
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["m", "r"]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["5"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      taints:
        - key: tier
          value: critical
          effect: NoSchedule
      expireAfter: 720h
  limits:
    cpu: "50"
    memory: 200Gi
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 10m
    budgets:
      - nodes: "1"  # Only disrupt 1 node at a time
  weight: 5
```

```bash
kubectl apply -f nodepool-spot-general.yaml
kubectl apply -f nodepool-ondemand-fallback.yaml
kubectl apply -f nodepool-critical-ondemand.yaml
```

**Step 2: Deploy Workloads with Proper Scheduling**

```yaml
# Stateless workload - can run on spot
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 6
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api-server
      containers:
        - name: api
          image: mycompany/api:v3.0
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
---
# Critical workload - needs on-demand
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-processor
  template:
    metadata:
      labels:
        app: payment-processor
    spec:
      nodeSelector:
        tier: critical
      tolerations:
        - key: tier
          value: critical
          effect: NoSchedule
      containers:
        - name: payment
          image: mycompany/payment:v2.0
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
```

**Step 3: Monitor the Result**

```bash
# View all nodes by NodePool
kubectl get nodes -L karpenter.sh/nodepool,karpenter.sh/capacity-type,node.kubernetes.io/instance-type

# View cost breakdown
kubectl get nodeclaims -o custom-columns=\
NODEPOOL:.metadata.labels.karpenter\\.sh/nodepool,\
INSTANCE:.metadata.labels.node\\.kubernetes\\.io/instance-type,\
CAPACITY:.metadata.labels.karpenter\\.sh/capacity-type,\
ARCH:.metadata.labels.kubernetes\\.io/arch,\
ZONE:.metadata.labels.topology\\.kubernetes\\.io/zone,\
AGE:.metadata.creationTimestamp
```

Expected output:
```
NODEPOOL            INSTANCE       CAPACITY    ARCH    ZONE           AGE
spot-general        m6g.xlarge     spot        arm64   us-east-1a     2024-01-15T10:30:00Z
spot-general        c6i.xlarge     spot        amd64   us-east-1b     2024-01-15T10:30:00Z
spot-general        m6g.large      spot        arm64   us-east-1a     2024-01-15T10:31:00Z
critical-ondemand   r6g.large      on-demand   arm64   us-east-1b     2024-01-15T10:32:00Z
```

---

## Exercises

1. **Multi-Architecture Migration**: Take an existing AMD64-only application, build multi-arch container images, and deploy with a Karpenter NodePool that allows both AMD64 and ARM64. Measure the cost difference between architectures.

2. **GPU Job Scheduling**: Create a NodePool for GPU workloads with taints. Deploy a batch job that requests a GPU, verify Karpenter provisions a GPU instance, and verify the node is removed after the job completes.

3. **Monitoring Dashboard**: Set up Prometheus + Grafana and create a dashboard showing: nodes by capacity type, estimated hourly cost, consolidation actions, pod startup latency, and instance type distribution.

4. **Chaos Testing**: Configure Karpenter with spot instances, then simulate a spot interruption (terminate an instance). Measure how quickly Karpenter provisions a replacement and whether pods experience downtime.

5. **Cost Report**: Run a production-like workload for 24 hours with Karpenter (spot + on-demand, consolidation enabled). Compare the actual cost against what it would have been with fixed-size node groups. Document the savings.

---

## Knowledge Check

**Q1: How does Karpenter handle multi-architecture (AMD64 + ARM64) workloads?**

<details>
<summary>Answer</summary>

When a NodePool allows both architectures (`kubernetes.io/arch In [amd64, arm64]`), Karpenter includes both AMD64 and ARM64 instance types in its optimization. It will select the cheapest option that satisfies all pod requirements. Since ARM64 (Graviton) instances are typically 20-40% cheaper, Karpenter naturally gravitates toward them. The prerequisite is that container images must be built for both architectures (multi-arch images using `docker buildx`). If a pod has a node selector specifying `kubernetes.io/arch: amd64`, Karpenter will only consider AMD64 instances for that pod.
</details>

**Q2: What is drift detection and how does Karpenter handle it?**

<details>
<summary>Answer</summary>

Drift detection identifies when a running node no longer matches the desired configuration defined in its NodePool or EC2NodeClass. Examples: the EC2NodeClass AMI selector resolves to a new AMI, security groups were updated, subnet list changed, or NodePool requirements were modified. When drift is detected, Karpenter marks the NodeClaim as "Drifted" and schedules it for replacement. It cordons the node, drains pods (respecting PDBs and disruption budgets), launches a replacement with the correct configuration, and then terminates the old node. This provides automatic, rolling updates for node configuration changes.
</details>

**Q3: How should you configure Karpenter for a mix of spot and on-demand workloads?**

<details>
<summary>Answer</summary>

Create multiple NodePools with different weights and configurations: (1) A high-weight (e.g., 100) spot NodePool for general workloads -- allows many instance types for diversity, aggressive consolidation. (2) A lower-weight (e.g., 10) on-demand fallback NodePool for when spot capacity is unavailable. (3) A critical on-demand NodePool with taints for workloads that cannot tolerate interruption (payment processing, databases). Critical workloads use nodeSelectors and tolerations to target the critical NodePool. Stateless workloads naturally land on the spot pool (highest weight). If spot is unavailable, Karpenter falls back to on-demand.
</details>

**Q4: What Karpenter metrics should you monitor and why?**

<details>
<summary>Answer</summary>

Key metrics: (1) `karpenter_pods_startup_duration_seconds` -- measures how quickly pods go from pending to running; if this increases, Karpenter may be struggling to find capacity. (2) `karpenter_nodeclaims_disrupted_total` by reason -- tracks consolidation, drift, expiry, and emptiness events; high disruption may indicate unstable scheduling. (3) `karpenter_nodeclaims_instance_type_price_estimate` -- approximate hourly cost per node; sum this for total cluster cost. (4) `karpenter_disruption_actions_performed_total` -- tracks consolidation replacements and deletions; healthy clusters show regular consolidation. (5) Node count by capacity type -- monitors spot vs on-demand ratio; sudden shift to on-demand may indicate spot capacity issues.
</details>
