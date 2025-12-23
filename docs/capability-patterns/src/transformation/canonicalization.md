# 25. Canonicalization

★★

*Different systems, different conventions. Canonicalization (μ₄) normalizes output format—line endings, whitespace, encoding—ensuring consistent artifacts regardless of where transformation runs.*

---

After **[Template Emission](./template-emission.md)**, you have rendered output. But this output may have inconsistencies:
- Mixed line endings (CRLF on Windows, LF on Unix)
- Trailing whitespace from template quirks
- Inconsistent indentation
- Missing final newlines

These inconsistencies cause problems:
- Git diffs show spurious changes
- Idempotence checks fail incorrectly
- Different team members get different output

Canonicalization normalizes these variations, producing consistent output regardless of platform or template quirks.

**The problem: Template output varies in formatting details. These variations break idempotence and create noisy diffs.**

---

**The forces at play:**

- *Compatibility wants flexibility.* Different platforms have different conventions.

- *Consistency wants standards.* One true format eliminates variation.

- *Tools want specific formats.* Some tools require specific line endings.

- *Simplicity wants minimal processing.* Extra processing adds complexity.

The tension: normalize enough to ensure consistency, not so much that you break tool requirements.

---

**Therefore:**

Implement canonicalization (μ₄) as a post-processing stage that normalizes formatting to a canonical form.

**Canonicalization operations:**

```
┌───────────────────────────────────────────────────────────────┐
│  μ₄ CANONICALIZE                                              │
│                                                               │
│  1. Normalize line endings to LF (Unix style)                 │
│  2. Remove trailing whitespace from each line                 │
│  3. Ensure consistent indentation (spaces, not tabs)*         │
│  4. Ensure file ends with single newline                      │
│  5. Normalize Unicode to NFC form                             │
│  6. Apply format-specific rules (if configured)               │
│                                                               │
│  Input: raw_output.txt                                        │
│  Output: canonical_output.txt                                 │
└───────────────────────────────────────────────────────────────┘

* Unless file format requires tabs (e.g., Makefiles)
```

**Configuration:**

```toml
# ggen.toml
[canonicalization]
line_ending = "lf"           # lf | crlf | native
trailing_whitespace = "remove"
final_newline = "ensure"
unicode_normalization = "nfc"

# Format-specific overrides
[canonicalization.overrides."*.md"]
trailing_whitespace = "preserve"  # Markdown uses trailing spaces

[canonicalization.overrides."Makefile"]
indentation = "tabs"
```

**Implementation example:**

```python
def canonicalize(content: str, config: dict) -> str:
    """Apply canonicalization to content."""

    # 1. Normalize line endings
    if config.get('line_ending') == 'lf':
        content = content.replace('\r\n', '\n').replace('\r', '\n')

    # 2. Remove trailing whitespace (unless preserved)
    if config.get('trailing_whitespace') == 'remove':
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)

    # 3. Ensure final newline
    if config.get('final_newline') == 'ensure':
        if not content.endswith('\n'):
            content += '\n'
        # Remove multiple trailing newlines
        while content.endswith('\n\n'):
            content = content[:-1]

    # 4. Unicode normalization
    if config.get('unicode_normalization') == 'nfc':
        import unicodedata
        content = unicodedata.normalize('NFC', content)

    return content
```

**Format-specific canonicalization:**

Different output formats may need specific treatment:

| Format | Considerations |
|--------|----------------|
| Python | PEP 8 formatting (black, ruff) |
| Markdown | Preserve intentional trailing spaces |
| YAML | Consistent indentation (2 spaces) |
| JSON | Consistent key ordering, indentation |
| Makefile | Tabs for recipes |

---

**Resulting context:**

After applying this pattern, you have:

- Consistent output format regardless of platform
- Reproducible transformation (same input → same output)
- Clean diffs showing only meaningful changes
- Artifacts that pass linter checks

This precedes **[Receipt Generation](./receipt-generation.md)** and enables **[Idempotent Transform](./idempotent-transform.md)**.

---

**Related patterns:**

- *Part of:* **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₄
- *Follows:* **[24. Template Emission](./template-emission.md)** — Normalizes emission output
- *Precedes:* **[26. Receipt Generation](./receipt-generation.md)** — Canonical hash
- *Enables:* **[27. Idempotent Transform](./idempotent-transform.md)** — Consistent output

---

> *"Consistency is the last refuge of the unimaginative."*
>
> — Oscar Wilde

In transformations, consistency is the first requirement of the reliable. Canonicalization ensures that what you see is what you get—every time, everywhere.
