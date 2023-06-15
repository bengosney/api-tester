import tomllib
from typing import Any, Literal

from icecream import ic
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    base_url: str = "http://localhost/"


class AuthConf(BaseModel):
    url: str
    type: Literal["bearer"]
    headers: list[str]


class ApiConf(BaseModel):
    auth: AuthConf
    urls: dict[str, str | dict[str, str]]

    @property
    def auth_url(self) -> str:
        if self.auth.url[0] == ':':
            return getattr(self, self.auth.url[1:])
        
        return self.auth.url
    
    #def get_url(self, name):
    def __getitem__(self, key: str) -> str:
        return f"{Settings().base_url.strip('/')}/{str(self.urls[key]).strip('/')}"


with open("api-conf.toml") as f:
    content = f.read()
    raw_api_conf = tomllib.loads(content)

api_config = ApiConf(**raw_api_conf)


if __name__ == "__main__":
    ic(raw_api_conf)
    ic(api_config)
