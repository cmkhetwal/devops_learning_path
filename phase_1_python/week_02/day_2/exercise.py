"""
Week 2, Day 2: Nested Conditions & Logical Operators - Exercise
================================================================
Complete each task below. Replace '# YOUR CODE HERE' with your solution.
Run 'python check.py' when you are done to see your score!
"""

# ---------------------------------------------------------------------------
# TASK 1: Dual Resource Alert
# ---------------------------------------------------------------------------
# You are monitoring a server. Two variables are given:
#   cpu_usage  (a number, percentage)
#   mem_usage  (a number, percentage)
#
# If BOTH cpu_usage > 90 AND mem_usage > 90, print "CRITICAL: Both resources maxed"
# If ONLY cpu_usage > 90 (but not memory), print "WARNING: High CPU"
# If ONLY mem_usage > 90 (but not CPU), print "WARNING: High Memory"
# Otherwise, print "OK"

cpu_usage = 95
mem_usage = 92

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 2: Access Control
# ---------------------------------------------------------------------------
# Variables: role (string), is_authenticated (boolean)
#
# Rules:
#   - If role is "admin" AND is_authenticated is True, print "Full access"
#   - If role is "admin" AND is_authenticated is False, print "Login required"
#   - If role is "viewer" AND is_authenticated is True, print "Read-only access"
#   - For anything else, print "Access denied"

role = "admin"
is_authenticated = True

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 3: Deploy Gate Check
# ---------------------------------------------------------------------------
# Variables:
#   tests_passing    (boolean)
#   is_deploy_freeze (boolean)
#   environment      (string)
#
# Deploy is allowed ONLY if ALL of these are true:
#   - tests_passing is True
#   - is_deploy_freeze is False  (hint: use 'not')
#   - environment is NOT "production" OR environment is "production" and
#     tests_passing is True and is_deploy_freeze is False
#
# Simplified rules:
#   If tests_passing is True AND is_deploy_freeze is False, print "Deploy approved"
#   Otherwise, print "Deploy blocked"

tests_passing = True
is_deploy_freeze = False

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 4: Server Tier Classification
# ---------------------------------------------------------------------------
# Variables: cpu_cores (int), ram_gb (int)
#
# Classification rules (check in this order):
#   - If cpu_cores >= 16 AND ram_gb >= 64, print "Tier 1: Production"
#   - If cpu_cores >= 8 AND ram_gb >= 32, print "Tier 2: Staging"
#   - If cpu_cores >= 4 AND ram_gb >= 16, print "Tier 3: Development"
#   - Otherwise, print "Tier 4: Testing"

cpu_cores = 8
ram_gb = 32

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 5: Nested Incident Response
# ---------------------------------------------------------------------------
# Variables:
#   is_critical    (boolean)  - Is this a critical incident?
#   is_production  (boolean)  - Is this in production?
#   is_acknowledged (boolean) - Has someone acknowledged the incident?
#
# Logic (use NESTED if statements):
#   First check if is_critical is True:
#       If yes, then check if is_production is True:
#           If yes, then check if is_acknowledged is True:
#               If yes, print "Critical production incident: team notified"
#               If no, print "Critical production incident: paging on-call"
#           If is_production is False:
#               print "Critical non-production incident: logged"
#   If is_critical is False:
#       print "Minor incident: monitoring"

is_critical = True
is_production = True
is_acknowledged = False

# YOUR CODE HERE
