# Crossplane Compositions

## Why This Matters in DevOps

Raw managed resources in Crossplane expose the full complexity of cloud APIs. A developer who needs a database should not have to understand RDS parameter groups, subnet groups, security group ingress rules, and KMS key policies. Compositions let platform teams build abstractions -- simple, opinionated APIs that hide cloud complexity. A developer submits a Claim saying "I need a PostgreSQL database, size medium" and the platform provisions everything correctly. This is the core of platform engineering with Crossplane: you are building an Internal Developer Platform where infrastructure is as easy to request as ordering from a menu.

---

## Core Concepts

### The Composition Architecture

Crossplane's abstraction layer has three components that work together:

```
┌──────────────────────────────────────────────────────────┐
│  Developer ("Consumer")                                  │
│                                                          │
│  apiVersion: mycompany.io/v1alpha1                      │
│  kind: Database         ◄──── Claim (XRC)               │
│  spec:                       (namespace-scoped)          │
│    engine: postgresql                                    │
│    size: medium                                          │
└──────────┬───────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│  Platform Team ("Producer")                              │
│                                                          │
│  CompositeResourceDefinition (XRD)                      │
│    "Defines the API schema"                              │
│    - What parameters are exposed                         │
│    - What the claim looks like                           │
│                                                          │
│  Composition                                             │
│    "Implements the API"                                  │
│    - Maps claim parameters to managed resources          │
│    - Patches values between resources                    │
│    - Defines what gets created                           │
└──────────┬───────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│  Cloud Resources (Managed Resources)                     │
│                                                          │
│  - RDS Instance (db.r6g.large)                          │
│  - RDS Subnet Group                                      │
│  - Security Group (port 5432)                            │
│  - Secret (connection details)                           │
└──────────────────────────────────────────────────────────┘
```

### Composite Resource Definitions (XRDs)

An XRD defines the API schema -- what parameters your users can set, what values are required vs optional, and what connection details are published.

Key XRD concepts:
- **group**: Your organization's API group (e.g., `platform.mycompany.io`)
- **names**: The kind name (e.g., `XDatabase`) and claim kind (e.g., `Database`)
- **versions**: Schema versions with OpenAPI v3 validation
- **claimNames**: Makes the resource available as a namespace-scoped claim

### Compositions

A Composition defines the implementation -- which managed resources to create and how to wire them together. It uses **patches** to flow values from the composite resource into managed resources.

Patch types:
- **FromCompositeFieldPath**: Copy a value from the XR spec into a managed resource
- **ToCompositeFieldPath**: Copy a value from a managed resource back to the XR status
- **CombineFromComposite**: Combine multiple XR fields into one managed resource field
- **CombineToComposite**: Combine managed resource fields back to XR

### Claims (XRCs)

Claims are the developer-facing interface. They are namespace-scoped (unlike XRs, which are cluster-scoped), making them safe for multi-tenant environments. A claim triggers the creation of an XR, which triggers the creation of managed resources via the composition.

---

## Step-by-Step Practical

### Building a "Database" Platform API

We will build a complete abstraction that lets developers provision a production-ready PostgreSQL database by submitting a simple claim.

**Step 1: Define the XRD (API Schema)**

```yaml
# xrd-database.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.platform.mycompany.io
spec:
  group: platform.mycompany.io
  names:
    kind: XDatabase
    plural: xdatabases
  claimNames:
    kind: Database
    plural: databases
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                parameters:
                  type: object
                  properties:
                    engine:
                      type: string
                      enum: ["postgresql", "mysql"]
                      description: "Database engine type"
                    engineVersion:
                      type: string
                      default: "15.4"
                      description: "Engine version"
                    size:
                      type: string
                      enum: ["small", "medium", "large"]
                      description: "Database size (maps to instance class)"
                    storageGB:
                      type: integer
                      default: 20
                      minimum: 20
                      maximum: 1000
                      description: "Storage size in GB"
                    region:
                      type: string
                      default: "us-east-1"
                    environment:
                      type: string
                      enum: ["dev", "staging", "production"]
                      default: "dev"
                  required:
                    - engine
                    - size
              required:
                - parameters
            status:
              type: object
              properties:
                endpoint:
                  type: string
                port:
                  type: integer
                instanceClass:
                  type: string
  connectionSecretKeys:
    - username
    - password
    - endpoint
    - port
```

```bash
kubectl apply -f xrd-database.yaml

# Verify the XRD is established
kubectl get xrd xdatabases.platform.mycompany.io
```

Expected output:
```
NAME                                ESTABLISHED   OFFERED   AGE
xdatabases.platform.mycompany.io   True          True      10s
```

**Step 2: Create the Composition (Implementation)**

```yaml
# composition-database-aws.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: database-aws
  labels:
    provider: aws
    crossplane.io/xrd: xdatabases.platform.mycompany.io
spec:
  compositeTypeRef:
    apiVersion: platform.mycompany.io/v1alpha1
    kind: XDatabase
  writeConnectionSecretsToNamespace: crossplane-system

  resources:
    # --- Security Group ---
    - name: security-group
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: SecurityGroup
        spec:
          forProvider:
            region: us-east-1
            description: "Database security group managed by Crossplane"
            vpcId: "vpc-0abc123def456"  # Replace with your VPC ID
            tags:
              ManagedBy: crossplane
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.region
          toFieldPath: spec.forProvider.region
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.environment
          toFieldPath: spec.forProvider.tags.Environment
        - type: CombineFromComposite
          combine:
            variables:
              - fromFieldPath: metadata.name
            strategy: string
            string:
              fmt: "sg-%s-db"
          toFieldPath: spec.forProvider.name

    # --- Security Group Ingress Rule ---
    - name: sg-rule-ingress
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: SecurityGroupRule
        spec:
          forProvider:
            region: us-east-1
            type: ingress
            fromPort: 5432
            toPort: 5432
            protocol: tcp
            cidrBlocks:
              - "10.0.0.0/8"
            description: "Allow database access from VPC"
            securityGroupIdSelector:
              matchControllerRef: true
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.region
          toFieldPath: spec.forProvider.region
        # Set port based on engine
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.engine
          toFieldPath: spec.forProvider.fromPort
          transforms:
            - type: map
              map:
                postgresql: "5432"
                mysql: "3306"
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.engine
          toFieldPath: spec.forProvider.toPort
          transforms:
            - type: map
              map:
                postgresql: "5432"
                mysql: "3306"

    # --- RDS Subnet Group ---
    - name: subnet-group
      base:
        apiVersion: rds.aws.upbound.io/v1beta1
        kind: SubnetGroup
        spec:
          forProvider:
            region: us-east-1
            description: "Subnet group for Crossplane-managed database"
            subnetIds:
              - "subnet-0abc123"  # Replace with your subnet IDs
              - "subnet-0def456"
            tags:
              ManagedBy: crossplane
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.region
          toFieldPath: spec.forProvider.region
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.environment
          toFieldPath: spec.forProvider.tags.Environment

    # --- RDS Instance ---
    - name: rds-instance
      base:
        apiVersion: rds.aws.upbound.io/v1beta2
        kind: Instance
        spec:
          forProvider:
            region: us-east-1
            dbName: appdb
            allocatedStorage: 20
            autoMinorVersionUpgrade: true
            backupRetentionPeriod: 7
            deletionProtection: false
            multiAz: false
            publiclyAccessible: false
            skipFinalSnapshot: true
            storageEncrypted: true
            storageType: gp3
            username: dbadmin
            autoGeneratePassword: true
            passwordSecretRef:
              namespace: crossplane-system
              key: password
            dbSubnetGroupNameSelector:
              matchControllerRef: true
            vpcSecurityGroupIdSelector:
              matchControllerRef: true
            tags:
              ManagedBy: crossplane
          writeConnectionSecretToRef:
            namespace: crossplane-system
      patches:
        # Region
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.region
          toFieldPath: spec.forProvider.region
        # Engine
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.engine
          toFieldPath: spec.forProvider.engine
        # Engine version
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.engineVersion
          toFieldPath: spec.forProvider.engineVersion
        # Storage
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
        # Instance class (map size to instance type)
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.size
          toFieldPath: spec.forProvider.instanceClass
          transforms:
            - type: map
              map:
                small: "db.t3.micro"
                medium: "db.r6g.large"
                large: "db.r6g.xlarge"
        # Multi-AZ for production
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.environment
          toFieldPath: spec.forProvider.multiAz
          transforms:
            - type: map
              map:
                dev: "false"
                staging: "false"
                production: "true"
        # Backup retention (longer for production)
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.environment
          toFieldPath: spec.forProvider.backupRetentionPeriod
          transforms:
            - type: map
              map:
                dev: "1"
                staging: "7"
                production: "30"
        # Connection secret name
        - type: CombineFromComposite
          combine:
            variables:
              - fromFieldPath: metadata.name
            strategy: string
            string:
              fmt: "%s-connection"
          toFieldPath: spec.writeConnectionSecretToRef.name
        # Publish endpoint to status
        - type: ToCompositeFieldPath
          fromFieldPath: status.atProvider.endpoint
          toFieldPath: status.endpoint
        - type: ToCompositeFieldPath
          fromFieldPath: status.atProvider.port
          toFieldPath: status.port
        - type: ToCompositeFieldPath
          fromFieldPath: spec.forProvider.instanceClass
          toFieldPath: status.instanceClass
      connectionDetails:
        - name: username
          fromFieldPath: spec.forProvider.username
        - name: password
          fromConnectionSecretKey: attribute.password
        - name: endpoint
          fromFieldPath: status.atProvider.endpoint
        - name: port
          fromFieldPath: status.atProvider.port
          type: FromFieldPath
```

```bash
kubectl apply -f composition-database-aws.yaml

# Verify
kubectl get composition
```

Expected output:
```
NAME           XR-KIND     XR-APIVERSION                      AGE
database-aws   XDatabase   platform.mycompany.io/v1alpha1     5s
```

**Step 3: Submit a Claim (Developer Experience)**

```yaml
# claim-my-database.yaml
apiVersion: platform.mycompany.io/v1alpha1
kind: Database
metadata:
  name: orders-db
  namespace: team-orders
spec:
  parameters:
    engine: postgresql
    engineVersion: "15.4"
    size: medium
    storageGB: 50
    environment: production
    region: us-east-1
  compositionSelector:
    matchLabels:
      provider: aws
  writeConnectionSecretToRef:
    name: orders-db-connection
```

```bash
# Create the namespace
kubectl create namespace team-orders

# Submit the claim
kubectl apply -f claim-my-database.yaml

# Watch provisioning
kubectl get database orders-db -n team-orders -w
```

Expected output:
```
NAME        SYNCED   READY   CONNECTION-SECRET       AGE
orders-db   True     False   orders-db-connection    10s
orders-db   True     False   orders-db-connection    2m
orders-db   True     True    orders-db-connection    8m
```

**Step 4: Inspect Created Resources**

```bash
# See all managed resources created by the composition
kubectl get managed -l crossplane.io/claim-name=orders-db

# View the composite resource
kubectl get xdatabase -o yaml

# Check connection secret
kubectl get secret orders-db-connection -n team-orders -o jsonpath='{.data}' | jq
```

Expected managed resources output:
```
NAME                                         READY   SYNCED   AGE
securitygroup.ec2/orders-db-xyz-sg           True    True     8m
securitygrouprule.ec2/orders-db-xyz-rule     True    True     8m
subnetgroup.rds/orders-db-xyz-subnet         True    True     8m
instance.rds/orders-db-xyz-rds               True    True     8m
```

**Step 5: Use the Connection Secret in an Application**

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-service
  namespace: team-orders
spec:
  replicas: 2
  selector:
    matchLabels:
      app: orders-service
  template:
    metadata:
      labels:
        app: orders-service
    spec:
      containers:
        - name: orders
          image: mycompany/orders-service:v1.2.0
          env:
            - name: DB_HOST
              valueFrom:
                secretKeyRef:
                  name: orders-db-connection
                  key: endpoint
            - name: DB_PORT
              valueFrom:
                secretKeyRef:
                  name: orders-db-connection
                  key: port
            - name: DB_USERNAME
              valueFrom:
                secretKeyRef:
                  name: orders-db-connection
                  key: username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: orders-db-connection
                  key: password
```

---

## Exercises

1. **Build a Storage API**: Create an XRD and Composition for an "ObjectStore" claim that provisions an S3 bucket with configurable versioning, encryption, and lifecycle rules. The developer should only specify: `name`, `versioning: true/false`, and `retentionDays`.

2. **Multi-Cloud Composition**: Create two Compositions for the same XRD -- one for AWS (RDS) and one for GCP (CloudSQL). The developer selects the cloud via a `compositionSelector` label. Test switching between clouds with the same claim.

3. **Environment Differentiation**: Extend the Database composition to behave differently based on environment: dev gets `db.t3.micro`, no Multi-AZ, 1-day backups; production gets `db.r6g.large`, Multi-AZ, 30-day backups, deletion protection enabled.

4. **Composition Validation**: Add validation to your XRD that prevents developers from requesting more than 100GB of storage in the dev environment. Use OpenAPI v3 schema constraints.

5. **Connection Secret Propagation**: Build a composition that creates a database and automatically creates a Kubernetes ConfigMap in the developer's namespace with the non-sensitive connection details (endpoint, port, database name).

---

## Knowledge Check

**Q1: What is the difference between an XR (Composite Resource) and an XRC (Claim)?**

<details>
<summary>Answer</summary>

An XR (Composite Resource) is cluster-scoped and represents the full composite resource with all its managed resources. An XRC (Claim) is namespace-scoped and represents a developer's request for that composite resource. Claims exist in the developer's namespace, while XRs exist at the cluster level. When a developer creates a Claim, Crossplane automatically creates the corresponding XR. Claims provide namespace-level isolation and RBAC, making them safe for multi-tenant clusters. Platform engineers work with XRDs and Compositions; developers work with Claims.
</details>

**Q2: How do patches work in a Composition and why are they important?**

<details>
<summary>Answer</summary>

Patches are the mechanism for flowing data between the composite resource (XR) and managed resources. `FromCompositeFieldPath` copies values from the XR spec into managed resources (e.g., mapping `spec.parameters.size` to `spec.forProvider.instanceClass`). `ToCompositeFieldPath` copies values back from managed resources to the XR status (e.g., copying the RDS endpoint to `status.endpoint`). Transforms can modify values during patching (e.g., mapping "small" to "db.t3.micro"). Patches are important because they enable parameterization -- the same Composition template can produce different infrastructure based on the claim parameters.
</details>

**Q3: Why would you create multiple Compositions for the same XRD?**

<details>
<summary>Answer</summary>

Multiple Compositions allow the same API (XRD) to be implemented differently based on context. Common reasons: (1) Multi-cloud support -- one Composition provisions on AWS (RDS), another on GCP (CloudSQL), same developer API. (2) Environment variations -- a "lightweight" composition for dev (single instance, minimal config) vs a "hardened" composition for production (Multi-AZ, encryption, monitoring). (3) Compliance -- different compositions for different regulatory environments (PCI vs non-PCI). Developers select a composition using `compositionSelector` labels or `compositionRef`.
</details>

**Q4: How does Crossplane handle connection secrets and why is this important?**

<details>
<summary>Answer</summary>

When managed resources produce connection details (endpoints, credentials, certificates), Crossplane can propagate them through the composition chain: managed resource -> XR -> claim -> Kubernetes Secret in the developer's namespace. The XRD defines `connectionSecretKeys` to specify which values to expose. The Composition's `connectionDetails` block maps managed resource fields to these keys. The claim's `writeConnectionSecretToRef` creates a Secret in the developer's namespace. This is important because it provides a secure, automated way to pass infrastructure credentials to applications without developers ever seeing raw cloud credentials or needing cloud console access.
</details>
