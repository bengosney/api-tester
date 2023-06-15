import tomllib
from typing import Literal

from icecream import ic
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    base_url: str = "http://localhost/"


class AuthConf(BaseModel):
    url: str
    type: Literal["bearer"]
    headers: list[str]


class ApiConf(BaseModel):
    auth = AuthConf
    urls: dict[str, str | dict[str, str]]


with open("api-conf.toml") as f:
    content = f.read()
    raw_api_conf = tomllib.loads(content)

api_config = ApiConf.parse_obj(raw_api_conf)


if __name__ == "__main__":
    ic(api_config)
