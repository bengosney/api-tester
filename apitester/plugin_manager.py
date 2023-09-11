# Standard Library
from collections import ChainMap
from collections.abc import Iterable
from typing import Any

# Third Party
import pluggy
from pydantic import BaseModel

# First Party
from apitester import __name__ as project_name
from apitester.specs import RequestSpec

# Locals
from . import plugins


class PluginManager:
    log: Any

    def __init__(self, log=None) -> None:
        self.log = log or print
        self._plugin_manager = self._get_plugin_manager()

    def _get_plugin_manager(self):
        pm = pluggy.PluginManager(project_name)
        pm.add_hookspecs(RequestSpec)
        for plugin in plugins.__all__:
            __import__(f"apitester.plugins.{plugin}")
            _class = getattr(plugins, plugin)
            pm.register(_class(), plugin)
        pm.load_setuptools_entrypoints(project_name)

        return pm

    @property
    def active_plugins(self) -> Iterable[tuple[str, str | None]]:
        for name, plugin in self._plugin_manager.list_name_plugin():
            yield (name, str(plugin.__doc__) or None)

    def get_cookies(self, inital: dict[str, str] | None = None):
        cookies = self._plugin_manager.hook.cookies()
        return ChainMap((inital or {}), *cookies)

    def get_headers(self, inital: dict[str, str] | None = None):
        headers = self._plugin_manager.hook.headers()
        return ChainMap((inital or {}), *headers)

    def get_auth_methods(self) -> list[type[BaseModel]]:
        auth = self._plugin_manager.hook.auth()
        return auth
