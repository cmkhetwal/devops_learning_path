# Autonomous Operations

## Why This Matters in DevOps

The promise of autonomous operations is not about replacing humans -- it is about reducing the time between "something is wrong" and "it is fixed" from hours to minutes or seconds. AI-powered incident detection catches anomalies that static thresholds miss. Automated root cause analysis reduces mean-time-to-diagnose from 45 minutes to 5 minutes. Self-healing infrastructure automatically remediates known failure patterns. These capabilities reduce on-call burden, improve reliability, and let engineers focus on building rather than firefighting.

---

## Core Concepts

### AI for Incident Detection

**Traditional Monitoring:**
```
Static threshold: Alert if CPU > 80%
Problem: 80% at 3 AM might be normal for batch processing
         80% at 2 PM during a traffic spike is normal too
         75% during a typically quiet period might be the real problem
```

**AI-Powered Anomaly Detection:**
```
ML model learns: "CPU for this service is usually 20-30% during weekday
                  business hours, 60-70% during batch runs (11 PM-3 AM),
                  and 10-15% on weekends"

Alert: "CPU is 55% at 2 PM on Tuesday. This is 2.5 standard deviations
        above the learned baseline for this time period."
```

```python
# anomaly_detection.py
"""Simple anomaly detection for Prometheus metrics."""

import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: dict


class AnomalyDetector:
    """Detect anomalies in time-series metrics using statistical methods."""

    def __init__(self, sensitivity: float = 2.5):
        self.sensitivity = sensitivity  # Number of standard deviations
        self.baselines = {}  # {metric_key: {hour_of_week: (mean, std)}}

    def learn_baseline(self, metric_name: str, historical_data: list[MetricPoint]):
        """Learn normal behavior patterns from historical data."""
        # Group by hour of week (0-167)
        hourly_values = {}
        for point in historical_data:
            hour_of_week = point.timestamp.weekday() * 24 + point.timestamp.hour
            hourly_values.setdefault(hour_of_week, []).append(point.value)

        # Calculate mean and standard deviation per hour
        self.baselines[metric_name] = {}
        for hour, values in hourly_values.items():
            self.baselines[metric_name][hour] = (
                np.mean(values),
                max(np.std(values), 0.01),  # Minimum std to avoid division by zero
            )

    def is_anomalous(self, metric_name: str, point: MetricPoint) -> dict:
        """Check if a metric value is anomalous."""
        if metric_name not in self.baselines:
            return {"anomalous": False, "reason": "No baseline learned"}

        hour_of_week = point.timestamp.weekday() * 24 + point.timestamp.hour
        baseline = self.baselines[metric_name].get(hour_of_week)

        if not baseline:
            return {"anomalous": False, "reason": "No baseline for this hour"}

        mean, std = baseline
        z_score = abs(point.value - mean) / std

        is_anomaly = z_score > self.sensitivity

        return {
            "anomalous": is_anomaly,
            "value": point.value,
            "expected_mean": round(mean, 2),
            "expected_std": round(std, 2),
            "z_score": round(z_score, 2),
            "deviation": "above" if point.value > mean else "below",
            "severity": "critical" if z_score > 4 else "warning" if z_score > 3 else "info",
        }


# Usage
detector = AnomalyDetector(sensitivity=2.5)

# Learn from 4 weeks of historical data
# (In production, query Prometheus API)
historical = [
    MetricPoint(
        datetime(2026, 3, d, h, 0),
        np.random.normal(30, 5) if 9 <= h <= 17 else np.random.normal(10, 3),
        {"service": "orders-api"},
    )
    for d in range(1, 29)
    for h in range(24)
]

detector.learn_baseline("cpu_usage", historical)

# Check current value
current = MetricPoint(
    datetime(2026, 4, 16, 14, 0),  # Wednesday 2 PM
    75.0,  # Unusually high
    {"service": "orders-api"},
)

result = detector.is_anomalous("cpu_usage", current)
print(f"Anomalous: {result['anomalous']}")
print(f"Value: {result['value']}%, Expected: {result['expected_mean']}% +/- {result['expected_std']}%")
print(f"Z-Score: {result['z_score']} ({result['severity']})")
```

### Root Cause Analysis Automation

```python
# rca_assistant.py
"""AI-assisted root cause analysis."""


class RootCauseAnalyzer:
    """Correlate symptoms across services to identify root causes."""

    def __init__(self):
        self.known_patterns = [
            {
                "symptoms": ["high_latency", "high_cpu", "increased_errors"],
                "services_affected": ["api", "database"],
                "root_cause": "Database query performance degradation",
                "remediation": [
                    "Check slow query log: kubectl exec -it postgres-0 -- pg_stat_activity",
                    "Look for missing indexes: EXPLAIN ANALYZE on slow queries",
                    "Check connection pool: max_connections vs active_connections",
                ],
                "confidence": 0.85,
            },
            {
                "symptoms": ["high_latency", "connection_errors", "pod_restarts"],
                "services_affected": ["api", "redis"],
                "root_cause": "Redis connection exhaustion",
                "remediation": [
                    "Check Redis connections: redis-cli info clients",
                    "Restart affected pods: kubectl rollout restart deployment/api",
                    "Increase connection pool size in application config",
                ],
                "confidence": 0.80,
            },
            {
                "symptoms": ["5xx_errors", "pod_oom_killed", "high_memory"],
                "services_affected": ["api"],
                "root_cause": "Memory leak in application",
                "remediation": [
                    "Check OOMKilled events: kubectl get events --field-selector reason=OOMKilling",
                    "Increase memory limits temporarily",
                    "Profile application memory usage",
                    "Check for known memory leak in recent deployments",
                ],
                "confidence": 0.75,
            },
        ]

    def analyze(self, symptoms: list[str], affected_services: list[str]) -> list[dict]:
        """Find matching patterns for the given symptoms."""
        matches = []
        for pattern in self.known_patterns:
            symptom_overlap = len(set(symptoms) & set(pattern["symptoms"]))
            service_overlap = len(set(affected_services) & set(pattern["services_affected"]))

            if symptom_overlap > 0 and service_overlap > 0:
                score = (symptom_overlap / len(pattern["symptoms"]) * 0.6 +
                        service_overlap / len(pattern["services_affected"]) * 0.4)
                matches.append({
                    **pattern,
                    "match_score": round(score * pattern["confidence"], 2),
                })

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)


# Usage
analyzer = RootCauseAnalyzer()
results = analyzer.analyze(
    symptoms=["high_latency", "high_cpu", "increased_errors"],
    affected_services=["api", "database"],
)

for i, result in enumerate(results, 1):
    print(f"\n--- Hypothesis {i} (confidence: {result['match_score']}) ---")
    print(f"Root Cause: {result['root_cause']}")
    print("Remediation Steps:")
    for step in result['remediation']:
        print(f"  - {step}")
```

### Self-Healing Infrastructure

```yaml
# self-healing-kyverno.yaml
# Automatically restart pods that fail health checks repeatedly
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: auto-restart-unhealthy-pods
spec:
  rules:
    - name: restart-crashloopbackoff
      match:
        resources:
          kinds: ["Pod"]
      preconditions:
        all:
          - key: "{{ request.object.status.containerStatuses[0].state.waiting.reason }}"
            operator: Equals
            value: "CrashLoopBackOff"
          - key: "{{ request.object.status.containerStatuses[0].restartCount }}"
            operator: GreaterThan
            value: "5"
      mutate:
        patchStrategicMerge:
          metadata:
            annotations:
              auto-healed: "true"
              auto-healed-at: "{{ time_now() }}"
```

```python
# self_healing_controller.py
"""Self-healing controller for common infrastructure issues."""

import subprocess
import json
from datetime import datetime


class SelfHealingController:
    """Automatically remediate known infrastructure issues."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.actions_taken = []

    def check_and_heal_disk_space(self, threshold_percent: int = 85):
        """Clean up disk space when nodes are running low."""
        # Check node disk usage via Prometheus
        # In production, query Prometheus API
        nodes_with_low_disk = self._get_nodes_with_low_disk(threshold_percent)

        for node in nodes_with_low_disk:
            action = {
                "timestamp": datetime.now().isoformat(),
                "issue": f"Disk usage at {node['usage']}% on {node['name']}",
                "action": "docker system prune + clear old logs",
                "node": node["name"],
            }

            if not self.dry_run:
                # Clean unused Docker images and containers
                subprocess.run([
                    "kubectl", "debug", f"node/{node['name']}",
                    "--image=busybox", "--",
                    "sh", "-c", "docker system prune -f --volumes"
                ])
                action["status"] = "executed"
            else:
                action["status"] = "dry_run"

            self.actions_taken.append(action)
            print(f"[HEAL] {action['issue']} -> {action['action']} ({action['status']})")

    def check_and_heal_certificate_expiry(self, days_threshold: int = 14):
        """Renew certificates expiring within N days."""
        # In production, check cert-manager certificates
        print(f"Checking for certificates expiring within {days_threshold} days...")
        # cert-manager handles this automatically, but we can trigger early renewal

    def report(self):
        """Generate a self-healing report."""
        print(f"\n{'='*50}")
        print(f"Self-Healing Report: {len(self.actions_taken)} actions")
        for action in self.actions_taken:
            print(f"  [{action['status']}] {action['issue']}")


# Run the controller
controller = SelfHealingController(dry_run=True)
controller.check_and_heal_disk_space(threshold_percent=85)
controller.report()
```

---

## Step-by-Step Practical

### Designing an AI-Enhanced Incident Response Workflow

```yaml
# incident-response-workflow.yaml
workflow:
  name: "AI-Enhanced Incident Response"

  step_1_detection:
    trigger: "Anomaly detected by ML model OR static alert fires"
    ai_actions:
      - "Classify severity using historical patterns"
      - "Correlate with other active alerts"
      - "Check if similar incidents occurred recently"
    output: "Enriched alert with context and initial classification"

  step_2_triage:
    trigger: "Alert reaches on-call engineer"
    ai_actions:
      - "Display top 3 probable root causes with confidence scores"
      - "Show relevant runbook sections"
      - "Display recent deployment history"
      - "Show correlated metrics dashboard"
    human_action: "Verify AI assessment, adjust if needed"

  step_3_diagnosis:
    trigger: "Engineer begins investigation"
    ai_actions:
      - "Query logs for relevant error patterns"
      - "Suggest diagnostic commands based on symptoms"
      - "Identify blast radius (affected users, services)"
    human_action: "Run diagnostics, confirm root cause"

  step_4_remediation:
    trigger: "Root cause confirmed"
    ai_actions:
      - "Suggest remediation steps from knowledge base"
      - "Pre-stage rollback if deployment-related"
      - "Auto-scale if capacity-related (with approval)"
    human_action: "Approve and execute remediation"

  step_5_postmortem:
    trigger: "Incident resolved"
    ai_actions:
      - "Generate incident timeline from logs and alerts"
      - "Draft postmortem with root cause and impact"
      - "Suggest preventive measures"
      - "Update knowledge base with new pattern"
    human_action: "Review and finalize postmortem"
```

---

## Exercises

1. **Anomaly Detection**: Implement the anomaly detection script against real Prometheus data (or generate synthetic data). Tune the sensitivity parameter and measure false positive/negative rates.

2. **Root Cause Knowledge Base**: Build a knowledge base of 10 common failure patterns in your environment. Include symptoms, affected services, root causes, and remediation steps. Implement the pattern matching.

3. **Self-Healing Script**: Write a self-healing script that checks for and automatically remediates: pods in CrashLoopBackOff (> 5 restarts), unbound PersistentVolumeClaims, and expired certificates.

4. **Incident Response Workflow**: Design and document an AI-enhanced incident response workflow for your organization. Define what AI does at each step and what requires human approval.

5. **ChatOps Integration**: Design a Slack bot that integrates with your monitoring system. When an alert fires, the bot should: post the alert with context, suggest probable causes, provide relevant runbook links, and allow the on-call engineer to acknowledge and take action.

---

## Knowledge Check

**Q1: How does AI-powered anomaly detection differ from static threshold alerting?**

<details>
<summary>Answer</summary>

Static thresholds use fixed values (alert if CPU > 80%) that do not account for context -- time of day, day of week, seasonal patterns, or gradual trends. AI-powered anomaly detection learns the normal behavior baseline for each metric (using historical data) and alerts when values deviate significantly from what is expected for that specific context. For example, 80% CPU might be normal during nightly batch processing but anomalous at 3 PM. This reduces false positives (alerts for normal behavior) and catches true anomalies that fall below static thresholds (subtle but meaningful deviations).
</details>

**Q2: What is self-healing infrastructure and what are its limits?**

<details>
<summary>Answer</summary>

Self-healing infrastructure automatically detects and remediates known failure patterns without human intervention. Examples: restarting crashed pods, clearing disk space when nodes are full, scaling up when CPU is high, renewing expiring certificates. Limits: (1) it only works for known, predictable failure modes, (2) it cannot handle novel problems or complex multi-service failures, (3) it can mask underlying issues (restarting a crashing pod every 5 minutes instead of fixing the bug), (4) it can make things worse if the remediation is wrong (auto-scaling during a runaway query increases cloud costs without fixing the problem). Self-healing should be limited to low-risk, reversible actions with clear logging.
</details>

**Q3: How should AI-assisted root cause analysis work in practice?**

<details>
<summary>Answer</summary>

AI-assisted RCA should augment, not replace, human investigation: (1) When an incident occurs, AI correlates symptoms across services using a knowledge base of known patterns. (2) It ranks probable root causes by confidence score based on symptom overlap and historical data. (3) It presents the top 3-5 hypotheses to the on-call engineer with supporting evidence and suggested diagnostic commands. (4) The engineer investigates, confirms or rejects each hypothesis. (5) After resolution, the actual root cause is fed back into the knowledge base to improve future accuracy. The key insight is that AI reduces time-to-diagnosis by surfacing relevant patterns, but the final judgment call remains human.
</details>
