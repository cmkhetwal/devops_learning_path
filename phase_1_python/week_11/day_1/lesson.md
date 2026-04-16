# Week 11, Day 1: Git with Python (GitPython)

## What You'll Learn

- How to interact with Git repositories programmatically using Python
- The GitPython library: Repo object, commits, branches, diffs, and status
- Automating Git workflows for DevOps pipelines

## Why This Matters for DevOps

Every DevOps pipeline starts with source control. Being able to programmatically
inspect repositories, check commit history, compare branches, and automate Git
operations is essential for building CI/CD pipelines, deployment scripts, and
compliance tools.

---

## 1. Installing GitPython

```bash
pip install gitpython
```

GitPython wraps the `git` command-line tool and provides a Pythonic interface
to Git repositories.

## 2. The Repo Object

The `Repo` object is your entry point to everything in a Git repository:

```python
from git import Repo

# Open an existing repository
repo = Repo("/path/to/your/repo")

# Check if the repo is valid (not bare, not empty)
print(repo.bare)          # False for a normal repo
print(repo.working_dir)   # The working directory path
print(repo.git_dir)       # The .git directory path
```

## 3. Checking Repository Status

```python
# Check if there are uncommitted changes
if repo.is_dirty():
    print("There are uncommitted changes!")

# Get untracked files
untracked = repo.untracked_files
print(f"Untracked files: {untracked}")

# Get modified files (staged and unstaged)
changed_files = [item.a_path for item in repo.index.diff(None)]
print(f"Modified files: {changed_files}")

# Get staged files (ready to commit)
staged_files = [item.a_path for item in repo.index.diff("HEAD")]
print(f"Staged files: {staged_files}")
```

## 4. Working with Branches

```python
# List all branches
for branch in repo.branches:
    print(f"Branch: {branch.name}")

# Get the active branch
active = repo.active_branch
print(f"Current branch: {active.name}")

# Create a new branch
new_branch = repo.create_head("feature/my-feature")

# Switch to a branch
new_branch.checkout()

# Delete a branch (must not be checked out)
repo.delete_head("feature/my-feature", force=True)
```

## 5. Commit History

```python
# Get the last 10 commits
for commit in list(repo.iter_commits("main", max_count=10)):
    print(f"Commit: {commit.hexsha[:8]}")
    print(f"Author: {commit.author.name} <{commit.author.email}>")
    print(f"Date:   {commit.committed_datetime}")
    print(f"Message: {commit.message.strip()}")
    print("---")

# Get commit count
total = repo.git.rev_list("--count", "main")
print(f"Total commits on main: {total}")
```

## 6. Viewing Diffs

```python
# Diff between working directory and last commit
diffs = repo.head.commit.diff(None)
for diff in diffs:
    print(f"Changed file: {diff.a_path}")
    print(f"Change type: {diff.change_type}")  # A=added, D=deleted, M=modified

# Diff between two commits
commit_a = list(repo.iter_commits("main", max_count=2))[1]
commit_b = list(repo.iter_commits("main", max_count=1))[0]

diffs = commit_a.diff(commit_b)
for diff in diffs:
    print(f"{diff.change_type}: {diff.a_path}")
```

## 7. Creating Commits Programmatically

```python
# Stage files
repo.index.add(["file1.py", "file2.py"])

# Or stage all changes
repo.git.add(A=True)

# Create a commit
repo.index.commit("feat: add new deployment script")
```

## 8. Working with Tags

```python
# List tags
for tag in repo.tags:
    print(f"Tag: {tag.name} -> {tag.commit.hexsha[:8]}")

# Create a tag
repo.create_tag("v1.0.0", message="Release version 1.0.0")
```

## 9. Remote Operations

```python
# List remotes
for remote in repo.remotes:
    print(f"Remote: {remote.name} -> {remote.url}")

# Fetch from origin
origin = repo.remotes.origin
origin.fetch()

# Pull
origin.pull()

# Push
origin.push()
```

## DevOps Connection

In real-world DevOps, GitPython is used to:
- **Automated release notes**: Parse commit messages between tags to generate changelogs
- **Branch protection**: Scripts that verify branch naming conventions
- **Deployment triggers**: Check what files changed to determine what needs redeploying
- **Compliance auditing**: Verify commit signing and author information
- **Monorepo tooling**: Determine which services changed in a monorepo

---

## Key Takeaways

| Concept | Code |
|---------|------|
| Open a repo | `Repo("/path")` |
| Check dirty | `repo.is_dirty()` |
| List branches | `repo.branches` |
| Active branch | `repo.active_branch` |
| Commit history | `repo.iter_commits()` |
| View diffs | `commit.diff(other)` |
| Stage files | `repo.index.add(files)` |
| Create commit | `repo.index.commit(msg)` |
