# Third Party
from pydantic import BaseModel

# First Party
from apitester.config import config
from apitester.types import URLMethod

# Locals
from .modal_form import ModalFormScreen


class NewURL(BaseModel):
    name: str
    url: str
    method: URLMethod = "GET"


class AddURLScreen(ModalFormScreen[NewURL]):
    model = NewURL

    def on_submit(self, model: NewURL) -> None:
        config.add_url(**dict(model))
