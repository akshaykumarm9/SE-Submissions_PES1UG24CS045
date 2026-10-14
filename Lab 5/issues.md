# Lab 5: Static Code Analysis — Issue Documentation

**Project:** Hotel Booking System  
**Tools:** Pylint, Bandit, Flake8

| Issue | Type | Original Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Unsafe use of `eval()` | Security | 42 | `eval()` can execute arbitrary Python expressions, potentially allowing code execution. | Replaced unrestricted evaluation with an allowlist of approved seasonal-rate calculations. |
| Weak MD5 hashing | Security | 47 | MD5 is not suitable for security-sensitive hashing. | Replaced MD5 with SHA-256 for the guest identifier digest. |
| Shell command execution | Security | 58 | Using `os.system()` with a constructed command can introduce command-injection risk. | Removed shell execution and used ordinary Python output instead. |
| Hardcoded secret key | Security | 62 | A secret embedded in source code may be exposed to anyone who can access the code. | Read the secret from the `HOTEL_SECRET_KEY` environment variable. |
| Mutable default argument | Code quality | Check original Pylint report | A default list can be shared between function calls, causing unexpected behavior. | Changed the default to `None` and initialized the list inside the function. |
| Missing docstrings | Code quality | Check original Pylint report | Functions without docstrings are harder to understand and maintain. | Added descriptive docstrings. |

## Verification

- Bandit: rerun after the changes and record the actual findings.
- Pylint: rerun after the changes and record the actual score.
- Flake8: rerun after the changes and record the actual violations.

## Reflection

Static code analysis helped identify potential security vulnerabilities, programming mistakes, and style violations without requiring the program to be executed for every check. Bandit focused on security, Pylint on code quality, and Flake8 on formatting and style. Fixing the findings improved code readability and reduced potential risks. Running the tools again helped verify whether the corrections addressed the reported issues.