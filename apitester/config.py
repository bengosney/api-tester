# Standard Library
import tomllib
from typing import Literal

# Third Party
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    base_url: str = "http://localhost/"


class BearerAuthConf(BaseModel):
    type: Literal["bearer"]
    url: str
    headers: list[str]
    token_path: str


class HeaderAuthConf(BaseModel):
    type: Literal["header"]
    key: str


class NoAuthCont(BaseModel):
    type: Literal["none"] = "none"


AuthConf = BearerAuthConf | HeaderAuthConf | NoAuthCont


class URLConf(BaseModel):
    url: str
    method: Literal["GET", "POST"]


URLConfType = str | URLConf


class ApiConf(BaseModel):
    auth: AuthConf = NoAuthCont()
    urls: dict[str, URLConfType | dict[str, URLConfType]]

    @property
    def auth_url(self) -> str | None:
        if self.auth.type == "bearer":
            if self.auth.url[0] == ":":
                return getattr(self, self.auth.url[1:])

            return self.auth.url
        return None

    @property
    def settings(self) -> Settings:
        return Settings()

    def __getitem__(self, key: str) -> str:
        return f"{Settings().base_url.strip('/')}/{str(self.urls[key]).strip('/')}"

    @property
    def service_name(self) -> str:
        return f"apt-test:{self.settings.base_url}"


with open("api-conf.toml") as f:
    content = f.read()
    raw_api_conf = tomllib.loads(content)

api_config = ApiConf(**raw_api_conf)
