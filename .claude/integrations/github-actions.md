# GitHub Actions Integration

## Automated PR Review

### Workflow File
```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  review:
    if: |
      github.event_name == 'pull_request' ||
      contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: review
          custom_instructions: |
            Follow these project-specific rules:
            - Check three-tier architecture compliance
            - Verify RDF-first principles
            - Ensure no shell=True in subprocess
```

## Automated Security Scan

```yaml
# .github/workflows/claude-security.yml
name: Claude Security Scan

on:
  pull_request:
    paths:
      - '**/*.py'

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          command: /security-scan
```

## Interactive PR Commands

Mention `@claude` in PR comments:
- `@claude review` - Full code review
- `@claude fix` - Attempt to fix issues
- `@claude explain` - Explain the changes
- `@claude test` - Suggest tests

## Secrets Setup

1. Go to repository Settings
2. Secrets and variables → Actions
3. New repository secret:
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your API key from console.anthropic.com

## Best Practices

- Run Claude on PR open for immediate feedback
- Use `@claude` for interactive assistance
- Set up security scans for Python file changes
- Configure architecture validation for layer compliance
