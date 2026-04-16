# Infisical

## Why This Matters in DevOps

HashiCorp Vault is powerful but complex -- it requires unsealing, policy management in HCL, and significant operational overhead. For many teams, especially startups and mid-size companies, this complexity is a barrier to adopting proper secrets management. Infisical is a modern, open-source alternative that provides 80% of Vault's value with 20% of the complexity. It has a developer-friendly UI, native SDK support, environment-based secret management, and seamless CI/CD integration. Understanding Infisical gives you a practical tool you can deploy in hours instead of weeks.

---

## Core Concepts

### What Is Infisical?

Infisical is an open-source secrets management platform designed for developer experience. It stores, syncs, and manages secrets across your team, environments, and infrastructure.

```
┌──────────────────────────────────────────────────┐
│                 Infisical Server                 │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │              Web Dashboard                 │  │
│  │  Projects → Environments → Secrets         │  │
│  └─────────────────┬──────────────────────────┘  │
│                    │                             │
│  ┌─────────────────▼──────────────────────────┐  │
│  │           API Layer                        │  │
│  │  REST API + SDKs (Python, Node, Go, etc)   │  │
│  └─────────────────┬──────────────────────────┘  │
│                    │                             │
│  ┌─────────────────▼──────────────────────────┐  │
│  │        Encryption Layer                    │  │
│  │  End-to-end encryption (client-side)       │  │
│  │  AES-256-GCM per secret                    │  │
│  └─────────────────┬──────────────────────────┘  │
│                    │                             │
│  ┌─────────────────▼──────────────────────────┐  │
│  │         Storage (PostgreSQL)               │  │
│  │  Encrypted secrets, audit logs, metadata   │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
         │              │              │
    ┌────▼────┐   ┌─────▼────┐  ┌─────▼─────┐
    │   CLI   │   │   SDKs   │  │ K8s       │
    │ infisical│   │Python/JS │  │ Operator  │
    └─────────┘   └──────────┘  └───────────┘
```

### Why Infisical Over Vault?

| Aspect | Vault | Infisical |
|---|---|---|
| Setup time | Hours to days | Minutes |
| UI | Functional but basic | Modern, developer-friendly |
| Learning curve | Steep (HCL policies, unsealing) | Gentle (web UI, SDKs) |
| Secret organization | Paths and mounts | Projects, environments, folders |
| Team features | Enterprise license | Built-in (open source) |
| Audit logs | Enterprise feature | Built-in |
| Secret versioning | KV v2 only | All secrets |
| Dynamic secrets | Yes (many engines) | Limited (growing) |
| Encryption as a service | Yes (Transit) | No |
| PKI/Certificate mgmt | Yes | No |
| Operational overhead | High (unsealing, HA, backups) | Low (single binary or container) |

Choose Infisical when: you need secrets management quickly, your team values developer experience, and you do not need dynamic secrets or encryption as a service.

Choose Vault when: you need dynamic credentials, transit encryption, PKI, or enterprise-grade features.

### Architecture

Infisical's architecture is straightforward:

- **Server**: Node.js application with PostgreSQL backend
- **Encryption**: Secrets are encrypted client-side before being stored
- **Projects**: Organizational units containing secrets
- **Environments**: dev, staging, production (customizable)
- **Folders**: Organize secrets within environments
- **Service Tokens / Machine Identities**: For programmatic access

---

## Step-by-Step Practical

### Installing Infisical

**Option 1: Docker Compose (Recommended for Getting Started)**

```bash
# Clone the repository
git clone https://github.com/Infisical/infisical.git
cd infisical

# Start with Docker Compose
docker compose -f docker-compose.prod.yml up -d
```

Or create your own compose file:

```yaml
# docker-compose.yaml
version: "3.9"
services:
  infisical:
    image: infisical/infisical:latest
    ports:
      - "8080:8080"
    environment:
      - ENCRYPTION_KEY=your-256-bit-encryption-key-here
      - AUTH_SECRET=your-auth-secret-for-jwt-here
      - DB_CONNECTION_URI=postgresql://infisical:password@postgres:5432/infisical
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: infisical
      POSTGRES_PASSWORD: password
      POSTGRES_DB: infisical
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

```bash
docker compose up -d

# Access the UI at http://localhost:8080
# Create your account and first project
```

**Option 2: Helm on Kubernetes**

```bash
helm repo add infisical https://dl.cloudsmith.io/public/infisical/helm-charts/helm/charts/
helm repo update

helm install infisical infisical/infisical \
  --namespace infisical \
  --create-namespace \
  --set infisical.encryption.key="$(openssl rand -hex 16)" \
  --set infisical.auth.secret="$(openssl rand -hex 16)"
```

### Setting Up Projects and Secrets

**Step 1: Install the CLI**

```bash
# macOS
brew install infisical/get-cli/infisical

# Linux
curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo bash
sudo apt-get install infisical

# Verify
infisical --version
```

**Step 2: Login and Initialize**

```bash
# Login to Infisical
infisical login

# Initialize a project in your code directory
cd /path/to/your/project
infisical init
# Select your project from the list
```

This creates `.infisical.json`:
```json
{
  "workspaceId": "abc123def456",
  "defaultEnvironment": "dev",
  "gitBranchToEnvironmentMapping": null
}
```

**Step 3: Manage Secrets via CLI**

```bash
# Set secrets for development
infisical secrets set \
  DB_HOST=localhost \
  DB_PORT=5432 \
  DB_NAME=myapp_dev \
  DB_USERNAME=dev_user \
  DB_PASSWORD=DevPassword123 \
  REDIS_URL=redis://localhost:6379 \
  API_KEY=sk-test-abc123 \
  --env=dev

# Set secrets for production
infisical secrets set \
  DB_HOST=db.production.internal \
  DB_PORT=5432 \
  DB_NAME=myapp_prod \
  DB_USERNAME=prod_user \
  DB_PASSWORD=ProdSuperSecret456! \
  REDIS_URL=redis://redis.production.internal:6379 \
  API_KEY=sk-live-xyz789 \
  --env=prod

# List secrets
infisical secrets list --env=dev
```

Expected output:
```
┌──────────────┬──────────────────────────────┬─────┐
│ SECRET NAME  │ SECRET VALUE                 │ ENV │
├──────────────┼──────────────────────────────┼─────┤
│ DB_HOST      │ localhost                    │ dev │
│ DB_PORT      │ 5432                         │ dev │
│ DB_NAME      │ myapp_dev                    │ dev │
│ DB_USERNAME  │ dev_user                     │ dev │
│ DB_PASSWORD  │ DevPa***                     │ dev │
│ REDIS_URL    │ redis://localhost:6379       │ dev │
│ API_KEY      │ sk-te***                     │ dev │
└──────────────┴──────────────────────────────┴─────┘
```

**Step 4: Run Applications with Secrets**

```bash
# Inject secrets as environment variables and run your app
infisical run --env=dev -- python app.py

# Or with Node.js
infisical run --env=dev -- npm start

# Or with Docker
infisical run --env=prod -- docker compose up
```

### SDK Integration (Python)

**Step 1: Install the SDK**

```bash
pip install infisical-python
```

**Step 2: Integrate with Your Application**

```python
# app.py
"""Application with Infisical secrets integration."""

from infisical_python import InfisicalClient
import os


def get_secrets():
    """Fetch secrets from Infisical."""
    client = InfisicalClient(
        token=os.environ.get("INFISICAL_TOKEN"),
        site_url="https://infisical.mycompany.com",  # Self-hosted URL
    )

    # Get a single secret
    db_password = client.get_secret(
        secret_name="DB_PASSWORD",
        environment="production",
        project_id="your-project-id",
        path="/",
    )

    return {
        "db_host": client.get_secret("DB_HOST", "production", "your-project-id").secret_value,
        "db_port": client.get_secret("DB_PORT", "production", "your-project-id").secret_value,
        "db_name": client.get_secret("DB_NAME", "production", "your-project-id").secret_value,
        "db_username": client.get_secret("DB_USERNAME", "production", "your-project-id").secret_value,
        "db_password": db_password.secret_value,
    }


def create_db_connection():
    """Create a database connection using Infisical secrets."""
    import psycopg2

    secrets = get_secrets()

    conn = psycopg2.connect(
        host=secrets["db_host"],
        port=int(secrets["db_port"]),
        dbname=secrets["db_name"],
        user=secrets["db_username"],
        password=secrets["db_password"],
    )
    return conn


if __name__ == "__main__":
    secrets = get_secrets()
    print(f"Connected to: {secrets['db_host']}:{secrets['db_port']}/{secrets['db_name']}")
```

### Kubernetes Operator Integration

```bash
# Install the Infisical Kubernetes Operator
helm install infisical-secrets-operator infisical/secrets-operator \
  --namespace infisical \
  --create-namespace
```

```yaml
# infisical-secret.yaml
apiVersion: secrets.infisical.com/v1alpha1
kind: InfisicalSecret
metadata:
  name: myapp-secrets
  namespace: myapp
spec:
  hostAPI: https://infisical.mycompany.com/api
  resyncInterval: 60  # Check for updates every 60 seconds
  authentication:
    universalAuth:
      secretsScope:
        projectSlug: my-project
        envSlug: production
        secretsPath: "/"
      credentialsRef:
        secretName: infisical-machine-identity
        secretNamespace: myapp
  managedSecretReference:
    secretName: myapp-k8s-secrets
    secretNamespace: myapp
    secretType: Opaque
```

```bash
# Create the machine identity credential
kubectl create secret generic infisical-machine-identity \
  --namespace myapp \
  --from-literal=clientId="your-client-id" \
  --from-literal=clientSecret="your-client-secret"

# Apply the InfisicalSecret
kubectl apply -f infisical-secret.yaml

# Verify the K8s secret was created
kubectl get secret myapp-k8s-secrets -n myapp -o yaml
```

### CI/CD Integration

**GitHub Actions:**

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Fetch secrets from Infisical
        uses: Infisical/secrets-action@v1.0.7
        with:
          method: "universal-auth"
          client-id: ${{ secrets.INFISICAL_CLIENT_ID }}
          client-secret: ${{ secrets.INFISICAL_CLIENT_SECRET }}
          env-slug: "production"
          project-slug: "my-project"

      - name: Deploy
        run: |
          echo "Deploying with DB_HOST=$DB_HOST"
          # Secrets are injected as environment variables
```

---

## Exercises

1. **Quick Start**: Install Infisical using Docker Compose. Create a project with three environments (dev, staging, production). Add 5 secrets to each environment with different values.

2. **Python Integration**: Build a Flask or FastAPI application that reads all its configuration from Infisical using the Python SDK. Deploy it locally and verify it works across environment switches.

3. **Kubernetes Operator**: Deploy the Infisical Kubernetes Operator. Create an InfisicalSecret resource that syncs production secrets to a Kubernetes Secret. Deploy a pod that uses the synced secret.

4. **CI/CD Pipeline**: Set up a GitHub Actions workflow that pulls secrets from Infisical and uses them during a build/deploy step. Verify that secrets are not logged in CI output.

5. **Migration from .env**: Take an existing project that uses .env files. Migrate all secrets to Infisical, update the application to use the Infisical CLI (`infisical run`), and remove the .env files from the repository.

---

## Knowledge Check

**Q1: When should you choose Infisical over Vault?**

<details>
<summary>Answer</summary>

Choose Infisical when: (1) you need to get secrets management running quickly (hours, not days), (2) your team values developer experience and a modern UI, (3) you primarily need static secret storage with environment-based organization, (4) you want built-in audit logs and versioning without paying for an enterprise license, (5) your team is small to mid-size and does not need dynamic credential generation, transit encryption, or PKI management. Infisical is ideal for startups and teams transitioning from .env files to proper secrets management.
</details>

**Q2: How does Infisical's encryption model work?**

<details>
<summary>Answer</summary>

Infisical uses end-to-end encryption. Secrets are encrypted client-side (in the browser, CLI, or SDK) before being sent to the server. The server stores only encrypted data and cannot read the secrets. Encryption uses AES-256-GCM with keys derived from the user's credentials or machine identity tokens. This means even if the Infisical database is compromised, the attacker gets only encrypted data. The encryption key management differs from Vault -- Vault uses a master key with Shamir's secret sharing, while Infisical derives keys from authentication credentials.
</details>

**Q3: How does the Infisical Kubernetes Operator compare to Vault's Agent Injector?**

<details>
<summary>Answer</summary>

The Infisical Kubernetes Operator creates and syncs Kubernetes Secret objects from Infisical. Pods consume secrets through standard Kubernetes mechanisms (envFrom, secretKeyRef). It is simpler than Vault's Agent Injector because: (1) no sidecar container per pod (lower resource overhead), (2) secrets appear as standard K8s Secrets (compatible with all existing workloads), (3) the operator handles synchronization (configurable resync interval). The tradeoff is: (1) secrets exist as K8s Secrets (base64 in etcd), which is less secure than Vault's in-memory file approach, (2) no support for dynamic secrets or template rendering.
</details>

**Q4: What is the `infisical run` command and why is it useful?**

<details>
<summary>Answer</summary>

`infisical run --env=<environment> -- <command>` fetches secrets from Infisical and injects them as environment variables into the specified command's process. For example, `infisical run --env=prod -- python app.py` makes all production secrets available as environment variables to the Python process. It is useful because: (1) no code changes needed -- existing apps that read from environment variables work immediately, (2) secrets never touch disk (injected into process memory only), (3) environment switching is a single flag change, (4) it works with any language or framework.
</details>
