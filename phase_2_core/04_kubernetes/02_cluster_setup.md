# Lesson 02: Cluster Setup and kubectl Basics

## Why This Matters in DevOps

You cannot learn Kubernetes from reading alone. You need a cluster to break, fix,
and experiment with. Choosing the right local cluster tool saves hours of frustration.
As a DevOps engineer, you will also manage production clusters, which means
understanding kubeconfig, contexts, and namespaces is not optional -- it is how you
avoid running a destructive command against the wrong cluster at 2 AM.

The CKA exam gives you multiple clusters and expects you to switch between them
rapidly. Mastering `kubectl` context switching is directly tested.

---

## Core Concepts

### Cluster Options for Learning

| Tool | Best For | Nodes | Requirements |
|---|---|---|---|
| **minikube** | CKA prep, single-node | 1 (multi-node possible) | 2 CPU, 2 GB RAM |
| **kind** | CI/CD, multi-node testing | Multi-node in Docker | Docker installed |
| **k3s** | Lightweight, IoT, ARM | Single or multi | 512 MB RAM |
| **Docker Desktop** | Mac/Windows convenience | 1 | Docker Desktop |
| **kubeadm** | Production-like clusters | Multi-node (VMs needed) | Multiple VMs |

**Recommendation for CKA preparation**: Start with minikube for single-node work,
then use kind when you need multi-node scenarios.

### kubeconfig: Your Cluster Passport

```
~/.kube/config
+--------------------------------------------------+
| clusters:                                         |
|   - name: minikube                                |
|     server: https://192.168.49.2:8443             |
|     certificate-authority: /path/to/ca.crt        |
|                                                   |
| users:                                            |
|   - name: minikube-user                           |
|     client-certificate: /path/to/client.crt       |
|     client-key: /path/to/client.key               |
|                                                   |
| contexts:                                         |
|   - name: minikube                                |
|     cluster: minikube                             |
|     user: minikube-user                           |
|     namespace: default                            |
|                                                   |
| current-context: minikube                         |
+--------------------------------------------------+
```

A **context** is a triple of (cluster, user, namespace). It tells kubectl:
- Which cluster to talk to
- Which credentials to use
- Which namespace to default to

### Namespaces: Virtual Clusters

```
+------- Kubernetes Cluster --------+
|                                   |
| +--- default --------+           |
| | (your stuff if you  |           |
| |  don't specify)     |           |
| +---------------------+           |
|                                   |
| +--- kube-system ----+           |
| | (K8s internals:     |           |
| |  coredns, proxy,    |           |
| |  scheduler, etc.)   |           |
| +---------------------+           |
|                                   |
| +--- kube-public ----+           |
| | (readable by all,   |           |
| |  rarely used)       |           |
| +---------------------+           |
|                                   |
| +--- dev -------------+           |
| | (your dev workloads) |           |
| +----------------------+           |
|                                   |
| +--- prod ------------+           |
| | (your prod workloads)|           |
| +----------------------+           |
+-----------------------------------+
```

Namespaces provide:
- **Resource isolation** -- quotas per namespace
- **Access control** -- RBAC can be scoped to a namespace
- **Organization** -- separate teams or environments

Namespaces do NOT provide network isolation by default. Any Pod can talk to any
Pod across namespaces unless NetworkPolicies are applied.

---

## Step-by-Step Practical

### 1. Install minikube

```bash
# Linux (x86_64)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

# macOS (with Homebrew)
brew install minikube

# Windows (with Chocolatey)
choco install minikube
```

### 2. Install kubectl

```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
rm kubectl

# macOS
brew install kubectl

# Verify
kubectl version --client
```

### 3. Start a cluster

```bash
# Start minikube with default settings
minikube start

# Start with specific resources and Kubernetes version
minikube start --cpus=2 --memory=4096 --kubernetes-version=v1.29.0

# Check status
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### 4. Explore kubeconfig

```bash
# View the full kubeconfig
kubectl config view

# See the current context
kubectl config current-context
# Output: minikube

# List all contexts
kubectl config get-contexts
# CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
# *         minikube   minikube   minikube   default

# Switch context (when you have multiple clusters)
kubectl config use-context minikube

# Set a default namespace for the current context
kubectl config set-context --current --namespace=kube-system
# Now all commands default to kube-system

# Reset to default namespace
kubectl config set-context --current --namespace=default
```

### 5. Work with namespaces

```bash
# List all namespaces
kubectl get namespaces
# NAME              STATUS   AGE
# default           Active   5m
# kube-node-lease   Active   5m
# kube-public       Active   5m
# kube-system       Active   5m

# Create a namespace
kubectl create namespace dev

# Create a namespace from YAML
cat <<'EOF' > /tmp/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    environment: staging
EOF
kubectl apply -f /tmp/namespace.yaml

# Run a command in a specific namespace
kubectl get pods -n kube-system

# Run a command across ALL namespaces
kubectl get pods -A
# or
kubectl get pods --all-namespaces
```

### 6. Cluster health checks

```bash
# Cluster info
kubectl cluster-info

# Component statuses (deprecated but still useful)
kubectl get componentstatuses
# or
kubectl get cs

# Check node status
kubectl get nodes
kubectl get nodes -o wide  # more detail: IPs, OS, container runtime

# Describe a node for full details
kubectl describe node minikube

# Check all system pods are running
kubectl get pods -n kube-system

# Check API server health directly
kubectl get --raw='/healthz'
# ok

# Check readiness of specific components
kubectl get --raw='/readyz'
```

### 7. kubectl output formats

```bash
# Default table output
kubectl get pods

# Wide output (more columns)
kubectl get pods -o wide

# YAML output (full object)
kubectl get pod <name> -o yaml

# JSON output
kubectl get pod <name> -o json

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# JSONPath (extract specific fields)
kubectl get nodes -o jsonpath='{.items[*].metadata.name}'

# Sort by a field
kubectl get pods --sort-by=.metadata.creationTimestamp
```

### 8. kubectl shortcuts and efficiency

```bash
# Tab completion (add to .bashrc or .zshrc)
source <(kubectl completion bash)
# For zsh:
source <(kubectl completion zsh)

# Alias (almost everyone uses this)
alias k=kubectl
complete -o default -F __start_kubectl k

# Short resource names
kubectl get po        # pods
kubectl get svc       # services
kubectl get deploy    # deployments
kubectl get ns        # namespaces
kubectl get no        # nodes
kubectl get cm        # configmaps
kubectl get pv        # persistentvolumes
kubectl get pvc       # persistentvolumeclaims
kubectl get sa        # serviceaccounts
kubectl get ing       # ingresses
kubectl get ds        # daemonsets
kubectl get sts       # statefulsets
kubectl get rs        # replicasets

# Dry run to preview what would be created
kubectl run test --image=nginx --dry-run=client -o yaml
```

### 9. Alternative setup: kind

```bash
# Install kind
# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create a simple cluster
kind create cluster --name my-cluster

# Create a multi-node cluster
cat <<'EOF' > /tmp/kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF
kind create cluster --config /tmp/kind-config.yaml --name multi-node

# List clusters
kind get clusters

# Delete a cluster
kind delete cluster --name my-cluster
```

---

## Exercises

1. **Install and Start**: Install minikube and kubectl on your machine. Start a
   cluster and verify all system pods are in the Running state.

2. **Namespace Management**: Create three namespaces: `dev`, `staging`, and `prod`.
   Set your default namespace to `dev`. Run `kubectl get pods` and confirm it shows
   pods from the `dev` namespace (should be empty). Switch back to `default`.

3. **kubeconfig Exploration**: Run `kubectl config view` and identify the three
   main sections (clusters, users, contexts). If you have access to a second
   cluster, add it and practice switching contexts.

4. **Output Formats**: Deploy a test pod (`kubectl run test --image=nginx`), then
   view it in default, wide, YAML, and JSON formats. Use JSONPath to extract just
   the pod's IP address. Clean up the pod when done.

5. **kind Multi-Node**: Install kind and create a 3-node cluster (1 control plane,
   2 workers). Run `kubectl get nodes` to see all three. Compare the experience
   with minikube.

---

## Knowledge Check

**Q1**: What is a kubeconfig context and why does it matter?
<details>
<summary>Answer</summary>
A context is a combination of a cluster, a user, and a default namespace. It allows
you to quickly switch between different clusters and environments. This matters
because in real work you will have dev, staging, and production clusters, and you
need to ensure your commands target the right one. The CKA exam also requires
switching between multiple cluster contexts.
</details>

**Q2**: What is the difference between `kubectl get pods` and `kubectl get pods -A`?
<details>
<summary>Answer</summary>
`kubectl get pods` shows pods in the current namespace only (default if not
changed). `kubectl get pods -A` (or `--all-namespaces`) shows pods across every
namespace in the cluster. This is useful for seeing system pods in kube-system
alongside your application pods.
</details>

**Q3**: Which namespaces exist in a fresh Kubernetes cluster?
<details>
<summary>Answer</summary>
Four namespaces: `default` (where your resources go by default), `kube-system`
(for Kubernetes internal components), `kube-public` (readable by all users,
rarely used), and `kube-node-lease` (holds Lease objects for node heartbeats).
</details>

**Q4**: How do you check if all control plane components are healthy?
<details>
<summary>Answer</summary>
Multiple approaches: `kubectl get pods -n kube-system` to see if all system pods
are Running, `kubectl get componentstatuses` for a quick overview, `kubectl get
nodes` to check node readiness, or `kubectl get --raw='/healthz'` and
`kubectl get --raw='/readyz'` to check the API server health endpoints directly.
</details>

**Q5**: What is the `--dry-run=client -o yaml` pattern used for?
<details>
<summary>Answer</summary>
It generates a YAML manifest without actually creating the resource. This is
extremely valuable for the CKA exam because you can quickly scaffold a YAML file
with the correct structure, then edit it as needed instead of writing YAML from
scratch. Example: `kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml`
</details>
