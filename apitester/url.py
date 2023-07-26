# Standard Library
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal
from urllib.parse import urljoin

# Third Party
from jinja2 import BaseLoader, Environment, meta, select_autoescape

# First Party
from apitester import config

env = Environment(loader=BaseLoader(), autoescape=select_autoescape())


@dataclass()
class URL:
    url: str
    method: Literal["GET", "POST"] = "GET"
    fields: list[str] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash((self.url, self.method))

    def __post_init__(self) -> None:
        self._data: dict[str, str] = {}

    def __str__(self) -> str:
        url = env.from_string(self.url)
        return urljoin(config.api_config.settings.base_url, url.render(self._data))

    def __repr__(self) -> str:
        return f"<{self.method}> - {self.url} {[f for f in self.fields]}"

    def __setitem__(self, name: str, value: str) -> None:
        self._data[name] = value

    def __getitem__(self, name: str) -> str:
        return self._data[name]

    @lru_cache
    def variables(self) -> set[str]:
        ast = env.parse(self.url)
        return meta.find_undeclared_variables(ast) | set(self.fields)

    @property
    def variable_count(self) -> int:
        return len(self.variables())
