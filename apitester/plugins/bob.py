# Standard Library
from typing import Literal

# Third Party
import pluggy
from pydantic import BaseModel, ConfigDict
from textual.screen import ModalScreen

# First Party
from apitester import __name__ as project_name

hookimpl = pluggy.HookimplMarker(project_name)


def get_bob() -> ModalScreen:
    # First Party
    from apitester.app.screens.modal_form import ModalFormScreen

    class BobModel(BaseModel):
        model_config = ConfigDict(title="Login")

        bob: str
        remember: bool = True

    class BobScreen(ModalFormScreen[BobModel]):
        model = BobModel

        async def on_submit(self, model: BobModel):
            self.notify("Logged in ok", title="Auth")

            return BobScreen

    return BobScreen()


class bob:
    """BOB auth method."""

    @hookimpl
    def auth_config(self) -> type[BaseModel]:
        class BobAuthConf(BaseModel):
            type: Literal["bob"]
            url: str

            def get_modal(self) -> ModalScreen:
                return get_bob()

        return BobAuthConf

    @hookimpl
    def auth_modal(self):
        return get_bob()
