# Quick Start: DSPy LaTeX Testing

Fast reference guide for using the DSPy LaTeX test suite.

## 🚀 Quick Commands

```bash
# Run all tests
pytest tests/unit/test_dspy_latex_processor.py \
       tests/integration/test_dspy_latex_compiler.py \
       tests/e2e/test_dspy_latex_pipeline.py -v

# Run with coverage
pytest tests/ -k "dspy_latex" --cov=src/specify_cli/dspy_latex --cov-report=term

# Run specific test class
pytest tests/unit/test_dspy_latex_processor.py::TestLaTeXParser -v

# Run single test
pytest tests/unit/test_dspy_latex_processor.py::TestLaTeXParser::test_parse_simple_document -v
```

## 📁 File Organization

```
tests/
├── unit/test_dspy_latex_processor.py      # Parser, validator, optimizer tests
├── integration/test_dspy_latex_compiler.py # Pipeline, recovery, caching tests
├── e2e/test_dspy_latex_pipeline.py        # Full workflow tests
└── fixtures/
    ├── latex_samples.py                   # Test data
    ├── latex_test_utils.py                # Helper functions
    ├── README_DSPY_LATEX_TESTS.md         # Full documentation
    └── QUICK_START_TESTING.md             # This file
```

## 🧪 Using Fixtures

### Simple Documents

```python
def test_my_feature(simple_latex: str):
    """Test using simple LaTeX fixture."""
    result = my_function(simple_latex)
    assert result is not None
```

### Complex Documents

```python
def test_thesis_compilation(complex_thesis: str):
    """Test using complex thesis fixture."""
    compiler = PDFCompiler()
    result = compiler.compile(complex_thesis)
    assert result.success
```

### Error Documents

```python
def test_error_handling(latex_syntax_errors: Dict[str, str]):
    """Test using error document fixtures."""
    missing_brace_doc = latex_syntax_errors["missing_brace"]
    validator = LaTeXValidator()
    result = validator.validate(missing_brace_doc)
    assert not result.valid
```

## 🛠️ Using Utilities

### Validation

```python
from tests.fixtures.latex_test_utils import validate_latex_syntax

def test_validation():
    content = r"\documentclass{article}\begin{document}Test\end{document}"
    result = validate_latex_syntax(content)
    assert result.valid
```

### Performance Measurement

```python
from tests.fixtures.latex_test_utils import PerformanceTimer

def test_performance():
    with PerformanceTimer() as timer:
        # Your code here
        result = compile_latex(document)

    assert timer.duration_ms < 2000  # Under 2 seconds
```

### PDF Verification

```python
from tests.fixtures.latex_test_utils import verify_pdf_exists, assess_pdf_quality

def test_pdf_output(tmp_path):
    pdf_path = tmp_path / "output.pdf"
    # Generate PDF...

    assert verify_pdf_exists(pdf_path)
    quality = assess_pdf_quality(pdf_path)
    assert quality.quality_score > 0.9
```

### Mock DSPy Results

```python
from tests.fixtures.latex_test_utils import create_mock_dspy_optimization_result

def test_optimization():
    mock_result = create_mock_dspy_optimization_result(
        optimized_content="optimized latex",
        improvement_score=0.85
    )
    # Use mock_result in your test
```

## 📊 Common Test Patterns

### Unit Test Pattern

```python
class TestLaTeXParser:
    """Tests for LaTeX parser."""

    def test_parse_document(self, simple_latex: str):
        """Test parsing a simple document."""
        parser = LaTeXParser()
        result = parser.parse(simple_latex)

        assert result is not None
        assert "documentclass" in result
        assert result["documentclass"] == "article"
```

### Integration Test Pattern

```python
@pytest.mark.integration
class TestCompilationPipeline:
    """Tests for compilation pipeline."""

    def test_full_pipeline(self, sample_thesis: Path):
        """Test complete compilation pipeline."""
        compiler = PDFCompiler()
        result = compiler.compile(sample_thesis)

        assert result.success
        assert result.pdf_path.exists()
        assert result.stages["compile"]["success"]
```

### E2E Test Pattern

```python
@pytest.mark.e2e
class TestCompleteWorkflow:
    """End-to-end workflow tests."""

    def test_thesis_workflow(self, phd_thesis_tex: Path):
        """Test complete thesis compilation workflow."""
        pipeline = LaTeXPipeline()
        result = pipeline.process(phd_thesis_tex)

        assert result["success"]
        assert result["output_pdf"].endswith(".pdf")
        assert result["total_duration_ms"] < 10000
```

## 🎯 Testing Checklist

When writing new tests:

- [ ] Test placed in correct file (unit/integration/e2e)
- [ ] Test has clear docstring
- [ ] Uses existing fixtures where possible
- [ ] Has 3-5 meaningful assertions
- [ ] Follows naming convention: `test_<feature>_<scenario>`
- [ ] Includes error cases
- [ ] Includes performance check (if applicable)
- [ ] Added to README if new category

## 🔍 Debugging Tests

### Run with verbose output
```bash
pytest tests/ -vv -s
```

### Run with pdb on failure
```bash
pytest tests/ --pdb
```

### Show print statements
```bash
pytest tests/ -s
```

### Run last failed tests only
```bash
pytest tests/ --lf
```

## 📈 Coverage Tips

### View coverage report
```bash
pytest tests/ --cov=src/specify_cli/dspy_latex --cov-report=html
open htmlcov/index.html
```

### Check coverage for specific file
```bash
pytest tests/ --cov=src/specify_cli/dspy_latex/processor.py --cov-report=term
```

### Show missing lines
```bash
pytest tests/ --cov=src/specify_cli/dspy_latex --cov-report=term-missing
```

## 🏷️ Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_parser():
    pass

@pytest.mark.integration
def test_pipeline():
    pass

@pytest.mark.e2e
def test_full_workflow():
    pass

@pytest.mark.slow
def test_large_document():
    pass
```

Run specific markers:
```bash
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## 💡 Pro Tips

1. **Use tmp_path fixture** for file operations:
   ```python
   def test_file_creation(tmp_path):
       test_file = tmp_path / "test.tex"
       test_file.write_text("content")
   ```

2. **Mock external dependencies**:
   ```python
   with patch("subprocess.run") as mock_run:
       mock_run.return_value.returncode = 0
       result = compile_latex(document)
   ```

3. **Use parametrize for multiple scenarios**:
   ```python
   @pytest.mark.parametrize("error_type,expected", [
       ("missing_brace", False),
       ("valid_doc", True),
   ])
   def test_validation(error_type, expected):
       pass
   ```

4. **Fixture composition**:
   ```python
   @pytest.fixture
   def compiled_pdf(simple_latex, compiler):
       return compiler.compile(simple_latex)
   ```

## 📚 Further Reading

- Full docs: `tests/fixtures/README_DSPY_LATEX_TESTS.md`
- Test summary: `/home/user/ggen-spec-kit/TEST_SUITE_SUMMARY.md`
- Pytest docs: https://docs.pytest.org/
- Project CLAUDE.md: `/home/user/ggen-spec-kit/CLAUDE.md`

## 🆘 Getting Help

1. Check README: `tests/fixtures/README_DSPY_LATEX_TESTS.md`
2. Review existing tests for patterns
3. Check fixture definitions in `latex_samples.py`
4. Use helper functions from `latex_test_utils.py`

---

**Quick Start Version:** 1.0.0
**Last Updated:** 2025-12-24
