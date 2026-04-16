#!/usr/bin/env python3
"""
Week 7, Day 3: REST APIs - Auto-Checker
Validates exercise.py solutions.
NOTE: Requires internet access.
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_3")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 7, Day 3: REST APIs - Checking Solutions")
    print("=" * 50)
    print("(Requires internet access)\n")

    # TASK 1: list_resources
    print("Task 1: List and Filter Resources")
    try:
        all_posts = exercise.list_resources("posts")
        filtered = exercise.list_resources("posts", filters={"userId": 1})
        if isinstance(all_posts, list) and len(all_posts) == 100 and isinstance(filtered, list) and len(filtered) == 10:
            print("  PASS: Resources listed and filtered correctly")
            score += 1
        else:
            print(f"  FAIL: Expected 100 and 10, got {len(all_posts) if isinstance(all_posts, list) else 'N/A'} and {len(filtered) if isinstance(filtered, list) else 'N/A'}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: crud
    print("\nTask 2: CRUD Operations")
    try:
        t2_pass = True
        # Read
        r = exercise.crud("read", "posts", resource_id=1)
        if not (r and r.get("success") and r.get("status_code") == 200 and r.get("data", {}).get("id") == 1):
            print(f"  FAIL: Read operation - got {r}")
            t2_pass = False
        # Create
        r = exercise.crud("create", "posts", data={"title": "T", "body": "B", "userId": 1})
        if not (r and r.get("success") and r.get("status_code") == 201):
            print(f"  FAIL: Create operation - got {r}")
            t2_pass = False
        # Update
        r = exercise.crud("update", "posts", resource_id=1, data={"title": "U"})
        if not (r and r.get("success") and r.get("status_code") == 200):
            print(f"  FAIL: Update operation - got {r}")
            t2_pass = False
        # Delete
        r = exercise.crud("delete", "posts", resource_id=1)
        if not (r and r.get("success") and r.get("status_code") == 200):
            print(f"  FAIL: Delete operation - got {r}")
            t2_pass = False
        if t2_pass:
            print("  PASS: All CRUD operations work correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: fetch_paginated
    print("\nTask 3: Paginated Fetcher")
    try:
        result = exercise.fetch_paginated("posts", per_page=10, max_pages=3)
        if result is None:
            print("  FAIL: Returned None")
        elif (result.get("total_fetched") == 30 and
              result.get("pages_fetched") == 3 and
              len(result.get("items", [])) == 30):
            print("  PASS: Pagination works correctly")
            score += 1
        else:
            print(f"  FAIL: Expected 30 items/3 pages, got {result.get('total_fetched')}/{result.get('pages_fetched')}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: get_user_dashboard
    print("\nTask 4: Related Resources Fetcher")
    try:
        result = exercise.get_user_dashboard(1)
        if result is None:
            print("  FAIL: Returned None")
        else:
            user = result.get("user", {})
            stats = result.get("stats", {})
            t4_pass = True
            if user.get("name") != "Leanne Graham":
                print(f"  FAIL: Wrong user name: {user.get('name')}")
                t4_pass = False
            if stats.get("total_posts") != 10:
                print(f"  FAIL: Wrong post count: {stats.get('total_posts')}")
                t4_pass = False
            if not isinstance(stats.get("comment_counts"), list) or len(stats.get("comment_counts", [])) != 3:
                print(f"  FAIL: comment_counts should be list of 3")
                t4_pass = False
            if stats.get("total_todos") is None:
                print("  FAIL: Missing total_todos")
                t4_pass = False
            if t4_pass:
                print("  PASS: User dashboard built correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: SimpleAPIClient
    print("\nTask 5: Simple API Client")
    try:
        client = exercise.SimpleAPIClient()
        t5_pass = True

        posts = client.get_posts()
        if not isinstance(posts, list) or len(posts) != 100:
            print(f"  FAIL: get_posts() should return 100 posts")
            t5_pass = False

        filtered = client.get_posts(user_id=1)
        if not isinstance(filtered, list) or len(filtered) != 10:
            print(f"  FAIL: get_posts(user_id=1) should return 10 posts")
            t5_pass = False

        post = client.get_post(1)
        if not isinstance(post, dict) or post.get("id") != 1:
            print(f"  FAIL: get_post(1) should return post with id=1")
            t5_pass = False

        created = client.create_post("Test", "Body")
        if not isinstance(created, dict) or "id" not in created:
            print(f"  FAIL: create_post should return dict with id")
            t5_pass = False

        users = client.get_users()
        if not isinstance(users, list) or len(users) != 10:
            print(f"  FAIL: get_users() should return 10 users")
            t5_pass = False

        user = client.get_user(1)
        if not isinstance(user, dict) or user.get("name") != "Leanne Graham":
            print(f"  FAIL: get_user(1) should return Leanne Graham")
            t5_pass = False

        if t5_pass:
            print("  PASS: API client works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You can build REST API clients!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Re-read the lesson on REST APIs.")
    print("=" * 50)

if __name__ == "__main__":
    main()
