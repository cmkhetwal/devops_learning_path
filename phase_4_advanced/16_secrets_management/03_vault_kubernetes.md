# Vault with Kubernetes

## Why This Matters in DevOps

Kubernetes applications need secrets at runtime -- database passwords, API keys, TLS certificates. The built-in Kubernetes Secrets resource stores values in base64 (not encrypted) in etcd, is visible to anyone with RBAC access, and has no rotation capability. Vault integration with Kubernetes solves these problems: secrets are stored encrypted in Vault, delivered to pods securely at startup, automatically rotated, and access is controlled by Vault policies. There are two primary patterns -- the Vault Agent Injector (sidecar) and the CSI Secret Store Driver (volume mount) -- and knowing when to use each is essential.

---

## Core Concepts

### Integration Patterns

```
Pattern 1: Vault Agent Injector (Sidecar)
─────────────────────────────────────────
┌─────────────────────────────────────┐
│  Pod                                │
│  ┌───────────┐  ┌────────────────┐  │
│  │ App       │  │ Vault Agent   │  │
│  │ Container │  │ (sidecar)     │  │
│  │           │  │               │  │
│  │ Reads     │◄─│ Fetches from  │  │
│  │ /vault/   │  │ Vault server  │  │
│  │ secrets   │  │ Renders to    │  │
│  │           │  │ shared volume │  │
│  └───────────┘  └────────────────┘  │
└─────────────────────────────────────┘

Pattern 2: CSI Secret Store Driver (Volume Mount)
──────────────────────────────────────────────────
┌─────────────────────────────────────┐
│  Pod                                │
│  ┌───────────────────────────────┐  │
│  │ App Container                 │  │
│  │                               │  │
│  │ /mnt/secrets/db-password      │  │
│  │  (mounted via CSI driver)     │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  CSI Secret Store Driver            │
│  (DaemonSet on each node)           │
│  Fetches secrets from Vault         │
│  Mounts as volume                   │
└─────────────────────────────────────┘
```

### Kubernetes Auth Method

Vault's Kubernetes auth method authenticates pods using their Kubernetes Service Account tokens. The flow:

```
1. Pod starts with a ServiceAccount
2. Pod presents SA token to Vault
3. Vault validates token with K8s API
4. Vault returns a Vault token with policies
5. Pod uses Vault token to read secrets
```

### Comparison of Approaches

| Feature | Agent Injector | CSI Driver |
|---|---|---|
| How secrets arrive | Written to shared volume by sidecar | Mounted as volume by CSI driver |
| Secret rotation | Yes (agent polls for changes) | Yes (with rotation enabled) |
| Resource overhead | Sidecar per pod (memory/CPU) | DaemonSet per node (shared) |
| Dynamic secrets | Yes | Limited |
| Template rendering | Yes (Go templates) | No (raw values only) |
| Init container | Optional (for pre-start secrets) | No |
| K8s Secret sync | No (files only) | Yes (optional sync to K8s Secret) |

---

## Step-by-Step Practical

### Deploying Vault on Kubernetes

**Step 1: Install Vault via Helm**

```bash
# Add HashiCorp Helm repo
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Install Vault with integrated storage (Raft)
cat <<EOF > vault-values.yaml
server:
  ha:
    enabled: true
    replicas: 3
    raft:
      enabled: true
      config: |
        ui = true
        listener "tcp" {
          tls_disable = 1
          address = "[::]:8200"
          cluster_address = "[::]:8201"
        }
        storage "raft" {
          path = "/vault/data"
        }
        service_registration "kubernetes" {}
  dataStorage:
    enabled: true
    size: 10Gi
    storageClass: gp3
  resources:
    requests:
      memory: 256Mi
      cpu: 250m
    limits:
      memory: 512Mi
      cpu: 500m

injector:
  enabled: true
  replicas: 2
  resources:
    requests:
      memory: 64Mi
      cpu: 50m

ui:
  enabled: true
  serviceType: ClusterIP
EOF

helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --values vault-values.yaml
```

```bash
# Check pods (they will be 0/1 until initialized)
kubectl get pods -n vault
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
vault-0                                 0/1     Running   0          30s
vault-1                                 0/1     Running   0          30s
vault-2                                 0/1     Running   0          30s
vault-agent-injector-5c7b7d6c9f-abc12   1/1     Running   0          30s
vault-agent-injector-5c7b7d6c9f-def34   1/1     Running   0          30s
```

**Step 2: Initialize and Unseal Vault**

```bash
# Initialize Vault (generates unseal keys and root token)
kubectl exec -n vault vault-0 -- vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-init.json

# IMPORTANT: Store vault-init.json securely! These are your recovery keys.

# Extract unseal keys
UNSEAL_KEY_1=$(jq -r '.unseal_keys_b64[0]' vault-init.json)
UNSEAL_KEY_2=$(jq -r '.unseal_keys_b64[1]' vault-init.json)
UNSEAL_KEY_3=$(jq -r '.unseal_keys_b64[2]' vault-init.json)
ROOT_TOKEN=$(jq -r '.root_token' vault-init.json)

# Unseal vault-0
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_1
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_2
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_3

# Join other nodes to the Raft cluster
kubectl exec -n vault vault-1 -- vault operator raft join http://vault-0.vault-internal:8200
kubectl exec -n vault vault-2 -- vault operator raft join http://vault-0.vault-internal:8200

# Unseal other nodes
for pod in vault-1 vault-2; do
  kubectl exec -n vault $pod -- vault operator unseal $UNSEAL_KEY_1
  kubectl exec -n vault $pod -- vault operator unseal $UNSEAL_KEY_2
  kubectl exec -n vault $pod -- vault operator unseal $UNSEAL_KEY_3
done

# Verify all nodes are ready
kubectl get pods -n vault
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
vault-0                                 1/1     Running   0          5m
vault-1                                 1/1     Running   0          5m
vault-2                                 1/1     Running   0          5m
vault-agent-injector-5c7b7d6c9f-abc12   1/1     Running   0          5m
vault-agent-injector-5c7b7d6c9f-def34   1/1     Running   0          5m
```

**Step 3: Configure Kubernetes Auth**

```bash
# Login to Vault
kubectl exec -n vault vault-0 -- vault login $ROOT_TOKEN

# Enable Kubernetes auth method
kubectl exec -n vault vault-0 -- vault auth enable kubernetes

# Configure K8s auth to use the in-cluster API
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc"
```

**Step 4: Store Secrets and Create Policies**

```bash
# Enable KV secrets engine
kubectl exec -n vault vault-0 -- vault secrets enable -path=secret kv-v2

# Store application secrets
kubectl exec -n vault vault-0 -- vault kv put secret/myapp/config \
  db_host="postgres.database.svc.cluster.local" \
  db_port="5432" \
  db_name="orders" \
  db_username="app_user" \
  db_password="ProductionDbPassword123!" \
  redis_url="redis://redis.cache.svc.cluster.local:6379" \
  api_key="sk-live-abc123def456"

# Create a read-only policy for the application
kubectl exec -n vault vault-0 -- sh -c 'vault policy write myapp-policy - <<POLICY
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
POLICY'

# Create a Kubernetes auth role
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=myapp \
  policies=myapp-policy \
  ttl=1h
```

**Step 5: Inject Secrets into Application Pods (Agent Injector)**

```yaml
# myapp-deployment.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: myapp
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        # Vault Agent Injector annotations
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp"

        # Inject database config as a file
        vault.hashicorp.com/agent-inject-secret-db-config: "secret/data/myapp/config"
        vault.hashicorp.com/agent-inject-template-db-config: |
          {{- with secret "secret/data/myapp/config" -}}
          DB_HOST={{ .Data.data.db_host }}
          DB_PORT={{ .Data.data.db_port }}
          DB_NAME={{ .Data.data.db_name }}
          DB_USERNAME={{ .Data.data.db_username }}
          DB_PASSWORD={{ .Data.data.db_password }}
          {{- end }}

        # Inject Redis URL as a separate file
        vault.hashicorp.com/agent-inject-secret-redis: "secret/data/myapp/config"
        vault.hashicorp.com/agent-inject-template-redis: |
          {{- with secret "secret/data/myapp/config" -}}
          {{ .Data.data.redis_url }}
          {{- end }}

        # Inject API key
        vault.hashicorp.com/agent-inject-secret-api-key: "secret/data/myapp/config"
        vault.hashicorp.com/agent-inject-template-api-key: |
          {{- with secret "secret/data/myapp/config" -}}
          {{ .Data.data.api_key }}
          {{- end }}
    spec:
      serviceAccountName: myapp-sa
      containers:
        - name: myapp
          image: mycompany/myapp:v1.0
          command: ["/bin/sh", "-c"]
          args:
            - |
              # Source the database config
              source /vault/secrets/db-config
              # Read other secrets
              export REDIS_URL=$(cat /vault/secrets/redis)
              export API_KEY=$(cat /vault/secrets/api-key)
              # Start the application
              python app.py
          ports:
            - containerPort: 8080
```

```bash
# Create namespace and deploy
kubectl create namespace myapp
kubectl apply -f myapp-deployment.yaml

# Verify secrets are injected
kubectl exec -n myapp deploy/myapp -c myapp -- cat /vault/secrets/db-config
```

Expected output:
```
DB_HOST=postgres.database.svc.cluster.local
DB_PORT=5432
DB_NAME=orders
DB_USERNAME=app_user
DB_PASSWORD=ProductionDbPassword123!
```

**Step 6: CSI Secret Store Driver (Alternative Approach)**

```bash
# Install Secrets Store CSI Driver
helm install csi-secrets-store \
  secrets-store-csi-driver/secrets-store-csi-driver \
  --namespace kube-system \
  --set syncSecret.enabled=true

# Install Vault CSI provider
helm install vault-csi hashicorp/vault \
  --namespace vault \
  --set "server.enabled=false" \
  --set "injector.enabled=false" \
  --set "csi.enabled=true"
```

```yaml
# secret-provider-class.yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-myapp
  namespace: myapp
spec:
  provider: vault
  parameters:
    vaultAddress: "http://vault.vault.svc.cluster.local:8200"
    roleName: "myapp"
    objects: |
      - objectName: "db-password"
        secretPath: "secret/data/myapp/config"
        secretKey: "db_password"
      - objectName: "api-key"
        secretPath: "secret/data/myapp/config"
        secretKey: "api_key"
  # Optionally sync to Kubernetes Secret
  secretObjects:
    - secretName: myapp-secrets
      type: Opaque
      data:
        - objectName: db-password
          key: DB_PASSWORD
        - objectName: api-key
          key: API_KEY
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-csi
  namespace: myapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp-csi
  template:
    metadata:
      labels:
        app: myapp-csi
    spec:
      serviceAccountName: myapp-sa
      containers:
        - name: myapp
          image: mycompany/myapp:v1.0
          volumeMounts:
            - name: secrets
              mountPath: "/mnt/secrets"
              readOnly: true
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: DB_PASSWORD
      volumes:
        - name: secrets
          csi:
            driver: secrets-store.csi.k8s.io
            readOnly: true
            volumeAttributes:
              secretProviderClass: vault-myapp
```

---

## Exercises

1. **Full Vault Deployment**: Deploy Vault on Kubernetes with HA (3 replicas), initialize it, unseal it, and configure Kubernetes auth. Store 5 different secrets and create appropriate policies.

2. **Agent Injector**: Deploy an application that reads database credentials from Vault using the Agent Injector. Modify the secret in Vault and verify the sidecar updates the file in the pod.

3. **CSI Driver**: Deploy the same application using the CSI Secret Store Driver instead. Compare the two approaches: resource usage, complexity, rotation behavior.

4. **Dynamic DB Credentials**: Configure Vault to generate dynamic PostgreSQL credentials. Deploy an application that gets fresh credentials from Vault on each restart. Verify old credentials expire.

5. **Multi-Team Setup**: Create three namespaces (team-a, team-b, team-c). Configure Vault so each team can only access their own secrets. Test isolation by attempting cross-team secret access.

---

## Knowledge Check

**Q1: What is the difference between the Vault Agent Injector and the CSI Secret Store Driver?**

<details>
<summary>Answer</summary>

The Agent Injector runs a sidecar container alongside each pod that authenticates to Vault, fetches secrets, renders them using Go templates, and writes them to a shared volume at `/vault/secrets/`. It continuously polls for changes and supports dynamic secrets and complex templating. The CSI Driver is a DaemonSet that runs once per node and mounts secrets as volumes using the Container Storage Interface. It does not require a sidecar per pod (lower resource overhead) and can optionally sync secrets to Kubernetes Secrets objects. Choose the Agent Injector when you need template rendering, dynamic secrets, or automatic rotation. Choose the CSI Driver when you want lower resource overhead or need secrets as Kubernetes Secret objects.
</details>

**Q2: How does the Kubernetes auth method work in Vault?**

<details>
<summary>Answer</summary>

When a pod needs to authenticate: (1) The pod (or its sidecar) reads its Kubernetes Service Account JWT token from `/var/run/secrets/kubernetes.io/serviceaccount/token`. (2) It sends this token to Vault's Kubernetes auth endpoint. (3) Vault validates the token by calling the Kubernetes TokenReview API. (4) If the token is valid, Vault checks if the service account name and namespace match a configured role. (5) If matched, Vault returns a Vault token with the policies associated with that role. This is secure because: no static Vault credentials are stored in pods, authentication is tied to Kubernetes identity, and policies are centrally managed in Vault.
</details>

**Q3: How do you handle Vault unsealing in production?**

<details>
<summary>Answer</summary>

In production, manual unsealing is impractical (Vault re-seals after restarts, crashes, or upgrades). Options: (1) **Auto-unseal with cloud KMS** -- Vault uses AWS KMS, Azure Key Vault, or GCP KMS to automatically unseal. The master key is encrypted with the KMS key. This is the recommended approach. (2) **Vault Enterprise auto-unseal** -- same concept, built into Enterprise. (3) **Shamir secret sharing with automation** -- store unseal keys in separate secure locations and automate the unseal process (risky, not recommended). Never store unseal keys in the same system as Vault. Enable transit auto-unseal with a separate Vault cluster for defense in depth.
</details>

**Q4: What happens to secrets when a Vault Agent Injector pod restarts?**

<details>
<summary>Answer</summary>

When the pod restarts, the Vault Agent init container runs first (if configured) and fetches all secrets from Vault before the main application container starts. This ensures the application always has secrets available at startup. The sidecar container then continues running alongside the application, periodically polling Vault for secret changes and updating the files in `/vault/secrets/`. If Vault is temporarily unavailable during a restart, the init container will retry until it can connect, which means the pod will stay in Init state until Vault is reachable. To mitigate this, use the `vault.hashicorp.com/agent-pre-populate-only: "true"` annotation if you do not need continuous rotation.
</details>
