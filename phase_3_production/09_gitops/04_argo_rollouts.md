# Lesson 04: Argo Rollouts

## Why This Matters in DevOps

The standard Kubernetes Deployment resource supports only two strategies: Recreate
(kill all old pods, then start new ones) and RollingUpdate (gradually replace pods).
Neither gives you fine-grained control over traffic shifting, automatic rollback
based on metrics, or the ability to test a new version with a small percentage of
users before committing.

Progressive delivery fills this gap. It acknowledges a hard truth: no amount of
testing in staging eliminates the risk of production. Instead of betting everything
on a single deployment, you gradually shift traffic, observe real production metrics,
and automatically roll back if something goes wrong.

Argo Rollouts extends Kubernetes with advanced deployment strategies — canary,
blue-green, and A/B testing — with built-in analysis that can query Prometheus,
Datadog, or any metrics provider to decide whether a release is safe.

---

## Core Concepts

### Deployment Strategies Compared

```
RECREATE
========
[v1 v1 v1] ---> [--- --- ---] ---> [v2 v2 v2]
  Running          All down            Running
  Downtime: Yes    Risk: High (all-or-nothing)

ROLLING UPDATE (standard K8s)
=============================
[v1 v1 v1] ---> [v1 v1 v2] ---> [v1 v2 v2] ---> [v2 v2 v2]
  Gradual pod replacement.  No downtime.
  Risk: Moderate (limited rollback granularity)

CANARY
======
[v1 v1 v1 v1 v1] ---> [v1 v1 v1 v1 v2]  (10% traffic to v2)
                  ---> [v1 v1 v1 v2 v2]  (20% traffic to v2)
                  ---> analyze metrics...
                  ---> [v2 v2 v2 v2 v2]  (100% traffic to v2)
  Risk: Low (metrics-driven progression)

BLUE-GREEN
==========
[v1 v1 v1] (active)    [v2 v2 v2] (preview)
  Switch traffic instantly:
[v1 v1 v1] (standby)   [v2 v2 v2] (active)
  Risk: Low (instant rollback by switching back)

A/B TESTING
===========
Traffic is routed based on headers, cookies, or user attributes.
  Header: "X-Canary: true" -> v2
  All other traffic -> v1
  Risk: Low (targeted testing with specific users)
```

### Installing Argo Rollouts

```bash
# Install the controller
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f \
  https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install the kubectl plugin
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts

# Verify installation
kubectl argo rollouts version
```

### The Rollout Resource

The Rollout resource replaces the Deployment resource. It has the same pod template
spec but adds a `strategy` section with progressive delivery options:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api-service
  namespace: production
spec:
  replicas: 5
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
        - name: api
          image: acme/api-service:v2.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: { duration: 2m }
        - setWeight: 30
        - pause: { duration: 2m }
        - setWeight: 60
        - pause: { duration: 5m }
        - setWeight: 100
```

### Canary Steps

| Step              | Description                                            |
|-------------------|--------------------------------------------------------|
| `setWeight: N`    | Route N% of traffic to the canary version              |
| `pause: {}`       | Pause indefinitely (requires manual promotion)         |
| `pause: {duration: 5m}` | Pause for 5 minutes, then continue               |
| `analysis`        | Run an AnalysisTemplate to evaluate metrics            |
| `setCanaryScale`  | Set exact replica count for canary (not percentage)    |
| `setHeaderRoute`  | Route traffic based on HTTP headers (A/B testing)      |

### AnalysisTemplates — Automated Metric Evaluation

The real power of Argo Rollouts is automated analysis. Instead of a human watching
dashboards, you define metrics queries that determine whether the canary is healthy:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
  namespace: production
spec:
  args:
    - name: service-name
    - name: threshold
      value: "0.99"    # Default: 99% success rate
  metrics:
    - name: success-rate
      interval: 60s
      count: 5                # Run 5 measurements
      successCondition: "result[0] >= {{args.threshold}}"
      failureLimit: 2         # Allow up to 2 failures before aborting
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"2.."
            }[5m])) /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))
```

Reference the analysis in the Rollout:

```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: { duration: 1m }
      - analysis:
          templates:
            - templateName: success-rate
          args:
            - name: service-name
              value: api-service
      - setWeight: 50
      - pause: { duration: 2m }
      - analysis:
          templates:
            - templateName: success-rate
          args:
            - name: service-name
              value: api-service
            - name: threshold
              value: "0.995"     # Stricter threshold at higher traffic
```

If the analysis fails, Argo Rollouts automatically aborts the rollout and scales
the canary back to zero.

### Blue-Green Deployments

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-frontend
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-frontend
  template:
    metadata:
      labels:
        app: web-frontend
    spec:
      containers:
        - name: web
          image: acme/web-frontend:v2.0.0
          ports:
            - containerPort: 80
  strategy:
    blueGreen:
      activeService: web-frontend-active      # Production traffic
      previewService: web-frontend-preview    # Internal testing
      autoPromotionEnabled: false             # Require manual promotion
      scaleDownDelaySeconds: 300              # Keep old version for 5 min
      prePromotionAnalysis:
        templates:
          - templateName: smoke-tests
      postPromotionAnalysis:
        templates:
          - templateName: success-rate
```

Required Services:

```yaml
# Active service: receives production traffic
apiVersion: v1
kind: Service
metadata:
  name: web-frontend-active
spec:
  selector:
    app: web-frontend
  ports:
    - port: 80
---
# Preview service: internal testing of new version
apiVersion: v1
kind: Service
metadata:
  name: web-frontend-preview
spec:
  selector:
    app: web-frontend
  ports:
    - port: 80
```

The Rollout controller manages which ReplicaSet each Service points to. During a
deployment, the preview service points to the new version while the active service
continues pointing to the old version. After promotion, the active service switches.

---

## Step-by-Step Practical

### Canary Deployment with Automated Analysis

**Step 1: Create the namespace and Prometheus AnalysisTemplate**

```bash
kubectl create namespace canary-demo
```

```yaml
# analysis-template.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: http-success-rate
  namespace: canary-demo
spec:
  args:
    - name: service
  metrics:
    - name: success-rate
      interval: 30s
      count: 3
      successCondition: "result[0] >= 0.95"
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring.svc:9090
          query: |
            sum(rate(
              http_requests_total{service="{{args.service}}",code=~"2.."}[2m]
            )) /
            sum(rate(
              http_requests_total{service="{{args.service}}"}[2m]
            ))
```

```bash
kubectl apply -f analysis-template.yaml
```

**Step 2: Create the Rollout**

```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: canary-demo
  namespace: canary-demo
spec:
  replicas: 4
  selector:
    matchLabels:
      app: canary-demo
  template:
    metadata:
      labels:
        app: canary-demo
    spec:
      containers:
        - name: app
          image: acme/api:v1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
  strategy:
    canary:
      canaryService: canary-demo-canary
      stableService: canary-demo-stable
      steps:
        - setWeight: 20
        - pause: { duration: 30s }
        - analysis:
            templates:
              - templateName: http-success-rate
            args:
              - name: service
                value: canary-demo
        - setWeight: 50
        - pause: { duration: 1m }
        - analysis:
            templates:
              - templateName: http-success-rate
            args:
              - name: service
                value: canary-demo
        - setWeight: 100
```

```yaml
# services.yaml
apiVersion: v1
kind: Service
metadata:
  name: canary-demo-stable
  namespace: canary-demo
spec:
  selector:
    app: canary-demo
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: canary-demo-canary
  namespace: canary-demo
spec:
  selector:
    app: canary-demo
  ports:
    - port: 80
      targetPort: 8080
```

```bash
kubectl apply -f services.yaml
kubectl apply -f rollout.yaml
```

**Step 3: Trigger a canary release**

```bash
# Update the image to trigger a rollout
kubectl argo rollouts set image canary-demo \
  app=acme/api:v2.0.0 -n canary-demo

# Watch the rollout progress in real-time
kubectl argo rollouts get rollout canary-demo \
  -n canary-demo --watch
```

Expected output:

```
Name:            canary-demo
Namespace:       canary-demo
Status:          ॥ Paused
Strategy:        Canary
  Step:          2/7
  SetWeight:     20
  ActualWeight:  20
Images:          acme/api:v1.0.0 (stable)
                 acme/api:v2.0.0 (canary)
Replicas:
  Desired:       4
  Current:       5
  Updated:       1
  Ready:         5
  Available:     5

NAME                                  KIND        STATUS     AGE
rev:2  canary-demo-6f7b8c9d4          ReplicaSet  ● Healthy  30s
  ├──  canary-demo-6f7b8c9d4-k2j9m   Pod         ✔ Running  30s
rev:1  canary-demo-5e6a7b8c3          ReplicaSet  ● Healthy  10m
  ├──  canary-demo-5e6a7b8c3-p3r7t   Pod         ✔ Running  10m
  ├──  canary-demo-5e6a7b8c3-w8m2k   Pod         ✔ Running  10m
  ├──  canary-demo-5e6a7b8c3-x7n4q   Pod         ✔ Running  10m
  └──  canary-demo-5e6a7b8c3-y9o5r   Pod         ✔ Running  10m
```

**Step 4: Observe analysis and progression**

The rollout pauses at each analysis step, queries Prometheus, and proceeds only if
the success rate is above 95%.

**Step 5: Manual abort or promotion**

```bash
# If you need to abort
kubectl argo rollouts abort canary-demo -n canary-demo

# If you need to skip an indefinite pause
kubectl argo rollouts promote canary-demo -n canary-demo

# To see rollout history
kubectl argo rollouts list rollouts -n canary-demo
```

**Step 6: Simulate a failed release**

Deploy a version that returns 500 errors. The analysis will detect the drop in
success rate and automatically abort:

```
Status:          ✖ Degraded
Message:         RolloutAborted: metric "success-rate" assessed Failed
                 due to consecutiveErrors (2) > failureLimit (1)
```

The Rollout controller scales the canary ReplicaSet to zero and routes 100% of
traffic back to the stable version. No human intervention required.

---

## Exercises

### Exercise 1: Basic Canary
Create a Rollout with three canary steps: 25%, 50%, 100%. Use timed pauses (no
analysis). Deploy a new version and watch the progression with
`kubectl argo rollouts get rollout`.

### Exercise 2: Blue-Green with Preview
Set up a blue-green Rollout with active and preview services. Deploy a new version,
verify it is accessible via the preview service, then manually promote. Confirm the
active service switches to the new version.

### Exercise 3: Automated Analysis
Create an AnalysisTemplate that checks a Prometheus metric (or a simple web endpoint
that returns a JSON value). Wire it into a canary Rollout. Deploy a healthy version
and verify the analysis passes. Then deploy a broken version and verify automatic
rollback.

### Exercise 4: Argo Rollouts Dashboard
Install the Argo Rollouts dashboard (`kubectl argo rollouts dashboard`) and use the
web interface to visualize a canary deployment in progress. Compare the experience
with the CLI.

---

## Knowledge Check

### Question 1
What is the key difference between a Kubernetes Deployment and an Argo Rollout?

<details>
<summary>Answer</summary>

A Kubernetes Deployment supports only Recreate and RollingUpdate strategies. An Argo
Rollout extends this with canary, blue-green, and A/B testing strategies, along with
automated analysis (querying metrics providers like Prometheus to decide whether to
proceed or roll back). The Rollout resource replaces the Deployment resource and has
the same pod template spec but adds a `strategy` section.

</details>

### Question 2
What happens when an AnalysisRun fails during a canary deployment?

<details>
<summary>Answer</summary>

When an AnalysisRun fails (the metric exceeds the `failureLimit`), Argo Rollouts
automatically aborts the rollout. The canary ReplicaSet is scaled to zero, and 100%
of traffic is routed back to the stable ReplicaSet. The Rollout status changes to
"Degraded" with a message indicating which metric failed. No manual intervention is
required.

</details>

### Question 3
In a blue-green deployment, what are the two required Services?

<details>
<summary>Answer</summary>

1. **activeService** — Carries production traffic and points to the currently active
   (stable) ReplicaSet.
2. **previewService** — Used for internal testing and points to the new version's
   ReplicaSet before promotion.

After promotion, the active service switches to the new ReplicaSet. The old
ReplicaSet is kept for a configurable period (`scaleDownDelaySeconds`) to allow
quick rollback.

</details>

### Question 4
What is the purpose of `setWeight` in a canary strategy?

<details>
<summary>Answer</summary>

`setWeight` controls what percentage of traffic is routed to the canary version. For
example, `setWeight: 20` sends 20% of traffic to the new version and 80% to the
stable version. This is achieved by adjusting replica counts or (with a service mesh
or ingress controller like Istio/Nginx) by configuring traffic splitting rules. The
weight increases gradually through the steps, allowing operators to observe the new
version under increasing load.

</details>
