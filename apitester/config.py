# Standard Library
import os
import tomllib
from typing import Annotated, Any, Literal, Union

# Third Party
from pydantic import BaseModel, BeforeValidator, ValidationError, WrapValidator
from pydantic_settings import BaseSettings

# First Party
from apitester.plugin_manager import PluginManager
from apitester.types import URLMethod
from apitester.url import URL
from apitester.utils import deferedURLRender


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


pm = PluginManager()
AuthConf = BearerAuthConf | HeaderAuthConf | NoAuthConf | Union[tuple(pm.get_auth_configs())]  # type: ignore


def validate_urldict(v, handler):
    passed = handler(v)
    if "url" in passed:
        raise ValidationError()

    return passed


URLType = Annotated[URL, BeforeValidator(lambda x: URL(x) if type(x) is str else x)]
URLDict = Annotated[dict[str, URLType], WrapValidator(validate_urldict)]
URLConf = dict[str, URLType | dict[str, URLType | URLDict]]


class ConfigModel(BaseModel):
    auth: AuthConf = NoAuthConf()
    urls: URLConf

    def model_post_init(self, __context: Any) -> None:
        if hasattr(self.auth, "url"):
            self.auth.url = deferedURLRender(getattr(self.auth, "url", ""), {"urls": self.urls}, self.settings.base_url)

    @property
    def settings(self) -> Settings:
        return Settings()

    def __getitem__(self, key: str) -> str:
        return f"{Settings().base_url.strip('/')}/{str(self.urls[key]).strip('/')}"

    @property
    def service_name(self) -> str:
        return f"apt-test:{self.settings.base_url}"


class Config:
    path: str
    _st_mtime: float
    api_conf: ConfigModel | None = None

    def __init__(self, path: str = "api-conf.toml") -> None:
        self.path = path
        self.load()

    def load(self) -> None:
        with open(self.path) as f:
            content = f.read()
            raw_api_conf = tomllib.loads(content)

        self.api_conf = ConfigModel(**raw_api_conf)
        self._st_mtime = os.stat(self.path).st_mtime

    def check_reload(self):
        if self._st_mtime == os.stat(self.path).st_mtime:
            return False

        self.load()
        return True

    def add_url(self, name: str, url: str, method: URLMethod):
        if self.api_conf is not None:
            self.api_conf.urls[name] = URL(url=url, method=method)

        with open(self.path, "a") as f:
            f.write(f'\n# {name} = {{ url = "{url}", method = "{method}" }}')

    def __getattr__(self, __name: str) -> Any:
        return getattr(self.api_conf, __name)


config = Config()
