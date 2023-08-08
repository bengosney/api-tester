# Standard Library

# Third Party
from textual.app import ComposeResult
from textual.widgets import Static, Tree

# Locals
from ..config import URLConf


class URLTree(Static):
    urls: URLConf

    def __init__(self, urls, *args, **kwargs) -> None:
        self.urls = urls
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("URLs")

        if self.urls is not None:
            self._build_tree(self.urls, tree.root)

        tree.root.expand_all()

        yield tree

    @classmethod
    def _build_tree(cls, items: dict, node):
        for key, val in items.items():
            if isinstance(val, dict):
                cls._build_tree(val, node.add(key))
            else:
                node.add_leaf(f"{key} - {val.url}", data={"url": val})

    def update(self, urls: URLConf):
        tree: Tree[dict] = self.query_one(Tree)

        tree.root.remove_children()
        self._build_tree(urls, tree.root)

        tree.root.expand_all()
