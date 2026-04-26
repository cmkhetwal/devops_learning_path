# 12 - Storage & Filesystem Management
## LVM, RAID, NFS, Disk Management, Filesystem Repair

---

## SECTION 1: Disk Management Basics

```bash
# List all disks and partitions
lsblk
lsblk -f                    # -f = show filesystem type, label, UUID, and mount point
fdisk -l                    # -l = list partition tables for all disks
blkid                       # Show block device attributes (UUID, type, label)
parted -l                   # -l = list partition layout on all disks (GPT-aware)

# Check disk health
smartctl -H /dev/sda         # -H = show SMART health status (PASSED/FAILED)
smartctl -a /dev/sda         # -a = show all SMART info (health, attributes, error logs)
# Install: dnf/apt install smartmontools

# Partition a new disk (GPT)
parted /dev/sdb mklabel gpt              # mklabel = create new partition table (gpt or msdos)
parted /dev/sdb mkpart primary ext4 0% 100%   # mkpart = create partition (type, fs-hint, start, end)
# Or use fdisk for MBR:
fdisk /dev/sdb               # Interactive: n=new, p=primary, w=write

# Create filesystem
mkfs.ext4 /dev/sdb1
mkfs.xfs /dev/sdb1
mkfs.ext4 -L "data" /dev/sdb1    # -L = set filesystem volume label

# Mount
mount /dev/sdb1 /mnt/data
mount -t nfs server:/share /mnt/nfs       # -t = specify filesystem type
mount -o loop disk.iso /mnt/iso   # -o = mount options (loop = treat file as block device)

# Persistent mount (/etc/fstab)
# Device              Mountpoint     Type   Options          Dump Pass
UUID=xxxx-xxxx       /mnt/data      ext4   defaults         0    2
/dev/sdb1            /mnt/data      xfs    defaults,noatime 0    2
server:/share        /mnt/nfs       nfs    defaults,_netdev 0    0

# Verify fstab before reboot
mount -a                    # Mount all fstab entries
findmnt --verify            # --verify = check fstab for syntax errors and missing mount points
```

---

## SECTION 2: LVM (Logical Volume Manager)

```bash
# Concept: Physical Volume (PV) → Volume Group (VG) → Logical Volume (LV)

# Step 1: Create Physical Volumes
pvcreate /dev/sdb /dev/sdc  # pvcreate = initialize disk(s) as LVM physical volumes
pvs                          # pvs = brief summary of all physical volumes
pvdisplay                    # pvdisplay = detailed physical volume info

# Step 2: Create Volume Group
vgcreate data_vg /dev/sdb /dev/sdc   # vgcreate = create a volume group from physical volumes
vgs                          # vgs = brief summary of all volume groups
vgdisplay data_vg            # vgdisplay = detailed volume group info

# Step 3: Create Logical Volumes
lvcreate -n web_lv -L 50G data_vg        # -n = LV name, -L = size in absolute units (e.g. 50G)
lvcreate -n db_lv -l 100%FREE data_vg    # -l = size as % or extent count (100%FREE = all remaining)
lvs                          # List LVs
lvdisplay                    # Detailed LV info

# Step 4: Format and mount
mkfs.xfs /dev/data_vg/web_lv
mkfs.ext4 /dev/data_vg/db_lv
mkdir -p /var/www /var/lib/mysql
mount /dev/data_vg/web_lv /var/www
mount /dev/data_vg/db_lv /var/lib/mysql

# Add to fstab
echo "/dev/data_vg/web_lv  /var/www       xfs  defaults  0  2" >> /etc/fstab
echo "/dev/data_vg/db_lv   /var/lib/mysql ext4 defaults  0  2" >> /etc/fstab

# --- Extend LV (add more space) ---
# Extend by 10GB
lvextend -L +10G /dev/data_vg/web_lv     # -L = extend by absolute size (+10G = add 10GB)
# Extend to fill all free space in VG
lvextend -l +100%FREE /dev/data_vg/web_lv  # -l = extend by % or extents (+100%FREE = all remaining)

# Resize filesystem after extending LV
resize2fs /dev/data_vg/web_lv     # resize2fs = grow ext2/3/4 filesystem to fill its partition
xfs_growfs /var/www               # xfs_growfs = grow XFS filesystem (uses mount point, not device)

# Or extend + resize in one command
lvextend -L +10G -r /dev/data_vg/web_lv   # -r = also resize the filesystem after extending

# --- Add new disk to existing VG ---
pvcreate /dev/sdd
vgextend data_vg /dev/sdd
# Now LVs can use the new space

# --- Shrink LV (ext4 only, NOT XFS) ---
umount /var/lib/mysql
e2fsck -f /dev/data_vg/db_lv       # -f = force check even if filesystem seems clean
resize2fs /dev/data_vg/db_lv 30G   # Shrink filesystem
lvreduce -L 30G /dev/data_vg/db_lv # Shrink LV
mount /dev/data_vg/db_lv /var/lib/mysql

# --- LVM Snapshots ---
lvcreate -s -n db_snap -L 5G /dev/data_vg/db_lv  # -s = create snapshot of the LV
mount -o ro /dev/data_vg/db_snap /mnt/snapshot     # -o ro = mount read-only
lvremove /dev/data_vg/db_snap                       # Remove snapshot
```

---

## SECTION 3: RAID (mdadm)

```bash
# Install
# CentOS: dnf install mdadm
# Ubuntu: apt install mdadm

# Create RAID 1 (mirror)
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
# --create = build a new array, --level = RAID level, --raid-devices = number of active disks

# Create RAID 5 (striping with parity)
mdadm --create /dev/md0 --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd

# Create RAID 10 (mirror + stripe)
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sdb /dev/sdc /dev/sdd /dev/sde

# Check RAID status
cat /proc/mdstat
mdadm --detail /dev/md0                  # --detail = show detailed array status

# Save config
mdadm --detail --scan >> /etc/mdadm.conf       # --scan = scan for all arrays and output config
mdadm --detail --scan >> /etc/mdadm/mdadm.conf # Ubuntu

# Format and mount
mkfs.xfs /dev/md0
mount /dev/md0 /mnt/raid

# Add spare disk
mdadm --add /dev/md0 /dev/sdf

# Remove failed disk
mdadm --fail /dev/md0 /dev/sdc          # --fail = mark a device as faulty
mdadm --remove /dev/md0 /dev/sdc        # --remove = remove a faulty device from the array

# Replace failed disk
mdadm --add /dev/md0 /dev/sdg    # --add = add a device to the array (rebuild starts automatically)

# Monitor rebuild progress
watch cat /proc/mdstat
```

---

## SECTION 4: NFS (Network File System)

### NFS Server
```bash
# Install
# CentOS: dnf install nfs-utils
# Ubuntu: apt install nfs-kernel-server

# Create and configure exports
mkdir -p /exports/shared
chown nobody:nobody /exports/shared     # CentOS: nfsnobody

# /etc/exports
/exports/shared    10.0.0.0/8(rw,sync,no_root_squash,no_subtree_check)
/exports/readonly  10.0.0.0/8(ro,sync,root_squash,no_subtree_check)
/exports/web       192.168.1.0/24(rw,sync,no_root_squash)

# Options:
# rw/ro           = Read-write / Read-only
# sync            = Write to disk before replying (safe)
# no_root_squash  = Allow root access from client (use carefully)
# root_squash     = Map remote root to nobody (default, safer)
# no_subtree_check = Faster, less strict checking

# Apply exports
exportfs -a              # -a = export/unexport all directories listed in /etc/exports
exportfs -rv             # -r = re-export all (sync with /etc/exports), -v = verbose
exportfs -v              # -v = display currently exported directories with options

# Start NFS
systemctl enable --now nfs-server     # CentOS
systemctl enable --now nfs-kernel-server  # Ubuntu

# Firewall
firewall-cmd --add-service=nfs --permanent
firewall-cmd --add-service=mountd --permanent
firewall-cmd --add-service=rpc-bind --permanent
firewall-cmd --reload
```

### NFS Client
```bash
# Install
# CentOS: dnf install nfs-utils
# Ubuntu: apt install nfs-common

# Discover server exports
showmount -e nfs-server.example.com      # -e = show the server's exported directories

# Mount
mount -t nfs nfs-server:/exports/shared /mnt/shared

# Persistent mount (/etc/fstab)
nfs-server:/exports/shared  /mnt/shared  nfs  defaults,_netdev,soft,timeo=30  0  0

# NFS mount options (specified via -o or in fstab options column):
# soft    = return error on timeout (instead of hanging forever)
# hard    = retry indefinitely (default, safer for data integrity)
# timeo=N = timeout in 0.1s units (e.g., timeo=30 = 3 seconds)
# retrans = number of retries before error (soft mounts)
# noatime = don't update access time on reads (reduces NFS traffic)
# vers=4  = force NFS protocol version 4
```

### NFS Troubleshooting
```bash
# Check NFS status
systemctl status nfs-server
rpcinfo -p                    # RPC services
nfsstat -s                    # -s = show server-side NFS statistics
nfsstat -c                    # -c = show client-side NFS statistics

# Check mounted NFS
mount | grep nfs
df -hT | grep nfs

# Test NFS performance
dd if=/dev/zero of=/mnt/shared/testfile bs=1M count=1024 conv=fdatasync

# Debug mount issues
mount -t nfs -v nfs-server:/exports/shared /mnt/shared   # -v = verbose (show mount negotiation details)
# Check: firewall, rpcbind service, SELinux booleans
setsebool -P nfs_export_all_rw 1
setsebool -P nfs_export_all_ro 1
```

---

## SECTION 5: Filesystem Repair

```bash
# Check filesystem (UNMOUNT FIRST!)
umount /dev/sdb1

# ext4 repair
fsck.ext4 -y /dev/sdb1          # -y = auto-answer yes to all repair prompts
e2fsck -f /dev/sdb1             # -f = force check even if filesystem appears clean

# XFS repair
xfs_repair /dev/sdb1            # xfs_repair = check and repair XFS filesystem
xfs_repair -L /dev/sdb1         # -L = zero out (clear) the journal log (data loss risk)

# Check for bad blocks
badblocks -sv /dev/sdb1          # -s = show progress, -v = verbose (report errors found)

# For root filesystem (can't unmount):
# Boot into rescue mode or:
touch /forcefsck                 # Force check on next boot
# Or add fsck to kernel boot params: fsck.mode=force

# XFS filesystem info
xfs_info /dev/sdb1
xfs_info /mount/point

# Filesystem usage details
tune2fs -l /dev/sdb1           # -l = list superblock info (label, UUID, mount count, etc.)
dumpe2fs /dev/sdb1             # dumpe2fs = dump all ext2/3/4 filesystem metadata (groups, blocks, etc.)
```
