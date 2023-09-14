# Standard Library
from typing import Literal

# Third Party
import pluggy
from pydantic import BaseModel
from textual.screen import ModalScreen

# First Party
from apitester import __name__ as project_name

hookspec = pluggy.HookspecMarker(project_name)


class RequestSpec:
    @hookspec
    def headers(self) -> dict[str, str]:
        """Add headers to a request."""

    @hookspec
    def cookies(self) -> dict[str, str]:
        """Add cookies to a request."""

    @hookspec
    def auth_config(self) -> BaseModel:
        """Provide auth config model."""

    @hookspec(firstresult=True)
    def auth_modal(self) -> ModalScreen | Literal[False]:
        """Provide any auth modal, if needed."""
