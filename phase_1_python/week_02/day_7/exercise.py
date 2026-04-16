"""
Week 2, Day 7: Quiz Day - 10 Code Completion Questions
========================================================
Complete the missing code in each question.
Replace '# YOUR CODE HERE' with your solution.
Run 'python check.py' when you are done to see your score!
"""

# ===========================================================================
# QUESTION 1: Complete the if/elif/else
# ===========================================================================
# Given a status_code, print the correct message.
# 200 -> "OK", 404 -> "Not Found", 500 -> "Server Error", else -> "Unknown"

status_code = 500

# YOUR CODE HERE


# ===========================================================================
# QUESTION 2: Fix the while loop
# ===========================================================================
# This countdown should print 5, 4, 3, 2, 1 and then "Liftoff!"
# Fill in the missing parts.

countdown_num = 5

while countdown_num > 0:
    print(countdown_num)
    # YOUR CODE HERE (decrement countdown_num)

print("Liftoff!")


# ===========================================================================
# QUESTION 3: Complete the for loop
# ===========================================================================
# Loop through the list and print each service with "is running".
# Expected: "nginx is running", "postgres is running", "redis is running"

services = ["nginx", "postgres", "redis"]

# YOUR CODE HERE


# ===========================================================================
# QUESTION 4: Use logical operators
# ===========================================================================
# Print "ALERT" if cpu > 80 AND memory > 80.
# Print "OK" otherwise.
# Expected output with these values: "ALERT"

cpu = 95
memory = 88

# YOUR CODE HERE


# ===========================================================================
# QUESTION 5: Complete the range() call
# ===========================================================================
# Use range() to print even numbers from 2 to 10 (inclusive).
# Expected output: 2, 4, 6, 8, 10  (each on its own line)

# YOUR CODE HERE (use a for loop with range)


# ===========================================================================
# QUESTION 6: Use break correctly
# ===========================================================================
# Loop through the list of ports. When you find port 22, print
# "SSH port found" and stop the loop. Do NOT print anything for other ports.
# Expected output: "SSH port found"

ports = [80, 443, 22, 3306, 5432]

# YOUR CODE HERE


# ===========================================================================
# QUESTION 7: Use continue correctly
# ===========================================================================
# Loop through the numbers 1 to 10 (use range(1, 11)).
# Skip numbers divisible by 3 (use continue).
# Print all other numbers.
# Expected output: 1, 2, 4, 5, 7, 8, 10  (each on its own line)
# Hint: divisible by 3 means num % 3 == 0

# YOUR CODE HERE


# ===========================================================================
# QUESTION 8: Nested conditions
# ===========================================================================
# Given is_weekend and is_maintenance_window:
# If it is a weekend AND a maintenance window, print "Deploying update"
# If it is a weekend but NOT a maintenance window, print "Waiting for window"
# If it is NOT a weekend, print "No weekend deploys"
# Expected output: "Deploying update"

is_weekend = True
is_maintenance_window = True

# YOUR CODE HERE


# ===========================================================================
# QUESTION 9: Accumulator in a loop
# ===========================================================================
# Calculate the total response time for all servers.
# Loop through response_times and add each value to total_time.
# After the loop, print: "Total response time: X ms"
# Expected output: "Total response time: 1650 ms"

response_times = [200, 350, 150, 500, 450]
total_time = 0

# YOUR CODE HERE


# ===========================================================================
# QUESTION 10: Nested for loops
# ===========================================================================
# Print each combination of environment and server.
# Format: "<env>-<server>"
# Expected output:
#   dev-web
#   dev-db
#   prod-web
#   prod-db

envs = ["dev", "prod"]
server_types = ["web", "db"]

# YOUR CODE HERE
