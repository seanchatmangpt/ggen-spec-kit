"""
Tests for plugin system (discovery, loading, lifecycle).
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from specify_cli.plugins.api import (
    BasePlugin,
    PluginConfig,
    PluginDependency,
    PluginDependencyError,
    PluginError,
    PluginInitError,
    PluginLoadError,
    PluginMetadata,
    PluginState,
    PluginType,
    PluginVersionError,
)
from specify_cli.plugins.system import (
    PluginLoader,
    PluginManager,
    PluginRegistry,
)


class TestPluginRegistry:
    """Tests for PluginRegistry."""

    def test_registry_creation(self) -> None:
        """Test creating plugin registry."""
        registry = PluginRegistry()

        assert len(registry.list_plugins()) == 0
        assert len(registry.list_loaded()) == 0

    def test_register_plugin(self) -> None:
        """Test registering a plugin."""
        registry = PluginRegistry()
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
        )

        registry.register(metadata)

        assert "test-plugin" in registry.list_plugins()
        assert registry.get_metadata("test-plugin") == metadata
        assert registry.get_state("test-plugin") == PluginState.DISCOVERED

    def test_unregister_plugin(self) -> None:
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
        )

        registry.register(metadata)
        registry.unregister("test-plugin")

        assert "test-plugin" not in registry.list_plugins()

    def test_set_loaded(self) -> None:
        """Test marking plugin as loaded."""
        registry = PluginRegistry()
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
        )

        registry.register(metadata)

        plugin = MagicMock()
        registry.set_loaded("test-plugin", plugin)

        assert registry.get_plugin("test-plugin") == plugin
        assert registry.get_state("test-plugin") == PluginState.LOADED


class MockTestPlugin(BasePlugin):
    """Mock plugin for testing."""

    def metadata(self) -> PluginMetadata:
        """Return mock metadata."""
        return PluginMetadata(
            name="mock-test-plugin",
            version="1.0.0",
            description="Mock plugin for testing",
        )

    def _initialize_impl(self) -> None:
        """Initialize mock plugin."""
        pass


class TestPluginLoader:
    """Tests for PluginLoader."""

    def test_loader_creation(self) -> None:
        """Test creating plugin loader."""
        loader = PluginLoader(cli_version="0.0.25")

        assert loader is not None

    def test_check_version_compatibility(self) -> None:
        """Test version compatibility checking."""
        loader = PluginLoader(cli_version="1.0.0")

        # Compatible version
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test",
            min_cli_version="0.5.0",
            max_cli_version="2.0.0",
        )

        assert loader.check_version_compatibility(metadata)

    def test_check_version_incompatible(self) -> None:
        """Test incompatible version detection."""
        loader = PluginLoader(cli_version="1.0.0")

        # Incompatible version (too old)
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test",
            min_cli_version="2.0.0",
            max_cli_version="3.0.0",
        )

        with pytest.raises(PluginVersionError):
            loader.check_version_compatibility(metadata)

    def test_load_from_entry_point_invalid(self) -> None:
        """Test loading from invalid entry point."""
        loader = PluginLoader()

        with pytest.raises(PluginLoadError):
            loader.load_from_entry_point("invalid:entry:point")


class TestPluginManager:
    """Tests for PluginManager."""

    def test_manager_creation(self) -> None:
        """Test creating plugin manager."""
        manager = PluginManager()

        assert manager is not None

    def test_discover_plugins(self) -> None:
        """Test plugin discovery."""
        manager = PluginManager()

        # Discover plugins (may find none if no plugins installed)
        discovered = manager.discover_plugins()

        assert isinstance(discovered, list)

    def test_list_plugins(self) -> None:
        """Test listing plugins."""
        manager = PluginManager()
        manager.discover_plugins()

        plugins = manager.list_plugins()

        assert isinstance(plugins, list)

    def test_load_plugin_not_found(self) -> None:
        """Test loading non-existent plugin."""
        manager = PluginManager()

        with pytest.raises(PluginLoadError):
            manager.load_plugin("non-existent-plugin")

    def test_unload_plugin_not_loaded(self) -> None:
        """Test unloading non-loaded plugin."""
        manager = PluginManager()

        with pytest.raises(PluginError):
            manager.unload_plugin("non-existent-plugin")

    def test_get_plugin(self) -> None:
        """Test getting plugin instance."""
        manager = PluginManager()

        # Non-existent plugin
        assert manager.get_plugin("non-existent") is None

    def test_register_hook(self) -> None:
        """Test registering hook handler."""
        manager = PluginManager()

        handler_called = False

        def hook_handler(**kwargs) -> None:
            nonlocal handler_called
            handler_called = True

        manager.register_hook("test_hook", hook_handler)

        # Call the hook
        manager._call_hook("test_hook")

        assert handler_called

    def test_enable_hot_reload(self) -> None:
        """Test enabling hot-reload."""
        manager = PluginManager()

        manager.enable_hot_reload()

        assert manager._hot_reload is True

        manager.disable_hot_reload()

        assert manager._hot_reload is False


class TestPluginDependencies:
    """Tests for plugin dependency resolution."""

    def test_dependency_graph(self) -> None:
        """Test dependency graph building."""
        registry = PluginRegistry()

        # Register plugin with dependency
        metadata = PluginMetadata(
            name="dependent-plugin",
            version="1.0.0",
            description="Depends on other plugin",
            dependencies=[
                PluginDependency(name="base-plugin", version_spec=">=1.0.0")
            ],
        )

        registry.register(metadata)

        deps = registry.get_dependencies("dependent-plugin")
        assert "base-plugin" in deps

    def test_missing_dependency(self) -> None:
        """Test missing dependency detection."""
        manager = PluginManager()

        # Create metadata with missing dependency
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test",
            dependencies=[
                PluginDependency(name="missing-plugin", version_spec="*", optional=False)
            ],
        )

        with pytest.raises(PluginDependencyError):
            manager._check_dependencies(metadata)

    def test_optional_dependency(self) -> None:
        """Test optional dependency handling."""
        manager = PluginManager()

        # Create metadata with optional dependency
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test",
            dependencies=[
                PluginDependency(name="optional-plugin", version_spec="*", optional=True)
            ],
        )

        # Should not raise even though dependency is missing
        manager._check_dependencies(metadata)
