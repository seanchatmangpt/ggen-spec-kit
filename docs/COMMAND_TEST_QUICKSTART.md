# Command Test Generation - Quick Start

**Constitutional Equation**: `test_commands_*.py = μ(cli-commands.ttl)`

## 🚀 5-Minute Quick Start

### Step 1: Create RDF Specification (2 min)

Create `ontology/cli-commands.ttl`:

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .

sk:MyCommand a sk:CLICommand ;
    sk:commandName "mycommand" ;
    sk:commandDescription "My awesome CLI command" ;
    sk:hasOption sk:VerboseOption .

sk:VerboseOption a sk:CommandOption ;
    sk:optionName "--verbose" ;
    sk:optionType "flag" ;
    sk:optionDescription "Show detailed output" .
```

### Step 2: Generate Tests (1 min)

```bash
ggen sync --config docs/ggen.toml
```

### Step 3: Run Tests (2 min)

```bash
pytest tests/e2e/test_commands_mycommand.py -v
```

**Done!** ✅ You now have 10+ comprehensive E2E tests.

---

## 📋 RDF Vocabulary Cheat Sheet

### Minimal Command

```turtle
sk:CmdName a sk:CLICommand ;
    sk:commandName "name" ;           # REQUIRED
    sk:commandDescription "Desc..." . # REQUIRED
```

### Add Argument

```turtle
sk:CmdName sk:hasArgument sk:ArgName .

sk:ArgName a sk:CommandArgument ;
    sk:argumentName "arg" ;           # REQUIRED
    sk:argumentType "string" ;        # REQUIRED: string|int|path
    sk:argumentRequired "true" ;      # REQUIRED: "true"|"false"
    sk:argumentPosition 0 .           # REQUIRED: 0, 1, 2...
```

### Add Option

```turtle
sk:CmdName sk:hasOption sk:OptName .

sk:OptName a sk:CommandOption ;
    sk:optionName "--option" ;        # REQUIRED
    sk:optionType "flag" .            # REQUIRED: flag|string|int|path
```

### Add Error Case

```turtle
sk:CmdName sk:hasErrorCase sk:ErrName .

sk:ErrName a sk:CommandErrorCase ;
    sk:errorId "error-id" ;           # REQUIRED
    sk:errorScenario "What..." ;      # REQUIRED
    sk:errorExpectedBehavior "How..." . # REQUIRED
```

---

## 🔧 Common Tasks

### Validate RDF

```bash
shacl validate \
  -s ontology/cli-command-shapes.ttl \
  -d ontology/cli-commands.ttl
```

### Generate All Tests

```bash
ggen sync --config docs/ggen.toml
```

### Run All E2E Tests

```bash
pytest tests/e2e/ -v -m e2e
```

### Check Coverage

```bash
pytest tests/e2e/ --cov=src/specify_cli/commands --cov-report=term-missing
```

---

## 📊 What Gets Generated

For each command, you automatically get:

✅ Help test (`test_mycommand_help`)
✅ Basic execution test
✅ Tests for each argument (N tests)
✅ Tests for each option (M tests)
✅ Tests for each error case (E tests)
✅ Keyboard interrupt test
✅ Unexpected error test
✅ JSON output test (if --json exists)
✅ Verbose output test (if --verbose exists)
✅ Full workflow test
✅ Environment variable test

**Total**: ~10-25 tests per command

---

## 🎯 Quality Standards

All generated tests have:

- ✅ 100% type hints
- ✅ NumPy-style docstrings
- ✅ `@pytest.mark.e2e` markers
- ✅ CliRunner E2E testing
- ✅ Proper mocking
- ✅ Exit code validation

---

## 🐛 Troubleshooting

### Tests don't generate

```bash
# Check RDF syntax
rapper -i turtle ontology/cli-commands.ttl

# Validate with SHACL
shacl validate -s ontology/cli-command-shapes.ttl -d ontology/cli-commands.ttl
```

### Tests fail to run

```bash
# Check imports
python -c "from specify_cli.app import app"

# Verify test collection
pytest tests/e2e/test_commands_*.py --collect-only
```

### Generated code has errors

```bash
# Format and check
ruff format tests/e2e/test_commands_*.py
ruff check tests/e2e/test_commands_*.py --show-source
```

---

## 📚 Full Documentation

- [Complete Guide](COMMAND_TEST_GENERATION.md) - 14KB, 478 lines
- [System Reference](COMMAND_TEST_SYSTEM.md) - 15KB, 516 lines
- [Example Spec](examples/cli-command-spec-example.ttl) - 9.8KB, 258 lines
- [Template README](../templates/README.md) - 11KB, 441 lines

---

## 💡 Examples

### Example 1: Command with Argument

```turtle
sk:InitCommand a sk:CLICommand ;
    sk:commandName "init" ;
    sk:commandDescription "Initialize project" ;
    sk:hasArgument sk:ProjectName .

sk:ProjectName a sk:CommandArgument ;
    sk:argumentName "project_name" ;
    sk:argumentType "string" ;
    sk:argumentRequired "true" ;
    sk:argumentPosition 0 ;
    sk:argumentDefaultTestValue "test-project" .
```

**Generates**: 12 tests including argument validation

### Example 2: Command with Multiple Options

```turtle
sk:CheckCommand a sk:CLICommand ;
    sk:commandName "check" ;
    sk:commandDescription "Check tools" ;
    sk:hasOption sk:VerboseOpt ;
    sk:hasOption sk:JsonOpt ;
    sk:hasOption sk:QuietOpt .

sk:VerboseOpt a sk:CommandOption ;
    sk:optionName "--verbose" ;
    sk:optionType "flag" .

sk:JsonOpt a sk:CommandOption ;
    sk:optionName "--json" ;
    sk:optionType "flag" .

sk:QuietOpt a sk:CommandOption ;
    sk:optionName "--quiet" ;
    sk:optionType "flag" .
```

**Generates**: 15 tests including option combinations

### Example 3: Command with Error Cases

```turtle
sk:InitCommand a sk:CLICommand ;
    sk:commandName "init" ;
    sk:commandDescription "Initialize project" ;
    sk:hasErrorCase sk:MissingNameError ;
    sk:hasErrorCase sk:DirExistsError .

sk:MissingNameError a sk:CommandErrorCase ;
    sk:errorId "missing-name" ;
    sk:errorScenario "No project name provided" ;
    sk:errorExpectedBehavior "Exit with error" ;
    sk:errorExpectedExitCode 1 ;
    sk:errorExpectedOutput "provide a project name" .

sk:DirExistsError a sk:CommandErrorCase ;
    sk:errorId "dir-exists" ;
    sk:errorScenario "Directory already exists" ;
    sk:errorExpectedBehavior "Exit with error" ;
    sk:errorExpectedExitCode 1 ;
    sk:errorExpectedOutput "already exists" .
```

**Generates**: 18 tests including comprehensive error handling

---

## ⚡ Pro Tips

### 1. Always Validate First

```bash
# Before generating
shacl validate -s ontology/cli-command-shapes.ttl -d ontology/cli-commands.ttl

# Then generate
ggen sync
```

### 2. Use Realistic Test Values

```turtle
# ✅ Good
sk:argumentDefaultTestValue "my-awesome-project" .

# ❌ Avoid
sk:argumentDefaultTestValue "test-value" .
```

### 3. Document Expected Behavior

```turtle
sk:optionExpectedBehavior "Shows version info and tool paths" .
sk:errorExpectedBehavior "Exit with code 1 and show installation instructions" .
```

### 4. Test Error Messages

```turtle
sk:errorExpectedOutput "required tool(s) missing" .
```

### 5. Provide Mock Setup for Complex Cases

```turtle
sk:errorMockSetup """
with patch('specify_cli.runtime.tools.which_tool') as mock:
    mock.return_value = None
""" .
```

---

## 🏆 Benefits

1. **Zero Manual Test Writing** - Define once in RDF, tests auto-generated
2. **100% Coverage** - Every argument, option, error case tested
3. **Single Source of Truth** - RDF spec is canonical
4. **Always In Sync** - Tests match spec by construction
5. **Lean Six Sigma Quality** - Production-ready tests guaranteed

---

## 📦 System Files

```
ggen-spec-kit/
├── templates/
│   └── command-test.tera          # Template (498 lines, 18KB)
├── sparql/
│   └── command-test-query.rq      # Query (135 lines, 4.7KB)
├── ontology/
│   └── cli-command-shapes.ttl     # Shapes (424 lines, 13KB)
├── docs/
│   ├── COMMAND_TEST_GENERATION.md # Guide (478 lines, 14KB)
│   ├── COMMAND_TEST_SYSTEM.md     # Reference (516 lines, 15KB)
│   └── examples/
│       └── cli-command-spec-example.ttl  # Example (258 lines, 9.8KB)
└── tests/e2e/
    └── test_commands_*.py         # Generated tests ✨
```

**Total**: 2,750+ lines of reusable infrastructure

---

**Constitutional Equation**: `test_commands_*.py = μ(cli-commands.ttl)`

*This is the μ transformation that proves tests are derivable from specifications.*
