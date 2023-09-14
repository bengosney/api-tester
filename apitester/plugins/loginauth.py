# Standard Library
from typing import Literal

# Third Party
import pluggy
from pydantic import BaseModel
from textual.screen import ModalScreen

# First Party
from apitester import __name__ as project_name

hookimpl = pluggy.HookimplMarker(project_name)


class loginauth:
    """Login Auth."""

    @hookimpl
    def auth_config(self) -> type[BaseModel]:
        class LoginAuthConf(BaseModel):
            type: Literal["login"]
            url: str
            headers: list[str]
            token_path: str

            def get_modal(self) -> type[ModalScreen]:
                # First Party
                from apitester.app.screens.login import LoginScreen

                LoginScreen.set_plugin(self)
                return LoginScreen

        return LoginAuthConf
