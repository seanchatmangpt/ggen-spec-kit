"""
LaTeX Sample Documents and Test Fixtures

Provides comprehensive test data for DSPy LaTeX-to-PDF engine testing.
Includes valid documents, error scenarios, and edge cases.

Fixtures:
    - Simple documents
    - Complex thesis-style documents
    - Documents with errors
    - Documents with special features (math, graphics, bibliography)
    - Performance test documents
    - Edge case documents
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest


# ============================================================================
# Simple LaTeX Documents
# ============================================================================


@pytest.fixture
def minimal_latex() -> str:
    """
    Minimal valid LaTeX document.

    Returns
    -------
    str
        Absolute minimum LaTeX document
    """
    return r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""


@pytest.fixture
def simple_article() -> str:
    """
    Simple article with basic structure.

    Returns
    -------
    str
        Simple article document
    """
    return r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\title{Simple Article}
\author{Test Author}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
This is a simple article for testing purposes.
\end{abstract}

\section{Introduction}
This is the introduction section.

\section{Methods}
This section describes the methods used.

\section{Results}
This section presents the results.

\section{Conclusion}
This is the conclusion.

\end{document}
"""


# ============================================================================
# Complex Documents
# ============================================================================


@pytest.fixture
def complex_thesis() -> str:
    """
    Complex thesis-style document.

    Returns
    -------
    str
        Comprehensive thesis document
    """
    return r"""
\documentclass[12pt,a4paper,oneside]{report}

% Packages
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{longtable}

% Spacing
\onehalfspacing
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0.5in}

% Code listing style
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!10},
    numberstyle=\tiny\color{gray},
    numbers=left,
    numbersep=5pt,
}

% Header and footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[R]{\thepage}
\fancyhead[L]{PhD Thesis}
\renewcommand{\headrulewidth}{0.5pt}

% Title page
\title{%
    \textbf{PhD Thesis}\\[0.5cm]
    \Large Research Topic Title
}
\author{Test Author}
\date{\today}

\begin{document}

% Title page
\maketitle

% Abstract
\begin{abstract}
This thesis presents comprehensive research on an important topic.
Key contributions include novel methodologies and significant findings.
\end{abstract}

% Table of contents
\tableofcontents
\newpage

% List of figures
\listoffigures
\newpage

% List of tables
\listoftables
\newpage

% Chapters
\chapter{Introduction}

\section{Background}
Background information and context for the research.

\subsection{Problem Statement}
Clear articulation of the research problem.

\subsection{Research Questions}
\begin{itemize}
    \item Research question 1
    \item Research question 2
    \item Research question 3
\end{itemize}

\section{Objectives}
Research objectives and goals.

\section{Thesis Structure}
Overview of the thesis organization.

\chapter{Literature Review}

\section{Theoretical Framework}
Review of relevant theories and frameworks.

\section{Related Work}
Summary of existing research in the field.

\subsection{Previous Studies}
Discussion of previous research efforts.

\subsection{Research Gaps}
Identification of gaps in existing literature.

\chapter{Methodology}

\section{Research Design}
Description of the overall research approach.

\section{Data Collection}
Methods used for collecting data.

\section{Analysis Methods}
Techniques applied for data analysis.

\chapter{Results}

\section{Findings}
Presentation of research findings.

\subsection{Quantitative Results}
Statistical analysis and quantitative findings.

\subsection{Qualitative Results}
Thematic analysis and qualitative insights.

\section{Discussion}
Interpretation of results and their implications.

\chapter{Conclusion}

\section{Summary}
Summary of key findings and contributions.

\section{Limitations}
Acknowledgment of research limitations.

\section{Future Work}
Suggestions for future research directions.

% Bibliography
\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""


# ============================================================================
# Error Documents
# ============================================================================


@pytest.fixture
def latex_syntax_errors() -> Dict[str, str]:
    """
    Collection of LaTeX documents with various syntax errors.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping error type to document
    """
    return {
        "missing_brace": r"""
\documentclass{article}
\begin{document}
\textbf{Missing closing brace
\end{document}
""",
        "undefined_command": r"""
\documentclass{article}
\begin{document}
\unknowncommand{test}
\end{document}
""",
        "unmatched_environment": r"""
\documentclass{article}
\begin{document}
\begin{equation}
    x = y
\end{itemize}
\end{document}
""",
        "missing_end_document": r"""
\documentclass{article}
\begin{document}
\section{Test}
Some content.
""",
        "duplicate_begin": r"""
\documentclass{article}
\begin{document}
\begin{document}
Test
\end{document}
""",
        "unclosed_math": r"""
\documentclass{article}
\begin{document}
Inline math: $x = y
Text continues.
\end{document}
""",
    }


@pytest.fixture
def latex_package_errors() -> Dict[str, str]:
    """
    LaTeX documents with package-related errors.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping error type to document
    """
    return {
        "missing_package": r"""
\documentclass{article}
\begin{document}
\begin{tikzpicture}
    \draw (0,0) -- (1,1);
\end{tikzpicture}
\end{document}
""",
        "conflicting_packages": r"""
\documentclass{article}
\usepackage{times}
\usepackage{mathptmx}
\begin{document}
Test
\end{document}
""",
        "package_load_order": r"""
\documentclass{article}
\usepackage{hyperref}
\usepackage{cleveref}
\begin{document}
Test
\end{document}
""",
    }


# ============================================================================
# Math Documents
# ============================================================================


@pytest.fixture
def latex_with_math() -> str:
    """
    Document with comprehensive mathematical content.

    Returns
    -------
    str
        LaTeX with various math environments
    """
    return r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}

\begin{document}

\section{Mathematical Equations}

\subsection{Inline Math}
Euler's formula: $e^{i\pi} + 1 = 0$

\subsection{Display Math}
\begin{equation}
    E = mc^2
\end{equation}

\subsection{Aligned Equations}
\begin{align}
    f(x) &= x^2 + 2x + 1 \\
    &= (x + 1)^2 \\
    &\geq 0
\end{align}

\subsection{Matrix}
\begin{equation}
    A = \begin{bmatrix}
        1 & 2 & 3 \\
        4 & 5 & 6 \\
        7 & 8 & 9
    \end{bmatrix}
\end{equation}

\subsection{Integral}
\begin{equation}
    \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
\end{equation}

\subsection{Summation}
\begin{equation}
    \sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
\end{equation}

\subsection{Theorem}
\begin{theorem}
Let $f: \mathbb{R} \to \mathbb{R}$ be a continuous function.
Then $f$ is integrable on any closed interval $[a,b]$.
\end{theorem}

\begin{proof}
Proof goes here.
\end{proof}

\end{document}
"""


# ============================================================================
# Graphics Documents
# ============================================================================


@pytest.fixture
def latex_with_graphics(tmp_path: Path) -> tuple[Path, Path]:
    """
    Document with graphics and image references.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    tuple[Path, Path]
        Tuple of (LaTeX file path, image file path)
    """
    # Create fake image
    img_file = tmp_path / "test_figure.png"
    # Minimal PNG header
    img_file.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    latex_file = tmp_path / "graphics.tex"
    latex_content = rf"""
\documentclass{{article}}
\usepackage{{graphicx}}
\graphicspath{{{{{tmp_path}/}}}}

\begin{{document}}

\section{{Figures}}

\begin{{figure}}[h]
\centering
\includegraphics[width=0.5\textwidth]{{test_figure.png}}
\caption{{Sample figure}}
\label{{fig:sample}}
\end{{figure}}

Reference to Figure~\ref{{fig:sample}}.

\begin{{figure}}[h]
\centering
\includegraphics[width=0.8\textwidth]{{test_figure.png}}
\caption{{Another figure}}
\label{{fig:another}}
\end{{figure}}

\end{{document}}
"""
    latex_file.write_text(latex_content)

    return latex_file, img_file


# ============================================================================
# Bibliography Documents
# ============================================================================


@pytest.fixture
def latex_with_bibliography(tmp_path: Path) -> tuple[Path, Path]:
    """
    Document with bibliography and citations.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    tuple[Path, Path]
        Tuple of (LaTeX file path, BibTeX file path)
    """
    # Create bibliography file
    bib_file = tmp_path / "references.bib"
    bib_content = """
@article{knuth1984,
    author = {Donald E. Knuth},
    title = {Literate Programming},
    journal = {The Computer Journal},
    volume = {27},
    number = {2},
    pages = {97--111},
    year = {1984}
}

@book{lamport1994,
    author = {Leslie Lamport},
    title = {LaTeX: A Document Preparation System},
    publisher = {Addison-Wesley},
    year = {1994},
    edition = {2nd}
}

@inproceedings{dijkstra1968,
    author = {Edsger W. Dijkstra},
    title = {Go To Statement Considered Harmful},
    booktitle = {Communications of the ACM},
    year = {1968},
    pages = {147--148}
}
"""
    bib_file.write_text(bib_content)

    # Create LaTeX file with citations
    latex_file = tmp_path / "bibliography.tex"
    latex_content = r"""
\documentclass{article}

\begin{document}

\section{Introduction}

According to Knuth \cite{knuth1984}, literate programming is...

Lamport \cite{lamport1994} developed LaTeX for document preparation.

Dijkstra \cite{dijkstra1968} famously criticized the goto statement.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""
    latex_file.write_text(latex_content)

    return latex_file, bib_file


# ============================================================================
# Performance Test Documents
# ============================================================================


@pytest.fixture
def large_document_generator():
    """
    Generator for large documents for performance testing.

    Returns
    -------
    callable
        Function that generates large documents
    """

    def generate_large_doc(num_chapters: int = 10, sections_per_chapter: int = 5) -> str:
        """
        Generate a large document.

        Parameters
        ----------
        num_chapters : int
            Number of chapters
        sections_per_chapter : int
            Sections per chapter

        Returns
        -------
        str
            Large LaTeX document
        """
        preamble = r"""
\documentclass[12pt]{report}
\usepackage{amsmath}
\usepackage{lipsum}

\begin{document}

\tableofcontents
\newpage
"""

        chapters = []
        for i in range(num_chapters):
            chapter_content = [f"\\chapter{{Chapter {i + 1}}}"]

            for j in range(sections_per_chapter):
                chapter_content.append(f"\\section{{Section {j + 1}}}")
                chapter_content.append(r"\lipsum[1-3]")

                # Add some math
                chapter_content.append(
                    f"""
\\begin{{equation}}
    x_{{{i + 1},{j + 1}}} = \\sum_{{k=1}}^{{10}} k^2
\\end{{equation}}
"""
                )

            chapters.append("\n".join(chapter_content))

        body = "\n\n".join(chapters)
        ending = r"\end{document}"

        return preamble + body + ending

    return generate_large_doc


# ============================================================================
# Edge Case Documents
# ============================================================================


@pytest.fixture
def latex_edge_cases() -> Dict[str, str]:
    """
    Collection of edge case LaTeX documents.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping edge case name to document
    """
    return {
        "empty_document": r"""
\documentclass{article}
\begin{document}
\end{document}
""",
        "only_whitespace": r"""
\documentclass{article}
\begin{document}




\end{document}
""",
        "deeply_nested_environments": r"""
\documentclass{article}
\begin{document}
\begin{itemize}
\item Level 1
    \begin{itemize}
    \item Level 2
        \begin{itemize}
        \item Level 3
            \begin{itemize}
            \item Level 4
            \end{itemize}
        \end{itemize}
    \end{itemize}
\end{itemize}
\end{document}
""",
        "many_packages": r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{setspace}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{multirow}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{algorithm}
\usepackage{algpseudocode}

\begin{document}
Using many packages.
\end{document}
""",
        "unicode_characters": r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\begin{document}

Greek: α β γ δ ε ζ η θ

Cyrillic: А Б В Г Д Е Ё Ж

Chinese: 你好世界

Math symbols: ∀ ∃ ∈ ∉ ∩ ∪ ⊂ ⊃

Arrows: → ← ↑ ↓ ↔ ⇒ ⇐

\end{document}
""",
        "verbatim_code": r"""
\documentclass{article}
\usepackage{listings}

\begin{document}

\section{Code Examples}

\begin{verbatim}
def hello_world():
    print("Hello, World!")
    return 42
\end{verbatim}

\begin{lstlisting}[language=Python]
class Example:
    def __init__(self, value):
        self.value = value
\end{lstlisting}

\end{document}
""",
    }


# ============================================================================
# Mock Compilers and Tools
# ============================================================================


@pytest.fixture
def mock_pdflatex():
    """
    Mock pdflatex compiler.

    Returns
    -------
    MagicMock
        Mock pdflatex with standard behavior
    """
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.version = "pdfTeX 3.14159265-2.6-1.40.21"
    mock.compile.return_value = {
        "success": True,
        "output_file": "document.pdf",
        "log_file": "document.log",
        "returncode": 0,
    }
    return mock


@pytest.fixture
def mock_chktex():
    """
    Mock chktex linter.

    Returns
    -------
    MagicMock
        Mock chktex with standard warnings
    """
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.check.return_value = {
        "warnings": [],
        "errors": [],
        "style_issues": [],
    }
    return mock


# ============================================================================
# Utility Functions
# ============================================================================


def create_latex_file(tmp_path: Path, name: str, content: str) -> Path:
    """
    Create a LaTeX file in temporary directory.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory
    name : str
        File name
    content : str
        LaTeX content

    Returns
    -------
    Path
        Path to created file
    """
    latex_file = tmp_path / name
    latex_file.write_text(content)
    return latex_file


def create_test_image(tmp_path: Path, name: str) -> Path:
    """
    Create a test image file.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory
    name : str
        Image file name

    Returns
    -------
    Path
        Path to created image
    """
    img_file = tmp_path / name

    # Minimal valid PNG
    png_data = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10"
        b"\x08\x02\x00\x00\x00\x90\x91h6"
        b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    img_file.write_bytes(png_data)
    return img_file
