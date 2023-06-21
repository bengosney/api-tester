# Standard Library
from typing import Self

# Third Party
from textual.app import ComposeResult
from textual.widgets import ProgressBar, Static


class Loader(Static):
    def compose(self) -> ComposeResult:
        self.bar = ProgressBar(total=100, show_eta=False, show_percentage=False)
        yield self.bar

    def on_mount(self) -> None:
        def tick():
            self.bar.advance(1)
            if self.bar.progress == 100:
                self.bar.progress = 0

        self.set_interval(0.01, tick)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args) -> None:
        self.remove()
