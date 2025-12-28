# Code Review Prompt Template

## Variables
- `{{files}}` - List of files to review
- `{{focus}}` - Specific focus areas (optional)
- `{{context}}` - Additional context (optional)

## Template

Review the following code changes for quality, security, and architecture compliance:

### Files to Review
{{files}}

### Focus Areas
{{focus}}

### Additional Context
{{context}}

## Review Criteria

### Architecture (Three-Tier)
1. Commands layer: Only CLI parsing and Rich formatting
2. Operations layer: Pure business logic, no side effects
3. Runtime layer: All subprocess, file I/O, HTTP calls
4. No imports crossing layer boundaries incorrectly

### Code Quality
1. Type hints on all functions
2. Docstrings on public APIs (NumPy style)
3. No code smells or anti-patterns
4. Clear, descriptive naming

### Security
1. No `shell=True` in subprocess calls
2. No hardcoded secrets
3. Proper input validation
4. Safe path handling

### RDF-First Compliance
1. Generated files not manually edited
2. RDF source updated when needed
3. ggen sync run after RDF changes

## Output Format

```markdown
## Review Summary
[Brief overview]

## Critical Issues
- [file:line] Description

## Major Issues
- [file:line] Description

## Minor Issues
- [file:line] Description

## Recommendations
- [Suggestions for improvement]

## Verdict
[Approve | Request Changes | Comment]
```
