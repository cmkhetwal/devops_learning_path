# Week 11, Day 2: Jenkins API with Python

## What You'll Learn

- How to interact with Jenkins CI/CD server using its REST API
- Using Python's `requests` library to trigger builds and check job status
- Building a Jenkins API client for automation

## Why This Matters for DevOps

Jenkins is one of the most widely used CI/CD servers. Being able to
programmatically trigger builds, check statuses, and manage jobs through
its API enables powerful automation -- from ChatOps bots to deployment
orchestrators.

---

## 1. Jenkins REST API Basics

Jenkins exposes a REST API at every URL by appending `/api/json`:

```
http://jenkins-server:8080/api/json              # Server info
http://jenkins-server:8080/job/my-job/api/json    # Job info
http://jenkins-server:8080/job/my-job/42/api/json # Build #42 info
```

## 2. Authentication

Jenkins uses Basic Auth or API tokens:

```python
import requests

JENKINS_URL = "http://jenkins:8080"
USERNAME = "admin"
API_TOKEN = "your-api-token"

# All requests use basic auth
response = requests.get(
    f"{JENKINS_URL}/api/json",
    auth=(USERNAME, API_TOKEN)
)
print(response.json())
```

## 3. Listing Jobs

```python
def list_jobs(jenkins_url, auth):
    """Get all jobs from Jenkins."""
    response = requests.get(
        f"{jenkins_url}/api/json?tree=jobs[name,color,url]",
        auth=auth
    )
    response.raise_for_status()
    data = response.json()

    for job in data["jobs"]:
        status = "SUCCESS" if job["color"] == "blue" else "FAILURE"
        print(f"  {job['name']}: {status}")

    return data["jobs"]
```

## 4. Getting Job Details

```python
def get_job_info(jenkins_url, job_name, auth):
    """Get detailed info about a specific job."""
    response = requests.get(
        f"{jenkins_url}/job/{job_name}/api/json",
        auth=auth
    )
    response.raise_for_status()
    data = response.json()

    print(f"Job: {data['name']}")
    print(f"URL: {data['url']}")
    print(f"Buildable: {data.get('buildable', False)}")
    print(f"Last build: #{data.get('lastBuild', {}).get('number', 'N/A')}")

    return data
```

## 5. Triggering a Build

```python
def trigger_build(jenkins_url, job_name, auth, parameters=None):
    """Trigger a Jenkins build, optionally with parameters."""
    if parameters:
        url = f"{jenkins_url}/job/{job_name}/buildWithParameters"
        response = requests.post(url, auth=auth, data=parameters)
    else:
        url = f"{jenkins_url}/job/{job_name}/build"
        response = requests.post(url, auth=auth)

    if response.status_code == 201:
        print(f"Build triggered for {job_name}!")
        # Get queue location from headers
        queue_url = response.headers.get("Location")
        return queue_url
    else:
        print(f"Failed: {response.status_code}")
        return None
```

## 6. Checking Build Status

```python
def get_build_status(jenkins_url, job_name, build_number, auth):
    """Check the status of a specific build."""
    response = requests.get(
        f"{jenkins_url}/job/{job_name}/{build_number}/api/json",
        auth=auth
    )
    response.raise_for_status()
    data = response.json()

    return {
        "number": data["number"],
        "result": data.get("result", "IN_PROGRESS"),
        "duration": data.get("duration", 0),
        "timestamp": data.get("timestamp", 0),
        "building": data.get("building", False),
    }
```

## 7. Getting Console Output

```python
def get_console_output(jenkins_url, job_name, build_number, auth):
    """Get the console output of a build."""
    response = requests.get(
        f"{jenkins_url}/job/{job_name}/{build_number}/consoleText",
        auth=auth
    )
    return response.text
```

## 8. Waiting for a Build to Complete

```python
import time

def wait_for_build(jenkins_url, job_name, build_number, auth, timeout=300):
    """Poll until a build completes or timeout."""
    start = time.time()

    while time.time() - start < timeout:
        status = get_build_status(jenkins_url, job_name, build_number, auth)
        if not status["building"]:
            return status
        print(f"  Build #{build_number} still running...")
        time.sleep(10)

    raise TimeoutError(f"Build did not complete within {timeout}s")
```

## 9. Complete Jenkins Client Class

```python
class JenkinsClient:
    """A simple Jenkins API client."""

    def __init__(self, url, username, token):
        self.url = url.rstrip("/")
        self.auth = (username, token)

    def get(self, path):
        resp = requests.get(f"{self.url}{path}", auth=self.auth)
        resp.raise_for_status()
        return resp.json()

    def post(self, path, data=None):
        resp = requests.post(f"{self.url}{path}", auth=self.auth, data=data)
        return resp

    def list_jobs(self):
        return self.get("/api/json")["jobs"]

    def trigger(self, job_name, params=None):
        if params:
            return self.post(f"/job/{job_name}/buildWithParameters", params)
        return self.post(f"/job/{job_name}/build")

    def last_build(self, job_name):
        return self.get(f"/job/{job_name}/lastBuild/api/json")
```

## DevOps Connection

Jenkins API automation enables:
- **ChatOps**: Trigger deployments from Slack or Teams
- **Pipeline orchestration**: Chain jobs across multiple Jenkins instances
- **Monitoring dashboards**: Show build statuses on a wall display
- **Automated rollback**: Detect failed builds and trigger rollback jobs
- **Compliance reporting**: Audit all builds and their results

---

## Key Takeaways

| Operation | Endpoint |
|-----------|----------|
| List jobs | `GET /api/json` |
| Job info | `GET /job/{name}/api/json` |
| Trigger build | `POST /job/{name}/build` |
| Build status | `GET /job/{name}/{num}/api/json` |
| Console output | `GET /job/{name}/{num}/consoleText` |
| Auth method | Basic Auth (username + API token) |
