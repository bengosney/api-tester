# Standard Library
from typing import Any

# Third Party
from tinydb import Query, TinyDB


class DataStore:
    _db = None

    def __init__(self, prefix: str | None = None) -> None:
        self._file_name = "store"
        self.prexif = prefix

    @property
    def db(self) -> TinyDB:
        if self.__class__._db is None:
            self.__class__._db = TinyDB(".apitester.json")
        return self.__class__._db

    def _prefix_key(self, name):
        return f"{self.prexif}-{name}" if self.prexif is not None else name

    def __setitem__(self, name: str, value: Any) -> None:
        kv = Query()
        self.db.upsert({"key": self._prefix_key(name), "value": value}, kv.key == self._prefix_key(name))

    def __getitem__(self, name: str) -> Any:
        kv = Query()
        try:
            res = self.db.search(kv.key == self._prefix_key(name)).pop()
            return res["value"]
        except IndexError:
            return ""
