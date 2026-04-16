# Lesson 07: Ingress -- Layer 7 Routing

## Why This Matters in DevOps

Services handle L4 (TCP/UDP) traffic, but real-world applications need L7 (HTTP/HTTPS)
routing: directing traffic based on hostnames and URL paths, terminating TLS, and
consolidating multiple services behind a single external endpoint. Without Ingress,
you would need a separate LoadBalancer Service (and a separate cloud load balancer
with a separate IP) for every service you expose -- expensive and hard to manage.

As a DevOps engineer, you will configure Ingress resources to route traffic to
microservices, set up TLS certificates, and troubleshoot routing issues. The CKA
exam tests Ingress creation with host-based and path-based rules.

---

## Core Concepts

### What Is Ingress?

Ingress is a Kubernetes API resource that manages external HTTP/HTTPS access to
Services. It provides:
- **Host-based routing**: `api.example.com` goes to the API Service
- **Path-based routing**: `/api` goes to one Service, `/web` to another
- **TLS termination**: HTTPS at the edge, HTTP internally
- **Name-based virtual hosting**: Multiple domains on one IP

```
Internet
    |
    v
+--- Ingress Controller (nginx/traefik) ---+
| Listens on ports 80/443                  |
|                                          |
| Rules:                                   |
|   api.example.com/* --> api-service:80   |
|   web.example.com/* --> web-service:80   |
|   example.com/blog  --> blog-service:80  |
+------------------------------------------+
    |           |            |
    v           v            v
api-service  web-service  blog-service
(ClusterIP)  (ClusterIP)  (ClusterIP)
    |           |            |
  pods        pods         pods
```

### Ingress vs Ingress Controller

This distinction is critical:

| Component | What It Is |
|---|---|
| **Ingress** | A Kubernetes API resource (YAML). Just configuration. Does nothing by itself. |
| **Ingress Controller** | A Pod running nginx/traefik/HAProxy that reads Ingress resources and configures routing. |

**You must install an Ingress Controller before Ingress resources work.** Kubernetes
does not include one by default (unlike Services, which work out of the box via
kube-proxy).

### Popular Ingress Controllers

| Controller | Backed By | Notes |
|---|---|---|
| **ingress-nginx** | NGINX | Most popular, CNCF maintained |
| **traefik** | Traefik Proxy | Auto-discovery, Let's Encrypt |
| **HAProxy Ingress** | HAProxy | High performance |
| **AWS ALB Ingress** | AWS ALB | AWS-native integration |
| **GCE Ingress** | Google Cloud LB | GKE default |

### IngressClass

When multiple Ingress Controllers are installed, IngressClass tells Kubernetes
which controller should handle which Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx
  annotations:
    ingressclass.kubernetes.io/is-default-class: "true"
spec:
  controller: k8s.io/ingress-nginx
```

---

## Step-by-Step Practical

### 1. Install an Ingress Controller (minikube)

```bash
# Enable the ingress addon in minikube
minikube addons enable ingress

# Verify the controller is running
kubectl get pods -n ingress-nginx
# NAME                                       READY   STATUS
# ingress-nginx-controller-xxxxx             1/1     Running

# Check IngressClass
kubectl get ingressclass
# NAME    CONTROLLER                    PARAMETERS   AGE
# nginx   k8s.io/ingress-nginx          <none>       30s
```

### 2. Deploy sample applications

```yaml
# Save as /tmp/ingress-apps.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-v1
  template:
    metadata:
      labels:
        app: app-v1
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args:
        - "-text=Hello from App V1"
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: app-v1-svc
spec:
  selector:
    app: app-v1
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-v2
  template:
    metadata:
      labels:
        app: app-v2
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args:
        - "-text=Hello from App V2"
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: app-v2-svc
spec:
  selector:
    app: app-v2
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-api
  template:
    metadata:
      labels:
        app: app-api
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args:
        - "-text=Hello from API"
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: app-api-svc
spec:
  selector:
    app: app-api
  ports:
  - port: 80
    targetPort: 5678
```

```bash
kubectl apply -f /tmp/ingress-apps.yaml
kubectl get deploy,svc
```

### 3. Path-based Ingress

```yaml
# Save as /tmp/path-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: app-v1-svc
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: app-v2-svc
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: app-api-svc
            port:
              number: 80
```

```bash
kubectl apply -f /tmp/path-ingress.yaml

# Check the Ingress
kubectl get ingress
# NAME           CLASS   HOSTS        ADDRESS        PORTS   AGE
# path-ingress   nginx   myapp.local  192.168.49.2   80      5s

# Get the minikube IP
MINIKUBE_IP=$(minikube ip)

# Add to /etc/hosts (or use --resolve with curl)
echo "$MINIKUBE_IP myapp.local" | sudo tee -a /etc/hosts

# Test path-based routing
curl http://myapp.local/v1    # "Hello from App V1"
curl http://myapp.local/v2    # "Hello from App V2"
curl http://myapp.local/api   # "Hello from API"

# Alternative without modifying /etc/hosts:
curl -H "Host: myapp.local" http://$MINIKUBE_IP/v1
```

### 4. Host-based Ingress

```yaml
# Save as /tmp/host-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: v1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-v1-svc
            port:
              number: 80
  - host: v2.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-v2-svc
            port:
              number: 80
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-api-svc
            port:
              number: 80
```

```bash
kubectl apply -f /tmp/host-ingress.yaml

MINIKUBE_IP=$(minikube ip)

# Test host-based routing
curl -H "Host: v1.example.com" http://$MINIKUBE_IP    # App V1
curl -H "Host: v2.example.com" http://$MINIKUBE_IP    # App V2
curl -H "Host: api.example.com" http://$MINIKUBE_IP   # API
```

### 5. Ingress with TLS

```bash
# Create a self-signed TLS certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /tmp/tls.key -out /tmp/tls.crt \
  -subj "/CN=secure.example.com"

# Create a Kubernetes Secret with the certificate
kubectl create secret tls tls-secret \
  --key /tmp/tls.key \
  --cert /tmp/tls.crt
```

```yaml
# Save as /tmp/tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - secure.example.com
    secretName: tls-secret
  rules:
  - host: secure.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-v1-svc
            port:
              number: 80
```

```bash
kubectl apply -f /tmp/tls-ingress.yaml

MINIKUBE_IP=$(minikube ip)

# Test HTTPS (using -k to accept self-signed cert)
curl -k -H "Host: secure.example.com" https://$MINIKUBE_IP
# "Hello from App V1"

# HTTP requests are typically redirected to HTTPS
curl -H "Host: secure.example.com" http://$MINIKUBE_IP
# 308 Permanent Redirect
```

### 6. Path types explained

```yaml
# pathType: Exact
# Only matches the exact path
- path: /api
  pathType: Exact
  # Matches:   /api
  # No match:  /api/, /api/users, /api/v1

# pathType: Prefix
# Matches the path prefix
- path: /api
  pathType: Prefix
  # Matches:   /api, /api/, /api/users, /api/v1/data
  # No match:  /apis, /apiVersion

# pathType: ImplementationSpecific
# Behavior depends on the IngressClass/controller
```

### 7. Common Ingress annotations (nginx)

```yaml
metadata:
  annotations:
    # Rewrite the URL path
    nginx.ingress.kubernetes.io/rewrite-target: /

    # Force HTTPS redirect
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

    # Set proxy body size (file uploads)
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"

    # Rate limiting
    nginx.ingress.kubernetes.io/limit-rps: "10"

    # Custom timeouts
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"

    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"

    # Sticky sessions
    nginx.ingress.kubernetes.io/affinity: "cookie"
```

### 8. Default backend

```yaml
# Save as /tmp/default-backend-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: default-backend-ingress
spec:
  ingressClassName: nginx
  defaultBackend:
    service:
      name: app-v1-svc
      port:
        number: 80
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: app-api-svc
            port:
              number: 80
      # Any path not matching /api goes to defaultBackend (app-v1-svc)
```

### 9. Debugging Ingress issues

```bash
# Check Ingress resource
kubectl get ingress
kubectl describe ingress path-ingress

# Check Ingress Controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Verify backend services have endpoints
kubectl get endpoints app-v1-svc app-v2-svc app-api-svc

# Check the controller's nginx config (for nginx-ingress)
kubectl exec -n ingress-nginx \
  $(kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o name | head -1) \
  -- cat /etc/nginx/nginx.conf | grep -A5 "server_name"
```

### 10. Clean up

```bash
kubectl delete ingress path-ingress host-ingress tls-ingress default-backend-ingress
kubectl delete deploy app-v1 app-v2 app-api
kubectl delete svc app-v1-svc app-v2-svc app-api-svc
kubectl delete secret tls-secret
```

---

## Exercises

1. **Path Routing**: Deploy three different applications (use `hashicorp/http-echo`
   with different messages). Create a single Ingress that routes `/app1`, `/app2`,
   and `/app3` to the respective services. Test each path.

2. **Host Routing**: Using the same three applications, create an Ingress that routes
   `app1.local`, `app2.local`, and `app3.local` to different services. Test using
   curl with the `-H "Host: ..."` header.

3. **TLS Setup**: Create a self-signed certificate and a TLS Ingress. Verify that
   HTTPS works and that HTTP redirects to HTTPS.

4. **Default Backend**: Create an Ingress with specific path rules and a default
   backend. Verify that requests to undefined paths go to the default backend.

5. **Troubleshooting**: Deliberately misconfigure an Ingress (wrong service name,
   wrong port). Use `kubectl describe ingress` and controller logs to identify and
   fix the issue.

---

## Knowledge Check

**Q1**: What is the difference between an Ingress resource and an Ingress Controller?
<details>
<summary>Answer</summary>
An Ingress resource is a Kubernetes API object (defined in YAML) that declares
routing rules -- which host/path should go to which Service. An Ingress Controller
is a running Pod (nginx, traefik, etc.) that watches for Ingress resources and
implements the actual routing. Without a Controller, Ingress resources have no effect.
</details>

**Q2**: What is the difference between `pathType: Exact` and `pathType: Prefix`?
<details>
<summary>Answer</summary>
Exact matches only the specified path exactly (`/api` matches `/api` but not `/api/`
or `/api/users`). Prefix matches any path that starts with the specified prefix
(`/api` matches `/api`, `/api/`, `/api/users`, `/api/v1/data`). Prefix is more
common in practice.
</details>

**Q3**: How do you configure TLS termination on an Ingress?
<details>
<summary>Answer</summary>
Create a Kubernetes Secret of type `kubernetes.io/tls` containing the certificate
and key. Reference that Secret in the Ingress spec under `tls[].secretName`, and
list the hosts it covers under `tls[].hosts`. The Ingress Controller terminates
TLS and forwards unencrypted traffic to the backend Services.
</details>

**Q4**: What happens when no Ingress rule matches an incoming request?
<details>
<summary>Answer</summary>
If a `defaultBackend` is configured in the Ingress spec, traffic goes there. If
no default backend is configured, the behavior depends on the Ingress Controller
-- most return a 404 Not Found response. In nginx-ingress, you can customize the
default backend globally.
</details>

**Q5**: Why would you choose Ingress over a LoadBalancer Service?
<details>
<summary>Answer</summary>
A LoadBalancer Service provisions one cloud load balancer per service (each with
its own public IP and cost). Ingress consolidates multiple services behind a single
load balancer, provides L7 routing (host/path-based), TLS termination, and URL
rewriting. For anything beyond a single service exposed externally, Ingress is
more cost-effective and manageable.
</details>
