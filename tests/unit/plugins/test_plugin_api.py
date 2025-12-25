"""
Tests for plugin API and protocols.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from specify_cli.plugins.api import (
    BasePlugin,
    CommandPlugin,
    PluginConfig,
    PluginDependency,
    PluginError,
    PluginMetadata,
    PluginPermission,
    PluginState,
    PluginType,
)


class TestPluginMetadata:
    """Tests for PluginMetadata."""

    def test_metadata_creation(self) -> None:
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            plugin_type=PluginType.COMMAND,
        )

        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin"
        assert metadata.plugin_type == PluginType.COMMAND

    def test_metadata_with_dependencies(self) -> None:
        """Test metadata with dependencies."""
        dep = PluginDependency(name="other-plugin", version_spec=">=1.0.0")

        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            dependencies=[dep],
        )

        assert len(metadata.dependencies) == 1
        assert metadata.dependencies[0].name == "other-plugin"


class TestPluginConfig:
    """Tests for PluginConfig."""

    def test_config_creation(self) -> None:
        """Test creating plugin configuration."""
        config = PluginConfig(
            enabled=True,
            auto_load=True,
            priority=100,
            config={"key": "value"},
        )

        assert config.enabled is True
        assert config.auto_load is True
        assert config.priority == 100
        assert config.config["key"] == "value"

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        config = PluginConfig()

        assert config.enabled is True
        assert config.auto_load is True
        assert config.priority == 100
        assert config.config == {}


class MockPlugin(BasePlugin):
    """Mock plugin for testing."""

    def metadata(self) -> PluginMetadata:
        """Return mock metadata."""
        return PluginMetadata(
            name="mock-plugin",
            version="1.0.0",
            description="Mock plugin for testing",
        )

    def _initialize_impl(self) -> None:
        """Initialize mock plugin."""
        pass


class TestBasePlugin:
    """Tests for BasePlugin."""

    def test_plugin_creation(self) -> None:
        """Test creating a plugin."""
        plugin = MockPlugin()

        assert plugin.state == PluginState.DISCOVERED
        assert plugin.config is None
        assert plugin.error is None

    def test_plugin_initialization(self) -> None:
        """Test plugin initialization."""
        plugin = MockPlugin()
        config = PluginConfig()

        plugin.initialize(config)

        assert plugin.state == PluginState.ACTIVE
        assert plugin.config == config

    def test_plugin_shutdown(self) -> None:
        """Test plugin shutdown."""
        plugin = MockPlugin()
        config = PluginConfig()

        plugin.initialize(config)
        plugin.shutdown()

        assert plugin.state == PluginState.UNLOADED

    def test_plugin_health_check(self) -> None:
        """Test plugin health check."""
        plugin = MockPlugin()
        config = PluginConfig()

        # Before initialization
        assert not plugin.health_check()

        # After initialization
        plugin.initialize(config)
        assert plugin.health_check()


class TestPluginTypes:
    """Tests for plugin type enumerations."""

    def test_plugin_types(self) -> None:
        """Test plugin type enumeration."""
        assert PluginType.COMMAND.value == "command"
        assert PluginType.INTEGRATION.value == "integration"
        assert PluginType.DATA_SOURCE.value == "data_source"
        assert PluginType.TRANSFORMER.value == "transformer"
        assert PluginType.REPORTER.value == "reporter"
        assert PluginType.HOOK.value == "hook"

    def test_plugin_states(self) -> None:
        """Test plugin state enumeration."""
        assert PluginState.DISCOVERED.value == "discovered"
        assert PluginState.LOADING.value == "loading"
        assert PluginState.LOADED.value == "loaded"
        assert PluginState.ACTIVE.value == "active"
        assert PluginState.ERROR.value == "error"
        assert PluginState.DISABLED.value == "disabled"


class TestPluginDependency:
    """Tests for PluginDependency."""

    def test_dependency_creation(self) -> None:
        """Test creating plugin dependency."""
        dep = PluginDependency(
            name="required-plugin",
            version_spec=">=1.0.0,<2.0.0",
            optional=False,
        )

        assert dep.name == "required-plugin"
        assert dep.version_spec == ">=1.0.0,<2.0.0"
        assert not dep.optional

    def test_optional_dependency(self) -> None:
        """Test optional dependency."""
        dep = PluginDependency(
            name="optional-plugin",
            version_spec="*",
            optional=True,
        )

        assert dep.optional
        assert dep.version_spec == "*"


class TestPluginPermission:
    """Tests for PluginPermission."""

    def test_permission_creation(self) -> None:
        """Test creating plugin permission."""
        perm = PluginPermission(
            name="test_permission",
            description="Test permission",
            required=True,
            dangerous=False,
        )

        assert perm.name == "test_permission"
        assert perm.description == "Test permission"
        assert perm.required
        assert not perm.dangerous

    def test_dangerous_permission(self) -> None:
        """Test dangerous permission."""
        perm = PluginPermission(
            name="dangerous_permission",
            description="Dangerous permission",
            required=False,
            dangerous=True,
        )

        assert perm.dangerous
