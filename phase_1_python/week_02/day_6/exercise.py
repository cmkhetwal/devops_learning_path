"""
Week 2, Day 6: Practice Day - Mini-Projects
=============================================
Complete all 5 mini-projects below.
Run 'python check.py' when you are done to see your score!
"""

# ===========================================================================
# PROJECT 1: Number Guessing Game (Simulated)
# ===========================================================================
# The secret number is 7. The player gets a list of guesses to try.
# Use a while loop to go through each guess.
# For each guess:
#   - If the guess is too low, print: "Guess X: Too low!"
#   - If the guess is too high, print: "Guess X: Too high!"
#   - If the guess is correct, print: "Guess X: Correct! You win!" and break
# X is the guess number starting at 1.
# After the loop (if they never guessed right), print:
#   "Game over! The number was 7"
# Use for/else or while with a flag to handle the "never guessed" case.
#
# Expected output:
#   Guess 1: Too low!
#   Guess 2: Too high!
#   Guess 3: Too low!
#   Guess 4: Correct! You win!

secret_number = 7
guesses = [3, 10, 5, 7, 2]

# YOUR CODE HERE


# ===========================================================================
# PROJECT 2: Server Health Monitor
# ===========================================================================
# You have a list of servers with their metrics.
# Loop through each server and classify its status:
#   - If cpu > 90 OR memory > 90: print "<name>: CRITICAL"
#   - If cpu > 70 OR memory > 70: print "<name>: WARNING"
#   - Otherwise: print "<name>: HEALTHY"
#
# After checking all servers, print a summary:
#   "Summary: X healthy, Y warning, Z critical"
#
# Expected output:
#   web-01: HEALTHY
#   web-02: WARNING
#   db-01: CRITICAL
#   cache-01: HEALTHY
#   api-01: WARNING
#   Summary: 2 healthy, 2 warning, 1 critical

server_metrics = [
    {"name": "web-01", "cpu": 45, "memory": 50},
    {"name": "web-02", "cpu": 75, "memory": 60},
    {"name": "db-01", "cpu": 92, "memory": 88},
    {"name": "cache-01", "cpu": 30, "memory": 25},
    {"name": "api-01", "cpu": 65, "memory": 78},
]

# YOUR CODE HERE


# ===========================================================================
# PROJECT 3: Simple Menu System
# ===========================================================================
# Simulate a menu system using a list of user choices.
# The menu options are:
#   1 = Show servers  -> print "Servers: web-01, web-02, db-01"
#   2 = Show status   -> print "Status: All systems operational"
#   3 = Exit          -> print "Goodbye!" and break
#   anything else     -> print "Invalid choice"
#
# Use a while loop with an index to go through the choices list.
# Process each choice as described above.
# After the loop (after break or all choices processed), print nothing extra.
#
# Expected output:
#   Status: All systems operational
#   Servers: web-01, web-02, db-01
#   Invalid choice
#   Goodbye!

menu_choices = [2, 1, 5, 3, 1]

# YOUR CODE HERE


# ===========================================================================
# PROJECT 4: Password Validator
# ===========================================================================
# Check if the password meets ALL of these requirements:
#   1. At least 8 characters long
#   2. Contains at least one uppercase letter (A-Z)
#   3. Contains at least one digit (0-9)
#   4. Contains at least one special character (from the set: !@#$%^&*)
#
# Loop through each character to check requirements 2, 3, and 4.
# Hint: use char.isupper(), char.isdigit(), and "char in '!@#$%^&*'"
#
# Print each check result:
#   "Length check: PASS" or "Length check: FAIL"
#   "Uppercase check: PASS" or "Uppercase check: FAIL"
#   "Digit check: PASS" or "Digit check: FAIL"
#   "Special char check: PASS" or "Special char check: FAIL"
#
# Then print the final verdict:
#   If ALL checks pass: "Password is STRONG"
#   If any check fails: "Password is WEAK"
#
# Expected output (with the given password):
#   Length check: PASS
#   Uppercase check: PASS
#   Digit check: PASS
#   Special char check: PASS
#   Password is STRONG

password = "DevOps2024!"

# YOUR CODE HERE


# ===========================================================================
# PROJECT 5: Port Scanner Simulator
# ===========================================================================
# Simulate scanning ports on multiple servers.
# For each server, check each port in the scan range.
# The dictionary open_ports tells you which ports are "open" on each server.
#
# Rules:
#   - For each server, loop through ports 80, 443, 3306, 5432, 8080
#   - If the port is in that server's open_ports list, print:
#       "<server>:<port> OPEN"
#   - If the port is NOT open, skip it (use continue, do NOT print anything)
#   - After checking all ports for a server, print:
#       "<server>: Scan complete"
#
# Expected output:
#   web-01:80 OPEN
#   web-01:443 OPEN
#   web-01: Scan complete
#   db-01:3306 OPEN
#   db-01:5432 OPEN
#   db-01: Scan complete
#   api-01:443 OPEN
#   api-01:8080 OPEN
#   api-01: Scan complete

servers_to_scan = ["web-01", "db-01", "api-01"]
scan_ports = [80, 443, 3306, 5432, 8080]
open_ports = {
    "web-01": [80, 443],
    "db-01": [3306, 5432],
    "api-01": [443, 8080],
}

# YOUR CODE HERE
