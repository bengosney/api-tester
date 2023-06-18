# Standard Library
from functools import lru_cache
from urllib.parse import urljoin

# Third Party
from jinja2 import BaseLoader, Environment, meta, select_autoescape

# First Party
from apitester.config import api_config

env = Environment(loader=BaseLoader(), autoescape=select_autoescape())


class URL:
    def __init__(self, url: str) -> None:
        self.url = url
        self._data = {}

    def __str__(self) -> str:
        url = env.from_string(self.url)
        return urljoin(api_config.settings.base_url, url.render(self._data))

    def __setitem__(self, name: str, value: str) -> None:
        self._data[name] = value

    def __getitem__(self, name: str) -> str:
        return self._data[name]

    @lru_cache
    def variables(self) -> set[str]:
        ast = env.parse(self.url)
        return meta.find_undeclared_variables(ast)

    @property
    def variable_count(self) -> int:
        return len(self.variables())
