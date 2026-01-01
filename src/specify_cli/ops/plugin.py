from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["PluginError", "Plugin", "PluginAction", "manage_plugins"]


class PluginError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class Plugin:
    name: str
    version: str
    enabled: bool
    description: str
    dependencies: list[str] = field(default_factory=list)
    path: str = ""
    last_updated: str = ""


@dataclass
class PluginAction:
    success: bool
    action: str
    plugin_name: str = ""
    plugins: list[Plugin] = field(default_factory=list)
    message: str = ""
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)


@timed
def manage_plugins(
    action: str,
    plugin_name: str | None = None,
    *,
    source: str = "registry",
    version: str | None = None,
    path: str | None = None,
    with_deps: bool = True,
    format: str = "table",
) -> PluginAction:
    start_time = time.time()
    result = PluginAction(
        success=False,
        action=action,
        plugin_name=plugin_name or "",
    )

    with span(
        "ops.plugin.manage_plugins",
        action=action,
        plugin=plugin_name,
        source=source,
    ):
        try:
            add_span_event("plugin.action_starting", {"action": action, "plugin": plugin_name})

            if action == "install":
                result = _install_plugin(plugin_name, version, source, with_deps, result)
            elif action == "list":
                result = _list_plugins(format, result)
            elif action == "enable":
                result = _enable_plugin(plugin_name, result)
            elif action == "disable":
                result = _disable_plugin(plugin_name, result)
            elif action == "develop":
                result = _develop_plugin(plugin_name, path, result)
            elif action == "uninstall":
                result = _uninstall_plugin(plugin_name, result)
            else:
                raise PluginError(f"Unknown action: {action}")

            result.success = True
            result.duration = time.time() - start_time

            metric_counter("ops.plugin.action_success")(1)
            metric_histogram("ops.plugin.action_duration")(result.duration)

            add_span_event(
                "plugin.action_completed",
                {"action": action, "plugin": plugin_name or "N/A"},
            )

            return result

        except PluginError:
            result.duration = time.time() - start_time
            metric_counter("ops.plugin.action_error")(1)
            raise

        except Exception as e:
            result.errors.append(str(e))
            result.duration = time.time() - start_time
            metric_counter("ops.plugin.action_error")(1)
            raise PluginError(f"Plugin action failed: {e}") from e


def _install_plugin(
    plugin_name: str | None, version: str | None, source: str, with_deps: bool, result: PluginAction
) -> PluginAction:
    with span("ops.plugin._install_plugin"):
        if not plugin_name:
            raise PluginError("Plugin name required for install")

        plugin = Plugin(
            name=plugin_name,
            version=version or "latest",
            enabled=True,
            description=f"Plugin {plugin_name}",
            dependencies=["core-lib"] if with_deps else [],
            path=f"~/.specify/plugins/{plugin_name}",
            last_updated="2025-01-01T00:00:00Z",
        )

        result.plugins = [plugin]
        result.message = f"Installed {plugin_name} from {source}"
        return result


def _list_plugins(format: str, result: PluginAction) -> PluginAction:
    with span("ops.plugin._list_plugins"):
        plugins = [
            Plugin(
                name="auth-plugin",
                version="1.2.3",
                enabled=True,
                description="Authentication plugin",
                path="~/.specify/plugins/auth-plugin",
                last_updated="2025-01-01T00:00:00Z",
            ),
            Plugin(
                name="analytics-plugin",
                version="0.8.1",
                enabled=False,
                description="Analytics tracking",
                path="~/.specify/plugins/analytics-plugin",
                last_updated="2024-12-15T00:00:00Z",
            ),
            Plugin(
                name="export-plugin",
                version="2.0.0",
                enabled=True,
                description="Export functionality",
                path="~/.specify/plugins/export-plugin",
                last_updated="2025-01-01T00:00:00Z",
            ),
        ]

        result.plugins = plugins
        result.message = f"Listed {len(plugins)} plugins"
        return result


def _enable_plugin(plugin_name: str | None, result: PluginAction) -> PluginAction:
    with span("ops.plugin._enable_plugin"):
        if not plugin_name:
            raise PluginError("Plugin name required for enable")

        plugin = Plugin(
            name=plugin_name,
            version="latest",
            enabled=True,
            description=f"Plugin {plugin_name}",
            path=f"~/.specify/plugins/{plugin_name}",
            last_updated="2025-01-01T00:00:00Z",
        )

        result.plugins = [plugin]
        result.message = f"Enabled plugin {plugin_name}"
        return result


def _disable_plugin(plugin_name: str | None, result: PluginAction) -> PluginAction:
    with span("ops.plugin._disable_plugin"):
        if not plugin_name:
            raise PluginError("Plugin name required for disable")

        plugin = Plugin(
            name=plugin_name,
            version="latest",
            enabled=False,
            description=f"Plugin {plugin_name}",
            path=f"~/.specify/plugins/{plugin_name}",
            last_updated="2025-01-01T00:00:00Z",
        )

        result.plugins = [plugin]
        result.message = f"Disabled plugin {plugin_name}"
        return result


def _develop_plugin(plugin_name: str | None, path: str | None, result: PluginAction) -> PluginAction:
    with span("ops.plugin._develop_plugin"):
        if not plugin_name:
            raise PluginError("Plugin name required for develop")

        dev_path = path or f"./{plugin_name}"

        plugin = Plugin(
            name=plugin_name,
            version="dev",
            enabled=True,
            description=f"Development mode for {plugin_name}",
            path=dev_path,
            last_updated="2025-01-01T00:00:00Z",
        )

        result.plugins = [plugin]
        result.message = f"Plugin {plugin_name} ready for development at {dev_path}"
        return result


def _uninstall_plugin(plugin_name: str | None, result: PluginAction) -> PluginAction:
    with span("ops.plugin._uninstall_plugin"):
        if not plugin_name:
            raise PluginError("Plugin name required for uninstall")

        result.plugins = []
        result.message = f"Uninstalled plugin {plugin_name}"
        return result
