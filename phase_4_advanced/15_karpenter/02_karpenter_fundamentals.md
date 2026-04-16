# Karpenter Fundamentals

## Why This Matters in DevOps

Karpenter is the most impactful cost optimization tool you can deploy on EKS. It eliminates the need to manage Auto Scaling Groups, automatically selects the cheapest instance types for your workloads, and consolidates underutilized nodes -- all while provisioning new capacity in under 90 seconds. If you run EKS in production, Karpenter should be your default node provisioner. This lesson covers installation, configuration, and practical usage patterns that you will use daily.

---

## Core Concepts

### Karpenter Architecture

```
┌────────────────────────────────────────────────┐
│                EKS Cluster                     │
│                                                │
│  ┌──────────────────────────────────────────┐  │
│  │         Karpenter Controller              │  │
│  │                                           │  │
│  │  ┌──────────┐  ┌────────────────────┐    │  │
│  │  │ Scheduler│  │ Disruption Engine  │    │  │
│  │  │ Watcher  │  │ (consolidation,    │    │  │
│  │  │          │  │  drift, expiry)    │    │  │
│  │  └──────────┘  └────────────────────┘    │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌────────┐ ┌────────┐ ┌────────┐             │
│  │NodePool│ │NodePool│ │NodePool│  ← Config   │
│  │default │ │gpu     │ │batch   │              │
│  └───┬────┘ └───┬────┘ └───┬────┘             │
│      │          │          │                   │
│  ┌───▼──────────▼──────────▼───┐               │
│  │     EC2NodeClass            │ ← AWS-specific│
│  │ (AMI, subnets, SGs, tags)   │               │
│  └─────────────────────────────┘               │
└────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│    EC2 Fleet    │ ← Directly provisions instances
│    API          │
└─────────────────┘
```

### Key Resources

**NodePool**: Defines the constraints and requirements for nodes that Karpenter can provision. This is where you specify instance types, architectures, capacity types (spot/on-demand), and resource limits.

**EC2NodeClass**: AWS-specific configuration including AMI selection, subnet placement, security groups, instance profiles, block device mappings, and user data. One EC2NodeClass can be shared across multiple NodePools.

**NodeClaim**: Created automatically by Karpenter when it provisions a node. Represents the intent to create a node with specific requirements. You typically do not create these manually.

### Instance Type Selection

Karpenter supports two approaches:

**Flexible (recommended):** Specify constraints, let Karpenter choose

```yaml
requirements:
  - key: karpenter.k8s.aws/instance-category
    operator: In
    values: ["c", "m", "r"]  # Compute, General, Memory
  - key: karpenter.k8s.aws/instance-generation
    operator: Gt
    values: ["4"]  # 5th gen and newer
  - key: karpenter.k8s.aws/instance-size
    operator: In
    values: ["large", "xlarge", "2xlarge"]
```

**Constrained:** Specify exact instance types

```yaml
requirements:
  - key: node.kubernetes.io/instance-type
    operator: In
    values: ["m5.large", "m5.xlarge", "m6i.large", "m6i.xlarge"]
```

### Consolidation

Karpenter's consolidation engine continuously evaluates the cluster and takes action when it finds optimization opportunities:

```
Consolidation Strategies:
─────────────────────────

1. Delete Empty Nodes
   Before: Node A (0 pods) → Delete Node A

2. Replace with Cheaper Node
   Before: m5.2xlarge (using 2 vCPU of 8) → Replace with m5.large (2 vCPU)

3. Merge Underutilized Nodes
   Before: Node A (30% used) + Node B (20% used)
   After:  Node C (50% used) → Delete A and B
```

### Disruption Policies

```yaml
disruption:
  consolidationPolicy: WhenEmptyOrUnderutilized
  consolidateAfter: 30s          # How long to wait before consolidating

  budgets:
    - nodes: "10%"               # Max 10% of nodes disrupted at once
    - nodes: "0"                 # Block all disruption
      schedule: "0 9 * * 1-5"   # During business hours (Mon-Fri 9AM)
      duration: 8h
```

### Spot Instances with Karpenter

Karpenter makes spot instances practical for production:

```yaml
requirements:
  - key: karpenter.sh/capacity-type
    operator: In
    values: ["spot", "on-demand"]  # Prefer spot, fall back to on-demand
```

Karpenter automatically:
- Diversifies across many instance types (reducing interruption risk)
- Handles 2-minute interruption notices
- Provisions replacement capacity before draining
- Falls back to on-demand if no spot capacity available
- Respects Pod Disruption Budgets during interruptions

---

## Step-by-Step Practical

### Setting Up Karpenter on EKS

**Step 1: Prerequisites**

```bash
# Set environment variables
export KARPENTER_NAMESPACE="kube-system"
export KARPENTER_VERSION="1.0.6"
export CLUSTER_NAME="my-cluster"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION="us-east-1"

# Verify EKS cluster exists
aws eks describe-cluster --name $CLUSTER_NAME --query 'cluster.status'
```

**Step 2: Create IAM Roles**

```bash
# Create the Karpenter controller IAM role (using IRSA)
cat <<EOF > karpenter-controller-trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/oidc.eks.${AWS_REGION}.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.${AWS_REGION}.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE:sub": "system:serviceaccount:${KARPENTER_NAMESPACE}:karpenter"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name "KarpenterControllerRole-${CLUSTER_NAME}" \
  --assume-role-policy-document file://karpenter-controller-trust-policy.json

# Create the Karpenter node IAM role
cat <<EOF > karpenter-node-trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name "KarpenterNodeRole-${CLUSTER_NAME}" \
  --assume-role-policy-document file://karpenter-node-trust-policy.json

# Attach required policies to node role
for policy in AmazonEKSWorkerNodePolicy AmazonEKS_CNI_Policy AmazonEC2ContainerRegistryReadOnly AmazonSSMManagedInstanceCore; do
  aws iam attach-role-policy \
    --role-name "KarpenterNodeRole-${CLUSTER_NAME}" \
    --policy-arn "arn:aws:iam::aws:policy/${policy}"
done

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name "KarpenterNodeInstanceProfile-${CLUSTER_NAME}"

aws iam add-role-to-instance-profile \
  --instance-profile-name "KarpenterNodeInstanceProfile-${CLUSTER_NAME}" \
  --role-name "KarpenterNodeRole-${CLUSTER_NAME}"
```

**Step 3: Install Karpenter with Helm**

```bash
# Add Karpenter Helm repo
helm registry logout public.ecr.aws || true

helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter \
  --version "${KARPENTER_VERSION}" \
  --namespace "${KARPENTER_NAMESPACE}" \
  --set "settings.clusterName=${CLUSTER_NAME}" \
  --set "settings.interruptionQueue=${CLUSTER_NAME}" \
  --set controller.resources.requests.cpu=1 \
  --set controller.resources.requests.memory=1Gi \
  --set controller.resources.limits.cpu=1 \
  --set controller.resources.limits.memory=1Gi \
  --wait

# Verify Karpenter is running
kubectl get pods -n kube-system -l app.kubernetes.io/name=karpenter
```

Expected output:
```
NAME                         READY   STATUS    RESTARTS   AGE
karpenter-6b5f7d8c9f-j4k2m  1/1     Running   0          60s
karpenter-6b5f7d8c9f-n8p3q  1/1     Running   0          60s
```

**Step 4: Create EC2NodeClass**

```yaml
# ec2nodeclass.yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  # AMI selection - use latest EKS-optimized AMI
  amiSelectorTerms:
    - alias: al2023@latest  # Amazon Linux 2023

  # Subnet selection - use tagged subnets
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
        kubernetes.io/role/internal-elb: "1"

  # Security group selection
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster

  # IAM role for nodes
  role: "KarpenterNodeRole-my-cluster"

  # Block device configuration
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 100Gi
        volumeType: gp3
        iops: 3000
        throughput: 125
        encrypted: true
        deleteOnTermination: true

  # Tags applied to EC2 instances
  tags:
    ManagedBy: karpenter
    Environment: production
    Team: platform

  # Metadata options (IMDSv2 required for security)
  metadataOptions:
    httpEndpoint: enabled
    httpProtocolIPv6: disabled
    httpPutResponseHopLimit: 2
    httpTokens: required  # Enforce IMDSv2
```

```bash
kubectl apply -f ec2nodeclass.yaml
```

**Step 5: Create NodePool**

```yaml
# nodepool-default.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    metadata:
      labels:
        managed-by: karpenter
        workload-type: general
    spec:
      requirements:
        # Architecture: support both AMD64 and ARM64
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]

        # Capacity type: prefer spot, allow on-demand
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]

        # Instance categories: general, compute, memory
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]

        # Instance generation: 5th gen and newer
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["4"]

        # Instance sizes
        - key: karpenter.k8s.aws/instance-size
          operator: In
          values: ["medium", "large", "xlarge", "2xlarge"]

      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default

      # Expire nodes after 720h (30 days) to force updates
      expireAfter: 720h

  # Resource limits (prevent runaway scaling)
  limits:
    cpu: "200"
    memory: 800Gi

  # Disruption policy
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m

    # Disruption budgets
    budgets:
      - nodes: "10%"
      # No disruption during business hours on weekdays
      - nodes: "0"
        schedule: "0 9 * * 1-5"
        duration: 10h

  # Weight for priority (higher = preferred)
  weight: 50
```

```bash
kubectl apply -f nodepool-default.yaml

# Verify
kubectl get nodepool
kubectl get ec2nodeclass
```

Expected output:
```
NAME      NODECLASS   NODES   READY   AGE
default   default     0       True    10s

NAME      READY   AGE
default   True    30s
```

**Step 6: Test Scaling**

```bash
# Deploy a workload that triggers node provisioning
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scaling-test
spec:
  replicas: 20
  selector:
    matchLabels:
      app: scaling-test
  template:
    metadata:
      labels:
        app: scaling-test
    spec:
      containers:
        - name: pause
          image: registry.k8s.io/pause:3.9
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
      terminationGracePeriodSeconds: 0
EOF

# Watch Karpenter provision nodes
kubectl logs -n kube-system -l app.kubernetes.io/name=karpenter -f --tail=50
```

Expected log output:
```
INFO    controller.provisioner  found provisionable pod(s)  {"commit": "abc123", "pods": 20}
INFO    controller.provisioner  computed new nodeclaim(s) to fit pod(s)  {"nodeclaims": 3, "pods": 20}
INFO    controller.provisioner  created nodeclaim  {"nodepool": "default", "nodeclaim": "default-xyz1", "instance-types": "m6i.xlarge, m5.xlarge, c6i.xlarge, ..."}
INFO    controller.provisioner  created nodeclaim  {"nodepool": "default", "nodeclaim": "default-xyz2", "instance-types": "m6g.xlarge, m6gd.xlarge, ..."}
INFO    controller.nodeclaim    launched nodeclaim  {"nodeclaim": "default-xyz1", "provider-id": "aws:///us-east-1a/i-0abc123", "instance-type": "m6i.xlarge", "capacity-type": "spot", "zone": "us-east-1a"}
```

```bash
# Check provisioned nodes
kubectl get nodes -l managed-by=karpenter

# Check node details
kubectl get nodes -l managed-by=karpenter -o custom-columns=\
NAME:.metadata.name,\
TYPE:.metadata.labels.node\\.kubernetes\\.io/instance-type,\
CAPACITY:.metadata.labels.karpenter\\.sh/capacity-type,\
ARCH:.metadata.labels.kubernetes\\.io/arch,\
ZONE:.metadata.labels.topology\\.kubernetes\\.io/zone
```

Expected output:
```
NAME                           TYPE          CAPACITY   ARCH    ZONE
ip-10-0-1-123.ec2.internal    m6i.xlarge    spot       amd64   us-east-1a
ip-10-0-2-456.ec2.internal    m6g.xlarge    spot       arm64   us-east-1b
ip-10-0-1-789.ec2.internal    c6i.xlarge    spot       amd64   us-east-1a
```

**Step 7: Test Consolidation**

```bash
# Scale down to trigger consolidation
kubectl scale deployment scaling-test --replicas=5

# Watch Karpenter consolidate nodes (wait 1-2 minutes)
kubectl logs -n kube-system -l app.kubernetes.io/name=karpenter -f --tail=20
```

Expected log output:
```
INFO    controller.disruption   disrupting via consolidation delete  {"nodeclaim": "default-xyz2", "node": "ip-10-0-2-456.ec2.internal", "reason": "underutilized"}
INFO    controller.disruption   initiating delete  {"node": "ip-10-0-2-456.ec2.internal", "nodeclaim": "default-xyz2"}
```

---

## Exercises

1. **Installation**: Install Karpenter on an EKS cluster (or simulate with a Kind cluster and the Karpenter controller in dry-run mode). Create a NodePool and EC2NodeClass. Deploy 50 pods and observe Karpenter's provisioning decisions.

2. **Instance Diversity**: Configure a NodePool that allows 20+ instance types across 3 generations and 2 architectures. Deploy workloads and verify that Karpenter selects different instance types based on pod requirements.

3. **Consolidation Testing**: Deploy 100 pods across many nodes, then scale down to 10 pods. Measure how long Karpenter takes to consolidate and how much cost it saves by replacing large nodes with smaller ones.

4. **Disruption Budgets**: Configure a disruption budget that prevents any node disruption during business hours (9 AM - 5 PM, Monday-Friday). Verify that consolidation only happens outside these hours.

---

## Knowledge Check

**Q1: What is the difference between a NodePool and an EC2NodeClass?**

<details>
<summary>Answer</summary>

A NodePool defines the scheduling constraints and disruption policies -- what types of instances are allowed (architecture, capacity type, instance categories), resource limits, consolidation policies, and node expiry. It is cloud-agnostic in its API. An EC2NodeClass defines AWS-specific configuration -- which AMI to use, which subnets and security groups, IAM roles, EBS volume configuration, and instance metadata options. One EC2NodeClass can be shared across multiple NodePools, and one NodePool references exactly one EC2NodeClass.
</details>

**Q2: How does Karpenter decide which instance type to launch?**

<details>
<summary>Answer</summary>

Karpenter: (1) Collects all pending pods that cannot be scheduled, (2) Evaluates their resource requests (CPU, memory, GPU), node selectors, tolerations, topology spread constraints, and affinity rules, (3) Filters the EC2 instance catalog to find types that match the NodePool's requirements, (4) Uses a bin-packing algorithm to find the optimal set of instances that fit all pending pods at the lowest cost, (5) Prioritizes spot instances if allowed, with automatic fallback to on-demand. The key insight is that Karpenter considers all pending pods together and makes a globally optimal decision rather than scaling one node at a time.
</details>

**Q3: What does `consolidationPolicy: WhenEmptyOrUnderutilized` do?**

<details>
<summary>Answer</summary>

This policy enables two consolidation behaviors: (1) `WhenEmpty` -- if a node has no pods running (after evictions, scaling down, etc.), Karpenter deletes it immediately after the `consolidateAfter` duration. (2) `WhenUnderutilized` -- if a node's pods could fit on other existing nodes, or if the node could be replaced with a cheaper instance type, Karpenter will consolidate. It cordons the node, drains pods respecting PDBs, and terminates the instance. The alternative policy `WhenEmpty` only deletes truly empty nodes, which is more conservative but leaves underutilized nodes running.
</details>

**Q4: How does the `expireAfter` setting work and why would you use it?**

<details>
<summary>Answer</summary>

`expireAfter` sets a maximum lifetime for nodes. When a node reaches this age, Karpenter drains and replaces it (respecting disruption budgets and PDBs). Common values: 720h (30 days) or 168h (7 days). Reasons to use it: (1) Security -- ensure nodes get the latest OS patches and AMIs regularly, (2) Drift prevention -- replace nodes with potentially stale configurations, (3) Node health -- prevent issues from long-running nodes (memory leaks in system components, disk fragmentation), (4) Compliance -- some security frameworks require regular node rotation.
</details>
