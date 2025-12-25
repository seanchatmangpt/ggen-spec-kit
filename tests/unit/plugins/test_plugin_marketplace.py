"""
Tests for plugin marketplace.
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from specify_cli.plugins.marketplace import (
    PluginInstaller,
    PluginMarketplace,
    PluginPackage,
    PluginRegistry,
    PluginSource,
)


class TestPluginSource:
    """Tests for PluginSource."""

    def test_source_creation(self) -> None:
        """Test creating plugin source."""
        source = PluginSource(
            name="test-source",
            url="https://example.com",
            type="registry",
            enabled=True,
            priority=100,
        )

        assert source.name == "test-source"
        assert source.url == "https://example.com"
        assert source.type == "registry"
        assert source.enabled is True
        assert source.priority == 100


class TestPluginPackage:
    """Tests for PluginPackage."""

    def test_package_creation(self) -> None:
        """Test creating plugin package."""
        package = PluginPackage(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin package",
            author="Test Author",
            tags=["test", "example"],
        )

        assert package.name == "test-plugin"
        assert package.version == "1.0.0"
        assert package.author == "Test Author"
        assert "test" in package.tags


class TestPluginRegistry:
    """Tests for PluginRegistry (marketplace)."""

    @patch("httpx.Client")
    def test_registry_creation(self, mock_client: MagicMock) -> None:
        """Test creating plugin registry."""
        registry = PluginRegistry(base_url="https://test.com")

        assert registry is not None

    @patch("httpx.Client")
    def test_search_plugins(self, mock_client: MagicMock) -> None:
        """Test searching plugins."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "plugins": [
                {
                    "name": "test-plugin",
                    "version": "1.0.0",
                    "description": "Test plugin",
                    "author": "Test",
                }
            ]
        }
        mock_client.return_value.get.return_value = mock_response

        registry = PluginRegistry()
        results = registry.search("test")

        assert len(results) == 1
        assert results[0].name == "test-plugin"

    @patch("httpx.Client")
    def test_get_package_info(self, mock_client: MagicMock) -> None:
        """Test getting package information."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Test",
        }
        mock_client.return_value.get.return_value = mock_response

        registry = PluginRegistry()
        info = registry.get_package_info("test-plugin")

        assert info is not None
        assert info.name == "test-plugin"


class TestPluginInstaller:
    """Tests for PluginInstaller."""

    def test_installer_creation(self, tmp_path: Path) -> None:
        """Test creating plugin installer."""
        installer = PluginInstaller(install_dir=tmp_path)

        assert installer is not None

    def test_is_installed(self, tmp_path: Path) -> None:
        """Test checking if plugin is installed."""
        installer = PluginInstaller(install_dir=tmp_path)

        # Not installed
        assert not installer.is_installed("test-plugin")

        # Create plugin directory to simulate installation
        (tmp_path / "test_plugin").mkdir()

        assert installer.is_installed("test-plugin")


class TestPluginMarketplace:
    """Tests for PluginMarketplace."""

    def test_marketplace_creation(self, tmp_path: Path) -> None:
        """Test creating plugin marketplace."""
        marketplace = PluginMarketplace(
            install_dir=tmp_path / "install",
            cache_dir=tmp_path / "cache",
        )

        assert marketplace is not None

    @patch("specify_cli.plugins.marketplace.PluginRegistry")
    def test_search(self, mock_registry_class: MagicMock, tmp_path: Path) -> None:
        """Test searching for plugins."""
        mock_registry = MagicMock()
        mock_registry.search.return_value = [
            PluginPackage(
                name="test-plugin",
                version="1.0.0",
                description="Test",
            )
        ]
        mock_registry_class.return_value = mock_registry

        marketplace = PluginMarketplace(install_dir=tmp_path)
        results = marketplace.search("test")

        assert len(results) == 1
        assert results[0].name == "test-plugin"

    def test_list_installed(self, tmp_path: Path) -> None:
        """Test listing installed plugins."""
        marketplace = PluginMarketplace(
            install_dir=tmp_path / "install",
            cache_dir=tmp_path / "cache",
        )

        # No plugins installed
        installed = marketplace.list_installed()

        assert isinstance(installed, list)
        assert len(installed) == 0
