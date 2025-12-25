"""
specify_cli.plugins.marketplace - Plugin Marketplace
===================================================

Plugin repository integration, installation, and management.

This module provides:
- Plugin repository integration
- Install/update/uninstall operations
- Dependency resolution
- Plugin store management
- Version management
- Plugin search and discovery

Architecture
-----------

    ┌────────────────────────────────────────────┐
    │  Plugin Marketplace (this module)          │
    │  • Repository integration                  │
    │  • Install/Update/Uninstall                │
    │  • Dependency resolution                   │
    │  • Version management                      │
    └────────────────────────────────────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │  Plugin Sources                            │
    │  • PyPI                                    │
    │  • Git repositories                        │
    │  • Local directories                       │
    │  • Plugin registry                         │
    └────────────────────────────────────────────┘

Usage
-----
    from specify_cli.plugins.marketplace import PluginMarketplace

    marketplace = PluginMarketplace()

    # Search plugins
    results = marketplace.search("github")

    # Install plugin
    marketplace.install("specify-plugin-github")

    # Update plugin
    marketplace.update("specify-plugin-github")

    # Uninstall plugin
    marketplace.uninstall("specify-plugin-github")

See Also
--------
- :mod:`specify_cli.plugins.system` : Plugin loading and management
- :mod:`specify_cli.plugins.api` : Plugin protocols
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from specify_cli.plugins.api import PluginError, PluginMetadata


@dataclass
class PluginSource:
    """Plugin source configuration.

    Attributes:
        name: Source name
        url: Source URL
        type: Source type (pypi, git, registry)
        enabled: Whether source is enabled
        priority: Source priority (higher = preferred)
    """

    name: str
    url: str
    type: str = "registry"  # pypi, git, registry
    enabled: bool = True
    priority: int = 100


@dataclass
class PluginPackage:
    """Plugin package information.

    Attributes:
        name: Plugin name
        version: Plugin version
        description: Short description
        author: Author name
        homepage: Homepage URL
        repository: Repository URL
        downloads: Download count
        rating: User rating (0-5)
        tags: Searchable tags
        checksum: Package checksum (SHA256)
    """

    name: str
    version: str
    description: str
    author: str = ""
    homepage: str = ""
    repository: str = ""
    downloads: int = 0
    rating: float = 0.0
    tags: list[str] | None = None
    checksum: str = ""

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.tags is None:
            self.tags = []


class PluginRegistry:
    """Plugin registry client.

    Interacts with the plugin registry API to search and fetch plugin metadata.

    Attributes:
        _base_url: Registry base URL
        _client: HTTP client
    """

    def __init__(self, base_url: str = "https://plugins.specify.dev") -> None:
        """Initialize plugin registry.

        Args:
            base_url: Registry base URL
        """
        self._base_url = base_url
        self._client = httpx.Client(timeout=30.0)

    def search(
        self, query: str, tags: list[str] | None = None, limit: int = 20
    ) -> list[PluginPackage]:
        """Search plugins in registry.

        Args:
            query: Search query
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of matching plugin packages
        """
        params: dict[str, Any] = {"q": query, "limit": limit}
        if tags:
            params["tags"] = ",".join(tags)

        try:
            response = self._client.get(f"{self._base_url}/api/v1/search", params=params)
            response.raise_for_status()

            results = response.json()
            return [PluginPackage(**pkg) for pkg in results.get("plugins", [])]

        except httpx.HTTPError:
            # Registry unavailable, return empty results
            return []

    def get_package_info(self, name: str, version: str | None = None) -> PluginPackage | None:
        """Get package information.

        Args:
            name: Plugin name
            version: Specific version (latest if None)

        Returns:
            Plugin package info or None if not found
        """
        url = f"{self._base_url}/api/v1/packages/{name}"
        if version:
            url += f"/{version}"

        try:
            response = self._client.get(url)
            response.raise_for_status()

            data = response.json()
            return PluginPackage(**data)

        except httpx.HTTPError:
            return None

    def get_versions(self, name: str) -> list[str]:
        """Get available versions for plugin.

        Args:
            name: Plugin name

        Returns:
            List of available versions
        """
        try:
            response = self._client.get(f"{self._base_url}/api/v1/packages/{name}/versions")
            response.raise_for_status()

            data = response.json()
            return data.get("versions", [])  # type: ignore[str]

        except httpx.HTTPError:
            return []

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()


class PluginInstaller:
    """Plugin installer.

    Handles plugin installation from various sources.

    Attributes:
        _install_dir: Plugin installation directory
    """

    def __init__(self, install_dir: Path | None = None) -> None:
        """Initialize plugin installer.

        Args:
            install_dir: Plugin installation directory
        """
        self._install_dir = install_dir or Path.home() / ".specify" / "plugins" / "installed"
        self._install_dir.mkdir(parents=True, exist_ok=True)

    def install_from_pypi(self, package_name: str, version: str | None = None) -> Path:
        """Install plugin from PyPI.

        Args:
            package_name: PyPI package name
            version: Specific version (latest if None)

        Returns:
            Path to installed plugin

        Raises:
            PluginError: If installation fails
        """
        try:
            # Build pip install command
            if version:
                package_spec = f"{package_name}=={version}"
            else:
                package_spec = package_name

            # Install to target directory
            result = subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--target",
                    str(self._install_dir),
                    package_spec,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if result.returncode != 0:
                raise PluginError(f"Failed to install {package_name}: {result.stderr}")

            return self._install_dir / package_name.replace("-", "_")

        except subprocess.CalledProcessError as e:
            raise PluginError(f"Failed to install {package_name}: {e.stderr}") from e

    def install_from_git(self, repo_url: str, ref: str | None = None) -> Path:
        """Install plugin from Git repository.

        Args:
            repo_url: Git repository URL
            ref: Git reference (branch, tag, commit)

        Returns:
            Path to installed plugin

        Raises:
            PluginError: If installation fails
        """
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Clone repository
                clone_cmd = ["git", "clone", repo_url, str(temp_path)]
                subprocess.run(clone_cmd, capture_output=True, text=True, check=True)

                # Checkout specific ref if provided
                if ref:
                    checkout_cmd = ["git", "checkout", ref]
                    subprocess.run(
                        checkout_cmd,
                        cwd=temp_path,
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                # Install from local directory
                return self.install_from_directory(temp_path)

        except subprocess.CalledProcessError as e:
            raise PluginError(f"Failed to install from {repo_url}: {e.stderr}") from e

    def install_from_directory(self, source_dir: Path) -> Path:
        """Install plugin from local directory.

        Args:
            source_dir: Source directory path

        Returns:
            Path to installed plugin

        Raises:
            PluginError: If installation fails
        """
        if not source_dir.exists():
            raise PluginError(f"Source directory does not exist: {source_dir}")

        # Look for setup.py or pyproject.toml
        has_setup = (source_dir / "setup.py").exists()
        has_pyproject = (source_dir / "pyproject.toml").exists()

        if has_setup or has_pyproject:
            # Install as package
            try:
                subprocess.run(
                    [
                        "uv",
                        "pip",
                        "install",
                        "--target",
                        str(self._install_dir),
                        str(source_dir),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Get package name from directory
                package_name = source_dir.name.replace("-", "_")
                return self._install_dir / package_name

            except subprocess.CalledProcessError as e:
                raise PluginError(f"Failed to install from {source_dir}: {e.stderr}") from e
        else:
            # Copy as standalone plugin
            plugin_name = source_dir.name
            target_dir = self._install_dir / plugin_name

            if target_dir.exists():
                shutil.rmtree(target_dir)

            shutil.copytree(source_dir, target_dir)
            return target_dir

    def uninstall(self, plugin_name: str) -> None:
        """Uninstall plugin.

        Args:
            plugin_name: Plugin name

        Raises:
            PluginError: If uninstallation fails
        """
        plugin_dir = self._install_dir / plugin_name.replace("-", "_")

        if not plugin_dir.exists():
            raise PluginError(f"Plugin {plugin_name} is not installed")

        try:
            shutil.rmtree(plugin_dir)
        except OSError as e:
            raise PluginError(f"Failed to uninstall {plugin_name}: {e}") from e

    def is_installed(self, plugin_name: str) -> bool:
        """Check if plugin is installed.

        Args:
            plugin_name: Plugin name

        Returns:
            True if installed
        """
        plugin_dir = self._install_dir / plugin_name.replace("-", "_")
        return plugin_dir.exists()

    def get_installed_version(self, plugin_name: str) -> str | None:
        """Get installed plugin version.

        Args:
            plugin_name: Plugin name

        Returns:
            Version string or None if not installed
        """
        if not self.is_installed(plugin_name):
            return None

        # Try to read version from metadata file
        plugin_dir = self._install_dir / plugin_name.replace("-", "_")
        metadata_file = plugin_dir / "metadata.json"

        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    return metadata.get("version")  # type: ignore[no-any-return]
            except (OSError, json.JSONDecodeError):
                pass

        return None


class PluginMarketplace:
    """Plugin marketplace for searching, installing, and managing plugins.

    Attributes:
        _registry: Plugin registry client
        _installer: Plugin installer
        _sources: Configured plugin sources
        _cache_dir: Cache directory for metadata
    """

    def __init__(
        self,
        install_dir: Path | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        """Initialize plugin marketplace.

        Args:
            install_dir: Plugin installation directory
            cache_dir: Cache directory
        """
        self._registry = PluginRegistry()
        self._installer = PluginInstaller(install_dir)
        self._sources: list[PluginSource] = [
            PluginSource(
                name="default",
                url="https://plugins.specify.dev",
                type="registry",
                priority=100,
            ),
            PluginSource(
                name="pypi",
                url="https://pypi.org",
                type="pypi",
                priority=50,
            ),
        ]
        self._cache_dir = cache_dir or Path.home() / ".specify" / "plugins" / "cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self, query: str, tags: list[str] | None = None, limit: int = 20
    ) -> list[PluginPackage]:
        """Search for plugins.

        Args:
            query: Search query
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of matching plugin packages
        """
        return self._registry.search(query, tags, limit)

    def install(
        self,
        plugin_spec: str,
        upgrade: bool = False,
        force: bool = False,
    ) -> PluginMetadata:
        """Install plugin.

        Args:
            plugin_spec: Plugin specification (name, name==version, git+url, path)
            upgrade: Upgrade if already installed
            force: Force reinstall

        Returns:
            Installed plugin metadata

        Raises:
            PluginError: If installation fails
        """
        # Parse plugin specification
        if plugin_spec.startswith("git+"):
            # Git repository
            repo_url = plugin_spec[4:]
            ref = None

            if "@" in repo_url:
                repo_url, ref = repo_url.split("@", 1)

            plugin_path = self._installer.install_from_git(repo_url, ref)

        elif Path(plugin_spec).exists():
            # Local directory
            plugin_path = self._installer.install_from_directory(Path(plugin_spec))

        else:
            # PyPI package or plugin name
            try:
                req = Requirement(plugin_spec)
                package_name = req.name
                version = None

                if req.specifier:
                    # Get specific version from specifier
                    spec_set = SpecifierSet(str(req.specifier))
                    versions = self._registry.get_versions(package_name)
                    matching_versions = [
                        v for v in versions if Version(v) in spec_set
                    ]
                    if matching_versions:
                        version = matching_versions[-1]  # Latest matching

            except Exception:
                # Treat as simple package name
                package_name = plugin_spec
                version = None

            # Check if already installed
            if self._installer.is_installed(package_name) and not upgrade and not force:
                raise PluginError(
                    f"Plugin {package_name} is already installed. "
                    "Use --upgrade to upgrade or --force to reinstall."
                )

            plugin_path = self._installer.install_from_pypi(package_name, version)

        # Load plugin metadata
        metadata = self._load_plugin_metadata(plugin_path)

        # Cache metadata
        self._cache_plugin_metadata(metadata)

        return metadata

    def update(self, plugin_name: str) -> PluginMetadata:
        """Update plugin to latest version.

        Args:
            plugin_name: Plugin name

        Returns:
            Updated plugin metadata

        Raises:
            PluginError: If update fails
        """
        return self.install(plugin_name, upgrade=True)

    def uninstall(self, plugin_name: str) -> None:
        """Uninstall plugin.

        Args:
            plugin_name: Plugin name

        Raises:
            PluginError: If uninstallation fails
        """
        self._installer.uninstall(plugin_name)

        # Remove cached metadata
        cache_file = self._cache_dir / f"{plugin_name}.json"
        if cache_file.exists():
            cache_file.unlink()

    def list_installed(self) -> list[PluginMetadata]:
        """List installed plugins.

        Returns:
            List of installed plugin metadata
        """
        installed = []

        for cache_file in self._cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    metadata = PluginMetadata(**data)
                    installed.append(metadata)
            except (OSError, json.JSONDecodeError, TypeError):
                pass

        return installed

    def get_plugin_info(self, plugin_name: str) -> PluginPackage | None:
        """Get plugin information from registry.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin package info or None if not found
        """
        return self._registry.get_package_info(plugin_name)

    def _load_plugin_metadata(self, plugin_path: Path) -> PluginMetadata:
        """Load plugin metadata from path.

        Args:
            plugin_path: Path to plugin

        Returns:
            Plugin metadata

        Raises:
            PluginError: If metadata cannot be loaded
        """
        # Look for metadata.json
        metadata_file = plugin_path / "metadata.json"

        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    data = json.load(f)
                    return PluginMetadata(**data)
            except (OSError, json.JSONDecodeError, TypeError) as e:
                raise PluginError(f"Failed to load plugin metadata: {e}") from e

        # Try to import and get metadata
        raise PluginError(f"No metadata found in {plugin_path}")

    def _cache_plugin_metadata(self, metadata: PluginMetadata) -> None:
        """Cache plugin metadata.

        Args:
            metadata: Plugin metadata
        """
        cache_file = self._cache_dir / f"{metadata.name}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(asdict(metadata), f, indent=2)
        except OSError:
            pass  # Ignore cache errors

    def close(self) -> None:
        """Close marketplace resources."""
        self._registry.close()


__all__ = [
    "PluginInstaller",
    "PluginMarketplace",
    "PluginPackage",
    "PluginRegistry",
    "PluginSource",
]
