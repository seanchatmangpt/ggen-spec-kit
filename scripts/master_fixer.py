#!/usr/bin/env python3
"""
Master Ruff Violation Fixer

Orchestrates all automated fixes in the optimal order and verifies results.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple


def run_command(cmd: list[str], description: str) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    print(f"\n{'=' * 80}")
    print(f"{description}")
    print(f"{'=' * 80}")
    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode, result.stdout, result.stderr


def get_violation_stats() -> Dict[str, int]:
    """Get current violation statistics."""
    result = subprocess.run(
        ['uv', 'run', 'ruff', 'check', 'src/specify_cli', '--output-format=json'],
        capture_output=True,
        text=True
    )

    violations = json.loads(result.stdout)

    # Count by code
    stats = {}
    for v in violations:
        code = v['code']
        stats[code] = stats.get(code, 0) + 1

    return stats


def print_violation_comparison(before: Dict[str, int], after: Dict[str, int]):
    """Print before/after violation comparison."""
    print("\n" + "=" * 80)
    print("VIOLATION REDUCTION REPORT")
    print("=" * 80)
    print(f"\n{'Rule':<12} {'Before':>10} {'After':>10} {'Reduction':>12} {'%':>8}")
    print("-" * 80)

    all_codes = sorted(set(list(before.keys()) + list(after.keys())))

    total_before = sum(before.values())
    total_after = sum(after.values())

    for code in all_codes:
        before_count = before.get(code, 0)
        after_count = after.get(code, 0)
        reduction = before_count - after_count

        if reduction != 0:
            pct = (reduction / before_count * 100) if before_count > 0 else 0
            print(f"{code:<12} {before_count:>10} {after_count:>10} {reduction:>12} {pct:>7.1f}%")

    print("-" * 80)
    total_reduction = total_before - total_after
    total_pct = (total_reduction / total_before * 100) if total_before > 0 else 0
    print(f"{'TOTAL':<12} {total_before:>10} {total_after:>10} {total_reduction:>12} {total_pct:>7.1f}%")
    print("=" * 80)


def main():
    """Execute all automated fixes."""
    print("=" * 80)
    print("MASTER RUFF VIOLATION FIXER")
    print("=" * 80)

    # Get initial stats
    print("\nPhase 1: Analyzing current violations...")
    before_stats = get_violation_stats()
    total_before = sum(before_stats.values())
    print(f"\nTotal violations: {total_before}")

    # Show top 10
    print("\nTop 10 violations:")
    sorted_violations = sorted(before_stats.items(), key=lambda x: x[1], reverse=True)
    for code, count in sorted_violations[:10]:
        print(f"  {code}: {count}")

    # Phase 2: Run auto-fixes (ruff --fix first)
    print("\n" + "=" * 80)
    print("Phase 2: Running ruff --fix (safe automated fixes)")
    print("=" * 80)

    run_command(
        ['uv', 'run', 'ruff', 'check', 'src/specify_cli', '--fix'],
        "Applying ruff's built-in fixes"
    )

    # Check stats after ruff --fix
    after_ruff_fix = get_violation_stats()
    ruff_fix_reduction = total_before - sum(after_ruff_fix.values())
    print(f"\n✓ Ruff --fix eliminated {ruff_fix_reduction} violations")

    # Phase 3: Run custom fixers
    print("\n" + "=" * 80)
    print("Phase 3: Running custom AST-based fixers")
    print("=" * 80)

    fixers = [
        (['python3', 'scripts/fix_undefined_names.py'], "Fix undefined names (F821)"),
        (['python3', 'scripts/fix_raise_from.py'], "Fix raise-without-from (B904)"),
        (['python3', 'scripts/ast_violation_fixer.py'], "Fix multiple violation types"),
    ]

    for cmd, desc in fixers:
        if Path(cmd[1]).exists():
            run_command(cmd, desc)
        else:
            print(f"Skipping {desc} - script not found: {cmd[1]}")

    # Phase 4: Run ruff --fix again (cleanup)
    print("\n" + "=" * 80)
    print("Phase 4: Running ruff --fix again (cleanup)")
    print("=" * 80)

    run_command(
        ['uv', 'run', 'ruff', 'check', 'src/specify_cli', '--fix'],
        "Final cleanup pass"
    )

    # Get final stats
    print("\n" + "=" * 80)
    print("Phase 5: Final verification")
    print("=" * 80)

    after_stats = get_violation_stats()

    # Print comparison
    print_violation_comparison(before_stats, after_stats)

    # Run tests
    print("\n" + "=" * 80)
    print("Phase 6: Running tests to verify fixes")
    print("=" * 80)

    test_result, test_stdout, test_stderr = run_command(
        ['uv', 'run', 'pytest', 'tests/unit', '-q', '--tb=short'],
        "Running unit tests"
    )

    if test_result == 0:
        print("\n✓ All tests passed!")
    else:
        print("\n⚠ Some tests failed - manual review needed")

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    total_after = sum(after_stats.values())
    total_reduction = total_before - total_after
    reduction_pct = (total_reduction / total_before * 100) if total_before > 0 else 0

    print(f"""
Violations before:  {total_before}
Violations after:   {total_after}
Violations fixed:   {total_reduction}
Reduction:          {reduction_pct:.1f}%

Test status:        {'✓ PASSED' if test_result == 0 else '✗ FAILED'}
""")

    print("\nNext steps:")
    print("  1. Review changes: git diff")
    print("  2. Run full test suite: uv run pytest tests/")
    print("  3. Manual review of remaining violations:")
    print("     uv run ruff check src/specify_cli --statistics")

    if total_after > 0:
        print(f"\n  Remaining violations require manual review:")
        remaining_sorted = sorted(after_stats.items(), key=lambda x: x[1], reverse=True)
        for code, count in remaining_sorted[:5]:
            print(f"    - {code}: {count}")

    return 0 if test_result == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
