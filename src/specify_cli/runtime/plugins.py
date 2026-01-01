from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span


@dataclass
class PluginMetadata:
    name: str
    version: str
    author: str
    description: str
    hooks: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


class PluginHook(ABC):
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.handlers: list[Callable] = []

    def register_handler(self, handler: Callable) -> None:
        self.handlers.append(handler)

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        pass


class BeforeExecutionHook(PluginHook):
    def __init__(self):
        super().__init__("before_execution")

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        for handler in self.handlers:
            context = handler(context) or context
        return context


class AfterExecutionHook(PluginHook):
    def __init__(self):
        super().__init__("after_execution")

    def execute(self, result: dict[str, Any]) -> dict[str, Any]:
        for handler in self.handlers:
            result = handler(result) or result
        return result


class TransformDataHook(PluginHook):
    def __init__(self):
        super().__init__("transform_data")

    def execute(self, data: Any) -> Any:
        for handler in self.handlers:
            data = handler(data) or data
        return data


class ValidateInputHook(PluginHook):
    def __init__(self):
        super().__init__("validate_input")

    def execute(self, input_data: Any) -> tuple[bool, str]:
        for handler in self.handlers:
            valid, message = handler(input_data)
            if not valid:
                return valid, message
        return True, "Valid"


class BasePlugin(ABC):
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.enabled = True

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def shutdown(self) -> None:
        pass


class PluginRegistry:
    def __init__(self):
        self.plugins: dict[str, BasePlugin] = {}
        self.hooks: dict[str, PluginHook] = {
            "before_execution": BeforeExecutionHook(),
            "after_execution": AfterExecutionHook(),
            "transform_data": TransformDataHook(),
            "validate_input": ValidateInputHook(),
        }

    @timed
    def register_plugin(self, plugin: BasePlugin) -> None:
        with span("plugin.register", name=plugin.metadata.name):
            if plugin.metadata.name in self.plugins:
                raise ValueError(f"Plugin {plugin.metadata.name} already registered")

            plugin.initialize()
            self.plugins[plugin.metadata.name] = plugin
            metric_counter("plugin.registered", 1)

    @timed
    def unregister_plugin(self, plugin_name: str) -> None:
        with span("plugin.unregister", name=plugin_name):
            if plugin_name in self.plugins:
                self.plugins[plugin_name].shutdown()
                del self.plugins[plugin_name]
                metric_counter("plugin.unregistered", 1)

    def get_plugin(self, name: str) -> BasePlugin | None:
        return self.plugins.get(name)

    def get_hook(self, hook_name: str) -> PluginHook | None:
        return self.hooks.get(hook_name)

    def list_plugins(self) -> list[PluginMetadata]:
        return [p.metadata for p in self.plugins.values()]

    @timed
    def execute_plugin(self, plugin_name: str, *args: Any, **kwargs: Any) -> Any:
        with span("plugin.execute", name=plugin_name):
            plugin = self.get_plugin(plugin_name)
            if not plugin or not plugin.enabled:
                raise ValueError(f"Plugin {plugin_name} not found or disabled")

            return plugin.execute(*args, **kwargs)

    @timed
    def execute_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> Any:
        with span("hook.execute", name=hook_name):
            hook = self.get_hook(hook_name)
            if not hook:
                raise ValueError(f"Hook {hook_name} not found")

            return hook.execute(*args, **kwargs)

    def enable_plugin(self, plugin_name: str) -> None:
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = True

    def disable_plugin(self, plugin_name: str) -> None:
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = False

    def get_system_status(self) -> dict[str, Any]:
        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": sum(1 for p in self.plugins.values() if p.enabled),
            "registered_hooks": list(self.hooks.keys()),
            "plugins": [
                {
                    "name": p.metadata.name,
                    "version": p.metadata.version,
                    "enabled": p.enabled,
                }
                for p in self.plugins.values()
            ],
        }


_global_registry: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry
