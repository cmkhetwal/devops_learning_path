# Lesson 02: ArgoCD Fundamentals

## Why This Matters in DevOps

Knowing the philosophy of GitOps is step one. Implementing it requires an agent
that watches Git, compares desired state to actual state, and reconciles differences.
ArgoCD is the dominant GitOps operator for Kubernetes, a CNCF graduated project
with over 18,000 GitHub stars, used by companies including Intuit, Tesla, Red Hat,
and the US Department of Defense.

ArgoCD transforms abstract GitOps principles into a concrete, production-grade
system. It provides a web UI for visualizing application state, a CLI for
automation, SSO integration for enterprise authentication, RBAC for multi-team
environments, and webhook support for near-instant sync. Learning ArgoCD is not
optional for modern Kubernetes operations — it is the industry standard.

---

## Core Concepts

### What Is ArgoCD?

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It
continuously monitors Git repositories and compares the desired application state
(defined in Git) with the actual state (running in the cluster). When differences
are detected, ArgoCD can either alert the operator or automatically synchronize the
cluster to match Git.

ArgoCD supports multiple configuration management tools out of the box:
- Plain Kubernetes YAML manifests
- Helm charts
- Kustomize overlays
- Jsonnet
- Custom plugins (for tools like cdk8s or Tanka)

### Architecture

ArgoCD runs as a set of Kubernetes controllers in the `argocd` namespace:

```
+------------------------------------------------------------------+
|                         ArgoCD Architecture                       |
+------------------------------------------------------------------+
|                                                                    |
|  +-----------------+     +------------------+                      |
|  |   API Server    |<--->|     Redis         |                     |
|  | (gRPC + REST)   |     | (cache + state)   |                     |
|  +-----------------+     +------------------+                      |
|         ^                                                          |
|         |  serves UI + CLI                                         |
|         v                                                          |
|  +-----------------+     +------------------+                      |
|  |   Repo Server   |     |   App Controller  |                     |
|  | (renders manifests)   | (reconciliation   |                     |
|  |  from Git/Helm/   |   |  loop, health     |                     |
|  |  Kustomize)       |   |  checks, sync)    |                     |
|  +-----------------+     +------------------+                      |
|         |                        |                                 |
|         v                        v                                 |
|  +-------------+         +-------------+                           |
|  |  Git Repos  |         |  K8s Cluster |                          |
|  +-------------+         +-------------+                           |
+------------------------------------------------------------------+
```

**API Server**: Exposes the gRPC and REST API consumed by the web UI, CLI, and CI
systems. Handles authentication and RBAC enforcement.

**Repo Server**: Clones Git repositories, renders manifests (runs `helm template`,
`kustomize build`, etc.), and caches the results. This component never touches the
cluster directly.

**Application Controller**: The heart of ArgoCD. Runs the reconciliation loop every
3 minutes (configurable). Compares rendered manifests from the Repo Server with live
cluster state. Applies changes when sync is triggered.

**Redis**: In-memory cache for application state, manifest caching, and UI session
data. Reduces load on the Repo Server and API Server.

**Dex (optional)**: An OpenID Connect provider for SSO integration with LDAP,
GitHub, SAML, etc.

### Installing ArgoCD on Kubernetes

#### Option A: kubectl (quick start)

```bash
# Create the namespace
kubectl create namespace argocd

# Install ArgoCD (stable release)
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Verify all pods are running
kubectl get pods -n argocd
```

Expected output:

```
NAME                                  READY   STATUS    RESTARTS   AGE
argocd-application-controller-0       1/1     Running   0          2m
argocd-dex-server-5f8d6c5db4-k2j9m   1/1     Running   0          2m
argocd-redis-74cb89f67b-x7n4q         1/1     Running   0          2m
argocd-repo-server-6b7f5d9c8-p3r7t    1/1     Running   0          2m
argocd-server-7f8b9c6d4-w8m2k         1/1     Running   0          2m
```

#### Option B: Helm (production)

```bash
# Add the ArgoCD Helm repository
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Install with custom values
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --set server.service.type=LoadBalancer \
  --set server.extraArgs="{--insecure}" \
  --set controller.metrics.enabled=true \
  --set repoServer.resources.requests.cpu=250m \
  --set repoServer.resources.requests.memory=256Mi
```

### Accessing the UI

```bash
# Port-forward the API server
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
echo  # newline after password

# Open https://localhost:8080 in your browser
# Username: admin
# Password: (from above command)
```

### The ArgoCD CLI

```bash
# Install the CLI
curl -sSL -o argocd \
  https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd
sudo mv argocd /usr/local/bin/

# Log in
argocd login localhost:8080 --username admin --password <password> --insecure

# Change the admin password
argocd account update-password

# List applications
argocd app list

# Get cluster info
argocd cluster list
```

### Sync Status

ArgoCD tracks two key statuses for every application:

#### Sync Status

| Status      | Meaning                                                  |
|-------------|----------------------------------------------------------|
| `Synced`    | Live state matches desired state in Git                  |
| `OutOfSync` | Live state differs from desired state in Git             |
| `Unknown`   | ArgoCD cannot determine the state (e.g., repo unreachable)|

#### Health Status

| Status       | Meaning                                                 |
|--------------|----------------------------------------------------------|
| `Healthy`    | All resources are running and passing health checks      |
| `Progressing`| Resources are being updated (e.g., rollout in progress)  |
| `Degraded`   | One or more resources are failing health checks          |
| `Suspended`  | Resource is paused (e.g., scaled to 0 or suspended job)  |
| `Missing`    | Resource exists in Git but not in the cluster            |
| `Unknown`    | Health cannot be determined                              |

The ideal state is **Synced + Healthy**. An application that is `OutOfSync` and
`Degraded` needs immediate attention.

---

## Step-by-Step Practical

### Creating Your First ArgoCD Application

**Step 1: Prepare a Git repository with Kubernetes manifests**

Create a public Git repo (or use an existing one) with a simple application:

```
my-app-config/
  namespace.yaml
  deployment.yaml
  service.yaml
```

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: demo-app
```

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: demo-app
  labels:
    app: demo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:0.2.3
          args:
            - "-text=Hello from GitOps!"
          ports:
            - containerPort: 5678
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 64Mi
```

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-app
  namespace: demo-app
spec:
  selector:
    app: demo-app
  ports:
    - port: 80
      targetPort: 5678
  type: ClusterIP
```

**Step 2: Create the Application via CLI**

```bash
argocd app create demo-app \
  --repo https://github.com/your-org/my-app-config.git \
  --path . \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace demo-app \
  --sync-policy none \
  --project default

# Check the application status
argocd app get demo-app
```

Expected output:

```
Name:               argocd/demo-app
Project:            default
Server:             https://kubernetes.default.svc
Namespace:          demo-app
URL:                https://localhost:8080/applications/demo-app
Repo:               https://github.com/your-org/my-app-config.git
Path:               .
SyncWindow:         Sync Allowed
Sync Policy:        <none>
Sync Status:        OutOfSync
Health Status:      Missing
```

**Step 3: Create the Application via YAML (preferred for GitOps)**

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: demo-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/my-app-config.git
    targetRevision: HEAD
    path: .
  destination:
    server: https://kubernetes.default.svc
    namespace: demo-app
  syncPolicy:
    automated:
      prune: false
      selfHeal: false
```

```bash
kubectl apply -f argocd-application.yaml
```

**Step 4: Sync the application**

```bash
# Manual sync
argocd app sync demo-app

# Watch the sync progress
argocd app wait demo-app --health --timeout 120
```

Expected output:

```
TIMESTAMP   GROUP  KIND        NAMESPACE  NAME      STATUS   HEALTH   HOOK  MESSAGE
2024-01-15  v1     Namespace              demo-app  Synced
2024-01-15  apps   Deployment  demo-app   demo-app  Synced   Healthy
2024-01-15  v1     Service     demo-app   demo-app  Synced   Healthy

Name:               argocd/demo-app
Sync Status:        Synced
Health Status:      Healthy
```

**Step 5: Verify in the cluster**

```bash
kubectl get all -n demo-app
```

```
NAME                            READY   STATUS    RESTARTS   AGE
pod/demo-app-7f8b9c6d4-k2j9m   1/1     Running   0          30s
pod/demo-app-7f8b9c6d4-p3r7t   1/1     Running   0          30s

NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/demo-app   ClusterIP   10.96.123.45    <none>        80/TCP    30s

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/demo-app   2/2     2            2           30s
```

**Step 6: Make a change in Git and observe**

Update the replica count in `deployment.yaml` from 2 to 4, commit, and push.
Within 3 minutes (or instantly with a webhook), ArgoCD detects the change.

```bash
# Check status
argocd app get demo-app
# Sync Status: OutOfSync

# Sync
argocd app sync demo-app
# The deployment scales to 4 replicas
```

---

## Exercises

### Exercise 1: Install ArgoCD
Install ArgoCD on a local Kubernetes cluster (minikube, kind, or k3d). Access the
UI, log in, and explore the interface. Take note of the Settings section where you
configure repositories and clusters.

### Exercise 2: Deploy via CLI and YAML
Create the same application twice — once using `argocd app create` and once using a
YAML manifest applied with `kubectl apply`. Compare the experience and discuss which
approach is more "GitOps-native."

### Exercise 3: Trigger an OutOfSync Event
After syncing your application, manually run `kubectl scale deployment demo-app
--replicas=10 -n demo-app`. Observe ArgoCD's sync status change to OutOfSync. Note
that without auto-sync, ArgoCD reports but does not fix the drift.

### Exercise 4: Explore the UI
Navigate the ArgoCD UI and find: (a) the resource tree for your application, (b) the
diff view showing desired vs live state, (c) the sync history, and (d) the logs for
a specific pod.

---

## Knowledge Check

### Question 1
What are the four main components of ArgoCD's architecture?

<details>
<summary>Answer</summary>

1. **API Server** — Serves the gRPC/REST API for the UI and CLI, handles auth/RBAC.
2. **Repo Server** — Clones Git repos and renders manifests (Helm, Kustomize, etc.).
3. **Application Controller** — Runs the reconciliation loop, compares desired vs
   live state, triggers syncs.
4. **Redis** — In-memory cache for state, manifests, and sessions.

</details>

### Question 2
What is the difference between Sync Status and Health Status?

<details>
<summary>Answer</summary>

**Sync Status** indicates whether the live cluster state matches the desired state
in Git. Values: Synced, OutOfSync, Unknown.

**Health Status** indicates whether the running resources are functioning correctly.
Values: Healthy, Progressing, Degraded, Suspended, Missing, Unknown.

An application can be `Synced` but `Degraded` (the correct manifests are applied but
pods are crash-looping). It can also be `OutOfSync` but `Healthy` (the live state
differs from Git but everything is running fine).

</details>

### Question 3
Why is defining an ArgoCD Application as a YAML manifest preferred over using the CLI?

<details>
<summary>Answer</summary>

Defining the Application as YAML and storing it in Git follows GitOps principles:
the Application definition itself is declarative, versioned, and auditable. Using
the CLI is imperative — there is no record of the `argocd app create` command in
version control, no review process, and no easy way to recreate it if the ArgoCD
instance is lost. YAML manifests can also be managed by a parent Application
(app-of-apps pattern).

</details>

### Question 4
How often does ArgoCD poll Git repositories by default, and how can this be improved?

<details>
<summary>Answer</summary>

By default ArgoCD polls Git repositories every **3 minutes**. This can be improved
by configuring **webhooks** in your Git provider (GitHub, GitLab, Bitbucket) to
notify ArgoCD immediately when a push occurs, reducing sync latency to seconds.

</details>
