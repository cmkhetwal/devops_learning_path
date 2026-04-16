# Cloud Cost Tools

## Why This Matters in DevOps

You cannot optimize what you cannot measure. Cloud cost visibility tools transform abstract billing data into actionable insights -- which services cost the most, which teams are over-spending, and where waste exists. As Kubernetes adoption grows, understanding cost at the pod and service level (not just the EC2 level) becomes essential. This lesson covers the tools that give you visibility from the cloud bill down to individual Kubernetes pods.

---

## Core Concepts

### Cloud-Native Cost Tools

**AWS Cost Explorer**

Built into AWS, provides cost and usage analysis with filtering, grouping, and forecasting.

```bash
# Query cost by service for the last month
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-04-01 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query '{
    "Dimensions": {
      "Key": "SERVICE",
      "MatchOptions": ["EQUALS"]
    }
  }'
```

```bash
# Get cost by tag (team)
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-04-01 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=TAG,Key=Team

# Get cost forecast
aws ce get-cost-forecast \
  --time-period Start=2026-04-16,End=2026-05-01 \
  --metric UNBLENDED_COST \
  --granularity MONTHLY
```

**Azure Cost Management**

```bash
# Query Azure costs via CLI
az costmanagement query --type ActualCost \
  --timeframe MonthToDate \
  --dataset-grouping name="ServiceName" type="Dimension"

# Create a budget
az consumption budget create \
  --budget-name "team-orders-monthly" \
  --amount 10000 \
  --category Cost \
  --time-grain Monthly
```

### Kubernetes Cost Tools

**Kubecost**: The most popular Kubernetes cost management tool. Provides cost per namespace, deployment, pod, and label.

```bash
# Install Kubecost
helm install kubecost \
  kubecost/cost-analyzer \
  --namespace kubecost \
  --create-namespace \
  --set kubecostToken="YOUR_TOKEN"

# Access the dashboard
kubectl port-forward -n kubecost svc/kubecost-cost-analyzer 9090:9090
# Open http://localhost:9090
```

Kubecost allocation model:
```
Cloud Bill: $50,000/month
  │
  ├── Kubernetes Cluster: $35,000
  │   ├── Namespace: orders     → $8,500
  │   │   ├── Deployment: api   → $5,000
  │   │   │   ├── CPU:          → $2,500
  │   │   │   ├── Memory:       → $1,500
  │   │   │   └── Network:      → $1,000
  │   │   └── Deployment: worker→ $3,500
  │   │
  │   ├── Namespace: payments   → $6,200
  │   ├── Namespace: monitoring → $4,800
  │   └── System (kube-system)  → $15,500
  │
  └── Non-Kubernetes: $15,000
      ├── RDS: $8,000
      ├── S3: $3,000
      └── Lambda: $4,000
```

**Kubecost API:**

```bash
# Get namespace costs for the last 7 days
curl http://kubecost:9090/model/allocation \
  -d window=7d \
  -d aggregate=namespace \
  -d accumulate=true

# Get cost by label (team)
curl http://kubecost:9090/model/allocation \
  -d window=30d \
  -d aggregate=label:team \
  -d accumulate=true
```

**OpenCost**: CNCF open-source alternative to Kubecost.

```bash
# Install OpenCost
helm install opencost \
  opencost/opencost \
  --namespace opencost \
  --create-namespace

# Query API
curl http://opencost:9003/allocation/compute \
  -d window=24h \
  -d resolution=1h \
  -d aggregate=namespace
```

### Infrastructure Cost in PRs (Infracost)

Infracost shows cloud cost estimates in Terraform/OpenTofu pull requests before infrastructure is deployed.

```bash
# Install Infracost
brew install infracost

# Authenticate
infracost auth login

# Run on a Terraform directory
infracost breakdown --path=./terraform/
```

Expected output:
```
Project: mycompany/terraform

 Name                                          Monthly Qty  Unit         Monthly Cost

 aws_instance.web_server
 ├─ Instance usage (Linux/UNIX, on-demand, m5.xlarge)   730  hours              $140.16
 ├─ root_block_device
 │  └─ Storage (gp3)                                    100  GB                   $8.00
 └─ ebs_block_device[0]
    └─ Storage (gp3)                                    500  GB                  $40.00

 aws_rds_instance.database
 ├─ Database instance (on-demand, db.r6g.large)         730  hours              $131.40
 └─ Storage (gp2)                                       100  GB                  $11.50

 aws_s3_bucket.assets
 └─ Storage (Standard)                                1,000  GB                  $23.00

 OVERALL TOTAL                                                                  $354.06
```

**Infracost in GitHub Actions:**

```yaml
# .github/workflows/infracost.yml
name: Infracost
on:
  pull_request:

jobs:
  infracost:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate Infracost JSON
        run: infracost breakdown --path=./terraform --format=json --out-file=/tmp/infracost.json

      - name: Post PR Comment
        uses: infracost/actions/comment@v3
        with:
          path: /tmp/infracost.json
          behavior: update
```

PR comment example:
```
## Infracost estimate

| Project | Baseline cost | New cost | Diff |
|---------|--------------|----------|------|
| terraform | $354.06/mo | $489.22/mo | +$135.16/mo (+38%) |

### New resources:
- aws_elasticache_cluster.redis: +$97.06/mo
- aws_cloudfront_distribution.cdn: +$38.10/mo
```

### CAST AI (Automated Optimization)

CAST AI automatically optimizes Kubernetes clusters by right-sizing instances, moving workloads to spot, and consolidating nodes.

```bash
# Install CAST AI agent
helm install castai-agent castai-helm/castai-agent \
  --namespace castai-agent \
  --create-namespace \
  --set apiKey=$CASTAI_API_KEY \
  --set clusterID=$CLUSTER_ID
```

---

## Step-by-Step Practical

### Setting Up Cost Visibility

**Step 1: Install Kubecost on Your Cluster**

```bash
helm repo add kubecost https://kubecost.github.io/cost-analyzer/
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost \
  --create-namespace \
  --set kubecostProductConfigs.clusterName="production" \
  --set kubecostProductConfigs.currencyCode="USD" \
  --set global.prometheus.enabled=true
```

**Step 2: Configure Cost Allocation Labels**

```yaml
# Ensure all deployments have cost allocation labels
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
  labels:
    app: orders-api
    team: orders
    cost-center: engineering
    environment: production
spec:
  template:
    metadata:
      labels:
        app: orders-api
        team: orders
        cost-center: engineering
```

**Step 3: Query Costs via API**

```python
# kubecost_report.py
"""Generate cost reports from Kubecost API."""

import requests
import json
from datetime import datetime


KUBECOST_URL = "http://kubecost.kubecost.svc.cluster.local:9090"


def get_namespace_costs(window="30d"):
    """Get costs grouped by namespace."""
    response = requests.get(
        f"{KUBECOST_URL}/model/allocation",
        params={
            "window": window,
            "aggregate": "namespace",
            "accumulate": "true",
        },
    )
    data = response.json()["data"][0]

    print(f"\n{'Namespace':<25} {'CPU':>10} {'Memory':>10} {'Total':>12}")
    print("-" * 60)

    total = 0
    for ns, costs in sorted(data.items(), key=lambda x: x[1].get("totalCost", 0), reverse=True):
        cpu_cost = costs.get("cpuCost", 0)
        mem_cost = costs.get("ramCost", 0)
        total_cost = costs.get("totalCost", 0)
        total += total_cost
        print(f"{ns:<25} ${cpu_cost:>8,.2f} ${mem_cost:>8,.2f} ${total_cost:>10,.2f}")

    print("-" * 60)
    print(f"{'TOTAL':<25} {'':>10} {'':>10} ${total:>10,.2f}")


def get_idle_costs(window="7d"):
    """Identify namespaces with high idle cost (over-provisioned)."""
    response = requests.get(
        f"{KUBECOST_URL}/model/allocation",
        params={
            "window": window,
            "aggregate": "namespace",
            "accumulate": "true",
            "idle": "true",
        },
    )
    data = response.json()["data"][0]

    print(f"\n{'Namespace':<25} {'Requested':>12} {'Used':>12} {'Efficiency':>12}")
    print("-" * 65)

    for ns, costs in sorted(data.items()):
        if ns.startswith("__"):
            continue
        requested = costs.get("totalCost", 0)
        efficiency = costs.get("totalEfficiency", 0) * 100
        used = requested * (efficiency / 100)
        print(f"{ns:<25} ${requested:>10,.2f} ${used:>10,.2f} {efficiency:>10.1f}%")


if __name__ == "__main__":
    print("=== Monthly Cost by Namespace ===")
    get_namespace_costs("30d")

    print("\n=== Resource Efficiency ===")
    get_idle_costs("7d")
```

Expected output:
```
=== Monthly Cost by Namespace ===

Namespace                       CPU     Memory        Total
------------------------------------------------------------
monitoring                   $2,100   $1,800      $4,200.00
orders                       $1,800   $1,200      $3,500.00
payments                     $1,500   $1,000      $2,800.00
kube-system                  $1,200     $800      $2,200.00
users                          $800     $600      $1,600.00
------------------------------------------------------------
TOTAL                                             $14,300.00

=== Resource Efficiency ===

Namespace                    Requested         Used   Efficiency
-----------------------------------------------------------------
monitoring                    $4,200.00    $2,940.00       70.0%
orders                        $3,500.00    $2,100.00       60.0%
payments                      $2,800.00      $840.00       30.0%  ← waste!
users                         $1,600.00      $480.00       30.0%  ← waste!
```

**Step 4: Set Up Infracost for Terraform PRs**

```bash
# Install and configure
infracost auth login
infracost configure set pricing_api_endpoint https://pricing.api.infracost.io

# Generate baseline cost
cd terraform/
infracost breakdown --path . --format json --out-file baseline.json

# After making changes, compare
infracost diff --path . --compare-to baseline.json
```

---

## Exercises

1. **Cost Dashboard**: Install Kubecost or OpenCost on a Kubernetes cluster. Create a dashboard that shows cost by namespace, by team label, and by environment (dev/staging/prod).

2. **Waste Detection Script**: Write a Python script that uses the AWS CLI to find: unattached EBS volumes, idle EC2 instances (CPU < 5%), old snapshots (> 90 days), and unused Elastic IPs. Calculate total potential savings.

3. **Infracost Integration**: Add Infracost to a Terraform repository's CI/CD pipeline. Make a change that increases costs and verify the PR comment shows the cost diff.

4. **Cost per Service**: Calculate the true cost of running one of your services, including: compute, database, cache, storage, data transfer, and monitoring. Determine cost per transaction.

5. **Cloud Provider Comparison**: For your primary workload, compare costs across AWS, Azure, and GCP using their pricing calculators. Include compute, storage, database, and data transfer.

---

## Knowledge Check

**Q1: What is the difference between Kubecost and Infracost?**

<details>
<summary>Answer</summary>

Kubecost provides real-time cost visibility for running Kubernetes workloads -- it tells you what you are spending now, broken down by namespace, deployment, pod, and label. It monitors actual resource usage and allocation. Infracost provides cost estimates for infrastructure changes before they are deployed -- it analyzes Terraform/OpenTofu code in pull requests and comments with the projected cost impact. They solve different problems: Kubecost = "what are we spending?" (ongoing monitoring), Infracost = "what will this change cost?" (pre-deployment estimation). Use both together for comprehensive cost management.
</details>

**Q2: Why is Kubernetes cost allocation harder than traditional cloud cost allocation?**

<details>
<summary>Answer</summary>

In traditional cloud, each resource (EC2 instance, RDS database) has a clear cost and can be tagged to a team. In Kubernetes, multiple workloads share the same nodes, and the cost of a node must be split among all pods running on it. Challenges: (1) shared node costs must be apportioned based on resource requests/limits, (2) system components (kube-system, monitoring) are shared costs that need fair allocation, (3) pods can be rescheduled across nodes, making tracking dynamic, (4) resource requests may differ from actual usage, so you need to decide between requested vs. actual allocation. Tools like Kubecost solve this by monitoring resource usage and applying allocation models.
</details>

**Q3: How does Infracost work in a CI/CD pipeline?**

<details>
<summary>Answer</summary>

Infracost integrates into CI/CD as a step that runs during pull requests. The workflow: (1) Infracost parses the Terraform/OpenTofu code in the PR, (2) it resolves resource types, sizes, and configurations, (3) it queries cloud pricing APIs to calculate costs, (4) it compares the new cost against the baseline (current infrastructure), (5) it posts a comment on the PR showing the cost diff (e.g., "+$135/month"). This gives engineers cost awareness before they merge infrastructure changes. Some teams add cost thresholds that require approval for changes exceeding a certain amount.
</details>

**Q4: What is CAST AI and how does it differ from Karpenter?**

<details>
<summary>Answer</summary>

CAST AI is a commercial Kubernetes optimization platform that automatically right-sizes workloads, moves pods to spot instances, and replaces nodes with cheaper alternatives. It differs from Karpenter in scope: Karpenter optimizes node provisioning (which instance types to launch), while CAST AI also optimizes workload configuration (recommending resource request/limit changes, pod scheduling, and bin-packing improvements). CAST AI works across multiple cloud providers (AWS, GCP, Azure) while Karpenter was designed primarily for EKS. CAST AI provides a managed dashboard with cost savings reports and recommendations, while Karpenter is a self-managed controller.
</details>
