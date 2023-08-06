"""ASIT - SES - SSO - SE16 - Selection Screen

Provides different methods helping to work with the transaction se16

    Date / user / action
    05.05.2022 / ckoeste1 / initial creation

Methods:

    * create

"""

from typing import Any

from ..session import active
from .. import button, checkbox, key, label, menubar, tab, textfield, window
from . import elements

_single_selection_values = []
_range_selection_values = []
_exclude_single_selection_values = []
_exclude_range_selection_values = []


def single_selection(values: list = None) -> list:
    """Sets the values for the single selection

        Parameters
        ----------
            :param values:
            :return list:
        """
    global _single_selection_values
    if values is None:
        return _single_selection_values

    for value in values:
        _single_selection_values.append(value)


def exclude_single(values: list = None) -> list:
    """Sets the values to exclude for the single selection

        Parameters
        ----------
            :param values:
            :return list:
    """
    global _exclude_single_selection_values
    if values is None:
        return _exclude_single_selection_values

    for value in values:
        _exclude_single_selection_values.append(value)


def select_ranges(values: list = None) -> list:
    """Sets the ranges to select

        Parameters
        ----------
            :param values:
            :return list:
    """
    global _range_selection_values
    if values is None:
        return _range_selection_values

    for value in values:
        _range_selection_values.append(value)


def exclude_ranges(values: list = None) -> list:
    """Sets the ranges to exclude for the selection

        Parameters
        ----------
            :param values:
            :return list:
    """
    global _exclude_range_selection_values
    if values is None:
        return _exclude_range_selection_values

    for value in values:
        _exclude_range_selection_values.append(value)


def field_value(position_or_path: int | str, value: Any = None, is_high: bool = False, window_id: int = 0):
    """Sets a value for a defined field

        Parameters
        ----------
            :param window_id:
            :param value:
            :param position_or_path:
            :param is_high:
    """
    local_field = textfield.create(path_or_position=position_or_path, is_high=is_high, window_id=window_id)
    if value is None:
        return local_field.text
    local_field.text = value


def selection_field(position_or_path: str | int, value: Any = None, is_high: bool = False,
                    window_id: int = 0):
    """Sets a value for a defined field

        Parameters
        ----------
                :param is_high:
                :param window_id:
                :param value:
                :param position_or_path:
        """
    return textfield.create(path_or_position=position_or_path, is_high=is_high, value=value, window_id=window_id)


def number_of_entries() -> int:
    """Gets the amount entries for a selection
        Return
        ------
            :returns int
            """
    button.click(31, 1)
    if window.exists():
        if window.get_title(1) == "Anzeige: Anzahl der Einträge":
            return int(label.get_content('usr/txtG_DBCOUNT', 1))
        window.close(1)


def fields_for_selection(fields, find_by="technical"):
    max_fields = len(fields)
    set_checkboxes = 0

    fields_column = 36 if find_by != "technical" else 4
    menubar.open_by_positions([0, 3, 2])
    button.click(14, 0, 1)

    go_one = True
    row_counter = 5

    while go_one:
        label_field = label.create(fields_column, row_counter, 1)
        if label_field is not None and label_field.text in fields:
            checkbox.activate(2, row_counter, 1)
            set_checkboxes += 1
        if set_checkboxes == max_fields:
            go_one = False
        if row_counter == 21:
            key.page_down(1)
            row_counter = 0
        row_counter = row_counter + 1

    button.green_tick(1)


def set_single_values_for_selection(position_or_name, values):
    button.click_by_path(f'usr/btn%_{position_or_name}_%_APP_%-VALU_PUSH')
    tab.create(path='usr/tabsTAB_STRIP', window_id=1, value=elements.multi_selection.einzelwerte_selektieren)
    if isinstance(values, str):
        values = values.split(",") if "," in values else [values]
    counter = 0
    for value in values:
        table_field = active.session.findById(
            f'wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/txtRSCSEL_255'
            f'-SLOW_I[1,{counter}]')
        table_field.text = value

    key.f8(1)


def mehrfachselektion(feldname_oder_feldnummer):
    """
        if TypeName(Feldname_oder_Feldnummer) == "String":
            _actions.Buttons.click_by_id(f'usr/btn%_{Feldname_oder_Feldnummer}_%_APP_%-VALU_PUSH')
            #'/app/con[0]/ses[0]/wnd[0]/usr/btn%_R_FIKEY_%_APP_%-VALU_PUSH
            #'/app/con[0]/ses[0]/wnd[0]/usr/btn%_FIKEY_%_APP_%-VALU_PUSH"	String
        else:
            _actions.Buttons.click_by_id(f'usr/btn%_I{Feldname_oder_Feldnummer}_%_APP_%-VALU_PUSH')

        lobjTabs = Tabs.object(f'usr/tabsTAB_STRIP', 1)

        if len(se16.SelectionScreen.carrlEinzelwerteSelektieren) > 0:
            lobjTabs.Select("Einzelwerte selektieren")
            lobjESTabelle = Tables.object(f'usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE', 1)
            for counter in range(len(se16.SelectionScreen.carrlEinzelwerteSelektieren)):
                #SAPGuiSession("S").SAPGuiWindow("Mehrfachselektion für Referenz").SAPGuiTable("SAPLALDBSINGLE").SetCellData 1,"Einzelwert","3434234234"
                lobjESTabelle.SetCellData counter + 1, "Einzelwert", carrlEinzelwerteSelektieren.Item(lintZaehler)
        if len(se16.SelectionScreen.carrlEinzelwerteAusschliessen.count) > 0:
            lobjTabs.Select("Einzelwerte ausschließen")
            lobjESTabelle = Tables.object(f'usr/tabsTAB_STRIP/tabpNOSV/ssubSCREEN_HEADER:SAPLALDB:3030/tblSAPLALDBSINGLE_E', 1)
            for counter in range(len(se16.SelectionScreen.carrlEinzelwerteAusschliessen.count)):
                lobjEATabelle.SetCellData lintZaehler + 1, 1, carrlEinzelwerteAusschliessen.Item(lintZaehler)

        if len(se16.SelectionScreen.carrlIntervalleSelektieren) > 0:
            lobjTabs.Select("Intervalle selektieren")
            lobjISTabelle = Tables.object(f'usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL', 1)
            for counter in range(len(se16.SelectionScreen.carrlIntervalleSelektieren)):
                larrWerte = split(carrlEinzelwerteAusschliessen.Item(lintZaehler), ",")
                lobjISTabelle.SetCellData lintZaehler + 1, 1, larrWert(0)
                lobjISTabelle.SetCellData lintZaehler + 1, 2, larrWert(1)
            Next
        if len(se16.SelectionScreen.carrlIntervalleAusschliessen.count) > 0:
            lobjTabs.Select("Intervalle ausschliessen")
            Set lobjIATabelle = SapGui_Elemente.SF(1).SAPGuiTable("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsTAB_STRIP/tabpNOINT/ssubSCREEN_HEADER:SAPLALDB:3040/tblSAPLALDBINTERVAL_E")
            for counter in range(len(se16.SelectionScreen.carrlIntervalleAusschliessen)):
                larrWerte = split(carrlIntervalleAusschliessen.Item(lintZaehler), ",")
                lobjIATabelle.SetCellData lintZaehler + 1, 1, larrWert(0)
                lobjIATabelle.SetCellData lintZaehler + 1, 2, larrWert(1)

        Keys.f8(1)
        """
    raise NotImplementedError


def set_selection_option_with_value(value, postion: int, high_low: str = "low", selection_type: str = "g",
                                    window_id: int = 0):
    local_selection_field = textfield.create_selection_field(position=postion, high_low=high_low,
                                                             window_id=window_id)
    local_selection_field._text = value
    local_selection_field.setFocus()
    button.selection_options()

    subtract_value = 2

    grid = active.session.findById('wnd[1]/usr/cntlOPTION_CONTAINER/shellcont/shell')
    grid.currentCellRow = 0

    if grid.getCellValue(0, 'TEXT') == "Muster":
        subtract_value = 0

    row_to_select = 0

    if selection_type.lower() in {'muster', "m"}:
        row_to_select = 0
    if selection_type.lower() in {'muster ausschließen', "ma"}:
        row_to_select = 1
    if selection_type.lower() in {'einzelwert', 'ew', 'e'}:
        row_to_select = 2 - subtract_value
    if selection_type.lower() in {'größer oder gleich', 'gog'}:
        row_to_select = 3 - subtract_value
    if selection_type.lower() in {'kleiner oder gleich', 'kog'}:
        row_to_select = 4 - subtract_value
    if selection_type.lower() in {'größer', 'g'}:
        row_to_select = 5 - subtract_value
    if selection_type.lower() in {'kleiner', 'k'}:
        row_to_select = 6 - subtract_value
    if selection_type.lower() in {'ungleich', 'ug', 'u'}:
        row_to_select = 7 - subtract_value

    grid.currentCellRow = row_to_select
    grid.doubleClickCurrentCell()


def selektionsoption(feldnummer, feldtyp, wert, selektionsoptionswert, ist_cfeld, fenster_id):
    """
        if isnull(istCFeld) = true Then
            istCFeld = true
        Set lobjFeld = SapGui_Selektion.selection_field(Feldnummer, Feldtyp, istCFeld, FensterID)
        if istCFeld = true AND lobjFeld.exist(1) = false Then
            Set lobjFeld = SapGui_Selektion.selection_field(Feldnummer, Feldtyp, false, FensterID)
        if istCFeld = false AND lobjFeld.exist(1) = false Then
            Set lobjFeld = SapGui_Selektion.selection_field(Feldnummer, Feldtyp, true, FensterID)

        lobjFeld.setFocus
        lobjFeld.Set Wert
        SapGui_Taste.F2_Taste 0

        lintMinus = 2
        if SapGui_Elemente.SF(0).SapGuiGrid("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/cntlOPTION_CONTAINER/shellcont/shell").GetCellData(1,"#2") = "Muster" Then
            lintMinus = 0

        lintReihe = 0

        Select Case lcase(Selektionsoptionswert)
            Case "muster", "m":
                lintReihe = 1
            Case "muster ausschließen", "ma":
                lintReihe = 2
            Case "einzelwert", "ew", "e":
                lintReihe = 3 - lintMinus
            Case "größer oder gleich", "gog":
                lintReihe = 4 - lintMinus
            Case "kleiner oder gleich", "kog":
                lintReihe = 5 - lintMinus
            Case "größer", "g":
                lintReihe = 6 - lintMinus
            Case "kleiner", "k":
                lintReihe = 7 - lintMinus
            Case "ungleich", "ug", "u":
                lintReihe = 8 - lintMinus

    SapGui_Elemente.SF(0).SapGuiGrid("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/cntlOPTION_CONTAINER/shellcont/shell").SelectRow lintReihe

    _actions.Buttons.click(0, 0, 1)
    """
    raise NotImplementedError


def maximale_trefferzahl(anzahl):
    """
        if not isinstance(Anzahl, int):
            raise Exception("Die Funktion 'Maximale Trefferzahl' muss einen Integer-Wert übergeben bekommen")
        else:
            SapGui_Elemente.EF("MAX_SEL", 0).set cstr(Anzahl)
        """
    raise NotImplementedError


def benutzerparameter_feldname():
    """
        Setze_Schluesselwort("Feldname")
        """
    raise NotImplementedError


def benutzerparameter_feldbezeichner():
    """
        Setze_Schluesselwort("Feldbezeichner")
        """
    raise NotImplementedError


def setze_schluesselwort(typ):
    """
        Menubars.open("Einstellungen;Benutzerparameter...")

        if Typ.lower() == "feldname":
            Fields.Radiobuttons.set("SEUCUSTOM-FIELDNAME", 1)
        else:
            Fields.Radiobuttons.set("SEUCUSTOM-FIELDTEXT", 1)

        _actions.Buttons.green_tick(1)
        """
    raise NotImplementedError
