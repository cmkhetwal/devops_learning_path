# Week 10, Day 3: S3 Operations with boto3

## What You'll Learn
- Creating and listing S3 buckets
- Uploading and downloading files
- Listing objects in a bucket
- Deleting objects and buckets
- Understanding S3 key naming and structure

## S3 Overview

S3 (Simple Storage Service) is AWS's object storage. It is used for:
- Static website hosting
- Application data storage
- Log storage
- Backup and disaster recovery
- Data lake storage

S3 is organized as: **Buckets** contain **Objects** (files). Each object
has a **Key** (like a file path) and the **Body** (the data).

## Bucket Operations

```python
import boto3

s3 = boto3.client("s3")

# Create a bucket
s3.create_bucket(
    Bucket="my-devops-bucket-12345",
    CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
)

# List all buckets
response = s3.list_buckets()
for bucket in response["Buckets"]:
    print(f"{bucket['Name']}  (created: {bucket['CreationDate']})")

# Delete a bucket (must be empty first!)
s3.delete_bucket(Bucket="my-devops-bucket-12345")
```

## Uploading Files

```python
# Upload a file
s3.upload_file("local_file.txt", "my-bucket", "path/in/s3/file.txt")

# Upload with metadata
s3.upload_file(
    "report.pdf", "my-bucket", "reports/2024/report.pdf",
    ExtraArgs={"ContentType": "application/pdf", "Metadata": {"author": "devops"}}
)

# Upload string data directly
s3.put_object(
    Bucket="my-bucket",
    Key="data/config.json",
    Body='{"setting": "value"}',
    ContentType="application/json"
)
```

## Downloading Files

```python
# Download to a file
s3.download_file("my-bucket", "path/in/s3/file.txt", "local_copy.txt")

# Get object content directly
response = s3.get_object(Bucket="my-bucket", Key="data/config.json")
content = response["Body"].read().decode("utf-8")
print(content)
```

## Listing Objects

```python
# List objects
response = s3.list_objects_v2(Bucket="my-bucket")
for obj in response.get("Contents", []):
    print(f"{obj['Key']:40s}  {obj['Size']:>10d} bytes  {obj['LastModified']}")

# List with prefix (like a directory)
response = s3.list_objects_v2(Bucket="my-bucket", Prefix="logs/2024/")
for obj in response.get("Contents", []):
    print(obj["Key"])

# Paginate for buckets with many objects
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket"):
    for obj in page.get("Contents", []):
        print(obj["Key"])
```

## Deleting Objects

```python
# Delete a single object
s3.delete_object(Bucket="my-bucket", Key="old_file.txt")

# Delete multiple objects
s3.delete_objects(
    Bucket="my-bucket",
    Delete={
        "Objects": [
            {"Key": "file1.txt"},
            {"Key": "file2.txt"},
        ]
    }
)
```

## Simulating S3 for Practice

```python
class MockS3Bucket:
    """Simulates an S3 bucket."""

    def __init__(self, name, region="us-east-1"):
        self.name = name
        self.region = region
        self.objects = {}  # key -> {size, content_type, last_modified}
        self.creation_date = "2024-01-15T10:00:00Z"

    def put_object(self, key, size=0, content_type="application/octet-stream"):
        self.objects[key] = {
            "Key": key,
            "Size": size,
            "ContentType": content_type,
            "LastModified": "2024-03-01T12:00:00Z",
        }

    def list_objects(self, prefix=""):
        return [v for k, v in self.objects.items() if k.startswith(prefix)]

    def delete_object(self, key):
        return self.objects.pop(key, None)
```

## DevOps Connection
- **Artifact storage**: Store build artifacts, Docker images, Terraform state
- **Log aggregation**: Collect and store logs from all services
- **Backup**: Automated backup of databases, configs, and code
- **Static hosting**: Deploy frontends directly to S3
- **Data pipelines**: S3 is the hub for data engineering workflows

## Key Takeaways
1. Buckets are globally unique -- names must be unique across all of AWS
2. Objects are identified by Key (like a file path)
3. `upload_file()` and `download_file()` work with local files
4. `put_object()` and `get_object()` work with data in memory
5. Always use `list_objects_v2` (not the old `list_objects`)
6. Delete all objects before deleting a bucket
