# Thesis Builder - PhD Thesis Management Tool

A comprehensive Python utility for managing the PhD thesis on RDF-First Specification-Driven Development with Autonomous Generative Intelligence.

## Overview

The thesis builder automates:
- **LaTeX validation**: Syntax checking and structure validation
- **PDF generation**: Multi-compiler fallback system (pdflatex → lualatex → xelatex)
- **Consistency checking**: Detects when PDF/Markdown versions are out of sync with LaTeX source
- **Statistics**: Line counts, file sizes, modification times
- **Build cleanup**: Removes temporary LaTeX compilation artifacts

## File Structure

```
docs/
├── PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex  (SOURCE - 1,524 lines)
├── PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.pdf  (Generated PDF - 209 KB)
└── PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.md   (Generated Markdown - 1,138 lines)
```

## Usage

### Check Status
```bash
python3 scripts/thesis_builder.py status
```

Shows:
- File consistency (which files are out of date)
- Statistics (size, lines, modification times)
- Recommendations for regeneration

Example output:
```
📋 Thesis Build Status
============================================================

🔗 Checking file consistency...
LaTeX modified: 2025-12-24 04:49:59
PDF modified:   2025-12-23 04:52:24
⚠️  PDF is older than LaTeX source - regeneration recommended

📊 Thesis File Statistics
============================================================

PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex
  Size: 0.05 MB (52856 bytes)
  Modified: 2025-12-24T04:49:59
  Lines: 1524

PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.pdf
  Size: 0.2 MB (209041 bytes)
  Modified: 2025-12-23T04:52:24

PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.md
  Size: 0.03 MB (36386 bytes)
  Modified: 2025-12-23T04:52:24
  Lines: 1138
```

### Validate LaTeX Syntax
```bash
python3 scripts/thesis_builder.py validate
```

Checks:
- File exists and is readable
- Brace matching (all `{` have matching `}`)
- Document structure (`\begin{document}` and `\end{document}`)

Example output:
```
🔍 Validating LaTeX syntax...
✅ LaTeX syntax valid
```

### Generate PDF
```bash
python3 scripts/thesis_builder.py generate
```

Automatically tries compilers in order:
1. **pdflatex** - Most common (TeX Live standard)
2. **lualatex** - Modern Unicode support
3. **xelatex** - Advanced font support

Runs two passes to generate table of contents.

Example output:
```
📄 Generating PDF from LaTeX...
✅ PDF generated successfully (0.2 MB)
```

### Clean Build Artifacts
```bash
python3 scripts/thesis_builder.py clean
```

Removes temporary files:
- `*.aux` - Auxiliary files
- `*.log` - Compilation logs
- `*.out` - Hyperref outputs
- `*.toc` - Table of contents
- `*.idx` - Index files

## Setup Requirements

### For PDF Generation (Optional)

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive texlive-latex-extra texlive-fonts-recommended
```

**macOS:**
```bash
brew install mactex
# or
brew install basictex
tlmgr install texliveonline  # For online compilation
```

**Windows:**
- Download [MiKTeX](https://miktex.org/download)
- Or [TeX Live](http://www.tug.org/texlive/)

### Python Requirements

The tool requires only Python 3.7+ with standard library:
```python
import subprocess  # PDF generation
import pathlib     # File operations
import datetime    # File timestamps
import argparse    # CLI interface
```

No external pip dependencies needed.

## Thesis Content

### Recently Enhanced (December 24, 2025)

Added **698 new lines** documenting Autonomous Generative Intelligence:

#### **Chapter 7: RDF AGI Framework**
- Semantic agents (SpecificationAnalyzer, DependencyResolver, DesignExplorer)
- Autonomous reasoning engine with 5 inference strategies
- Multi-agent collaboration and consensus
- Learning mechanisms (belief reinforcement/questioning)

#### **Chapter 8: Hyperdimensional Semantic Spaces**
- Deterministic RDF-to-vector transformation (10,000D)
- Relationship encoding and constraint vectorization
- Semantic operations (cosine similarity, k-NN)
- Constraint satisfaction and analogical reasoning

#### **Appendices**
- **Appendix A**: 6 practical RDF AGI examples with code
- **Appendix B**: Semantic agent implementation details

### Total Thesis Size

| Metric | Value |
|--------|-------|
| LaTeX lines | 1,524 |
| PDF size | 209 KB |
| Markdown lines | 1,138 |
| Chapters | 10 |
| Appendices | 2 |
| Code examples | 20+ |

## Advanced Usage

### Python API

```python
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')
from thesis_builder import ThesisBuilder

# Initialize
builder = ThesisBuilder('docs')

# Check status
builder.check_consistency()  # True/False

# Get statistics
stats = builder.get_statistics()
print(f"LaTeX lines: {stats['files']['PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex']['lines']}")

# Validate
if builder.validate_tex():
    # Generate
    success = builder.generate_pdf()
```

### Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: Build Thesis

on:
  push:
    paths:
      - 'docs/PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install TeX Live
        run: |
          sudo apt-get update
          sudo apt-get install -y texlive texlive-latex-extra

      - name: Validate LaTeX
        run: python3 scripts/thesis_builder.py validate

      - name: Generate PDF
        run: python3 scripts/thesis_builder.py generate

      - name: Upload PDF
        uses: actions/upload-artifact@v2
        with:
          name: thesis-pdf
          path: docs/PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.pdf
```

## Troubleshooting

### No LaTeX Compiler Found

**Error**: `No LaTeX compiler found (pdflatex, lualatex, xelatex)`

**Solution**: Install TeX Live or MiKTeX:
```bash
# Ubuntu/Debian
sudo apt-get install texlive texlive-latex-extra

# macOS
brew install mactex

# Windows
# Download from https://miktex.org or http://www.tug.org/texlive/
```

### PDF Generation Timeout

**Error**: `Compilation timed out`

**Solution**:
- Increase timeout in `thesis_builder.py` (default: 120 seconds)
- Check for infinite loops in custom LaTeX code
- Ensure sufficient disk space

### Brace Mismatch Error

**Error**: `Brace mismatch: 1`

**Solution**:
- Count `{` and `}` in the file
- Use text editor's bracket matching feature
- Check for unescaped braces in code blocks

## Contributing

When enhancing the thesis:

1. **Edit LaTeX source**:
   ```bash
   vim docs/PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex
   ```

2. **Validate syntax**:
   ```bash
   python3 scripts/thesis_builder.py validate
   ```

3. **Generate PDF** (when LaTeX available):
   ```bash
   python3 scripts/thesis_builder.py generate
   ```

4. **Check consistency**:
   ```bash
   python3 scripts/thesis_builder.py status
   ```

5. **Commit changes**:
   ```bash
   git add docs/PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.{tex,pdf}
   git commit -m "docs: Update thesis with new content"
   ```

## Architecture

### ThesisBuilder Class

```python
class ThesisBuilder:
    def __init__(self, docs_dir: str = "docs")
    def validate_tex() -> bool
    def generate_pdf() -> bool
    def check_consistency() -> bool
    def get_statistics() -> dict
    def print_statistics()
    def status()
    def clean()
```

### Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `validate_tex()` | Check LaTeX syntax | bool |
| `generate_pdf()` | Create PDF from LaTeX | bool |
| `check_consistency()` | Compare file timestamps | bool |
| `get_statistics()` | Collect file metadata | dict |
| `print_statistics()` | Display formatted stats | None |
| `status()` | Full status report | None |
| `clean()` | Remove build artifacts | None |

## References

- [LaTeX Project](https://www.latex-project.org/)
- [TeX Live Documentation](https://tug.org/texlive/)
- [MiKTeX Documentation](https://miktex.org/docs/)
- [PhD Thesis: RDF-First Specification-Driven Development](docs/PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex)

## License

Same as ggen-spec-kit project.

---

**Last Updated**: December 24, 2025
**Tool Version**: 1.0
**Thesis Version**: v2.0 (with RDF AGI enhancements)
