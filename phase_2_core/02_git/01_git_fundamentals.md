# Git Fundamentals

## Why This Matters in DevOps

Version control is the bedrock of every DevOps practice. Without it, infrastructure as code is just scripts on someone's laptop, CI/CD pipelines have nothing to trigger against, and collaboration degenerates into emailing zip files. Git is not merely a developer tool; it is the single source of truth for your entire software delivery lifecycle.

In a DevOps culture, every artifact that defines your system -- application code, Dockerfiles, Kubernetes manifests, Terraform configurations, Ansible playbooks, pipeline definitions -- lives in Git. This principle, often called "everything as code," means that Git becomes the audit log, the collaboration platform, and the deployment trigger all at once. When an incident occurs at 3 AM, `git log` tells you exactly what changed and who changed it. When a new team member joins, `git clone` gives them the entire history of every decision ever made.

The philosophy is simple: if it is not in Git, it does not exist. Configuration drift, undocumented changes, and tribal knowledge are the enemies of reliable operations. Git eliminates all three.

---

## Core Concepts

### What Is Version Control?

Version control is a system that records changes to files over time so you can recall specific versions later. Git is a **distributed** version control system (DVCS), meaning every developer has a complete copy of the repository, including the entire history. This stands in contrast to centralized systems like SVN where a single server holds the history.

### Git Architecture: The Three Trees

Git organizes your work into three distinct areas:

```
Working Directory  -->  Staging Area (Index)  -->  Repository (.git)
   (your files)         (next commit preview)      (committed history)
```

1. **Working Directory (Working Tree):** The actual files on your filesystem. You edit files here.
2. **Staging Area (Index):** A holding area where you prepare the next commit. Think of it as a draft of your next snapshot.
3. **Repository (.git directory):** The database of all commits, branches, and history. This is what makes Git powerful.

This three-stage architecture gives you fine-grained control. You can modify ten files but only commit three of them, keeping the rest for a separate, logically distinct commit.

### How Git Stores Data

Git does not store diffs. It stores **snapshots**. Every commit is a complete snapshot of your entire project at that point in time. Git is smart about this: if a file has not changed, Git stores a pointer to the previous identical file rather than a duplicate. This makes Git fast and efficient.

Each commit is identified by a SHA-1 hash (a 40-character hexadecimal string) computed from the commit contents, parent commit, author, timestamp, and message. This means commits are immutable and tamper-proof -- a property that matters deeply when Git becomes your audit trail.

### The .git Directory

When you initialize a repository, Git creates a `.git` directory containing:

- `HEAD` -- pointer to the current branch
- `objects/` -- all commits, trees, and blobs (file contents)
- `refs/` -- pointers to commits (branches and tags)
- `index` -- the staging area
- `config` -- repository-specific configuration

You should never need to edit these files directly, but understanding they exist demystifies Git.

---

## Step-by-Step Practical

### Initializing a Repository

```bash
# Create a project directory
mkdir ~/devops-project && cd ~/devops-project

# Initialize a Git repository
git init
```

Expected output:

```
Initialized empty Git repository in /home/user/devops-project/.git/
```

### Configuring Your Identity

```bash
# Set your name and email (required for commits)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Verify configuration
git config --list --global
```

Expected output:

```
user.name=Your Name
user.email=you@example.com
```

### Creating and Tracking Files

```bash
# Create a Terraform configuration file
cat > main.tf <<'EOF'
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
}
EOF

# Check repository status
git status
```

Expected output:

```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	main.tf

nothing added to commit but untracked files present (use "git add" to track)
```

### Staging and Committing

```bash
# Stage the file
git add main.tf

# Check status again -- note the difference
git status
```

Expected output:

```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   main.tf
```

```bash
# Commit with a descriptive message
git commit -m "Add initial AWS infrastructure configuration"
```

Expected output:

```
[main (root-commit) a1b2c3d] Add initial AWS infrastructure configuration
 1 file changed, 8 insertions(+)
 create mode 100644 main.tf
```

### Viewing History

```bash
# View commit log
git log
```

Expected output:

```
commit a1b2c3d4e5f6789... (HEAD -> main)
Author: Your Name <you@example.com>
Date:   Thu Apr 16 10:00:00 2026 +0000

    Add initial AWS infrastructure configuration
```

```bash
# Compact log format (useful for quick scanning)
git log --oneline
```

Expected output:

```
a1b2c3d Add initial AWS infrastructure configuration
```

### Viewing Changes with diff

```bash
# Modify the file
echo '  tags = { Name = "web-server" }' >> main.tf

# See what changed in the working directory
git diff
```

Expected output:

```diff
diff --git a/main.tf b/main.tf
index 1234567..abcdefg 100644
--- a/main.tf
+++ b/main.tf
@@ -5,4 +5,5 @@ resource "aws_instance" "web" {
   ami           = "ami-0c55b159cbfafe1f0"
   instance_type = "t2.micro"
+  tags = { Name = "web-server" }
 }
```

```bash
# Stage the change and see the staged diff
git add main.tf
git diff --staged
```

### Cloning an Existing Repository

```bash
# Clone a remote repository
git clone https://github.com/example/infrastructure.git

# Clone into a specific directory
git clone https://github.com/example/infrastructure.git my-infra
```

### Creating a .gitignore

The `.gitignore` file tells Git which files to never track. This is critical for security and cleanliness.

```bash
cat > .gitignore <<'EOF'
# Terraform
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl

# Secrets -- NEVER commit these
*.pem
*.key
.env
secrets.yaml

# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
EOF

git add .gitignore
git commit -m "Add .gitignore for Terraform project"
```

---

## Exercises

### Exercise 1: Initialize and Track a DevOps Project

Create a new directory called `ansible-project`. Inside it, initialize a Git repository, create an `inventory.ini` file and a `playbook.yml` file with placeholder content, and make your first commit with an appropriate message.

### Exercise 2: Practice the Staging Area

Create three files: `app.py`, `test_app.py`, and `notes.txt`. Stage and commit only `app.py` and `test_app.py` in one commit, then stage and commit `notes.txt` separately. Use `git log --oneline` to verify you have two commits.

### Exercise 3: Build a Comprehensive .gitignore

Create a `.gitignore` file suitable for a project that uses Python, Docker, Terraform, and Ansible. It should exclude compiled Python files, virtual environments, Terraform state, Docker override files, Ansible retry files, and any files that might contain secrets. Commit it with an appropriate message.

### Exercise 4: Investigate History

After making at least three commits, practice using `git log` with different flags: `--oneline`, `--graph`, `--stat`, and `--patch`. Write down what each flag shows you and when you would use it during incident response.

### Exercise 5: Understand the Diff Workflow

Modify a file, then run `git diff` to see unstaged changes. Stage the file and run `git diff --staged` to see staged changes. Run `git diff HEAD` to see all changes since the last commit. Document the difference between these three commands.

---

## Knowledge Check

**Q1: What are the three areas (trees) in Git's architecture, and what role does each play?**

<details>
<summary>Answer</summary>

1. **Working Directory:** Where you edit files directly on disk.
2. **Staging Area (Index):** Where you prepare and curate changes for the next commit. It acts as a preview of what will be committed.
3. **Repository (.git):** The permanent history of all commits. Once committed, changes are safely stored and can be retrieved at any time.

</details>

**Q2: Why is `.gitignore` critical in a DevOps context? Name three categories of files that should always be ignored.**

<details>
<summary>Answer</summary>

`.gitignore` prevents sensitive, generated, or environment-specific files from being committed. Three critical categories:

1. **Secrets and credentials:** `.env`, `*.pem`, `*.key`, `secrets.yaml` -- committing these is a security breach.
2. **Generated state files:** `*.tfstate`, `.terraform/`, `__pycache__/` -- these are environment-specific and should not be shared.
3. **IDE and OS files:** `.vscode/`, `.idea/`, `.DS_Store` -- these are developer-specific and create noise in the repository.

</details>

**Q3: What does the phrase "infrastructure as code starts with version control" mean in practice?**

<details>
<summary>Answer</summary>

It means that every piece of infrastructure configuration -- Terraform files, Ansible playbooks, Dockerfiles, Kubernetes manifests, CI/CD pipeline definitions -- must be stored in Git. This provides: (1) an audit trail of who changed what and when, (2) the ability to roll back to any previous state, (3) collaboration through pull requests and code review, and (4) the foundation for automated pipelines that trigger on Git events. Without version control, infrastructure as code is just unmanaged scripts.

</details>

**Q4: Git stores snapshots, not diffs. Why does this design decision matter?**

<details>
<summary>Answer</summary>

Storing snapshots means every commit is a complete, self-contained picture of the project. This makes branching and merging fast (Git just moves pointers rather than replaying diffs), enables integrity checking (each snapshot is hashed), and simplifies operations like checkout and reset (Git can reconstruct any point in time without replaying a chain of diffs). It also means Git can detect file renames and copies by comparing snapshots rather than tracking them explicitly.

</details>

**Q5: What is the difference between `git diff`, `git diff --staged`, and `git diff HEAD`?**

<details>
<summary>Answer</summary>

- `git diff` shows changes in the working directory that have NOT been staged.
- `git diff --staged` (or `--cached`) shows changes that HAVE been staged but not yet committed.
- `git diff HEAD` shows ALL changes (both staged and unstaged) compared to the last commit.

Understanding these three commands is essential for knowing exactly what will be included in your next commit.

</details>
