# 25. Canonicalization

★★

*Different systems, different conventions. Canonicalization (μ₄) normalizes output format—line endings, whitespace, encoding—ensuring consistent artifacts regardless of where transformation runs. This stage eliminates platform-induced variation.*

---

## The Consistency Gate

After **[Template Emission](./template-emission.md)**, you have rendered output. But this output may harbor invisible inconsistencies:

- A Windows developer's template produces CRLF line endings
- A Mac developer's output has LF line endings
- Templates leave trailing whitespace on some lines
- Some files end with a newline; others don't
- Unicode characters might be in different normalization forms

These inconsistencies seem trivial until they're not:

```bash
$ git diff
diff --git a/src/commands/validate.py b/src/commands/validate.py
@@ -1,10 +1,10 @@
-"""Validate RDF files."""^M
-^M
-import typer^M
+"""Validate RDF files."""
+
+import typer
```

Every line appears changed because of invisible line ending differences. Git blame becomes useless. Code reviews drown in noise.

Canonicalization normalizes these variations, producing consistent output regardless of platform, template quirks, or developer environment. Same input specification, same output bytes—always.

---

## The Normalization Problem

**The fundamental challenge: Template output varies in formatting details that are invisible to humans but visible to machines. These variations break idempotence and create noisy diffs that obscure meaningful changes.**

Let us examine the sources of variation:

### Line Ending Chaos

Operating systems disagree on line endings:

| System | Line Ending | Bytes | Name |
|--------|-------------|-------|------|
| Unix/Linux | LF | `0x0A` | Line Feed |
| Windows | CRLF | `0x0D 0x0A` | Carriage Return + Line Feed |
| Classic Mac | CR | `0x0D` | Carriage Return |

When developers on different platforms collaborate:

```
Developer A (Linux):  def validate():\n
Developer B (Windows): def validate():\r\n
```

Even if the template is identical, output differs based on where it runs.

### Trailing Whitespace

Templates often produce trailing whitespace:

```jinja
{% for arg in arguments %}
    {{ arg.name }}    {# <- Four trailing spaces here #}
{% endfor %}
```

Some lines have trailing spaces; others don't. This variation:
- Triggers linter warnings
- Creates spurious diffs
- Violates code style guidelines

### Missing Final Newlines

Files might or might not end with a newline:

```
# File A: ends with newline
content here
<newline>

# File B: no final newline
content here<EOF>
```

POSIX mandates files end with newlines. Git shows warnings. Diffs appear different.

### Unicode Normalization

The same character can be represented different ways:

```
é = U+00E9 (single codepoint)
é = U+0065 + U+0301 (e + combining acute accent)
```

Both look identical but compare differently. Hash values differ.

### Indentation Inconsistency

Templates might mix tabs and spaces:

```python
def validate():
    if True:  # 4 spaces
	    pass  # 1 tab (invisible difference!)
```

---

## The Forces

Several tensions shape canonicalization design:

### Force: Consistency vs. Compatibility

*Consistent output is good. But some tools require specific formats.*

Makefiles require tabs for recipe indentation. Some legacy systems require CRLF. XML might need specific Unicode forms.

```
    Consistency
         │
   Single│ Multiple
   format│ formats
         │
         ├────────────────────────────►
         │                    Compatibility
         │
   Default rules    Format-specific overrides
```

**Resolution:** Establish defaults, allow format-specific overrides.

### Force: Normalization vs. Preservation

*Normalize formatting. But preserve intentional formatting.*

Markdown uses trailing spaces for line breaks. Python indentation is semantic. Some files have intentional whitespace.

**Resolution:** Format-aware canonicalization. Understand what whitespace means in each format.

### Force: Speed vs. Thoroughness

*Complete normalization takes time. Fast normalization might miss edge cases.*

For a small file, normalization is instant. For a large codebase with thousands of generated files, cumulative time matters.

**Resolution:** Optimize common cases. Profile and tune for project size.

### Force: Built-in vs. External Tools

*Build canonicalization into the pipeline. Or delegate to external formatters.*

ggen could normalize everything. Or it could call `black` for Python, `prettier` for JavaScript, `gofmt` for Go.

**Resolution:** Use built-in normalization for basics (line endings, final newlines), defer to external formatters for language-specific styling.

---

## Therefore

**Implement canonicalization (μ₄) as a post-emission stage that normalizes formatting to a canonical form, eliminating platform and template variations while respecting format-specific requirements.**

The canonicalization pipeline:

```
┌────────────────────────────────────────────────────────────────────┐
│  μ₄ CANONICALIZE                                                    │
│                                                                     │
│  1. ANALYZE output format                                           │
│     ├── Determine file type from extension                         │
│     ├── Load format-specific rules                                 │
│     └── Merge with default rules                                   │
│                                                                     │
│  2. NORMALIZE line endings                                          │
│     ├── Detect current line endings                                │
│     ├── Convert to target format (LF by default)                   │
│     └── Handle mixed line endings                                  │
│                                                                     │
│  3. CLEAN whitespace                                                │
│     ├── Remove trailing whitespace (unless preserved)              │
│     ├── Normalize indentation (tabs vs spaces)                     │
│     └── Remove trailing blank lines                                │
│                                                                     │
│  4. ENSURE final newline                                            │
│     ├── Add final newline if missing                               │
│     └── Remove multiple trailing newlines                          │
│                                                                     │
│  5. NORMALIZE Unicode                                               │
│     └── Convert to NFC form                                        │
│                                                                     │
│  6. APPLY format-specific rules                                     │
│     ├── Run external formatters if configured                      │
│     └── Apply format-specific adjustments                          │
│                                                                     │
│  Input: raw_artifact (from μ₃)                                     │
│  Output: canonical_artifact (to μ₅ and output)                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Canonicalization Rules

### Line Ending Normalization

```python
def normalize_line_endings(content: str, target: str = "lf") -> str:
    """
    Normalize line endings to target format.

    Args:
        content: Raw file content
        target: Target line ending (lf | crlf | native)

    Returns:
        Content with normalized line endings
    """
    # First, convert all line endings to LF
    content = content.replace('\r\n', '\n')  # CRLF -> LF
    content = content.replace('\r', '\n')    # CR -> LF

    # Then convert to target format if needed
    if target == "crlf":
        content = content.replace('\n', '\r\n')
    elif target == "native":
        import os
        content = content.replace('\n', os.linesep)
    # else: keep as LF

    return content
```

### Trailing Whitespace Removal

```python
def remove_trailing_whitespace(
    content: str,
    preserve_intentional: bool = False
) -> str:
    """
    Remove trailing whitespace from each line.

    Args:
        content: File content
        preserve_intentional: Keep trailing spaces that might be intentional
                             (e.g., Markdown line breaks)

    Returns:
        Content with trailing whitespace removed
    """
    lines = content.split('\n')

    if preserve_intentional:
        # Preserve exactly two trailing spaces (Markdown line break)
        cleaned = []
        for line in lines:
            stripped = line.rstrip()
            if line.endswith('  '):  # Intentional line break
                cleaned.append(stripped + '  ')
            else:
                cleaned.append(stripped)
    else:
        cleaned = [line.rstrip() for line in lines]

    return '\n'.join(cleaned)
```

### Final Newline Handling

```python
def ensure_final_newline(content: str) -> str:
    """
    Ensure file ends with exactly one newline.

    Args:
        content: File content

    Returns:
        Content ending with single newline
    """
    # Remove any trailing newlines
    content = content.rstrip('\n')

    # Add exactly one
    return content + '\n'
```

### Unicode Normalization

```python
import unicodedata

def normalize_unicode(content: str, form: str = "NFC") -> str:
    """
    Normalize Unicode to specified form.

    Args:
        content: File content
        form: Normalization form (NFC | NFD | NFKC | NFKD)

    Returns:
        Unicode-normalized content

    Forms:
        NFC  - Canonical composition (most compatible)
        NFD  - Canonical decomposition
        NFKC - Compatibility composition
        NFKD - Compatibility decomposition
    """
    return unicodedata.normalize(form, content)
```

### Complete Canonicalization

```python
def canonicalize(
    content: str,
    config: CanonicalizationConfig
) -> str:
    """
    Apply full canonicalization pipeline.

    Args:
        content: Raw file content
        config: Canonicalization configuration

    Returns:
        Canonicalized content
    """
    # 1. Normalize Unicode first (affects string operations)
    if config.unicode_normalization:
        content = normalize_unicode(content, config.unicode_form)

    # 2. Normalize line endings
    content = normalize_line_endings(content, config.line_ending)

    # 3. Handle trailing whitespace
    if config.trailing_whitespace == "remove":
        content = remove_trailing_whitespace(
            content,
            preserve_intentional=config.preserve_md_linebreaks
        )

    # 4. Handle indentation
    if config.indentation == "spaces":
        content = tabs_to_spaces(content, config.tab_width)
    elif config.indentation == "tabs":
        content = spaces_to_tabs(content, config.tab_width)

    # 5. Ensure final newline
    if config.final_newline == "ensure":
        content = ensure_final_newline(content)
    elif config.final_newline == "remove":
        content = content.rstrip('\n')

    # 6. Remove trailing blank lines
    if config.trailing_blank_lines == "remove":
        lines = content.split('\n')
        while lines and lines[-1].strip() == '':
            lines.pop()
        content = '\n'.join(lines) + '\n'

    return content
```

---

## Format-Specific Rules

Different file formats need different treatment:

### Python Files

```toml
[canonicalization.overrides."*.py"]
line_ending = "lf"
trailing_whitespace = "remove"
indentation = "spaces"
tab_width = 4
final_newline = "ensure"

# Optional: run black for full formatting
external_formatter = "black -q {file}"
```

### Markdown Files

```toml
[canonicalization.overrides."*.md"]
line_ending = "lf"
trailing_whitespace = "preserve"  # Trailing spaces mean line breaks!
final_newline = "ensure"
```

### Makefiles

```toml
[canonicalization.overrides."Makefile"]
[canonicalization.overrides."*.mk"]
line_ending = "lf"
indentation = "tabs"  # Makefiles REQUIRE tabs
tab_width = 8
```

### YAML Files

```toml
[canonicalization.overrides."*.yaml"]
[canonicalization.overrides."*.yml"]
line_ending = "lf"
indentation = "spaces"
tab_width = 2  # YAML convention
trailing_whitespace = "remove"
```

### JSON Files

```toml
[canonicalization.overrides."*.json"]
line_ending = "lf"
indentation = "spaces"
tab_width = 2
trailing_whitespace = "remove"

# Ensure consistent key ordering
external_formatter = "jq --sort-keys . {file}"
```

---

## External Formatters

For language-specific formatting, delegate to specialized tools:

### Formatter Configuration

```toml
[canonicalization.external]

[canonicalization.external.python]
command = "black -q {file}"
check_command = "black --check {file}"
on_failure = "warn"  # warn | error | ignore

[canonicalization.external.javascript]
command = "prettier --write {file}"
check_command = "prettier --check {file}"
on_failure = "error"

[canonicalization.external.go]
command = "gofmt -w {file}"
check_command = "gofmt -l {file}"
on_failure = "error"

[canonicalization.external.rust]
command = "rustfmt {file}"
check_command = "rustfmt --check {file}"
on_failure = "error"
```

### Formatter Integration

```python
def apply_external_formatter(
    file_path: Path,
    formatter_config: FormatterConfig
) -> tuple[bool, str]:
    """
    Apply external formatter to file.

    Args:
        file_path: Path to file
        formatter_config: Formatter configuration

    Returns:
        Tuple of (success, message)
    """
    import subprocess

    command = formatter_config.command.format(file=file_path)

    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, "Formatted successfully"
        else:
            message = f"Formatter failed: {result.stderr}"
            if formatter_config.on_failure == "error":
                raise FormatterError(message)
            elif formatter_config.on_failure == "warn":
                logger.warning(message)
            return False, message

    except subprocess.TimeoutExpired:
        message = f"Formatter timed out: {command}"
        if formatter_config.on_failure == "error":
            raise FormatterError(message)
        return False, message
```

---

## Configuration

### Full Configuration

```toml
# ggen.toml

[canonicalization]
# Default rules for all files
line_ending = "lf"                    # lf | crlf | native
trailing_whitespace = "remove"        # remove | preserve
final_newline = "ensure"              # ensure | remove | preserve
trailing_blank_lines = "remove"       # remove | preserve
unicode_normalization = "nfc"         # nfc | nfd | nfkc | nfkd | none
indentation = "preserve"              # spaces | tabs | preserve
tab_width = 4

# Format-specific overrides
[canonicalization.overrides."*.py"]
external_formatter = "black -q {file}"

[canonicalization.overrides."*.md"]
trailing_whitespace = "preserve"

[canonicalization.overrides."Makefile"]
indentation = "tabs"

[canonicalization.overrides."*.yaml"]
tab_width = 2

# External formatter settings
[canonicalization.formatters]
timeout = 30  # seconds
parallel = true
max_workers = 4
```

### Per-Target Configuration

```toml
[[targets]]
name = "python-commands"
template = "templates/command.py.tera"
output = "src/commands/{{ name }}.py"

[targets.canonicalization]
external_formatter = "black -q {file}"

[[targets]]
name = "command-docs"
template = "templates/command.md.tera"
output = "docs/commands/{{ name }}.md"

[targets.canonicalization]
trailing_whitespace = "preserve"
```

---

## Case Study: The Diff Noise Elimination

*A team eliminates spurious diffs through systematic canonicalization.*

### The Situation

The WebOps team was frustrated. Every pull request showed hundreds of changed lines, but most were meaningless:

```bash
$ git diff --stat
 src/commands/validate.py      | 50 +++++++++++++++++++-------------------
 src/commands/check.py         | 42 ++++++++++++++++++-----------------
 docs/commands/validate.md     | 38 ++++++++++++++++--------------
 ...
 45 files changed, 892 insertions(+), 892 deletions(-)
```

The actual logic changes? Maybe 10 lines. The rest was invisible formatting differences.

### The Investigation

They analyzed the spurious diffs:

1. **Line endings:** Windows developers contributed CRLF, Unix developers contributed LF
2. **Trailing whitespace:** Templates left trailing spaces randomly
3. **Final newlines:** Some files ended with newlines, some didn't
4. **Formatter disagreement:** Python files weren't consistently black-formatted

### The Solution

**Step 1: Establish Canonical Rules**

```toml
# ggen.toml
[canonicalization]
line_ending = "lf"
trailing_whitespace = "remove"
final_newline = "ensure"

[canonicalization.overrides."*.py"]
external_formatter = "black -q {file}"

[canonicalization.overrides."*.md"]
trailing_whitespace = "preserve"
```

**Step 2: Canonicalize Existing Files**

```bash
# One-time cleanup
find . -name "*.py" -exec black {} \;
find . -name "*" -exec dos2unix {} \;
git add -A && git commit -m "chore: canonicalize all files"
```

**Step 3: Add CI Verification**

```yaml
# .github/workflows/canonical.yml
- name: Verify canonical formatting
  run: |
    ggen sync
    git diff --exit-code || {
      echo "Files are not canonically formatted!"
      echo "Run 'ggen sync' locally and commit the changes."
      exit 1
    }
```

**Step 4: Pre-Commit Hook**

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: canonicalize
      name: Canonicalize generated files
      entry: ggen sync --canonicalize-only
      language: system
      pass_filenames: false
```

### The Results

After canonicalization was enforced:

```bash
$ git diff --stat
 src/commands/validate.py | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)
```

Now diffs show only meaningful changes:
- **99% reduction in diff noise**
- **Clear code reviews** focused on logic
- **Useful git blame** showing real authorship
- **Consistent files** across all environments

---

## Anti-Patterns

### Anti-Pattern: Over-Canonicalization

*"Normalize everything to our preferred format."*

Aggressive canonicalization breaks files that need specific formatting:
- Makefiles with tabs replaced by spaces (broken!)
- Markdown with trailing spaces removed (broken line breaks!)
- Shell scripts with Windows line endings (broken shebang!)

**Resolution:** Format-aware canonicalization with overrides.

### Anti-Pattern: Canonicalize Then Format

*"We'll canonicalize, then run the external formatter."*

This creates two passes that might conflict:

```bash
# Canonicalization converts tabs to spaces
# Black converts spaces back (its preference)
# Result: inconsistent
```

**Resolution:** Use external formatter as the canonicalizer for that format, or ensure they agree.

### Anti-Pattern: Missing Verification

*"We canonicalize during generation. That's enough."*

Without CI verification, developers can still commit non-canonical files:
- Direct edits to generated files
- Manual file creation
- Merge conflicts resolved incorrectly

**Resolution:** CI verification that regeneration produces no diff.

### Anti-Pattern: Platform-Specific Output

*"We'll use native line endings—each platform gets what it expects."*

This breaks cross-platform collaboration:
- Git shows diffs between platforms
- Tests behave differently
- Hashes differ

**Resolution:** Consistent output (LF) with .gitattributes for platform-specific needs.

---

## Implementation Checklist

### Core Canonicalization

- [ ] Implement line ending normalization
- [ ] Implement trailing whitespace removal
- [ ] Implement final newline handling
- [ ] Implement Unicode normalization
- [ ] Implement indentation normalization

### Format-Specific Rules

- [ ] Configure Python rules
- [ ] Configure Markdown rules (preserve trailing spaces)
- [ ] Configure Makefile rules (preserve tabs)
- [ ] Configure YAML rules
- [ ] Configure any project-specific formats

### External Formatters

- [ ] Configure black for Python
- [ ] Configure prettier for JavaScript (if applicable)
- [ ] Configure other language formatters
- [ ] Set timeout and error handling policies

### Verification

- [ ] Add CI step to verify canonical output
- [ ] Add pre-commit hook for local verification
- [ ] Document canonical requirements for team

### Migration

- [ ] Canonicalize existing generated files
- [ ] Commit canonicalization as a separate PR
- [ ] Update documentation

---

## Exercises

### Exercise 1: Line Ending Detective

Investigate line endings in a project:

1. Create files with different line endings (LF, CRLF, mixed)
2. Write a script to detect line endings in each file
3. Report statistics on the project
4. Normalize all to LF
5. Verify with git diff

### Exercise 2: Format-Aware Canonicalization

Handle format-specific requirements:

1. Create a Makefile with intentional tabs
2. Create a Markdown file with intentional trailing spaces
3. Write canonicalization that preserves both
4. Verify both files still work correctly

### Exercise 3: External Formatter Integration

Integrate an external formatter:

1. Configure black for Python files
2. Configure prettier for JavaScript files
3. Run both through canonicalization pipeline
4. Handle formatter failures gracefully
5. Verify output is consistent

### Exercise 4: CI Verification

Set up CI canonicalization verification:

1. Create GitHub Actions workflow
2. Regenerate all files
3. Check for any diff
4. Fail if non-canonical
5. Provide helpful error message

---

## Resulting Context

After implementing this pattern, you have:

- **Consistent output format** regardless of platform or template quirks
- **Reproducible transformation** with same input producing same output bytes
- **Clean diffs** showing only meaningful changes
- **Linter-clean artifacts** that pass code style checks
- **Cross-platform compatibility** for team collaboration
- **Format-aware handling** that respects each format's requirements

Canonicalization is the unsung hero of the transformation pipeline. It eliminates the invisible variations that would otherwise create noise, break idempotence, and erode trust in the generation system.

---

## Code References

The following spec-kit source files implement the canonicalization stage (μ₄):

| Reference | Description |
|-----------|-------------|
| `src/specify_cli/runtime/receipt.py:136` | Stage "canonicalize" in pipeline |
| `templates/command.tera:229-366` | Template with consistent formatting conventions |
| `ggen.toml` | Format-specific canonicalization configuration |

---

## Related Patterns

- **Part of:** **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₄
- **Follows:** **[24. Template Emission](./template-emission.md)** — Normalizes emission output
- **Precedes:** **[26. Receipt Generation](./receipt-generation.md)** — Canonical content for hash
- **Enables:** **[27. Idempotent Transform](./idempotent-transform.md)** — Consistent output

---

## Philosophical Note

> *"Consistency is the last refuge of the unimaginative."*
> — Oscar Wilde

Wilde critiqued foolish consistency—hobgoblin of little minds. But in transformations, consistency is the first requirement of reliability. Canonicalization ensures that what you see is what you get—every time, everywhere, for everyone.

The invisible variations that canonicalization eliminates are not expressions of creativity. They're accidents of environment—the platform you happen to use, the quirks of your template engine, the defaults of your text editor. Eliminating these accidents frees developers to focus on intentional differences—the changes that actually matter.

---

**Next:** The canonical output flows to **[26. Receipt Generation](./receipt-generation.md)**, where cryptographic proofs record the transformation for verification.
