# Standard Library
import tomllib
from typing import Literal

# Third Party
from pydantic import BaseModel, BaseSettings

# First Party
from apitester.url import URL
from apitester.utils import deferedRenderURL


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


class NoAuthConf(BaseModel):
    type: Literal["none"] = "none"


AuthConf = BearerAuthConf | HeaderAuthConf | NoAuthConf


URLConfType = str | URL


class ApiConf(BaseModel):
    auth: AuthConf = NoAuthConf()
    urls: dict[str, URLConfType | dict[str, URLConfType]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self.auth, "url"):
            self.auth.url = deferedRenderURL(
                template=getattr(self.auth, "url", ""), args={"urls": self.urls}, base_url=self.settings.base_url
            )

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
