from .session import active


def open_by_path(path):
    pass
    # SapGui_Menueleiste.Objekt().Select Menuepfad


def open_by_positions(positions: list, window_id: int = 0):
    path = f'wnd[{window_id}]/mbar'
    for position in positions:
        path += f'/menubar[{position}]'
    active.session.findById(path).select()
