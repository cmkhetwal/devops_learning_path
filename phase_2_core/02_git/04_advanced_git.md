# Advanced Git

## Why This Matters in DevOps

Once you move beyond basic branching and merging, Git becomes a precision tool for maintaining software delivery quality. Advanced Git commands let you surgically extract specific fixes from one branch to another with cherry-pick, recover from mistakes with reflog, find the exact commit that introduced a bug with bisect, and enforce code quality with hooks.

In a DevOps context, these skills matter during incidents when you need to apply a hotfix from a feature branch to production without bringing unfinished work. They matter when preparing release branches that require a clean, reviewable history. They matter when automating quality gates with pre-commit hooks that run linters and security scans before code even reaches the remote. Mastering advanced Git turns you from someone who uses Git into someone who trusts Git to protect your production systems.

---

## Core Concepts

### Cherry-Pick

Cherry-pick copies a specific commit from one branch and applies it to another. It creates a new commit with the same changes but a different hash. This is essential for hotfixes: you can pick a bug fix from a development branch and apply it directly to the release branch without merging everything.

### Stash

Stash temporarily shelves uncommitted changes so you can work on something else, then come back. Think of it as a clipboard for your working directory. This is invaluable when you are in the middle of work and an urgent issue requires switching branches.

### Bisect

Bisect performs a binary search through your commit history to find the exact commit that introduced a bug. You tell Git one "good" commit and one "bad" commit, and it narrows down the culprit by checking out commits for you to test. This can find a bug in a history of 1000 commits in about 10 steps.

### Reflog

The reflog records every time HEAD moves -- every commit, checkout, merge, rebase, and reset. It is your safety net. Even if you accidentally delete a branch or reset to the wrong commit, the reflog remembers where you were, and you can recover your work.

### Interactive Rebase

Interactive rebase lets you rewrite history by reordering, editing, squashing, or dropping commits on your branch. This creates a clean, logical history before merging. Instead of committing "WIP," "fix typo," "actually fix the thing," you can squash those into a single, meaningful commit.

### Tags and Semantic Versioning

Tags mark specific commits as important -- typically releases. Unlike branches, tags do not move. They are permanent markers in history.

Semantic versioning (SemVer) follows the format `MAJOR.MINOR.PATCH`:
- **MAJOR:** Breaking changes (v1.0.0 to v2.0.0)
- **MINOR:** New features, backward compatible (v1.0.0 to v1.1.0)
- **PATCH:** Bug fixes, backward compatible (v1.0.0 to v1.0.1)

### Git Hooks

Hooks are scripts that Git executes at specific points in the workflow. They enable automation and quality enforcement:

- **pre-commit:** Runs before a commit is created. Used for linting, formatting, and secret detection.
- **pre-push:** Runs before pushing. Used for running tests.
- **commit-msg:** Validates commit message format.
- **post-merge:** Runs after a merge. Used for installing dependencies.

### Submodules

Submodules embed one Git repository inside another. They are used when a project depends on external code that you want to track at a specific version. Common in infrastructure projects that share modules.

### Worktrees

Worktrees let you check out multiple branches simultaneously in separate directories. Instead of stashing and switching, you can have `main` in one directory and `feature/new-api` in another, both linked to the same repository.

---

## Step-by-Step Practical

### Cherry-Pick: Surgical Hotfix Application

```bash
# Scenario: commit abc123 on develop fixes a critical bug.
# You need this fix on the release branch without merging all of develop.

# Find the commit hash
git log develop --oneline
```

Expected output:

```
abc1234 fix(auth): prevent session hijacking vulnerability
def5678 feat(api): add batch processing endpoint
ghi9012 chore: update test fixtures
```

```bash
# Switch to the release branch
git checkout release/v2.1

# Cherry-pick only the security fix
git cherry-pick abc1234
```

Expected output:

```
[release/v2.1 xyz7890] fix(auth): prevent session hijacking vulnerability
 Date: Thu Apr 16 14:30:00 2026 +0000
 1 file changed, 5 insertions(+), 2 deletions(-)
```

### Stash: Shelving Work in Progress

```bash
# You are mid-feature but need to switch branches for an urgent fix
git stash push -m "WIP: halfway through metrics dashboard"
```

Expected output:

```
Saved working directory and index state On feature/metrics: WIP: halfway through metrics dashboard
```

```bash
# List all stashes
git stash list
```

Expected output:

```
stash@{0}: On feature/metrics: WIP: halfway through metrics dashboard
```

```bash
# Do your urgent work on another branch...
git checkout hotfix/critical-fix
# ... make fix, commit, push ...

# Come back and restore your work
git checkout feature/metrics
git stash pop
```

Expected output:

```
On branch feature/metrics
Changes not staged for commit:
  (modified)   dashboard.py
Dropped refs/stash@{0} (a1b2c3d...)
```

```bash
# Stash specific files only
git stash push -m "stash only config" -- config.yml

# Apply without removing from stash list (keep as backup)
git stash apply stash@{0}
```

### Bisect: Finding When a Bug Was Introduced

```bash
# Start bisect
git bisect start

# Mark the current commit as bad (bug exists)
git bisect bad

# Mark a known good commit (bug did not exist here)
git bisect good v2.0.0
```

Expected output:

```
Bisecting: 15 revisions left to test after this (roughly 4 steps)
[commit-hash] Some commit message
```

```bash
# Git checks out a middle commit. Test it.
# If the bug exists here:
git bisect bad

# If the bug does NOT exist here:
git bisect good

# Repeat until Git finds the exact commit:
```

Expected output (after several steps):

```
abc1234def is the first bad commit
commit abc1234def
Author: developer@example.com
Date:   Mon Apr 6 09:15:00 2026 +0000

    refactor(db): change connection pooling strategy

 src/database.py | 12 +++++-------
 1 file changed, 5 insertions(+), 7 deletions(-)
```

```bash
# Automate bisect with a test script
git bisect start
git bisect bad HEAD
git bisect good v2.0.0
git bisect run python -m pytest tests/test_database.py

# Clean up when done
git bisect reset
```

### Reflog: Recovering Lost Work

```bash
# View the reflog
git reflog
```

Expected output:

```
a1b2c3d HEAD@{0}: commit: Add monitoring config
e4f5g6h HEAD@{1}: checkout: moving from feature/x to main
i7j8k9l HEAD@{2}: commit: WIP feature x
m0n1o2p HEAD@{3}: reset: moving to HEAD~3
```

```bash
# Recover a commit after accidental reset
git reset --hard HEAD~3  # Oops! Lost three commits

# Find them in the reflog
git reflog

# Restore to the commit before the reset
git reset --hard HEAD@{1}
```

### Interactive Rebase: Cleaning Up History

```bash
# Squash the last 3 commits into one
git rebase -i HEAD~3
```

This opens an editor:

```
pick a1b2c3d Add user model
pick e4f5g6h Fix typo in user model
pick i7j8k9l Add validation to user model

# Rebase commands:
# p, pick = use commit
# r, reword = use commit, but edit the message
# s, squash = use commit, but meld into previous commit
# d, drop = remove commit
```

Change it to:

```
pick a1b2c3d Add user model
squash e4f5g6h Fix typo in user model
squash i7j8k9l Add validation to user model
```

Save and close. Git opens another editor for the combined commit message.

### Tagging Releases

```bash
# Create an annotated tag (preferred for releases)
git tag -a v1.2.0 -m "Release v1.2.0: add monitoring and health checks"

# List tags
git tag -l
```

Expected output:

```
v1.0.0
v1.1.0
v1.2.0
```

```bash
# Push tags to remote
git push origin v1.2.0

# Push all tags
git push origin --tags

# Tag a specific past commit
git tag -a v1.1.1 abc1234 -m "Patch: fix authentication bypass"
```

### Git Hooks: Automating Quality Checks

```bash
# Create a pre-commit hook that runs linting
cat > .git/hooks/pre-commit <<'HOOK'
#!/bin/bash
echo "Running pre-commit checks..."

# Check for secrets (simplified example)
if grep -rn "API_KEY\|SECRET\|PASSWORD" --include="*.py" --include="*.yml" .; then
    echo "ERROR: Potential secret detected. Remove before committing."
    exit 1
fi

# Run Python linting
if command -v flake8 &> /dev/null; then
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    if [ $? -ne 0 ]; then
        echo "ERROR: Linting failed. Fix errors before committing."
        exit 1
    fi
fi

echo "Pre-commit checks passed."
HOOK

chmod +x .git/hooks/pre-commit
```

For team-wide hooks, use a framework like `pre-commit`:

```bash
# .pre-commit-config.yaml (committed to the repo)
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: detect-private-key
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/hadolint/hadolint
    rev: v2.12.0
    hooks:
      - id: hadolint
EOF
```

### Submodules

```bash
# Add a shared Terraform module as a submodule
git submodule add https://github.com/org/terraform-modules.git modules/shared

# Clone a repo that has submodules
git clone --recurse-submodules https://github.com/org/infrastructure.git

# Update submodule to latest
cd modules/shared
git pull origin main
cd ../..
git add modules/shared
git commit -m "chore: update shared terraform modules"
```

### Worktrees

```bash
# Create a worktree for a hotfix while keeping current branch intact
git worktree add ../hotfix-workspace hotfix/critical-fix

# List worktrees
git worktree list
```

Expected output:

```
/home/user/project           a1b2c3d [main]
/home/user/hotfix-workspace  e4f5g6h [hotfix/critical-fix]
```

```bash
# Remove worktree when done
git worktree remove ../hotfix-workspace
```

---

## Exercises

### Exercise 1: Cherry-Pick a Hotfix

Create a repository with a `main` and `develop` branch. Make three commits on `develop`, then cherry-pick only the second commit onto `main`. Verify that `main` has the cherry-picked commit but not the other two.

### Exercise 2: Stash Workflow

Start working on a feature (modify two files but do not commit). Stash your work, switch to `main` to fix a bug, commit the fix, then switch back and restore your stashed work. Verify nothing was lost.

### Exercise 3: Bisect to Find a Bug

Create a repository with ten commits. In the fifth commit, introduce a "bug" (e.g., change a function to return the wrong value). Use `git bisect` to find which commit introduced the bug. Try both manual bisect and automated bisect with a test script.

### Exercise 4: Clean Up History with Interactive Rebase

Create a branch with five messy commits including "WIP," "fix typo," and "oops." Use interactive rebase to squash them into two clean, meaningful commits. Verify the history is clean with `git log --oneline`.

### Exercise 5: Set Up Pre-Commit Hooks

Install the `pre-commit` framework and configure it with hooks for: trailing whitespace removal, YAML validation, private key detection, and Python formatting. Make a commit that violates one of these rules and observe the hook preventing the commit.

---

## Knowledge Check

**Q1: When would you use cherry-pick instead of merge in a DevOps workflow?**

<details>
<summary>Answer</summary>

Cherry-pick is used when you need a specific fix from one branch without bringing all the other changes. Common scenarios: (1) applying a security hotfix from `develop` to `release` without unfinished features, (2) backporting a bug fix to an older supported version, (3) pulling a specific configuration change into a branch for testing. Merge brings everything; cherry-pick is surgical.

</details>

**Q2: How does `git reflog` serve as a safety net, and when would you need it?**

<details>
<summary>Answer</summary>

The reflog records every movement of HEAD, including operations that rewrite or delete history (reset, rebase, branch deletion). You need it when: (1) you accidentally run `git reset --hard` and lose commits, (2) a rebase goes wrong and you want to return to the pre-rebase state, (3) you delete a branch and realize you needed it, or (4) you need to undo a merge. The reflog keeps references to "lost" commits for at least 30 days (by default), letting you recover them with `git reset` or `git cherry-pick`.

</details>

**Q3: Why are Git hooks important for DevOps, and what is the limitation of the `.git/hooks/` approach?**

<details>
<summary>Answer</summary>

Git hooks automate quality enforcement at the developer's machine: linting, formatting, secret detection, and test running happen before code is pushed. The limitation of `.git/hooks/` is that hooks are local to each clone and not version-controlled (the `.git` directory is not tracked). This means each developer must manually set up hooks. The solution is the `pre-commit` framework, which stores hook configuration in a version-controlled file (`.pre-commit-config.yaml`) so the entire team shares the same quality gates.

</details>

**Q4: What is the difference between a lightweight tag and an annotated tag? Which should you use for releases?**

<details>
<summary>Answer</summary>

A lightweight tag is just a pointer to a commit (like a branch that does not move). An annotated tag is a full Git object with a tagger name, email, date, message, and optional GPG signature. Always use annotated tags (`git tag -a`) for releases because: (1) they record who created the tag and when, (2) the message can describe the release, (3) they can be GPG-signed for verification, and (4) `git describe` and many CI tools work better with annotated tags.

</details>

**Q5: Explain how `git bisect run` automates bug finding. Why is this particularly valuable in CI/CD contexts?**

<details>
<summary>Answer</summary>

`git bisect run <script>` automates bisect by running a script at each step. If the script exits with 0, Git marks the commit as good; non-zero marks it as bad. You provide a test that detects the bug (e.g., `pytest tests/test_auth.py`), and Git finds the first bad commit automatically.

This is valuable in CI/CD because: (1) when a nightly build breaks, you can bisect across hundreds of commits automatically, (2) the test script can be any executable (unit test, integration test, curl command), and (3) it provides a definitive answer about when a regression was introduced, which is critical for incident postmortems.

</details>
