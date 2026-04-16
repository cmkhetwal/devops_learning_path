# Optimization Strategies

## Why This Matters in DevOps

Identifying waste is only half the battle -- you need concrete strategies to eliminate it. Cloud cost optimization is not a one-time project but a continuous practice with techniques ranging from simple (turning off unused resources) to sophisticated (spot instance orchestration, storage tiering, architecture redesign). The strategies in this lesson can typically reduce cloud spend by 30-60%, and they compound: right-sizing alone saves 20%, adding spot instances saves another 30%, and storage optimization adds another 10%.

---

## Core Concepts

### Right-Sizing Instances

Right-sizing means matching instance sizes to actual workload requirements instead of over-provisioning "just in case."

```
Before Right-Sizing:                After Right-Sizing:
m5.2xlarge (8 vCPU, 32 GB)        m5.large (2 vCPU, 8 GB)
├── CPU Usage: 12% avg             ├── CPU Usage: 55% avg
├── Memory Usage: 18% avg         ├── Memory Usage: 65% avg
├── Cost: $280/month              ├── Cost: $70/month
└── Waste: ~75%                   └── Savings: 75%
```

```bash
# AWS Compute Optimizer recommendations
aws compute-optimizer get-ec2-instance-recommendations \
  --filters name=Finding,values=OVER_PROVISIONED \
  --query "instanceRecommendations[*].{
    Instance: instanceArn,
    Current: currentInstanceType,
    Recommended: recommendationOptions[0].instanceType,
    Savings: recommendationOptions[0].estimatedMonthlySavings.value
  }" --output table
```

Expected output:
```
Instance                    Current         Recommended     Savings
i-0abc123 (orders-api)     m5.2xlarge      m5.large        $210.00
i-0def456 (user-service)   r5.xlarge       r5.large        $95.00
i-0ghi789 (batch-worker)   c5.4xlarge      c5.xlarge       $340.00
```

### Reserved Instances vs Savings Plans vs Spot

```
Pricing Model      Commitment    Savings    Flexibility     Best For
───────────────────────────────────────────────────────────────────────
On-Demand          None          0%         Full            Unpredictable workloads
Reserved (1yr)     Instance      40%        Low (locked)    Stable, predictable
Reserved (3yr)     Instance      60%        Very Low        Long-term stable
Savings Plan(1yr)  $/hour        30-40%     High            Flexible commitment
Savings Plan(3yr)  $/hour        50-60%     High            Long-term flexible
Spot               None          60-90%     Lowest          Fault-tolerant, flexible

Decision Framework:
├── Stable 24/7 workload → Savings Plan or Reserved Instance
├── Variable but predictable → Savings Plan
├── Fault-tolerant batch → Spot Instances
├── Short-term project → On-Demand
└── Mixed → Savings Plan base + Spot for burst
```

```bash
# Check Savings Plan recommendations
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days SIXTY_DAYS
```

### Auto-Scaling to Zero

Development and staging environments that run 24/7 waste 67% of their cost (16 hours of unused time per day).

```yaml
# keda-scaler-schedule.yaml - Scale to zero outside business hours
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: orders-api-dev
  namespace: dev
spec:
  scaleTargetRef:
    name: orders-api
  minReplicaCount: 0  # Scale to zero
  maxReplicaCount: 3
  triggers:
    - type: cron
      metadata:
        timezone: America/New_York
        start: "0 8 * * 1-5"   # Scale up Mon-Fri 8 AM
        end: "0 20 * * 1-5"    # Scale down Mon-Fri 8 PM
        desiredReplicas: "2"
```

```bash
# AWS: Stop/start dev instances on schedule
# EventBridge rule + Lambda
aws events put-rule \
  --name "stop-dev-instances" \
  --schedule-expression "cron(0 20 ? * MON-FRI *)" \
  --description "Stop dev instances at 8 PM ET"

aws events put-rule \
  --name "start-dev-instances" \
  --schedule-expression "cron(0 8 ? * MON-FRI *)" \
  --description "Start dev instances at 8 AM ET"
```

### Storage Tiering

```
S3 Storage Classes and Costs (per GB/month):
────────────────────────────────────────────
S3 Standard:               $0.023  ← Hot data (frequent access)
S3 Standard-IA:            $0.0125 ← Warm data (monthly access)
S3 One Zone-IA:            $0.010  ← Non-critical warm data
S3 Glacier Instant:        $0.004  ← Cold data (quarterly access)
S3 Glacier Flexible:       $0.0036 ← Archive (annual access)
S3 Glacier Deep Archive:   $0.00099← Long-term archive (7+ years)
```

```json
{
  "Rules": [
    {
      "ID": "lifecycle-optimization",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

### Data Transfer Optimization

```
Data Transfer Costs (often overlooked):
───────────────────────────────────────
Within AZ:              Free
Cross-AZ:               $0.01/GB each way  ← adds up fast
Cross-Region:           $0.02/GB
Internet Outbound:      $0.09/GB (first 10TB)
CloudFront to Internet: $0.085/GB (cheaper than direct)
VPC Endpoints:          $0.01/GB (vs NAT GW $0.045/GB)
```

```
Optimization Strategies:
├── Use VPC endpoints instead of NAT Gateway for AWS services
│   NAT Gateway: $0.045/GB + $32/month
│   VPC Endpoint: $0.01/GB + $7.30/month
│   Savings: 75%+
│
├── Keep traffic within AZ when possible
│   Deploy replicas of databases in each AZ
│   Use topology-aware routing in K8s
│
├── Use CloudFront for static content
│   Direct S3: $0.09/GB outbound
│   CloudFront: $0.085/GB + caching reduces total transfer
│
└── Compress data in transit
    Enable gzip/brotli on APIs and web servers
```

### Unused Resource Cleanup

```python
# cleanup_audit.py
"""Identify and report unused AWS resources."""

import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
elb = boto3.client('elbv2')
rds = boto3.client('rds')


def find_unattached_volumes():
    """Find EBS volumes not attached to any instance."""
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )['Volumes']

    total_cost = 0
    print("\n=== Unattached EBS Volumes ===")
    for vol in volumes:
        size = vol['Size']
        vol_type = vol['VolumeType']
        # gp3: $0.08/GB/month, gp2: $0.10/GB/month
        monthly_cost = size * (0.08 if vol_type == 'gp3' else 0.10)
        total_cost += monthly_cost
        print(f"  {vol['VolumeId']}: {size}GB {vol_type} = ${monthly_cost:.2f}/mo "
              f"(created: {vol['CreateTime'].strftime('%Y-%m-%d')})")

    print(f"  TOTAL SAVINGS: ${total_cost:.2f}/month")
    return total_cost


def find_unused_load_balancers():
    """Find ALBs/NLBs with no targets."""
    lbs = elb.describe_load_balancers()['LoadBalancers']

    print("\n=== Load Balancers with No Targets ===")
    total_cost = 0
    for lb in lbs:
        target_groups = elb.describe_target_groups(
            LoadBalancerArn=lb['LoadBalancerArn']
        )['TargetGroups']

        has_targets = False
        for tg in target_groups:
            health = elb.describe_target_health(
                TargetGroupArn=tg['TargetGroupArn']
            )['TargetHealthDescriptions']
            if health:
                has_targets = True
                break

        if not has_targets:
            monthly_cost = 22  # ~$22/month for idle ALB
            total_cost += monthly_cost
            print(f"  {lb['LoadBalancerName']}: No targets = ${monthly_cost:.2f}/mo")

    print(f"  TOTAL SAVINGS: ${total_cost:.2f}/month")
    return total_cost


def find_old_snapshots(days_old=90):
    """Find EBS snapshots older than N days."""
    cutoff = datetime.now(tz=None) - timedelta(days=days_old)
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

    old_snaps = [s for s in snapshots if s['StartTime'].replace(tzinfo=None) < cutoff]

    total_size = sum(s['VolumeSize'] for s in old_snaps)
    total_cost = total_size * 0.05  # $0.05/GB/month for snapshots

    print(f"\n=== Snapshots older than {days_old} days ===")
    print(f"  Count: {len(old_snaps)}")
    print(f"  Total Size: {total_size} GB")
    print(f"  TOTAL SAVINGS: ${total_cost:.2f}/month")
    return total_cost


if __name__ == "__main__":
    print("=" * 50)
    print("  CLOUD WASTE AUDIT REPORT")
    print("=" * 50)

    total = 0
    total += find_unattached_volumes()
    total += find_unused_load_balancers()
    total += find_old_snapshots()

    print(f"\n{'=' * 50}")
    print(f"  TOTAL POTENTIAL SAVINGS: ${total:.2f}/month (${total * 12:.2f}/year)")
    print(f"{'=' * 50}")
```

---

## Step-by-Step Practical

### Analyzing and Optimizing a Cloud Bill

**Step 1: Get Current Spending Breakdown**

```bash
# Top 10 services by cost
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-04-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
services = data['ResultsByTime'][0]['Groups']
services.sort(key=lambda x: float(x['Metrics']['UnblendedCost']['Amount']), reverse=True)
print(f\"{'Service':<40} {'Cost':>12}\")
print('-' * 55)
total = 0
for s in services[:10]:
    cost = float(s['Metrics']['UnblendedCost']['Amount'])
    total += cost
    print(f\"{s['Keys'][0]:<40} \${cost:>10,.2f}\")
print('-' * 55)
print(f\"{'TOTAL (top 10)':<40} \${total:>10,.2f}\")
"
```

**Step 2: Apply Optimization Strategies**

```yaml
# optimization-plan.yaml
optimizations:
  - category: "Right-sizing"
    actions:
      - description: "Downsize 5 over-provisioned EC2 instances"
        current_cost: "$1,400/month"
        projected_cost: "$450/month"
        savings: "$950/month"
        risk: "Low (based on 30-day metrics)"

  - category: "Compute Savings Plans"
    actions:
      - description: "Purchase 1-year no-upfront Savings Plan"
        commitment: "$500/month (covers stable baseline)"
        savings: "$200/month (40% on committed usage)"
        risk: "Medium (1-year commitment)"

  - category: "Spot Instances"
    actions:
      - description: "Move batch workers to Spot (via Karpenter)"
        current_cost: "$2,100/month (on-demand)"
        projected_cost: "$630/month (spot, 70% savings)"
        savings: "$1,470/month"
        risk: "Low (batch jobs are fault-tolerant)"

  - category: "Storage Optimization"
    actions:
      - description: "Add S3 lifecycle policies"
        current_cost: "$800/month (all Standard)"
        projected_cost: "$350/month (tiered)"
        savings: "$450/month"

      - description: "Delete unattached EBS volumes"
        savings: "$120/month"

  - category: "Scheduling"
    actions:
      - description: "Stop dev/staging outside business hours"
        current_cost: "$3,000/month (24/7)"
        projected_cost: "$1,000/month (10h/day, weekdays)"
        savings: "$2,000/month"

total_monthly_savings: "$5,190/month"
total_annual_savings: "$62,280/year"
```

---

## Exercises

1. **Right-Sizing Analysis**: Use AWS Compute Optimizer (or analyze CloudWatch metrics) to identify 5 over-provisioned instances. Calculate current cost, recommended cost, and total savings.

2. **Savings Plan Calculator**: Using your last 3 months of EC2 usage data, calculate the optimal Savings Plan commitment. Compare: no-upfront 1-year, all-upfront 1-year, and no-upfront 3-year options.

3. **Storage Audit**: Audit all S3 buckets and EBS volumes. Implement lifecycle policies for S3, identify unattached EBS volumes, and clean up old snapshots. Calculate total savings.

4. **Schedule Optimization**: Implement a scheduling system that stops non-production resources outside business hours. Calculate the savings from running dev/staging 10 hours/day vs 24 hours/day.

5. **Data Transfer Analysis**: Analyze your data transfer costs using AWS Cost Explorer (filter by usage type containing "DataTransfer"). Identify the largest sources and propose optimizations (VPC endpoints, CloudFront, compression).

---

## Knowledge Check

**Q1: What is right-sizing and how do you identify candidates?**

<details>
<summary>Answer</summary>

Right-sizing is adjusting instance sizes to match actual workload requirements. Identify candidates by: (1) CloudWatch metrics -- look for instances with average CPU < 20% and memory < 30% over 14+ days, (2) AWS Compute Optimizer -- provides automated recommendations based on utilization patterns, (3) Kubecost/Prometheus -- for Kubernetes, compare resource requests to actual usage. Start with the largest instances (highest potential savings). Right-size in stages: monitor for 2 weeks, downsize one tier, monitor for another week, then downsize further if needed. Always keep a buffer (target 60-70% peak utilization, not 100%).
</details>

**Q2: When should you use Savings Plans vs Reserved Instances?**

<details>
<summary>Answer</summary>

Savings Plans are generally preferred because they are more flexible. Compute Savings Plans apply to any EC2 instance family, size, region, OS, or tenancy, and also cover Fargate and Lambda. Reserved Instances lock you to a specific instance type and region. Use Savings Plans when: you want flexibility to change instance types or regions, you use a mix of EC2, Fargate, and Lambda. Use Reserved Instances when: you have very stable, long-term workloads on specific instance types, or when RIs offer better pricing for your specific case (Standard RIs can be 5-10% cheaper than equivalent Savings Plans for committed instance types).
</details>

**Q3: What are the most commonly overlooked cloud costs?**

<details>
<summary>Answer</summary>

Five commonly overlooked costs: (1) **Data transfer** -- cross-AZ ($0.01/GB each way), NAT Gateway ($0.045/GB), and internet egress ($0.09/GB) can add up to 10-15% of the total bill. (2) **Idle load balancers** -- each ALB costs ~$22/month even with no traffic. (3) **EBS snapshots** -- accumulate over time; old snapshots are easy to forget. (4) **CloudWatch logs** -- ingestion costs $0.50/GB; verbose logging can cost thousands. (5) **RDS storage I/O** -- provisioned IOPS and storage auto-scaling can significantly increase database costs beyond the base instance price.
</details>

**Q4: How do you implement auto-scaling to zero for development environments?**

<details>
<summary>Answer</summary>

Three approaches: (1) **KEDA with cron trigger** -- configure ScaledObjects with cron schedules that set minReplicaCount to 0 outside business hours and back to N during work hours. (2) **AWS Lambda + EventBridge** -- create Lambda functions that stop/start EC2 instances, RDS instances, and EKS node groups on a cron schedule. (3) **Karpenter with expiry** -- configure Karpenter to expire dev nodes after 10 hours, and use pod disruption budgets that allow full eviction. Combine with KEDA to scale deployments to zero. Expected savings: running 10 hours/day instead of 24 saves 58%; running only weekdays saves an additional 28%, for total savings of 70%.
</details>
