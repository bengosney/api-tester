# Standard Library
import tomllib
from typing import Literal

# Third Party
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    base_url: str = "http://localhost/"


class AuthConf(BaseModel):
    url: str
    type: Literal["bearer"]
    headers: list[str]
    token_path: str


class URLConf(BaseModel):
    url: str
    method: Literal["GET", "POST"]


URLConfType = str | URLConf


class ApiConf(BaseModel):
    auth: AuthConf
    urls: dict[str, URLConfType | dict[str, URLConfType]]

    @property
    def auth_url(self) -> str:
        if self.auth.url[0] == ":":
            return getattr(self, self.auth.url[1:])

        return self.auth.url

    @property
    def settings(self) -> Settings:
        return Settings()

    def __getitem__(self, key: str) -> str:
        return f"{Settings().base_url.strip('/')}/{str(self.urls[key]).strip('/')}"

    @property
    def service_name(self) -> str:
        return f"apt-test:{self.settings.base_url}"

    @staticmethod
    def _load_toml():
        with open("api-conf.toml") as f:
            content = f.read()
            return tomllib.loads(content)

    @classmethod
    def load(cls):
        raw_api_conf = cls._load_toml()
        return cls(**raw_api_conf)

    def reload(self):
        raw_api_conf = self._load_toml()
        self.__dict__.update(raw_api_conf)


api_config = ApiConf.load()
