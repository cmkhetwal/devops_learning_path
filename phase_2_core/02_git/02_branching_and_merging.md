# Branching and Merging

## Why This Matters in DevOps

Branching is how teams work on multiple things simultaneously without stepping on each other's toes. In DevOps, your branching strategy directly determines how fast you can deliver software and how stable your releases are. A poorly chosen branching model creates merge conflicts, delays deployments, and breaks CI/CD pipelines. A well-chosen one enables continuous delivery, safe experimentation, and rapid rollbacks.

The branching strategy you choose is not a technical decision alone -- it is an organizational decision. Trunk-based development enables teams practicing continuous deployment. Git Flow suits teams with scheduled releases. The strategy must match your deployment cadence, team size, and risk tolerance. Understanding branches deeply is what separates a DevOps engineer who configures pipelines from one who designs delivery workflows.

Every CI/CD pipeline starts with a branch event: a push, a pull request, a tag. If you do not understand how branches work, you cannot design pipelines that respond correctly to your team's workflow.

---

## Core Concepts

### What Is a Branch?

A branch in Git is simply a lightweight, movable pointer to a commit. When you create a branch, Git creates a new pointer -- it does not copy files. This makes branching in Git almost instantaneous and nearly free in terms of storage.

```
main:      A --- B --- C
                        \
feature:                 D --- E
```

In this diagram, `main` points to commit C, and `feature` points to commit E. Commits D and E only exist on the `feature` branch.

### HEAD: Where You Are

`HEAD` is a special pointer that tells Git which branch you are currently on. When you switch branches, HEAD moves to point to the new branch. When you make a commit, the current branch pointer advances to the new commit.

### Merge vs Rebase

These are two strategies for integrating changes from one branch into another.

**Merge** creates a new "merge commit" that ties two branches together. It preserves the complete history of both branches.

```
main:      A --- B --- C --------- M
                        \         /
feature:                 D --- E
```

**Rebase** replays your commits on top of the target branch, creating a linear history. It rewrites commit hashes.

```
Before rebase:
main:      A --- B --- C
                        \
feature:                 D --- E

After rebase (feature onto main):
main:      A --- B --- C
                        \
feature:                 C --- D' --- E'
```

**When to use each:**
- Use **merge** when you want to preserve the full history of how work happened (default for pull requests).
- Use **rebase** when you want a clean, linear history and your branch has not been shared with others.
- **Never rebase commits that have been pushed to a shared branch.** This rewrites history and causes problems for everyone else.

### Branch Naming Conventions

Consistent naming helps automation and humans alike:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/add-monitoring-dashboard` |
| `bugfix/` | Non-critical bug repairs | `bugfix/fix-login-timeout` |
| `hotfix/` | Critical production fixes | `hotfix/patch-sql-injection` |
| `release/` | Release preparation | `release/v2.3.0` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |

CI/CD pipelines can use these prefixes to trigger different workflows: `feature/*` branches run tests, `release/*` branches deploy to staging, `hotfix/*` branches get fast-tracked to production.

### Git Flow vs Trunk-Based Development

**Git Flow** uses long-lived branches (`develop`, `release/*`, `hotfix/*`) alongside `main`. It works well for teams with scheduled releases but adds complexity.

```
main:       ---- v1.0 -------------- v1.1 ----
                  \                  /
develop:    -------*----*----*------*----------
                    \      /
feature:             *----*
```

**Trunk-Based Development** keeps `main` as the single source of truth. Developers work on short-lived branches (hours to a couple of days) and merge frequently. This is the preferred model for continuous deployment.

```
main:       ---- * ---- * ---- * ---- * ---- * ----
                  \   /   \  /         \   /
branches:          *-*     **           *-*
```

**For DevOps teams practicing CI/CD, trunk-based development is almost always the better choice.** It reduces merge conflicts, enables continuous integration, and keeps the deployment pipeline flowing.

---

## Step-by-Step Practical

### Creating and Switching Branches

```bash
# Create a new branch
git branch feature/add-monitoring

# Switch to it
git checkout feature/add-monitoring

# Or do both in one command
git checkout -b feature/add-monitoring

# Modern alternative (Git 2.23+)
git switch -c feature/add-monitoring
```

Expected output:

```
Switched to a new branch 'feature/add-monitoring'
```

### Listing Branches

```bash
# List local branches (* indicates current branch)
git branch
```

Expected output:

```
  main
* feature/add-monitoring
```

```bash
# List all branches including remote
git branch -a

# List branches with last commit info
git branch -v
```

### Making Changes on a Branch

```bash
# Create a monitoring configuration file
cat > monitoring.yml <<'EOF'
prometheus:
  scrape_interval: 15s
  targets:
    - "app:8080"
    - "api:9090"
alerting:
  slack_webhook: "${SLACK_WEBHOOK_URL}"
EOF

git add monitoring.yml
git commit -m "Add Prometheus monitoring configuration"
```

### Merging a Branch

```bash
# Switch back to main
git checkout main

# Merge the feature branch
git merge feature/add-monitoring
```

Expected output:

```
Updating a1b2c3d..e4f5g6h
Fast-forward
 monitoring.yml | 8 ++++++++
 1 file changed, 8 insertions(+)
 create mode 100644 monitoring.yml
```

A **fast-forward merge** happens when there are no new commits on `main` since the branch was created. Git simply moves the pointer forward. If both branches have new commits, Git creates a **merge commit**.

### Creating a Merge Commit (No Fast-Forward)

```bash
# Force a merge commit even when fast-forward is possible
git merge --no-ff feature/add-monitoring -m "Merge feature/add-monitoring into main"
```

This creates an explicit merge commit, which is useful for seeing when features were integrated. Many teams require `--no-ff` for all merges.

### Resolving Merge Conflicts

```bash
# Simulate a conflict: both branches modify the same line
git checkout -b feature/update-port
echo 'port: 8080' > config.yml
git add config.yml && git commit -m "Set port to 8080"

git checkout main
echo 'port: 9090' > config.yml
git add config.yml && git commit -m "Set port to 9090"

# Now merge -- this will conflict
git merge feature/update-port
```

Expected output:

```
Auto-merging config.yml
CONFLICT (content): Merge conflict in config.yml
Automatic merge failed; fix conflicts and then commit the result.
```

```bash
# View the conflict markers
cat config.yml
```

Expected output:

```
<<<<<<< HEAD
port: 9090
=======
port: 8080
>>>>>>> feature/update-port
```

```bash
# Resolve by editing the file (choose the correct value)
echo 'port: 8080' > config.yml

# Mark as resolved and complete the merge
git add config.yml
git commit -m "Merge feature/update-port, resolve port conflict to 8080"
```

### Rebasing a Branch

```bash
# On your feature branch, rebase onto latest main
git checkout feature/add-logging
git rebase main
```

Expected output:

```
Successfully rebased and updated refs/heads/feature/add-logging.
```

If conflicts occur during rebase:

```bash
# Fix the conflict in the file, then:
git add <conflicted-file>
git rebase --continue

# Or abort the rebase entirely:
git rebase --abort
```

### Deleting Branches

```bash
# Delete a merged branch
git branch -d feature/add-monitoring
```

Expected output:

```
Deleted branch feature/add-monitoring (was e4f5g6h).
```

```bash
# Force delete an unmerged branch (careful!)
git branch -D feature/abandoned-experiment
```

---

## Exercises

### Exercise 1: Feature Branch Workflow

Create a repository with an initial commit on `main`. Create a `feature/user-auth` branch, add two commits to it, then merge it back into `main` using `--no-ff`. Verify the merge commit appears in `git log --graph --oneline`.

### Exercise 2: Conflict Resolution

Create a scenario where two branches modify the same file on the same lines. Practice resolving the conflict manually. After resolving, use `git log --graph --oneline` to visualize the merge.

### Exercise 3: Rebase Practice

Create a feature branch with three commits. Add two new commits to `main`. Rebase your feature branch onto `main`, then verify with `git log --oneline` that the history is linear.

### Exercise 4: Branch Naming Strategy

Design a branch naming convention for a team of five developers working on a web application with monthly releases. Document which prefixes you would use, and write example branch names for: a new search feature, a login bug fix, a critical security patch, and a dependency update.

### Exercise 5: Compare Git Flow and Trunk-Based

Set up a small repository and simulate three sprints using Git Flow (with `develop` and `release` branches). Then repeat the same work using trunk-based development with short-lived branches. Write down which approach felt simpler and why.

---

## Knowledge Check

**Q1: What is the fundamental difference between `git merge` and `git rebase`? When should you use each?**

<details>
<summary>Answer</summary>

`git merge` creates a new merge commit that combines two branches, preserving the full history of both. `git rebase` replays commits from one branch on top of another, creating a linear history but rewriting commit hashes.

Use **merge** for integrating shared branches and pull requests where you want to preserve history. Use **rebase** for keeping your local feature branch up to date with main before merging, but only when the branch has not been shared with others. The golden rule: never rebase commits that have been pushed to a shared branch.

</details>

**Q2: Why does trunk-based development align better with CI/CD than Git Flow?**

<details>
<summary>Answer</summary>

Trunk-based development uses short-lived branches (hours to a couple of days) that merge frequently into main. This means: (1) integration happens continuously rather than in big batches, (2) merge conflicts are small and easy to resolve, (3) the main branch is always in a deployable state, and (4) CI/CD pipelines run against changes that are close to what will be deployed. Git Flow's long-lived branches delay integration and create large, risky merges.

</details>

**Q3: What is a fast-forward merge, and why do some teams disable it?**

<details>
<summary>Answer</summary>

A fast-forward merge occurs when the target branch has no new commits since the feature branch was created. Git simply moves the branch pointer forward without creating a merge commit. Some teams disable fast-forward merges (`--no-ff`) because merge commits provide an explicit record of when features were integrated, making it easier to revert an entire feature and to see the history of integrations in `git log --graph`.

</details>

**Q4: How do branch naming conventions help CI/CD pipelines?**

<details>
<summary>Answer</summary>

CI/CD pipelines can use branch name patterns to trigger different workflows. For example: `feature/*` branches run unit tests and linting; `release/*` branches deploy to a staging environment and run integration tests; `hotfix/*` branches get fast-tracked through an abbreviated pipeline directly to production; `main` triggers production deployment. Without naming conventions, pipelines cannot distinguish between different types of work.

</details>

**Q5: You accidentally started working on `main` instead of a feature branch. You have three uncommitted files. How do you move this work to a new branch without losing anything?**

<details>
<summary>Answer</summary>

Since the changes are uncommitted, you can simply create and switch to a new branch:

```bash
git checkout -b feature/my-work
```

Your uncommitted changes (both staged and unstaged) travel with you to the new branch. Then stage and commit as normal. This works because uncommitted changes exist in the working directory and staging area, which are not branch-specific. If you had already committed to `main`, you would need `git reset` and `git cherry-pick` or `git stash` to move the work.

</details>
