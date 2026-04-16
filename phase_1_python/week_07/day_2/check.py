#!/usr/bin/env python3
"""
Week 7, Day 2: The requests Library - Auto-Checker
Validates exercise.py solutions.
NOTE: Requires internet access and the requests library.
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_2")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 7, Day 2: requests Library - Checking Solutions")
    print("=" * 50)
    print("(Requires internet access)\n")

    # TASK 1: fetch_url
    print("Task 1: Simple GET Request")
    try:
        result = exercise.fetch_url("https://httpbin.org/get")
        if result is None:
            print("  FAIL: Returned None")
        elif result.get("status_code") == 200 and result.get("content_type") and result.get("body_length", 0) > 0:
            print("  PASS: GET request works correctly")
            score += 1
        else:
            print(f"  FAIL: Unexpected result: {result}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: get_post_titles
    print("\nTask 2: GET with Parameters")
    try:
        all_titles = exercise.get_post_titles()
        user_titles = exercise.get_post_titles(user_id=1)
        if all_titles is None or user_titles is None:
            print("  FAIL: Returned None")
        elif isinstance(all_titles, list) and len(all_titles) == 100 and isinstance(user_titles, list) and len(user_titles) == 10:
            if all(isinstance(t, str) for t in all_titles[:5]):
                print("  PASS: Post titles fetched correctly")
                score += 1
            else:
                print("  FAIL: Titles should be strings")
        else:
            print(f"  FAIL: Expected 100 all titles and 10 user titles, got {len(all_titles) if isinstance(all_titles, list) else 'N/A'} and {len(user_titles) if isinstance(user_titles, list) else 'N/A'}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: create_post
    print("\nTask 3: POST Request")
    try:
        result = exercise.create_post("Test Title", "Test Body", user_id=1)
        if result is None:
            print("  FAIL: Returned None")
        elif result.get("success") is True and result.get("id") is not None and result.get("status_code") == 201:
            print("  PASS: POST request works correctly")
            score += 1
        else:
            print(f"  FAIL: Unexpected result: {result}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: check_response_times
    print("\nTask 4: Response Time Checker")
    try:
        results = exercise.check_response_times(["https://httpbin.org/get"])
        if results is None:
            print("  FAIL: Returned None")
        elif isinstance(results, list) and len(results) == 1:
            r = results[0]
            if (r.get("url") == "https://httpbin.org/get" and
                r.get("status_code") == 200 and
                isinstance(r.get("response_time_ms"), float) and
                r.get("ok") is True):
                print("  PASS: Response times measured correctly")
                score += 1
            else:
                print(f"  FAIL: Unexpected result format: {r}")
        else:
            print(f"  FAIL: Expected list with 1 item, got {type(results)}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: get_user_summary
    print("\nTask 5: API Data Extractor")
    try:
        result = exercise.get_user_summary(1)
        if result is None:
            print("  FAIL: Returned None")
        elif (result.get("user_name") == "Leanne Graham" and
              result.get("user_email") == "Sincere@april.biz" and
              result.get("company") == "Romaguera-Crona" and
              result.get("post_count") == 10 and
              isinstance(result.get("post_titles"), list) and
              len(result.get("post_titles")) == 10):
            print("  PASS: User summary extracted correctly")
            score += 1
        else:
            print(f"  FAIL: Unexpected result: {result}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You can work with the requests library!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Make sure you have internet access.")
    print("=" * 50)

if __name__ == "__main__":
    main()
