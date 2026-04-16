# Crossplane Fundamentals

## Why This Matters in DevOps

Every DevOps team faces the same challenge: developers need infrastructure (databases, caches, queues, storage) but provisioning it requires specialized knowledge of cloud consoles, Terraform modules, or opening tickets. Crossplane solves this by turning Kubernetes into a universal control plane where developers can provision any cloud resource using `kubectl apply` -- the same tool they already use for deployments. If you run Kubernetes, Crossplane lets you build a self-service platform without building a custom portal, and it gives you continuous reconciliation (self-healing) that Terraform cannot match.

---

## Core Concepts

### What Is Crossplane?

Crossplane is a CNCF project that extends Kubernetes to manage any infrastructure resource -- cloud services, databases, DNS records, even SaaS products. It installs as a set of controllers inside your Kubernetes cluster and uses Custom Resource Definitions (CRDs) to represent external resources.

```
┌─────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                 │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              Crossplane Core                  │   │
│  │  ┌────────────┐  ┌────────────────────────┐  │   │
│  │  │ Composition │  │ Composite Resource     │  │   │
│  │  │ Engine      │  │ Definition Engine      │  │   │
│  │  └────────────┘  └────────────────────────┘  │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              Providers                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────────┐   │   │
│  │  │ AWS     │ │ Azure   │ │ GCP          │   │   │
│  │  │Provider │ │Provider │ │Provider      │   │   │
│  │  └────┬────┘ └────┬────┘ └──────┬───────┘   │   │
│  └───────┼───────────┼─────────────┼────────────┘   │
└──────────┼───────────┼─────────────┼────────────────┘
           │           │             │
     ┌─────▼──┐  ┌─────▼──┐  ┌──────▼─┐
     │  AWS   │  │ Azure  │  │  GCP   │
     │  APIs  │  │  APIs  │  │  APIs  │
     └────────┘  └────────┘  └────────┘
```

### Architecture Components

**Providers** are controller packages that know how to manage specific cloud resources. Each provider installs CRDs for the resources it manages.

```yaml
# Install the AWS provider
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v1.14.0
```

**Managed Resources** are Kubernetes custom resources that represent a single external resource (an S3 bucket, an RDS instance, a VPC). Each managed resource maps 1:1 to a cloud resource.

**Composite Resources (XRs)** are higher-level abstractions that combine multiple managed resources into a single logical unit. Think of them as reusable modules.

**Composite Resource Definitions (XRDs)** define the schema (API) for composite resources -- what parameters users can set.

**Claims (XRCs)** are namespace-scoped requests for composite resources. They are the developer-facing API -- simple, abstracted, safe.

**Compositions** define how a claim maps to actual cloud resources -- the implementation behind the API.

```
Developer View:              Platform Team View:

Claim (XRC)                  XRD (defines the API)
  "I need a database"          → schema, parameters
      │                      Composition (implements the API)
      ▼                        → RDS instance
  Composite Resource (XR)      → Security Group
      │                        → Subnet Group
      ▼                        → Parameter Group
  Managed Resources            → Secret (connection details)
  (actual cloud resources)
```

### Crossplane Providers

Crossplane supports providers for all major clouds and many services:

| Provider Family | Examples | Resource Count |
|---|---|---|
| AWS (Upbound) | S3, RDS, EC2, EKS, Lambda, SQS, SNS | 1000+ CRDs |
| Azure (Upbound) | Storage, SQL, AKS, Functions | 800+ CRDs |
| GCP (Upbound) | GCS, CloudSQL, GKE, Pub/Sub | 600+ CRDs |
| Kubernetes | Namespaces, ConfigMaps, RBAC | K8s resources |
| Helm | Helm releases | Helm charts |
| SQL | Database schemas, users, grants | SQL databases |

---

## Step-by-Step Practical

### Installing Crossplane on Kubernetes

**Step 1: Install Crossplane using Helm**

```bash
# Add the Crossplane Helm repository
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm repo update

# Install Crossplane into its own namespace
helm install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --set args='{"--enable-usages"}'

# Verify installation
kubectl get pods -n crossplane-system
```

Expected output:
```
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-5f8c7d9b5c-k2x4m              1/1     Running   0          45s
crossplane-rbac-manager-7f8b9c6d4-j3n2p   1/1     Running   0          45s
```

**Step 2: Install the AWS S3 Provider**

```bash
# Install Crossplane CLI (optional but helpful)
curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh" | sh
sudo mv crossplane /usr/local/bin/

# Apply the provider
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v1.14.0
EOF

# Wait for the provider to be healthy
kubectl get providers -w
```

Expected output:
```
NAME               INSTALLED   HEALTHY   PACKAGE                                         AGE
provider-aws-s3    True        True      xpkg.upbound.io/upbound/provider-aws-s3:v1.14.0   2m
```

**Step 3: Configure AWS Credentials**

```bash
# Create a Kubernetes secret with AWS credentials
kubectl create secret generic aws-secret \
  -n crossplane-system \
  --from-literal=creds="$(cat <<EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
EOF
)"

# Create a ProviderConfig that references the secret
cat <<EOF | kubectl apply -f -
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-secret
      key: creds
EOF
```

**Step 4: Provision Your First Managed Resource -- an S3 Bucket**

```yaml
# s3-bucket.yaml
apiVersion: s3.aws.upbound.io/v1beta2
kind: Bucket
metadata:
  name: my-crossplane-demo-bucket
  labels:
    app: demo
spec:
  forProvider:
    region: us-east-1
    tags:
      Environment: dev
      ManagedBy: crossplane
  providerConfigRef:
    name: default
```

```bash
# Apply the resource
kubectl apply -f s3-bucket.yaml

# Watch the resource being provisioned
kubectl get bucket my-crossplane-demo-bucket -w
```

Expected output:
```
NAME                        READY   SYNCED   EXTERNAL-NAME                  AGE
my-crossplane-demo-bucket   False   True     my-crossplane-demo-bucket      5s
my-crossplane-demo-bucket   True    True     my-crossplane-demo-bucket      45s
```

**Step 5: Inspect and Verify**

```bash
# Describe the resource for full details
kubectl describe bucket my-crossplane-demo-bucket

# Check events
kubectl get events --field-selector involvedObject.name=my-crossplane-demo-bucket

# Verify in AWS CLI
aws s3 ls | grep crossplane-demo
```

Expected describe output (abbreviated):
```
Name:         my-crossplane-demo-bucket
Status:
  Conditions:
    Type:   Ready
    Status: True
    Type:   Synced
    Status: True
  At Provider:
    Id:     my-crossplane-demo-bucket
    Region: us-east-1
```

**Step 6: Test Self-Healing (Drift Detection)**

```bash
# Manually delete the bucket from AWS
aws s3 rb s3://my-crossplane-demo-bucket

# Watch Crossplane re-create it (within ~1 minute)
kubectl get bucket my-crossplane-demo-bucket -w
```

Expected output:
```
NAME                        READY   SYNCED   AGE
my-crossplane-demo-bucket   False   False    5m    # Detects drift
my-crossplane-demo-bucket   False   True     5m    # Re-creating
my-crossplane-demo-bucket   True    True     6m    # Restored
```

**Step 7: Clean Up**

```bash
# Delete via kubectl (Crossplane deletes the real AWS resource)
kubectl delete bucket my-crossplane-demo-bucket

# Verify
aws s3 ls | grep crossplane-demo
# (no output -- bucket deleted)
```

### Adding Versioning and Encryption

```yaml
# s3-complete.yaml
apiVersion: s3.aws.upbound.io/v1beta2
kind: Bucket
metadata:
  name: my-secure-bucket
spec:
  forProvider:
    region: us-east-1
    tags:
      Environment: production
  providerConfigRef:
    name: default
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: BucketVersioning
metadata:
  name: my-secure-bucket-versioning
spec:
  forProvider:
    region: us-east-1
    bucketRef:
      name: my-secure-bucket
    versioningConfiguration:
      - status: Enabled
---
apiVersion: s3.aws.upbound.io/v1beta2
kind: BucketServerSideEncryptionConfiguration
metadata:
  name: my-secure-bucket-encryption
spec:
  forProvider:
    region: us-east-1
    bucketRef:
      name: my-secure-bucket
    rule:
      - applyServerSideEncryptionByDefault:
          - sseAlgorithm: aws:kms
```

```bash
kubectl apply -f s3-complete.yaml
kubectl get bucket,bucketversioning,bucketserversideencryptionconfiguration
```

---

## Exercises

1. **Install and Explore**: Install Crossplane on a local Kind or Minikube cluster. Install the AWS provider and list all CRDs it creates (`kubectl get crds | grep aws`). How many resource types does it support?

2. **Multi-Resource Provisioning**: Create a YAML file that provisions an S3 bucket with: versioning enabled, server-side encryption with AES256, lifecycle rules that transition objects to Glacier after 90 days, and a bucket policy that denies unencrypted uploads.

3. **Drift Experiment**: Provision an S3 bucket via Crossplane, then manually modify a tag in the AWS console. Observe how long Crossplane takes to detect and correct the drift. Document the behavior.

4. **Provider Exploration**: Install the Kubernetes provider for Crossplane and use it to create a Namespace and a ConfigMap in your cluster. This demonstrates that Crossplane can manage Kubernetes resources too.

5. **Resource Graph**: Provision three related resources (VPC, Subnet, Security Group) using the AWS provider. Document the dependency chain and how Crossplane handles ordering.

---

## Knowledge Check

**Q1: What is the difference between a Managed Resource and a Composite Resource in Crossplane?**

<details>
<summary>Answer</summary>

A Managed Resource represents a single external resource (e.g., one S3 bucket, one RDS instance) and maps 1:1 to a cloud resource. A Composite Resource (XR) is a higher-level abstraction that composes multiple managed resources into a single logical unit. For example, a "Database" composite resource might include an RDS instance, a security group, a subnet group, and a Kubernetes secret -- all provisioned together as one unit. Managed resources are typically created by platform engineers; composite resources (via Claims) are exposed to developers.
</details>

**Q2: How does Crossplane handle drift detection differently from Terraform?**

<details>
<summary>Answer</summary>

Terraform detects drift only when you run `terraform plan` or `terraform apply` -- it is not continuous. If someone modifies a resource in the console, Terraform does not know until the next run. Crossplane runs a continuous reconciliation loop inside Kubernetes. Controllers poll cloud APIs at regular intervals (typically every 1-10 minutes depending on the provider) and compare actual state with desired state. If drift is detected, Crossplane automatically corrects it without human intervention. This makes Crossplane self-healing by default.
</details>

**Q3: Why does Crossplane require a Kubernetes cluster?**

<details>
<summary>Answer</summary>

Crossplane uses Kubernetes as its control plane runtime. It relies on: (1) the Kubernetes API server for receiving and validating resource definitions, (2) etcd for storing desired state (replacing the need for a separate state file), (3) the controller-manager pattern for continuous reconciliation, (4) RBAC for access control, (5) Custom Resource Definitions for extending the API with cloud resource types. This is why Crossplane is described as extending Kubernetes rather than being a standalone tool -- it is built on top of Kubernetes' proven infrastructure.
</details>

**Q4: What is a ProviderConfig and why is it important?**

<details>
<summary>Answer</summary>

A ProviderConfig tells a Crossplane provider how to authenticate with the target cloud. It contains or references credentials (API keys, service account tokens, IAM role ARNs). Without a ProviderConfig, the provider cannot create or manage resources. You can have multiple ProviderConfigs for different accounts or regions, and each managed resource can reference a specific ProviderConfig. This enables multi-account and multi-region management from a single Crossplane installation.
</details>
