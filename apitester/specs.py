# Third Party
import pluggy

# First Party
from apitester import __name__ as project_name

hookspec = pluggy.HookspecMarker(project_name)


class RequestSpec:
    @hookspec
    def headers(self) -> dict[str, str]:
        """Add headers to a request."""

    @hookspec
    def cookies(self) -> dict[str, str]:
        """Add cookies to a request."""

    @hookspec
    def auth(self, method: str) -> bool:
        """Provide auth screen."""
