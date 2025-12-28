# Review Pull Request

Review a pull request for code quality, architecture compliance, and best practices.

## Usage
```
/review-pr [PR_NUMBER]
```

## Instructions

Review pull request $ARGUMENTS for:

1. **Code Quality**
   - Type hints present and accurate
   - Docstrings on public APIs
   - No code smells or anti-patterns

2. **Architecture Compliance**
   - Three-tier layer boundaries respected
   - Commands layer has no side effects
   - Operations layer is pure
   - Runtime layer handles all I/O

3. **Security**
   - No hardcoded secrets
   - No shell=True in subprocess
   - Proper input validation

4. **Testing**
   - Adequate test coverage
   - Edge cases handled
   - Tests follow naming conventions

5. **RDF-First Compliance**
   - Generated files not manually edited
   - RDF source and code in sync

Use `gh pr view $ARGUMENTS --json files,additions,deletions,body` to get PR details.
Use `gh pr diff $ARGUMENTS` to see the changes.

Provide a structured review with:
- Summary of changes
- Issues found (critical, major, minor)
- Recommendations
- Approval status (Approve / Request Changes / Comment)
