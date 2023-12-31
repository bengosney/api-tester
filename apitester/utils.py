# Standard Library
import functools
from contextlib import suppress as ctx_suppress
from typing import Any
from urllib.parse import urljoin

# Third Party
from jinja2 import BaseLoader, Environment, select_autoescape


def extract(store: dict[str, Any], selector: str) -> Any:
    selectors = selector.split(".")
    cur = store
    for s in selectors:
        cur = cur[s]

    return cur


def join_url(*args) -> str:
    return "/".join([str(p).strip("/") for p in args])


class suppress_disable:
    def __init__(self, func, exception, disabled_return=None) -> None:
        functools.update_wrapper(self, func)
        self.func = func
        self.exception = exception
        self.disabled_return = disabled_return
        self.enabled = True

    def __call__(self, *args, **kwargs):
        if self.enabled:
            try:
                return self.func(*args, **kwargs)
            except self.exception:
                self.enabled = False

        return self.disabled_return


def suppress(exception, default=None):
    def decorator_suppress(func):
        @functools.wraps(func)
        def wrapper_suppress(*args, **kwargs):
            with ctx_suppress(exception):
                try:
                    return func(*args, **kwargs)
                except exception:
                    return default

        return wrapper_suppress

    return decorator_suppress


def deferedURLRender(template: str, args: dict[str, Any], base_url: str) -> str:
    class _proxy(str):
        template: str
        args: dict[str, Any]
        base_url: str

        def __str__(self) -> str:
            env = Environment(loader=BaseLoader(), autoescape=select_autoescape())
            template = env.from_string(self.template)
            rendered = template.render(self.args)
            return urljoin(self.base_url, rendered)

    proxy = _proxy()
    proxy.template = template
    proxy.args = args
    proxy.base_url = base_url

    return proxy
