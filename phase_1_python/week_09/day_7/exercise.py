"""
Week 9, Day 7: Quiz Day - Docker & Containers

WEEK 9 QUIZ
============

Answer each question by assigning the correct value to the variable.
Read each question carefully!

TASKS
-----
10 quiz questions covering Docker SDK, containers, images, compose, monitoring
"""


# ============================================================
# QUESTION 1: Docker SDK Connection
# ============================================================
# What function do you call to connect to a local Docker daemon?
# a) docker.connect()
# b) docker.from_env()
# c) docker.DockerClient()
# d) docker.local()
q1 = ""  # YOUR ANSWER: assign "a", "b", "c", or "d"

# YOUR CODE HERE


# ============================================================
# QUESTION 2: List All Containers
# ============================================================
# To list ALL containers (including stopped), what argument do you pass?
# a) client.containers.list(running=False)
# b) client.containers.list(all=True)
# c) client.containers.list(status="all")
# d) client.containers.all()
q2 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 3: Container Status Values
# ============================================================
# Which of these is NOT a valid Docker container status?
# a) "running"
# b) "exited"
# c) "paused"
# d) "terminated"
q3 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 4: Docker Image Pull
# ============================================================
# What is the correct way to pull a specific tag of an image?
# a) client.images.pull("nginx:latest")
# b) client.images.pull("nginx", tag="latest")
# c) client.images.download("nginx", "latest")
# d) Both a and b work
q4 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 5: YAML Safe Load
# ============================================================
# Why do we use yaml.safe_load() instead of yaml.load()?
# a) It is faster
# b) It prevents arbitrary code execution from YAML
# c) It handles Unicode better
# d) It auto-formats the output
q5 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 6: Docker Compose Version
# ============================================================
# In a docker-compose.yml, what is the typical version string?
# a) "1.0"
# b) "2.0"
# c) "3.8"
# d) "4.0"
q6 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 7: Container Stats
# ============================================================
# To get a single snapshot of stats (not a stream), you use:
# a) container.stats()
# b) container.stats(stream=False)
# c) container.stats(once=True)
# d) container.get_stats()
q7 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 8: Docker Error Handling
# ============================================================
# What exception class should you catch for Docker-specific errors?
# a) DockerError
# b) DockerException
# c) ContainerException
# d) EngineError
q8 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 9: Image Size
# ============================================================
# Where is an image's size stored in the Python Docker SDK?
# a) image.size
# b) image.attrs["Size"]
# c) image.get_size()
# d) image.metadata["size"]
q9 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# QUESTION 10: Container Removal
# ============================================================
# To force-remove a running container without stopping first:
# a) container.remove()
# b) container.remove(force=True)
# c) container.kill_and_remove()
# d) container.delete(force=True)
q10 = ""  # YOUR ANSWER

# YOUR CODE HERE


# ============================================================
# MAIN - Display your answers
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  WEEK 9 QUIZ - Docker & Containers")
    print("=" * 50)

    answers = {
        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5,
        "Q6": q6, "Q7": q7, "Q8": q8, "Q9": q9, "Q10": q10,
    }

    for q, a in answers.items():
        status = "answered" if a else "UNANSWERED"
        print(f"  {q}: {a if a else '---':10s}  ({status})")

    answered = sum(1 for a in answers.values() if a)
    print(f"\n  Answered: {answered}/10")
