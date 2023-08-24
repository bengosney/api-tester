# Third Party
from pydantic import BaseModel, ConfigDict

# First Party
from apitester.config import config
from apitester.types import URLMethod

# Locals
from .modal_form import ModalFormScreen


class NewURL(BaseModel):
    model_config = ConfigDict(title="Add URL")

    name: str
    url: str
    method: URLMethod = "GET"


class AddURLScreen(ModalFormScreen[NewURL]):
    model = NewURL

    def on_submit(self, model: NewURL) -> None:
        config.add_url(**dict(model))
        self.notify("New URL save as a comment in your config file", title="New URL")
