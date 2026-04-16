# Lesson 10: RBAC and Security

## Why This Matters in DevOps

A Kubernetes cluster without proper access control is a security incident waiting
to happen. Any Pod can talk to the API server. Any user can delete any resource.
Any container can run as root. RBAC (Role-Based Access Control) and security
policies are the guardrails that prevent mistakes and contain breaches.

As a DevOps engineer, you will set up RBAC for teams, configure ServiceAccounts
for applications, and enforce Pod security standards. The principle of least
privilege is not optional -- it is the foundation of cluster security.

The CKA exam tests RBAC creation (Roles, ClusterRoles, RoleBindings), ServiceAccount
management, and SecurityContext configuration.

---

## Core Concepts

### Authentication vs Authorization

```
User/Pod makes a request to the API server:

Step 1: AUTHENTICATION (who are you?)
  +--- Methods ---+
  | Certificates  |
  | Tokens        |
  | OIDC          |
  | ServiceAccount|
  +--------------+
         |
         v
Step 2: AUTHORIZATION (what can you do?)
  +--- Methods ---+
  | RBAC          |  <-- Most common
  | ABAC          |
  | Webhook       |
  | Node          |
  +--------------+
         |
         v
Step 3: ADMISSION CONTROL (is this request valid/allowed?)
  +--- Controllers -----+
  | ResourceQuota        |
  | LimitRanger          |
  | PodSecurity          |
  | MutatingWebhook      |
  | ValidatingWebhook    |
  +----------------------+
         |
         v
    Request processed
```

### RBAC Model

```
+--- Role/ClusterRole ---+      +--- RoleBinding/ClusterRoleBinding ---+
| WHAT actions on WHICH  |      | WHO gets the Role                    |
| resources?             |      |                                      |
|                        | <--- | Connects Role to Subject:            |
| rules:                 |      |   - User                             |
| - resources: [pods]    |      |   - Group                            |
|   verbs: [get, list]   |      |   - ServiceAccount                   |
+------------------------+      +--------------------------------------+

Role + RoleBinding = permissions within a NAMESPACE
ClusterRole + ClusterRoleBinding = permissions CLUSTER-WIDE
```

### Scope Comparison

| Resource | Scope | Use Case |
|---|---|---|
| **Role** | Namespace | Dev team can manage pods in "dev" namespace |
| **ClusterRole** | Cluster-wide | Admin can manage nodes, cluster can read PVs |
| **RoleBinding** | Namespace | Binds a Role (or ClusterRole) to subjects in a namespace |
| **ClusterRoleBinding** | Cluster-wide | Binds a ClusterRole to subjects across all namespaces |

### RBAC Verbs

| Verb | HTTP Method | Description |
|---|---|---|
| `get` | GET (single) | Read a specific resource |
| `list` | GET (collection) | List resources |
| `watch` | GET (streaming) | Watch for changes |
| `create` | POST | Create a resource |
| `update` | PUT | Update a resource |
| `patch` | PATCH | Partially update a resource |
| `delete` | DELETE | Delete a specific resource |
| `deletecollection` | DELETE | Delete a collection of resources |

### ServiceAccounts

Every Pod runs with a ServiceAccount. By default, it uses the `default` SA in its
namespace. ServiceAccounts provide identity for Pods to authenticate with the API
server.

```
+--- Namespace: default ---+
|                          |
| ServiceAccount: default  |
|   (auto-created)         |
|   Token mounted in pods  |
|                          |
| ServiceAccount: app-sa   |
|   (you create this)      |
|   With specific RBAC     |
+---------------------------+
```

### Pod Security Standards

Kubernetes defines three security profiles:

| Profile | Description |
|---|---|
| **Privileged** | No restrictions. Full access. |
| **Baseline** | Prevents known privilege escalations. Allows most workloads. |
| **Restricted** | Heavily restricted. Best security. Requires non-root, read-only root FS, etc. |

---

## Step-by-Step Practical

### 1. Create a ServiceAccount

```bash
# Create a ServiceAccount
kubectl create serviceaccount app-sa

# Or declaratively
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: monitoring-sa
  namespace: default
automountServiceAccountToken: false    # Don't auto-mount token (security)
EOF

kubectl get serviceaccounts
kubectl get sa   # shorthand
```

### 2. Create a Role

```yaml
# Save as /tmp/role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]                    # "" = core API group
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
```

```bash
kubectl apply -f /tmp/role.yaml

# Or imperatively (CKA exam speed)
kubectl create role pod-manager \
  --verb=get,list,create,delete \
  --resource=pods \
  --namespace=default
```

### 3. Create a RoleBinding

```yaml
# Save as /tmp/rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: default
# Can also bind to users or groups:
# - kind: User
#   name: jane
#   apiGroup: rbac.authorization.k8s.io
# - kind: Group
#   name: developers
#   apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f /tmp/rolebinding.yaml

# Or imperatively
kubectl create rolebinding pod-manager-binding \
  --role=pod-manager \
  --serviceaccount=default:app-sa \
  --namespace=default
```

### 4. Test RBAC with ServiceAccount

```bash
# Test if the ServiceAccount can perform actions
kubectl auth can-i get pods --as=system:serviceaccount:default:app-sa
# yes

kubectl auth can-i delete pods --as=system:serviceaccount:default:app-sa
# no (pod-reader only allows get, list, watch)

kubectl auth can-i create deployments --as=system:serviceaccount:default:app-sa
# no

# List all permissions for the ServiceAccount
kubectl auth can-i --list --as=system:serviceaccount:default:app-sa
```

### 5. ClusterRole and ClusterRoleBinding

```yaml
# Save as /tmp/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-node-reader
subjects:
- kind: ServiceAccount
  name: monitoring-sa
  namespace: default
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f /tmp/clusterrole.yaml

# Or imperatively
kubectl create clusterrole secret-reader \
  --verb=get,list \
  --resource=secrets

kubectl create clusterrolebinding admin-secret-reader \
  --clusterrole=secret-reader \
  --serviceaccount=default:monitoring-sa
```

### 6. Use a ServiceAccount in a Pod

```yaml
# Save as /tmp/sa-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sa-demo
spec:
  serviceAccountName: app-sa
  containers:
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ['sh', '-c']
    args:
    - |
      echo "Trying to list pods (should work):"
      kubectl get pods
      echo ""
      echo "Trying to list deployments (should fail):"
      kubectl get deployments
      sleep 3600
```

```bash
kubectl apply -f /tmp/sa-pod.yaml
kubectl logs sa-demo
# Should successfully list pods but fail on deployments
kubectl delete pod sa-demo
```

### 7. SecurityContext

```yaml
# Save as /tmp/security-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-demo
spec:
  securityContext:
    # Pod-level security settings
    runAsUser: 1000              # Run as non-root user
    runAsGroup: 3000             # Primary group
    fsGroup: 2000                # Supplemental group for volume mounts
    runAsNonRoot: true           # Refuse to start if image runs as root
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'id && ls -la /data && sleep 3600']
    securityContext:
      # Container-level security settings (override pod-level)
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL                     # Drop all Linux capabilities
        # add:
        # - NET_BIND_SERVICE      # Add back only what you need
    volumeMounts:
    - name: data
      mountPath: /data
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: data
    emptyDir: {}
  - name: tmp
    emptyDir: {}
```

```bash
kubectl apply -f /tmp/security-pod.yaml
kubectl logs security-demo
# uid=1000 gid=3000 groups=2000
# Files in /data owned by group 2000

kubectl delete pod security-demo
```

### 8. Network Policies basics

```yaml
# Save as /tmp/netpol.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: api                    # Apply to pods with app=api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend           # Only allow traffic FROM frontend pods
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database           # Only allow traffic TO database pods
    ports:
    - protocol: TCP
      port: 5432
  - to:                           # Allow DNS resolution
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
```

```bash
kubectl apply -f /tmp/netpol.yaml
kubectl get networkpolicies
kubectl describe networkpolicy api-network-policy
```

### 9. Default deny NetworkPolicy

```yaml
# Save as /tmp/default-deny.yaml
# Deny all ingress traffic to all pods in the namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}          # Empty = all pods
  policyTypes:
  - Ingress
  # No ingress rules = deny all ingress

---
# Deny all egress traffic from all pods
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
spec:
  podSelector: {}
  policyTypes:
  - Egress
  # No egress rules = deny all egress
```

### 10. Pod Security Standards (admission)

```yaml
# Apply security standards at namespace level
# Save as /tmp/secure-ns.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-ns
  labels:
    # Enforce the restricted profile
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    # Warn about violations (but don't block)
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
    # Audit violations
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
```

```bash
kubectl apply -f /tmp/secure-ns.yaml

# Try to run a privileged pod (should be rejected)
kubectl run test --image=nginx -n secure-ns
# Error: violates PodSecurity "restricted":...

# A compliant pod would need:
# runAsNonRoot: true, allowPrivilegeEscalation: false,
# drop ALL capabilities, seccompProfile, etc.
```

### 11. Verify RBAC configuration

```bash
# Check who can do what
kubectl auth can-i create pods
kubectl auth can-i delete nodes
kubectl auth can-i '*' '*'    # Can I do everything?

# Check as a specific user/serviceaccount
kubectl auth can-i get pods --as=system:serviceaccount:default:app-sa -n default

# List all roles and bindings
kubectl get roles,rolebindings -A
kubectl get clusterroles,clusterrolebindings

# Describe to see details
kubectl describe role pod-reader
kubectl describe rolebinding read-pods-binding
```

### 12. Clean up

```bash
kubectl delete pod sa-demo security-demo 2>/dev/null
kubectl delete sa app-sa monitoring-sa
kubectl delete role pod-reader pod-manager
kubectl delete rolebinding read-pods-binding pod-manager-binding
kubectl delete clusterrole node-reader secret-reader
kubectl delete clusterrolebinding monitoring-node-reader admin-secret-reader
kubectl delete networkpolicy api-network-policy default-deny-ingress default-deny-egress
kubectl delete namespace secure-ns
```

---

## Exercises

1. **ServiceAccount RBAC**: Create a ServiceAccount named `deploy-sa`. Create a
   Role that allows get, list, create, and delete on Deployments and Pods. Bind
   it. Test with `kubectl auth can-i`.

2. **Least Privilege**: Create a ServiceAccount that can ONLY read ConfigMaps in
   the `dev` namespace. Verify it cannot read Secrets, cannot create anything,
   and cannot access other namespaces.

3. **SecurityContext**: Create a Pod that runs as user 1000, drops all capabilities,
   has a read-only root filesystem, and disallows privilege escalation. Verify with
   `id` and try to write to the root filesystem (should fail).

4. **NetworkPolicy**: Create a namespace with two Deployments: `frontend` and
   `backend`. Create a NetworkPolicy that only allows frontend Pods to reach
   backend Pods on port 8080. Test by exec-ing into pods and using wget.

5. **Audit Existing RBAC**: Run `kubectl get clusterrolebindings -o wide` and
   identify which ServiceAccounts have cluster-admin access. Discuss why this
   might be a security concern.

---

## Knowledge Check

**Q1**: What is the difference between a Role and a ClusterRole?
<details>
<summary>Answer</summary>
A Role grants permissions within a specific namespace. A ClusterRole grants
permissions cluster-wide or to cluster-scoped resources (nodes, PVs, namespaces).
A ClusterRole can also be bound to a specific namespace via a RoleBinding, which
is useful for reusing the same set of permissions across multiple namespaces.
</details>

**Q2**: How do you check if a ServiceAccount can perform a specific action?
<details>
<summary>Answer</summary>
Use `kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<namespace>:<sa-name>`.
For example: `kubectl auth can-i get pods --as=system:serviceaccount:default:app-sa`.
This impersonates the ServiceAccount and checks RBAC permissions.
</details>

**Q3**: What does `runAsNonRoot: true` do in a SecurityContext?
<details>
<summary>Answer</summary>
It tells the kubelet to refuse to start the container if its process would run as
root (UID 0). If the container image is configured to run as root and no `runAsUser`
is specified, the container will fail to start. This is a defense against images that
unexpectedly run as root.
</details>

**Q4**: What happens when you apply a NetworkPolicy with an empty podSelector?
<details>
<summary>Answer</summary>
An empty podSelector (`podSelector: {}`) selects ALL pods in the namespace. Combined
with a policyType of Ingress and no ingress rules, this creates a default deny policy
-- all incoming traffic to all pods in the namespace is blocked. Pods must then be
explicitly allowed traffic via additional NetworkPolicies.
</details>

**Q5**: Why should you set `automountServiceAccountToken: false`?
<details>
<summary>Answer</summary>
By default, Kubernetes mounts the ServiceAccount token into every Pod. If the Pod
is compromised, an attacker can use that token to authenticate with the API server.
Setting `automountServiceAccountToken: false` prevents the token from being mounted,
reducing the attack surface. Only Pods that need API access should have the token.
</details>
