# Standard Library
from typing import Literal

# Third Party
import pluggy
from pydantic import BaseModel

# First Party
from apitester import __name__ as project_name

hookimpl = pluggy.HookimplMarker(project_name)


class BobAuthConf(BaseModel):
    type: Literal["bob"]
    url: str


class bob:
    """BOB auth method."""

    @hookimpl
    def auth(self) -> type[BaseModel]:
        return BobAuthConf
