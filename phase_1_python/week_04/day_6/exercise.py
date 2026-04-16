"""
Week 4, Day 6: Practice Day - 5 Mini-Projects
==============================================

Build 5 real DevOps tools using functions and modules!

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to test your solutions.
"""

import random
import string


# =====================================================================
# MINI-PROJECT 1: Password Generator
# =====================================================================

# TASK 1: generate_password(length=16, use_uppercase=True, use_digits=True, use_special=True)
# -------------------------------------------------------------------------------------------
# Generate a random password.
#
# Rules:
#   - Always include lowercase letters (a-z)
#   - If use_uppercase is True, also include A-Z
#   - If use_digits is True, also include 0-9
#   - If use_special is True, also include: !@#$%^&*
#   - Return a string of the specified length
#   - Use random.choice() to pick random characters
#
# Note: Do NOT set a random seed. The checker will set it before calling.
#
# Examples:
#   generate_password(8, use_special=False)  -> "kJm3nP2x" (varies)
#   len(generate_password(20)) -> 20

# YOUR CODE HERE


# TASK 2: check_password_strength(password)
# -----------------------------------------
# Analyze a password and return its strength as a string.
# Rules:
#   - "strong" if length >= 12 AND has uppercase AND has lowercase
#                AND has digits AND has special chars (!@#$%^&*)
#   - "medium" if length >= 8 AND has at least 3 of the 4 categories
#                (uppercase, lowercase, digits, special)
#   - "weak" otherwise
#
# Examples:
#   check_password_strength("Abc123!@#xyz")  -> "strong"
#   check_password_strength("Abc12345")      -> "medium"
#   check_password_strength("abc")           -> "weak"

# YOUR CODE HERE


# =====================================================================
# MINI-PROJECT 2: File Size Converter
# =====================================================================

# TASK 3: bytes_to_human(size_bytes)
# -----------------------------------
# Convert bytes to a human-readable string.
# Rules:
#   - If >= 1073741824 (1024^3), show as GB
#   - If >= 1048576 (1024^2), show as MB
#   - If >= 1024, show as KB
#   - Otherwise, show as bytes
#   - Format numbers to 2 decimal places for KB/MB/GB
#
# Examples:
#   bytes_to_human(500)          -> "500 bytes"
#   bytes_to_human(1536)         -> "1.50 KB"
#   bytes_to_human(2621440)      -> "2.50 MB"
#   bytes_to_human(5368709120)   -> "5.00 GB"

# YOUR CODE HERE


# TASK 4: human_to_bytes(size_string)
# ------------------------------------
# Convert a human-readable size string back to bytes (integer).
# Rules:
#   - Input will be like "1.50 KB", "2.50 MB", "5.00 GB", or "500 bytes"
#   - Return an integer (round to nearest whole number)
#   - Handle case-insensitively ("kb", "KB", "Kb" all work)
#
# Examples:
#   human_to_bytes("500 bytes")  -> 500
#   human_to_bytes("1.50 KB")    -> 1536
#   human_to_bytes("2.50 MB")    -> 2621440
#   human_to_bytes("5.00 GB")    -> 5368709120

# YOUR CODE HERE


# =====================================================================
# MINI-PROJECT 3: Server Health Check Library
# =====================================================================

# TASK 5: check_cpu(cpu_percent, threshold=90)
# ---------------------------------------------
# Return a dictionary with:
#   "metric": "cpu"
#   "value": cpu_percent
#   "ok": True if cpu_percent < threshold, False otherwise
#
# Examples:
#   check_cpu(85)      -> {"metric": "cpu", "value": 85, "ok": True}
#   check_cpu(95)      -> {"metric": "cpu", "value": 95, "ok": False}
#   check_cpu(85, 80)  -> {"metric": "cpu", "value": 85, "ok": False}

# YOUR CODE HERE


# TASK 6: check_memory(mem_percent, threshold=85)
# ------------------------------------------------
# Same pattern as check_cpu but for memory.
#   "metric": "memory"
#   "value": mem_percent
#   "ok": True if mem_percent < threshold, False otherwise

# YOUR CODE HERE


# TASK 7: check_disk(disk_percent, threshold=80)
# -----------------------------------------------
# Same pattern for disk usage.
#   "metric": "disk"
#   "value": disk_percent
#   "ok": True if disk_percent < threshold, False otherwise

# YOUR CODE HERE


# TASK 8: full_health_check(cpu, memory, disk)
# ---------------------------------------------
# Run all three checks and return a summary.
# Return a dictionary with:
#   "status": "healthy" if ALL checks pass, "unhealthy" if any fail
#   "checks": a list of the three check results
#   "failed": a list of metric names that failed (empty if all healthy)
#
# Examples:
#   full_health_check(50, 60, 40)
#   -> {
#       "status": "healthy",
#       "checks": [
#           {"metric": "cpu", "value": 50, "ok": True},
#           {"metric": "memory", "value": 60, "ok": True},
#           {"metric": "disk", "value": 40, "ok": True}
#       ],
#       "failed": []
#   }
#
#   full_health_check(95, 60, 85)
#   -> {
#       "status": "unhealthy",
#       "checks": [...],
#       "failed": ["cpu", "disk"]
#   }

# YOUR CODE HERE


# =====================================================================
# MINI-PROJECT 4: Simple Encryption/Decryption (Caesar Cipher)
# =====================================================================

# TASK 9: encrypt(text, shift=3)
# -------------------------------
# Encrypt text using a Caesar cipher.
# Rules:
#   - Shift each letter by 'shift' positions in the alphabet
#   - Wrap around: 'z' shifted by 1 becomes 'a'
#   - Preserve case: 'A' shifted by 1 becomes 'B'
#   - Leave non-letter characters unchanged (spaces, numbers, symbols)
#
# Examples:
#   encrypt("abc", 1)           -> "bcd"
#   encrypt("xyz", 3)           -> "abc"
#   encrypt("Hello World!", 5)  -> "Mjqqt Btwqi!"
#   encrypt("abc")              -> "def"  (default shift=3)

# YOUR CODE HERE


# TASK 10: decrypt(text, shift=3)
# --------------------------------
# Decrypt text that was encrypted with the same shift value.
# Hint: decrypting is just encrypting with a negative shift.
#
# Examples:
#   decrypt("def", 3)            -> "abc"
#   decrypt("Mjqqt Btwqi!", 5)   -> "Hello World!"
#   decrypt(encrypt("test", 7), 7)  -> "test"

# YOUR CODE HERE


# =====================================================================
# MINI-PROJECT 5: CLI Tool (combining everything)
# =====================================================================

# TASK 11: process_command(command, *args)
# ----------------------------------------
# A function that dispatches to different tools based on the command.
# Commands:
#   "password" -> return generate_password(). If args[0] exists, use it as length.
#   "filesize" -> return bytes_to_human(int(args[0]))
#   "health"   -> return full_health_check(int(args[0]), int(args[1]), int(args[2]))
#                  (args are cpu, memory, disk percentages)
#   "encrypt"  -> return encrypt(args[0]) (with default shift)
#   "decrypt"  -> return decrypt(args[0]) (with default shift)
#   anything else -> return "Unknown command: <command>"
#
# Examples:
#   process_command("filesize", "2621440")  -> "2.50 MB"
#   process_command("encrypt", "hello")     -> "khoor"
#   process_command("unknown")              -> "Unknown command: unknown"

# YOUR CODE HERE
