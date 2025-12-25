"""
Advanced Cache Integration Examples
===================================

Demonstrates integrating advanced caching with existing spec-kit operations.

This module shows how to apply caching to:
1. ggen transformations (most expensive operation)
2. RDF parsing and validation
3. Tool availability checks
4. SPARQL query execution
5. File operations

Expected Performance Improvements:
- ggen sync: 2-10x speedup on repeated runs
- Tool checks: 50-100x speedup (< 1ms vs 50-100ms)
- RDF parsing: 5-20x speedup for large files
- SPARQL queries: 10-50x speedup for complex queries
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from specify_cli.core.advanced_cache import SmartCache, cached, get_global_cache

if TYPE_CHECKING:
    from collections.abc import Callable


# -----------------------------------------------------------------------------
# Example 1: Caching ggen Transformations
# -----------------------------------------------------------------------------


def cache_ggen_sync(project_path: Path) -> dict[str, Any]:
    """
    Cache ggen sync operations with dependency tracking.

    This example shows how to cache expensive ggen transformations
    with automatic invalidation when input files change.

    Parameters
    ----------
    project_path : Path
        Project root containing ggen.toml.

    Returns
    -------
    dict[str, Any]
        Transformation result.
    """
    from specify_cli.runtime.ggen import sync_specs

    cache = get_global_cache()

    # Find input files (RDF specs)
    input_files = list((project_path / "memory").glob("*.ttl"))
    input_files.extend(list((project_path / "ontology").glob("*.ttl")))

    # Generate cache key
    key = f"ggen:sync:{project_path}"

    def run_sync() -> dict[str, Any]:
        """Execute ggen sync."""
        start = time.time()
        success = sync_specs(project_path)
        duration = time.time() - start

        return {
            "success": success,
            "duration": duration,
            "timestamp": time.time(),
        }

    # Use cache with file dependencies and 5-minute TTL
    result = cache.get_or_compute(
        key=key,
        compute_fn=run_sync,
        dependencies=input_files,
        ttl=300,  # 5 minutes
        metadata={"operation": "ggen_sync", "project": str(project_path)},
    )

    return result


# -----------------------------------------------------------------------------
# Example 2: Caching Tool Availability Checks
# -----------------------------------------------------------------------------


@cached(ttl=600)  # Cache for 10 minutes
def check_tool_availability(tool: str) -> dict[str, Any]:
    """
    Cache tool availability checks.

    Tool availability rarely changes, so we can cache for longer periods.
    This dramatically speeds up repeated checks.

    Parameters
    ----------
    tool : str
        Tool name to check.

    Returns
    -------
    dict[str, Any]
        Tool availability info.
    """
    from specify_cli.runtime.tools import check_tool, which_tool

    start = time.time()
    available = check_tool(tool)
    path = which_tool(tool) if available else None
    duration = time.time() - start

    return {
        "tool": tool,
        "available": available,
        "path": str(path) if path else None,
        "check_duration": duration,
    }


# -----------------------------------------------------------------------------
# Example 3: Caching RDF Parsing
# -----------------------------------------------------------------------------


def cache_rdf_parsing(rdf_file: Path) -> dict[str, Any]:
    """
    Cache RDF parsing with dependency tracking.

    RDF parsing can be expensive for large files. Cache the parsed
    graph with automatic invalidation when file changes.

    Parameters
    ----------
    rdf_file : Path
        Path to RDF file.

    Returns
    -------
    dict[str, Any]
        Parsed RDF info.
    """
    cache = get_global_cache()
    key = f"rdf:parse:{rdf_file}"

    def parse_rdf() -> dict[str, Any]:
        """Parse RDF file."""
        try:
            from rdflib import Graph
        except ImportError:
            return {"success": False, "error": "rdflib not installed"}

        start = time.time()
        graph = Graph()
        graph.parse(str(rdf_file), format="turtle")
        duration = time.time() - start

        return {
            "success": True,
            "triples": len(graph),
            "duration": duration,
            "file": str(rdf_file),
        }

    # Cache with file dependency
    result = cache.get_or_compute(
        key=key,
        compute_fn=parse_rdf,
        dependencies=[rdf_file],
        ttl=3600,  # 1 hour
        metadata={"operation": "rdf_parse", "file": str(rdf_file)},
    )

    return result


# -----------------------------------------------------------------------------
# Example 4: Caching SPARQL Queries
# -----------------------------------------------------------------------------


def cache_sparql_query(
    rdf_content: str, query: str, query_name: str = "query"
) -> dict[str, Any]:
    """
    Cache SPARQL query results.

    SPARQL queries can be expensive. Cache results with content-based
    invalidation (when RDF content changes).

    Parameters
    ----------
    rdf_content : str
        RDF content in Turtle format.
    query : str
        SPARQL query.
    query_name : str
        Query identifier for cache key.

    Returns
    -------
    dict[str, Any]
        Query results.
    """
    import hashlib

    cache = get_global_cache()

    # Generate content hash for cache key
    content_hash = hashlib.sha256(
        rdf_content.encode(), usedforsecurity=False
    ).hexdigest()[:16]
    query_hash = hashlib.sha256(query.encode(), usedforsecurity=False).hexdigest()[:16]

    key = f"sparql:{query_name}:{content_hash}:{query_hash}"

    def execute_query() -> dict[str, Any]:
        """Execute SPARQL query."""
        try:
            from rdflib import Graph
        except ImportError:
            return {"success": False, "error": "rdflib not installed"}

        start = time.time()
        graph = Graph()
        graph.parse(data=rdf_content, format="turtle")
        results = list(graph.query(query))
        duration = time.time() - start

        return {
            "success": True,
            "results": len(results),
            "duration": duration,
        }

    # Cache with 1-hour TTL
    result = cache.get_or_compute(
        key=key,
        compute_fn=execute_query,
        ttl=3600,
        metadata={"operation": "sparql_query", "query": query_name},
    )

    return result


# -----------------------------------------------------------------------------
# Example 5: Caching File Operations
# -----------------------------------------------------------------------------


def cache_file_hash(file_path: Path) -> str:
    """
    Cache file hash computation with dependency tracking.

    File hashing can be expensive for large files. Cache with
    automatic invalidation when file changes.

    Parameters
    ----------
    file_path : Path
        Path to file.

    Returns
    -------
    str
        SHA256 hash of file.
    """
    cache = get_global_cache()
    key = f"file:hash:{file_path}"

    def compute_hash() -> str:
        """Compute file hash."""
        import hashlib

        sha256 = hashlib.sha256(usedforsecurity=False)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    # Cache with file dependency
    result = cache.get_or_compute(
        key=key,
        compute_fn=compute_hash,
        dependencies=[file_path],
        ttl=3600,
        metadata={"operation": "file_hash", "file": str(file_path)},
    )

    return result


# -----------------------------------------------------------------------------
# Example 6: Cache Monitoring and Statistics
# -----------------------------------------------------------------------------


def display_cache_stats() -> None:
    """Display comprehensive cache statistics."""
    cache = get_global_cache()
    stats = cache.get_stats()

    print("\n" + "=" * 60)
    print("ADVANCED CACHE STATISTICS")
    print("=" * 60)

    # Overall statistics
    print(f"\n📊 Overall Performance:")
    print(f"   Total requests:  {stats.total_requests}")
    print(f"   Cache hits:      {stats.l1_hits + stats.l2_hits}")
    print(f"   Cache misses:    {stats.misses}")
    print(f"   Hit rate:        {stats.hit_rate * 100:.1f}%")
    print(f"   Invalidations:   {stats.invalidations}")

    # L1 cache statistics
    print(f"\n💾 L1 Cache (Memory):")
    print(f"   Hits:            {stats.l1_hits}")
    print(f"   Hit rate:        {stats.l1_hit_rate * 100:.1f}%")
    print(f"   Size:            {stats.l1_size} entries")
    print(f"   Avg access time: {stats.avg_l1_time_ms:.3f}ms")

    # L2 cache statistics
    print(f"\n💿 L2 Cache (Disk):")
    print(f"   Hits:            {stats.l2_hits}")
    print(f"   Hit rate:        {stats.l2_hit_rate * 100:.1f}%")
    print(f"   Size:            {stats.l2_size} entries")
    print(f"   Disk usage:      {stats.l2_disk_bytes / 1024:.1f} KB")
    print(f"   Avg access time: {stats.avg_l2_time_ms:.3f}ms")

    # Computation statistics
    print(f"\n⚙️  Computation:")
    print(f"   Avg compute time: {stats.avg_compute_time_ms:.3f}ms")

    # Performance analysis
    if stats.avg_compute_time_ms > 0:
        l1_speedup = stats.avg_compute_time_ms / max(stats.avg_l1_time_ms, 0.001)
        l2_speedup = stats.avg_compute_time_ms / max(stats.avg_l2_time_ms, 0.001)

        print(f"\n🚀 Speedup Factors:")
        print(f"   L1 cache:        {l1_speedup:.1f}x faster")
        print(f"   L2 cache:        {l2_speedup:.1f}x faster")

    print("=" * 60)


# -----------------------------------------------------------------------------
# Example 7: Cache Invalidation Patterns
# -----------------------------------------------------------------------------


def invalidate_ggen_caches(project_path: Path) -> int:
    """
    Invalidate all ggen-related caches for a project.

    Useful when forcing a fresh build.

    Parameters
    ----------
    project_path : Path
        Project root.

    Returns
    -------
    int
        Number of cache entries invalidated.
    """
    from specify_cli.core.advanced_cache import invalidate_cache

    pattern = f"ggen:sync:{project_path}"
    count = invalidate_cache(pattern)

    print(f"Invalidated {count} ggen cache entries for {project_path}")
    return count


def invalidate_tool_caches() -> int:
    """
    Invalidate all tool availability caches.

    Useful after installing new tools.

    Returns
    -------
    int
        Number of cache entries invalidated.
    """
    from specify_cli.core.advanced_cache import invalidate_cache

    count = invalidate_cache("tool:")
    print(f"Invalidated {count} tool cache entries")
    return count


# -----------------------------------------------------------------------------
# Example 8: Custom Cache Configuration
# -----------------------------------------------------------------------------


def create_custom_cache() -> SmartCache:
    """
    Create custom cache with specific configuration.

    Returns
    -------
    SmartCache
        Configured cache instance.
    """
    cache = SmartCache(
        l1_size=256,  # Larger L1 cache
        l2_max_size_mb=1000,  # 1GB L2 cache
        enable_stats=True,
    )

    print("Created custom cache:")
    print(f"  L1 size: 256 entries")
    print(f"  L2 max size: 1000 MB")
    print(f"  Statistics: enabled")

    return cache


# -----------------------------------------------------------------------------
# Main Demo
# -----------------------------------------------------------------------------


def main() -> None:
    """Run integration examples."""
    print("\n" + "=" * 60)
    print("ADVANCED CACHE INTEGRATION EXAMPLES")
    print("=" * 60)

    # Example 1: Tool checks
    print("\n1. Caching tool availability checks...")
    for tool in ["git", "ggen", "python", "nonexistent"]:
        result = check_tool_availability(tool)
        print(f"   {tool}: {result['available']} ({result['check_duration']*1000:.2f}ms)")

    # Example 2: Repeated tool checks (should be cached)
    print("\n2. Repeated tool checks (cached)...")
    start = time.time()
    for _ in range(100):
        check_tool_availability("git")
    duration = time.time() - start
    print(f"   100 checks in {duration*1000:.2f}ms ({duration*10:.2f}ms per check)")

    # Example 3: Display statistics
    display_cache_stats()

    print("\n" + "=" * 60)
    print("INTEGRATION EXAMPLES COMPLETE")
    print("=" * 60)
    print("\nKey Integration Points:")
    print("✓ ggen transformations: cache with dependency tracking")
    print("✓ Tool checks: cache with long TTL (10 minutes)")
    print("✓ RDF parsing: cache with file dependency tracking")
    print("✓ SPARQL queries: cache with content-based keys")
    print("✓ File operations: cache with dependency tracking")
    print("\nNext Steps:")
    print("- Apply caching to runtime/ggen.py::sync_specs")
    print("- Apply caching to runtime/tools.py::check_tool")
    print("- Apply caching to ops layer for business logic")


if __name__ == "__main__":
    main()
