#!/usr/bin/env python3
"""
CLI Startup Profiler

Profiles specify CLI startup time using cProfile and pstats.
Identifies the top bottlenecks in CLI initialization.
"""

import cProfile
import pstats
import sys
from io import StringIO
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def profile_cli_startup():
    """Profile CLI startup with --help command."""
    profiler = cProfile.Profile()

    # Profile the import and execution
    profiler.enable()

    # Import and run the CLI with --help
    sys.argv = ["specify", "--help"]
    from specify_cli.app import main

    try:
        main()
    except SystemExit:
        pass  # --help exits with 0

    profiler.disable()

    # Save the profile
    profile_file = "/tmp/cli_startup.prof"
    profiler.dump_stats(profile_file)
    print(f"✓ Profile saved to: {profile_file}")

    # Analyze and print results
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)

    print("\n" + "=" * 80)
    print("TOP 30 SLOWEST FUNCTIONS (by cumulative time)")
    print("=" * 80)
    stats.sort_stats('cumulative')
    stats.print_stats(30)
    print(stream.getvalue())

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    print("\n" + "=" * 80)
    print("TOP 30 SLOWEST FUNCTIONS (by total time)")
    print("=" * 80)
    stats.sort_stats('tottime')
    stats.print_stats(30)
    print(stream.getvalue())

    # Get import time analysis
    print("\n" + "=" * 80)
    print("IMPORT BOTTLENECKS")
    print("=" * 80)
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')

    # Look for import-related functions
    import_funcs = []
    for func in stats.stats:
        func_name = func[2]
        if 'import' in func_name.lower() or '<module>' in func_name:
            cumtime = stats.stats[func][3]
            import_funcs.append((cumtime, func))

    import_funcs.sort(reverse=True)
    print("\nTop module imports by cumulative time:")
    for cumtime, func in import_funcs[:20]:
        print(f"  {cumtime:>8.3f}s  {func[0]}:{func[1]} ({func[2]})")

    return stats


if __name__ == "__main__":
    stats = profile_cli_startup()
