from . import window


def label_path(path_or_column: str | int, row: int = None, window_id: int = 0) -> str:
    path = path_or_column
    if isinstance(path_or_column, int):
        path = f'wnd[{window_id}]/usr/lbl[{path_or_column},{row}]'
    path = window.check_id(path, window_id)
    return check_wnd(path, window_id)


def button_path(path_or_number: str | int, container: int = None, window_id: int = 0):
    """

    :param path_or_number:
    :param container:
    :param window_id:
    :return:
    """
    path = path_or_number
    if isinstance(path_or_number, int):
        path = f'wnd[{window_id}]/tbar[{container}]/btn[{str(path_or_number)}]'
    path = check_wnd(path)
    return window.check_id(path, window_id)


def checkbox_path(path_or_column: str | int, row: int = None, window_id: int = 0) -> str:
    """

    :param path_or_column:
    :param row:
    :param window_id:
    :return:
    """
    path = path_or_column
    if isinstance(path_or_column, int):
        path = f'wnd[{window_id}]/usr/chk[{path_or_column},{row}]'
    path = check_wnd(path)
    return window.check_id(path, window_id)


def check_wnd(path: str, window_id: int = 0) -> str:
    if 'wnd[' not in path:
        path = f"wnd[{window_id}]{path}"
    return path

