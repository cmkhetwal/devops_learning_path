"""
Week 2, Day 3: While Loops - Exercise
======================================
Complete each task below. Replace '# YOUR CODE HERE' with your solution.
Run 'python check.py' when you are done to see your score!
"""

# ---------------------------------------------------------------------------
# TASK 1: Retry Connection
# ---------------------------------------------------------------------------
# Use a while loop to simulate retrying a connection.
# Start with attempt = 0 and max_retries = 5.
# Each iteration, increment attempt and print:
#   "Attempt X: Connecting..."
# where X is the current attempt number (1, 2, 3, 4, 5).
# After the loop, print:
#   "Finished: 5 attempts made"
#
# Expected output:
#   Attempt 1: Connecting...
#   Attempt 2: Connecting...
#   Attempt 3: Connecting...
#   Attempt 4: Connecting...
#   Attempt 5: Connecting...
#   Finished: 5 attempts made

attempt = 0
max_retries = 5

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 2: Countdown Timer
# ---------------------------------------------------------------------------
# Create a countdown from 10 to 1.
# Print each number on its own line.
# After the countdown, print "System shutdown complete"
#
# Expected output:
#   10
#   9
#   8
#   7
#   6
#   5
#   4
#   3
#   2
#   1
#   System shutdown complete

countdown = 10

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 3: Monitoring Loop with Break
# ---------------------------------------------------------------------------
# Simulate a monitoring loop that checks a server.
# Use "while True" and break out when check_number reaches 4.
# Start check_number at 0.
# Each loop iteration: increment check_number, then print:
#   "Check X: Server OK"
# When check_number reaches 4, print "Check 4: Server OK" then break.
# After the loop, print:
#   "Monitoring stopped after 4 checks"
#
# Expected output:
#   Check 1: Server OK
#   Check 2: Server OK
#   Check 3: Server OK
#   Check 4: Server OK
#   Monitoring stopped after 4 checks

check_number = 0

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 4: Sum Until Threshold
# ---------------------------------------------------------------------------
# You are tracking total data transferred in GB.
# Start with total = 0 and add 15 each iteration (simulating 15 GB transfers).
# Keep looping while total < 100.
# Each iteration, AFTER adding 15, print:
#   "Transferred so far: X GB"
# After the loop, print:
#   "Limit reached: X GB total"
#
# Expected output:
#   Transferred so far: 15 GB
#   Transferred so far: 30 GB
#   Transferred so far: 45 GB
#   Transferred so far: 60 GB
#   Transferred so far: 75 GB
#   Transferred so far: 90 GB
#   Transferred so far: 105 GB
#   Limit reached: 105 GB total

total = 0

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 5: Password Attempt Limiter
# ---------------------------------------------------------------------------
# Simulate a login system with limited attempts.
# The correct password is "devops123".
# You have a list of attempts to try (simulated input):
#   password_attempts = ["admin", "password", "devops123", "root"]
# Use a while loop with an index variable starting at 0.
# Each iteration, check if the current attempt matches the password.
#   If it does NOT match, print: "Attempt X: Incorrect password"
#   If it DOES match, print: "Attempt X: Access granted" and break
# X is the attempt number starting at 1.
#
# Expected output:
#   Attempt 1: Incorrect password
#   Attempt 2: Incorrect password
#   Attempt 3: Access granted

password_attempts = ["admin", "password", "devops123", "root"]
correct_password = "devops123"
index = 0

# YOUR CODE HERE
