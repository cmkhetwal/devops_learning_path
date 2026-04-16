# Lesson 09: Storage -- Persistent Volumes and Claims

## Why This Matters in DevOps

Containers are ephemeral by design. When a container restarts, its filesystem is
reset. This is fine for stateless web servers, but databases, file stores, and any
application that persists data needs storage that survives container restarts and
Pod rescheduling. Kubernetes storage abstracts the underlying storage provider
(cloud disks, NFS, local drives) behind a clean API.

As a DevOps engineer, you will provision storage for databases, configure
StorageClasses for dynamic provisioning, and troubleshoot volume mount failures.
Getting storage wrong means data loss -- the most unforgiving failure mode.

The CKA exam tests PV/PVC creation, StorageClasses, and deploying stateful
applications with persistent storage.

---

## Core Concepts

### The Container Storage Problem

```
Without Persistent Storage:
  Pod starts --> Container writes data to /data
  Pod dies   --> Data is GONE
  Pod restarts --> Empty /data directory

With Persistent Storage:
  Pod starts --> Container writes data to /data (backed by PV)
  Pod dies   --> Data is SAFE on the PV
  Pod restarts --> Same data available at /data
```

### The PV/PVC Model

Kubernetes separates storage into two concerns:

```
Cluster Admin creates:               Developer creates:
+--- PersistentVolume (PV) ---+      +--- PersistentVolumeClaim (PVC) ---+
| Represents actual storage   |      | "I need 10Gi of ReadWriteOnce     |
| e.g., AWS EBS disk, NFS     |      |  storage"                         |
| share, local SSD             |      |                                   |
|                              | <--- | PVC binds to a matching PV        |
| capacity: 10Gi               |      |                                   |
| accessModes: ReadWriteOnce  |      +-----------------------------------+
| storageClassName: standard  |              |
+-----------------------------+              |
                                             v
                                      +--- Pod ---+
                                      | Mounts    |
                                      | the PVC   |
                                      | at /data  |
                                      +-----------+
```

**Why this separation?**
- Admins manage physical storage (provision disks, set up NFS)
- Developers request storage without knowing the details
- PVCs are portable across environments (the StorageClass provides the right storage)

### Access Modes

| Mode | Short | Description |
|---|---|---|
| ReadWriteOnce | RWO | One node can mount read-write. Most common. |
| ReadOnlyMany | ROX | Many nodes can mount read-only. |
| ReadWriteMany | RWX | Many nodes can mount read-write. Requires NFS or similar. |
| ReadWriteOncePod | RWOP | Only one Pod can mount read-write (K8s 1.22+). |

**Not all storage backends support all modes.** Cloud block storage (AWS EBS,
GCP PD, Azure Disk) typically supports only RWO. NFS and cloud file storage
(EFS, Azure Files) support RWX.

### Reclaim Policies

What happens to the PV when the PVC is deleted:

| Policy | Behavior |
|---|---|
| **Retain** | PV is kept with data intact. Admin must manually clean up. |
| **Delete** | PV and underlying storage are deleted. Data is lost. |
| **Recycle** | Deprecated. Was `rm -rf /volume/*`. |

### StorageClasses and Dynamic Provisioning

```
Without Dynamic Provisioning:
  1. Admin creates PV (manually provisions a disk)
  2. Developer creates PVC
  3. PVC binds to PV

With Dynamic Provisioning:
  1. Admin creates StorageClass (once)
  2. Developer creates PVC referencing the StorageClass
  3. StorageClass automatically creates a PV and provisions the disk
  4. PVC binds to the new PV
```

```
+--- StorageClass (standard) -----+
| provisioner: kubernetes.io/gce-pd|
| parameters:                      |
|   type: pd-standard              |
| reclaimPolicy: Delete            |
+---------------------------------+
         |
         | Developer creates PVC with storageClassName: standard
         |
         v
+--- PVC (data-pvc) ---+     +--- PV (auto-created) ---+
| storageClassName:     | --> | storageClassName:        |
|   standard            |     |   standard               |
| resources:            |     | capacity: 10Gi           |
|   requests:           |     | gcePersistentDisk:       |
|     storage: 10Gi     |     |   pdName: auto-xyz       |
+-----------------------+     +-------------------------+
```

### Volume Types

Common volume types you will encounter:

| Type | Use Case |
|---|---|
| `emptyDir` | Temporary storage, shared between containers in a Pod. Lost when Pod dies. |
| `hostPath` | Maps a directory from the node. Use only for single-node testing. |
| `nfs` | Network File System mount. Supports RWX. |
| `persistentVolumeClaim` | The standard way to use persistent storage. |
| `configMap` / `secret` | Mount ConfigMaps/Secrets as files. |
| CSI drivers | Cloud-specific: aws-ebs-csi, gce-pd-csi, azure-disk-csi. |

---

## Step-by-Step Practical

### 1. emptyDir volume (temporary shared storage)

```yaml
# Save as /tmp/emptydir-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-demo
spec:
  containers:
  - name: writer
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      while true; do
        echo "$(date) - data written by writer" >> /data/output.txt
        sleep 5
      done
    volumeMounts:
    - name: shared-data
      mountPath: /data
  - name: reader
    image: busybox:1.36
    command: ['sh', '-c', 'tail -f /data/output.txt']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  volumes:
  - name: shared-data
    emptyDir: {}
    # emptyDir:
    #   medium: Memory       # Use RAM instead of disk (tmpfs)
    #   sizeLimit: 100Mi     # Limit the size
```

```bash
kubectl apply -f /tmp/emptydir-pod.yaml
kubectl logs emptydir-demo -c reader -f  # Follow the reader output
# Ctrl+C to stop

kubectl delete pod emptydir-demo
```

### 2. hostPath volume (single-node only)

```yaml
# Save as /tmp/hostpath-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostpath-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c', 'echo "Hello from Pod" > /host-data/test.txt && sleep 3600']
    volumeMounts:
    - name: host-volume
      mountPath: /host-data
  volumes:
  - name: host-volume
    hostPath:
      path: /tmp/k8s-hostpath-demo
      type: DirectoryOrCreate    # Create if it does not exist
```

```bash
kubectl apply -f /tmp/hostpath-pod.yaml
kubectl exec hostpath-demo -- cat /host-data/test.txt
# "Hello from Pod"

# On minikube, you can see the file on the node:
minikube ssh -- cat /tmp/k8s-hostpath-demo/test.txt

kubectl delete pod hostpath-demo
```

### 3. Create a PersistentVolume

```yaml
# Save as /tmp/pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /tmp/k8s-pv-data
```

```bash
kubectl apply -f /tmp/pv.yaml

kubectl get pv
# NAME    CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   AGE
# my-pv   5Gi        RWO            Retain           Available           manual         5s
```

### 4. Create a PersistentVolumeClaim

```yaml
# Save as /tmp/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: manual     # Must match the PV's storageClassName
  accessModes:
  - ReadWriteOnce              # Must match the PV's accessMode
  resources:
    requests:
      storage: 3Gi             # Must be <= PV capacity
```

```bash
kubectl apply -f /tmp/pvc.yaml

# PVC should bind to the PV
kubectl get pvc
# NAME     STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# my-pvc   Bound    my-pv    5Gi        RWO            manual         5s

kubectl get pv
# STATUS changes from Available to Bound
```

### 5. Use PVC in a Pod

```yaml
# Save as /tmp/pvc-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-demo
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sh', '-c']
    args:
    - |
      echo "Writing persistent data..."
      echo "Pod $(hostname) wrote this at $(date)" >> /data/persistent.txt
      cat /data/persistent.txt
      sleep 3600
    volumeMounts:
    - name: persistent-storage
      mountPath: /data
  volumes:
  - name: persistent-storage
    persistentVolumeClaim:
      claimName: my-pvc
```

```bash
kubectl apply -f /tmp/pvc-pod.yaml
kubectl logs pvc-demo

# Delete and recreate the pod -- data should persist
kubectl delete pod pvc-demo
kubectl apply -f /tmp/pvc-pod.yaml
kubectl logs pvc-demo
# Should see BOTH write entries (data persisted!)

kubectl delete pod pvc-demo
```

### 6. StorageClass for dynamic provisioning

```yaml
# Save as /tmp/storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-storage
provisioner: k8s.io/minikube-hostpath   # minikube provisioner
reclaimPolicy: Delete
volumeBindingMode: Immediate
# For cloud providers:
# provisioner: kubernetes.io/aws-ebs
# parameters:
#   type: gp3
#   fsType: ext4
```

```bash
kubectl apply -f /tmp/storageclass.yaml
kubectl get storageclass
# NAME                 PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE
# standard (default)   k8s.io/minikube-hostpath   Delete          Immediate
# fast-storage         k8s.io/minikube-hostpath   Delete          Immediate
```

### 7. PVC with dynamic provisioning

```yaml
# Save as /tmp/dynamic-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  storageClassName: fast-storage    # Reference the StorageClass
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  # No PV needed! The StorageClass will create one automatically.
```

```bash
kubectl apply -f /tmp/dynamic-pvc.yaml

# A PV is automatically created and bound
kubectl get pvc dynamic-pvc
kubectl get pv
# You should see a dynamically provisioned PV with a random name
```

### 8. Deploy a database with persistent storage

```yaml
# Save as /tmp/postgres-persistent.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  # Uses default StorageClass when storageClassName is not specified
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          value: "mysecretpassword"     # Use Secrets in production
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-svc
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

```bash
kubectl apply -f /tmp/postgres-persistent.yaml

# Wait for postgres to be ready
kubectl get pods -l app=postgres -w

# Connect and create data
kubectl exec -it $(kubectl get pod -l app=postgres -o name) -- \
  psql -U postgres -c "CREATE TABLE test (id serial, data text);"
kubectl exec -it $(kubectl get pod -l app=postgres -o name) -- \
  psql -U postgres -c "INSERT INTO test (data) VALUES ('persistent data');"
kubectl exec -it $(kubectl get pod -l app=postgres -o name) -- \
  psql -U postgres -c "SELECT * FROM test;"

# Delete and recreate the pod (simulate crash)
kubectl delete pod -l app=postgres
kubectl get pods -l app=postgres -w  # wait for new pod

# Data should survive
kubectl exec -it $(kubectl get pod -l app=postgres -o name) -- \
  psql -U postgres -c "SELECT * FROM test;"
# id |      data
# ----+----------------
#   1 | persistent data
```

### 9. Expanding a PVC

```bash
# Check if StorageClass allows expansion
kubectl get storageclass standard -o yaml | grep allowVolumeExpansion

# If true, you can expand:
kubectl patch pvc postgres-pvc -p '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'

# Note: shrinking is NOT supported
```

### 10. Clean up

```bash
kubectl delete deployment postgres
kubectl delete svc postgres-svc
kubectl delete pvc my-pvc dynamic-pvc postgres-pvc
kubectl delete pv my-pv
kubectl delete storageclass fast-storage
```

---

## Exercises

1. **PV/PVC Binding**: Create a PV with 10Gi capacity and a PVC requesting 5Gi.
   Verify they bind. Then create another PVC requesting 15Gi. Observe it stays
   Pending because no PV can satisfy it. Clean up.

2. **Data Persistence**: Deploy a Pod that writes a file to a PVC. Delete the Pod.
   Deploy a new Pod mounting the same PVC. Verify the file is still there.

3. **Dynamic Provisioning**: Create a StorageClass and a PVC that references it.
   Verify a PV is automatically created. Deploy a Pod that uses the PVC.

4. **Database Deployment**: Deploy PostgreSQL (or MySQL) with persistent storage.
   Insert data, delete the Pod, wait for the replacement, and verify data survived.

5. **Access Modes**: Create two PVCs -- one with ReadWriteOnce and one with the
   default StorageClass. Try to mount the RWO PVC from two Pods on different nodes
   (requires a multi-node cluster). Observe that one Pod stays Pending.

---

## Knowledge Check

**Q1**: What is the difference between a PersistentVolume and a PersistentVolumeClaim?
<details>
<summary>Answer</summary>
A PersistentVolume (PV) is a piece of storage provisioned by an admin (or
dynamically by a StorageClass). It represents actual storage capacity. A
PersistentVolumeClaim (PVC) is a request for storage by a user/developer. The
PVC specifies how much storage and what access mode is needed. Kubernetes binds
a PVC to a suitable PV automatically.
</details>

**Q2**: What is dynamic provisioning and why is it important?
<details>
<summary>Answer</summary>
Dynamic provisioning allows PVs to be created automatically when a PVC is submitted,
using a StorageClass as a template. Without it, an admin must manually create PVs
before developers can claim storage. Dynamic provisioning enables self-service
storage -- developers create PVCs and storage is provisioned automatically. This
is essential for scalable operations.
</details>

**Q3**: What happens to data when a PVC with reclaimPolicy: Delete is deleted?
<details>
<summary>Answer</summary>
Both the PV and the underlying storage (cloud disk, etc.) are deleted. The data is
permanently lost. This is the default for dynamically provisioned volumes. For
important data, use reclaimPolicy: Retain, which preserves the PV and data for
manual recovery.
</details>

**Q4**: What is the difference between ReadWriteOnce (RWO) and ReadWriteMany (RWX)?
<details>
<summary>Answer</summary>
RWO allows the volume to be mounted as read-write by a single node (all Pods on
that node can access it). RWX allows the volume to be mounted as read-write by
multiple nodes simultaneously. RWX requires a storage backend that supports shared
access, like NFS or cloud file storage (EFS, Azure Files). Most cloud block storage
only supports RWO.
</details>

**Q5**: What volume type would you use for temporary data shared between containers
in the same Pod?
<details>
<summary>Answer</summary>
`emptyDir`. It creates an empty directory when the Pod is assigned to a node and
exists as long as the Pod runs on that node. When the Pod is removed, the data is
deleted. It is ideal for sharing files between containers in the same Pod (e.g.,
a main container writes logs and a sidecar reads them). For RAM-based temporary
storage, use `emptyDir` with `medium: Memory`.
</details>
