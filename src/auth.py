# Third Party
import keyring

# First Party
from config import api_config


class Auth:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def _credentials(self):
        return keyring.get_credential(api_config.service_name, None)

    @property
    def username(self) -> str | None:
        if credentials := self._credentials():
            return credentials.username
        return None

    @property
    def password(self) -> str | None:
        if credentials := self._credentials():
            return credentials.password
        return None

    def store(self, username: str, password: str) -> None:
        keyring.set_password(api_config.service_name, username, password)

    def remove(self) -> None:
        if self.username:
            keyring.delete_password(api_config.service_name, self.username)

    def __setitem__(self, key: str, data: str) -> None:
        self._store[key] = data

    def __getitem__(self, key: str) -> str:
        return self._store[key]


auth = Auth()
