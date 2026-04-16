#!/usr/bin/env python3
"""
Week 7, Day 7: Quiz Day - Auto-Checker
Validates quiz answers.
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_7")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 10

    print("=" * 50)
    print("Week 7, Day 7: Quiz - Checking Answers")
    print("=" * 50)
    print()

    # Q1
    print("Question 1: HTTP Status Codes")
    try:
        a = exercise.question_1()
        if (a and a.get("status_code") == 503 and
            a.get("meaning") == "Service Unavailable" and
            a.get("category") == "server_error" and
            a.get("action") == "retry later"):
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: {a}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q2
    print("Question 2: HTTP Methods")
    try:
        a = exercise.question_2()
        expected = {
            "list_servers": "GET",
            "create_server": "POST",
            "update_server": "PUT",
            "delete_server": "DELETE",
            "get_server_details": "GET",
        }
        if a == expected:
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: {a}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q3
    print("Question 3: requests Library")
    try:
        a = exercise.question_3()
        if a == "B":
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: Expected 'B', got {repr(a)}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q4
    print("Question 4: Response Handling")
    try:
        a = exercise.question_4()
        if a == "B":
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: Expected 'B', got {repr(a)}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q5
    print("Question 5: REST API Design")
    try:
        a = exercise.question_5()
        expected = {
            "list_containers": {"method": "GET", "path": "/api/v1/containers"},
            "create_container": {"method": "POST", "path": "/api/v1/containers"},
            "get_container": {"method": "GET", "path": "/api/v1/containers/abc123"},
            "delete_container": {"method": "DELETE", "path": "/api/v1/containers/abc123"},
            "restart_container": {"method": "POST", "path": "/api/v1/containers/abc123/restart"},
        }
        if a == expected:
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: {a}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q6
    print("Question 6: Socket Programming")
    try:
        a = exercise.question_6()
        if a == "C":
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: Expected 'C', got {repr(a)}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q7
    print("Question 7: Common Ports")
    try:
        a = exercise.question_7()
        expected = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis"}
        if a == expected:
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: {a}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q8
    print("Question 8: Error Handling")
    try:
        a = exercise.question_8()
        # Timeout, ConnectionError, HTTPError are all siblings under RequestException
        # Accept any order for the first three as long as RequestException is last
        if isinstance(a, list) and len(a) == 4 and a[-1] == "RequestException":
            first_three = set(a[:3])
            if first_three == {"Timeout", "ConnectionError", "HTTPError"}:
                print("  PASS")
                score += 1
            else:
                print(f"  FAIL: First three should be Timeout, ConnectionError, HTTPError in any order")
        else:
            print(f"  FAIL: Expected list of 4 with RequestException last, got {a}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q9
    print("Question 9: SSH Concepts")
    try:
        a = exercise.question_9()
        if a == "B":
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: Expected 'B', got {repr(a)}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Q10
    print("Question 10: API Best Practices")
    try:
        a = exercise.question_10()
        expected = sorted(["A", "C", "E", "F"])
        if isinstance(a, list) and sorted(a) == expected:
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL: Expected {expected}, got {sorted(a) if isinstance(a, list) else a}")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} questions correct")
    if score == total:
        print("PERFECT! You've mastered Networking & APIs!")
    elif score >= 8:
        print("Excellent! Strong networking knowledge!")
    elif score >= 6:
        print("Good! Review the topics you missed.")
    elif score >= 4:
        print("Fair. Revisit the lessons from this week.")
    else:
        print("Needs work. Go through the week's lessons again.")
    print("=" * 50)

if __name__ == "__main__":
    main()
