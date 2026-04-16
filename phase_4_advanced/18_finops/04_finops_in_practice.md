# FinOps in Practice

## Why This Matters in DevOps

Cost optimization without organizational processes falls apart. Engineers optimize once, then costs creep back up as new resources are created without cost awareness. FinOps in practice means embedding cost consciousness into daily workflows: budgets that alert before overspending, tagging that enables accountability, anomaly detection that catches runaway costs, and CI/CD gates that show cost impact before deployment. This lesson covers the operational practices that make FinOps sustainable.

---

## Core Concepts

### Cost Budgets and Alerts

```bash
# Create an AWS Budget
aws budgets create-budget --account-id 123456789012 \
  --budget '{
    "BudgetName": "monthly-cloud-budget",
    "BudgetLimit": {"Amount": "50000", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {"SubscriptionType": "EMAIL", "Address": "finops@company.com"},
        {"SubscriptionType": "SNS", "Address": "arn:aws:sns:us-east-1:123456789:cost-alerts"}
      ]
    },
    {
      "Notification": {
        "NotificationType": "FORECASTED",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 100,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {"SubscriptionType": "EMAIL", "Address": "finops@company.com"}
      ]
    }
  ]'

# Create per-team budgets
for team in orders payments users platform; do
  aws budgets create-budget --account-id 123456789012 \
    --budget "{
      \"BudgetName\": \"team-${team}-monthly\",
      \"BudgetLimit\": {\"Amount\": \"10000\", \"Unit\": \"USD\"},
      \"TimeUnit\": \"MONTHLY\",
      \"BudgetType\": \"COST\",
      \"CostFilters\": {
        \"TagKeyValue\": [\"user:Team\$${team}\"]
      }
    }" \
    --notifications-with-subscribers "[{
      \"Notification\": {
        \"NotificationType\": \"ACTUAL\",
        \"ComparisonOperator\": \"GREATER_THAN\",
        \"Threshold\": 90,
        \"ThresholdType\": \"PERCENTAGE\"
      },
      \"Subscribers\": [{
        \"SubscriptionType\": \"EMAIL\",
        \"Address\": \"team-${team}-lead@company.com\"
      }]
    }]"
done
```

### Tagging Strategy

```yaml
# tagging-policy.yaml
mandatory_tags:
  - key: "Team"
    description: "Owning team name"
    allowed_values: ["orders", "payments", "users", "platform", "data"]
    enforcement: "deny creation without tag"

  - key: "Environment"
    description: "Deployment environment"
    allowed_values: ["dev", "staging", "production"]

  - key: "Service"
    description: "Service or application name"
    example: "orders-api"

  - key: "CostCenter"
    description: "Financial cost center code"
    example: "CC-1234"

recommended_tags:
  - key: "ManagedBy"
    values: ["terraform", "crossplane", "pulumi", "manual"]

  - key: "Lifecycle"
    values: ["temporary", "permanent"]
    description: "Helps identify resources that should be cleaned up"

  - key: "DataClassification"
    values: ["public", "internal", "confidential", "restricted"]
```

**Enforce Tagging with AWS SCP:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireTags",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "Null": {
          "aws:RequestTag/Team": "true",
          "aws:RequestTag/Environment": "true",
          "aws:RequestTag/Service": "true"
        }
      }
    }
  ]
}
```

**Enforce Tagging in Kubernetes (Kyverno):**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-cost-labels
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-team-label
      match:
        resources:
          kinds: ["Deployment", "StatefulSet"]
      validate:
        message: "All Deployments must have 'team' and 'cost-center' labels"
        pattern:
          metadata:
            labels:
              team: "?*"
              cost-center: "?*"
```

### Cost Anomaly Detection

```bash
# AWS Cost Anomaly Detection
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "service-cost-monitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'

aws ce create-anomaly-subscription \
  --anomaly-subscription '{
    "SubscriptionName": "cost-anomaly-alerts",
    "MonitorArnList": ["arn:aws:ce::123456789:anomalymonitor/abc123"],
    "Subscribers": [
      {"Type": "EMAIL", "Address": "finops@company.com"},
      {"Type": "SNS", "Address": "arn:aws:sns:us-east-1:123456789:cost-anomalies"}
    ],
    "Threshold": 100,
    "Frequency": "IMMEDIATE"
  }'
```

### FinOps in CI/CD (Cost Gates)

```yaml
# .github/workflows/cost-gate.yml
name: Cost Gate
on:
  pull_request:
    paths:
      - 'terraform/**'

jobs:
  cost-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate cost estimate
        run: |
          infracost breakdown --path=terraform/ \
            --format=json --out-file=/tmp/infracost.json

      - name: Check cost threshold
        run: |
          MONTHLY_DIFF=$(jq '.diffTotalMonthlyCost | tonumber' /tmp/infracost.json)
          THRESHOLD=500

          if (( $(echo "$MONTHLY_DIFF > $THRESHOLD" | bc -l) )); then
            echo "COST GATE FAILED: Monthly cost increase of \$$MONTHLY_DIFF exceeds threshold of \$$THRESHOLD"
            echo "Requires FinOps team approval."
            exit 1
          fi

          echo "Cost gate passed: \$$MONTHLY_DIFF monthly increase (threshold: \$$THRESHOLD)"

      - name: Post PR Comment
        uses: infracost/actions/comment@v3
        with:
          path: /tmp/infracost.json
```

### Team Accountability

```yaml
# weekly-cost-report.yaml (generated automatically)
report_date: "2026-04-16"
report_period: "April 7-13, 2026"

team_costs:
  - team: "orders"
    budget: 12000
    actual: 10800
    status: "on_track"
    trend: "stable"
    top_services:
      - { service: "EC2", cost: 4200, change: "-5%" }
      - { service: "RDS", cost: 3800, change: "+2%" }
      - { service: "S3", cost: 1200, change: "+8%" }

  - team: "payments"
    budget: 8000
    actual: 9200
    status: "over_budget"
    trend: "increasing"
    action_required: true
    top_services:
      - { service: "EC2", cost: 4500, change: "+15%" }
      - { service: "ElastiCache", cost: 2800, change: "+25%" }
    recommendation: "Right-size ElastiCache from r6g.xlarge to r6g.large"

  - team: "data"
    budget: 15000
    actual: 11200
    status: "under_budget"
    trend: "decreasing"
    savings_achieved: "$3,800 this month"
```

### FinOps Dashboards

```python
# finops_dashboard.py
"""Generate FinOps metrics for Grafana dashboard."""

import boto3
from datetime import datetime, timedelta


def get_daily_costs(days=30):
    """Get daily cost trend for Grafana."""
    ce = boto3.client('ce')
    end = datetime.now()
    start = end - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d'),
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
    )

    for day in response['ResultsByTime']:
        date = day['TimePeriod']['Start']
        cost = float(day['Total']['UnblendedCost']['Amount'])
        # Output in Prometheus format for Grafana
        print(f'daily_cloud_cost{{date="{date}"}} {cost}')


def get_cost_by_team():
    """Get cost per team for the current month."""
    ce = boto3.client('ce')
    now = datetime.now()
    start = now.replace(day=1).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'TAG', 'Key': 'Team'}],
    )

    for group in response['ResultsByTime'][0]['Groups']:
        team = group['Keys'][0].replace('Team$', '') or 'untagged'
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        print(f'team_cloud_cost{{team="{team}"}} {cost}')


def get_savings_metrics():
    """Calculate key FinOps metrics."""
    ce = boto3.client('ce')
    now = datetime.now()

    # Total spend
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': now.replace(day=1).strftime('%Y-%m-%d'),
            'End': now.strftime('%Y-%m-%d'),
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
    )
    total = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])

    # Savings plan coverage
    sp_response = ce.get_savings_plans_coverage(
        TimePeriod={
            'Start': now.replace(day=1).strftime('%Y-%m-%d'),
            'End': now.strftime('%Y-%m-%d'),
        },
        Granularity='MONTHLY',
    )
    coverage = float(sp_response['SavingsPlansCoverages'][0]['CoveragePercentage']['Percentage'])

    print(f'total_monthly_spend {total}')
    print(f'savings_plan_coverage {coverage}')
    print(f'untagged_spend_estimate {total * 0.15}')  # Estimate 15% untagged


if __name__ == "__main__":
    get_daily_costs()
    get_cost_by_team()
    get_savings_metrics()
```

### Building a Cost-Aware Culture

```
Culture Building Strategies:
────────────────────────────

1. Weekly Cost Digest (Slack)
   Automated bot posts: team costs, top changes, waste identified

2. "Cost Hero" Recognition
   Monthly recognition for engineers who achieve significant savings

3. Cost in Sprint Reviews
   Show infrastructure cost alongside feature demos

4. Lunch & Learn Sessions
   Monthly sessions on cost optimization techniques

5. Gamification
   Team leaderboard for efficiency (cost per transaction)

6. Architecture Reviews Include Cost
   Every architecture decision document includes cost estimate
```

---

## Step-by-Step Practical

### Setting Up a Complete FinOps Pipeline

```bash
# Step 1: Enable mandatory tagging (AWS Config rule)
aws configservice put-config-rule --config-rule '{
  "ConfigRuleName": "required-tags",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "REQUIRED_TAGS"
  },
  "InputParameters": "{\"tag1Key\":\"Team\",\"tag2Key\":\"Environment\",\"tag3Key\":\"Service\"}"
}'

# Step 2: Create cost anomaly detection
aws ce create-anomaly-monitor --anomaly-monitor '{
  "MonitorName": "all-services",
  "MonitorType": "DIMENSIONAL",
  "MonitorDimension": "SERVICE"
}'

# Step 3: Set up budget alerts for all teams
# (see budget creation commands above)

# Step 4: Install Kubecost for Kubernetes visibility
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost --create-namespace

# Step 5: Add Infracost to all Terraform repos
# (see CI/CD integration above)
```

---

## Exercises

1. **Budget System**: Create AWS budgets for your organization (or simulate). Set up alerts at 50%, 80%, and 100% of budget. Configure a Slack notification via SNS for the 80% threshold.

2. **Tagging Audit**: Run an audit on your AWS account to find untagged resources. Calculate what percentage of your spend is untagged. Implement mandatory tag enforcement using AWS Config or SCPs.

3. **Cost Anomaly Detection**: Enable AWS Cost Anomaly Detection. Create a custom monitor for your top-spending service. Simulate an anomaly (e.g., launch 10 large instances) and verify the alert fires.

4. **Weekly Cost Report**: Build an automated weekly cost report that shows: total spend, cost by team, week-over-week change, top cost drivers, and optimization recommendations. Send it via email or Slack.

5. **FinOps Certification Study Plan**: Review the FinOps Certified Practitioner exam objectives. Create a study plan covering all domains: FinOps principles, cloud billing, rate optimization, usage optimization, and organizational alignment.

---

## Knowledge Check

**Q1: Why is tagging essential for FinOps, and what happens without it?**

<details>
<summary>Answer</summary>

Tags are the mechanism for attributing cloud costs to teams, services, and environments. Without tags, you have a single cloud bill with no way to determine who is responsible for what. This makes showback/chargeback impossible, prevents team-level budgeting, and means optimization opportunities cannot be assigned to specific owners. Industry data shows 15-35% of cloud resources are untagged, creating a "dark spend" that nobody takes ownership of. Effective FinOps requires mandatory tag enforcement at the point of resource creation, combined with regular audits and remediation for untagged resources.
</details>

**Q2: What are cost gates in CI/CD and when should they block deployments?**

<details>
<summary>Answer</summary>

Cost gates are automated checks in CI/CD pipelines that evaluate the cost impact of infrastructure changes before deployment. Using tools like Infracost, the pipeline estimates the monthly cost difference of Terraform/OpenTofu changes and can block merges that exceed a threshold. Cost gates should block when: (1) the monthly cost increase exceeds a significant threshold (e.g., >$500/month), requiring FinOps team approval, (2) a change creates resources without required cost allocation tags, (3) a change uses non-approved instance types (e.g., creating a p4d.24xlarge without justification). Cost gates should inform (not block) for smaller changes, showing the cost impact as a PR comment.
</details>

**Q3: How should a weekly cost report be structured for maximum impact?**

<details>
<summary>Answer</summary>

An effective weekly cost report includes: (1) **Executive summary** -- total spend, budget status, week-over-week trend (one sentence). (2) **Team breakdown** -- each team's spend, budget utilization, and trend with red/yellow/green status. (3) **Cost changes** -- top 5 increases and decreases, with root causes identified. (4) **Waste identified** -- idle resources, over-provisioned instances, unattached storage found this week. (5) **Action items** -- specific, assigned recommendations (e.g., "Team Payments: right-size ElastiCache from r6g.xlarge to r6g.large, estimated savings $450/month"). (6) **Wins** -- celebrate teams that reduced costs or improved efficiency. Keep it concise (one page) and automated.
</details>

**Q4: What is the FinOps Certified Practitioner certification?**

<details>
<summary>Answer</summary>

The FinOps Certified Practitioner (FOCP) is a certification from the FinOps Foundation (part of the Linux Foundation) that validates knowledge of cloud financial management. It covers: FinOps principles and lifecycle (inform, optimize, operate), cloud billing and pricing models, rate optimization (reserved instances, savings plans), usage optimization (right-sizing, waste elimination), organizational alignment (showback, chargeback, team structures), and FinOps tooling. The exam is multiple-choice, remotely proctored, and costs approximately $300. It is valuable for DevOps engineers because it demonstrates FinOps competency and is increasingly requested by employers, especially for senior and platform engineering roles.
</details>
