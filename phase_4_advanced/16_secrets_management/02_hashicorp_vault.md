# HashiCorp Vault

## Why This Matters in DevOps

HashiCorp Vault is the industry standard for secrets management in production environments. It solves problems that simple secret stores (environment variables, AWS Secrets Manager) cannot: dynamic credential generation, encryption as a service, PKI certificate management, and fine-grained access policies. When your organization manages hundreds of services across multiple environments, Vault becomes the central authority for all sensitive data. Understanding Vault deeply -- not just basic key/value storage but dynamic secrets, transit encryption, and policy design -- is what separates a DevOps engineer from a platform engineer.

---

## Core Concepts

### What Is Vault?

Vault is a secrets management platform that provides centralized secret storage, dynamic secret generation, encryption as a service, and identity-based access control.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Vault Server                     │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │              API / CLI / UI                   │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │                               │
│  ┌──────────────────▼────────────────────────────┐  │
│  │           Authentication Layer                │  │
│  │  ┌────────┐ ┌────────┐ ┌──────┐ ┌──────────┐ │  │
│  │  │ Token  │ │  K8s   │ │ LDAP │ │ AppRole  │ │  │
│  │  └────────┘ └────────┘ └──────┘ └──────────┘ │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │                               │
│  ┌──────────────────▼────────────────────────────┐  │
│  │             Policy Engine                     │  │
│  │    "Who can access what, and how?"            │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │                               │
│  ┌──────────────────▼────────────────────────────┐  │
│  │            Secret Engines                     │  │
│  │  ┌─────┐ ┌─────────┐ ┌────────┐ ┌─────────┐ │  │
│  │  │ KV  │ │Database │ │Transit │ │  PKI    │ │  │
│  │  │v1/v2│ │(Dynamic)│ │(EaaS)  │ │(Certs)  │ │  │
│  │  └─────┘ └─────────┘ └────────┘ └─────────┘ │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │                               │
│  ┌──────────────────▼────────────────────────────┐  │
│  │           Storage Backend                     │  │
│  │  Consul │ Raft │ S3 │ DynamoDB │ PostgreSQL   │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Core Components

**Storage Backends**: Where Vault stores encrypted data. Raft (integrated storage) is the recommended choice for production -- it provides built-in HA without external dependencies.

**Secret Engines**: Plugins that generate, store, or encrypt data.
- **KV (Key-Value)**: Store static secrets with versioning
- **Database**: Generate short-lived database credentials on demand
- **Transit**: Encrypt/decrypt data without storing it (encryption as a service)
- **PKI**: Generate TLS certificates
- **AWS/Azure/GCP**: Generate cloud IAM credentials dynamically

**Auth Methods**: How clients prove their identity to Vault.
- **Token**: Direct token authentication
- **Kubernetes**: Authenticate using K8s service account tokens
- **AppRole**: Application-based authentication (role ID + secret ID)
- **LDAP/OIDC**: Enterprise directory integration
- **AWS IAM**: Authenticate using AWS IAM roles

**Policies**: HCL rules that define who can access what.

```hcl
# policy: read-only access to app secrets
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

# policy: full access for platform team
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# policy: database credential generation
path "database/creds/myapp-role" {
  capabilities = ["read"]
}
```

---

## Step-by-Step Practical

### Installing and Configuring Vault

**Step 1: Install Vault (Dev Mode for Learning)**

```bash
# Install Vault
# macOS
brew install vault

# Linux
curl -fsSL https://releases.hashicorp.com/vault/1.17.0/vault_1.17.0_linux_amd64.zip -o vault.zip
unzip vault.zip
sudo mv vault /usr/local/bin/

# Start in dev mode (NOT for production)
vault server -dev -dev-root-token-id="root"
```

In another terminal:
```bash
# Configure client
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Verify
vault status
```

Expected output:
```
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.17.0
Storage Type    inmem
Cluster Name    vault-cluster-abc123
```

**Step 2: Key/Value Secrets Engine**

```bash
# Enable KV v2 secrets engine (enabled by default in dev mode at secret/)
vault secrets enable -path=secret kv-v2

# Store a secret
vault kv put secret/myapp/config \
  db_host="db.production.internal" \
  db_port="5432" \
  db_name="appdb" \
  db_username="app_user" \
  db_password="SuperSecretPassword123!"

# Read a secret
vault kv get secret/myapp/config

# Read specific field
vault kv get -field=db_password secret/myapp/config

# Read as JSON
vault kv get -format=json secret/myapp/config
```

Expected output:
```
======= Secret Path =======
secret/data/myapp/config

======= Metadata =======
Key                Value
---                -----
created_time       2024-01-15T10:30:00.000000Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

====== Data ======
Key             Value
---             -----
db_host         db.production.internal
db_name         appdb
db_password     SuperSecretPassword123!
db_port         5432
db_username     app_user
```

```bash
# Update a secret (creates new version)
vault kv put secret/myapp/config \
  db_host="db.production.internal" \
  db_port="5432" \
  db_name="appdb" \
  db_username="app_user" \
  db_password="NewRotatedPassword456!"

# View version history
vault kv metadata get secret/myapp/config

# Read a specific version
vault kv get -version=1 secret/myapp/config

# Delete a version (soft delete)
vault kv delete -versions=1 secret/myapp/config

# Permanently destroy a version
vault kv destroy -versions=1 secret/myapp/config
```

**Step 3: Dynamic Database Credentials**

```bash
# Enable the database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/myapp-db \
  plugin_name=postgresql-database-plugin \
  allowed_roles="myapp-readonly,myapp-readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@db.production.internal:5432/appdb?sslmode=require" \
  username="vault_admin" \
  password="VaultAdminPassword"

# Create a read-only role (credentials expire after 1 hour)
vault write database/roles/myapp-readonly \
  db_name=myapp-db \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  revocation_statements="REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM \"{{name}}\"; DROP ROLE IF EXISTS \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Create a read-write role
vault write database/roles/myapp-readwrite \
  db_name=myapp-db \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  revocation_statements="REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM \"{{name}}\"; DROP ROLE IF EXISTS \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="4h"

# Generate dynamic credentials
vault read database/creds/myapp-readonly
```

Expected output:
```
Key                Value
---                -----
lease_id           database/creds/myapp-readonly/abc123def456
lease_duration     1h
lease_renewable    true
password           A1a-aBcDeFgHiJkLmNoP
username           v-token-myapp-re-abc123-1705312200
```

```bash
# Each read generates unique credentials
vault read database/creds/myapp-readonly
# Different username and password!

# Revoke credentials early
vault lease revoke database/creds/myapp-readonly/abc123def456

# Revoke ALL credentials for a role
vault lease revoke -prefix database/creds/myapp-readonly
```

**Step 4: Transit Engine (Encryption as a Service)**

```bash
# Enable transit engine
vault secrets enable transit

# Create an encryption key
vault write -f transit/keys/myapp-encryption

# Encrypt data (base64-encoded plaintext)
vault write transit/encrypt/myapp-encryption \
  plaintext=$(echo -n "sensitive-credit-card-4242424242424242" | base64)
```

Expected output:
```
Key           Value
---           -----
ciphertext    vault:v1:8SDd3WHDOjf7mq69CyCqYjBXAiQQAVZRkFM13ok481zoCmHnSeDX9vyf7w==
key_version   1
```

```bash
# Decrypt data
vault write transit/decrypt/myapp-encryption \
  ciphertext="vault:v1:8SDd3WHDOjf7mq69CyCqYjBXAiQQAVZRkFM13ok481zoCmHnSeDX9vyf7w=="
```

Expected output:
```
Key          Value
---          -----
plaintext    c2Vuc2l0aXZlLWNyZWRpdC1jYXJkLTQyNDI0MjQyNDI0MjQyNDI=
```

```bash
# Decode the base64
echo "c2Vuc2l0aXZlLWNyZWRpdC1jYXJkLTQyNDI0MjQyNDI0MjQyNDI=" | base64 -d
# Output: sensitive-credit-card-4242424242424242

# Rotate the encryption key
vault write -f transit/keys/myapp-encryption/rotate

# Re-encrypt with new key version (rewrapping)
vault write transit/rewrap/myapp-encryption \
  ciphertext="vault:v1:8SDd3WHDOjf7mq69CyCqYjBXAiQQAVZRkFM13ok481zoCmHnSeDX9vyf7w=="
# Returns vault:v2:... (same plaintext, new key version)
```

**Step 5: Application Integration (Python)**

```python
# vault_client.py
"""Vault integration for Python applications."""

import hvac
import os


def get_vault_client():
    """Create an authenticated Vault client."""
    client = hvac.Client(
        url=os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200'),
        token=os.environ.get('VAULT_TOKEN'),
    )
    assert client.is_authenticated(), "Vault authentication failed"
    return client


def get_static_secret(path: str, key: str) -> str:
    """Read a static KV secret."""
    client = get_vault_client()
    response = client.secrets.kv.v2.read_secret_version(path=path)
    return response['data']['data'][key]


def get_database_credentials(role: str) -> dict:
    """Get dynamic database credentials."""
    client = get_vault_client()
    response = client.secrets.database.generate_credentials(name=role)
    return {
        'username': response['data']['username'],
        'password': response['data']['password'],
        'lease_id': response['lease_id'],
        'lease_duration': response['lease_duration'],
    }


def encrypt_data(key_name: str, plaintext: str) -> str:
    """Encrypt data using Vault Transit."""
    import base64
    client = get_vault_client()
    response = client.secrets.transit.encrypt_data(
        name=key_name,
        plaintext=base64.b64encode(plaintext.encode()).decode(),
    )
    return response['data']['ciphertext']


# Usage
if __name__ == "__main__":
    # Static secret
    db_password = get_static_secret("myapp/config", "db_password")
    print(f"Static DB password: {db_password[:4]}****")

    # Dynamic credentials
    creds = get_database_credentials("myapp-readonly")
    print(f"Dynamic username: {creds['username']}")
    print(f"Expires in: {creds['lease_duration']}s")

    # Encryption
    ciphertext = encrypt_data("myapp-encryption", "SSN: 123-45-6789")
    print(f"Encrypted: {ciphertext[:30]}...")
```

---

## Exercises

1. **Vault Setup**: Install Vault in dev mode. Create a KV secret with 5 key-value pairs. Update one value and verify you can read both the current and previous versions.

2. **Dynamic Credentials**: Configure the database secrets engine with a PostgreSQL database (use Docker). Create two roles (readonly, readwrite) with different TTLs. Generate credentials for each and verify they work.

3. **Transit Encryption**: Set up the transit engine. Write a Python script that encrypts and decrypts user data (email, phone) using Vault Transit. Implement key rotation and verify old ciphertext can still be decrypted.

4. **Policy Design**: Write Vault policies for three personas: (a) developer (read-only access to staging secrets), (b) CI/CD pipeline (read access to production secrets, generate DB creds), (c) platform admin (full access). Test each policy.

5. **Audit Trail**: Enable Vault audit logging. Perform several operations and review the audit log to understand what is captured.

---

## Knowledge Check

**Q1: What are dynamic secrets and why are they more secure than static secrets?**

<details>
<summary>Answer</summary>

Dynamic secrets are credentials generated on-demand by Vault for each client request. For example, when an application needs database access, Vault creates a unique username/password pair that expires after a configured TTL (e.g., 1 hour). They are more secure because: (1) each consumer gets unique credentials, enabling attribution if they are misused, (2) credentials automatically expire, limiting the exploitation window, (3) no manual rotation needed -- new credentials are generated every session, (4) revocation is granular -- you can revoke one application's credentials without affecting others, (5) there is no shared password that multiple systems know.
</details>

**Q2: What is the Transit secrets engine and when would you use it?**

<details>
<summary>Answer</summary>

The Transit engine provides encryption as a service -- it encrypts and decrypts data without storing it. You send plaintext to Vault, it returns ciphertext. You send ciphertext, it returns plaintext. The encryption key never leaves Vault. Use it when: (1) you need to encrypt sensitive data at the application level (PII, credit cards, SSNs), (2) you want centralized key management without distributing encryption keys to applications, (3) you need key rotation without re-encrypting all data (rewrap operation), (4) compliance requires that encryption keys are managed in a dedicated system with audit trails.
</details>

**Q3: How does AppRole authentication work?**

<details>
<summary>Answer</summary>

AppRole is designed for machine-to-machine authentication. It has two components: (1) Role ID -- a static identifier for the application (like a username), stored in configuration, (2) Secret ID -- a dynamic, single-use or limited-use token (like a password), delivered through a trusted channel. The application presents both to Vault to receive a Vault token with policies attached to that AppRole. The separation allows: the CI/CD pipeline to deliver the Secret ID at deployment time (short-lived), while the Role ID is baked into configuration. If the Role ID is compromised alone, it is useless without a valid Secret ID.
</details>

**Q4: What storage backend should you use for production Vault?**

<details>
<summary>Answer</summary>

Raft (Integrated Storage) is the recommended backend for production. It is built into Vault, requires no external dependencies, supports automatic clustering and leader election, and provides consistent performance. Previously, Consul was the recommended backend, but Raft has superseded it for most deployments. Raft stores data locally on each Vault node with consensus-based replication. For production, run a minimum of 3 or 5 Vault nodes for high availability. Avoid using S3, DynamoDB, or PostgreSQL as storage backends -- they work but do not support HA without additional configuration.
</details>
