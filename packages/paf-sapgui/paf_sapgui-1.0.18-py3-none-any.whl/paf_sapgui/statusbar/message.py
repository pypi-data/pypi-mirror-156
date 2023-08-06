from .. import window
from ..session import active

_path = "wnd[0]/sbar/pane[0]"


def get_text(window_id=0):
    path = window.check_id(_path, window_id)
    local_statusbar = active.session.findById(path)
    return local_statusbar.text


"""
def get_value(value_number):
    pass
    # Set lobjStatusleiste = SapGui_Statusleiste.Objekt()
    # If lobjStatusleiste.exist(2) Then
    # Wert = lobjStatusleiste.getRoProperty("item" & Wertnummer)


def get_object():
    pass
    # Set Objekt = SapGui_Elemente.Statusleiste()


def get_message_type():
    pass
    # Nachrichtentyp = Objekt().GetROProperty("messagetype")


def get_text():
    pass
    # Text = False
    # Set lobjStatusleiste = SapGui_Statusleiste.Objekt()
    # If lobjStatusleiste.exist(2) = True Then
    # Text = lobjStatusleiste.getRoProperty("as-paf-paf_tools-text")
"""
