# Lesson 01: Kubernetes Philosophy and Architecture

## Why This Matters in DevOps

Kubernetes is the operating system of the cloud. As a DevOps engineer, you will spend
a significant portion of your career deploying, scaling, and managing applications on
Kubernetes clusters. Understanding *why* Kubernetes exists -- not just *how* to use it
-- separates operators who react to problems from engineers who design resilient systems.

The CKA exam tests your understanding of Kubernetes internals. You cannot troubleshoot
a broken cluster if you do not understand which component does what. This lesson gives
you the mental model that every other lesson builds upon.

---

## Core Concepts

### The Evolution of Infrastructure

```
Era 1: Bare Metal (1990s-2000s)
+----------------------------------+
| App A | App B | App C            |
|         Operating System         |
|           Hardware               |
+----------------------------------+
Problem: One app crashes, everything crashes.
         Scaling means buying a new server.
         Months to provision.

Era 2: Virtual Machines (2000s-2010s)
+----------+ +----------+ +----------+
| App A    | | App B    | | App C    |
| Guest OS | | Guest OS | | Guest OS |
+----------+ +----------+ +----------+
|            Hypervisor              |
|         Host OS / Hardware         |
+------------------------------------+
Better: Isolation between apps.
Problem: Each VM carries a full OS (GB of overhead).
         Minutes to boot. Still hard to scale.

Era 3: Containers (2013+)
+--------+ +--------+ +--------+
| App A  | | App B  | | App C  |
| Libs   | | Libs   | | Libs   |
+--------+ +--------+ +--------+
|       Container Runtime          |
|       Host OS / Hardware         |
+----------------------------------+
Better: Seconds to start. MB not GB.
Problem: How do you manage 500 containers
         across 50 machines?

Era 4: Orchestration (2014+)
+------------------------------------+
|           Kubernetes               |
| Scheduling, Scaling, Healing,      |
| Networking, Storage, Config        |
+------------------------------------+
| Container  | Container | Container |
| Runtime    | Runtime   | Runtime   |
+------------------------------------+
| Node 1     | Node 2    | Node 3    |
+------------------------------------+
```

### What Kubernetes Actually Does

Kubernetes solves the problem of running containers at scale. Specifically:

1. **Scheduling** -- Deciding which machine runs which container
2. **Self-healing** -- Restarting crashed containers automatically
3. **Scaling** -- Adding or removing container copies based on load
4. **Service discovery** -- Letting containers find each other by name
5. **Load balancing** -- Distributing traffic across container copies
6. **Rolling updates** -- Deploying new versions without downtime
7. **Configuration management** -- Injecting config and secrets into containers
8. **Storage orchestration** -- Attaching persistent storage to containers

### Desired State vs Current State

This is the most important concept in Kubernetes:

```
You declare:  "I want 3 replicas of my web app running."
              This is the DESIRED STATE.

Kubernetes:   Continuously compares desired state to current state.
              If only 2 are running, it starts a 3rd.
              If 4 are running, it stops one.
              This is the RECONCILIATION LOOP.

+------------------+       +------------------+
|  Desired State   | <---> |  Current State   |
|  (what you want) |       |  (what exists)   |
+------------------+       +------------------+
         |                          |
         +--- Controller Manager ---+
              (reconciles the gap)
```

You never say "start a container." You say "I want 3 containers" and Kubernetes
figures out how to get there. If a node dies and takes a container with it,
Kubernetes notices the gap and starts a replacement on another node.

### Declarative vs Imperative

```
Imperative (telling Kubernetes what to DO):
  kubectl run nginx --image=nginx
  kubectl scale deployment nginx --replicas=3

Declarative (telling Kubernetes what you WANT):
  kubectl apply -f deployment.yaml
  # The YAML file describes the desired state.
  # Kubernetes figures out what actions to take.
```

**The declarative approach is always preferred in production** because:
- YAML files can be version-controlled in Git
- Changes are auditable (who changed what, when)
- State is reproducible (apply the same YAML to recreate everything)
- It aligns with Infrastructure as Code principles

The imperative approach is useful for quick experiments and on the CKA exam
where speed matters.

### Kubernetes Architecture

```
+---------------------------------------------------------------+
|                       CONTROL PLANE                            |
|                                                                |
|  +-------------+  +----------+  +-----------+  +------------+ |
|  | API Server  |  |   etcd   |  | Scheduler |  | Controller | |
|  | (kube-      |  | (cluster |  | (assigns  |  | Manager    | |
|  |  apiserver) |  |  state   |  |  pods to  |  | (runs      | |
|  |             |  |  store)  |  |  nodes)   |  |  control   | |
|  | Front door  |  |          |  |           |  |  loops)    | |
|  | for ALL     |  | Key-value|  | Watches   |  |            | |
|  | operations  |  | database |  | for un-   |  | Deployment | |
|  |             |  |          |  | scheduled |  | ReplicaSet | |
|  | REST API    |  | Source   |  | pods      |  | Node       | |
|  | AuthN/AuthZ |  | of truth |  |           |  | controllers| |
|  +-------------+  +----------+  +-----------+  +------------+ |
+---------------------------------------------------------------+
         |                    |
         | (kubelet talks     | (all nodes)
         |  to API server)    |
+--------v--------------------v---------------------------------+
|                      WORKER NODE                               |
|                                                                |
|  +----------+  +------------+  +---------------------------+   |
|  | kubelet  |  | kube-proxy |  | Container Runtime        |   |
|  |          |  |            |  | (containerd / CRI-O)     |   |
|  | Agent on |  | Network    |  |                          |   |
|  | each node|  | proxy on   |  | Actually runs containers |   |
|  | Ensures  |  | each node  |  | via CRI (Container      |   |
|  | pods are |  | Manages    |  |     Runtime Interface)   |   |
|  | running  |  | iptables / |  |                          |   |
|  | as spec  |  | IPVS rules |  |                          |   |
|  +----------+  +------------+  +---------------------------+   |
|                                                                |
|  +---Pod-----------+  +---Pod-----------+                      |
|  | +--Container--+ |  | +--Container--+ |                      |
|  | |  nginx      | |  | |  app:v2     | |                      |
|  | +-------------+ |  | +-------------+ |                      |
|  +------------------+  +------------------+                      |
+---------------------------------------------------------------+
```

#### Component Details

**API Server (kube-apiserver)**
- The front door to Kubernetes. Every operation goes through it.
- kubectl, dashboards, CI/CD pipelines -- they all talk to the API server.
- Handles authentication, authorization, admission control, and validation.
- Stores the result in etcd.

**etcd**
- Distributed key-value store that holds ALL cluster state.
- If etcd is lost and there is no backup, the cluster state is gone.
- Only the API server talks to etcd directly.
- Runs on control plane nodes (typically 3 or 5 for HA).

**Scheduler (kube-scheduler)**
- Watches for newly created Pods with no assigned node.
- Evaluates which node is the best fit based on resource requests,
  affinity rules, taints/tolerations, and topology constraints.
- Assigns the Pod to a node by updating the Pod spec via the API server.

**Controller Manager (kube-controller-manager)**
- Runs a collection of controllers, each a reconciliation loop:
  - **Deployment controller**: ensures the right number of ReplicaSets exist.
  - **ReplicaSet controller**: ensures the right number of Pods exist.
  - **Node controller**: monitors node health, evicts Pods from unhealthy nodes.
  - **Job controller**: creates Pods for Job workloads.
  - And many more.

**kubelet**
- An agent running on every worker node.
- Receives Pod specs from the API server.
- Tells the container runtime to start/stop containers.
- Reports Pod and node status back to the API server.

**kube-proxy**
- Runs on every node.
- Maintains network rules (iptables or IPVS) so that Services work.
- Enables Pod-to-Service communication.

**Container Runtime**
- The software that actually runs containers.
- Kubernetes uses the Container Runtime Interface (CRI).
- Common choices: containerd (default in most distros), CRI-O.
- Docker is no longer a supported runtime as of K8s 1.24, but Docker-built
  images still work because they produce standard OCI images.

### When NOT to Use Kubernetes

Kubernetes adds complexity. It is not always the right choice:

| Scenario | Better Alternative |
|---|---|
| Small team, few services | Docker Compose, a single VM |
| Serverless workloads (event-driven) | AWS Lambda, Cloud Run |
| Monolithic application with no plans to split | A VM or PaaS |
| Learning/prototyping | Docker Compose or a single container |
| Tight budget with no ops team | Managed PaaS (Heroku, Railway) |

The rule: **use Kubernetes when the cost of NOT having orchestration exceeds
the cost of operating Kubernetes.** That usually means 5+ services, multiple
teams, need for auto-scaling, or strict availability requirements.

---

## Step-by-Step Practical

Since this is a philosophy lesson, the practical focuses on exploring a cluster.
You will set up a cluster in Lesson 02. For now, if you have access to any
Kubernetes cluster:

### 1. View the architecture in action

```bash
# See all components running in the kube-system namespace
kubectl get pods -n kube-system

# Example output:
# NAME                                       READY   STATUS    RESTARTS   AGE
# coredns-5dd5756b68-abcde                   1/1     Running   0          2d
# etcd-control-plane                         1/1     Running   0          2d
# kube-apiserver-control-plane               1/1     Running   0          2d
# kube-controller-manager-control-plane      1/1     Running   0          2d
# kube-proxy-xxxxx                           1/1     Running   0          2d
# kube-scheduler-control-plane               1/1     Running   0          2d
```

### 2. Check cluster info

```bash
kubectl cluster-info
# Kubernetes control plane is running at https://127.0.0.1:6443
# CoreDNS is running at https://127.0.0.1:6443/api/v1/...

kubectl version --short
# Client Version: v1.29.0
# Server Version: v1.29.0
```

### 3. See the declarative model in action

```bash
# Imperative: create a pod directly
kubectl run test-nginx --image=nginx

# Now see the desired state Kubernetes stored
kubectl get pod test-nginx -o yaml

# Notice the spec (desired) and status (current) sections
# Clean up
kubectl delete pod test-nginx
```

### 4. Explore the API

```bash
# List all API resources Kubernetes knows about
kubectl api-resources

# See available API versions
kubectl api-versions

# Get detailed info about a resource type
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
```

---

## Exercises

1. **Draw It Out**: On paper or a whiteboard, draw the Kubernetes architecture
   from memory. Include all control plane components and worker node components.
   Label what each component does in one sentence.

2. **Research**: Look up the Kubernetes release history. When was v1.0 released?
   What was the project called internally at Google before it was open-sourced?
   (Answer: Borg, released June 2015)

3. **Identify the Component**: For each scenario, name which Kubernetes component
   is responsible:
   - A new Pod needs to be assigned to a node
   - A Deployment is scaled from 3 to 5 replicas
   - Traffic needs to reach one of 3 identical Pods
   - The actual container process needs to start on a node
   - The cluster state needs to be persisted

4. **Debate**: Write down 3 reasons your current or hypothetical project should
   use Kubernetes, and 3 reasons it should not. Which side wins?

5. **Explore the API**: Run `kubectl api-resources` and count how many resource
   types exist. Pick 3 you have never heard of and use `kubectl explain` to
   learn what they do.

---

## Knowledge Check

**Q1**: What is the difference between desired state and current state?
<details>
<summary>Answer</summary>
Desired state is what you declare you want (e.g., "3 replicas of my app").
Current state is what actually exists in the cluster right now. Kubernetes
controllers continuously reconcile the current state to match the desired state.
If a Pod dies, the controller notices the gap and creates a replacement.
</details>

**Q2**: Which component is the single source of truth for all cluster data?
<details>
<summary>Answer</summary>
etcd. It is a distributed key-value store that holds all cluster state. Only the
API server communicates with etcd directly. If etcd data is lost without a backup,
the cluster's configuration is gone.
</details>

**Q3**: Why is the declarative approach preferred over the imperative approach
in production?
<details>
<summary>Answer</summary>
Because declarative manifests (YAML files) can be version-controlled in Git,
reviewed in pull requests, audited for changes, and reapplied to recreate
environments. The imperative approach leaves no record of what was done and
cannot be reliably reproduced.
</details>

**Q4**: A Pod is running on Node 2. Node 2 loses power. Which component detects
this and which component schedules the replacement Pod?
<details>
<summary>Answer</summary>
The Node controller (part of the Controller Manager) detects that the node is
not responding and marks it as NotReady. If the Pod was managed by a Deployment
or ReplicaSet, that controller creates a new Pod spec. The Scheduler then assigns
the new Pod to a healthy node.
</details>

**Q5**: Name two scenarios where Kubernetes is NOT the right choice.
<details>
<summary>Answer</summary>
(Any two of these are valid)
- Small team with only 1-2 services (Docker Compose is simpler)
- Purely event-driven/serverless workloads (Lambda/Cloud Run is cheaper)
- A monolithic application with no microservices plan
- A project with no dedicated operations staff to manage the cluster
- Early prototyping where speed of iteration matters more than scalability
</details>
