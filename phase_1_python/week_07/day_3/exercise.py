"""
Week 7, Day 3: REST APIs - Exercise

Build functions that interact with a REST API using full CRUD operations.
Uses jsonplaceholder.typicode.com as the test API.

DevOps Context: You'll use these exact patterns to automate cloud
infrastructure, manage CI/CD pipelines, and integrate DevOps tools.

NOTE: Requires internet access and the requests library.
"""

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

# ===========================================================
# TASK 1: List and Filter Resources
# ===========================================================
# Create a function that lists resources from the API with
# optional filtering.
#
# Parameters:
#   - resource (str): the resource type ("posts", "users", "comments", "todos")
#   - filters (dict, optional): query parameters to filter by
#
# Return a list of dictionaries (the JSON response).
# Use timeout of 10 seconds.
# On any error, return an empty list.
#
# Examples:
#   list_resources("posts")
#       -> [{"userId":1, "id":1, "title":"...", "body":"..."}, ...]  (100 items)
#   list_resources("posts", filters={"userId": 1})
#       -> [... 10 items ...]
#   list_resources("todos", filters={"completed": "true"})
#       -> [... completed todos ...]

def list_resources(resource, filters=None):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: CRUD Operations
# ===========================================================
# Create a function that performs any CRUD operation.
#
# Parameters:
#   - operation (str): "create", "read", "update", or "delete"
#   - resource (str): resource type (e.g., "posts")
#   - resource_id (int, optional): required for read/update/delete one
#   - data (dict, optional): required for create and update
#
# Return a dictionary:
#   {
#       "success": True/False,
#       "status_code": int,
#       "data": response JSON (dict) or None for delete
#   }
#
# Method mapping:
#   "create" -> POST to /{resource} with json=data
#   "read"   -> GET  /{resource}/{resource_id} (or /{resource} if no id)
#   "update" -> PUT  /{resource}/{resource_id} with json=data
#   "delete" -> DELETE /{resource}/{resource_id}
#
# Use timeout of 10 seconds. On error, return success=False.
#
# Examples:
#   crud("read", "posts", resource_id=1)
#   crud("create", "posts", data={"title":"New", "body":"Content", "userId":1})
#   crud("update", "posts", resource_id=1, data={"title":"Updated"})
#   crud("delete", "posts", resource_id=1)

def crud(operation, resource, resource_id=None, data=None):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: Paginated Fetcher
# ===========================================================
# Create a function that fetches resources page by page.
#
# jsonplaceholder supports pagination with _page and _limit params.
#
# Parameters:
#   - resource (str): resource type
#   - per_page (int): items per page, default 10
#   - max_pages (int): maximum pages to fetch, default 3
#
# Fetch pages starting from page 1. Stop when:
#   - You get an empty response, OR
#   - You've fetched max_pages pages
#
# Return a dictionary:
#   {
#       "items": [all items from all pages combined],
#       "total_fetched": total number of items,
#       "pages_fetched": number of pages fetched
#   }
#
# Use timeout of 10 seconds per request. On error, return what
# you have so far.
#
# Example:
#   fetch_paginated("posts", per_page=10, max_pages=3)
#   -> {"items": [...30 items...], "total_fetched": 30, "pages_fetched": 3}

def fetch_paginated(resource, per_page=10, max_pages=3):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: Related Resources Fetcher
# ===========================================================
# Create a function that fetches a resource and its related data.
#
# Given a user_id:
#   1. Fetch the user: GET /users/{user_id}
#   2. Fetch their posts: GET /posts?userId={user_id}
#   3. Fetch their todos: GET /todos?userId={user_id}
#   4. For each post, count comments: GET /comments?postId={post_id}
#      (only for the first 3 posts to avoid too many requests)
#
# Return:
#   {
#       "user": {"name": ..., "email": ..., "company": ...},
#       "stats": {
#           "total_posts": int,
#           "total_todos": int,
#           "completed_todos": int,
#           "comment_counts": [int, int, int]  (comments for first 3 posts)
#       }
#   }
#
# company should be user["company"]["name"].
# Use timeout of 10 seconds per request. On error, return None.
#
# Example:
#   get_user_dashboard(1) -> {"user": {...}, "stats": {...}}

def get_user_dashboard(user_id):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: Simple API Client
# ===========================================================
# Create a class called SimpleAPIClient that wraps the
# jsonplaceholder API.
#
# Constructor:
#   - base_url (str): defaults to "https://jsonplaceholder.typicode.com"
#   - timeout (int): defaults to 10
#
# Methods:
#   - get_posts(user_id=None): return list of posts (optionally filtered)
#   - get_post(post_id): return a single post dict
#   - create_post(title, body, user_id=1): return the created post dict
#   - get_users(): return list of all users
#   - get_user(user_id): return a single user dict
#
# All methods should use self.timeout and handle errors by returning
# None (for single items) or [] (for lists).
#
# Example:
#   client = SimpleAPIClient()
#   posts = client.get_posts(user_id=1)    # list of 10 posts
#   post = client.get_post(1)               # single post dict
#   new = client.create_post("Hi", "World") # created post dict

class SimpleAPIClient:
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    print("Task 1:", len(list_resources("posts")), "posts")
    print("Task 1:", len(list_resources("posts", filters={"userId": 1})), "posts for user 1")
    print()

    print("Task 2:", crud("read", "posts", resource_id=1))
    print("Task 2:", crud("create", "posts", data={"title": "New", "body": "Body", "userId": 1}))
    print()

    print("Task 3:", fetch_paginated("posts", per_page=10, max_pages=2))
    print()

    print("Task 4:", get_user_dashboard(1))
    print()

    client = SimpleAPIClient()
    print("Task 5:", len(client.get_posts()), "posts")
    print("Task 5:", client.get_post(1))
