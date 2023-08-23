# Third Party
from pydantic import BaseModel

# First Party
from apitester.auth import auth

# Locals
from .modal_form import ModalFormScreen


class APIKey(BaseModel):
    api_key: str
    remember: bool = True


class APIKeyScreen(ModalFormScreen[APIKey]):
    model = APIKey

    def on_submit(self, model: APIKey) -> None:
        if model.remember:
            auth.store("api_key", model.api_key)
        else:
            auth.remove()

        auth["api_key"] = model.api_key

        self.notify("API Key Set", title="Auth")
