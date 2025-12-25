"""
DSPy-based LaTeX Document Processor
====================================

Intelligent LaTeX parsing, validation, and optimization using DSPy.

This module provides comprehensive LaTeX document processing capabilities:

* **LaTeX Syntax Validation**: DSPy-powered validation with error detection
* **Intelligent Error Suggestions**: CoT reasoning for fix recommendations
* **Package Dependency Analysis**: Automatic detection of required packages
* **Structure Extraction**: Parse chapters, sections, equations, references
* **Metadata Extraction**: Extract title, author, date, and other metadata
* **Multi-pass Parsing**: Incremental parsing with caching for large documents
* **BibTeX Integration**: Cross-reference tracking and bibliography validation
* **Performance Optimization**: Suggestions for LaTeX compilation improvements

Key Classes
-----------
LaTeXDocument
    Represents a parsed LaTeX document with full structure
LaTeXValidator
    DSPy program for syntax validation with error detection
LaTeXOptimizer
    Suggests LaTeX improvements and best practices
LaTeXAnalyzer
    Extracts structural metrics and statistics

Example
-------
>>> from specify_cli.dspy_latex.processor import LaTeXProcessor
>>> processor = LaTeXProcessor()
>>> doc = processor.parse_file("thesis.tex")
>>> print(f"Chapters: {len(doc.chapters)}")
>>> print(f"Equations: {len(doc.equations)}")
>>> validation = processor.validate(doc)
>>> if not validation.is_valid:
...     for error in validation.errors:
...         print(f"Error: {error.message}")
...         print(f"Suggestion: {error.suggestion}")

Notes
-----
Requires DSPy to be installed and configured with a valid LLM provider.
OpenTelemetry instrumentation is included for performance monitoring.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from specify_cli.core.telemetry import (
    metric_counter,
    metric_histogram,
    record_exception,
    span,
)

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None  # type: ignore[assignment]


# ============================================================================
# Enums and Constants
# ============================================================================


class ErrorSeverity(Enum):
    """Error severity levels for LaTeX validation."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StructureType(Enum):
    """LaTeX document structure types."""

    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"
    SUBSUBSECTION = "subsubsection"
    PARAGRAPH = "paragraph"
    SUBPARAGRAPH = "subparagraph"


# Common LaTeX packages with their purposes
COMMON_PACKAGES = {
    "amsmath": "Advanced mathematics typesetting",
    "amssymb": "AMS mathematical symbols",
    "amsthm": "Theorem environments",
    "babel": "Multilingual support",
    "biblatex": "Bibliography management (modern)",
    "booktabs": "Publication quality tables",
    "caption": "Customizing captions",
    "cite": "Citation improvements",
    "color": "Color support",
    "fancyhdr": "Page headers and footers",
    "geometry": "Page layout customization",
    "graphicx": "Including graphics",
    "hyperref": "Hyperlinks and PDF features",
    "inputenc": "Input encoding specification",
    "listings": "Source code formatting",
    "natbib": "Bibliography management (traditional)",
    "tikz": "Graphics creation",
    "url": "URL formatting",
    "xcolor": "Extended color support",
}


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class LaTeXError:
    """Represents a LaTeX validation error with fix suggestion."""

    line: int
    column: int
    message: str
    severity: ErrorSeverity
    suggestion: str = ""
    reasoning: str = ""
    code_snippet: str = ""

    def __str__(self) -> str:
        """Format error for display."""
        return f"[{self.severity.value.upper()}] Line {self.line}: {self.message}"


@dataclass
class LaTeXPackage:
    """Represents a LaTeX package with options and purpose."""

    name: str
    options: list[str] = field(default_factory=list)
    purpose: str = ""
    required: bool = True
    line: int = 0

    def __str__(self) -> str:
        """Format package declaration."""
        opts = f"[{','.join(self.options)}]" if self.options else ""
        return f"\\usepackage{opts}{{{self.name}}}"


@dataclass
class LaTeXMetadata:
    """Extracted document metadata."""

    title: str = ""
    author: str = ""
    date: str = ""
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    document_class: str = ""
    document_class_options: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "document_class": self.document_class,
            "document_class_options": self.document_class_options,
        }


@dataclass
class LaTeXStructure:
    """Represents a document structure element (chapter, section, etc.)."""

    type: StructureType
    title: str
    label: str = ""
    line: int = 0
    level: int = 0
    content: str = ""
    children: list[LaTeXStructure] = field(default_factory=list)

    def __str__(self) -> str:
        """Format structure for display."""
        indent = "  " * self.level
        return f"{indent}{self.type.value}: {self.title}"


@dataclass
class LaTeXEquation:
    """Represents a mathematical equation."""

    content: str
    label: str = ""
    line: int = 0
    environment: str = "equation"
    numbered: bool = True
    references: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Format equation for display."""
        label_str = f"\\label{{{self.label}}}" if self.label else ""
        return f"\\begin{{{self.environment}}}\n{self.content}{label_str}\n\\end{{{self.environment}}}"


@dataclass
class LaTeXCrossReference:
    """Represents a cross-reference (\\ref, \\cite, etc.)."""

    type: str  # 'ref', 'cite', 'pageref', 'eqref', etc.
    target: str
    line: int = 0
    resolved: bool = False
    target_line: int = 0


@dataclass
class LaTeXDocument:
    """
    Represents a complete parsed LaTeX document.

    Attributes
    ----------
    source_file : Path
        Path to the source .tex file
    content : str
        Full document content
    metadata : LaTeXMetadata
        Extracted metadata (title, author, etc.)
    packages : list[LaTeXPackage]
        All \\usepackage declarations
    structures : list[LaTeXStructure]
        Document structure (chapters, sections, etc.)
    equations : list[LaTeXEquation]
        All mathematical equations
    cross_references : list[LaTeXCrossReference]
        All cross-references and citations
    labels : dict[str, int]
        Map of labels to line numbers
    citations : set[str]
        Set of all cited keys
    bibtex_files : list[str]
        Bibliography files referenced
    custom_commands : dict[str, str]
        User-defined commands (\\newcommand)
    cache_key : str
        MD5 hash for caching
    """

    source_file: Path
    content: str
    metadata: LaTeXMetadata = field(default_factory=LaTeXMetadata)
    packages: list[LaTeXPackage] = field(default_factory=list)
    structures: list[LaTeXStructure] = field(default_factory=list)
    equations: list[LaTeXEquation] = field(default_factory=list)
    cross_references: list[LaTeXCrossReference] = field(default_factory=list)
    labels: dict[str, int] = field(default_factory=dict)
    citations: set[str] = field(default_factory=set)
    bibtex_files: list[str] = field(default_factory=list)
    custom_commands: dict[str, str] = field(default_factory=dict)
    cache_key: str = ""

    def __post_init__(self) -> None:
        """Calculate cache key after initialization."""
        if not self.cache_key:
            self.cache_key = hashlib.md5(self.content.encode(), usedforsecurity=False).hexdigest()

    @property
    def chapters(self) -> list[LaTeXStructure]:
        """Get all chapter structures."""
        return [s for s in self.structures if s.type == StructureType.CHAPTER]

    @property
    def sections(self) -> list[LaTeXStructure]:
        """Get all section structures."""
        return [s for s in self.structures if s.type == StructureType.SECTION]

    def get_structure_by_label(self, label: str) -> LaTeXStructure | None:
        """Find structure by label."""
        for structure in self.structures:
            if structure.label == label:
                return structure
        return None

    def get_equation_by_label(self, label: str) -> LaTeXEquation | None:
        """Find equation by label."""
        for equation in self.equations:
            if equation.label == label:
                return equation
        return None

    def stats(self) -> dict[str, Any]:
        """Get document statistics."""
        return {
            "total_lines": len(self.content.splitlines()),
            "total_chars": len(self.content),
            "packages": len(self.packages),
            "chapters": len(self.chapters),
            "sections": len(self.sections),
            "equations": len(self.equations),
            "cross_references": len(self.cross_references),
            "labels": len(self.labels),
            "citations": len(self.citations),
            "bibtex_files": len(self.bibtex_files),
            "custom_commands": len(self.custom_commands),
        }


@dataclass
class ValidationResult:
    """
    Result of LaTeX document validation.

    Attributes
    ----------
    is_valid : bool
        Whether the document is valid
    errors : list[LaTeXError]
        All validation errors
    warnings : list[LaTeXError]
        All warnings
    suggestions : list[str]
        General improvement suggestions
    processing_time : float
        Time taken for validation (seconds)
    """

    is_valid: bool
    errors: list[LaTeXError] = field(default_factory=list)
    warnings: list[LaTeXError] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    processing_time: float = 0.0

    @property
    def error_count(self) -> int:
        """Count of errors."""
        return len([e for e in self.errors if e.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]])

    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return len([e for e in self.errors if e.severity == ErrorSeverity.WARNING])

    def __str__(self) -> str:
        """Format validation result."""
        if self.is_valid:
            return f"✓ Valid ({self.warning_count} warnings)"
        return f"✗ Invalid ({self.error_count} errors, {self.warning_count} warnings)"


@dataclass
class OptimizationResult:
    """
    Result of LaTeX document optimization.

    Attributes
    ----------
    suggestions : list[str]
        Optimization suggestions
    optimized_content : str
        Optimized LaTeX content
    improvements : dict[str, Any]
        Specific improvements made
    reasoning : str
        Explanation of optimizations
    performance_impact : str
        Expected performance impact
    """

    suggestions: list[str] = field(default_factory=list)
    optimized_content: str = ""
    improvements: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    performance_impact: str = ""


# ============================================================================
# DSPy Signatures
# ============================================================================

if DSPY_AVAILABLE:

    class ValidateLaTeXSignature(dspy.Signature):
        """Validate LaTeX syntax and detect errors with fix suggestions."""

        latex_content: str = dspy.InputField(desc="LaTeX document content to validate")
        line_number: int = dspy.InputField(desc="Starting line number for context")

        is_valid: bool = dspy.OutputField(desc="Whether the LaTeX syntax is valid")
        error_message: str = dspy.OutputField(
            desc="Error message if invalid, empty if valid"
        )
        error_line: int = dspy.OutputField(
            desc="Line number where error occurs, 0 if valid"
        )
        fix_suggestion: str = dspy.OutputField(
            desc="Suggested fix for the error, empty if valid"
        )
        reasoning: str = dspy.OutputField(
            desc="Chain of thought reasoning for the validation decision"
        )

    class ExtractMetadataSignature(dspy.Signature):
        """Extract metadata from LaTeX document preamble."""

        preamble: str = dspy.InputField(desc="LaTeX document preamble")

        title: str = dspy.OutputField(desc="Document title")
        author: str = dspy.OutputField(desc="Document author(s)")
        date: str = dspy.OutputField(desc="Document date")
        abstract: str = dspy.OutputField(desc="Document abstract")
        keywords: str = dspy.OutputField(
            desc="Comma-separated keywords"
        )

    class SuggestPackagesSignature(dspy.Signature):
        """Suggest required LaTeX packages based on document content."""

        latex_content: str = dspy.InputField(desc="LaTeX document content")
        current_packages: str = dspy.InputField(
            desc="Comma-separated list of current packages"
        )

        missing_packages: str = dspy.OutputField(
            desc="Comma-separated list of recommended missing packages"
        )
        reasoning: str = dspy.OutputField(
            desc="Explanation of why each package is recommended"
        )
        optional_packages: str = dspy.OutputField(
            desc="Comma-separated list of optional but useful packages"
        )

    class OptimizeLaTeXSignature(dspy.Signature):
        """Optimize LaTeX document for compilation performance and best practices."""

        latex_content: str = dspy.InputField(desc="LaTeX document content")
        focus: str = dspy.InputField(
            desc="Optimization focus: performance, readability, or compatibility"
        )

        optimized_content: str = dspy.OutputField(desc="Optimized LaTeX content")
        improvements: str = dspy.OutputField(
            desc="List of improvements made"
        )
        reasoning: str = dspy.OutputField(
            desc="Explanation of optimization decisions"
        )
        performance_impact: str = dspy.OutputField(
            desc="Expected performance improvement"
        )

    class AnalyzeEquationsSignature(dspy.Signature):
        """Analyze mathematical equations for correctness and style."""

        equations: str = dspy.InputField(
            desc="Mathematical equations to analyze"
        )
        context: str = dspy.InputField(
            desc="Document context for the equations"
        )

        issues: str = dspy.OutputField(
            desc="List of issues found in equations"
        )
        suggestions: str = dspy.OutputField(
            desc="Suggestions for improving equations"
        )
        best_practices: str = dspy.OutputField(
            desc="Mathematical typesetting best practices to apply"
        )


# ============================================================================
# DSPy Modules
# ============================================================================

if DSPY_AVAILABLE:

    class LaTeXValidator(dspy.Module):
        """
        DSPy module for LaTeX syntax validation.

        Uses Chain of Thought reasoning to validate LaTeX syntax,
        detect errors, and provide intelligent fix suggestions.
        """

        def __init__(self) -> None:
            """Initialize the validator."""
            super().__init__()
            self.validate = dspy.ChainOfThought(ValidateLaTeXSignature)

        def forward(
            self, latex_content: str, line_number: int = 0
        ) -> dspy.Prediction:
            """
            Validate LaTeX content.

            Parameters
            ----------
            latex_content : str
                LaTeX content to validate
            line_number : int, optional
                Starting line number for context

            Returns
            -------
            dspy.Prediction
                Validation result with error details
            """
            return self.validate(
                latex_content=latex_content, line_number=line_number
            )

    class LaTeXOptimizer(dspy.Module):
        """
        DSPy module for LaTeX optimization.

        Suggests improvements for compilation performance,
        readability, and LaTeX best practices.
        """

        def __init__(self) -> None:
            """Initialize the optimizer."""
            super().__init__()
            self.optimize = dspy.ChainOfThought(OptimizeLaTeXSignature)
            self.suggest_packages = dspy.Predict(SuggestPackagesSignature)

        def forward(
            self, latex_content: str, focus: str = "performance"
        ) -> dspy.Prediction:
            """
            Optimize LaTeX content.

            Parameters
            ----------
            latex_content : str
                LaTeX content to optimize
            focus : str, optional
                Optimization focus (performance, readability, compatibility)

            Returns
            -------
            dspy.Prediction
                Optimization result with suggestions
            """
            return self.optimize(latex_content=latex_content, focus=focus)

        def suggest_missing_packages(
            self, latex_content: str, current_packages: list[str]
        ) -> dspy.Prediction:
            """
            Suggest missing packages.

            Parameters
            ----------
            latex_content : str
                LaTeX content
            current_packages : list[str]
                Currently included packages

            Returns
            -------
            dspy.Prediction
                Package suggestions
            """
            return self.suggest_packages(
                latex_content=latex_content,
                current_packages=",".join(current_packages),
            )

    class LaTeXAnalyzer(dspy.Module):
        """
        DSPy module for LaTeX structural analysis.

        Extracts metadata, analyzes equations, and provides
        document statistics and insights.
        """

        def __init__(self) -> None:
            """Initialize the analyzer."""
            super().__init__()
            self.extract_metadata = dspy.Predict(ExtractMetadataSignature)
            self.analyze_equations = dspy.ChainOfThought(
                AnalyzeEquationsSignature
            )

        def forward(self, preamble: str) -> dspy.Prediction:
            """
            Extract metadata from preamble.

            Parameters
            ----------
            preamble : str
                LaTeX document preamble

            Returns
            -------
            dspy.Prediction
                Extracted metadata
            """
            return self.extract_metadata(preamble=preamble)

        def analyze_math(
            self, equations: str, context: str = ""
        ) -> dspy.Prediction:
            """
            Analyze mathematical equations.

            Parameters
            ----------
            equations : str
                Mathematical equations
            context : str, optional
                Document context

            Returns
            -------
            dspy.Prediction
                Equation analysis
            """
            return self.analyze_equations(equations=equations, context=context)


# ============================================================================
# LaTeX Parser
# ============================================================================


class LaTeXParser:
    """
    Pure Python LaTeX parser for structure extraction.

    Implements incremental parsing with caching for large documents.
    Does not use DSPy - provides structural parsing only.
    """

    def __init__(self) -> None:
        """Initialize the parser."""
        self._cache: dict[str, LaTeXDocument] = {}

    @lru_cache(maxsize=128)
    def _extract_packages(self, content: str) -> list[LaTeXPackage]:
        """Extract package declarations."""
        packages: list[LaTeXPackage] = []
        pattern = r"\\usepackage(?:\[([^\]]*)\])?\{([^}]+)\}"

        for match in re.finditer(pattern, content):
            options = match.group(1).split(",") if match.group(1) else []
            names = match.group(2).split(",")

            line = content[: match.start()].count("\n") + 1

            for name in names:
                name = name.strip()
                purpose = COMMON_PACKAGES.get(name, "")
                packages.append(
                    LaTeXPackage(
                        name=name,
                        options=[o.strip() for o in options],
                        purpose=purpose,
                        line=line,
                    )
                )

        return packages

    def _extract_document_class(self, content: str) -> tuple[str, list[str]]:
        """Extract document class and options."""
        pattern = r"\\documentclass(?:\[([^\]]*)\])?\{([^}]+)\}"
        match = re.search(pattern, content)

        if match:
            options = match.group(1).split(",") if match.group(1) else []
            doc_class = match.group(2).strip()
            return doc_class, [o.strip() for o in options]

        return "", []

    def _extract_metadata(self, content: str) -> LaTeXMetadata:
        """Extract basic metadata without DSPy."""
        metadata = LaTeXMetadata()

        # Extract document class
        doc_class, options = self._extract_document_class(content)
        metadata.document_class = doc_class
        metadata.document_class_options = options

        # Extract title
        title_match = re.search(r"\\title\{([^}]+)\}", content)
        if title_match:
            metadata.title = title_match.group(1).strip()

        # Extract author
        author_match = re.search(r"\\author\{([^}]+)\}", content)
        if author_match:
            metadata.author = author_match.group(1).strip()

        # Extract date
        date_match = re.search(r"\\date\{([^}]+)\}", content)
        if date_match:
            metadata.date = date_match.group(1).strip()

        # Extract abstract
        abstract_match = re.search(
            r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
            content,
            re.DOTALL,
        )
        if abstract_match:
            metadata.abstract = abstract_match.group(1).strip()

        return metadata

    def _extract_structures(self, content: str) -> list[LaTeXStructure]:
        """Extract document structures (chapters, sections, etc.)."""
        structures: list[LaTeXStructure] = []

        # Pattern for structure commands
        structure_patterns = {
            StructureType.CHAPTER: (r"\\chapter\{([^}]+)\}", 0),
            StructureType.SECTION: (r"\\section\{([^}]+)\}", 1),
            StructureType.SUBSECTION: (r"\\subsection\{([^}]+)\}", 2),
            StructureType.SUBSUBSECTION: (r"\\subsubsection\{([^}]+)\}", 3),
            StructureType.PARAGRAPH: (r"\\paragraph\{([^}]+)\}", 4),
            StructureType.SUBPARAGRAPH: (r"\\subparagraph\{([^}]+)\}", 5),
        }

        for struct_type, (pattern, level) in structure_patterns.items():
            for match in re.finditer(pattern, content):
                title = match.group(1).strip()
                line = content[: match.start()].count("\n") + 1

                # Try to find label
                label = ""
                label_pattern = r"\\label\{([^}]+)\}"
                # Look for label in next 200 characters
                context = content[match.end() : match.end() + 200]
                label_match = re.search(label_pattern, context)
                if label_match:
                    label = label_match.group(1).strip()

                structures.append(
                    LaTeXStructure(
                        type=struct_type,
                        title=title,
                        label=label,
                        line=line,
                        level=level,
                    )
                )

        # Sort by line number
        structures.sort(key=lambda s: s.line)
        return structures

    def _extract_equations(self, content: str) -> list[LaTeXEquation]:
        """Extract mathematical equations."""
        equations: list[LaTeXEquation] = []

        # Common equation environments
        environments = [
            "equation",
            "equation*",
            "align",
            "align*",
            "gather",
            "gather*",
            "multline",
            "multline*",
        ]

        for env in environments:
            pattern = rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}"
            for match in re.finditer(pattern, content, re.DOTALL):
                eq_content = match.group(1).strip()
                line = content[: match.start()].count("\n") + 1
                numbered = not env.endswith("*")

                # Extract label if present
                label = ""
                label_match = re.search(r"\\label\{([^}]+)\}", eq_content)
                if label_match:
                    label = label_match.group(1).strip()
                    # Remove label from content
                    eq_content = re.sub(r"\\label\{[^}]+\}", "", eq_content).strip()

                equations.append(
                    LaTeXEquation(
                        content=eq_content,
                        label=label,
                        line=line,
                        environment=env,
                        numbered=numbered,
                    )
                )

        return equations

    def _extract_labels(self, content: str) -> dict[str, int]:
        """Extract all labels and their line numbers."""
        labels: dict[str, int] = {}
        pattern = r"\\label\{([^}]+)\}"

        for match in re.finditer(pattern, content):
            label = match.group(1).strip()
            line = content[: match.start()].count("\n") + 1
            labels[label] = line

        return labels

    def _extract_cross_references(
        self, content: str
    ) -> list[LaTeXCrossReference]:
        """Extract cross-references."""
        references: list[LaTeXCrossReference] = []

        # Reference patterns
        ref_patterns = {
            "ref": r"\\ref\{([^}]+)\}",
            "eqref": r"\\eqref\{([^}]+)\}",
            "pageref": r"\\pageref\{([^}]+)\}",
            "cite": r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",
            "citep": r"\\citep(?:\[[^\]]*\])?\{([^}]+)\}",
            "citet": r"\\citet(?:\[[^\]]*\])?\{([^}]+)\}",
        }

        for ref_type, pattern in ref_patterns.items():
            for match in re.finditer(pattern, content):
                targets = match.group(1).split(",")
                line = content[: match.start()].count("\n") + 1

                for target in targets:
                    references.append(
                        LaTeXCrossReference(
                            type=ref_type,
                            target=target.strip(),
                            line=line,
                        )
                    )

        return references

    def _extract_citations(self, content: str) -> set[str]:
        """Extract all citation keys."""
        citations: set[str] = set()

        cite_pattern = r"\\cite[pt]?(?:\[[^\]]*\])?\{([^}]+)\}"
        for match in re.finditer(cite_pattern, content):
            keys = match.group(1).split(",")
            citations.update(k.strip() for k in keys)

        return citations

    def _extract_bibtex_files(self, content: str) -> list[str]:
        """Extract bibliography file references."""
        bibtex_files: list[str] = []

        # Traditional \bibliography
        bib_pattern = r"\\bibliography\{([^}]+)\}"
        for match in re.finditer(bib_pattern, content):
            files = match.group(1).split(",")
            bibtex_files.extend(f.strip() for f in files)

        # BibLaTeX \addbibresource
        addbib_pattern = r"\\addbibresource\{([^}]+)\}"
        for match in re.finditer(addbib_pattern, content):
            bibtex_files.append(match.group(1).strip())

        return bibtex_files

    def _extract_custom_commands(self, content: str) -> dict[str, str]:
        """Extract user-defined commands."""
        commands: dict[str, str] = {}

        # \newcommand{\name}[args]{definition}
        pattern = r"\\newcommand\{\\([^}]+)\}(?:\[(\d+)\])?\{([^}]+)\}"
        for match in re.finditer(pattern, content):
            name = match.group(1).strip()
            args = match.group(2) if match.group(2) else "0"
            definition = match.group(3).strip()
            commands[name] = f"[{args}] {definition}"

        return commands

    def parse(self, content: str, source_file: Path | None = None) -> LaTeXDocument:
        """
        Parse LaTeX content into structured document.

        Parameters
        ----------
        content : str
            LaTeX document content
        source_file : Path, optional
            Source file path

        Returns
        -------
        LaTeXDocument
            Parsed document structure
        """
        with span("latex.parse", source_file=str(source_file) if source_file else ""):
            start_time = time.perf_counter()

            # Check cache
            cache_key = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()
            if cache_key in self._cache:
                metric_counter("latex.parse.cache_hit")(1)
                return self._cache[cache_key]

            metric_counter("latex.parse.cache_miss")(1)

            # Create document
            doc = LaTeXDocument(
                source_file=source_file or Path(),
                content=content,
                cache_key=cache_key,
            )

            # Extract all components
            doc.metadata = self._extract_metadata(content)
            doc.packages = self._extract_packages(content)
            doc.structures = self._extract_structures(content)
            doc.equations = self._extract_equations(content)
            doc.labels = self._extract_labels(content)
            doc.cross_references = self._extract_cross_references(content)
            doc.citations = self._extract_citations(content)
            doc.bibtex_files = self._extract_bibtex_files(content)
            doc.custom_commands = self._extract_custom_commands(content)

            # Cache the result
            self._cache[cache_key] = doc

            # Record metrics
            parse_time = time.perf_counter() - start_time
            metric_histogram("latex.parse.duration")(parse_time)
            metric_counter("latex.parse.completed")(1)

            return doc

    def parse_file(self, file_path: Path) -> LaTeXDocument:
        """
        Parse LaTeX file.

        Parameters
        ----------
        file_path : Path
            Path to .tex file

        Returns
        -------
        LaTeXDocument
            Parsed document

        Raises
        ------
        FileNotFoundError
            If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"LaTeX file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        return self.parse(content, source_file=file_path)


# ============================================================================
# Main Processor
# ============================================================================


class LaTeXProcessor:
    """
    Main LaTeX document processor with DSPy-powered validation and optimization.

    Combines structural parsing, intelligent validation, and optimization
    into a unified interface.

    Example
    -------
    >>> processor = LaTeXProcessor()
    >>> doc = processor.parse_file("document.tex")
    >>> validation = processor.validate(doc)
    >>> if not validation.is_valid:
    ...     for error in validation.errors:
    ...         print(error)
    >>> optimization = processor.optimize(doc, focus="performance")
    >>> print(optimization.suggestions)
    """

    def __init__(self) -> None:
        """Initialize the processor."""
        self.parser = LaTeXParser()
        self.dspy_available = DSPY_AVAILABLE

        if DSPY_AVAILABLE:
            self.validator = LaTeXValidator()
            self.optimizer = LaTeXOptimizer()
            self.analyzer = LaTeXAnalyzer()
        else:
            self.validator = None  # type: ignore[assignment]
            self.optimizer = None  # type: ignore[assignment]
            self.analyzer = None  # type: ignore[assignment]

    def parse(self, content: str, source_file: Path | None = None) -> LaTeXDocument:
        """
        Parse LaTeX content.

        Parameters
        ----------
        content : str
            LaTeX content
        source_file : Path, optional
            Source file path

        Returns
        -------
        LaTeXDocument
            Parsed document
        """
        return self.parser.parse(content, source_file)

    def parse_file(self, file_path: Path) -> LaTeXDocument:
        """
        Parse LaTeX file.

        Parameters
        ----------
        file_path : Path
            Path to .tex file

        Returns
        -------
        LaTeXDocument
            Parsed document
        """
        return self.parser.parse_file(file_path)

    def validate(
        self, doc: LaTeXDocument, use_dspy: bool = True
    ) -> ValidationResult:
        """
        Validate LaTeX document.

        Parameters
        ----------
        doc : LaTeXDocument
            Document to validate
        use_dspy : bool, optional
            Use DSPy for intelligent validation

        Returns
        -------
        ValidationResult
            Validation result with errors and suggestions
        """
        with span("latex.validate", use_dspy=use_dspy):
            start_time = time.perf_counter()
            errors: list[LaTeXError] = []

            # Basic validation (always performed)
            errors.extend(self._validate_structure(doc))
            errors.extend(self._validate_cross_references(doc))
            errors.extend(self._validate_citations(doc))

            # DSPy-powered validation
            if use_dspy and self.dspy_available and self.validator:
                try:
                    # Validate in chunks for large documents
                    chunk_size = 1000
                    lines = doc.content.splitlines()

                    for i in range(0, len(lines), chunk_size):
                        chunk = "\n".join(lines[i : i + chunk_size])
                        result = self.validator.forward(chunk, line_number=i)

                        if not getattr(result, "is_valid", True):
                            error_line = getattr(result, "error_line", 0)
                            error_msg = getattr(result, "error_message", "")
                            suggestion = getattr(result, "fix_suggestion", "")
                            reasoning = getattr(result, "reasoning", "")

                            errors.append(
                                LaTeXError(
                                    line=error_line,
                                    column=0,
                                    message=error_msg,
                                    severity=ErrorSeverity.ERROR,
                                    suggestion=suggestion,
                                    reasoning=reasoning,
                                )
                            )

                except Exception as e:
                    record_exception(e)
                    metric_counter("latex.validate.dspy_error")(1)

            # Determine if valid
            critical_errors = [
                e for e in errors if e.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]
            ]
            is_valid = len(critical_errors) == 0

            processing_time = time.perf_counter() - start_time

            # Separate errors and warnings
            actual_errors = [e for e in errors if e.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]]
            warnings = [e for e in errors if e.severity == ErrorSeverity.WARNING]

            result = ValidationResult(
                is_valid=is_valid,
                errors=actual_errors,
                warnings=warnings,
                processing_time=processing_time,
            )

            metric_histogram("latex.validate.duration")(processing_time)
            metric_counter("latex.validate.completed")(1)

            return result

    def _validate_structure(self, doc: LaTeXDocument) -> list[LaTeXError]:
        """Validate document structure."""
        errors: list[LaTeXError] = []

        # Check for document class
        if not doc.metadata.document_class:
            errors.append(
                LaTeXError(
                    line=1,
                    column=0,
                    message="Missing \\documentclass declaration",
                    severity=ErrorSeverity.ERROR,
                    suggestion="Add \\documentclass{article} or similar at the beginning",
                )
            )

        # Check for begin/end document
        if "\\begin{document}" not in doc.content:
            errors.append(
                LaTeXError(
                    line=1,
                    column=0,
                    message="Missing \\begin{document}",
                    severity=ErrorSeverity.CRITICAL,
                    suggestion="Add \\begin{document} after preamble",
                )
            )

        if "\\end{document}" not in doc.content:
            errors.append(
                LaTeXError(
                    line=len(doc.content.splitlines()),
                    column=0,
                    message="Missing \\end{document}",
                    severity=ErrorSeverity.CRITICAL,
                    suggestion="Add \\end{document} at the end of document",
                )
            )

        return errors

    def _validate_cross_references(self, doc: LaTeXDocument) -> list[LaTeXError]:
        """Validate cross-references."""
        errors: list[LaTeXError] = []

        for ref in doc.cross_references:
            if ref.type in ["ref", "eqref", "pageref"] and ref.target not in doc.labels:
                errors.append(
                    LaTeXError(
                        line=ref.line,
                        column=0,
                        message=f"Undefined reference: {ref.target}",
                        severity=ErrorSeverity.WARNING,
                        suggestion=f"Add \\label{{{ref.target}}} to the referenced element",
                    )
                )

        return errors

    def _validate_citations(self, doc: LaTeXDocument) -> list[LaTeXError]:
        """Validate citations."""
        errors: list[LaTeXError] = []

        # Check if citations exist but no bibliography
        if doc.citations and not doc.bibtex_files:
            errors.append(
                LaTeXError(
                    line=1,
                    column=0,
                    message="Citations found but no bibliography files specified",
                    severity=ErrorSeverity.WARNING,
                    suggestion="Add \\bibliography{refs} or \\addbibresource{refs.bib}",
                )
            )

        return errors

    def optimize(
        self,
        doc: LaTeXDocument,
        focus: str = "performance",
    ) -> OptimizationResult:
        """
        Optimize LaTeX document.

        Parameters
        ----------
        doc : LaTeXDocument
            Document to optimize
        focus : str, optional
            Optimization focus (performance, readability, compatibility)

        Returns
        -------
        OptimizationResult
            Optimization suggestions and results
        """
        with span("latex.optimize", focus=focus):
            if not self.dspy_available or not self.optimizer:
                return OptimizationResult(
                    suggestions=[
                        "DSPy not available - install with: pip install dspy"
                    ]
                )

            try:
                # Run optimization
                result = self.optimizer.forward(doc.content, focus=focus)

                optimized = getattr(result, "optimized_content", doc.content)
                improvements = getattr(result, "improvements", "")
                reasoning = getattr(result, "reasoning", "")
                performance = getattr(result, "performance_impact", "")

                # Parse improvements
                improvement_list = [
                    i.strip() for i in improvements.split("\n") if i.strip()
                ]

                return OptimizationResult(
                    suggestions=improvement_list,
                    optimized_content=optimized,
                    improvements={"raw": improvements},
                    reasoning=reasoning,
                    performance_impact=performance,
                )

            except Exception as e:
                record_exception(e)
                return OptimizationResult(
                    suggestions=[f"Optimization failed: {e}"]
                )

    def suggest_packages(self, doc: LaTeXDocument) -> list[str]:
        """
        Suggest missing packages.

        Parameters
        ----------
        doc : LaTeXDocument
            Document to analyze

        Returns
        -------
        list[str]
            Suggested packages
        """
        if not self.dspy_available or not self.optimizer:
            return []

        try:
            current = [p.name for p in doc.packages]
            result = self.optimizer.suggest_missing_packages(
                doc.content, current
            )

            missing = getattr(result, "missing_packages", "")
            return [p.strip() for p in missing.split(",") if p.strip()]


        except Exception as e:
            record_exception(e)
            return []

    def analyze_equations(
        self, doc: LaTeXDocument
    ) -> dict[str, Any]:
        """
        Analyze mathematical equations.

        Parameters
        ----------
        doc : LaTeXDocument
            Document containing equations

        Returns
        -------
        dict[str, Any]
            Analysis results
        """
        if not self.dspy_available or not self.analyzer:
            return {
                "total": len(doc.equations),
                "numbered": sum(1 for eq in doc.equations if eq.numbered),
            }

        try:
            # Combine equations for analysis
            equations_text = "\n\n".join(
                f"% Line {eq.line}\n{eq}" for eq in doc.equations
            )

            result = self.analyzer.analyze_math(
                equations_text, context=doc.metadata.title
            )

            issues = getattr(result, "issues", "")
            suggestions = getattr(result, "suggestions", "")
            best_practices = getattr(result, "best_practices", "")

            return {
                "total": len(doc.equations),
                "numbered": sum(1 for eq in doc.equations if eq.numbered),
                "issues": [i.strip() for i in issues.split("\n") if i.strip()],
                "suggestions": [
                    s.strip() for s in suggestions.split("\n") if s.strip()
                ],
                "best_practices": [
                    b.strip() for b in best_practices.split("\n") if b.strip()
                ],
            }

        except Exception as e:
            record_exception(e)
            return {"error": str(e)}


# ============================================================================
# Convenience Functions
# ============================================================================


def process_latex_file(
    file_path: Path,
    validate: bool = True,
    optimize: bool = False,
) -> tuple[LaTeXDocument, ValidationResult | None, OptimizationResult | None]:
    """
    Process a LaTeX file with validation and optional optimization.

    Parameters
    ----------
    file_path : Path
        Path to .tex file
    validate : bool, optional
        Perform validation
    optimize : bool, optional
        Perform optimization

    Returns
    -------
    tuple[LaTeXDocument, ValidationResult | None, OptimizationResult | None]
        Parsed document, validation result, optimization result

    Example
    -------
    >>> doc, validation, optimization = process_latex_file(
    ...     Path("thesis.tex"),
    ...     validate=True,
    ...     optimize=True
    ... )
    >>> print(f"Chapters: {len(doc.chapters)}")
    >>> print(validation)
    >>> print(optimization.suggestions)
    """
    processor = LaTeXProcessor()

    # Parse document
    doc = processor.parse_file(file_path)

    # Validate
    validation_result = processor.validate(doc) if validate else None

    # Optimize
    optimization_result = processor.optimize(doc) if optimize else None

    return doc, validation_result, optimization_result


__all__ = [
    "ErrorSeverity",
    "LaTeXAnalyzer",
    "LaTeXCrossReference",
    "LaTeXDocument",
    "LaTeXEquation",
    "LaTeXError",
    "LaTeXMetadata",
    "LaTeXOptimizer",
    "LaTeXPackage",
    "LaTeXParser",
    "LaTeXProcessor",
    "LaTeXStructure",
    "LaTeXValidator",
    "OptimizationResult",
    "StructureType",
    "ValidationResult",
    "process_latex_file",
]
