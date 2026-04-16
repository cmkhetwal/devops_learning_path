# MCP and AI Agents in DevOps

## Why This Matters in DevOps

AI agents represent the next frontier of DevOps automation. Instead of AI that generates code you must copy-paste, AI agents can directly interact with your tools -- querying Prometheus, creating Jira tickets, triggering deployments, and investigating incidents. The Model Context Protocol (MCP) standardizes how AI models connect to external tools and data sources. Understanding these concepts positions you to build and leverage the next generation of DevOps automation where AI assistants actively participate in operations.

---

## Core Concepts

### Model Context Protocol (MCP) Explained

MCP is an open protocol (created by Anthropic) that standardizes how AI models connect to external data sources and tools. Think of it as a USB-C port for AI -- a universal interface that lets any AI model work with any tool.

```
Without MCP:                      With MCP:
────────────                      ────────
Each AI tool needs               One standard protocol
custom integrations              for all integrations

AI ──custom──► Prometheus        AI ──MCP──► MCP Server ──► Prometheus
AI ──custom──► Kubernetes        AI ──MCP──► MCP Server ──► Kubernetes
AI ──custom──► GitHub            AI ──MCP──► MCP Server ──► GitHub
AI ──custom──► Jira              AI ──MCP──► MCP Server ──► Jira

N AI tools × M integrations      N AI tools × 1 protocol
= N×M custom integrations        = N+M integrations
```

```
MCP Architecture:
─────────────────

┌──────────────────┐     MCP Protocol     ┌──────────────────┐
│                  │ ◄──────────────────► │                  │
│   MCP Client     │    (JSON-RPC over    │   MCP Server     │
│   (AI Model)     │     stdio/SSE)       │   (Tool Bridge)  │
│                  │                      │                  │
│   Claude         │                      │   Prometheus     │
│   GPT            │                      │   Kubernetes     │
│   Local LLM      │                      │   GitHub         │
│                  │                      │   Custom tools   │
└──────────────────┘                      └──────────────────┘

MCP Server exposes:
  - Tools: Functions the AI can call (query_metrics, create_issue)
  - Resources: Data the AI can read (dashboards, configs)
  - Prompts: Pre-built prompt templates for common tasks
```

### What Are AI Agents in DevOps?

An AI agent is a system that uses AI to autonomously plan and execute multi-step tasks, using tools and APIs to interact with the real world.

```
Traditional Script:              AI Agent:
───────────────────              ─────────
Predefined steps                 Dynamic planning
"If X, then Y"                   "Given this situation,
                                  what should I do?"

Fixed logic                      Adaptive reasoning
Breaks on unexpected input       Handles novel situations
No learning                      Learns from outcomes

Example:                         Example:
if cpu > 80:                     "CPU is high on orders-service.
  scale_up()                      Looking at recent deployments...
                                  A new version was deployed 10m ago.
                                  The previous version had normal CPU.
                                  Recommendation: rollback to v2.3.1
                                  and investigate memory leak in v2.4.0"
```

### Agent Frameworks

```
Framework      Language    Best For                    Complexity
─────────────────────────────────────────────────────────────────
LangGraph      Python      Complex multi-step agents   High
CrewAI         Python      Multi-agent collaboration   Medium
AutoGen        Python      Code generation agents      Medium
Semantic Kernel .NET/Python Enterprise AI agents       High
Custom (API)   Any         Simple, focused agents      Low
```

### Building DevOps Agents

A DevOps agent connects AI reasoning to operational tools:

```python
# devops_agent.py
"""Conceptual DevOps agent using tool-calling pattern."""

import json
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict

    def execute(self, **kwargs) -> str:
        """Execute the tool (stub for demonstration)."""
        raise NotImplementedError


class PrometheusQueryTool(Tool):
    def __init__(self):
        super().__init__(
            name="query_prometheus",
            description="Query Prometheus for current metric values",
            parameters={
                "query": {"type": "string", "description": "PromQL query"},
                "time_range": {"type": "string", "description": "Time range (e.g., 1h, 24h)"},
            },
        )

    def execute(self, query: str, time_range: str = "1h") -> str:
        # In production: requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        return json.dumps({
            "status": "success",
            "data": {"result": [{"metric": {"service": "orders-api"}, "value": [1713200000, "85.2"]}]},
        })


class KubectlTool(Tool):
    def __init__(self):
        super().__init__(
            name="kubectl",
            description="Execute kubectl commands on the Kubernetes cluster",
            parameters={
                "command": {"type": "string", "description": "kubectl command (e.g., 'get pods -n orders')"},
            },
        )

    def execute(self, command: str) -> str:
        # In production: subprocess.run(["kubectl"] + command.split(), capture_output=True)
        return "NAME                         READY   STATUS    RESTARTS   AGE\norders-api-6b5f7d8c9f-abc   1/1     Running   3          2h"


class ArgocdTool(Tool):
    def __init__(self):
        super().__init__(
            name="argocd_rollback",
            description="Rollback an ArgoCD application to a previous version",
            parameters={
                "app_name": {"type": "string"},
                "revision": {"type": "string", "description": "Git revision to rollback to"},
            },
        )

    def execute(self, app_name: str, revision: str) -> str:
        return f"Application {app_name} rolled back to revision {revision}"


class PagerDutyTool(Tool):
    def __init__(self):
        super().__init__(
            name="create_incident",
            description="Create or update a PagerDuty incident",
            parameters={
                "title": {"type": "string"},
                "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                "description": {"type": "string"},
            },
        )

    def execute(self, title: str, severity: str, description: str) -> str:
        return f"Incident created: [{severity}] {title}"


class DevOpsAgent:
    """Agent that reasons about infrastructure issues and takes action."""

    def __init__(self):
        self.tools = {
            "query_prometheus": PrometheusQueryTool(),
            "kubectl": KubectlTool(),
            "argocd_rollback": ArgocdTool(),
            "create_incident": PagerDutyTool(),
        }
        self.action_log = []

    def available_tools_description(self) -> str:
        """Generate tool descriptions for the AI model."""
        return "\n".join(
            f"- {t.name}: {t.description} (params: {list(t.parameters.keys())})"
            for t in self.tools.values()
        )

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool and log the action."""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Unknown tool {tool_name}"

        result = tool.execute(**kwargs)
        self.action_log.append({
            "tool": tool_name,
            "params": kwargs,
            "result": result,
        })
        return result

    def investigate_incident(self, alert: dict) -> dict:
        """
        Simulated agent investigation flow.
        In production, this would use an LLM to reason about each step.
        """
        investigation = {"alert": alert, "steps": [], "recommendation": None}

        # Step 1: Check metrics
        metrics = self.execute_tool(
            "query_prometheus",
            query=f'rate(http_requests_total{{service="{alert["service"]}", status="5xx"}}[5m])',
        )
        investigation["steps"].append({"action": "query_metrics", "result": metrics})

        # Step 2: Check pods
        pods = self.execute_tool(
            "kubectl",
            command=f"get pods -n {alert['namespace']} -l app={alert['service']}",
        )
        investigation["steps"].append({"action": "check_pods", "result": pods})

        # Step 3: Check recent deployments
        deploys = self.execute_tool(
            "kubectl",
            command=f"get events -n {alert['namespace']} --field-selector reason=Started",
        )
        investigation["steps"].append({"action": "check_deployments", "result": deploys})

        # Step 4: Recommend action
        # In production, LLM would analyze all gathered data and reason about next steps
        investigation["recommendation"] = {
            "action": "rollback",
            "confidence": 0.85,
            "reason": "High error rate started after recent deployment. 3 pod restarts detected.",
            "requires_approval": True,
        }

        return investigation


# Usage
agent = DevOpsAgent()

investigation = agent.investigate_incident({
    "service": "orders-api",
    "namespace": "orders",
    "alert": "High 5xx Error Rate",
    "severity": "P2",
})

print(f"Alert: {investigation['alert']['alert']}")
print(f"Steps taken: {len(investigation['steps'])}")
print(f"Recommendation: {investigation['recommendation']['action']}")
print(f"Confidence: {investigation['recommendation']['confidence']}")
print(f"Requires approval: {investigation['recommendation']['requires_approval']}")
```

### CloudBees MCP for Software Delivery

CloudBees has implemented MCP servers for software delivery, allowing AI assistants to interact with CI/CD pipelines, deployment status, and feature flags.

```
MCP Server capabilities:
├── query_pipeline_status(pipeline_id) → current status, logs
├── list_recent_deployments(service) → deployment history
├── get_feature_flags(environment) → active flags
├── trigger_deployment(service, version, env) → deploy (with approval)
└── rollback_deployment(service, env) → rollback to previous
```

---

## Step-by-Step Practical

### Conceptual Design of a DevOps Agent

**Step 1: Define the Agent's Capabilities**

```yaml
# agent-design.yaml
agent:
  name: "DevOps Copilot"
  purpose: "Assist on-call engineers with incident detection, investigation, and remediation"

  tools:
    monitoring:
      - name: "query_prometheus"
        description: "Query metrics using PromQL"
        risk: "none (read-only)"
      - name: "query_loki"
        description: "Search logs using LogQL"
        risk: "none (read-only)"
      - name: "get_traces"
        description: "Retrieve distributed traces from Tempo"
        risk: "none (read-only)"

    kubernetes:
      - name: "kubectl_get"
        description: "Get Kubernetes resource status"
        risk: "none (read-only)"
      - name: "kubectl_describe"
        description: "Describe Kubernetes resources"
        risk: "none (read-only)"
      - name: "kubectl_scale"
        description: "Scale a deployment"
        risk: "medium (requires approval)"
      - name: "kubectl_rollout_restart"
        description: "Restart a deployment"
        risk: "medium (requires approval)"

    deployment:
      - name: "argocd_status"
        description: "Check ArgoCD application status"
        risk: "none (read-only)"
      - name: "argocd_rollback"
        description: "Rollback to previous version"
        risk: "high (requires approval)"

    communication:
      - name: "slack_notify"
        description: "Send message to Slack channel"
        risk: "low"
      - name: "pagerduty_create"
        description: "Create PagerDuty incident"
        risk: "low"
      - name: "jira_create"
        description: "Create Jira ticket"
        risk: "low"

  approval_policy:
    no_approval_needed:
      - read-only queries
      - sending notifications
      - creating tickets
    requires_approval:
      - scaling deployments
      - restarting pods
      - rollbacks
    never_automated:
      - deleting resources
      - modifying security policies
      - database operations
```

**Step 2: Design the Agent Workflow**

```
Agent Workflow: Incident Investigation
──────────────────────────────────────

1. Alert received → Agent activated
   │
2. Agent gathers context (autonomous, no approval needed)
   ├── Query Prometheus for relevant metrics
   ├── Query Loki for error logs
   ├── Check Kubernetes pod status
   ├── Check ArgoCD deployment history
   └── Check PagerDuty for related incidents
   │
3. Agent analyzes and generates report
   ├── Root cause hypothesis (with confidence)
   ├── Impact assessment (affected users, services)
   ├── Similar past incidents
   └── Recommended remediation
   │
4. Agent presents to engineer (human-in-the-loop)
   ├── "I found high error rates correlating with deployment v2.4.0"
   ├── "Recommend: rollback to v2.3.1"
   └── "Shall I proceed with rollback? [Approve/Reject]"
   │
5. Engineer approves → Agent executes
   ├── Triggers ArgoCD rollback
   ├── Monitors rollback progress
   ├── Verifies error rates decrease
   └── Updates PagerDuty incident
```

---

## Exercises

1. **MCP Server Design**: Design an MCP server for your primary monitoring tool (Prometheus, Datadog, or similar). Define 5 tools the server would expose, their parameters, and return types.

2. **Agent Tool Kit**: Define the complete set of tools a DevOps agent would need for your environment. Categorize each as: read-only (no approval), write (approval needed), and dangerous (never automated).

3. **Investigation Workflow**: Build a Python script that simulates an agent investigating an incident by calling multiple tool APIs in sequence. Use mock data to demonstrate the investigation flow.

4. **Approval System Design**: Design a Slack-based approval system for agent actions. When the agent wants to take a destructive action, it posts to Slack with an "Approve" button. Only on-call engineers can approve.

5. **Agent Evaluation**: Design a test suite for evaluating agent accuracy. Create 10 incident scenarios with known root causes. Run the agent against each and measure: correct diagnosis rate, time to diagnosis, and false positive rate.

---

## Knowledge Check

**Q1: What is MCP and why does it matter for DevOps?**

<details>
<summary>Answer</summary>

MCP (Model Context Protocol) is a standardized protocol for connecting AI models to external tools and data sources. It matters for DevOps because it enables AI assistants to directly interact with DevOps tools (Prometheus, Kubernetes, ArgoCD, PagerDuty) through a universal interface. Without MCP, each AI tool needs custom integrations with each DevOps tool (N*M problem). With MCP, you build one MCP server per tool, and any MCP-compatible AI can use it (N+M problem). This standardization accelerates the adoption of AI agents in DevOps by reducing integration effort.
</details>

**Q2: What is the difference between an AI agent and a traditional automation script?**

<details>
<summary>Answer</summary>

A traditional automation script follows predefined logic: if condition A, then action B. It breaks when encountering unexpected situations. An AI agent uses reasoning to dynamically plan actions based on context. Given the same alert, an agent might: query metrics, check logs, review recent deployments, correlate with other incidents, and then reason about the most likely root cause. It can handle novel situations by combining information from multiple sources and applying learned patterns. However, agents are also less predictable -- they might take different paths for similar situations, and their reasoning can be wrong. This is why the human-in-the-loop principle is critical.
</details>

**Q3: How should you handle the approval workflow for AI agent actions?**

<details>
<summary>Answer</summary>

Categorize actions into three tiers: (1) **No approval needed** -- read-only operations (querying metrics, reading logs, checking pod status) and informational actions (sending notifications, creating tickets). (2) **Requires approval** -- state-changing operations (scaling deployments, restarting pods, triggering rollbacks). The agent proposes the action with its reasoning, and a human (on-call engineer) approves or rejects via Slack, a web UI, or ChatOps. Include a timeout (default to no-action if not approved within N minutes). (3) **Never automated** -- destructive operations (deleting data, modifying security policies, database schema changes). These should never be automated regardless of approval because the consequences of errors are too severe.
</details>
