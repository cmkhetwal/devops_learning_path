# Lesson 08: ConfigMaps and Secrets

## Why This Matters in DevOps

The twelve-factor app methodology mandates separating configuration from code.
Hardcoding database URLs, API keys, or feature flags in container images means
rebuilding images for every environment (dev, staging, prod). ConfigMaps and Secrets
let you inject configuration at runtime, keeping images portable and credentials safe.

As a DevOps engineer, you will manage configuration for dozens of services across
multiple environments. Understanding how to create, mount, and rotate ConfigMaps
and Secrets prevents environment drift, security incidents, and deployment failures.

The CKA exam tests creating ConfigMaps and Secrets from the command line and mounting
them both as environment variables and volume files.

---

## Core Concepts

### The 12-Factor App Config Principle

```
BAD: Config baked into the image
+--- Docker Image ---+
| app.py             |
| DB_HOST=prod-db    |  <-- Rebuild image for every environment
| API_KEY=secret123  |  <-- Secret exposed in image layers
+--------------------+

GOOD: Config injected at runtime
+--- Docker Image ---+     +--- ConfigMap ----+
| app.py             | <-- | DB_HOST=prod-db  |
|                    |     | LOG_LEVEL=info   |
+--------------------+     +------------------+
                           +--- Secret -------+
                       <-- | API_KEY=secret123|
                           +------------------+
Same image used everywhere. Config changes without rebuilding.
```

### ConfigMaps vs Secrets

| Feature | ConfigMap | Secret |
|---|---|---|
| Purpose | Non-sensitive configuration | Sensitive data (passwords, tokens, keys) |
| Storage | Plain text in etcd | Base64 encoded in etcd |
| Size limit | 1 MiB | 1 MiB |
| Encryption at rest | No (unless you configure it) | Optional (EncryptionConfiguration) |
| Example | Database hostname, log level | Database password, TLS certificates |

**Important**: Secrets are NOT encrypted by default. They are only base64 encoded,
which provides zero security. For real security, you must enable encryption at rest
or use an external secret manager.

### Ways to Consume ConfigMaps and Secrets

```
ConfigMap/Secret
    |
    +---> Environment Variables (injected into container)
    |     env:
    |     - name: DB_HOST
    |       valueFrom:
    |         configMapKeyRef:
    |           name: app-config
    |           key: database_host
    |
    +---> Volume Mount (files in a directory)
          volumeMounts:
          - name: config-volume
            mountPath: /etc/config
          # Each key becomes a file:
          # /etc/config/database_host  (contains the value)
          # /etc/config/log_level      (contains the value)
```

### Secret Types

| Type | Usage |
|---|---|
| `Opaque` | Default. Arbitrary key-value pairs. |
| `kubernetes.io/tls` | TLS certificate and private key. |
| `kubernetes.io/dockerconfigjson` | Docker registry credentials. |
| `kubernetes.io/basic-auth` | Username and password. |
| `kubernetes.io/ssh-auth` | SSH private key. |
| `kubernetes.io/service-account-token` | ServiceAccount token (auto-created). |

---

## Step-by-Step Practical

### 1. Create ConfigMaps

```bash
# From literal values
kubectl create configmap app-config \
  --from-literal=database_host=postgres.default.svc \
  --from-literal=database_port=5432 \
  --from-literal=log_level=info

# Verify
kubectl get configmap app-config
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml
```

```bash
# From a file
cat <<'EOF' > /tmp/app.properties
database.host=postgres.default.svc
database.port=5432
database.name=myapp
log.level=info
log.format=json
EOF

kubectl create configmap app-file-config --from-file=/tmp/app.properties

# The filename becomes the key, file content becomes the value
kubectl get configmap app-file-config -o yaml
```

```bash
# From a directory (each file becomes a key)
mkdir -p /tmp/config-dir
echo "postgres.default.svc" > /tmp/config-dir/db_host
echo "5432" > /tmp/config-dir/db_port
echo "info" > /tmp/config-dir/log_level

kubectl create configmap dir-config --from-file=/tmp/config-dir/
kubectl get configmap dir-config -o yaml
```

### 2. Create ConfigMap declaratively

```yaml
# Save as /tmp/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  # Simple key-value pairs
  DATABASE_HOST: "postgres.default.svc"
  DATABASE_PORT: "5432"
  LOG_LEVEL: "info"

  # Multi-line config file
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
```

```bash
kubectl apply -f /tmp/configmap.yaml
kubectl get configmap webapp-config -o yaml
```

### 3. Use ConfigMap as environment variables

```yaml
# Save as /tmp/cm-env-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cm-env-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'env | sort && sleep 3600']
    # Method 1: Reference specific keys
    env:
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_host
    - name: DB_PORT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_port
    # Method 2: Load ALL keys from a ConfigMap as env vars
    envFrom:
    - configMapRef:
        name: app-config
        # Optional prefix to avoid name collisions
      prefix: APP_
```

```bash
kubectl apply -f /tmp/cm-env-pod.yaml
kubectl logs cm-env-demo | grep -E "DB_|APP_"
# DB_HOST=postgres.default.svc
# DB_PORT=5432
# APP_database_host=postgres.default.svc
# APP_database_port=5432
# APP_log_level=info

kubectl delete pod cm-env-demo
```

### 4. Mount ConfigMap as a volume

```yaml
# Save as /tmp/cm-vol-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cm-vol-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'ls -la /etc/config && cat /etc/config/nginx.conf && sleep 3600']
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: webapp-config
```

```bash
kubectl apply -f /tmp/cm-vol-pod.yaml
kubectl logs cm-vol-demo
# Each key becomes a file in /etc/config/
# DATABASE_HOST, DATABASE_PORT, LOG_LEVEL, nginx.conf

kubectl exec cm-vol-demo -- cat /etc/config/DATABASE_HOST
# postgres.default.svc

kubectl exec cm-vol-demo -- cat /etc/config/nginx.conf
# (full nginx config)

kubectl delete pod cm-vol-demo
```

### 5. Mount specific keys as specific files

```yaml
# Save as /tmp/cm-specific-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cm-specific-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    volumeMounts:
    - name: nginx-config
      mountPath: /etc/nginx/conf.d/default.conf
      subPath: nginx.conf       # Mount single key as a single file
  volumes:
  - name: nginx-config
    configMap:
      name: webapp-config
      items:
      - key: nginx.conf
        path: nginx.conf        # Rename the file if needed
```

```bash
kubectl apply -f /tmp/cm-specific-pod.yaml
kubectl exec cm-specific-demo -- cat /etc/nginx/conf.d/default.conf
kubectl delete pod cm-specific-demo
```

### 6. Create Secrets

```bash
# From literal values (automatically base64 encoded)
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password='S3cur3P@ss!'

# View the secret (values are base64 encoded)
kubectl get secret db-credentials -o yaml
# data:
#   password: UzNjdXIzUEBzcyE=
#   username: YWRtaW4=

# Decode a value
kubectl get secret db-credentials -o jsonpath='{.data.password}' | base64 -d
# S3cur3P@ss!
```

```bash
# From files
echo -n 'admin' > /tmp/username.txt
echo -n 'S3cur3P@ss!' > /tmp/password.txt

kubectl create secret generic db-creds-file \
  --from-file=username=/tmp/username.txt \
  --from-file=password=/tmp/password.txt

rm /tmp/username.txt /tmp/password.txt
```

### 7. Create Secrets declaratively

```yaml
# Save as /tmp/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  # Values MUST be base64 encoded
  username: YWRtaW4=                  # echo -n 'admin' | base64
  password: UzNjdXIzUEBzcyE=          # echo -n 'S3cur3P@ss!' | base64

---
# Alternative: use stringData to provide plain text (auto-encoded)
apiVersion: v1
kind: Secret
metadata:
  name: app-secret-plain
type: Opaque
stringData:
  username: admin
  password: "S3cur3P@ss!"
```

```bash
kubectl apply -f /tmp/secret.yaml
kubectl get secrets
```

### 8. Use Secrets in Pods

```yaml
# Save as /tmp/secret-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'echo "User: $DB_USER" && echo "Pass: $DB_PASS" && sleep 3600']
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
    # Or mount as files
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-credentials
```

```bash
kubectl apply -f /tmp/secret-pod.yaml
kubectl logs secret-demo
# User: admin
# Pass: S3cur3P@ss!

kubectl exec secret-demo -- cat /etc/secrets/username
# admin

kubectl delete pod secret-demo
```

### 9. TLS Secret

```bash
# Create a TLS certificate and key
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /tmp/tls.key -out /tmp/tls.crt \
  -subj "/CN=myapp.example.com"

# Create a TLS secret
kubectl create secret tls myapp-tls \
  --cert=/tmp/tls.crt \
  --key=/tmp/tls.key

kubectl get secret myapp-tls -o yaml
# type: kubernetes.io/tls
# data:
#   tls.crt: <base64>
#   tls.key: <base64>
```

### 10. Docker registry Secret

```bash
kubectl create secret docker-registry registry-creds \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=me@example.com
```

```yaml
# Use in a Pod spec
spec:
  imagePullSecrets:
  - name: registry-creds
  containers:
  - name: app
    image: myuser/private-app:latest
```

### 11. Immutable ConfigMaps and Secrets

```yaml
# Save as /tmp/immutable-cm.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: immutable-config
data:
  setting: "value"
immutable: true     # Cannot be changed after creation
                    # Reduces API server load (no watches needed)
                    # Must delete and recreate to change
```

### 12. Best practices for Secrets

```bash
# DO NOT store secrets in YAML files committed to git
# DO NOT echo secrets to logs
# DO use external secret operators in production:
#   - AWS Secrets Manager + External Secrets Operator
#   - HashiCorp Vault + Vault Secrets Operator
#   - Azure Key Vault + CSI Secrets Store Driver

# Enable encryption at rest for secrets in etcd:
# Create an EncryptionConfiguration and pass it to kube-apiserver
# --encryption-provider-config=/path/to/encryption-config.yaml

# Limit who can read secrets via RBAC
# kubectl create role secret-reader --verb=get --resource=secrets
# kubectl create rolebinding dev-secret-reader --role=secret-reader --user=dev-user
```

### 13. Clean up

```bash
kubectl delete configmap app-config app-file-config dir-config webapp-config
kubectl delete secret db-credentials db-creds-file app-secret app-secret-plain myapp-tls registry-creds
kubectl delete configmap immutable-config
```

---

## Exercises

1. **ConfigMap Lifecycle**: Create a ConfigMap with 3 key-value pairs. Mount it as
   environment variables in a Pod. Verify the values. Update the ConfigMap. Delete
   and recreate the Pod. Verify the new values are reflected.

2. **Volume Mount**: Create a ConfigMap containing a custom nginx configuration.
   Mount it into an nginx Pod at `/etc/nginx/conf.d/default.conf` using `subPath`.
   Verify nginx uses the custom configuration.

3. **Secret Management**: Create a Secret with database credentials. Mount it as
   environment variables and as a volume in the same Pod. Verify both methods work.
   Decode the Secret using `kubectl get secret -o jsonpath` and base64.

4. **Multi-Environment**: Create two ConfigMaps: `dev-config` (DB_HOST=dev-db) and
   `prod-config` (DB_HOST=prod-db). Deploy the same Pod spec twice, once referencing
   dev-config and once referencing prod-config. Verify each Pod sees different values.

5. **Security Audit**: Run `kubectl get secrets -A` to list all secrets in the cluster.
   Identify which are auto-created by Kubernetes. Discuss: what additional steps
   would you take to secure secrets in a production cluster?

---

## Knowledge Check

**Q1**: What is the difference between ConfigMaps and Secrets?
<details>
<summary>Answer</summary>
ConfigMaps store non-sensitive configuration data in plain text. Secrets store
sensitive data (passwords, tokens, keys) and are base64 encoded. Both can be
consumed as environment variables or volume mounts. Secrets can optionally be
encrypted at rest in etcd with EncryptionConfiguration. Both have a 1 MiB size
limit.
</details>

**Q2**: Are Kubernetes Secrets encrypted by default?
<details>
<summary>Answer</summary>
No. Secrets are only base64 encoded, not encrypted. Base64 is an encoding, not
encryption -- anyone can decode it. For actual encryption, you must configure
encryption at rest via EncryptionConfiguration on the API server, or use an
external secret manager like HashiCorp Vault or AWS Secrets Manager.
</details>

**Q3**: What are two ways to consume a ConfigMap in a Pod?
<details>
<summary>Answer</summary>
(1) As environment variables using `env[].valueFrom.configMapKeyRef` for specific
keys or `envFrom[].configMapRef` for all keys. (2) As volume mounts using a
volume of type `configMap`, where each key becomes a file in the mount path.
Volume mounts are preferred for large config files; environment variables are
simpler for single values.
</details>

**Q4**: What does `subPath` do when mounting a ConfigMap volume?
<details>
<summary>Answer</summary>
Without subPath, mounting a ConfigMap volume to a directory replaces ALL contents
of that directory. With subPath, only the specific file is mounted, preserving
other files in the directory. For example, mounting a custom nginx config at
`/etc/nginx/conf.d/default.conf` with subPath ensures other files in conf.d are
not removed.
</details>

**Q5**: How do you create a Secret from the command line with literal values?
<details>
<summary>Answer</summary>
`kubectl create secret generic <name> --from-literal=key1=value1 --from-literal=key2=value2`.
The values are automatically base64 encoded. You can also use `--from-file` to
create Secrets from file contents, or use the declarative approach with YAML
(using `data` with base64-encoded values or `stringData` with plain text).
</details>
