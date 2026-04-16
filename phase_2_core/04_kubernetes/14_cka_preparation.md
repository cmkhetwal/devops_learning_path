# Lesson 14: CKA Exam Preparation

## Why This Matters in DevOps

The Certified Kubernetes Administrator (CKA) exam is the industry-standard
certification for Kubernetes operations. It is a hands-on, performance-based exam
-- no multiple choice. You get a live cluster and must complete tasks within a time
limit. Passing the CKA proves you can operate Kubernetes clusters in production.

This lesson focuses on exam strategy, speed techniques, and practice scenarios that
mirror the real exam. Everything here is about doing things FAST and CORRECTLY under
time pressure.

---

## Core Concepts

### Exam Format

| Detail | Value |
|---|---|
| Duration | 2 hours |
| Questions | 15-20 tasks |
| Passing score | 66% |
| Environment | Remote proctored, Linux terminal in browser |
| Kubernetes version | Specified at exam time (typically latest stable) |
| Resources allowed | Official Kubernetes documentation (kubernetes.io/docs) |
| Retake | 1 free retake included |

### Exam Domains and Weights

```
+------------------------------------+--------+
| Domain                             | Weight |
+------------------------------------+--------+
| Cluster Architecture, Installation | 25%    |
|   & Configuration                  |        |
+------------------------------------+--------+
| Workloads & Scheduling             | 15%    |
+------------------------------------+--------+
| Services & Networking              | 20%    |
+------------------------------------+--------+
| Storage                            | 10%    |
+------------------------------------+--------+
| Troubleshooting                    | 30%    |
+------------------------------------+--------+
```

**Troubleshooting is the largest category.** You MUST be able to diagnose and fix
broken clusters, failing pods, and networking issues quickly.

### Time Management Strategy

```
15-20 questions in 120 minutes = ~6-8 minutes per question

Strategy:
  Pass 1 (first 60 minutes):
    - Do all easy/medium questions first
    - Skip anything that takes more than 8 minutes
    - Flag skipped questions

  Pass 2 (remaining 60 minutes):
    - Return to skipped questions
    - Spend more time on high-value questions
    - Partial answers are better than no answers

Point values vary. A 2-point question on creating a simple Pod is
not worth the same time as a 7-point troubleshooting scenario.
```

---

## Step-by-Step Practical

### 1. Essential setup (do this first on exam day)

```bash
# Set up aliases and auto-completion IMMEDIATELY
alias k=kubectl
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deploy'
alias kgn='kubectl get nodes'
alias kga='kubectl get all'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias kaf='kubectl apply -f'

# Enable bash completion
source <(kubectl completion bash)
complete -o default -F __start_kubectl k

# Set your default editor (if you prefer nano over vim)
export EDITOR=vim
# or
export KUBE_EDITOR=vim

# Verify
k get nodes
```

### 2. Context switching (CRITICAL -- do this for every question)

```bash
# The exam gives you multiple clusters. ALWAYS switch context first.
# The context command is provided at the top of each question.

kubectl config use-context <context-name>

# Verify you are in the right cluster
kubectl config current-context
kubectl get nodes

# If the question specifies a namespace:
kubectl config set-context --current --namespace=<namespace>
# or use -n <namespace> on every command
```

### 3. YAML generation tricks (the biggest time saver)

```bash
# Generate Pod YAML
k run nginx --image=nginx:1.25 --dry-run=client -o yaml > pod.yaml

# Generate Pod with port and labels
k run nginx --image=nginx:1.25 --port=80 --labels="app=web,tier=frontend" \
  --dry-run=client -o yaml > pod.yaml

# Generate Deployment YAML
k create deploy web --image=nginx:1.25 --replicas=3 \
  --dry-run=client -o yaml > deploy.yaml

# Generate Service YAML (expose a deployment)
k expose deploy web --port=80 --target-port=80 --type=ClusterIP \
  --dry-run=client -o yaml > svc.yaml

# Generate NodePort Service
k expose deploy web --port=80 --target-port=80 --type=NodePort \
  --dry-run=client -o yaml > nodeport.yaml

# Generate Job YAML
k create job my-job --image=busybox:1.36 \
  --dry-run=client -o yaml -- /bin/sh -c "echo done" > job.yaml

# Generate CronJob YAML
k create cronjob my-cron --image=busybox:1.36 --schedule="*/5 * * * *" \
  --dry-run=client -o yaml -- /bin/sh -c "echo done" > cronjob.yaml

# Generate ConfigMap
k create configmap my-config --from-literal=key1=val1 --from-literal=key2=val2 \
  --dry-run=client -o yaml > cm.yaml

# Generate Secret
k create secret generic my-secret --from-literal=user=admin --from-literal=pass=secret \
  --dry-run=client -o yaml > secret.yaml

# Generate ServiceAccount
k create sa my-sa --dry-run=client -o yaml > sa.yaml

# Generate Role
k create role pod-reader --verb=get,list,watch --resource=pods \
  --dry-run=client -o yaml > role.yaml

# Generate RoleBinding
k create rolebinding read-pods --role=pod-reader --serviceaccount=default:my-sa \
  --dry-run=client -o yaml > rb.yaml

# Generate ClusterRole
k create clusterrole node-reader --verb=get,list --resource=nodes \
  --dry-run=client -o yaml > cr.yaml

# Generate ClusterRoleBinding
k create clusterrolebinding node-rb --clusterrole=node-reader --serviceaccount=default:my-sa \
  --dry-run=client -o yaml > crb.yaml

# Generate Ingress
k create ingress my-ingress --rule="myapp.com/api*=api-svc:80" \
  --dry-run=client -o yaml > ingress.yaml

# Generate Namespace
k create ns dev --dry-run=client -o yaml > ns.yaml

# Generate PVC
# No direct generation, but you can use kubectl explain:
k explain pvc.spec
```

### 4. Vim essentials for the exam

```
# Vim configuration (add to ~/.vimrc)
set number           " Show line numbers
set tabstop=2        " Tab width of 2
set shiftwidth=2     " Indent width of 2
set expandtab        " Use spaces instead of tabs
set autoindent       " Auto indent new lines
set paste            " Prevent auto-indent when pasting

# One-liner to set up vim:
cat <<'EOF' >> ~/.vimrc
set number tabstop=2 shiftwidth=2 expandtab autoindent paste
EOF

# Essential Vim commands:
  i       Enter insert mode
  Esc     Exit insert mode
  :wq     Save and quit
  :q!     Quit without saving
  dd      Delete a line
  yy      Copy a line
  p       Paste below
  u       Undo
  Ctrl+r  Redo
  /text   Search for "text"
  n       Next search result
  :%s/old/new/g   Find and replace all
  :set paste       Fix indentation issues when pasting
  gg      Go to top of file
  G       Go to bottom of file
  5G      Go to line 5
  V       Visual line mode (select lines)
  d       Delete selection
  >       Indent selection
  <       Unindent selection
```

### 5. kubectl explain (your in-exam documentation)

```bash
# Instead of searching kubernetes.io, use kubectl explain
k explain pod.spec
k explain pod.spec.containers
k explain pod.spec.containers.resources
k explain pod.spec.volumes
k explain deployment.spec.strategy
k explain service.spec
k explain ingress.spec.rules
k explain pv.spec
k explain pvc.spec

# Recursive explanation (shows all fields)
k explain pod.spec --recursive | grep -i volume
k explain deployment.spec --recursive | grep -i strategy
```

### 6. Practice Scenario: Create a Deployment and expose it

```bash
# Task: Create a deployment "web" with nginx:1.25, 3 replicas,
# in namespace "production". Expose it as a NodePort service on port 30080.

# Step 1: Create namespace
k create ns production

# Step 2: Create deployment
k create deploy web --image=nginx:1.25 --replicas=3 -n production

# Step 3: Verify
k get deploy web -n production
k get pods -n production

# Step 4: Expose as NodePort
k expose deploy web -n production --port=80 --target-port=80 \
  --type=NodePort --name=web-svc

# Step 5: Set the specific NodePort (need to edit)
k edit svc web-svc -n production
# Change nodePort to 30080

# Or do it in one step:
k expose deploy web -n production --port=80 --target-port=80 \
  --type=NodePort --name=web-svc --dry-run=client -o yaml | \
  sed 's/nodePort: .*/nodePort: 30080/' | k apply -f -

# Verify
k get svc web-svc -n production
```

### 7. Practice Scenario: Troubleshoot a failing Pod

```bash
# Task: A pod named "broken-app" in namespace "debug" is not working. Fix it.

# Step 1: Check the pod status
k get pod broken-app -n debug

# Step 2: Describe the pod
k describe pod broken-app -n debug
# Look at Events section for clues

# Step 3: Check logs
k logs broken-app -n debug
k logs broken-app -n debug --previous

# Common fixes:
# Wrong image -> edit pod (delete and recreate with correct image)
# Missing ConfigMap -> create the ConfigMap
# Missing Secret -> create the Secret
# Wrong command -> fix the command
# Resource limits too low -> increase limits
# Wrong port -> fix the port
```

### 8. Practice Scenario: Create RBAC

```bash
# Task: Create a ServiceAccount "deploy-bot" in namespace "ci-cd".
# Grant it permissions to create, update, and delete deployments
# and services in the "ci-cd" namespace only.

# Step 1: Create namespace and ServiceAccount
k create ns ci-cd
k create sa deploy-bot -n ci-cd

# Step 2: Create Role
k create role deploy-manager -n ci-cd \
  --verb=create,update,delete,get,list \
  --resource=deployments,services

# Step 3: Create RoleBinding
k create rolebinding deploy-bot-binding -n ci-cd \
  --role=deploy-manager \
  --serviceaccount=ci-cd:deploy-bot

# Step 4: Verify
k auth can-i create deployments --as=system:serviceaccount:ci-cd:deploy-bot -n ci-cd
# yes

k auth can-i delete pods --as=system:serviceaccount:ci-cd:deploy-bot -n ci-cd
# no (not granted)

k auth can-i create deployments --as=system:serviceaccount:ci-cd:deploy-bot -n default
# no (only granted in ci-cd namespace)
```

### 9. Practice Scenario: Backup and restore etcd

```bash
# Task: Back up the etcd database and restore it.

# Find etcd pod to get certificate paths
k get pods -n kube-system -l component=etcd
k describe pod etcd-controlplane -n kube-system

# The certificates are usually at:
# --cert-file=/etc/kubernetes/pki/etcd/server.crt
# --key-file=/etc/kubernetes/pki/etcd/server.key
# --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt

# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db --write-table

# Restore etcd (to a new data directory)
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restored \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Update etcd pod manifest to use the new data directory
# Edit /etc/kubernetes/manifests/etcd.yaml
# Change --data-dir to /var/lib/etcd-restored
# Change the hostPath volume to /var/lib/etcd-restored
```

### 10. Practice Scenario: Network Policy

```bash
# Task: Create a NetworkPolicy that allows ingress to pods with label
# app=api only from pods with label app=frontend on port 8080.

cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
EOF

k get netpol
k describe netpol allow-frontend-to-api
```

### 11. Practice Scenario: Persistent Volume

```bash
# Task: Create a PV of 1Gi with ReadWriteOnce access mode using hostPath
# /mnt/data. Create a PVC requesting 500Mi. Deploy a pod that uses it.

cat <<'EOF' | k apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: exam-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /mnt/data
  storageClassName: manual
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: exam-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  storageClassName: manual
---
apiVersion: v1
kind: Pod
metadata:
  name: pv-pod
spec:
  containers:
  - name: app
    image: nginx:1.25
    volumeMounts:
    - name: data
      mountPath: /usr/share/nginx/html
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: exam-pvc
EOF

k get pv,pvc
k get pod pv-pod
```

### 12. Practice Scenario: Scheduling with taints and node affinity

```bash
# Task: Taint node01 with key=spray, value=mortein, effect=NoSchedule.
# Create a pod that tolerates this taint.

# Taint the node
k taint nodes node01 spray=mortein:NoSchedule

# Create a pod with toleration
k run tolerant-pod --image=nginx:1.25 --dry-run=client -o yaml > /tmp/tp.yaml
```

```yaml
# Edit /tmp/tp.yaml to add tolerations:
apiVersion: v1
kind: Pod
metadata:
  name: tolerant-pod
spec:
  tolerations:
  - key: "spray"
    operator: "Equal"
    value: "mortein"
    effect: "NoSchedule"
  containers:
  - name: nginx
    image: nginx:1.25
```

```bash
k apply -f /tmp/tp.yaml
k get pod tolerant-pod -o wide
```

### 13. Quick reference: resource short names

```
pods          = po
services      = svc
deployments   = deploy
replicasets   = rs
statefulsets  = sts
daemonsets    = ds
configmaps    = cm
secrets       = (no short name)
namespaces    = ns
nodes         = no
persistentvolumes       = pv
persistentvolumeclaims  = pvc
serviceaccounts         = sa
ingresses               = ing
networkpolicies         = netpol
storageclasses          = sc
horizontalpodautoscalers = hpa
priorityclasses         = pc
poddisruptionbudgets    = pdb
```

### 14. Quick reference: imperative commands cheat sheet

```bash
# Create resources fast
k run <name> --image=<img>
k create deploy <name> --image=<img> --replicas=<n>
k create ns <name>
k create sa <name>
k create cm <name> --from-literal=<k>=<v>
k create secret generic <name> --from-literal=<k>=<v>
k create role <name> --verb=<v> --resource=<r>
k create rolebinding <name> --role=<r> --serviceaccount=<ns>:<sa>
k create clusterrole <name> --verb=<v> --resource=<r>
k create clusterrolebinding <name> --clusterrole=<cr> --serviceaccount=<ns>:<sa>
k create job <name> --image=<img> -- <cmd>
k create cronjob <name> --image=<img> --schedule="<cron>" -- <cmd>
k create ingress <name> --rule="<host>/<path>=<svc>:<port>"

# Modify resources
k scale deploy <name> --replicas=<n>
k set image deploy/<name> <container>=<img>
k label <resource> <name> <key>=<value>
k annotate <resource> <name> <key>=<value>
k taint nodes <name> <key>=<val>:<effect>
k taint nodes <name> <key>-   # remove taint

# Expose resources
k expose deploy <name> --port=<p> --target-port=<tp> --type=<type>

# Debug resources
k get <resource> -o wide
k describe <resource> <name>
k logs <pod> [-c <container>] [--previous]
k exec -it <pod> -- /bin/sh
k top pods/nodes
k auth can-i <verb> <resource> [--as=<user>]

# Delete resources
k delete <resource> <name> [--force --grace-period=0]
```

---

## Exercises

1. **Speed Drill**: Time yourself creating a Deployment with 3 replicas, exposing
   it as a NodePort Service, and creating an Ingress for it. Target: under 3 minutes.

2. **RBAC from Scratch**: Without looking at the lesson, create a ServiceAccount,
   Role (list and get pods and services), and RoleBinding in a new namespace.
   Verify with `auth can-i`. Target: under 2 minutes.

3. **Troubleshooting Marathon**: Create 5 broken resources (wrong image, missing
   configmap reference, wrong label selector in service, insufficient resources,
   wrong port in readiness probe). Practice diagnosing and fixing each one.

4. **etcd Backup/Restore**: Practice the etcd backup and restore procedure. Find
   the correct certificate paths from the etcd pod spec. Perform a backup and
   verify the snapshot.

5. **Full Mock Exam**: Set a 2-hour timer and attempt the following tasks without
   looking at any lesson. Track your time per task:
   - Create a namespace "exam" with a ResourceQuota (10 pods, 4 CPU, 8Gi memory)
   - Deploy nginx with 3 replicas, resource requests, and a readiness probe
   - Create a CronJob that runs every 5 minutes
   - Create a PV and PVC and mount it in a Pod
   - Create a NetworkPolicy allowing only specific pod labels
   - Create a complete RBAC setup (SA, Role, RoleBinding)
   - Troubleshoot a provided broken deployment
   - Taint a node and create a pod with matching toleration

---

## Knowledge Check

**Q1**: What is the fastest way to generate a Deployment YAML in the exam?
<details>
<summary>Answer</summary>
`kubectl create deployment web --image=nginx:1.25 --replicas=3 --dry-run=client -o yaml > deploy.yaml`.
This generates a complete Deployment manifest without creating it in the cluster.
You can then edit the file to add any additional fields (resources, probes, volumes,
etc.) and apply it with `kubectl apply -f deploy.yaml`.
</details>

**Q2**: You need to switch to a different cluster context. What command do you use?
<details>
<summary>Answer</summary>
`kubectl config use-context <context-name>`. The context name is provided at the
top of each exam question. Always run this FIRST before doing anything else. Verify
with `kubectl config current-context` and `kubectl get nodes` to confirm you are
on the right cluster.
</details>

**Q3**: How do you back up etcd?
<details>
<summary>Answer</summary>
Use `ETCDCTL_API=3 etcdctl snapshot save <backup-file> --endpoints=https://127.0.0.1:2379
--cacert=<ca-cert> --cert=<server-cert> --key=<server-key>`. The certificate paths
can be found by describing the etcd pod: `kubectl describe pod etcd-controlplane
-n kube-system`. Look for the command arguments `--cert-file`, `--key-file`, and
`--trusted-ca-file`.
</details>

**Q4**: A question is taking too long. What should you do?
<details>
<summary>Answer</summary>
Flag it and move on. Return to it in Pass 2. Not all questions are worth the same
points. A 2-point question that takes 15 minutes is a poor use of time. Complete
all easy questions first, then return to difficult ones with remaining time. Partial
credit is possible -- even an incomplete answer is better than no answer.
</details>

**Q5**: How do you quickly find the YAML structure for a specific field?
<details>
<summary>Answer</summary>
Use `kubectl explain`. For example, `kubectl explain pod.spec.volumes` shows all
volume types and their fields. Use `--recursive` to see the full structure:
`kubectl explain deployment.spec --recursive | grep -i strategy`. This is faster
than searching kubernetes.io during the exam.
</details>
