# Verify AI-Generated Documentation

Quality assurance process for verifying documentation created or updated by AI agents.

## Overview

AI-generated documentation needs verification to ensure:
- **Accuracy** - Information matches implementation
- **Completeness** - All required sections present
- **Clarity** - Understandable to target audience
- **Consistency** - Matches project style
- **Linkage** - Properly cross-referenced

## Pre-Verification Checklist

Before reviewing AI-generated docs:

### Structure
- [ ] File in correct location (docs/guides/, docs/reference/, etc.)
- [ ] Follows Diataxis category (tutorial, guide, reference, explanation)
- [ ] Has proper markdown heading hierarchy
- [ ] Organized logically with clear sections

### Content
- [ ] Matches actual implementation (not aspirational)
- [ ] All code examples compile/work
- [ ] All command examples are valid
- [ ] All file paths are correct
- [ ] All links are valid (internal and external)

### Style
- [ ] Uses consistent terminology
- [ ] Matches project writing style
- [ ] Tone appropriate for target audience
- [ ] Professional and clear language

## Verification Categories

### Category 1: Technical Accuracy

**Verify code examples work:**

```bash
# Create test directory
mkdir -p /tmp/verify-docs

# 1. Extract code example
# Find: ```python...```code block
# Copy to test file

cat > /tmp/verify-docs/example.py << 'EOF'
[Paste code from docs]
EOF

# 2. Test it works
cd /tmp/verify-docs
python example.py

# Result: Should execute without errors
```

**Verify commands work:**

```bash
# If docs says: "Run: specify ggen sync"
specify ggen sync

# If docs says: "Run: specify init my-project"
specify init my-project

# Verify output matches docs
```

**Verify file paths:**

```bash
# If docs references: "ontology/cli-commands.ttl"
ls ontology/cli-commands.ttl

# Should exist without error
```

### Category 2: Completeness

**Check all required sections present:**

For **How-To Guides**, verify:
- [ ] Prerequisites (what's needed beforehand)
- [ ] Step-by-step instructions
- [ ] Expected output shown
- [ ] Troubleshooting (common issues)
- [ ] See Also (related docs)

For **References**, verify:
- [ ] All parameters documented
- [ ] All options explained
- [ ] Default values specified
- [ ] Examples for major features
- [ ] Error codes/exceptions listed

For **Explanations**, verify:
- [ ] Context and background
- [ ] Conceptual foundation
- [ ] Why (rationale) explained
- [ ] Alternatives discussed
- [ ] Tradeoffs mentioned

For **Tutorials**, verify:
- [ ] Learning objectives clear
- [ ] Prerequisites stated
- [ ] Hands-on, learner-focused
- [ ] Progressive complexity
- [ ] 10-25 minute duration

### Category 3: Clarity

**Read for understanding:**

- [ ] First paragraph explains purpose
- [ ] Jargon minimized or explained
- [ ] Examples clarify complex concepts
- [ ] Diagrams/visuals help understanding
- [ ] Summary or conclusion at end

**Test with target audience:**

```
If doc is for "beginners":
  ✓ Can someone new understand it?
  ✓ Are prerequisites clear?
  ✓ Would they feel capable after?

If doc is for "operators":
  ✓ Can experienced user apply it?
  ✓ Are edge cases covered?
  ✓ Are assumptions stated?

If doc is for "architects":
  ✓ Are design decisions justified?
  ✓ Are tradeoffs explained?
  ✓ Are alternatives considered?
```

### Category 4: Consistency

**Style consistency:**

```bash
# Check naming consistency
grep -r "ggen sync" docs/
grep -r "ggen_sync" docs/
# Should use one consistently

grep -r "Python" docs/
grep -r "python" docs/
# Should use capitalization consistently
```

**Format consistency:**

```bash
# Check code block style
grep -r "```python" docs/guides/
grep -r "```bash" docs/guides/
# All should use markdown backticks

# Check link style
grep -r "\\[Link\\](" docs/
grep -r "\\[Link\\](url)" docs/
# Should be consistent
```

**Terminology consistency:**

```
If docs says:
  - Sometimes: "RDF specification"
  - Sometimes: "RDF spec"
  - Sometimes: "specification"

Fix to use ONE term consistently throughout
```

### Category 5: Cross-References

**Verify all links work:**

```bash
# Extract all links from doc
grep -o '\[.*\](.*)'  docs/guides/new-doc.md | \
  sed 's/.*(\(.*\)).*/\1/' > /tmp/links.txt

# Check each link
while read link; do
  if [[ $link == http* ]]; then
    curl -I "$link" 2>/dev/null | head -1
  else
    # Internal link
    if [ -f "$(echo $link | cut -d'#' -f1)" ]; then
      echo "✓ $link"
    else
      echo "✗ BROKEN: $link"
    fi
  fi
done < /tmp/links.txt
```

**Verify documentation is indexed:**

```bash
# Check if new doc appears in README
grep "new-doc" docs/guides/README.md

# Check if in explanation index (if explanation)
grep "new-concept" docs/explanation/README.md

# Check if linked from main index
grep "new-doc" docs/index.md
```

## Verification Workflow

### Step 1: Automated Checks

```bash
# Run link validator
find docs/ -name "*.md" | while read f; do
  python scripts/validate-links.py "$f"
done

# Check markdown syntax
npx markdownlint docs/

# Check spell
aspell check docs/new-doc.md

# Check code blocks
python scripts/test-code-examples.py docs/new-doc.md
```

### Step 2: Manual Review

```
Review by:
  1. Subject Matter Expert (SME) - Is it technically accurate?
  2. Technical Writer - Is it clear and well-written?
  3. Target User - Is it useful and understandable?
  4. Architect - Does it fit the system?
```

### Step 3: Integration Check

```bash
# Build documentation
sphinx-build -b html docs/ _build/

# Check generated HTML
# - Links work?
# - Formatting correct?
# - Cross-references resolved?
# - Hierarchy clear?

# Check in actual doc viewer
open _build/index.html
```

### Step 4: Publish Check

```bash
# Before merging to main:
git diff --check                      # No whitespace issues
ruff check docs/                      # Code style
vale docs/new-doc.md                 # Writing style
```

## Common AI Mistakes to Check

### Mistake 1: Aspirational vs. Actual

**Problem:** Doc describes desired state, not actual implementation

```
❌ WRONG:
"When you run 'specify cache', it will automatically
clean up old files every day."

✓ RIGHT:
"The cache cleanup happens manually:
  specify cache clean --max-age 7d
Automatic cleanup is planned for v0.9."
```

**How to verify:**
- Run commands mentioned in docs
- Check if behavior matches description
- Look for "will be", "plans to", "soon"

### Mistake 2: Incorrect Code Examples

**Problem:** Examples have bugs or don't run

```python
❌ WRONG:
# Missing import
def my_function():
    logger.info("Starting")  # logger not defined

✓ RIGHT:
from specify_cli.core.telemetry import timed

@timed
def my_function():
    """Properly instrumented function"""
    pass
```

**How to verify:**
- Copy code block into a file
- Try to run it
- Check for import errors, syntax errors

### Mistake 3: Outdated Information

**Problem:** Docs reference old APIs or patterns

```
❌ WRONG (old pattern):
from specify_cli.telemetry import get_tracer
tracer = get_tracer()

✓ RIGHT (current pattern):
from specify_cli.core.telemetry import timed

@timed
def my_func():
    pass
```

**How to verify:**
- Check API reference against current code
- Look for deprecated patterns
- Verify examples match current code

### Mistake 4: Missing Context

**Problem:** Doc assumes knowledge reader doesn't have

```
❌ WRONG (for beginners):
"Run ggen sync with --incremental flag for faster builds."
(Doesn't explain what ggen sync does)

✓ RIGHT (for beginners):
"Run `ggen sync` to transform your RDF specifications
into code and documentation. Use `ggen sync --incremental`
for faster builds on subsequent runs."
```

**How to verify:**
- Read doc assuming you're target audience
- Do you have enough context?
- Are terms explained?
- Are prerequisites stated?

### Mistake 5: Broken Links

**Problem:** Links to non-existent files or wrong paths

```
❌ WRONG:
See: /docs/guides/advanced-ggen.md
(Path doesn't exist or wrong capitalization)

✓ RIGHT:
See: `../advanced-ggen.md`
(Relative path verified to exist)

✓ RIGHT (absolute):
See: `/docs/guides/ggen/advanced-features.md`
(Verified path exists)
```

**How to verify:**
- Check every link in generated doc
- Verify relative paths work from current location
- Verify absolute paths match actual file structure

## Verification Checklist Template

Use this for reviews:

```markdown
## Documentation Verification Checklist

### ✓ Content Accuracy
- [ ] Code examples compile and run
- [ ] Commands shown actually work
- [ ] File paths are correct
- [ ] API references match current implementation
- [ ] No aspirational/planned features

### ✓ Completeness
- [ ] All required sections present
- [ ] No obvious gaps or TODOs
- [ ] Examples cover main use cases
- [ ] Edge cases mentioned where relevant
- [ ] Troubleshooting section if applicable

### ✓ Clarity & Style
- [ ] First paragraph explains purpose
- [ ] Writing is clear and concise
- [ ] Consistent terminology used
- [ ] Tone appropriate for audience
- [ ] No grammar/spelling errors

### ✓ Organization
- [ ] Logical section order
- [ ] Proper heading hierarchy
- [ ] Clear subsections
- [ ] Good use of lists/formatting
- [ ] Not too long (can break into multiple docs?)

### ✓ Cross-References
- [ ] All links work (internal and external)
- [ ] See Also section links to relevant docs
- [ ] Properly indexed in README files
- [ ] Linked from main docs/index.md
- [ ] No orphaned documentation

### ✓ Target Audience
- [ ] Appropriate for intended audience
- [ ] Prerequisites are clear
- [ ] Jargon is explained or minimized
- [ ] Assumes right level of knowledge
- [ ] Would target user find this helpful?

### Overall Assessment
- [ ] APPROVED - Ready to merge
- [ ] NEEDS FIXES - Issues must be addressed
- [ ] INCOMPLETE - Waiting for more content
- [ ] DUPLICATE - Conflicts with existing doc

Comments:
[Specific feedback for author]
```

## Automation Tools

### Setup: Documentation Validation

```bash
# Create validation script
cat > scripts/validate-docs.py << 'EOF'
#!/usr/bin/env python3

import os, sys, re
from pathlib import Path

def validate_doc(filepath):
    with open(filepath) as f:
        content = f.read()

    issues = []

    # Check 1: Has heading
    if not content.startswith('#'):
        issues.append("Missing main heading")

    # Check 2: Has introduction
    if len(content.split('\n')) < 10:
        issues.append("Document too short")

    # Check 3: Check links
    links = re.findall(r'\[.*?\]\((.*?)\)', content)
    for link in links:
        if link.startswith('http'):
            continue
        if not (Path(filepath).parent / link).exists():
            issues.append(f"Broken link: {link}")

    return issues

for doc in sys.argv[1:]:
    issues = validate_doc(doc)
    if issues:
        print(f"✗ {doc}")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"✓ {doc}")
EOF

# Run validation
python scripts/validate-docs.py docs/**/*.md
```

## See Also

- `setup-ai-agents.md` - Configuring AI agents
- `token-optimization.md` - Context optimization
- `/docs/reference/definition-of-done.md` - Quality standards
- `/docs/guides/rdf/write-rdf-spec.md` - Specification quality
