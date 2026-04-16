# SAST, DAST, and SCA: Security Testing in CI/CD

## Why This Matters in DevOps

Security vulnerabilities in code fall into three categories: bugs you write
(your code has an SQL injection), bugs you import (a library you depend on has
a known CVE), and bugs you expose (your running application accepts malicious
input). Each category requires a different type of scanner.

SAST (Static Application Security Testing) finds bugs in your code before it
runs. SCA (Software Composition Analysis) finds known vulnerabilities in your
dependencies. DAST (Dynamic Application Security Testing) finds vulnerabilities
in your running application. Together, they form the security testing triad
that catches vulnerabilities at every stage.

Integrating these scanners into CI/CD transforms security from a manual,
periodic activity into a continuous, automated process. Every pull request is
scanned. Every dependency update is checked. Every deployment is tested.
Security becomes a quality gate, not an afterthought.

---

## Core Concepts

### Static Application Security Testing (SAST)

SAST analyzes source code or compiled bytecode without executing it. It looks
for patterns that indicate vulnerabilities:

```
Source Code → Parser → AST → Pattern Matching → Findings
```

What SAST finds:
- SQL injection
- Cross-site scripting (XSS)
- Path traversal
- Hardcoded credentials
- Insecure cryptography
- Buffer overflows
- Command injection
- Insecure deserialization

What SAST cannot find:
- Runtime configuration issues
- Authentication/authorization logic bugs
- Business logic vulnerabilities
- Issues that only manifest under specific conditions

#### Semgrep

Semgrep is an open-source SAST tool that uses lightweight, pattern-based rules:

```bash
# Install Semgrep
pip install semgrep

# Run with default rules
semgrep scan --config auto .
# Scanning 42 files...
#
# Findings:
#
# src/api/users.py
#   security.sql-injection
#   SQL injection via string concatenation
#   Details: https://sg.run/AbCd
#
#   15│ query = "SELECT * FROM users WHERE id = " + user_id
#   ⋮│
#
# src/api/auth.py
#   security.insecure-hash
#   Use of MD5 for password hashing
#   Details: https://sg.run/EfGh
#
#   28│ password_hash = hashlib.md5(password.encode()).hexdigest()

# Run with specific rule sets
semgrep scan --config p/python .
semgrep scan --config p/owasp-top-ten .
semgrep scan --config p/security-audit .

# Run with custom rules
cat > .semgrep.yml << 'EOF'
rules:
  - id: no-exec-calls
    pattern: exec($X)
    message: "Avoid exec() - potential code injection"
    languages: [python]
    severity: ERROR

  - id: no-shell-true
    pattern: subprocess.call(..., shell=True, ...)
    message: "subprocess with shell=True is vulnerable to injection"
    languages: [python]
    severity: ERROR

  - id: require-parameterized-queries
    patterns:
      - pattern: |
          cursor.execute("..." + $VAR)
      - pattern: |
          cursor.execute(f"...{$VAR}...")
      - pattern: |
          cursor.execute("...%s..." % $VAR)
    message: "Use parameterized queries to prevent SQL injection"
    languages: [python]
    severity: ERROR
    metadata:
      owasp: "A03:2021 - Injection"
      cwe: "CWE-89: SQL Injection"
EOF

semgrep scan --config .semgrep.yml .

# Output as JSON for CI integration
semgrep scan --config auto --json -o results.json .

# Output as SARIF for GitHub Security tab
semgrep scan --config auto --sarif -o results.sarif .
```

#### CodeQL (GitHub)

```yaml
# .github/workflows/codeql.yml
name: CodeQL Analysis
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday at 6 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      matrix:
        language: ['python', 'javascript']

    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

### Dynamic Application Security Testing (DAST)

DAST tests running applications by sending crafted requests and analyzing
responses. It finds vulnerabilities that only appear at runtime:

```
Running Application ← DAST Scanner sends malicious requests
    │                     │
    ▼                     ▼
Responses analyzed for vulnerability indicators:
  - Error messages revealing stack traces
  - SQL error messages (injection successful)
  - Reflected input (XSS)
  - Unexpected status codes
  - Missing security headers
  - Authentication bypasses
```

What DAST finds:
- SQL injection (confirmed, not just pattern-matched)
- XSS (reflected and stored)
- CSRF vulnerabilities
- Missing security headers
- Authentication/session issues
- Information disclosure
- SSL/TLS misconfigurations
- API security issues

What DAST cannot find:
- Dead code vulnerabilities (code paths not reachable)
- Exact line of code causing the issue
- Vulnerabilities in code not exposed via HTTP

#### OWASP ZAP

OWASP ZAP (Zed Attack Proxy) is the most popular open-source DAST tool:

```bash
# Run ZAP baseline scan (passive scanning)
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t https://myapp.example.com \
  -r report.html

# Output:
# PASS: Absence of Anti-CSRF Tokens [10202]
# WARN: Cookie Without SameSite Attribute [10054]
# WARN: CSP: Notices [10055]
# WARN: Missing Anti-clickjacking Header [10020]
# WARN: Server Leaks Version Information [10036]
# FAIL: Cross-Site Scripting (Reflected) [40012]
# FAIL: SQL Injection [40018]

# Run ZAP full scan (active scanning - sends attack payloads)
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
  -t https://myapp.example.com \
  -r full-report.html

# Run ZAP API scan (for REST APIs)
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py \
  -t https://myapp.example.com/openapi.json \
  -f openapi \
  -r api-report.html

# Run with custom configuration
cat > zap-rules.conf << 'EOF'
# Rule ID, Action (IGNORE, WARN, FAIL), Description
10020	WARN	Anti-clickjacking Header
10021	FAIL	X-Content-Type-Options Missing
10036	WARN	Server Leaks Version Information
40012	FAIL	Cross-Site Scripting (Reflected)
40018	FAIL	SQL Injection
40019	FAIL	SQL Injection - MySQL
40014	FAIL	Cross-Site Scripting (Persistent)
EOF

docker run --rm -v $(pwd):/zap/wrk:rw \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t https://myapp.example.com \
  -c zap-rules.conf \
  -r report.html
```

### Software Composition Analysis (SCA)

SCA scans your dependencies for known vulnerabilities (CVEs):

```bash
# Python - pip-audit
pip install pip-audit
pip-audit
# Found 2 known vulnerabilities in 1 package
# Name     Version  ID                 Fix Versions
# -------  -------  -----------------  ------------
# django   4.2.7    PYSEC-2024-001     4.2.9
# django   4.2.7    GHSA-xxxx-xxxx     4.2.9

# Python - safety
pip install safety
safety check
# +==============================================================================+
# | REPORT                                                                       |
# | checked 42 packages, using free vulnerability database                       |
# +==============================================================================+
# | package  | installed | affected | ID    | more info                          |
# +----------+-----------+----------+-------+------------------------------------+
# | django   | 4.2.7     | <4.2.9   | 12345 | https://pyup.io/v/12345/f/        |

# Node.js - npm audit
npm audit
# 3 vulnerabilities (1 moderate, 1 high, 1 critical)
#
# express  <4.19.2
# Severity: high
# Open Redirect - https://github.com/advisories/GHSA-xxxx
# fix available via `npm audit fix`

# Node.js - fix automatically
npm audit fix

# Go - govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...
# Scanning your code and 125 packages across 3 modules for known vulnerabilities...
#
# Vulnerability #1: GO-2024-0001
#   stdlib: net/http: memory exhaustion
#   Found in: net/http@go1.21.0
#   Fixed in: net/http@go1.21.6
#   More info: https://pkg.go.dev/vuln/GO-2024-0001

# Snyk (all-in-one: SCA + SAST + Container scanning)
npm install -g snyk
snyk auth
snyk test
# Testing /path/to/project...
#
# Tested 142 dependencies for known issues
# Found 3 issues, 1 with critical severity
#
# Issues:
#
# ✗ Remote Code Execution [Critical Severity]
#   in lodash@4.17.20
#   Fixed in: lodash@4.17.21
```

### Integrating All Scanners into CI/CD

```yaml
# .github/workflows/security-scanning.yaml
name: Security Scanning
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  # Stage 1: Static Analysis (fastest, runs first)
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep SAST
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            p/python
          generateSarif: true

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif

  # Stage 2: Dependency Scanning
  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit --format json --output audit-results.json
          pip-audit --strict  # Fail on any vulnerability

      - name: Run Trivy filesystem scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          format: 'sarif'
          output: 'trivy-fs.sarif'

      - name: Upload results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-fs.sarif

  # Stage 3: Container Scanning
  container-scan:
    needs: [sast, sca]  # Only build if code and deps are clean
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Scan container image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          format: 'sarif'
          output: 'trivy-image.sarif'

      - name: Upload results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-image.sarif

  # Stage 4: Dynamic Testing (requires running application)
  dast:
    needs: [container-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start application
        run: |
          docker build -t myapp:test .
          docker run -d -p 8080:8080 --name myapp myapp:test
          sleep 10  # Wait for application to start

      - name: Run OWASP ZAP baseline scan
        uses: zaproxy/action-baseline@v0.11.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: 'zap-rules.conf'
          fail_action: true
          cmd_options: '-a'

      - name: Upload ZAP report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: zap-report
          path: report_html.html

      - name: Cleanup
        if: always()
        run: docker stop myapp
```

### Snyk: All-in-One Security Platform

```bash
# Snyk combines SAST, SCA, and container scanning
# Install
npm install -g snyk
snyk auth

# SCA: Test dependencies
snyk test
# Tested 142 dependencies for known issues, found 3 issues

# SAST: Test source code
snyk code test
# Testing /path/to/project ...
# ✗ [High] SQL Injection
#   Path: src/api/users.py, line 15

# Container scanning
snyk container test myapp:latest
# Testing myapp:latest...
# ✗ High severity vulnerability found in openssl/libssl3
#   From: openssl/libssl3@3.0.11

# Monitor (continuous scanning)
snyk monitor
# Monitoring /path/to/project ...
# Explore this snapshot at https://app.snyk.io/...

# Fix suggestions
snyk fix
# Applies fixes automatically where possible
```

---

## Step-by-Step Practical

### Adding Security Scanning to a GitHub Actions Pipeline

```bash
# 1. Create a vulnerable Python application for testing
mkdir -p security-demo/src
cd security-demo

cat > src/app.py << 'PYEOF'
from flask import Flask, request
import sqlite3
import hashlib
import subprocess
import pickle
import yaml

app = Flask(__name__)

# Vulnerability: SQL Injection
@app.route('/users')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    # BAD: String concatenation in SQL query
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return str(cursor.fetchall())

# Vulnerability: Weak cryptography
@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    # BAD: MD5 for password hashing
    password_hash = hashlib.md5(password.encode()).hexdigest()
    return f"Hash: {password_hash}"

# Vulnerability: Command injection
@app.route('/ping')
def ping():
    host = request.args.get('host')
    # BAD: shell=True with user input
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)
    return result.stdout.decode()

# Vulnerability: Insecure deserialization
@app.route('/load', methods=['POST'])
def load_data():
    data = request.get_data()
    # BAD: pickle.loads with untrusted data
    obj = pickle.loads(data)
    return str(obj)

# Vulnerability: Unsafe YAML loading
@app.route('/config', methods=['POST'])
def load_config():
    config_data = request.get_data().decode()
    # BAD: yaml.load without SafeLoader
    config = yaml.load(config_data)
    return str(config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
PYEOF

cat > requirements.txt << 'EOF'
flask==3.0.0
pyyaml==6.0.1
gunicorn==21.2.0
EOF

# 2. Run Semgrep locally
pip install semgrep
semgrep scan --config p/security-audit --config p/python src/
# Should find:
# - SQL injection (string concatenation)
# - Weak hash (MD5)
# - Command injection (shell=True)
# - Insecure deserialization (pickle.loads)
# - Unsafe YAML loading (yaml.load without SafeLoader)

# 3. Run pip-audit
pip install pip-audit
pip-audit -r requirements.txt

# 4. Create the CI/CD workflow
mkdir -p .github/workflows

cat > .github/workflows/security.yaml << 'GHEOF'
name: Security Pipeline
on:
  pull_request:
    branches: [main]

jobs:
  sast-scan:
    name: SAST with Semgrep
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Semgrep scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit p/owasp-top-ten

  dependency-scan:
    name: SCA with pip-audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: |
          pip install -r requirements.txt
          pip install pip-audit
          pip-audit --strict

  container-scan:
    name: Container scan with Trivy
    needs: [sast-scan, dependency-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:test .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:test
          severity: CRITICAL,HIGH
          exit-code: '1'
GHEOF

echo "Security scanning pipeline created successfully."
echo "Found vulnerabilities will block the PR from merging."
```

---

## Exercises

### Exercise 1: SAST with Semgrep
Write a Python or JavaScript application with five intentional vulnerabilities
(SQL injection, XSS, command injection, hardcoded secret, insecure
deserialization). Run Semgrep with multiple rule sets and verify it finds all
five. Write a custom Semgrep rule that catches a vulnerability pattern specific
to your codebase.

### Exercise 2: SCA Deep Dive
Create a Python project with `requirements.txt` that includes at least three
packages with known vulnerabilities (use older versions). Run pip-audit, Trivy
fs scan, and Snyk test. Compare the results: do all tools find the same
vulnerabilities? Which provides the most actionable output?

### Exercise 3: DAST with OWASP ZAP
Deploy the vulnerable Flask application from the practical section. Run OWASP
ZAP baseline scan and full scan against it. Compare the findings between
baseline and full scan. Document which vulnerabilities DAST found that SAST
missed, and vice versa.

### Exercise 4: Complete Pipeline
Build a GitHub Actions workflow that runs SAST (Semgrep), SCA (pip-audit +
Trivy), container scanning (Trivy), and DAST (ZAP) in sequence. Configure
each tool to fail the pipeline on high-severity findings. Upload all results
as SARIF to GitHub Security tab. Test with both a vulnerable and a fixed
version of the application.

### Exercise 5: Custom Rules
Write three custom Semgrep rules for your organization's specific patterns:
one that catches use of a deprecated internal API, one that enforces use of
the company's logging library instead of print statements, and one that
requires all database queries to use the ORM instead of raw SQL. Test each
rule against sample code.

---

## Knowledge Check

### Question 1
What is the difference between SAST and DAST, and why do you need both?

**Answer:** SAST (Static Application Security Testing) analyzes source code
without executing it, finding vulnerabilities through pattern matching and
data flow analysis. It runs early (on every commit), is fast, and identifies
the exact line of code with the vulnerability. DAST (Dynamic Application
Security Testing) tests a running application by sending malicious requests
and analyzing responses. It finds runtime vulnerabilities that SAST cannot
detect (authentication bypasses, misconfigurations, response header issues).
You need both because they complement each other: SAST catches issues at the
code level (SQL injection patterns, insecure functions), while DAST confirms
exploitability and finds issues that only manifest at runtime (missing security
headers, session management bugs).

### Question 2
What is SCA and how does it differ from SAST?

**Answer:** SCA (Software Composition Analysis) scans third-party dependencies
(libraries, frameworks, packages) for known vulnerabilities by checking them
against vulnerability databases (NVD, GitHub Advisory Database, OSV). SAST
scans your own source code for vulnerability patterns. SCA finds issues in
code you did not write (but depend on), while SAST finds issues in code you
did write. SCA matches package names and versions against known CVEs, while
SAST performs pattern matching and data flow analysis on source code. Both are
essential: SAST catches your bugs, SCA catches other people's bugs that you
have imported.

### Question 3
Why should security scanners fail the CI/CD pipeline?

**Answer:** If security scanners only warn but do not fail the pipeline,
vulnerabilities accumulate because there is no enforcement mechanism. Developers
see warnings, plan to fix them "later," and the warnings are eventually ignored.
Failing the pipeline creates a hard gate: code with critical vulnerabilities
cannot be merged or deployed. This is the "shift left" principle in action:
the cost of fixing is low (developer fixes before merge), and the alternative
(deploying vulnerable code) is unacceptable. The key is tuning severity
thresholds: fail on CRITICAL and HIGH, warn on MEDIUM, ignore LOW. This
prevents alert fatigue while maintaining security standards.

### Question 4
How do you handle false positives in security scanning?

**Answer:** False positives are inevitable in security scanning. Handle them
through: (1) Tool-specific suppression -- Semgrep supports `# nosemgrep`
inline comments, Trivy supports `.trivyignore` files. (2) Risk-based triage
-- verify whether the finding is actually exploitable in your context.
(3) Custom rules -- tune scanner rules to reduce false positives for your
codebase. (4) Documented exceptions -- when suppressing a finding, document
why it is a false positive so future auditors understand the decision.
(5) Periodic review -- review suppressed findings regularly (quarterly) to
ensure they are still valid. Never suppress without documentation, and never
suppress CRITICAL findings without a thorough review.

### Question 5
What is SARIF and why is it important for security tooling?

**Answer:** SARIF (Static Analysis Results Interchange Format) is a standard
JSON format for expressing the output of static analysis tools. It is important
because it provides a common format that allows different tools to report
findings in a consistent way. GitHub Security tab natively supports SARIF,
so findings from any SARIF-compatible tool (Semgrep, Trivy, CodeQL, ZAP)
appear in the same unified dashboard. This enables: centralized vulnerability
management across all scanners, consistent reporting regardless of the tool,
integration with issue tracking and remediation workflows, and historical
tracking of findings over time. Without SARIF, each tool has its own output
format, making aggregation and management difficult.
