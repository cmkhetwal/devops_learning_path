# Week 12, Day 6: Code Review Day

## What You'll Learn

- Code review best practices for DevOps Python code
- Clean code principles applied to automation scripts
- Common anti-patterns and how to fix them
- Refactoring techniques for production readiness

## Code Review Checklist

### 1. Code Structure
- [ ] Functions do ONE thing and do it well
- [ ] Functions are under 30 lines
- [ ] Classes have clear, single responsibilities
- [ ] Module organization makes sense

### 2. Naming Conventions
- [ ] Variables and functions use `snake_case`
- [ ] Classes use `PascalCase`
- [ ] Constants use `UPPER_SNAKE_CASE`
- [ ] Names are descriptive (not `x`, `tmp`, `data2`)
- [ ] Boolean variables start with `is_`, `has_`, `can_`

### 3. Error Handling
- [ ] Never use bare `except:` (catch specific exceptions)
- [ ] Errors provide useful messages
- [ ] Resources are properly cleaned up (use `with` for files)
- [ ] Functions validate their inputs

### 4. Documentation
- [ ] Every module has a docstring
- [ ] Public functions have docstrings
- [ ] Complex logic has inline comments explaining WHY
- [ ] Type hints on function signatures

### 5. DevOps-Specific
- [ ] No hardcoded credentials or secrets
- [ ] Configurable values use environment variables or config files
- [ ] Proper logging (not print statements)
- [ ] Timeouts on network operations
- [ ] Graceful degradation on failures
- [ ] Idempotent operations where possible

---

## Common Anti-Patterns

### Anti-Pattern 1: God Function
```python
# BAD: One function doing everything
def deploy(server, app, version):
    # 200 lines of mixed concerns...
```

### Anti-Pattern 2: Bare Exception
```python
# BAD
try:
    result = do_something()
except:
    pass
```

### Anti-Pattern 3: Hardcoded Secrets
```python
# BAD
password = "admin123"
api_key = "sk-12345"
```

### Anti-Pattern 4: No Validation
```python
# BAD
def create_server(name, ip, port):
    servers[name] = {"ip": ip, "port": port}  # No validation!
```

### Anti-Pattern 5: Print Instead of Log
```python
# BAD
print(f"Deploying {app} to {server}")

# GOOD
logger.info(f"Deploying {app} to {server}")
```

---

## Refactoring Principles

1. **DRY** (Don't Repeat Yourself) - Extract common logic
2. **KISS** (Keep It Simple) - Simple solutions over clever ones
3. **YAGNI** (You Ain't Gonna Need It) - Only build what's needed
4. **SRP** (Single Responsibility) - Each unit has one job
5. **Fail Fast** - Validate early, error clearly

## Clean Code for DevOps

DevOps code often becomes "throw-away scripts" that end up running
in production for years. Apply the same quality standards to
automation code as you would to application code:

- Write tests for your scripts
- Use version control
- Code review before deploying
- Document assumptions and requirements
- Plan for failure modes
