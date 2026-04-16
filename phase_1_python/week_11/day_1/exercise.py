"""
Week 11, Day 1: Exercise - Git Repository Inspector

In this exercise you will build functions that simulate working with
Git repository data. Since we cannot guarantee GitPython is installed
or that a real repo exists, we will work with SIMULATED git data
using dictionaries and classes.

Your job: Implement all the functions below that analyze git data.

TASKS:
    1. get_repo_status()       - Analyze repository status from data
    2. list_branches()         - List and categorize branches
    3. get_recent_commits()    - Parse and format commit history
    4. find_commits_by_author()- Filter commits by author name
    5. get_file_changes()      - Analyze file changes across commits
    6. generate_changelog()    - Build a changelog from commit messages
"""

# ============================================================
# SAMPLE GIT DATA (simulates what GitPython would return)
# ============================================================

REPO_STATUS = {
    "branch": "feature/deploy-script",
    "is_dirty": True,
    "untracked_files": ["temp_debug.py", "notes.txt", ".env.local"],
    "modified_files": ["deploy.py", "config.yaml", "README.md"],
    "staged_files": ["deploy.py", "config.yaml"],
    "deleted_files": ["old_script.sh"],
}

BRANCHES = [
    {"name": "main", "is_active": False, "last_commit": "abc1234", "protected": True},
    {"name": "develop", "is_active": False, "last_commit": "def5678", "protected": True},
    {"name": "feature/deploy-script", "is_active": True, "last_commit": "ghi9012", "protected": False},
    {"name": "feature/monitoring", "is_active": False, "last_commit": "jkl3456", "protected": False},
    {"name": "bugfix/login-fix", "is_active": False, "last_commit": "mno7890", "protected": False},
    {"name": "release/v2.1.0", "is_active": False, "last_commit": "pqr1234", "protected": False},
    {"name": "hotfix/security-patch", "is_active": False, "last_commit": "stu5678", "protected": False},
]

COMMITS = [
    {
        "sha": "ghi9012abc",
        "short_sha": "ghi9012",
        "author": "Alice Chen",
        "email": "alice@devops.com",
        "date": "2025-01-15T14:30:00",
        "message": "feat: add deployment automation script",
        "files_changed": ["deploy.py", "config.yaml"],
        "insertions": 145,
        "deletions": 12,
    },
    {
        "sha": "xyz7890def",
        "short_sha": "xyz7890",
        "author": "Bob Kumar",
        "email": "bob@devops.com",
        "date": "2025-01-15T10:15:00",
        "message": "fix: resolve Docker build timeout issue",
        "files_changed": ["Dockerfile", "docker-compose.yaml"],
        "insertions": 8,
        "deletions": 3,
    },
    {
        "sha": "lmn4567ghi",
        "short_sha": "lmn4567",
        "author": "Alice Chen",
        "email": "alice@devops.com",
        "date": "2025-01-14T16:45:00",
        "message": "feat: add health check endpoint",
        "files_changed": ["app.py", "tests/test_health.py"],
        "insertions": 67,
        "deletions": 0,
    },
    {
        "sha": "opq8901jkl",
        "short_sha": "opq8901",
        "author": "Carol Davis",
        "email": "carol@devops.com",
        "date": "2025-01-14T09:00:00",
        "message": "docs: update README with setup instructions",
        "files_changed": ["README.md"],
        "insertions": 35,
        "deletions": 10,
    },
    {
        "sha": "rst2345mno",
        "short_sha": "rst2345",
        "author": "Bob Kumar",
        "email": "bob@devops.com",
        "date": "2025-01-13T11:30:00",
        "message": "refactor: clean up logging configuration",
        "files_changed": ["logging_config.py", "app.py", "deploy.py"],
        "insertions": 42,
        "deletions": 58,
    },
    {
        "sha": "uvw6789pqr",
        "short_sha": "uvw6789",
        "author": "Alice Chen",
        "email": "alice@devops.com",
        "date": "2025-01-12T15:00:00",
        "message": "feat: implement config file parser",
        "files_changed": ["config_parser.py", "tests/test_config.py"],
        "insertions": 120,
        "deletions": 5,
    },
    {
        "sha": "yza0123stu",
        "short_sha": "yza0123",
        "author": "Carol Davis",
        "email": "carol@devops.com",
        "date": "2025-01-12T08:20:00",
        "message": "fix: correct environment variable handling",
        "files_changed": ["env_handler.py"],
        "insertions": 15,
        "deletions": 8,
    },
    {
        "sha": "bcd4567uvw",
        "short_sha": "bcd4567",
        "author": "Bob Kumar",
        "email": "bob@devops.com",
        "date": "2025-01-11T17:45:00",
        "message": "chore: update dependencies in requirements.txt",
        "files_changed": ["requirements.txt"],
        "insertions": 5,
        "deletions": 5,
    },
]

# ============================================================
# TASK 1: get_repo_status(status_data)
#
# Given a status dictionary (like REPO_STATUS), return a
# dictionary with:
#   - "branch": the current branch name (string)
#   - "clean": True if NOT dirty, False if dirty (boolean)
#   - "total_untracked": count of untracked files (int)
#   - "total_modified": count of modified files (int)
#   - "total_staged": count of staged files (int)
#   - "ready_to_commit": True if there are staged files and
#                        no modified-but-unstaged files exist
#                        that are NOT in staged (boolean)
#   - "files_to_review": list of modified files that are NOT
#                        staged (list of strings, sorted)
# ============================================================

def get_repo_status(status_data):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: list_branches(branches_data)
#
# Given a list of branch dicts (like BRANCHES), return a
# dictionary with:
#   - "active": name of the active branch (string)
#   - "protected": list of protected branch names (sorted)
#   - "feature": list of feature/* branch names (sorted)
#   - "bugfix": list of bugfix/* branch names (sorted)
#   - "release": list of release/* branch names (sorted)
#   - "hotfix": list of hotfix/* branch names (sorted)
#   - "total": total number of branches (int)
# ============================================================

def list_branches(branches_data):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: get_recent_commits(commits_data, n=5)
#
# Given a list of commit dicts (like COMMITS), return a list
# of the most recent n commits, each formatted as a dict with:
#   - "sha": the short sha (string)
#   - "author": author name (string)
#   - "date": just the date part YYYY-MM-DD (string)
#   - "message": the commit message (string)
#   - "stats": a string like "+145 -12" (insertions/deletions)
#
# The list should be sorted by date, most recent first.
# ============================================================

def get_recent_commits(commits_data, n=5):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: find_commits_by_author(commits_data, author_name)
#
# Return a list of commits (same format as COMMITS) where
# the author matches author_name (case-insensitive partial
# match). Example: "alice" should match "Alice Chen".
#
# Return them sorted by date, most recent first.
# ============================================================

def find_commits_by_author(commits_data, author_name):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: get_file_changes(commits_data)
#
# Analyze all commits and return a dictionary where:
#   - Keys are filenames
#   - Values are dicts with:
#       - "times_changed": how many commits touched this file
#       - "total_insertions": sum of insertions across all
#         commits that include this file (divide evenly among
#         files in each commit -- just use per-commit totals
#         mapped to each file in that commit for simplicity)
#       - "authors": sorted list of unique authors who changed it
#
# NOTE: For insertions/deletions, each file in a commit gets
#       the FULL commit's insertions/deletions (since we don't
#       have per-file stats in this simulation).
# ============================================================

def get_file_changes(commits_data):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 6: generate_changelog(commits_data)
#
# Generate a changelog string grouped by commit type.
# Parse the type from the message prefix (e.g., "feat:", "fix:").
#
# Format:
# ## Features
# - add deployment automation script (ghi9012)
# - add health check endpoint (lmn4567)
# - implement config file parser (uvw6789)
#
# ## Fixes
# - resolve Docker build timeout issue (xyz7890)
# - correct environment variable handling (yza0123)
#
# ## Other
# - update README with setup instructions (opq8901)
# - clean up logging configuration (rst2345)
# - update dependencies in requirements.txt (bcd4567)
#
# Rules:
# - "feat" -> "Features", "fix" -> "Fixes",
#   everything else -> "Other"
# - Remove the prefix (e.g., "feat: ") from the display message
# - Include the short SHA in parentheses
# - Sections in order: Features, Fixes, Other
# - Within each section, maintain the original order from the data
# - Return as a single string with newline separators
# ============================================================

def generate_changelog(commits_data):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing (optional)
# ============================================================
if __name__ == "__main__":
    print("=== Task 1: Repo Status ===")
    status = get_repo_status(REPO_STATUS)
    if status:
        for k, v in status.items():
            print(f"  {k}: {v}")

    print("\n=== Task 2: Branches ===")
    branches = list_branches(BRANCHES)
    if branches:
        for k, v in branches.items():
            print(f"  {k}: {v}")

    print("\n=== Task 3: Recent Commits ===")
    recent = get_recent_commits(COMMITS, 3)
    if recent:
        for c in recent:
            print(f"  {c['sha']} | {c['date']} | {c['author']} | {c['message']}")

    print("\n=== Task 4: Commits by Author ===")
    alice = find_commits_by_author(COMMITS, "alice")
    if alice:
        for c in alice:
            print(f"  {c['short_sha']} - {c['message']}")

    print("\n=== Task 5: File Changes ===")
    changes = get_file_changes(COMMITS)
    if changes:
        for f, info in sorted(changes.items()):
            print(f"  {f}: changed {info['times_changed']}x, authors={info['authors']}")

    print("\n=== Task 6: Changelog ===")
    log = generate_changelog(COMMITS)
    if log:
        print(log)
