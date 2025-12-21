# Local ggen Build Documentation

## Overview

This document describes how to build and install the local Rust implementation of ggen v5.0.0 from the `tools/ggen-cli/` directory.

## Why Local Build?

The system-installed ggen 5.0.1 has API issues (missing sync subcommand). The local Rust implementation provides:
- Full API support including `sync` subcommand
- Direct integration with ggen-spec-kit workflows
- Proper μ₁-μ₅ transformation pipeline support

## Prerequisites

- Rust toolchain (rustup + cargo)
- Install if needed: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

## Build Process

### 1. Navigate to ggen-cli directory
```bash
cd /Users/sac/ggen-spec-kit/tools/ggen-cli
```

### 2. Build release binary
```bash
cargo build --release
```

**Expected:**
- Build time: ~3 minutes
- Binary location: `target/release/ggen`
- Binary size: ~23MB
- Warnings: 5 deprecation warnings (safe to ignore)

### 3. Install to PATH
```bash
# Create local bin directory
mkdir -p ~/.local/bin

# Copy binary
cp target/release/ggen ~/.local/bin/ggen

# Make executable
chmod +x ~/.local/bin/ggen
```

### 4. Verify installation
```bash
# Check version
ggen --version
# Expected: ggen 5.0.0

# Check help
ggen --help
# Should show sync and version subcommands

# Verify sync subcommand
ggen sync --help
# Should show sync options

# Check PATH
which ggen
# Expected: /Users/sac/.local/bin/ggen
```

## API Reference

### Sync Subcommand

```bash
ggen sync [OPTIONS]

Options:
  --from <FROM>      Source ontology directory
  --to <TO>          Target output directory
  --mode <MODE>      Sync mode: full, incremental, verify [default: full]
  --dry-run          Preview changes without writing
  --force            Override conflicts
  -v, --verbose      Verbose output
```

### Version Subcommand

```bash
ggen version
# Displays: ggen 5.0.0
```

## Implementation Details

### Architecture

The local ggen implementation:
- Built with Rust 1.91.1
- Uses oxigraph 0.5.3 for RDF storage
- Uses tera 1.20 for template rendering
- Includes SPARQL query support via spargebra 0.4.3

### Key Dependencies

```toml
ggen = "5.0.0"
ggen-cli-lib = "5.0.1"
ggen-config = "5.0.1"
ggen-core = "5.0.1"
clap = "4.5"          # CLI argument parsing
oxigraph = "0.5"      # RDF store
tera = "1.20"         # Template engine
```

### Transformation Pipeline

The sync command implements the constitutional equation:

```
spec.md = μ(feature.ttl)
```

Where μ consists of:
1. **μ₁ Normalize**: Load and validate Turtle files
2. **μ₂ Extract**: Execute SPARQL queries to extract classes/properties
3. **μ₃ Emit**: Render Tera templates with extracted data
4. **μ₄ Canonicalize**: Format and organize output
5. **μ₅ Receipt**: Generate SHA256 hash proofs

### Source Code Structure

```
tools/ggen-cli/
├── Cargo.toml           # Project metadata and dependencies
├── src/
│   └── main.rs         # Main CLI implementation
│       ├── load_ontology()      # μ₁ - Load TTL files
│       ├── extract_classes()    # μ₂ - SPARQL extraction
│       ├── extract_properties() # μ₂ - Property extraction
│       ├── render_templates()   # μ₃ - Tera rendering
│       └── map_xsd_type()       # Type mapping logic
└── target/
    └── release/
        └── ggen        # Built binary
```

## API Differences from Installed Version

### Local ggen v5.0.0 (This Build)
- ✅ `ggen sync` - Full support with all options
- ✅ `ggen version` - Version display
- ✅ `ggen --help` - Complete help text
- ✅ Proper RDF/Turtle file loading
- ✅ SPARQL query execution
- ✅ Tera template rendering

### System-Installed ggen 5.0.1
- ❌ `ggen sync` - Subcommand missing
- ✅ `ggen --version` - Works but incomplete API
- ⚠️  Limited functionality

## Troubleshooting

### Build Fails

**Issue:** Cargo build errors
```bash
# Update Rust toolchain
rustup update

# Clean and rebuild
cargo clean
cargo build --release
```

### Sync Command Not Found

**Issue:** `ggen sync` not recognized

**Solution:** Wrong ggen version in PATH
```bash
# Check which ggen is active
which ggen

# Should be: /Users/sac/.local/bin/ggen
# If not, check PATH order in shell config
```

### Binary Not Found After Install

**Issue:** `ggen: command not found`

**Solution:** Add ~/.local/bin to PATH
```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.zshrc
```

### Deprecation Warnings

**Issue:** 5 deprecation warnings during build

**Status:** Safe to ignore
- Warnings about `oxigraph::sparql::Query` deprecation
- Functionality still works correctly
- Will be addressed in future oxigraph updates

## Verification Checklist

After installation, verify all features work:

```bash
# ✓ Version check
ggen --version | grep "5.0.0"

# ✓ Help text
ggen --help | grep "sync"

# ✓ Sync subcommand help
ggen sync --help | grep "Source ontology"

# ✓ Binary location
which ggen | grep ".local/bin"

# ✓ Binary is executable
test -x ~/.local/bin/ggen && echo "Executable: OK"
```

## Integration with ggen-spec-kit

This local ggen build is ready for use with ggen-spec-kit workflows:

```bash
# Example: Sync ontology to docs
cd /Users/sac/ggen-spec-kit
ggen sync --from ontology/ --to docs/ --verbose

# Example: Dry run to preview
ggen sync --from memory/ --to docs/specs/ --dry-run

# Example: Force overwrite
ggen sync --from ontology/ --to docs/ --force
```

## Future Updates

To update the local build:

```bash
cd /Users/sac/ggen-spec-kit/tools/ggen-cli

# Pull latest changes
git pull

# Rebuild
cargo build --release

# Reinstall
cp target/release/ggen ~/.local/bin/ggen
```

## Notes

- Local version (5.0.0) has full API support
- Replaces broken installed version (5.0.1)
- Required for μ₁-μ₅ transformation implementation
- Ready for Weeks 2-4 ggen integration work
- Build time: ~3 minutes on first build
- Incremental builds: ~10 seconds

## Status

✅ **Ready for Production Use**
- Binary built successfully
- Installed to ~/.local/bin/ggen
- All subcommands verified working
- Documentation complete
