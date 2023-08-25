# Third Party
import pluggy

# First Party
from apitester import __name__ as project_name

hookimpl = pluggy.HookimplMarker(project_name)


class xdebug:
    @hookimpl
    def cookies(self):
        return {"XDEBUG_SESSION": "start"}
