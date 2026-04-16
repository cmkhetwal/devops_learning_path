# Backstage

## Why This Matters in DevOps

When your organization has hundreds of services, developers waste hours trying to find documentation, understand service ownership, or figure out how to create a new project. Backstage, created by Spotify and donated to the CNCF, solves this by providing a single developer portal where all services, APIs, documentation, and tooling are centralized. It is the most widely adopted developer portal in the industry, and understanding it is essential for any platform engineering initiative.

---

## Core Concepts

### What Is Backstage?

Backstage is an open-source framework for building developer portals. It provides a software catalog, documentation system, software templates, and a plugin architecture for extending functionality.

```
┌──────────────────────────────────────────────────────┐
│                    Backstage                         │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Software   │  │  Software    │  │  TechDocs  │ │
│  │  Catalog    │  │  Templates   │  │            │ │
│  │             │  │              │  │  Docs as   │ │
│  │  Systems    │  │  Scaffold    │  │  code      │ │
│  │  Components │  │  new         │  │            │ │
│  │  APIs       │  │  services    │  │  Markdown  │ │
│  │  Resources  │  │              │  │  → portal  │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              Plugin Ecosystem                │   │
│  │  Kubernetes │ ArgoCD │ GitHub │ PagerDuty    │   │
│  │  Grafana │ Vault │ Cost │ CI/CD │ Custom     │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser                                            │
│  ┌───────────────────────────────────────────────┐  │
│  │  Backstage Frontend (React SPA)               │  │
│  │  ├── Catalog pages                            │  │
│  │  ├── Template wizard                          │  │
│  │  ├── TechDocs viewer                          │  │
│  │  └── Plugin UIs                               │  │
│  └───────────────────┬───────────────────────────┘  │
└──────────────────────┼──────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────┐
│  Backstage Backend (Node.js)                        │
│  ├── Catalog processor (reads catalog-info.yaml)    │
│  ├── Template engine (scaffolder)                   │
│  ├── TechDocs generator (mkdocs)                    │
│  ├── Auth (GitHub, Google, OIDC)                    │
│  └── Plugin backends                                │
│                                                     │
│  Database: PostgreSQL                               │
└─────────────────────────────────────────────────────┘
```

### Software Catalog

The catalog is the core of Backstage. It contains all entities in your organization:

```yaml
# Entity kinds in the catalog:
Component  → A software component (service, website, library)
API        → An API exposed by a component
System     → A collection of related components
Domain     → A business area containing systems
Resource   → Infrastructure (database, S3 bucket, queue)
Group      → A team or organizational unit
User       → An individual person
```

Entity relationships form a graph:
```
Domain: "E-Commerce"
  └── System: "Orders Platform"
       ├── Component: "orders-service" (service)
       │    ├── API: "orders-api" (provides)
       │    ├── Resource: "orders-db" (consumes)
       │    └── Component: "orders-worker" (depends on)
       └── Component: "orders-frontend" (website)
            └── API: "orders-api" (consumes)
```

---

## Step-by-Step Practical

### Setting Up Backstage

**Step 1: Create a Backstage App**

```bash
# Prerequisites
node --version  # v18 or v20
yarn --version  # v1.x (classic)

# Create Backstage app
npx @backstage/create-app@latest

# Follow prompts:
# ? Enter a name for the app: my-backstage
# Creating the app...

cd my-backstage
```

Project structure:
```
my-backstage/
├── app-config.yaml          # Main configuration
├── app-config.production.yaml
├── packages/
│   ├── app/                 # Frontend React app
│   │   └── src/
│   └── backend/             # Backend Node.js app
│       └── src/
├── plugins/                 # Custom plugins
├── catalog-info.yaml        # Backstage's own catalog entry
└── package.json
```

**Step 2: Configure the Catalog**

```yaml
# app-config.yaml
app:
  title: MyCompany Developer Portal
  baseUrl: http://localhost:3000

organization:
  name: MyCompany

backend:
  baseUrl: http://localhost:7007
  database:
    client: pg
    connection:
      host: localhost
      port: 5432
      user: backstage
      password: backstage
      database: backstage

catalog:
  import:
    entityFilename: catalog-info.yaml
    pullRequestBranchName: backstage-integration
  rules:
    - allow: [Component, System, API, Resource, Domain, Group, User]
  locations:
    # Local catalog entities
    - type: file
      target: ./catalog-entities/all.yaml

    # GitHub discovery (scan all repos for catalog-info.yaml)
    - type: github-discovery
      target: https://github.com/mycompany/*/blob/main/catalog-info.yaml

    # Organization teams and users
    - type: github-org
      target: https://github.com/mycompany
```

**Step 3: Create Catalog Entities**

```yaml
# catalog-entities/orders-service.yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders-service
  description: "Handles order processing, payment validation, and fulfillment"
  annotations:
    github.com/project-slug: mycompany/orders-service
    backstage.io/techdocs-ref: dir:.
    argocd/app-name: orders-service-prod
    grafana/dashboard-selector: "orders-service"
    pagerduty.com/service-id: PABC123
  tags:
    - python
    - fastapi
    - critical
  links:
    - url: https://grafana.mycompany.com/d/orders
      title: Grafana Dashboard
    - url: https://mycompany.pagerduty.com/services/PABC123
      title: PagerDuty
spec:
  type: service
  lifecycle: production
  owner: team-orders
  system: orders-platform
  dependsOn:
    - resource:orders-db
    - component:payment-gateway
  providesApis:
    - orders-api
---
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: orders-api
  description: "REST API for order management"
spec:
  type: openapi
  lifecycle: production
  owner: team-orders
  system: orders-platform
  definition:
    $text: https://raw.githubusercontent.com/mycompany/orders-service/main/openapi.yaml
---
apiVersion: backstage.io/v1alpha1
kind: Resource
metadata:
  name: orders-db
  description: "PostgreSQL database for order data"
spec:
  type: database
  owner: team-orders
  system: orders-platform
---
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: orders-platform
  description: "Complete order processing platform"
spec:
  owner: team-orders
  domain: e-commerce
---
apiVersion: backstage.io/v1alpha1
kind: Group
metadata:
  name: team-orders
  description: "Order Processing Team"
spec:
  type: team
  children: []
  members:
    - jane.doe
    - john.smith
```

**Step 4: Add a `catalog-info.yaml` to Each Repository**

```yaml
# In each service's Git repo root: catalog-info.yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: user-service
  description: "User authentication and profile management"
  annotations:
    github.com/project-slug: mycompany/user-service
    backstage.io/techdocs-ref: dir:.
  tags:
    - python
    - fastapi
spec:
  type: service
  lifecycle: production
  owner: team-identity
  system: identity-platform
  providesApis:
    - users-api
```

**Step 5: Create Software Templates**

```yaml
# templates/python-fastapi/template.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: python-fastapi-service
  title: Python FastAPI Microservice
  description: Create a new Python FastAPI microservice with CI/CD, monitoring, and Kubernetes deployment
  tags:
    - python
    - fastapi
    - recommended
spec:
  owner: platform-team
  type: service

  parameters:
    - title: Service Information
      required:
        - name
        - description
        - owner
      properties:
        name:
          title: Service Name
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "Lowercase, hyphens only (e.g., order-processor)"
        description:
          title: Description
          type: string
        owner:
          title: Owner Team
          type: string
          ui:field: OwnerPicker
          ui:options:
            catalogFilter:
              kind: Group

    - title: Infrastructure
      properties:
        needsDatabase:
          title: Needs PostgreSQL Database?
          type: boolean
          default: true
        needsRedis:
          title: Needs Redis Cache?
          type: boolean
          default: false
        environment:
          title: Initial Environment
          type: string
          enum: ["dev", "staging"]
          default: "dev"

  steps:
    # Generate project from template
    - id: fetch-template
      name: Fetch Template
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          description: ${{ parameters.description }}
          owner: ${{ parameters.owner }}
          needsDatabase: ${{ parameters.needsDatabase }}
          needsRedis: ${{ parameters.needsRedis }}

    # Create GitHub repository
    - id: publish
      name: Create Repository
      action: publish:github
      input:
        repoUrl: github.com?repo=${{ parameters.name }}&owner=mycompany
        description: ${{ parameters.description }}
        defaultBranch: main
        repoVisibility: internal

    # Create ArgoCD application
    - id: create-argocd-app
      name: Create ArgoCD Application
      action: argocd:create-resources
      input:
        appName: ${{ parameters.name }}-${{ parameters.environment }}
        argoInstance: production
        namespace: ${{ parameters.name }}
        repoUrl: ${{ steps.publish.output.remoteUrl }}
        path: deploy/

    # Register in catalog
    - id: register
      name: Register in Catalog
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml

  output:
    links:
      - title: Repository
        url: ${{ steps.publish.output.remoteUrl }}
      - title: Open in Backstage
        icon: catalog
        entityRef: ${{ steps.register.output.entityRef }}
```

**Step 6: Run Backstage**

```bash
# Start in development mode
yarn dev

# Access at http://localhost:3000
```

Expected experience:
```
1. Open http://localhost:3000
2. See the Software Catalog with all registered services
3. Click "Create..." → see available templates
4. Select "Python FastAPI Microservice"
5. Fill in the form (name, team, database needs)
6. Click "Create" → Backstage:
   - Creates GitHub repository from template
   - Sets up ArgoCD application
   - Registers service in catalog
   - Developer gets a link to their new repo
```

---

## Exercises

1. **Backstage Setup**: Create a Backstage instance and register at least 5 services in the catalog. Include systems, APIs, and resources. Explore the dependency graph visualization.

2. **Software Template**: Create a software template for your most common service type. Include a skeleton project with Dockerfile, CI/CD pipeline, Helm chart, and catalog-info.yaml.

3. **TechDocs**: Set up TechDocs for one of your services. Write documentation in Markdown, configure mkdocs.yml, and verify it renders correctly in Backstage.

4. **Plugin Integration**: Install and configure at least two Backstage plugins (e.g., Kubernetes, ArgoCD, GitHub Actions, PagerDuty). Verify they show real-time data in service pages.

5. **Catalog Discovery**: Configure GitHub discovery to automatically find and register all services in your GitHub organization that have a `catalog-info.yaml` file.

---

## Knowledge Check

**Q1: What are the three core features of Backstage?**

<details>
<summary>Answer</summary>

(1) **Software Catalog** -- a centralized inventory of all software (services, APIs, libraries, infrastructure) with ownership, metadata, and dependency information. It answers "what services exist, who owns them, and how are they connected?" (2) **Software Templates (Scaffolder)** -- a self-service tool that generates new projects from templates, including repository creation, CI/CD setup, and catalog registration. It enables golden paths. (3) **TechDocs** -- a docs-as-code solution that renders Markdown documentation from service repositories directly in Backstage, making documentation discoverable and always up to date.
</details>

**Q2: What is a catalog-info.yaml file and where does it go?**

<details>
<summary>Answer</summary>

`catalog-info.yaml` is a metadata file placed in the root of each service's Git repository. It tells Backstage about the service: its name, description, owner, type, lifecycle stage, APIs it provides, resources it depends on, and links to dashboards and documentation. Backstage discovers these files (via GitHub discovery or manual registration) and ingests them into the Software Catalog. The file follows the Backstage Catalog Model specification with kinds like Component, API, System, Resource, Domain, Group, and User.
</details>

**Q3: How do Software Templates enable golden paths?**

<details>
<summary>Answer</summary>

Software Templates encode the golden path as a self-service wizard. A platform team creates a template that includes: a skeleton project (pre-configured code structure, Dockerfile, CI/CD pipeline, monitoring, documentation), a set of parameters the developer can customize (service name, team, database needs), and automated steps (create Git repo, set up ArgoCD, register in catalog). When a developer uses the template, they get a production-ready service in minutes instead of days. The template ensures every new service follows organizational standards for security, observability, and deployment practices.
</details>

**Q4: Why is Backstage described as a "framework" rather than a "product"?**

<details>
<summary>Answer</summary>

Backstage provides the foundation (catalog, templates, TechDocs, plugin architecture) but requires significant customization for each organization. You need to: configure authentication for your identity provider, create software templates matching your tech stack, install and configure plugins for your tools (ArgoCD, Grafana, PagerDuty), register your services in the catalog, and potentially build custom plugins for organization-specific features. Out of the box, Backstage is a shell that you fill with your organization's content and integrations. This makes it extremely flexible but means it requires a dedicated team to set up and maintain.
</details>
