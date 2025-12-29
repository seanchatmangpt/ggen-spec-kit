# Git Operations and Production Workflows

Comprehensive git workflow automation for ggen-spec-kit following semantic versioning and GitFlow principles.

## Overview

This document describes the production git operations and release workflows designed for ggen-spec-kit. All operations follow the RDF-first architecture with specifications defined in Turtle format.

## RDF Specifications

### Ontology Files

- `/home/user/ggen-spec-kit/ontology/git-commands.ttl` - Git command specifications (source of truth)
- `/home/user/ggen-spec-kit/memory/production-lifecycle.ttl` - Production lifecycle specification

### Generated Artifacts

Following the constitutional equation `spec.md = μ(feature.ttl)`, the following will be generated via `ggen sync`:

- CLI commands in `src/specify_cli/commands/git_*.py`
- Tests in `tests/e2e/test_git_*.py`
- Documentation in `docs/git-workflows.md`

## Git Commands

### 1. Branch Management

**Command:** `specify git branch <type> <name> [options]`

Creates feature, bugfix, release, or hotfix branches with automatic numbering and naming conventions.

**Types:**
- `feature` - New feature development (feature/NNN-name)
- `bugfix` - Bug fixes (bugfix/NNN-name)
- `release` - Release preparation (release/1.2.0)
- `hotfix` - Emergency production fixes (hotfix/1.2.3-name)

**Options:**
- `--from BRANCH` - Base branch (default: main)
- `--push` - Push to remote (default: true)
- `--checkout` - Checkout after creation (default: true)

**Examples:**
```bash
# Create feature branch
specify git branch feature user-authentication

# Create hotfix from specific release
specify git branch hotfix security-patch --from v1.2.3

# Create release branch
specify git branch release 1.3.0
```

**Shell Script:** `/home/user/ggen-spec-kit/scripts/git/create-branch.sh`

### 2. Branch Cleanup

**Command:** `specify git branch-cleanup [options]`

Cleans up merged feature branches (local and remote).

**Options:**
- `--dry-run` - Preview deletions without executing
- `--remote` - Also clean remote branches
- `--exclude PATTERN` - Exclude branches matching regex
- `--force` - Force delete unmerged branches

**Examples:**
```bash
# Preview cleanup
specify git branch-cleanup --dry-run

# Clean local and remote
specify git branch-cleanup --remote

# Exclude certain branches
specify git branch-cleanup --exclude "release/*|hotfix/*"
```

### 3. Commit Validation

**Command:** `specify git commit-lint [ref] [options]`

Validates commit messages against conventional commit format.

**Format:** `<type>(<scope>): <subject>`

**Allowed types:** feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

**Options:**
- `--range RANGE` - Validate commit range (e.g., main..HEAD)
- `--strict` - Strict mode (require scope, body length > 20)
- `--types TYPES` - Custom allowed types (comma-separated)

**Examples:**
```bash
# Validate HEAD commit
specify git commit-lint

# Validate commit range
specify git commit-lint --range main..HEAD

# Strict validation
specify git commit-lint --strict
```

### 4. Commit Template

**Command:** `specify git commit-template [options]`

Generates conventional commit message template from staged changes.

**Features:**
- Analyzes git diff to suggest commit type
- Detects scope from changed files
- Provides structured template

**Options:**
- `--analyze` - Analyze diff for suggestions (default: true)
- `--scope SCOPE` - Override scope detection
- `--type TYPE` - Override type detection

**Examples:**
```bash
# Generate template with auto-detection
specify git commit-template

# Override type
specify git commit-template --type fix --scope auth
```

## Release Management

### 5. Release Creation

**Command:** `specify git release [version] [options]`

Creates semantic version release with changelog and tags.

**Version Formats:**
- `1.2.3` - Exact version
- `major` - Auto-increment major (breaking changes)
- `minor` - Auto-increment minor (new features)
- `patch` - Auto-increment patch (bug fixes)

**Options:**
- `--dry-run` - Preview release without creating
- `--changelog` - Generate changelog from commits (default: true)
- `--push` - Push tag to remote (default: true)
- `--sign` - GPG sign release tag
- `--pre-release TYPE` - Pre-release identifier (alpha, beta, rc.1)

**Examples:**
```bash
# Auto-detect version bump from commits
specify git release minor

# Create specific version
specify git release 1.2.3

# Pre-release
specify git release 1.3.0-beta.1 --pre-release beta
```

**Workflow:**
1. Validate pre-release gates (tests, linting, security)
2. Generate changelog from conventional commits
3. Update CHANGELOG.md and pyproject.toml
4. Create annotated git tag
5. Build artifacts (wheel, sdist)
6. Publish to PyPI
7. Create GitHub release
8. Run post-release verification

### 6. Changelog Generation

**Command:** `specify git changelog [options]`

Generates changelog from conventional commits.

**Options:**
- `--from TAG` - Start tag/commit (default: latest tag)
- `--to TAG` - End tag/commit (default: HEAD)
- `--output FILE` - Output file (default: CHANGELOG.md)
- `--format FORMAT` - Format: keepachangelog, github, conventional
- `--group-by GROUP` - Group by: type, scope, author

**Examples:**
```bash
# Generate changelog for unreleased commits
specify git changelog

# Specific range
specify git changelog --from v1.2.0 --to v1.3.0

# Group by scope
specify git changelog --group-by scope
```

**Changelog Format (Keep a Changelog):**
```markdown
## [1.2.3] - 2025-12-28

### Added
- New feature X from commit abc123

### Fixed
- Bug fix Y from commit def456

### Changed
- Update Z from commit ghi789
```

## Hotfix Procedures

### 7. Hotfix Creation

**Command:** `specify git hotfix <name> [options]`

Creates and deploys hotfix for critical production issues.

**Fast-track Process:**
1. Create hotfix branch from release tag
2. Implement minimal fix + test
3. Run focused validation (unit tests, security scan)
4. Auto-increment patch version
5. Merge to main and develop
6. Create emergency release

**Options:**
- `--version VERSION` - Hotfix version (auto-increments if not provided)
- `--from TAG` - Base branch/tag (default: main or latest release)
- `--finish` - Finish hotfix (merge, tag, release)
- `--delete-branch` - Delete hotfix branch after finishing (default: true)

**Examples:**
```bash
# Create hotfix branch
specify git hotfix auth-bypass --from v1.2.3

# Finish hotfix (merge and release)
specify git hotfix auth-bypass --finish
```

**Hotfix SLA:**
- Critical severity: < 4 hours
- High severity: < 24 hours
- Medium severity: < 1 week (use regular release)

**GitHub Actions Workflow:** `.github/workflows/hotfix.yml`

### 8. Cherry-Pick Workflow

**Command:** `specify git cherry-pick <commits> [options]`

Cherry-pick commits with automated conflict detection.

**Options:**
- `--to BRANCH` - Target branch (default: current)
- `--strategy STRATEGY` - Merge strategy: recursive, ours, theirs
- `--continue` - Continue after resolving conflicts
- `--abort` - Abort cherry-pick

**Examples:**
```bash
# Cherry-pick single commit
specify git cherry-pick abc123

# Cherry-pick range
specify git cherry-pick main~5..main~2

# Cherry-pick to different branch
specify git cherry-pick abc123 --to release/1.2.x
```

## Rollback Procedures

### 9. Release Rollback

**Command:** `specify git rollback [version] [options]`

Rollback to previous release (revert or reset).

**Strategies:**
- `revert` (Recommended) - Creates revert commits, preserves history
- `reset` (Destructive) - Resets to previous state, rewrites history

**Options:**
- `--strategy STRATEGY` - Rollback strategy (default: revert)
- `--dry-run` - Preview rollback without executing
- `--push` - Push rollback to remote (requires confirmation)
- `--no-confirm` - Skip confirmation prompts (dangerous!)

**Examples:**
```bash
# Rollback to previous release (safe)
specify git rollback

# Rollback to specific version
specify git rollback v1.2.2

# Preview rollback
specify git rollback --dry-run

# Destructive reset (use with caution)
specify git rollback --strategy reset --push
```

**Rollback Process:**
1. Verify rollback target exists
2. Create backup tag (rollback-backup-TIMESTAMP)
3. Apply rollback strategy (revert or reset)
4. Run smoke tests
5. Create new patch release (auto-increment)
6. Update CHANGELOG
7. Deprecate bad release on GitHub

**Shell Script:** `/home/user/ggen-spec-kit/scripts/git/rollback.sh`

## Pre/Post-Release Gates

### 10. Pre-Release Validation

**Command:** `specify git pre-release-check <version> [options]`

Runs comprehensive pre-release validation gates.

**Validation Checks:**
1. Git Status Clean
   - No uncommitted changes
   - No untracked files

2. Quality Gates
   - Ruff linting passes
   - MyPy type checking passes
   - Bandit security scan passes (no high/critical)

3. Test Coverage
   - All tests pass (100% pass rate)
   - Coverage ≥ 50%
   - No skipped tests

4. Changelog Updated
   - CHANGELOG.md contains version section
   - Changes categorized (Added, Changed, Fixed)

5. Documentation
   - README.md up-to-date
   - RDF docs generated (ggen sync)
   - No broken links

6. Version Consistency
   - pyproject.toml version matches
   - Version bumped per semver rules

**Options:**
- `--skip CHECKS` - Skip specific checks (tests,lint,security,changelog,docs)
- `--strict` - Strict mode (fail on warnings)
- `--output FILE` - Output report (JSON)

**Examples:**
```bash
# Full validation
specify git pre-release-check 1.2.3

# Skip changelog check
specify git pre-release-check 1.2.3 --skip changelog

# Generate JSON report
specify git pre-release-check 1.2.3 --output report.json
```

**GitHub Actions Workflow:** `.github/workflows/pre-release.yml`

**Manual Trigger:**
```bash
gh workflow run pre-release.yml -f version=1.2.3
```

### 11. Post-Release Verification

**Command:** `specify git post-release-verify <version> [options]`

Verifies release was deployed correctly.

**Verification Checks:**
1. Git Verification
   - Tag exists on remote
   - Tag matches local (SHA comparison)
   - Tag is annotated and signed (if requested)

2. GitHub Release
   - Release exists and published
   - All artifacts uploaded (wheel, sdist)
   - Checksums match

3. PyPI Verification
   - Package published
   - Version installable (`pip install specify-cli==VERSION`)
   - CLI executable (`specify --version`)

4. Documentation
   - Docs updated for new version
   - Changelog contains release notes

5. Smoke Tests
   - Install from PyPI in fresh venv
   - Run basic CLI commands
   - Verify version output

**Options:**
- `--remote REMOTE` - Remote to check (default: origin)
- `--artifacts` - Verify GitHub artifacts (default: true)
- `--registry REGISTRY` - Verify package registry (pypi, npm, docker)

**Examples:**
```bash
# Full verification
specify git post-release-verify 1.2.3

# Skip artifact check
specify git post-release-verify 1.2.3 --no-artifacts

# Verify Docker registry
specify git post-release-verify 1.2.3 --registry docker
```

## CI/CD Integration

### GitHub Actions Workflows

#### 1. Pre-Release Validation (`.github/workflows/pre-release.yml`)

**Trigger:** Manual (workflow_dispatch)

**Jobs:**
- Git status validation
- Quality gates (lint, type check, security)
- Test coverage
- Changelog validation
- Documentation validation
- Version consistency check
- Summary report

**Usage:**
```bash
gh workflow run pre-release.yml -f version=1.2.3 -f skip_checks=""
```

#### 2. Release Automation (`.github/workflows/release.yml`)

**Trigger:** Push tag matching `v*.*.*`

**Jobs:**
- Build artifacts (wheel, sdist)
- Run smoke tests
- Publish to PyPI
- Create GitHub release
- Upload artifacts
- Post-release verification

**Usage:**
```bash
# Tag triggers automatic release
git tag v1.2.3
git push origin v1.2.3
```

#### 3. Hotfix Pipeline (`.github/workflows/hotfix.yml`)

**Trigger:** Push to `hotfix/**` branches or manual

**Jobs:**
- Fast-track validation (unit tests, security)
- Build hotfix artifacts
- Create hotfix PR
- Auto-merge (requires manual approval)
- Backport to develop

**Usage:**
```bash
# Push hotfix branch triggers pipeline
git push origin hotfix/1.2.3-security-patch

# Or manual trigger
gh workflow run hotfix.yml -f hotfix_name=security-patch -f base_version=1.2.3
```

#### 4. Quality Gates (`.github/workflows/quality.yml`)

**Trigger:** Push to main, PRs

**Jobs:**
- Ruff linting
- MyPy type checking
- Bandit security scan
- Test suite with coverage
- Integration tests

## Semantic Versioning Strategy

### Version Format

`MAJOR.MINOR.PATCH[-PRE-RELEASE][+BUILD]`

**Components:**
- **MAJOR**: Breaking changes (incompatible API)
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)
- **PRE-RELEASE**: Optional (alpha, beta, rc.1)
- **BUILD**: Optional build metadata (+20130313144700)

### Increment Rules

| Commit Type | Version Bump |
|-------------|--------------|
| feat(scope)!: or BREAKING CHANGE | MAJOR + 1, MINOR = 0, PATCH = 0 |
| feat(scope): | MINOR + 1, PATCH = 0 |
| fix(scope): | PATCH + 1 |
| perf(scope): | PATCH + 1 |
| refactor(scope): | PATCH + 1 |

### Pre-Release Versions

- **Alpha**: 1.0.0-alpha.1 (internal testing, unstable)
- **Beta**: 1.0.0-beta.1 (external testing, feature-complete)
- **RC**: 1.0.0-rc.1 (release candidate, production-ready)

## Success Criteria

| Metric | Target | Description |
|--------|--------|-------------|
| Release Time | < 15 minutes | Full release process (pre-check → publish) |
| Release Success Rate | ≥ 95% | Releases succeed without rollback |
| Hotfix Time to Production | < 4 hours | Critical hotfixes deployed |
| Zero Downtime | 100% | No service interruption during releases |
| Rollback Success | < 10 minutes | Rollback to previous version |

## Shell Scripts

### 1. Create Branch Script

**Path:** `/home/user/ggen-spec-kit/scripts/git/create-branch.sh`

**Usage:**
```bash
./scripts/git/create-branch.sh <type> <name> [options]
```

**Features:**
- Auto-numbering for feature/bugfix branches
- Version validation for release/hotfix branches
- Automatic remote push
- Branch existence checks
- Interactive confirmation

**Examples:**
```bash
# Create feature branch
./scripts/git/create-branch.sh feature user-auth

# Create hotfix
./scripts/git/create-branch.sh hotfix security-patch --from v1.2.3

# No push, no checkout
./scripts/git/create-branch.sh bugfix login-error --no-push --no-checkout
```

### 2. Rollback Script

**Path:** `/home/user/ggen-spec-kit/scripts/git/rollback.sh`

**Usage:**
```bash
./scripts/git/rollback.sh [version] [options]
```

**Features:**
- Safe revert or destructive reset
- Automatic backup tag creation
- Smoke test execution
- CHANGELOG update
- Interactive confirmations
- Dry-run mode

**Examples:**
```bash
# Safe rollback to previous release
./scripts/git/rollback.sh

# Rollback to specific version
./scripts/git/rollback.sh v1.2.2

# Preview rollback
./scripts/git/rollback.sh --dry-run

# Destructive reset (requires double confirmation)
./scripts/git/rollback.sh --strategy reset --push
```

## Edge Cases

### 1. Release Fails During PyPI Publish

**Problem:** Tag pushed but PyPI publish fails

**Solution:**
- Rollback script deletes remote tag
- Retry publish
- Or create hotfix release

### 2. Hotfix on Diverged Main Branch

**Problem:** Main branch diverged significantly from release

**Solution:**
- Create hotfix from release tag (not main)
- Cherry-pick specific commits
- Avoid full merge

### 3. Multiple Concurrent Hotfixes

**Problem:** Different production versions need hotfixes

**Solution:**
- Support multiple hotfix branches (hotfix/1.2.x, hotfix/1.3.x)
- Parallel releases
- Independent backporting

### 4. Pre-Release Check Fails but Urgent Release Needed

**Problem:** Quality gate fails but business needs release

**Solution:**
- Allow override with `--force` flag
- Create incident report
- Schedule follow-up fix

### 5. GitHub API Rate Limit

**Problem:** Rate limit hit during release

**Solution:**
- Retry with exponential backoff
- Fallback to manual GitHub release
- Use GitHub App token (higher limits)

## Dependencies

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Git | ≥ 2.30.0 | Version control |
| GitHub CLI (gh) | ≥ 2.0.0 | GitHub API interaction |
| uv | ≥ 0.5.0 | Python package management |
| Python | ≥ 3.11 | Runtime environment |

### Installation

```bash
# macOS
brew install git gh uv

# Linux (Debian/Ubuntu)
apt-get install git gh
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
git --version
gh --version
uv --version
```

## Configuration

### GitHub Secrets

Required secrets in GitHub repository settings:

- `PYPI_TOKEN` - PyPI API token for publishing
- `GITHUB_TOKEN` - Auto-provided by GitHub Actions
- `GPG_PRIVATE_KEY` - Optional: GPG key for signing releases

### Git Configuration

```bash
# Configure git user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Optional: Configure GPG signing
git config commit.gpgsign true
git config user.signingkey YOUR_GPG_KEY_ID
```

### Pre-Commit Hooks

Pre-commit hooks automatically run on every commit:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install --hook-type commit-msg --hook-type pre-commit

# Run manually
pre-commit run --all-files
```

Configured in: `/home/user/ggen-spec-kit/.pre-commit-config.yaml`

## Implementation Status

### Completed

- ✅ RDF specifications (ontology/git-commands.ttl)
- ✅ Production lifecycle spec (memory/production-lifecycle.ttl)
- ✅ Pre-release workflow (.github/workflows/pre-release.yml)
- ✅ Hotfix workflow (.github/workflows/hotfix.yml)
- ✅ Branch creation script (scripts/git/create-branch.sh)
- ✅ Rollback script (scripts/git/rollback.sh)
- ✅ Markdown link checker config

### Pending Implementation

- ⏳ CLI commands (src/specify_cli/commands/git_*.py)
- ⏳ Operations layer (src/specify_cli/ops/git_*_ops.py)
- ⏳ Runtime layer (src/specify_cli/runtime/git_runtime.py)
- ⏳ E2E tests (tests/e2e/test_git_*.py)
- ⏳ Run ggen sync to generate from RDF

### Next Steps

1. Run `ggen sync` to generate Python code from RDF specifications
2. Implement runtime operations (git tag, push, commit parsing)
3. Write comprehensive tests
4. Update documentation with generated CLI help
5. Test full release workflow end-to-end

## Contributing

When adding new git operations:

1. **Define in RDF first** (ontology/git-commands.ttl)
2. Run `ggen sync` to generate CLI commands
3. Implement operations layer (pure logic, no side effects)
4. Implement runtime layer (git commands, I/O)
5. Write tests (unit + integration + e2e)
6. Update this documentation

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitFlow Workflow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Generated from RDF specifications following the constitutional equation:**
```
spec.md = μ(feature.ttl)
```

**Source files:**
- `/home/user/ggen-spec-kit/ontology/git-commands.ttl`
- `/home/user/ggen-spec-kit/memory/production-lifecycle.ttl`
