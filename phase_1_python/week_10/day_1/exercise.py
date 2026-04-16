"""
Week 10, Day 1: boto3 Setup - AWS SDK for Python

AWS SDK FUNDAMENTALS
====================

In this exercise you will learn boto3 patterns using mock classes.
No AWS account is needed -- we simulate the SDK's behavior so you learn
the API patterns that transfer directly to real AWS work.

TASKS
-----
1. Create a MockAWSSession class
2. Create a MockAWSClient class
3. Write a safe connection function
4. Build a region explorer
5. Create an AWS environment report
"""


# ============================================================
# TASK 1: MockAWSSession class
# ============================================================
# Create a class called `MockAWSSession` with:
#   __init__(self, region_name="us-east-1", profile_name="default"):
#       - self.region_name = region_name
#       - self.profile_name = profile_name
#       - self.available_services = ["ec2", "s3", "iam", "lambda",
#           "cloudwatch", "dynamodb", "rds", "sns", "sqs", "sts"]
#
#   Methods:
#       client(service_name, region_name=None):
#           - Returns a MockAWSClient(service_name, region_name or self.region_name)
#           - Prints "Created <service_name> client in <region>"
#
#       get_available_services():
#           - Returns self.available_services

# YOUR CODE HERE


# ============================================================
# TASK 2: MockAWSClient class
# ============================================================
# Create a class called `MockAWSClient` with:
#   __init__(self, service_name, region_name="us-east-1"):
#       - self.service_name = service_name
#       - self.region_name = region_name
#
#   Methods:
#       get_caller_identity():
#           Returns: {
#               "UserId": "AIDAEXAMPLEUSERID",
#               "Account": "123456789012",
#               "Arn": "arn:aws:iam::123456789012:user/devops-student"
#           }
#
#       describe_regions():
#           Returns: {
#               "Regions": [
#                   {"RegionName": "us-east-1", "Endpoint": "ec2.us-east-1.amazonaws.com"},
#                   {"RegionName": "us-west-2", "Endpoint": "ec2.us-west-2.amazonaws.com"},
#                   {"RegionName": "eu-west-1", "Endpoint": "ec2.eu-west-1.amazonaws.com"},
#                   {"RegionName": "ap-southeast-1", "Endpoint": "ec2.ap-southeast-1.amazonaws.com"},
#                   {"RegionName": "ap-northeast-1", "Endpoint": "ec2.ap-northeast-1.amazonaws.com"},
#               ]
#           }
#
#       __repr__():
#           Returns "AWSClient(<service_name>, <region_name>)"

# YOUR CODE HERE


# ============================================================
# TASK 3: Safe connection function
# ============================================================
# Write a function called `get_aws_session` that:
#   - Takes keyword arguments: region_name="us-east-1", profile_name="default"
#   - Tries to import boto3 and create a real session: boto3.Session(...)
#   - If import or session creation fails, return a MockAWSSession instead
#   - Prints "Connected to AWS (region: <region>)" for real sessions
#   - Prints "AWS not available - using mock session (region: <region>)" for mock
#   - Returns the session object

# YOUR CODE HERE


# ============================================================
# TASK 4: Region explorer
# ============================================================
# Write a function called `explore_regions` that:
#   - Takes one argument: client (MockAWSClient or real boto3 client)
#   - Calls client.describe_regions() to get region data
#   - Returns a list of dicts, each with:
#       "name": region name (e.g. "us-east-1")
#       "endpoint": endpoint URL
#   - Prints a formatted table:
#       REGION               ENDPOINT
#       us-east-1            ec2.us-east-1.amazonaws.com
#       ...
#   - Prints "Total regions: X"

# YOUR CODE HERE


# ============================================================
# TASK 5: AWS environment report
# ============================================================
# Write a function called `aws_environment_report` that:
#   - Takes one argument: session (MockAWSSession or real session)
#   - Creates an STS client using session.client("sts")
#   - Creates an EC2 client using session.client("ec2")
#   - Calls sts_client.get_caller_identity()
#   - Calls ec2_client.describe_regions()
#   - Returns a multi-line string:
#
#     AWS Environment Report
#     ======================
#     Profile : <profile_name>
#     Region  : <region_name>
#     Account : <account from identity>
#     User ARN: <arn from identity>
#     Available Services: X
#     Available Regions : Y
#
#   - Also prints the report

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  WEEK 10, DAY 1 - boto3 Setup")
    print("=" * 55)

    # Task 1 test
    print("\n--- Task 1: MockAWSSession ---")
    session = MockAWSSession(region_name="us-west-2", profile_name="dev")
    print(f"Region: {session.region_name}")
    print(f"Profile: {session.profile_name}")
    print(f"Services: {len(session.get_available_services())}")

    # Task 2 test
    print("\n--- Task 2: MockAWSClient ---")
    client = MockAWSClient("ec2", "us-east-1")
    print(repr(client))
    identity = client.get_caller_identity()
    print(f"Account: {identity['Account']}")
    regions = client.describe_regions()
    print(f"Regions: {len(regions['Regions'])}")

    # Task 3 test
    print("\n--- Task 3: Safe Connection ---")
    safe_session = get_aws_session(region_name="eu-west-1")
    print(f"Session type: {type(safe_session).__name__}")

    # Task 4 test
    print("\n--- Task 4: Region Explorer ---")
    ec2 = safe_session.client("ec2")
    region_list = explore_regions(ec2)
    print(f"Regions found: {len(region_list)}")

    # Task 5 test
    print("\n--- Task 5: Environment Report ---")
    report = aws_environment_report(safe_session)
