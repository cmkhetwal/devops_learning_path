"""
Week 11, Day 2: Exercise - Jenkins API Client (Simulated)

Build a Jenkins API client using SIMULATED data. No actual Jenkins
server is needed. You'll work with mock data structures that mimic
what the Jenkins REST API returns.

TASKS:
    1. JenkinsClient class      - Initialize and store connection info
    2. list_jobs()              - Parse and format job listings
    3. get_job_details()        - Get detailed job information
    4. trigger_build()          - Simulate triggering a build
    5. get_build_status()       - Check build result and duration
    6. generate_build_report()  - Create a summary report of all jobs
"""

# ============================================================
# MOCK JENKINS DATA (simulates Jenkins REST API responses)
# ============================================================

JENKINS_JOBS = {
    "jobs": [
        {
            "name": "webapp-build",
            "color": "blue",
            "url": "http://jenkins:8080/job/webapp-build/",
            "buildable": True,
            "lastBuild": {"number": 142, "url": "http://jenkins:8080/job/webapp-build/142/"},
            "lastSuccessfulBuild": {"number": 142},
            "lastFailedBuild": {"number": 139},
        },
        {
            "name": "api-tests",
            "color": "red",
            "url": "http://jenkins:8080/job/api-tests/",
            "buildable": True,
            "lastBuild": {"number": 87, "url": "http://jenkins:8080/job/api-tests/87/"},
            "lastSuccessfulBuild": {"number": 85},
            "lastFailedBuild": {"number": 87},
        },
        {
            "name": "deploy-staging",
            "color": "blue",
            "url": "http://jenkins:8080/job/deploy-staging/",
            "buildable": True,
            "lastBuild": {"number": 56, "url": "http://jenkins:8080/job/deploy-staging/56/"},
            "lastSuccessfulBuild": {"number": 56},
            "lastFailedBuild": {"number": 50},
        },
        {
            "name": "deploy-production",
            "color": "blue_anime",
            "url": "http://jenkins:8080/job/deploy-production/",
            "buildable": True,
            "lastBuild": {"number": 23, "url": "http://jenkins:8080/job/deploy-production/23/"},
            "lastSuccessfulBuild": {"number": 22},
            "lastFailedBuild": {"number": 20},
        },
        {
            "name": "nightly-backup",
            "color": "disabled",
            "url": "http://jenkins:8080/job/nightly-backup/",
            "buildable": False,
            "lastBuild": {"number": 365, "url": "http://jenkins:8080/job/nightly-backup/365/"},
            "lastSuccessfulBuild": {"number": 365},
            "lastFailedBuild": {"number": 340},
        },
    ]
}

JENKINS_BUILDS = {
    "webapp-build": {
        142: {"number": 142, "result": "SUCCESS", "duration": 45000, "timestamp": 1705312200000, "building": False,
              "actions": [{"parameters": [{"name": "BRANCH", "value": "main"}]}]},
        141: {"number": 141, "result": "SUCCESS", "duration": 43000, "timestamp": 1705225800000, "building": False,
              "actions": [{"parameters": [{"name": "BRANCH", "value": "main"}]}]},
        140: {"number": 140, "result": "SUCCESS", "duration": 47000, "timestamp": 1705139400000, "building": False,
              "actions": [{"parameters": [{"name": "BRANCH", "value": "develop"}]}]},
        139: {"number": 139, "result": "FAILURE", "duration": 12000, "timestamp": 1705053000000, "building": False,
              "actions": [{"parameters": [{"name": "BRANCH", "value": "feature/new-ui"}]}]},
    },
    "api-tests": {
        87: {"number": 87, "result": "FAILURE", "duration": 120000, "timestamp": 1705312200000, "building": False,
             "actions": [{"parameters": [{"name": "SUITE", "value": "full"}]}]},
        86: {"number": 86, "result": "SUCCESS", "duration": 95000, "timestamp": 1705225800000, "building": False,
             "actions": [{"parameters": [{"name": "SUITE", "value": "smoke"}]}]},
        85: {"number": 85, "result": "SUCCESS", "duration": 98000, "timestamp": 1705139400000, "building": False,
             "actions": [{"parameters": [{"name": "SUITE", "value": "full"}]}]},
    },
    "deploy-staging": {
        56: {"number": 56, "result": "SUCCESS", "duration": 180000, "timestamp": 1705312200000, "building": False,
             "actions": [{"parameters": [{"name": "VERSION", "value": "2.1.0"}]}]},
        55: {"number": 55, "result": "SUCCESS", "duration": 175000, "timestamp": 1705225800000, "building": False,
             "actions": [{"parameters": [{"name": "VERSION", "value": "2.0.9"}]}]},
    },
    "deploy-production": {
        23: {"number": 23, "result": None, "duration": 0, "timestamp": 1705312200000, "building": True,
             "actions": [{"parameters": [{"name": "VERSION", "value": "2.1.0"}]}]},
        22: {"number": 22, "result": "SUCCESS", "duration": 200000, "timestamp": 1705225800000, "building": False,
             "actions": [{"parameters": [{"name": "VERSION", "value": "2.0.8"}]}]},
    },
    "nightly-backup": {
        365: {"number": 365, "result": "SUCCESS", "duration": 600000, "timestamp": 1705312200000, "building": False,
              "actions": [{"parameters": []}]},
    },
}


# ============================================================
# TASK 1: JenkinsClient.__init__(self, url, username, token)
#
# Create a JenkinsClient class. The __init__ should:
#   - Store url (strip trailing slashes), username, token
#   - Store a tuple (username, token) as self.auth
#   - Store the mock data: self.jobs_data and self.builds_data
#     (accept these as optional params, default to the constants)
#
# Also implement __repr__ returning:
#   "JenkinsClient(http://jenkins:8080, user=admin)"
# ============================================================
# TASK 2: list_jobs(self)
#
# Return a list of dicts, one per job, with:
#   - "name": job name (string)
#   - "status": one of "SUCCESS", "FAILURE", "RUNNING", "DISABLED"
#     (blue=SUCCESS, red=FAILURE, *_anime=RUNNING, disabled=DISABLED)
#   - "last_build": last build number (int)
#   - "buildable": whether the job can be built (bool)
# ============================================================
# TASK 3: get_job_details(self, job_name)
#
# Return a dict with:
#   - "name": job name
#   - "url": job URL
#   - "status": same logic as list_jobs
#   - "last_build": number of last build
#   - "last_success": number of last successful build
#   - "last_failure": number of last failed build
#   - "health": "GOOD" if last build == last successful build,
#               "BAD" if last build == last failed build,
#               "BUILDING" if status is RUNNING
#
# If job_name not found, return None.
# ============================================================
# TASK 4: trigger_build(self, job_name, parameters=None)
#
# Simulate triggering a build. Return a dict with:
#   - "status": "TRIGGERED" if job is buildable, "FAILED" otherwise
#   - "job": job_name
#   - "next_build": last build number + 1 (if triggered)
#   - "parameters": the parameters dict (or {} if None)
#   - "message": a descriptive message
#
# If job doesn't exist, return status "FAILED" with appropriate message.
# ============================================================
# TASK 5: get_build_status(self, job_name, build_number)
#
# Return a dict with:
#   - "job": job_name
#   - "number": build number
#   - "result": "SUCCESS", "FAILURE", or "IN_PROGRESS"
#   - "duration_seconds": duration in seconds (duration is in ms)
#   - "building": boolean
#   - "parameters": dict of parameter name->value from actions
#
# If job or build not found, return None.
# ============================================================
# TASK 6: generate_build_report(self)
#
# Return a string report summarizing all jobs:
#
# === Jenkins Build Report ===
#
# Job: webapp-build
#   Status: SUCCESS
#   Last Build: #142
#   Health: GOOD
#
# Job: api-tests
#   Status: FAILURE
#   Last Build: #87
#   Health: BAD
# ...
#
# Summary:
#   Total Jobs: 5
#   Healthy: 2
#   Failing: 1
#   Running: 1
#   Disabled: 1
# ============================================================

class JenkinsClient:
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    client = JenkinsClient("http://jenkins:8080/", "admin", "secret-token")
    print(repr(client))

    print("\n=== Jobs ===")
    jobs = client.list_jobs()
    if jobs:
        for j in jobs:
            print(f"  {j['name']}: {j['status']} (#{j['last_build']})")

    print("\n=== Job Details ===")
    details = client.get_job_details("webapp-build")
    if details:
        for k, v in details.items():
            print(f"  {k}: {v}")

    print("\n=== Trigger Build ===")
    result = client.trigger_build("webapp-build", {"BRANCH": "main"})
    if result:
        print(f"  {result}")

    print("\n=== Build Status ===")
    status = client.get_build_status("webapp-build", 142)
    if status:
        for k, v in status.items():
            print(f"  {k}: {v}")

    print("\n=== Report ===")
    report = client.generate_build_report()
    if report:
        print(report)
