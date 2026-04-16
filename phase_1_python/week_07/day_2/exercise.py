"""
Week 7, Day 2: The requests Library - Exercise

Practice making HTTP requests with the requests library.
Uses httpbin.org and jsonplaceholder.typicode.com as test APIs.

DevOps Context: These are the exact patterns you'll use to
interact with cloud APIs, monitoring endpoints, and webhooks.

NOTE: These exercises require internet access and the requests library.
      Install with: pip install requests
"""

import requests

# ===========================================================
# TASK 1: Simple GET Request
# ===========================================================
# Create a function that makes a GET request to a URL and returns
# a dictionary with:
#   "status_code": the HTTP status code (int)
#   "content_type": the Content-Type header value (str)
#   "body_length": length of response text (int)
#
# If the request fails (any exception), return:
#   {"status_code": None, "content_type": None, "body_length": 0, "error": str(e)}
#
# IMPORTANT: Use a timeout of 10 seconds.
#
# Example:
#   fetch_url("https://httpbin.org/get")
#   -> {"status_code": 200, "content_type": "application/json", "body_length": 432}

def fetch_url(url):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: GET with Parameters
# ===========================================================
# Create a function that fetches posts from jsonplaceholder.
# URL: https://jsonplaceholder.typicode.com/posts
#
# Parameters:
#   - user_id (int, optional): if provided, filter by userId query param
#
# Return a list of post titles (strings).
# If user_id is provided, add params={"userId": user_id} to the request.
# Use timeout of 10 seconds.
# On any error, return an empty list.
#
# Example:
#   get_post_titles()  -> ["sunt aut facere...", "qui est esse", ...]  (100 titles)
#   get_post_titles(user_id=1)  -> ["sunt aut facere...", ...]  (10 titles)

def get_post_titles(user_id=None):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: POST Request
# ===========================================================
# Create a function that creates a new post on jsonplaceholder.
# URL: https://jsonplaceholder.typicode.com/posts
# Method: POST
#
# Parameters:
#   - title (str): post title
#   - body (str): post body
#   - user_id (int): the user ID, default 1
#
# Send JSON payload: {"title": title, "body": body, "userId": user_id}
# Use timeout of 10 seconds.
#
# Return a dictionary:
#   {"success": True, "id": <id from response>, "status_code": 201}
# On failure:
#   {"success": False, "id": None, "status_code": <code or None>}
#
# Example:
#   create_post("Test Title", "Test body text")
#   -> {"success": True, "id": 101, "status_code": 201}

def create_post(title, body, user_id=1):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: Response Time Checker
# ===========================================================
# Create a function that measures response time for a list of URLs.
#
# Parameters:
#   - urls (list of str): URLs to check
#   - timeout (int): request timeout in seconds, default 5
#
# Return a list of dictionaries, one per URL:
#   {
#       "url": the URL,
#       "status_code": int or None,
#       "response_time_ms": float (milliseconds, rounded to 2 places),
#       "ok": True/False
#   }
#
# If a request fails, set status_code to None, response_time_ms to 0.0,
# and ok to False.
#
# Example:
#   check_response_times(["https://httpbin.org/get", "https://httpbin.org/status/500"])
#   -> [
#       {"url": "https://httpbin.org/get", "status_code": 200,
#        "response_time_ms": 123.45, "ok": True},
#       {"url": "https://httpbin.org/status/500", "status_code": 500,
#        "response_time_ms": 98.76, "ok": False},
#   ]

def check_response_times(urls, timeout=5):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: API Data Extractor
# ===========================================================
# Create a function that fetches a user and all their posts
# from jsonplaceholder.
#
# Steps:
#   1. GET https://jsonplaceholder.typicode.com/users/{user_id}
#   2. GET https://jsonplaceholder.typicode.com/posts?userId={user_id}
#   3. Combine into a summary dictionary
#
# Return:
#   {
#       "user_name": <name from user data>,
#       "user_email": <email from user data>,
#       "company": <company.name from user data>,
#       "post_count": <number of posts>,
#       "post_titles": [list of post title strings]
#   }
#
# Use timeout of 10 seconds for each request.
# On any error, return None.
#
# Example:
#   get_user_summary(1)
#   -> {
#       "user_name": "Leanne Graham",
#       "user_email": "Sincere@april.biz",
#       "company": "Romaguera-Crona",
#       "post_count": 10,
#       "post_titles": ["sunt aut facere...", ...]
#   }

def get_user_summary(user_id):
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    print("Task 1:", fetch_url("https://httpbin.org/get"))
    print()
    print("Task 2:", get_post_titles(user_id=1)[:3], "...")
    print()
    print("Task 3:", create_post("My Title", "My Body"))
    print()
    print("Task 4:", check_response_times(["https://httpbin.org/get"]))
    print()
    print("Task 5:", get_user_summary(1))
