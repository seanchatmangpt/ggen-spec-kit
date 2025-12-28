#!/usr/bin/env bash
# ============================================================================
# create-branch.sh - Create feature/bugfix/release/hotfix branches
# ============================================================================
# Usage:
#   ./create-branch.sh <type> <name> [options]
#
# Arguments:
#   type     Branch type: feature, bugfix, release, hotfix
#   name     Branch name (kebab-case)
#
# Options:
#   --from BRANCH    Base branch to create from (default: main)
#   --push           Push branch to remote after creation (default: true)
#   --no-push        Don't push branch to remote
#   --checkout       Checkout branch after creation (default: true)
#   --no-checkout    Don't checkout branch after creation
#   -v, --verbose    Verbose output
#   -h, --help       Show this help message
#
# Examples:
#   ./create-branch.sh feature user-authentication
#   ./create-branch.sh bugfix login-error --from develop
#   ./create-branch.sh hotfix security-patch --from v1.2.3
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
FROM_BRANCH="main"
PUSH=true
CHECKOUT=true
VERBOSE=false

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

show_help() {
    sed -n '/^# ====/,/^# ====/p' "$0" | sed 's/^# //; s/^#//'
    exit 0
}

# Parse arguments
if [ $# -lt 2 ]; then
    print_error "Missing required arguments"
    echo ""
    show_help
fi

BRANCH_TYPE="$1"
BRANCH_NAME="$2"
shift 2

# Validate branch type
case "$BRANCH_TYPE" in
    feature|bugfix|release|hotfix)
        ;;
    *)
        print_error "Invalid branch type: $BRANCH_TYPE"
        echo "Valid types: feature, bugfix, release, hotfix"
        exit 1
        ;;
esac

# Parse options
while [ $# -gt 0 ]; do
    case "$1" in
        --from)
            FROM_BRANCH="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --no-push)
            PUSH=false
            shift
            ;;
        --checkout)
            CHECKOUT=true
            shift
            ;;
        --no-checkout)
            CHECKOUT=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate branch name (kebab-case)
if ! echo "$BRANCH_NAME" | grep -Pq '^[a-z0-9]+(-[a-z0-9]+)*$'; then
    print_error "Branch name must be kebab-case (lowercase, hyphens only)"
    echo "Example: user-authentication, fix-login-bug"
    exit 1
fi

# Get next branch number for feature/bugfix branches
get_next_number() {
    local prefix="$1"
    local max_num=0

    # Get all branches matching pattern (local and remote)
    for branch in $(git branch -a | grep -oP "${prefix}/\K\d+" | sort -n); do
        if [ "$branch" -gt "$max_num" ]; then
            max_num="$branch"
        fi
    done

    echo $((max_num + 1))
}

# Generate full branch name
case "$BRANCH_TYPE" in
    feature|bugfix)
        NEXT_NUM=$(get_next_number "$BRANCH_TYPE")
        FULL_BRANCH_NAME="${BRANCH_TYPE}/$(printf "%03d" "$NEXT_NUM")-${BRANCH_NAME}"
        ;;
    release)
        # Release branches: release/1.2.0
        if ! echo "$BRANCH_NAME" | grep -Pq '^\d+\.\d+\.\d+$'; then
            print_error "Release branch name must be a version (e.g., 1.2.0)"
            exit 1
        fi
        FULL_BRANCH_NAME="release/${BRANCH_NAME}"
        ;;
    hotfix)
        # Hotfix branches: hotfix/1.2.3-description
        # Extract version if present
        if echo "$BRANCH_NAME" | grep -Pq '^\d+\.\d+\.\d+-'; then
            FULL_BRANCH_NAME="hotfix/${BRANCH_NAME}"
        else
            # Auto-detect version from FROM_BRANCH or latest tag
            if echo "$FROM_BRANCH" | grep -Pq '^v?\d+\.\d+\.\d+$'; then
                VERSION=$(echo "$FROM_BRANCH" | sed 's/^v//')
            else
                VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "0.0.0")
            fi
            FULL_BRANCH_NAME="hotfix/${VERSION}-${BRANCH_NAME}"
        fi
        ;;
esac

# Check if branch already exists
if git rev-parse --verify "$FULL_BRANCH_NAME" >/dev/null 2>&1; then
    print_error "Branch $FULL_BRANCH_NAME already exists"
    exit 1
fi

# Check if remote branch exists
if git ls-remote --heads origin "$FULL_BRANCH_NAME" | grep -q "$FULL_BRANCH_NAME"; then
    print_error "Remote branch $FULL_BRANCH_NAME already exists"
    exit 1
fi

# Check if base branch exists
if ! git rev-parse --verify "$FROM_BRANCH" >/dev/null 2>&1; then
    # Try as remote branch
    if ! git rev-parse --verify "origin/$FROM_BRANCH" >/dev/null 2>&1; then
        print_error "Base branch $FROM_BRANCH does not exist"
        exit 1
    fi
    FROM_BRANCH="origin/$FROM_BRANCH"
fi

# Print summary
print_info "Creating branch:"
echo "  Type: $BRANCH_TYPE"
echo "  Name: $FULL_BRANCH_NAME"
echo "  From: $FROM_BRANCH"
echo "  Push: $PUSH"
echo "  Checkout: $CHECKOUT"
echo ""

# Confirm with user
read -p "Proceed? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Cancelled"
    exit 0
fi

# Fetch latest changes
print_info "Fetching latest changes..."
git fetch origin

# Create branch
print_info "Creating branch $FULL_BRANCH_NAME..."
git branch "$FULL_BRANCH_NAME" "$FROM_BRANCH"
print_success "Branch created: $FULL_BRANCH_NAME"

# Checkout branch if requested
if [ "$CHECKOUT" = true ]; then
    print_info "Checking out $FULL_BRANCH_NAME..."
    git checkout "$FULL_BRANCH_NAME"
    print_success "Checked out $FULL_BRANCH_NAME"
fi

# Push to remote if requested
if [ "$PUSH" = true ]; then
    print_info "Pushing to remote..."
    git push -u origin "$FULL_BRANCH_NAME"
    print_success "Pushed to origin/$FULL_BRANCH_NAME"
fi

# Print next steps
echo ""
print_success "Branch created successfully!"
echo ""
echo "Next steps:"
echo "  1. Make your changes and commit"
echo "  2. Push changes: git push"
echo "  3. Create PR: gh pr create --title \"$BRANCH_NAME\" --body \"Description\""
echo ""

# Verbose output
if [ "$VERBOSE" = true ]; then
    echo "Git status:"
    git status
fi

exit 0
