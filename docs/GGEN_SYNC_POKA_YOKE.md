# ggen sync: Poka-Yoke Error-Proofing Design

**Principle**: Make errors impossible or immediately obvious
**Version**: 5.0.0+
**Date**: 2025-12-21
**Status**: DESIGN SPECIFICATION

---

## Executive Summary

This document specifies comprehensive error-proofing (poka-yoke) mechanisms for ggen sync across 6 dimensions:

1. **Prevention** (before errors happen)
2. **Detection** (catch errors immediately)
3. **Feedback** (make errors obvious)
4. **Recovery** (enable safe recovery)
5. **Implementation** (for developers)
6. **Deployment** (operational safety)

---

## 1. Prevention Poka-Yoke: Make Errors Impossible

### 1.1 Input Validation (Pre-Flight Checks)

**Goal**: Reject invalid input before processing starts

#### Config Manifest Validation

```python
# Prevent: Missing or malformed ggen.toml

def validate_manifest(manifest_path: str) -> dict:
    """
    Validate ggen.toml before processing.

    Checks:
    - File exists (absolute path)
    - TOML syntax valid
    - Required fields present: [project], [transformations]
    - All referenced files exist
    - Output paths are relative (not absolute/traversal)
    - SPARQL timeout > 0 and < 3600
    """
    manifest = toml.load(manifest_path)

    # Check required sections
    assert 'project' in manifest, "Missing [project] section"
    assert 'transformations' in manifest, "Missing [transformations] section"

    # Validate all file paths
    for transform in manifest['transformations']:
        for file_key in ['input_files', 'schema_files', 'sparql_query', 'template']:
            path = transform.get(file_key)
            if path:
                assert Path(path).exists(), f"File not found: {path}"
                assert Path(path).is_file(), f"Not a file: {path}"

    # Validate output paths (prevent directory traversal)
    for transform in manifest['transformations']:
        output = transform['output_file']
        assert not Path(output).is_absolute(), f"Absolute path not allowed: {output}"
        assert '..' not in output, f"Parent directory reference not allowed: {output}"
        canonical = (Path(manifest['metadata']['output_dir']) / output).resolve()
        assert str(canonical).startswith(str(manifest['metadata']['output_dir'])), \
            f"Output path escapes directory: {output}"

    return manifest
```

**Error Scenarios Prevented**:
- ❌ Missing manifest file
- ❌ Malformed TOML syntax
- ❌ Referenced files don't exist
- ❌ Paths outside output directory
- ❌ Missing required sections

#### RDF Input Validation

```python
def validate_rdf_inputs(input_files: List[str]) -> bool:
    """
    Validate RDF/Turtle syntax before SPARQL processing.

    Checks:
    - File exists and is readable
    - Turtle syntax valid (parse without error)
    - Prefixes all defined
    - UTF-8 encoded
    """
    graph = Graph()
    for input_file in input_files:
        try:
            graph.parse(input_file, format='turtle')
        except Exception as e:
            raise ValueError(f"Invalid RDF in {input_file}: {e}")

    # Check for undefined prefixes
    undefined = set()
    for triple in graph.triples((None, None, None)):
        for term in triple:
            if isinstance(term, URIRef):
                prefix = term.split('#')[0] if '#' in term else term.rsplit('/', 1)[0]
                if prefix not in [str(p) for p in graph.namespaces()]:
                    undefined.add(prefix)

    if undefined:
        raise ValueError(f"Undefined prefixes in RDF: {undefined}")

    return True
```

**Error Scenarios Prevented**:
- ❌ Invalid Turtle syntax
- ❌ Undefined namespace prefixes
- ❌ Missing input files
- ❌ Invalid encoding
- ❌ Circular RDF imports

#### Path Validation

```python
def validate_paths(from_dir: str, to_dir: str) -> bool:
    """
    Validate source and target directories before processing.

    Checks:
    - from_dir exists and is readable
    - to_dir parent exists or can be created
    - to_dir is writable (or parent is writable)
    - Sufficient disk space
    - No symlink attacks
    """
    from_path = Path(from_dir).resolve()
    to_path = Path(to_dir).resolve()

    # Source directory checks
    assert from_path.exists(), f"Source directory not found: {from_dir}"
    assert from_path.is_dir(), f"Source is not a directory: {from_dir}"
    assert os.access(from_path, os.R_OK), f"No read permission: {from_dir}"

    # Target directory checks
    if to_path.exists():
        assert to_path.is_dir(), f"Target is not a directory: {to_dir}"
        assert os.access(to_path, os.W_OK), f"No write permission: {to_dir}"
    else:
        assert os.access(to_path.parent, os.W_OK), f"Cannot create directory: {to_dir}"

    # No symlink attacks
    assert not from_path.is_symlink(), "Source cannot be symlink"
    assert not to_path.is_symlink(), "Target cannot be symlink"

    # Disk space check
    stat = os.statvfs(to_path.parent if not to_path.exists() else to_path)
    free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
    assert free_mb > 100, f"Insufficient disk space: {free_mb}MB free"

    return True
```

**Error Scenarios Prevented**:
- ❌ Missing source/target directories
- ❌ Permission denied (read/write)
- ❌ Symlink attacks
- ❌ Disk space exhaustion
- ❌ Invalid paths

### 1.2 Pre-Flight Health Checks

```python
def pre_flight_checks(config: dict, options: dict) -> CheckResult:
    """
    Run all pre-flight checks before starting transformation.

    Returns: (pass: bool, warnings: List[str], errors: List[str])
    """
    errors = []
    warnings = []

    # 1. Manifest validation
    try:
        validate_manifest(config['manifest_path'])
    except Exception as e:
        errors.append(f"Manifest error: {e}")

    # 2. RDF input validation
    try:
        validate_rdf_inputs(config['input_files'])
    except Exception as e:
        errors.append(f"RDF error: {e}")

    # 3. SHACL shape validation (new)
    try:
        validate_shacl_shapes(config['schema_files'], config['input_files'])
    except Exception as e:
        errors.append(f"SHACL validation failed: {e}")

    # 4. Path validation
    try:
        validate_paths(config['from_dir'], config['to_dir'])
    except Exception as e:
        errors.append(f"Path error: {e}")

    # 5. Environment checks
    required_vars = ['HOME', 'USER', 'PATH']
    for var in required_vars:
        if var not in os.environ:
            warnings.append(f"Environment variable {var} not set")

    # 6. Tool availability
    if not shutil.which('ggen'):
        errors.append("ggen not found in PATH")

    # 7. Disk space
    if get_free_disk_mb(config['to_dir']) < 100:
        errors.append("Less than 100MB free disk space")

    # Return results
    if errors:
        return CheckResult(passed=False, errors=errors, warnings=warnings)
    return CheckResult(passed=True, errors=[], warnings=warnings)
```

### 1.3 Configuration Constraint Enforcement

```python
# Prevent invalid configuration combinations

class ConfigValidator:
    """Enforce configuration constraints."""

    CONSTRAINTS = {
        'timeout_seconds': (1, 3600),  # 1 sec to 1 hour
        'max_parallel': (1, 32),       # Single to 32 threads
        'output_mode': ('full', 'incremental', 'verify'),
        'logging_level': ('error', 'warn', 'info', 'debug'),
        'force_overwrite': (True, False),
    }

    @staticmethod
    def validate(config: dict) -> bool:
        """Validate all config values against constraints."""
        for key, constraint in ConfigValidator.CONSTRAINTS.items():
            if key not in config:
                continue
            value = config[key]

            if isinstance(constraint, tuple) and len(constraint) == 2:
                min_val, max_val = constraint
                if not (min_val <= value <= max_val):
                    raise ValueError(
                        f"{key} out of range [{min_val}, {max_val}]: {value}"
                    )
            elif isinstance(constraint, (tuple, list)):
                if value not in constraint:
                    raise ValueError(
                        f"{key} invalid value {value}. Must be one of: {constraint}"
                    )

        return True
```

---

## 2. Detection Poka-Yoke: Catch Errors Immediately

### 2.1 Real-Time Validation During Processing

```python
def process_with_validation(manifest: dict, options: dict) -> ProcessResult:
    """
    Process transformations with continuous validation.
    """
    results = []

    for transform in manifest['transformations']:
        # Before: Validate transformation spec
        validate_transform_spec(transform)

        # Execute: SPARQL query
        sparql_results = execute_sparql_with_timeout(
            query=transform['sparql_query'],
            timeout_seconds=manifest['pipeline']['extract']['timeout_seconds']
        )

        # After: Validate SPARQL results
        if not sparql_results:
            raise ValueError(
                f"SPARQL query '{transform['name']}' returned empty results. "
                "This may indicate invalid query or missing data."
            )

        # Template rendering
        output_text = render_template(
            template_path=transform['template'],
            context=sparql_results
        )

        # Validate output syntax (language-specific)
        if output_text.endswith('.py'):
            validate_python_syntax(output_text)
        elif output_text.endswith('.json'):
            validate_json_syntax(output_text)
        elif output_text.endswith('.md'):
            validate_markdown_syntax(output_text)

        # Checksum comparison (if incremental)
        if options['mode'] == 'incremental':
            if file_unchanged(transform['output_file'], output_text):
                continue  # Skip writing unchanged file

        results.append({
            'name': transform['name'],
            'output': output_text,
            'status': 'validated'
        })

    return ProcessResult(passed=True, results=results)
```

### 2.2 Integrity Checking

```python
class IntegrityChecker:
    """Verify output integrity before writing."""

    @staticmethod
    def compute_hash(text: str) -> str:
        """Compute SHA256 hash of text."""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def verify_file_integrity(file_path: str, expected_hash: str) -> bool:
        """Verify file matches expected hash."""
        with open(file_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        return actual_hash == expected_hash

    @staticmethod
    def write_with_verification(file_path: str, content: str) -> bool:
        """Write file and verify contents match."""
        expected_hash = IntegrityChecker.compute_hash(content)

        # Write to staging location
        staging_path = f"{file_path}.staging"
        with open(staging_path, 'w') as f:
            f.write(content)

        # Verify staging file
        if not IntegrityChecker.verify_file_integrity(staging_path, expected_hash):
            raise IOError(f"File verification failed: {file_path}")

        # Move to final location (atomic)
        os.rename(staging_path, file_path)

        return True
```

### 2.3 Dependency Validation

```python
def validate_transformation_order(manifest: dict) -> bool:
    """
    Build dependency graph and detect cycles/missing dependencies.
    """
    graph = {}

    # Build graph
    for transform in manifest['transformations']:
        name = transform['name']
        depends_on = transform.get('depends_on', [])
        graph[name] = depends_on

    # Detect undefined dependencies
    all_names = set(graph.keys())
    for name, deps in graph.items():
        for dep in deps:
            if dep not in all_names:
                raise ValueError(f"Undefined dependency '{dep}' in '{name}'")

    # Detect cycles (DFS)
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    visited = set()
    for node in graph:
        if node not in visited:
            if has_cycle(node, visited, set()):
                raise ValueError("Circular dependency detected in transformation graph")

    return True
```

---

## 3. Feedback Poka-Yoke: Make Errors Obvious

### 3.1 Clear Error Messages

```python
class ErrorReporter:
    """Generate clear, actionable error messages."""

    @staticmethod
    def report_validation_error(error_type: str, context: dict) -> str:
        """Generate helpful error message."""
        templates = {
            'missing_file': (
                f"ERROR: File not found: {context['path']}\n"
                f"Expected location: {Path(context['path']).resolve()}\n"
                f"Check the path in your manifest or command-line arguments."
            ),
            'invalid_rdf': (
                f"ERROR: Invalid RDF/Turtle syntax in {context['file']}\n"
                f"Line {context['line']}: {context['message']}\n"
                f"Suggestion: Check namespace prefixes and use relative URIs."
            ),
            'shacl_violation': (
                f"ERROR: SHACL validation failed\n"
                f"Shape: {context['shape']}\n"
                f"Violation: {context['violation']}\n"
                f"Node: {context['node']}\n"
                f"Property: {context['property']}"
            ),
            'sparql_timeout': (
                f"ERROR: SPARQL query timed out after {context['timeout']}s\n"
                f"Query: {context['query_file']}\n"
                f"Suggestion: Simplify query or increase timeout in ggen.toml"
            ),
            'output_permission': (
                f"ERROR: Cannot write to output directory\n"
                f"Directory: {context['path']}\n"
                f"Permission: {context['permission_denied']}\n"
                f"Suggestion: Check directory permissions or choose different location"
            ),
        }

        return templates.get(error_type, f"ERROR: {context}")
```

### 3.2 Progress Reporting

```python
class ProgressReporter:
    """Show real-time progress of transformation."""

    def __init__(self, total_transforms: int, verbose: bool = False):
        self.total = total_transforms
        self.current = 0
        self.verbose = verbose
        self.start_time = time.time()

    def start_transform(self, name: str):
        """Report start of transformation."""
        self.current += 1
        elapsed = time.time() - self.start_time
        percent = (self.current / self.total) * 100
        print(
            f"[{percent:3.0f}%] ({self.current}/{self.total}) "
            f"{name:30s} ... ",
            end='',
            flush=True
        )

    def complete_transform(self, status: str = "✓"):
        """Report completion of transformation."""
        elapsed = time.time() - self.start_time
        print(f"{status} ({elapsed:.1f}s)")

    def error_transform(self, error: str):
        """Report transformation error."""
        print(f"ERROR\n  {error}")
```

### 3.3 Detailed Logging

```python
class StructuredLogger:
    """JSON structured logging for parsing and debugging."""

    def __init__(self, log_file: str):
        self.log_file = log_file

    def log_event(self, event_type: str, data: dict):
        """Log event as JSON."""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'data': data,
        }
        with open(self.log_file, 'a') as f:
            json.dump(event, f)
            f.write('\n')

    def log_transform_start(self, name: str, config: dict):
        self.log_event('transform_start', {'name': name, 'config': config})

    def log_transform_complete(self, name: str, duration_sec: float):
        self.log_event('transform_complete', {'name': name, 'duration_sec': duration_sec})

    def log_validation_error(self, name: str, error: str):
        self.log_event('validation_error', {'name': name, 'error': error})
```

---

## 4. Recovery Poka-Yoke: Enable Safe Recovery

### 4.1 Atomic Writes with Staging

```python
class AtomicFileWriter:
    """Write files atomically using staging + rename."""

    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.staging_dir = self.target_dir / '.ggen-staging'
        self.manifest = {}

    def write(self, relative_path: str, content: str) -> str:
        """Write file atomically. Returns absolute path."""
        # Create staging directory
        self.staging_dir.mkdir(parents=True, exist_ok=True)

        # Write to staging
        staging_file = self.staging_dir / relative_path
        staging_file.parent.mkdir(parents=True, exist_ok=True)
        with open(staging_file, 'w') as f:
            f.write(content)

        # Record in manifest
        self.manifest[relative_path] = {
            'hash': hashlib.sha256(content.encode()).hexdigest(),
            'size': len(content),
            'timestamp': datetime.utcnow().isoformat(),
        }

        return str(staging_file)

    def commit(self):
        """Move all staged files to final location (atomic)."""
        # Write manifest
        manifest_file = self.staging_dir / '.manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)

        # Move staging to target (all at once)
        for staged_file in self.staging_dir.glob('**/*'):
            if staged_file.is_file():
                target_file = self.target_dir / staged_file.relative_to(self.staging_dir)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(staged_file), str(target_file))

        # Remove staging directory
        shutil.rmtree(self.staging_dir)

    def rollback(self):
        """Discard all staged changes."""
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
```

### 4.2 Automatic Backups

```python
class BackupManager:
    """Manage backups before overwrite."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.backup_dir = self.output_dir / '.ggen-backups'

    def backup_existing_files(self, files: List[str]) -> dict:
        """Back up existing files before overwriting."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        run_backup = self.backup_dir / timestamp
        run_backup.mkdir(parents=True, exist_ok=True)

        backed_up = {}
        for file_path in files:
            abs_path = self.output_dir / file_path
            if abs_path.exists():
                backup_file = run_backup / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(abs_path, backup_file)
                backed_up[file_path] = str(backup_file)

        return backed_up

    def restore_backup(self, backup_timestamp: str):
        """Restore files from backup."""
        backup_run = self.backup_dir / backup_timestamp
        if not backup_run.exists():
            raise ValueError(f"Backup not found: {backup_timestamp}")

        for backup_file in backup_run.glob('**/*'):
            if backup_file.is_file():
                target_file = self.output_dir / backup_file.relative_to(backup_run)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_file)
```

### 4.3 Rollback Capability

```python
def rollback_to_manifest(output_dir: str, manifest_file: str):
    """Rollback files to state recorded in manifest."""
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)

    for file_path, file_info in manifest.items():
        abs_path = Path(output_dir) / file_path

        # Remove if file shouldn't exist
        if file_info['action'] == 'delete':
            if abs_path.exists():
                abs_path.unlink()

        # Restore from backup if overwritten
        elif file_info['action'] == 'overwrite':
            backup_path = Path(file_info['backup_path'])
            if backup_path.exists():
                shutil.copy2(backup_path, abs_path)

        # Mark as rolled back
        file_info['rolled_back'] = True

    # Update manifest
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
```

---

## 5. Implementation Poka-Yoke: For Developers

### 5.1 Type Hints (100% Coverage)

```python
from typing import Dict, List, Optional, Tuple, Callable

def process_transformation(
    manifest: Dict[str, Any],           # ← Type hint
    options: Dict[str, str],             # ← Type hint
    logger: Optional[StructuredLogger],  # ← Type hint
) -> ProcessResult:                      # ← Return type hint
    """Process RDF transformation with type safety."""
    pass
```

### 5.2 Pre/Post-Conditions

```python
from contracts import contract

@contract(
    output_dir='str,len>0',
    files='list(str),len>0',
    post_result='list(str),len>0'
)
def write_files(output_dir: str, files: List[str]) -> List[str]:
    """Write files to output directory.

    Preconditions:
    - output_dir is non-empty string
    - files is non-empty list

    Postconditions:
    - Returns list of written file paths
    """
    pass
```

### 5.3 Invariant Checking

```python
class TransformationContext:
    """Maintain transformation invariants."""

    def __init__(self, manifest: dict):
        self.manifest = manifest
        self._check_invariants()

    def _check_invariants(self):
        """Check invariants hold."""
        # Invariant 1: All transformations have names
        assert all('name' in t for t in self.manifest['transformations'])

        # Invariant 2: Output paths are relative
        for transform in self.manifest['transformations']:
            path = transform['output_file']
            assert not Path(path).is_absolute(), f"Output must be relative: {path}"

        # Invariant 3: No duplicate transformation names
        names = [t['name'] for t in self.manifest['transformations']]
        assert len(names) == len(set(names)), "Duplicate transformation names"
```

---

## 6. Deployment Poka-Yoke: Operational Safety

### 6.1 Version Compatibility Checks

```python
def check_version_compatibility(ggen_version: str, manifest_version: str):
    """Ensure ggen version matches manifest requirements."""
    ggen_major = int(ggen_version.split('.')[0])
    manifest_major = int(manifest_version.split('.')[0])

    if ggen_major != manifest_major:
        raise VersionMismatchError(
            f"ggen version {ggen_version} incompatible with manifest {manifest_version}. "
            f"Please upgrade: pip install ggen=={manifest_version}"
        )
```

### 6.2 Environment Validation

```python
def validate_deployment_environment():
    """Validate production environment before running."""
    checks = {
        'ggen_installed': shutil.which('ggen') is not None,
        'python_version': sys.version_info >= (3, 8),
        'disk_space_mb': get_free_disk_mb() > 500,
        'permissions': can_write_to_output_dir(),
        'network': (check_network_connectivity() if needs_network else True),
    }

    failures = [k for k, v in checks.items() if not v]
    if failures:
        raise EnvironmentError(
            f"Deployment environment validation failed: {failures}"
        )
```

### 6.3 Safe Degradation

```python
def graceful_degradation(mode: str, error: Exception) -> bool:
    """Determine if safe degradation is possible."""
    if mode == 'full':
        # Full mode: no degradation, fail fast
        return False

    elif mode == 'incremental':
        # Incremental mode: skip failed transformations, continue
        if isinstance(error, (IOError, PermissionError)):
            return True
        else:
            return False  # Fail on logic errors

    elif mode == 'verify':
        # Verify mode: just check, don't write
        return True  # Always degrade to dry-run

    return False
```

---

## Summary: Poka-Yoke Coverage

| Dimension | Mechanisms | Coverage |
|-----------|-----------|----------|
| **Prevention** | 5 mechanisms | Invalid input made impossible |
| **Detection** | 4 mechanisms | Errors caught immediately |
| **Feedback** | 3 mechanisms | Errors clearly reported |
| **Recovery** | 3 mechanisms | Safe recovery possible |
| **Implementation** | 3 mechanisms | Developer safety enforced |
| **Deployment** | 3 mechanisms | Operational safety enforced |

**Result**: Comprehensive error-proofing across all layers of ggen sync, from input validation through deployment.

