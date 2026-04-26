# 15 - Containers & Virtualization
## Docker, Podman, KVM Essentials for Server Admins

---

## SECTION 1: Docker

### 1.1 Installation
```bash
# --- CentOS/RHEL/Amazon Linux ---
dnf install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# --- Ubuntu ---
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Start and enable
systemctl enable --now docker

# Allow non-root user
usermod -aG docker $USER
```

### 1.2 Essential Docker Commands
```bash
# Images
docker pull nginx:latest           # :latest = image tag (version); defaults to "latest" if omitted
docker images                      # List all locally stored images
docker rmi nginx:latest            # rmi = remove image
docker image prune -a              # prune = remove unused images; -a = all (not just dangling)

# Containers
docker run -d --name web -p 80:80 nginx
# -d = detached mode (run in background)
# --name web = assign container name "web"
# -p 80:80 = map host port 80 to container port 80
docker run -d --name web -p 80:80 -v /data:/usr/share/nginx/html:ro nginx
# -v host:container = bind mount host directory into container
# :ro = mount as read-only
docker ps                          # List running containers
docker ps -a                       # -a = show all containers (including stopped)
docker stop web
docker start web
docker restart web
docker rm web
docker rm -f web                   # -f = force remove (kills running container first)

# Logs and debugging
docker logs web
docker logs -f web                 # -f = follow (stream new log output in real time)
docker logs --since 1h web         # --since = show logs from last 1 hour
docker exec -it web bash           # exec = run command in running container
# -i = interactive (keep stdin open) | -t = allocate pseudo-TTY
docker inspect web                 # inspect = show detailed JSON metadata for container
docker stats                       # stats = live-streaming resource usage (CPU, memory, I/O)
docker top web                     # top = show running processes inside container

# Resource limits
docker run -d --name web \
    --memory=512m \
    --cpus=1.5 \
    --restart=unless-stopped \
    -p 80:80 nginx
# --memory=512m = limit container to 512 MB of RAM
# --cpus=1.5 = limit container to 1.5 CPU cores
# --restart=unless-stopped = auto-restart unless explicitly stopped

# Cleanup
docker system prune -a             # prune = remove unused data; -a = all (include unused images, not just dangling)
docker volume prune                # Remove unused volumes
docker network prune               # Remove unused networks

# Save/Load images
docker save nginx:latest > nginx.tar   # save = export image to tar archive (for offline transfer)
docker load < nginx.tar                # load = import image from tar archive
```

### 1.3 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./html:/usr/share/nginx/html:ro
      - ./certs:/etc/nginx/certs:ro
    restart: unless-stopped
    depends_on:
      - app

  app:
    build: ./app
    expose:
      - "3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    restart: unless-stopped
    depends_on:
      - db

  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
      MYSQL_DATABASE: myapp
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'

volumes:
  db_data:
```

```bash
docker compose up -d               # up = create and start containers; -d = detached (background)
docker compose down                # down = stop and remove containers, networks defined in compose file
docker compose logs -f             # -f = follow (stream new log output in real time)
docker compose ps
docker compose exec app bash       # exec = run command in a running service container
docker compose pull && docker compose up -d    # Update images
```

### 1.4 Docker Troubleshooting
```bash
# Container won't start
docker logs container_name
docker inspect container_name | grep -i error

# Check resource usage
docker stats --no-stream            # --no-stream = print stats once and exit (no live update)

# Network issues
docker network ls
docker network inspect bridge
docker exec container_name ping other_container

# Disk space
docker system df                    # df = show Docker disk usage (images, containers, volumes)

# Check what's inside a container
docker exec -it container_name sh
docker cp container_name:/path/to/file ./local_file   # cp = copy files between container and host
```

---

## SECTION 2: Podman (Rootless Containers - RHEL/CentOS)

```bash
# Install
dnf install podman -y    # CentOS/RHEL
apt install podman -y    # Ubuntu

# Podman uses same commands as Docker (drop-in replacement, no daemon needed)
podman pull nginx
podman run -d --name web -p 80:80 nginx   # same flags as docker: -d, --name, -p
podman ps
podman logs web
podman exec -it web bash                   # same flags as docker: -i, -t
podman stop web && podman rm web

# Key difference: rootless by default (no daemon)
# Podman can generate systemd service files:
podman generate systemd --new --name web > ~/.config/systemd/user/container-web.service
systemctl --user enable --now container-web
```

---

## SECTION 3: KVM Virtualization

```bash
# Install KVM
# CentOS/RHEL:
dnf install -y qemu-kvm libvirt virt-install virt-manager bridge-utils
# Ubuntu:
apt install -y qemu-kvm libvirt-daemon-system virtinst virt-manager bridge-utils

systemctl enable --now libvirtd

# Verify KVM support
lsmod | grep kvm
virsh list --all             # --all = show all VMs including stopped ones

# Create VM
virt-install \
    --name centos9 \
    --ram 2048 \
    --vcpus 2 \
    --disk path=/var/lib/libvirt/images/centos9.qcow2,size=20 \
    --os-variant centos-stream9 \
    --network bridge=br0 \
    --graphics none \
    --console pty,target_type=serial \
    --location /var/lib/libvirt/images/CentOS-Stream-9.iso \
    --extra-args 'console=ttyS0'
# --name = VM name | --ram = memory in MB | --vcpus = number of virtual CPUs
# --disk path=...,size=20 = disk image path and size in GB
# --os-variant = optimize VM config for this OS type
# --network bridge=br0 = attach VM to bridged network
# --graphics none = no graphical console (headless)
# --console pty,target_type=serial = enable serial console access
# --location = installation media path (ISO or URL)
# --extra-args = extra kernel boot arguments (here: serial console)

# VM management
virsh list --all             # list = show VMs; --all = include inactive
virsh start centos9          # start = boot a stopped VM
virsh shutdown centos9       # shutdown = send ACPI power-off signal (graceful)
virsh destroy centos9        # destroy = force stop (like pulling the power cord)
virsh reboot centos9
virsh suspend centos9        # suspend = pause VM (freeze state in memory)
virsh resume centos9         # resume = unpause a suspended VM

# Snapshots
virsh snapshot-create-as centos9 --name "before-update"
# snapshot-create-as = create a named snapshot; --name = snapshot label
virsh snapshot-list centos9
virsh snapshot-revert centos9 --snapshotname "before-update"

# Console access
virsh console centos9        # console = attach to VM serial console (Ctrl+] to exit)

# VM resource info
virsh dominfo centos9        # dominfo = show basic VM info (memory, CPUs, state)
virsh domstats centos9       # domstats = show detailed VM statistics (CPU, balloon, block, net)
```
