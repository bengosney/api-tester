from typing import Any


def extract(store: dict[str, Any], selector: str) -> Any:
    selectors = selector.split(".")
    cur = store
    for s in selectors:
        cur = cur[s]

    return cur

def join_url(*args) -> str:
    return "/".join([str(p).strip('/') for p in args])