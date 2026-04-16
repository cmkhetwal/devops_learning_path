"""
Week 11, Day 1: Check - Git Repository Inspector
Verifies all 6 tasks from exercise.py
"""

import subprocess
import sys
import json

def run_test(test_code):
    """Run a test snippet and return (success, output)."""
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 6

    # --------------------------------------------------------
    # Task 1: get_repo_status
    # --------------------------------------------------------
    print("Task 1: get_repo_status()")
    code = '''
import sys
sys.path.insert(0, ".")
from exercise import get_repo_status, REPO_STATUS

result = get_repo_status(REPO_STATUS)
assert isinstance(result, dict), "Must return a dict"
assert result["branch"] == "feature/deploy-script", f"branch wrong: {result['branch']}"
assert result["clean"] == False, f"clean should be False"
assert result["total_untracked"] == 3, f"total_untracked wrong: {result['total_untracked']}"
assert result["total_modified"] == 3, f"total_modified wrong: {result['total_modified']}"
assert result["total_staged"] == 2, f"total_staged wrong: {result['total_staged']}"
assert result["ready_to_commit"] == False, f"ready_to_commit should be False (README.md is modified but not staged)"
assert result["files_to_review"] == ["README.md"], f"files_to_review wrong: {result['files_to_review']}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  Error: {err[:200]}")

    # --------------------------------------------------------
    # Task 2: list_branches
    # --------------------------------------------------------
    print("Task 2: list_branches()")
    code = '''
import sys
sys.path.insert(0, ".")
from exercise import list_branches, BRANCHES

result = list_branches(BRANCHES)
assert isinstance(result, dict), "Must return a dict"
assert result["active"] == "feature/deploy-script", f"active wrong: {result['active']}"
assert result["protected"] == ["develop", "main"], f"protected wrong: {result['protected']}"
assert result["feature"] == ["feature/deploy-script", "feature/monitoring"], f"feature wrong: {result['feature']}"
assert result["bugfix"] == ["bugfix/login-fix"], f"bugfix wrong: {result['bugfix']}"
assert result["release"] == ["release/v2.1.0"], f"release wrong: {result['release']}"
assert result["hotfix"] == ["hotfix/security-patch"], f"hotfix wrong: {result['hotfix']}"
assert result["total"] == 7, f"total wrong: {result['total']}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  Error: {err[:200]}")

    # --------------------------------------------------------
    # Task 3: get_recent_commits
    # --------------------------------------------------------
    print("Task 3: get_recent_commits()")
    code = '''
import sys
sys.path.insert(0, ".")
from exercise import get_recent_commits, COMMITS

result = get_recent_commits(COMMITS, 3)
assert isinstance(result, list), "Must return a list"
assert len(result) == 3, f"Expected 3 commits, got {len(result)}"
assert result[0]["sha"] == "ghi9012", f"First sha wrong: {result[0]['sha']}"
assert result[0]["date"] == "2025-01-15", f"Date format wrong: {result[0]['date']}"
assert result[0]["stats"] == "+145 -12", f"Stats wrong: {result[0]['stats']}"
assert result[0]["author"] == "Alice Chen", f"Author wrong: {result[0]['author']}"

# Check ordering - most recent first
assert result[1]["sha"] == "xyz7890", f"Second should be xyz7890, got {result[1]['sha']}"
assert result[2]["sha"] == "lmn4567", f"Third should be lmn4567, got {result[2]['sha']}"

# Test default n=5
result5 = get_recent_commits(COMMITS)
assert len(result5) == 5, f"Default n=5 should return 5, got {len(result5)}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  Error: {err[:200]}")

    # --------------------------------------------------------
    # Task 4: find_commits_by_author
    # --------------------------------------------------------
    print("Task 4: find_commits_by_author()")
    code = '''
import sys
sys.path.insert(0, ".")
from exercise import find_commits_by_author, COMMITS

# Case-insensitive partial match
result = find_commits_by_author(COMMITS, "alice")
assert len(result) == 3, f"Alice has 3 commits, got {len(result)}"
assert result[0]["short_sha"] == "ghi9012", f"First should be most recent"

result2 = find_commits_by_author(COMMITS, "Bob")
assert len(result2) == 3, f"Bob has 3 commits, got {len(result2)}"

result3 = find_commits_by_author(COMMITS, "carol")
assert len(result3) == 2, f"Carol has 2 commits, got {len(result3)}"

result4 = find_commits_by_author(COMMITS, "KUMAR")
assert len(result4) == 3, f"KUMAR should match Bob Kumar, got {len(result4)}"

result5 = find_commits_by_author(COMMITS, "nobody")
assert len(result5) == 0, f"nobody should return empty list"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  Error: {err[:200]}")

    # --------------------------------------------------------
    # Task 5: get_file_changes
    # --------------------------------------------------------
    print("Task 5: get_file_changes()")
    code = '''
import sys
sys.path.insert(0, ".")
from exercise import get_file_changes, COMMITS

result = get_file_changes(COMMITS)
assert isinstance(result, dict), "Must return a dict"

# deploy.py appears in commit ghi9012 and rst2345
assert "deploy.py" in result, "deploy.py should be in results"
assert result["deploy.py"]["times_changed"] == 2, f"deploy.py changed 2x, got {result['deploy.py']['times_changed']}"
assert "Alice Chen" in result["deploy.py"]["authors"], "Alice should be an author of deploy.py"
assert "Bob Kumar" in result["deploy.py"]["authors"], "Bob should be an author of deploy.py"
assert result["deploy.py"]["authors"] == sorted(result["deploy.py"]["authors"]), "Authors should be sorted"

# app.py appears in lmn4567 and rst2345
assert "app.py" in result
assert result["app.py"]["times_changed"] == 2

# requirements.txt only in one commit
assert result["requirements.txt"]["times_changed"] == 1
assert result["requirements.txt"]["authors"] == ["Bob Kumar"]
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  Error: {err[:200]}")

    # --------------------------------------------------------
    # Task 6: generate_changelog
    # --------------------------------------------------------
    print("Task 6: generate_changelog()")
    code = '''
import sys
sys.path.insert(0, ".")
from exercise import generate_changelog, COMMITS

result = generate_changelog(COMMITS)
assert isinstance(result, str), "Must return a string"

# Check section headers
assert "## Features" in result, "Missing Features section"
assert "## Fixes" in result, "Missing Fixes section"
assert "## Other" in result, "Missing Other section"

# Check Features section comes first
feat_pos = result.index("## Features")
fix_pos = result.index("## Fixes")
other_pos = result.index("## Other")
assert feat_pos < fix_pos < other_pos, "Sections must be in order: Features, Fixes, Other"

# Check entries
assert "add deployment automation script (ghi9012)" in result
assert "resolve Docker build timeout issue (xyz7890)" in result
assert "update README with setup instructions (opq8901)" in result

# Make sure prefixes are removed
assert "feat:" not in result, "Prefix feat: should be removed"
assert "fix:" not in result, "Prefix fix: should be removed"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  Error: {err[:200]}")

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    print(f"\n{'='*40}")
    print(f"  Score: {score}/{total}")
    if score == total:
        print("  PERFECT! You've mastered Git with Python!")
    elif score >= 4:
        print("  Great job! Review the failed tasks.")
    else:
        print("  Keep practicing. Review the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
