"""
Week 10, Day 7: Quiz Day - AWS with Python (boto3)

WEEK 10 QUIZ
=============

Answer each question by assigning the correct value to the variable.
Read each question carefully!

TASKS
-----
10 quiz questions covering boto3, EC2, S3, IAM, CloudWatch, Lambda
"""


# ============================================================
# QUESTION 1: boto3 Client vs Resource
# ============================================================
# Which boto3 interface returns raw dictionaries from AWS API calls?
# a) resource
# b) client
# c) session
# d) service
q1 = ""  # YOUR ANSWER: assign "a", "b", "c", or "d"

# YOUR CODE HERE


# ============================================================
# QUESTION 2: AWS Credentials Priority
# ============================================================
# What is the RECOMMENDED way to provide AWS credentials on an EC2 instance?
# a) Hardcode in Python source code
# b) Environment variables
# c) IAM roles
# d) Shared credentials file
q2 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 3: EC2 Instance States
# ============================================================
# What happens to an EC2 instance's data when you STOP it (not terminate)?
# a) All data is permanently lost
# b) EBS volumes are preserved, instance store is lost
# c) Everything is preserved exactly
# d) Only tags are preserved
q3 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 4: S3 Bucket Names
# ============================================================
# S3 bucket names must be:
# a) Unique within your AWS account
# b) Unique within your region
# c) Globally unique across all of AWS
# d) Any string you choose
q4 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 5: S3 List Objects
# ============================================================
# Which method should you use to list objects in an S3 bucket?
# a) s3.list_objects()
# b) s3.list_objects_v2()
# c) s3.get_objects()
# d) s3.describe_objects()
q5 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 6: IAM Policy Effect
# ============================================================
# In an IAM policy, if both an Allow and a Deny apply, which wins?
# a) Allow always wins
# b) Deny always wins
# c) The most specific one wins
# d) The most recent one wins
q6 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 7: IAM Best Practice
# ============================================================
# What is the "principle of least privilege"?
# a) Use the cheapest AWS services
# b) Give only the minimum permissions needed
# c) Use the fewest number of AWS accounts
# d) Minimize the number of IAM users
q7 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 8: CloudWatch Alarms
# ============================================================
# A CloudWatch alarm evaluates metrics over what?
# a) A single data point
# b) A period and number of evaluation periods
# c) The entire history of the metric
# d) Only the last 24 hours
q8 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 9: Lambda Invocation
# ============================================================
# What InvocationType do you use to invoke Lambda and wait for the response?
# a) "Synchronous"
# b) "RequestResponse"
# c) "WaitForResponse"
# d) "Blocking"
q9 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 10: boto3 Region
# ============================================================
# Why is specifying a region important in boto3?
# a) It affects pricing only
# b) AWS services are region-specific; resources exist in specific regions
# c) It is optional and has no effect
# d) It only matters for S3
q10 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# MAIN - Display your answers
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  WEEK 10 QUIZ - AWS with Python (boto3)")
    print("=" * 50)

    answers = {
        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5,
        "Q6": q6, "Q7": q7, "Q8": q8, "Q9": q9, "Q10": q10,
    }

    for q, a in answers.items():
        status = "answered" if a else "UNANSWERED"
        print(f"  {q}: {a if a else '---':10s}  ({status})")

    answered = sum(1 for a in answers.values() if a)
    print(f"\n  Answered: {answered}/10")
