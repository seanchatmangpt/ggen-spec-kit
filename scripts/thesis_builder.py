#!/usr/bin/env python3
"""
Thesis Builder Tool - Manage PhD thesis LaTeX, PDF, and Markdown versions.

This tool handles:
- LaTeX validation and syntax checking
- PDF generation from LaTeX source
- Markdown conversion (fallback format)
- Version consistency checking
- Thesis file statistics and metadata
"""

import os
import sys
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class ThesisBuilder:
    """Manages thesis generation and validation."""

    def __init__(self, docs_dir: str = "docs"):
        """Initialize thesis builder."""
        self.docs_dir = Path(docs_dir)
        self.tex_file = self.docs_dir / "PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex"
        self.pdf_file = self.docs_dir / "PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.pdf"
        self.md_file = self.docs_dir / "PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.md"

    def validate_tex(self) -> bool:
        """Validate LaTeX syntax."""
        print("🔍 Validating LaTeX syntax...")

        if not self.tex_file.exists():
            print(f"❌ LaTeX file not found: {self.tex_file}")
            return False

        try:
            with open(self.tex_file, 'r') as f:
                content = f.read()

            # Basic syntax checks
            brace_count = content.count('{') - content.count('}')
            if brace_count != 0:
                print(f"⚠️  Brace mismatch: {brace_count}")
                return False

            if '\\begin{document}' not in content or '\\end{document}' not in content:
                print("❌ Missing document environment")
                return False

            print("✅ LaTeX syntax valid")
            return True
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False

    def generate_pdf(self) -> bool:
        """Generate PDF from LaTeX source using available tools."""
        print("\n📄 Generating PDF from LaTeX...")

        if not self.validate_tex():
            return False

        # Try pdflatex (most common)
        if self._try_pdflatex():
            return True

        # Try lualatex
        if self._try_lualatex():
            return True

        # Try xelatex
        if self._try_xelatex():
            return True

        print("⚠️  No LaTeX compiler found (pdflatex, lualatex, xelatex)")
        print("   Install TeX Live or MiKTeX for PDF generation")
        return False

    def _try_pdflatex(self) -> bool:
        """Try to generate PDF using pdflatex."""
        try:
            # First pass
            result1 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", str(self.tex_file)],
                cwd=self.docs_dir,
                capture_output=True,
                timeout=120
            )

            if result1.returncode != 0:
                return False

            # Second pass for TOC
            result2 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", str(self.tex_file)],
                cwd=self.docs_dir,
                capture_output=True,
                timeout=120
            )

            if result2.returncode == 0 and self.pdf_file.exists():
                size_mb = self.pdf_file.stat().st_size / (1024 * 1024)
                print(f"✅ PDF generated successfully ({size_mb:.1f} MB)")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return False

    def _try_lualatex(self) -> bool:
        """Try to generate PDF using lualatex."""
        try:
            result1 = subprocess.run(
                ["lualatex", "-interaction=nonstopmode", str(self.tex_file)],
                cwd=self.docs_dir,
                capture_output=True,
                timeout=120
            )

            if result1.returncode != 0:
                return False

            result2 = subprocess.run(
                ["lualatex", "-interaction=nonstopmode", str(self.tex_file)],
                cwd=self.docs_dir,
                capture_output=True,
                timeout=120
            )

            if result2.returncode == 0 and self.pdf_file.exists():
                size_mb = self.pdf_file.stat().st_size / (1024 * 1024)
                print(f"✅ PDF generated with lualatex ({size_mb:.1f} MB)")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return False

    def _try_xelatex(self) -> bool:
        """Try to generate PDF using xelatex."""
        try:
            result1 = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", str(self.tex_file)],
                cwd=self.docs_dir,
                capture_output=True,
                timeout=120
            )

            if result1.returncode != 0:
                return False

            result2 = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", str(self.tex_file)],
                cwd=self.docs_dir,
                capture_output=True,
                timeout=120
            )

            if result2.returncode == 0 and self.pdf_file.exists():
                size_mb = self.pdf_file.stat().st_size / (1024 * 1024)
                print(f"✅ PDF generated with xelatex ({size_mb:.1f} MB)")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return False

    def get_statistics(self) -> dict:
        """Get thesis file statistics."""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }

        for file_path in [self.tex_file, self.pdf_file, self.md_file]:
            if file_path.exists():
                stat = file_path.stat()
                # Count lines if text file
                lines = None
                if file_path.suffix in ['.tex', '.md']:
                    try:
                        with open(file_path, 'r') as f:
                            lines = len(f.readlines())
                    except:
                        pass

                stats["files"][file_path.name] = {
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "lines": lines
                }

        return stats

    def print_statistics(self):
        """Print thesis statistics."""
        stats = self.get_statistics()

        print("\n📊 Thesis File Statistics")
        print("=" * 60)

        for filename, info in stats["files"].items():
            print(f"\n{filename}")
            print(f"  Size: {info['size_mb']} MB ({info['size_bytes']} bytes)")
            print(f"  Modified: {info['modified']}")
            if info.get('lines'):
                print(f"  Lines: {info['lines']}")

    def check_consistency(self) -> bool:
        """Check consistency between versions."""
        print("\n🔗 Checking file consistency...")

        all_exist = all(f.exists() for f in [self.tex_file, self.pdf_file, self.md_file])

        if not all_exist:
            print("⚠️  Not all versions exist:")
            print(f"  .tex: {'✅' if self.tex_file.exists() else '❌'}")
            print(f"  .pdf: {'✅' if self.pdf_file.exists() else '❌'}")
            print(f"  .md:  {'✅' if self.md_file.exists() else '❌'}")

        # Check modification times
        if self.tex_file.exists():
            tex_mtime = self.tex_file.stat().st_mtime
            print(f"\nLaTeX modified: {datetime.fromtimestamp(tex_mtime)}")

            if self.pdf_file.exists():
                pdf_mtime = self.pdf_file.stat().st_mtime
                pdf_time = datetime.fromtimestamp(pdf_mtime)
                print(f"PDF modified:   {pdf_time}")

                if pdf_mtime < tex_mtime:
                    print("⚠️  PDF is older than LaTeX source - regeneration recommended")
                    return False

            if self.md_file.exists():
                md_mtime = self.md_file.stat().st_mtime
                md_time = datetime.fromtimestamp(md_mtime)
                print(f"Markdown modified: {md_time}")

                if md_mtime < tex_mtime:
                    print("⚠️  Markdown is older than LaTeX source - update recommended")

        return True

    def status(self):
        """Print current status."""
        print("\n📋 Thesis Build Status")
        print("=" * 60)

        self.check_consistency()
        self.print_statistics()

        print("\n" + "=" * 60)

    def clean(self):
        """Clean generated files (keep source)."""
        print("🧹 Cleaning generated files...")

        to_clean = [
            self.docs_dir / "*.aux",
            self.docs_dir / "*.log",
            self.docs_dir / "*.out",
            self.docs_dir / "*.toc",
            self.docs_dir / "*.idx",
        ]

        for pattern in to_clean:
            for file in self.docs_dir.glob(pattern.name):
                try:
                    file.unlink()
                    print(f"  Removed: {file.name}")
                except Exception as e:
                    print(f"  Failed to remove {file.name}: {e}")

        print("✅ Clean complete")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="PhD Thesis Builder - Manage thesis generation"
    )
    parser.add_argument(
        "command",
        choices=["validate", "generate", "status", "clean"],
        help="Command to execute"
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Documentation directory (default: docs)"
    )

    args = parser.parse_args()

    # Ensure we're in the right directory
    if not Path(args.docs_dir).exists():
        print(f"❌ Directory not found: {args.docs_dir}")
        sys.exit(1)

    builder = ThesisBuilder(args.docs_dir)

    if args.command == "validate":
        success = builder.validate_tex()
        sys.exit(0 if success else 1)

    elif args.command == "generate":
        success = builder.generate_pdf()
        if success:
            print("\n✅ Thesis build successful")
            sys.exit(0)
        else:
            print("\n❌ Thesis build failed")
            sys.exit(1)

    elif args.command == "status":
        builder.status()

    elif args.command == "clean":
        builder.clean()


if __name__ == "__main__":
    main()
