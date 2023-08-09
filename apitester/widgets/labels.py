# Third Party
from rich.console import RenderableType
from rich.text import Text
from textual.widgets import Label


class AdvancedLabel(Label):
    prefix: str
    postfix: str

    def __init__(self, renderable: RenderableType = "", prefix: str = "", postfix: str = "", *args, **kwargs) -> None:
        super().__init__(renderable, *args, **kwargs)
        self.prefix = prefix
        self.postfix = postfix

    def render(self) -> RenderableType:
        return Text("".join([self.prefix, str(super().render()), self.postfix]))
