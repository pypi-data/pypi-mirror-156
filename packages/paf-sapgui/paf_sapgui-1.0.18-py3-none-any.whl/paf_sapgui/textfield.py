from typing import Any

from .session import active
from . import window


def create(path_or_position: str | int, value: Any = None, is_high: bool = False, window_id: int = 0):
    if isinstance(path_or_position, int):
        path_or_position = f"wnd[{window_id}]/usr/ctxtI{path_or_position}-{'HIGH' if is_high else 'LOW'}"
    path_or_position = window.check_id(path_or_position, window_id)
    local_field = active.session.findById(path_or_position)
    if value is not None:
        local_field._text = value
    return local_field


def set_focus(path_or_position, high_low="low", window_id=0):
    if isinstance(path_or_position, int):
        path_or_position = f"wnd[{window_id}]/usr/ctxtI{path_or_position}-{high_low.upper()}"
    local_field = create(path_or_position, window_id)
    local_field.setFocus()
    return local_field
