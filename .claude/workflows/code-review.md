# Code Review Workflow

## Overview
Comprehensive code review process for PRs and code changes.

## Review Checklist

### Architecture Compliance
- [ ] Commands layer has no side effects
- [ ] Operations layer is pure (no I/O)
- [ ] Runtime layer handles all I/O
- [ ] No circular dependencies between layers
- [ ] Correct layer for each change

### Code Quality
- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] No code smells or anti-patterns
- [ ] Appropriate error handling
- [ ] Clear variable and function names

### Security
- [ ] No `shell=True` in subprocess
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Path traversal prevention
- [ ] No command injection risks

### Testing
- [ ] Tests cover new functionality
- [ ] Edge cases handled
- [ ] Test names are descriptive
- [ ] Mocks used appropriately
- [ ] Coverage maintained or improved

### RDF-First Compliance
- [ ] Generated files not manually edited
- [ ] RDF source updated if behavior changes
- [ ] SPARQL/templates updated if needed
- [ ] `ggen sync` run if RDF changed

### Performance
- [ ] No obvious performance issues
- [ ] Appropriate data structures
- [ ] No unnecessary loops
- [ ] Resources properly cleaned up

## Review Process

### Step 1: Understand Context
```bash
# Get PR details
gh pr view [PR_NUMBER] --json title,body,files

# See the diff
gh pr diff [PR_NUMBER]
```

### Step 2: Architecture Review
- Check which layers are modified
- Verify layer boundaries respected
- Look for dependency issues

### Step 3: Code Review
- Read each file changed
- Check against quality checklist
- Note any concerns

### Step 4: Test Review
- Verify tests exist for changes
- Check test quality
- Run tests locally if needed

### Step 5: Provide Feedback

Format:
```markdown
## Summary
Brief overview of the changes.

## Issues Found

### Critical
- [file:line] Issue description

### Major
- [file:line] Issue description

### Minor
- [file:line] Issue description

## Suggestions
- Optional improvements

## Verdict
Approve / Request Changes / Comment
```
