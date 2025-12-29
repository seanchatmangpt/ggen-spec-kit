# Code Review Workflow

## Process

### 1. Understand Changes
**Agent/Skill**: Code Reviewer
**Tools**: Bash (gh pr), Read
**Steps**:
1. Review PR title and description
2. Check which files are modified
3. Read the diff: `gh pr diff [PR_NUMBER]`
4. Note scope of changes

**Success**: Clear understanding of what changed and why

---

### 2. Verify Architecture
**Agent/Skill**: Architecture Validator
**Tools**: Read, Grep
**Checklist**:
- [ ] Commands layer has no side effects/I/O
- [ ] Operations layer is pure (no I/O)
- [ ] Runtime layer handles all I/O
- [ ] No circular dependencies
- [ ] Correct layer for each change

**Success**: No layer violations, clear separation of concerns

---

### 3. Review Code Quality
**Agent/Skill**: Code Reviewer
**Tools**: Read
**Checklist**:
- [ ] All functions have type hints
- [ ] Public APIs have docstrings
- [ ] No code smells or antipatterns
- [ ] Error handling is appropriate
- [ ] Names are clear and descriptive

**Success**: Code follows quality standards

---

### 4. Check Security & Tests
**Agent/Skill**: Code Reviewer, Test Runner
**Tools**: Read, Bash (pytest)
**Security**:
- [ ] No `shell=True` in subprocess calls
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No command injection/path traversal risks

**Testing**:
- [ ] Tests cover new functionality
- [ ] Edge cases handled
- [ ] Coverage maintained or improved
- [ ] Run tests: `uv run pytest tests/ -v`

**Success**: Code is secure, tests pass, coverage acceptable

---

### 5. Verify RDF-First Compliance
**Agent/Skill**: ggen Operator
**Tools**: Grep, Bash
**Checklist**:
- [ ] Generated files not manually edited
- [ ] RDF source updated if behavior changed
- [ ] SPARQL/templates updated if needed
- [ ] `ggen sync` run if RDF modified

**Success**: No violations of constitutional equation

---

### 6. Provide Feedback

**Format**:
```markdown
## Summary
Brief description of changes.

## Status
- Architecture: ✓/✗
- Quality: ✓/✗
- Security: ✓/✗
- Tests: ✓/✗
- RDF Compliance: ✓/✗

## Issues Found
- [file:line] Issue description (Critical/Major/Minor)

## Suggestions
- Optional improvements

## Verdict
APPROVE | REQUEST CHANGES | COMMENT
```

**Success**: Clear, actionable feedback provided
