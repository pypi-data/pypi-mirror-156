from typing import NoReturn

from .session import active

_id = 0


def check_id(path_value: str, window_id=0) -> str:
    """

    :param path_value:
    :param window_id:
    :return str:
    """
    if f'wnd[{window_id}]' not in path_value:
        path_value = path_value.replace('wnd[0]', f'wnd[{window_id}]')
    return path_value


def id(id_value: int = None, window_id=0) -> int:
    """
    :param id_value:
    :param window_id:
    :return int:
    """
    global _id
    if id_value is None:
        return _id
    _id = window_id


def path(full_path: bool = False):
    short_path = f"wnd[{_id}]"
    if full_path:
        return f"/app/con[0]/ses[0]/{short_path}"
    return short_path


def get_title(window_id: int = 0) -> str | None:
    """

    :param window_id:
    :return str|None:
    """
    if exists(window_id):
        return active.session.findById(f'wnd[{window_id}]').text
    else:
        return None


def close(window_id: int = 0) -> NoReturn:
    """

    :param window_id:
    """
    active.session.findById(f'wnd[{window_id}]').close()


def exists(window_id: int = 0, go_on: bool = False, close_window: bool = False) -> bool:
    """

    :param close_window:
    :param go_on:
    :param window_id:
    :return bool:
    """
    try:
        local_element = active.session.findByID(f'wnd[{window_id}]')
        if go_on:
            raise NotImplementedError
        elif close_window:
            local_element.close()
            return True
        else:
            return True
    except Exception:
        return False


def get_contents(window_id: int = 0) -> str:
    # Check, which kind of window we have
    # Textlines or Messtxt
    content_lines: str = ''
    try:
        active.session.findById(f'wnd[{window_id}]/usr/txtSPOP-TEXTLINE1')
        content_lines = f'wnd[{window_id}]/usr/txtSPOP-TEXTLINE'
    except Exception:
        print(
            'Nope, this window do not contain textlines. Using the other element type (but only when it is '
            'implemented. Up to now, it is not ;-)')
        # active_session._session.findById('wnd[{window_id}]/usr/txtSPOP-TEXTLINE1')

    lines_exist = True
    read_text = ''
    line_counter = 1
    while lines_exist:
        try:
            local_element = active.session.findById(f'wnd[{window_id}]/usr/txtSPOP-TEXTLINE{line_counter}')
            read_text += f' {local_element.text}'
            line_counter += 1
        except Exception:
            lines_exist = False
    if content_lines == f'wnd[{window_id}]/usr/txtSPOP-TEXTLINE':
        active.session.findById(f'wnd[{window_id}]/usr/btnSPOP-OPTION1').press()

    return read_text
