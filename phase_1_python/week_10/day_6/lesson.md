# Week 10, Day 6: Practice Day - AWS with Python

## What You'll Practice
Today you combine everything from Week 10 into five mini-projects that
simulate real AWS DevOps automation tasks.

## Mini-Project Overview

### Project 1: AWS Resource Inventory
Build a tool that generates a complete inventory of AWS resources
(EC2 instances, S3 buckets, IAM users) in one unified report.

### Project 2: Cost Analyzer
Create a cost analysis tool that estimates monthly costs based on
instance types and S3 storage usage.

### Project 3: S3 Backup Tool
Build an automated backup utility that creates backup manifests,
tracks backup history, and identifies stale backups.

### Project 4: EC2 Fleet Manager
Create a fleet management tool that can start, stop, and report on
groups of EC2 instances by environment and team.

### Project 5: Infrastructure Report
Build a comprehensive infrastructure report generator that combines
EC2, S3, IAM, and CloudWatch data into a single JSON report.

## Tips
- Reuse the mock classes from Days 1-5
- Focus on clean data structures -- real AWS data is deeply nested
- Think about how these tools would work with real AWS credentials
- Print clear, actionable output

## DevOps Connection
These are the exact kinds of tools that DevOps engineers build for
their organizations. The mock data teaches the patterns; replacing
mocks with real boto3 calls is straightforward once you have AWS access.
