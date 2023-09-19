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

    token: str | None

    @hookimpl
    def headers(self) -> dict[str, str]:
        if self.token is None:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    @hookimpl
    def auth_config(self) -> type[BaseModel]:
        def set_token(token: str):
            self.token = token

        class LoginAuthConf(BaseModel):
            type: Literal["login"]
            url: str
            headers: list[str]
            token_path: str

            def get_modal(self) -> type[ModalScreen]:
                # First Party
                from apitester.app.screens.login import LoginScreen

                LoginScreen.on_got_token(set_token)
                return LoginScreen

        return LoginAuthConf
