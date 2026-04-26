# 16 - Backup & Disaster Recovery
## rsync, tar, snapshots, DR Planning

---

## SECTION 1: rsync (Most Important Backup Tool)

```bash
# Basic sync (local)
rsync -avz /source/ /destination/
# -a = archive (preserves permissions, timestamps, symlinks, etc.)
# -v = verbose
# -z = compress during transfer

# Remote sync (push)
rsync -avz /local/path/ user@remote:/remote/path/

# Remote sync (pull)
rsync -avz user@remote:/remote/path/ /local/path/

# With progress and partial resume
rsync -avzP /source/ /destination/
# -P = combines --progress (show transfer progress) and --partial (keep partially transferred files)

# Delete files on destination that don't exist on source (mirror)
rsync -avz --delete /source/ /destination/
# --delete = remove files on destination that no longer exist on source (true mirror)

# Exclude patterns
rsync -avz --exclude='*.log' --exclude='.git' --exclude='node_modules' /source/ /destination/
# --exclude = skip files/dirs matching the pattern
# Exclude from file
rsync -avz --exclude-from='exclude-list.txt' /source/ /destination/
# --exclude-from = read exclude patterns from a file (one per line)

# Dry run (see what would happen)
rsync -avzn /source/ /destination/
# -n = dry run (show what would be transferred without actually doing it)

# With bandwidth limit (KB/s)
rsync -avz --bwlimit=10000 /source/ user@remote:/destination/
# --bwlimit=10000 = limit bandwidth to 10000 KB/s (prevent saturating the link)

# Over SSH with custom port
rsync -avz -e "ssh -p 2222" /source/ user@remote:/destination/
# -e = specify remote shell command (here: ssh on custom port 2222)

# Backup with date-stamped directory
rsync -avz /data/ /backups/$(date +%Y-%m-%d)/

# Incremental backup using hard links (space efficient)
rsync -avz --link-dest=/backups/latest /data/ /backups/$(date +%Y-%m-%d)/
# --link-dest = hardlink unchanged files to reference dir (saves disk space)
ln -sfn /backups/$(date +%Y-%m-%d) /backups/latest
```

### Production Backup Script
```bash
#!/bin/bash
# /usr/local/bin/backup.sh

set -euo pipefail

# Configuration
SOURCE="/var/www /etc /home"
BACKUP_DIR="/backups"
REMOTE_HOST="backup-server"
REMOTE_DIR="/backups/$(hostname)"
RETENTION_DAYS=30
LOG="/var/log/backup.log"
DATE=$(date +%Y-%m-%d_%H%M)

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG"; }

log "Starting backup"

# Local backup
for src in $SOURCE; do
    dir_name=$(basename "$src")
    rsync -az --delete "$src/" "${BACKUP_DIR}/current/${dir_name}/" 2>> "$LOG"
done
log "Local sync complete"

# Create compressed snapshot
tar czf "${BACKUP_DIR}/archive/${DATE}.tar.gz" -C "${BACKUP_DIR}/current" . 2>> "$LOG"
log "Archive created: ${DATE}.tar.gz"

# Push to remote
rsync -az "${BACKUP_DIR}/archive/${DATE}.tar.gz" "${REMOTE_HOST}:${REMOTE_DIR}/" 2>> "$LOG"
log "Remote sync complete"

# Cleanup old backups
find "${BACKUP_DIR}/archive/" -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete
ssh "$REMOTE_HOST" "find ${REMOTE_DIR}/ -name '*.tar.gz' -mtime +${RETENTION_DAYS} -delete"
log "Cleanup complete (removed backups older than ${RETENTION_DAYS} days)"

log "Backup finished successfully"
```

---

## SECTION 2: tar (Archiving)

```bash
# Create archive
tar -czf backup.tar.gz /path/to/backup        # gzip compression
# -c = create archive | -z = compress with gzip | -f = output filename
tar -cjf backup.tar.bz2 /path/to/backup       # -j = compress with bzip2 (better compression, slower)
tar -cJf backup.tar.xz /path/to/backup        # -J = compress with xz (best compression, slowest)

# Extract archive
tar -xzf backup.tar.gz                         # -x = extract archive
tar -xzf backup.tar.gz -C /restore/path        # -C = change to directory before extracting
tar -xjf backup.tar.bz2                        # Extract bzip2
tar -xJf backup.tar.xz                         # Extract xz

# List contents without extracting
tar -tzf backup.tar.gz                         # -t = list contents without extracting
tar -tzf backup.tar.gz | head -20

# Extract single file
tar -xzf backup.tar.gz path/to/specific/file

# Exclude patterns
tar -czf backup.tar.gz --exclude='*.log' --exclude='.git' /data/

# Backup with preserve permissions (as root)
tar -czpf backup.tar.gz /etc/                  # -p = preserve file permissions and ownership

# Split large archives
tar -czf - /large/directory | split -b 4G - backup.tar.gz.part_
# -czf - = create gzip archive to stdout (the "-" means stdout)
# split -b 4G = split into chunks of 4 GB each
# - (after -b 4G) = read from stdin
# Restore: cat backup.tar.gz.part_* | tar -xzf -

# Database backup with tar
mysqldump --all-databases | gzip > /backups/mysql_$(date +%Y%m%d).sql.gz
pg_dump dbname | gzip > /backups/postgres_$(date +%Y%m%d).sql.gz
```

---

## SECTION 3: LVM Snapshots for Backups

```bash
# Create snapshot (requires free space in VG)
lvcreate -s -n data_snap -L 5G /dev/vg_data/lv_data
# -s = create a snapshot (not a regular LV)
# -n = snapshot name | -L 5G = allocate 5 GB for COW (copy-on-write) changes

# Mount snapshot read-only
mount -o ro /dev/vg_data/data_snap /mnt/snapshot
# -o ro = mount with read-only option (prevents accidental writes to snapshot)

# Backup from snapshot (consistent state)
tar -czf /backups/data_$(date +%Y%m%d).tar.gz -C /mnt/snapshot .

# Cleanup
umount /mnt/snapshot
lvremove -f /dev/vg_data/data_snap
```

---

## SECTION 4: Disaster Recovery Planning

### DR Checklist
```
1. BACKUP STRATEGY
   □ What is backed up (config, data, databases, certificates)
   □ How often (RPO - Recovery Point Objective)
   □ Where stored (on-site, off-site, cloud)
   □ Encryption of backups
   □ Regular restore testing

2. RECOVERY PROCEDURE
   □ Documented step-by-step recovery process
   □ Recovery time target (RTO - Recovery Time Objective)
   □ Contact list (team, vendors, management)
   □ Access credentials stored securely offline

3. WHAT TO BACKUP
   □ /etc/ (system configs)
   □ /home/ (user data)
   □ /var/www/ (web data)
   □ Databases (mysqldump, pg_dump)
   □ SSL certificates (/etc/letsencrypt/, /etc/ssl/)
   □ Crontabs (crontab -l > crontab.bak)
   □ Package list (rpm -qa > packages.txt / dpkg -l > packages.txt)
   □ Firewall rules
   □ DNS zone files
   □ Application configs
   □ Docker volumes and compose files

4. RECOVERY VERIFICATION
   □ Monthly restore test
   □ Verify backup integrity (tar -tzf, checksums)
   □ Test on standby server
```

### Quick Server Rebuild Backup
```bash
#!/bin/bash
# Save everything needed to rebuild a server
BACKUP_DIR="/backups/server-rebuild/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# System info
uname -a > "$BACKUP_DIR/system-info.txt"
cat /etc/os-release >> "$BACKUP_DIR/system-info.txt"

# Package list
rpm -qa --qf '%{NAME}\n' | sort > "$BACKUP_DIR/packages-rpm.txt" 2>/dev/null
dpkg -l | awk '/^ii/{print $2}' | sort > "$BACKUP_DIR/packages-deb.txt" 2>/dev/null

# Configs
tar -czf "$BACKUP_DIR/etc.tar.gz" /etc/ 2>/dev/null

# Crontabs
for user in $(cut -d: -f1 /etc/passwd); do
    crontab -u "$user" -l > "$BACKUP_DIR/crontab-${user}" 2>/dev/null
done

# Firewall
iptables-save > "$BACKUP_DIR/iptables.rules" 2>/dev/null
firewall-cmd --list-all > "$BACKUP_DIR/firewalld.txt" 2>/dev/null

# Network config
ip addr > "$BACKUP_DIR/ip-addr.txt"
ip route > "$BACKUP_DIR/ip-route.txt"

# Service list
systemctl list-unit-files --type=service --state=enabled > "$BACKUP_DIR/enabled-services.txt"

# SSL certs
tar -czf "$BACKUP_DIR/ssl-certs.tar.gz" /etc/letsencrypt/ /etc/ssl/ 2>/dev/null

echo "Server rebuild backup saved to: $BACKUP_DIR"
```
