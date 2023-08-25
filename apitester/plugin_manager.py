# Standard Library
from collections import ChainMap
from typing import Any

# Third Party
import pluggy

# First Party
from apitester import __name__ as project_name
from apitester.specs import RequestSpec

# Locals
from . import plugins


class PluginManager:
    log: Any

    def __init__(self, log=None) -> None:
        self.log = log or print

    def _get_plugin_manager(self):
        pm = pluggy.PluginManager(project_name)
        pm.add_hookspecs(RequestSpec)
        for plugin in plugins.__all__:
            __import__(f"apitester.plugins.{plugin}")
            _class = getattr(plugins, plugin)
            pm.register(_class())
        pm.load_setuptools_entrypoints(project_name)

        return pm

    def get_cookies(self, inital: dict[str, str] | None = None):
        cookies = self._get_plugin_manager().hook.cookies()
        return ChainMap((inital or {}), *cookies)

    def get_headers(self, inital: dict[str, str] | None = None):
        headers = self._get_plugin_manager().hook.headers()
        return ChainMap((inital or {}), *headers)
