# Standard Library
from typing import Any

# Third Party
from pydantic import BaseModel, ConfigDict

# First Party
from apitester.auth import auth

# Locals
from .modal_form import ModalFormScreen


class APIKey(BaseModel):
    model_config = ConfigDict(title="API Key")

    api_key: str
    remember: bool = True


class APIKeyScreen(ModalFormScreen[APIKey]):
    model = APIKey

    @property
    def inital(self) -> dict[str, Any]:
        return {"api_key": auth.get("api_key")}

    def on_submit(self, model: APIKey) -> None:
        if model.remember:
            auth.store("api_key", model.api_key)
        else:
            auth.remove()

        auth["api_key"] = model.api_key

        self.notify("API Key Set", title="Auth")
