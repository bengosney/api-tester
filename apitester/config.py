# Standard Library
import tomllib
from typing import Literal
from urllib.parse import urljoin

# Third Party
from jinja2 import BaseLoader, Environment, select_autoescape
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        env = Environment(loader=BaseLoader(), autoescape=select_autoescape())

        if hasattr(self.auth, "url"):
            url = env.from_string(getattr(self.auth, "url", ""))
            self.auth.url = urljoin(self.settings.base_url, url.render({"urls": self.urls}))

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
