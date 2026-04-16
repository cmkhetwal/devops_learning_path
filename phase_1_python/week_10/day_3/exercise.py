"""
Week 10, Day 3: S3 Operations with boto3

S3 BUCKET AND OBJECT MANAGEMENT
=================================

In this exercise you will build a complete S3 management system using
mock data.  The patterns map directly to real boto3 S3 operations.

TASKS
-----
1. Create a MockS3 class
2. Write bucket management functions
3. Implement object upload/list/delete
4. Build a storage analyzer
5. Create a backup utility
"""

import os
import json

OUTPUT_DIR = "/home/cmk/python/devops-python-path/week_10/day_3/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# TASK 1: MockS3 class
# ============================================================
# Create a class called `MockS3` that simulates S3:
#   __init__(self):
#       - self.buckets = {}  (dict of bucket_name -> dict of objects)
#         Each bucket maps to: {"objects": {}, "region": "us-east-1",
#                                "created": "2024-01-15T10:00:00Z"}
#
#   Methods:
#       create_bucket(name, region="us-east-1"):
#           - Add bucket to self.buckets
#           - Print "Created bucket: <name>"
#           - Return True if created, False if already exists
#
#       list_buckets():
#           - Return list of dicts: [{"Name": name, "Region": region}, ...]
#
#       delete_bucket(name):
#           - Only delete if bucket exists AND has no objects
#           - Print "Deleted bucket: <name>" or "Bucket not empty: <name>"
#             or "Bucket not found: <name>"
#           - Return True if deleted, False otherwise
#
#       put_object(bucket, key, size=0, content_type="binary/octet-stream"):
#           - Add object to the bucket's objects dict
#           - Print "Uploaded <key> to <bucket>"
#           - Return True if success, False if bucket not found
#
#       list_objects(bucket, prefix=""):
#           - Return list of objects (dicts with Key, Size, ContentType)
#             whose keys start with prefix
#           - Return empty list if bucket not found
#
#       delete_object(bucket, key):
#           - Remove object from bucket
#           - Print "Deleted <key> from <bucket>"
#           - Return True if deleted, False if not found
#
#       get_bucket_size(bucket):
#           - Return total size (sum of all object sizes) for the bucket
#           - Return 0 if bucket not found

# YOUR CODE HERE


# ============================================================
# TASK 2: Bucket management functions
# ============================================================
# Write a function called `manage_buckets` that:
#   - Takes one argument: s3 (MockS3 instance)
#   - Creates these buckets:
#       "app-logs-prod"      region="us-east-1"
#       "app-data-prod"      region="us-east-1"
#       "app-backups"        region="us-west-2"
#       "dev-artifacts"      region="eu-west-1"
#   - Lists all buckets and prints each one
#   - Returns the list from list_buckets()
#   - Prints "Total buckets: X"

# YOUR CODE HERE


# ============================================================
# TASK 3: Object operations
# ============================================================
# Write a function called `populate_bucket` that:
#   - Takes two arguments: s3 (MockS3), bucket_name (str)
#   - Uploads these objects to the given bucket:
#       "logs/2024/01/app.log"       size=1024    content_type="text/plain"
#       "logs/2024/02/app.log"       size=2048    content_type="text/plain"
#       "logs/2024/03/app.log"       size=4096    content_type="text/plain"
#       "data/config.json"           size=512     content_type="application/json"
#       "data/users.csv"             size=8192    content_type="text/csv"
#       "images/logo.png"            size=15360   content_type="image/png"
#   - Returns the total number of objects uploaded
#   - Prints "Uploaded X objects to <bucket_name>"

# YOUR CODE HERE


# ============================================================
# TASK 4: Storage analyzer
# ============================================================
# Write a function called `analyze_storage` that:
#   - Takes one argument: s3 (MockS3)
#   - For each bucket, calculates:
#       - Number of objects
#       - Total size in KB (divide bytes by 1024, round to 1 decimal)
#   - Prints a table:
#       Storage Analysis
#       ================
#       BUCKET                    OBJECTS   SIZE(KB)
#       <name>                    <count>   <size>
#       ...
#       ----------------
#       Total: X objects across Y buckets, Z KB
#   - BUCKET column: 25 chars, OBJECTS: 8 chars right-aligned, SIZE: 10 right-aligned
#   - Returns dict: {"total_objects": X, "total_buckets": Y, "total_kb": Z}

# YOUR CODE HERE


# ============================================================
# TASK 5: Backup utility
# ============================================================
# Write a function called `create_backup_manifest` that:
#   - Takes two arguments: s3 (MockS3), source_bucket (str)
#   - Lists all objects in the source bucket
#   - Creates a manifest (dict) with:
#       "source_bucket": source bucket name
#       "backup_bucket": source bucket name + "-backup"
#       "timestamp": "2024-03-15T10:00:00Z" (hardcoded for testing)
#       "objects": list of dicts, each with "key", "size", "content_type"
#       "total_size": sum of all sizes
#       "object_count": number of objects
#   - Writes manifest as JSON to OUTPUT_DIR/backup_manifest.json
#   - Prints "Backup manifest: X objects, Y bytes"
#   - Returns the manifest dict

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  WEEK 10, DAY 3 - S3 Operations")
    print("=" * 60)

    # Task 1 test
    print("\n--- Task 1: MockS3 ---")
    s3 = MockS3()
    s3.create_bucket("test-bucket")
    s3.put_object("test-bucket", "hello.txt", size=100, content_type="text/plain")
    objs = s3.list_objects("test-bucket")
    print(f"Objects in test-bucket: {len(objs)}")
    print(f"Bucket size: {s3.get_bucket_size('test-bucket')} bytes")
    s3.delete_object("test-bucket", "hello.txt")
    s3.delete_bucket("test-bucket")

    # Task 2 test
    print("\n--- Task 2: Bucket Management ---")
    s3 = MockS3()
    buckets = manage_buckets(s3)
    print(f"Bucket names: {[b['Name'] for b in buckets]}")

    # Task 3 test
    print("\n--- Task 3: Object Operations ---")
    count = populate_bucket(s3, "app-logs-prod")
    all_objs = s3.list_objects("app-logs-prod")
    log_objs = s3.list_objects("app-logs-prod", prefix="logs/")
    print(f"All objects: {len(all_objs)}")
    print(f"Log objects: {len(log_objs)}")

    # Task 4 test
    print("\n--- Task 4: Storage Analysis ---")
    populate_bucket(s3, "app-data-prod")
    analysis = analyze_storage(s3)
    print(f"Analysis: {analysis}")

    # Task 5 test
    print("\n--- Task 5: Backup Manifest ---")
    manifest = create_backup_manifest(s3, "app-logs-prod")
    print(f"Manifest objects: {manifest['object_count']}")
    print(f"Manifest file exists: {os.path.exists(os.path.join(OUTPUT_DIR, 'backup_manifest.json'))}")
