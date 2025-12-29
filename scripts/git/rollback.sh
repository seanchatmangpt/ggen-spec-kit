#!/usr/bin/env bash
# ============================================================================
# rollback.sh - Rollback to previous release
# ============================================================================
# Usage:
#   ./rollback.sh [version] [options]
#
# Arguments:
#   version      Tag or commit to rollback to (default: previous release tag)
#
# Options:
#   --strategy STRATEGY  Rollback strategy: revert (default), reset
#   --dry-run            Preview rollback without executing
#   --push               Push rollback to remote (requires confirmation)
#   --no-confirm         Skip confirmation prompts (dangerous!)
#   -v, --verbose        Verbose output
#   -h, --help           Show this help message
#
# Strategies:
#   revert   Safe: Creates revert commits (preserves history)
#   reset    Destructive: Resets to previous state (rewrites history)
#
# Examples:
#   ./rollback.sh                           # Rollback to previous release
#   ./rollback.sh v1.2.2                    # Rollback to specific version
#   ./rollback.sh --strategy reset --push   # Force reset (dangerous!)
#   ./rollback.sh --dry-run                 # Preview rollback
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default options
STRATEGY="revert"
DRY_RUN=false
PUSH=false
CONFIRM=true
VERBOSE=false
ROLLBACK_TO=""

# Functions
print_error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_danger() {
    echo -e "${RED}🚨 DANGER: $1${NC}"
}

show_help() {
    sed -n '/^# ====/,/^# ====/p' "$0" | sed 's/^# //; s/^#//'
    exit 0
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --strategy)
            STRATEGY="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --no-confirm)
            CONFIRM=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        -*)
            print_error "Unknown option: $1"
            exit 1
            ;;
        *)
            ROLLBACK_TO="$1"
            shift
            ;;
    esac
done

# Validate strategy
case "$STRATEGY" in
    revert|reset)
        ;;
    *)
        print_error "Invalid strategy: $STRATEGY"
        echo "Valid strategies: revert, reset"
        exit 1
        ;;
esac

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_error "Working directory is not clean"
    echo ""
    git status
    echo ""
    print_warning "Commit or stash your changes before rolling back"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
print_info "Current version: $CURRENT_VERSION"

# Determine rollback target
if [ -z "$ROLLBACK_TO" ]; then
    # Get previous release tag
    ROLLBACK_TO=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
    if [ -z "$ROLLBACK_TO" ]; then
        print_error "No previous release tag found"
        echo "Please specify a version to rollback to"
        exit 1
    fi
    print_info "Auto-detected rollback target: $ROLLBACK_TO"
fi

# Verify rollback target exists
if ! git rev-parse --verify "$ROLLBACK_TO" >/dev/null 2>&1; then
    print_error "Rollback target not found: $ROLLBACK_TO"
    exit 1
fi

# Get commit range
ROLLBACK_TO_COMMIT=$(git rev-parse "$ROLLBACK_TO")
CURRENT_COMMIT=$(git rev-parse HEAD)

# Check if rollback target is an ancestor
if ! git merge-base --is-ancestor "$ROLLBACK_TO_COMMIT" "$CURRENT_COMMIT"; then
    print_error "Rollback target is not an ancestor of current HEAD"
    echo "This doesn't look like a rollback - refusing to proceed"
    exit 1
fi

# Count commits to revert
COMMITS_TO_REVERT=$(git rev-list --count "$ROLLBACK_TO_COMMIT".."$CURRENT_COMMIT")

# Print rollback summary
echo ""
print_warning "ROLLBACK SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Current:  $CURRENT_VERSION ($CURRENT_COMMIT)"
echo "  Target:   $ROLLBACK_TO ($ROLLBACK_TO_COMMIT)"
echo "  Commits:  $COMMITS_TO_REVERT to rollback"
echo "  Strategy: $STRATEGY"
echo "  Push:     $PUSH"
echo "  Dry run:  $DRY_RUN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show commits that will be rolled back
print_info "Commits to be rolled back:"
git log --oneline --graph "$ROLLBACK_TO_COMMIT".."$CURRENT_COMMIT"
echo ""

# Strategy-specific warnings
if [ "$STRATEGY" = "reset" ]; then
    print_danger "RESET strategy will rewrite git history!"
    echo "  - This is DESTRUCTIVE and cannot be undone easily"
    echo "  - Other developers will need to force-pull"
    echo "  - Only use if commits haven't been pushed"
    echo ""
fi

# Confirmation
if [ "$CONFIRM" = true ]; then
    if [ "$STRATEGY" = "reset" ]; then
        print_danger "Type 'RESET' to confirm destructive rollback:"
        read -r CONFIRMATION
        if [ "$CONFIRMATION" != "RESET" ]; then
            print_warning "Cancelled"
            exit 0
        fi
    else
        read -p "Proceed with rollback? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Cancelled"
            exit 0
        fi
    fi
fi

# Dry run mode
if [ "$DRY_RUN" = true ]; then
    print_info "DRY RUN MODE - No changes will be made"
    echo ""

    case "$STRATEGY" in
        revert)
            echo "Would execute:"
            echo "  git revert --no-edit $ROLLBACK_TO_COMMIT..$CURRENT_COMMIT"
            ;;
        reset)
            echo "Would execute:"
            echo "  git reset --hard $ROLLBACK_TO_COMMIT"
            ;;
    esac

    if [ "$PUSH" = true ]; then
        echo "  git push origin main"
    fi

    echo ""
    print_success "Dry run complete"
    exit 0
fi

# Create backup tag
BACKUP_TAG="rollback-backup-$(date +%s)"
print_info "Creating backup tag: $BACKUP_TAG"
git tag "$BACKUP_TAG" HEAD

# Execute rollback strategy
case "$STRATEGY" in
    revert)
        print_info "Creating revert commits..."
        # Revert commits in reverse order (most recent first)
        git revert --no-edit "$ROLLBACK_TO_COMMIT".."$CURRENT_COMMIT" || {
            print_error "Revert failed"
            echo ""
            print_info "To abort: git revert --abort"
            print_info "To restore: git reset --hard $BACKUP_TAG"
            exit 1
        }
        print_success "Revert commits created"
        ;;

    reset)
        print_warning "Resetting to $ROLLBACK_TO_COMMIT (destructive)..."
        git reset --hard "$ROLLBACK_TO_COMMIT"
        print_success "Reset complete"
        ;;
esac

# Run smoke tests
print_info "Running smoke tests..."
if command -v uv &> /dev/null; then
    if uv run pytest tests/unit/ -v --tb=short -x 2>&1 | tee /tmp/rollback-tests.log; then
        print_success "Smoke tests passed"
    else
        print_error "Smoke tests failed"
        echo ""
        print_warning "Rollback code has test failures"
        echo "Review test output in /tmp/rollback-tests.log"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Restoring from backup..."
            git reset --hard "$BACKUP_TAG"
            git tag -d "$BACKUP_TAG"
            print_warning "Rollback aborted"
            exit 1
        fi
    fi
else
    print_warning "uv not found, skipping smoke tests"
fi

# Calculate new version (increment patch for rollback release)
NEW_VERSION=$(echo "$ROLLBACK_TO" | sed 's/^v//' | awk -F. '{print $1"."$2"."$3+1}')
print_info "New rollback version: v$NEW_VERSION"

# Create rollback release tag
print_info "Creating rollback release tag..."
git tag -a "v$NEW_VERSION" -m "Rollback release to $ROLLBACK_TO

Rollback strategy: $STRATEGY
Original version: $CURRENT_VERSION
Commits rolled back: $COMMITS_TO_REVERT

This is an automated rollback release.
"
print_success "Created tag v$NEW_VERSION"

# Update CHANGELOG
if [ -f "CHANGELOG.md" ]; then
    print_info "Updating CHANGELOG.md..."
    CHANGELOG_ENTRY="## [$NEW_VERSION] - $(date +%Y-%m-%d)

### Rollback
- Rolled back to version $ROLLBACK_TO
- Strategy: $STRATEGY
- Reason: Production rollback
- Commits affected: $COMMITS_TO_REVERT

"
    # Insert after header
    sed -i "/^## \[/i $CHANGELOG_ENTRY" CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for rollback release v$NEW_VERSION"
    print_success "CHANGELOG.md updated"
fi

# Push to remote if requested
if [ "$PUSH" = true ]; then
    print_warning "Pushing rollback to remote..."

    if [ "$STRATEGY" = "reset" ]; then
        print_danger "This will FORCE PUSH and rewrite remote history!"
        read -p "Type 'FORCE' to confirm: " -r
        if [ "$REPLY" != "FORCE" ]; then
            print_warning "Push cancelled"
            exit 0
        fi
        git push --force origin main
        git push origin "v$NEW_VERSION"
    else
        git push origin main
        git push origin "v$NEW_VERSION"
    fi

    print_success "Pushed to remote"
fi

# Print summary
echo ""
print_success "ROLLBACK COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Rolled back:  $CURRENT_VERSION → $ROLLBACK_TO"
echo "  New release:  v$NEW_VERSION"
echo "  Backup tag:   $BACKUP_TAG"
echo "  Strategy:     $STRATEGY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_info "Next steps:"
echo "  1. Verify application works correctly"
echo "  2. Deprecate bad release on GitHub (gh release edit $CURRENT_VERSION)"
echo "  3. Notify stakeholders"
echo "  4. Schedule post-mortem"
echo "  5. Delete backup tag when confident: git tag -d $BACKUP_TAG"
echo ""

if [ "$VERBOSE" = true ]; then
    echo "Git log:"
    git log --oneline --graph -10
fi

exit 0
