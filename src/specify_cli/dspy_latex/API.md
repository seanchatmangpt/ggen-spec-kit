# DSPy LaTeX Optimizer - API Reference

Complete API documentation for the cognitive optimization layer.

## Table of Contents

- [Main Classes](#main-classes)
- [Data Classes](#data-classes)
- [Enumerations](#enumerations)
- [Optimization Strategies](#optimization-strategies)
- [Machine Learning Components](#machine-learning-components)
- [Usage Examples](#usage-examples)

---

## Main Classes

### LaTeXOptimizer

Main cognitive optimization orchestrator implementing the three-stage architecture.

```python
class LaTeXOptimizer:
    def __init__(
        self,
        optimization_level: OptimizationLevel = OptimizationLevel.MODERATE,
        enable_ml: bool = True,
        history_path: Path | None = None
    )
```

**Parameters:**
- `optimization_level` (OptimizationLevel): Desired optimization aggressiveness
- `enable_ml` (bool): Enable machine learning components
- `history_path` (Path, optional): Custom path for compilation history storage

**Methods:**

#### analyze_complexity()

Ψ₁ Perception: Analyze document complexity and characteristics.

```python
def analyze_complexity(self, latex_content: str) -> DocumentComplexity
```

**Parameters:**
- `latex_content` (str): LaTeX document content

**Returns:**
- `DocumentComplexity`: Detailed complexity analysis

**Example:**
```python
complexity = optimizer.analyze_complexity(latex_content)
print(f"Type: {complexity.document_type.value}")
print(f"Score: {complexity.complexity_score:.1f}")
print(f"Equations: {complexity.equation_count}")
```

#### select_strategies()

Ψ₂ Reasoning: Select optimal optimization strategies based on analysis.

```python
def select_strategies(
    self,
    complexity: DocumentComplexity,
    compilation_errors: list[str] | None = None
) -> list[str]
```

**Parameters:**
- `complexity` (DocumentComplexity): Document complexity from analyze_complexity()
- `compilation_errors` (list[str], optional): Recent compilation errors

**Returns:**
- `list[str]`: Ordered list of strategy names

**Example:**
```python
strategies = optimizer.select_strategies(
    complexity,
    compilation_errors=["Undefined control sequence"]
)
print(f"Recommended: {strategies}")
```

#### apply_optimization()

Ψ₃ Generation: Apply a specific optimization transformation.

```python
def apply_optimization(
    self,
    latex_content: str,
    strategy_name: str,
    complexity: DocumentComplexity
) -> OptimizationResult
```

**Parameters:**
- `latex_content` (str): Original LaTeX content
- `strategy_name` (str): Name of strategy to apply
- `complexity` (DocumentComplexity): Document complexity info

**Returns:**
- `OptimizationResult`: Result with optimized content and metadata

**Example:**
```python
result = optimizer.apply_optimization(
    latex_content,
    "package_consolidation",
    complexity
)
if result.success and result.validation_passed:
    print(f"Applied with {result.confidence:.0%} confidence")
```

#### optimize()

Full optimization pipeline: Ψ₁ → Ψ₂ → Ψ₃ with multiple iterations.

```python
def optimize(
    self,
    latex_content: str,
    max_iterations: int = 3
) -> tuple[str, OptimizationMetrics]
```

**Parameters:**
- `latex_content` (str): Original LaTeX content
- `max_iterations` (int): Maximum optimization iterations

**Returns:**
- `tuple[str, OptimizationMetrics]`: (optimized_content, metrics)

**Example:**
```python
optimized, metrics = optimizer.optimize(latex_content, max_iterations=5)
print(f"Applied {metrics.successful_optimizations} optimizations")
print(f"Strategies: {metrics.strategies_used}")
```

---

## Data Classes

### DocumentComplexity

Analysis of document complexity metrics.

```python
@dataclass
class DocumentComplexity:
    total_lines: int = 0
    equation_count: int = 0
    figure_count: int = 0
    table_count: int = 0
    citation_count: int = 0
    package_count: int = 0
    custom_macro_count: int = 0
    nesting_depth: int = 0
    float_count: int = 0
    cross_ref_count: int = 0
    complexity_score: float = 0.0
    document_type: DocumentType = DocumentType.UNKNOWN
    packages: list[str] = field(default_factory=list)
    redundant_packages: list[str] = field(default_factory=list)
    conflicting_packages: list[tuple[str, str]] = field(default_factory=list)
    sections_depth: dict[str, int] = field(default_factory=dict)
    problematic_constructs: list[str] = field(default_factory=list)
```

**Key Fields:**
- `complexity_score`: Overall complexity (0-100)
- `document_type`: Detected document type
- `redundant_packages`: List of duplicate packages
- `problematic_constructs`: List of problematic LaTeX constructs

### OptimizationResult

Result of applying an optimization strategy.

```python
@dataclass
class OptimizationResult:
    success: bool
    original_content: str
    optimized_content: str
    strategy_name: str
    changes_made: list[str] = field(default_factory=list)
    estimated_improvement: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""
    validation_passed: bool = False
```

**Key Fields:**
- `success`: Whether optimization succeeded
- `validation_passed`: Whether changes passed safety checks
- `confidence`: Confidence score (0.0-1.0)
- `changes_made`: List of changes applied

### CompilationRecord

Record of a LaTeX compilation attempt.

```python
@dataclass
class CompilationRecord:
    timestamp: datetime
    document_hash: str
    status: CompilationStatus
    compile_time: float
    error_messages: list[str] = field(default_factory=list)
    warning_messages: list[str] = field(default_factory=list)
    optimization_applied: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
```

### OptimizationMetrics

Comprehensive metrics for optimization operations.

```python
@dataclass
class OptimizationMetrics:
    total_optimizations: int = 0
    successful_optimizations: int = 0
    failed_optimizations: int = 0
    total_compile_time_saved: float = 0.0
    strategies_used: dict[str, int] = field(default_factory=dict)
    document_types_optimized: dict[DocumentType, int] = field(default_factory=dict)
    avg_confidence: float = 0.0
```

### StrategyPerformance

Performance metrics for an optimization strategy.

```python
@dataclass
class StrategyPerformance:
    strategy_name: str
    success_count: int = 0
    failure_count: int = 0
    avg_improvement: float = 0.0
    avg_compile_time: float = 0.0
    success_rate: float = 0.0
    last_used: datetime | None = None
    document_types: dict[DocumentType, int] = field(default_factory=dict)
```

---

## Enumerations

### DocumentType

LaTeX document types with different optimization needs.

```python
class DocumentType(str, Enum):
    ARTICLE = "article"         # Journal articles, papers
    BOOK = "book"              # Books with chapters
    REPORT = "report"          # Technical reports
    THESIS = "thesis"          # PhD theses, dissertations
    PRESENTATION = "presentation"  # Beamer slides
    LETTER = "letter"          # Formal letters
    UNKNOWN = "unknown"        # Unrecognized
```

### OptimizationLevel

Optimization aggressiveness levels.

```python
class OptimizationLevel(str, Enum):
    CONSERVATIVE = "conservative"  # Safe changes only
    MODERATE = "moderate"          # Standard optimizations
    AGGRESSIVE = "aggressive"      # All available optimizations
```

### CompilationStatus

Compilation result status.

```python
class CompilationStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    TIMEOUT = "timeout"
```

---

## Optimization Strategies

### Base Class: OptimizationStrategy

Abstract base class for all optimization strategies.

```python
class OptimizationStrategy(ABC):
    def __init__(self, name: str, description: str, risk_level: str = "low")

    @abstractmethod
    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply the optimization strategy."""
        pass

    @abstractmethod
    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze what changes would be made."""
        pass

    def record_performance(self, improvement: float) -> None:
        """Record performance for learning."""
        pass

    def get_avg_performance(self) -> float:
        """Get average performance improvement."""
        pass
```

### Concrete Strategies

#### EquationSimplificationStrategy

**Risk Level:** Low
**Best For:** Math-heavy documents

Simplifies equation formatting while preserving mathematical meaning.

```python
strategy = EquationSimplificationStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'displaymath_conversions': int,
#   'spacing_simplifications': int,
#   'nested_fraction_improvements': int,
#   'total_changes': int
# }
```

**Changes:**
- Converts `\[...\]` to `\begin{equation*}...\end{equation*}`
- Simplifies spacing (`\,+` → `\,`)
- Optimizes nested fractions

#### PackageConsolidationStrategy

**Risk Level:** Medium
**Best For:** All documents

Removes redundant and conflicting package imports.

```python
strategy = PackageConsolidationStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'obsolete_packages': int,
#   'duplicate_packages': int,
#   'conflicting_packages': int,
#   'total_removals': int
# }
```

**Changes:**
- Removes duplicate package loads
- Replaces obsolete packages (epsfig→graphicx, subfigure→subcaption)
- Detects conflicting packages

#### MacroExpansionStrategy

**Risk Level:** Medium
**Best For:** Documents with compilation errors

Expands problematic custom macros.

```python
strategy = MacroExpansionStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'total_macros': int,
#   'problematic_macros': int,
#   'expansion_candidates': int
# }
```

**Changes:**
- Expands macros containing fragile commands (`\cite`, `\ref`, `\label`, `\footnote`)

#### BibliographyOptimizationStrategy

**Risk Level:** Low
**Best For:** Documents with many citations

Optimizes bibliography and citation processing.

```python
strategy = BibliographyOptimizationStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'using_natbib': bool,
#   'using_biblatex': bool,
#   'citation_count': int,
#   'optimization_opportunities': int
# }
```

#### FloatPlacementStrategy

**Risk Level:** Low
**Best For:** Documents with many figures/tables

Optimizes figure and table placement directives.

```python
strategy = FloatPlacementStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'restrictive_h_placement': int,
#   'restrictive_t_placement': int,
#   'forced_H_placement': int,
#   'total_improvements': int
# }
```

**Changes:**
- `[h]` → `[htbp]` (more flexible)
- `[t]` → `[tbp]` (better placement)

#### GraphicsPathStrategy

**Risk Level:** Low
**Best For:** Documents with many images

Optimizes graphics path resolution and caching.

```python
strategy = GraphicsPathStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'has_graphicspath': bool,
#   'unique_graphics_paths': int,
#   'total_graphics': int,
#   'would_add_graphicspath': bool
# }
```

**Changes:**
- Adds `\graphicspath{}` directive
- Consolidates image paths

#### CrossReferenceValidationStrategy

**Risk Level:** Low
**Best For:** All documents

Validates and fixes cross-reference issues.

```python
strategy = CrossReferenceValidationStrategy()
analysis = strategy.analyze(latex_content)
# Returns: {
#   'total_labels': int,
#   'total_references': int,
#   'undefined_references': int,
#   'unused_labels': int
# }
```

---

## Machine Learning Components

### StrategyLearner

Learns optimal strategies from compilation history.

```python
class StrategyLearner:
    def __init__(self, history_path: Path | None = None)

    def record_compilation(self, record: CompilationRecord) -> None:
        """Record a compilation attempt."""

    def get_strategy_ranking(
        self,
        document_type: DocumentType,
        optimization_level: OptimizationLevel
    ) -> list[tuple[str, float]]:
        """Get ranked list of strategies."""

    def save_history(self) -> None:
        """Save compilation history to disk."""

    def learn_from_history(self) -> None:
        """Train ML models from compilation history."""
```

**Example:**
```python
learner = StrategyLearner()

# Record compilation
record = CompilationRecord(
    timestamp=datetime.now(),
    document_hash="abc123",
    status=CompilationStatus.SUCCESS,
    compile_time=1.5,
    optimization_applied="package_consolidation"
)
learner.record_compilation(record)

# Get rankings
rankings = learner.get_strategy_ranking(
    DocumentType.ARTICLE,
    OptimizationLevel.MODERATE
)
```

### PerformancePredictor

ML-based performance predictor for optimization strategies.

```python
class PerformancePredictor:
    def __init__(self)

    def train(
        self,
        training_data: list[tuple[DocumentComplexity, str, bool]]
    ) -> None:
        """Train the predictor on historical data."""

    def predict_success_probability(
        self,
        complexity: DocumentComplexity,
        strategy_name: str
    ) -> float:
        """Predict probability of strategy success."""
```

**Example:**
```python
predictor = PerformancePredictor()

# Train
training_data = [
    (complexity1, "equation_simplification", True),
    (complexity2, "package_consolidation", False),
]
predictor.train(training_data)

# Predict
prob = predictor.predict_success_probability(
    new_complexity,
    "equation_simplification"
)
print(f"Success probability: {prob:.1%}")
```

---

## Usage Examples

### Basic Optimization

```python
from specify_cli.dspy_latex import LaTeXOptimizer, OptimizationLevel

# Create optimizer
optimizer = LaTeXOptimizer(
    optimization_level=OptimizationLevel.MODERATE,
    enable_ml=True
)

# Optimize document
with open("paper.tex") as f:
    latex_content = f.read()

optimized, metrics = optimizer.optimize(latex_content, max_iterations=3)

# Save result
with open("paper_optimized.tex", "w") as f:
    f.write(optimized)

print(f"Applied {metrics.successful_optimizations} optimizations")
```

### Strategy-by-Strategy

```python
from specify_cli.dspy_latex import PackageConsolidationStrategy

# Create and analyze
strategy = PackageConsolidationStrategy()
analysis = strategy.analyze(latex_content)

print(f"Would remove {analysis['total_removals']} packages")

# Apply if acceptable
if analysis['total_removals'] > 0:
    complexity = optimizer.analyze_complexity(latex_content)
    result = optimizer.apply_optimization(
        latex_content,
        "package_consolidation",
        complexity
    )

    if result.success and result.validation_passed:
        latex_content = result.optimized_content
```

### Learning from Compilations

```python
import subprocess
from datetime import datetime
import hashlib

def compile_and_learn(tex_file: Path, optimizer: LaTeXOptimizer):
    """Compile and record results for ML."""
    content = tex_file.read_text()

    # Optimize
    optimized, _ = optimizer.optimize(content)

    # Compile
    optimized_file = tex_file.with_suffix(".optimized.tex")
    optimized_file.write_text(optimized)

    start_time = time.time()
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", optimized_file],
        capture_output=True
    )
    compile_time = time.time() - start_time

    # Record
    record = CompilationRecord(
        timestamp=datetime.now(),
        document_hash=hashlib.sha256(optimized.encode()).hexdigest(),
        status=CompilationStatus.SUCCESS if result.returncode == 0
                else CompilationStatus.ERROR,
        compile_time=compile_time,
        optimization_applied="full_pipeline"
    )

    optimizer.learner.record_compilation(record)

    return result.returncode == 0
```

### Custom Strategy

```python
from specify_cli.dspy_latex import OptimizationStrategy, DocumentComplexity

class RemoveCommentsStrategy(OptimizationStrategy):
    """Remove all comments from LaTeX."""

    def __init__(self):
        super().__init__(
            name="remove_comments",
            description="Remove all LaTeX comments",
            risk_level="low"
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        import re
        # Remove comments (simple version)
        return re.sub(r'(?<!\\)%.*$', '', latex_content, flags=re.MULTILINE)

    def analyze(self, latex_content: str) -> dict[str, Any]:
        import re
        comments = re.findall(r'(?<!\\)%.*$', latex_content, flags=re.MULTILINE)
        return {'comment_count': len(comments)}

# Register
optimizer.strategies["remove_comments"] = RemoveCommentsStrategy()
```

### Batch Processing

```python
from pathlib import Path

def optimize_directory(directory: Path):
    """Optimize all .tex files in a directory."""
    optimizer = LaTeXOptimizer(optimization_level=OptimizationLevel.MODERATE)

    for tex_file in directory.glob("**/*.tex"):
        print(f"Processing {tex_file}...")

        content = tex_file.read_text()
        optimized, metrics = optimizer.optimize(content)

        # Save to _opt.tex
        output_file = tex_file.with_stem(f"{tex_file.stem}_opt")
        output_file.write_text(optimized)

        print(f"  ✓ {metrics.successful_optimizations} optimizations")

# Use it
optimize_directory(Path("papers/"))
```

---

## Performance Characteristics

- **Complexity Analysis** (Ψ₁): < 100ms for most documents
- **Strategy Selection** (Ψ₂): < 50ms without ML, < 200ms with ML
- **Single Optimization** (Ψ₃): < 100ms per strategy
- **Full Pipeline**: < 1s for typical documents
- **Memory Usage**: < 50MB for documents up to 10,000 lines

## Safety and Validation

All optimizations go through validation:

1. **Structural Checks**
   - `\begin{}` and `\end{}` balance
   - Document class preservation
   - Document environment preservation

2. **Length Checks**
   - Optimized document shouldn't be < 70% of original

3. **Content Preservation**
   - Critical commands preserved
   - Document structure maintained

Failed validations automatically reject changes.

## Telemetry

All operations instrumented with OpenTelemetry:

- `latex_optimizer.complexity_score` (histogram)
- `latex_optimizer.optimization_time` (histogram)
- `latex_optimizer.optimizations_applied` (counter)
- `latex_optimizer.optimization_failed` (counter)
- `latex_optimizer.strategies_selected` (counter)

## Error Handling

All methods handle errors gracefully:

```python
result = optimizer.apply_optimization(content, strategy, complexity)

if not result.success:
    print(f"Optimization failed: {result.changes_made}")
elif not result.validation_passed:
    print(f"Validation failed - changes rejected")
    print(f"Confidence was: {result.confidence:.1%}")
else:
    print(f"Success! Confidence: {result.confidence:.1%}")
```

## Thread Safety

- `LaTeXOptimizer`: Thread-safe for read operations
- `StrategyLearner`: File I/O uses locking
- Parallel optimization: Create separate optimizer instances

## Versioning

Follows semantic versioning:
- Major: Breaking API changes
- Minor: New strategies or features
- Patch: Bug fixes and improvements
