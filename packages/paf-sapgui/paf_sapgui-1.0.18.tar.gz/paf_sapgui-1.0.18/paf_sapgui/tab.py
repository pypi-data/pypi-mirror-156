from typing import Any

from .session import active
from . import window


def exists(path: str, tab_id, window_id: int = 0) -> bool:
    path = active.session.findById(f"{path}/{tab_id.value}")
    path = window.check_id(path, window_id)
    try:
        active.session.findById(f"{path}/{tab_id.value}")
        return True
    except Exception as ex:
        print(ex)
        return False


def create(path: str, value: Any = None, window_id: int = 0):
    path = window.check_id(path, window_id)
    if value is not None:
        try:
            tab_element = active.session.findById(f"{path}/{value.value}")
            tab_element.select()
            return tab_element
        except Exception as ex:
            print(ex)
            return None
    return active.session.findById(path)


def select(path: str, window_id: int = 0):
    path = window.check_id(path, window_id)
    active.session.findById(path).select()
