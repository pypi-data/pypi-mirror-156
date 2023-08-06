"""ASIT - SES - SSO - SE16 - Tables

Provides different methods helping to work with the transaction se16

    Date / user / action
    05.05.2022 / ckoeste1 / initial creation

Methods:

    * create

"""
import win32com.client
from .. import transaction
from paf_sapgui_eltrans import se16

from ..session import active
from .. import element
from .. import key
from . import elements


def open(table_name: str):
    """Creates a new object of type checkbox.

    Parameters
    ----------
    table_name: str
        The name of the table to open
    """
    transaction.open("se16")
    se16.SelectionScreen().table().value(table_name)
    key.enter()


def export_spreadsheat():
    # Menubars.open("Tabelleneintrag;Liste;Exportieren;Tabellenkalkulation...")
    raise NotImplementedError


def create_standard(window_id: int = 0):
    return create()


def create(path: str = None, window_id: int = 0) -> win32com.client.CDispatch:
    """Creates a new object of type table.

        Parameters
        ----------
        path: str
            A path to the table
        window_id: int, default=0
            The ID of the window the checkbox is contained in
        Returns
        -------
            win32com.client.CDispatch
    """
    if path is None:
        path = elements.standard_table
    path = element.check_wnd(path, window_id)
    return active.session.findById(path)


def feldbezeichner() -> object:
    """
        SapGui_Menueleiste.Objekt().Select "Einstellungen;Benutzerparameter..."

        SapGui_Elemente.SF(1).SAPGuiRadioButton("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDTEXT").Set

        SapGui_Schaltflaeche.Objekt(0, 0, 1).Click
        """
    raise NotImplementedError


def feldnamen():
    """
        SapGui_Menueleiste.Objekt().Select "Einstellungen;Benutzerparameter..."

        SapGui_Elemente.SF(1).SAPGuiRadioButton("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDNAME").Set

        SapGui_Schaltflaeche.Objekt(0, 0, 1).Click
        """
    raise NotImplementedError


def spaltennamen():
    """
        SapGui_Menueleiste.Oeffne("Einstellungen;Layout;Ändern...")
        Set lobjTabelle = SapGui_Elemente.SF(1).SapGuiGrid("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER2_LAYO/shellcont/shell","index:=0")

        Spaltennamen = ""

        For lintReihenzaehler = 1 To lobjTabelle.RowCount Step 1
            Spaltennamen = Spaltennamen & lobjTabelle.GetCellData(lintReihenzaehler, "#1") & ";"
        Next

        Spaltennamen = mid(Spaltennamen, 1, len(Spaltennamen) - 1)
        SapGui_Elemente.SF(1).close
        """
    raise NotImplementedError


def sichtbare_spalten(spaltennamen):
    """
        SapGui_Menueleiste.Oeffne("Einstellungen;Layout;Ändern...")
        ' Angezeigte Spalten
        set lobjAngezeigteSpalten = SapGui_Elemente.SF(1).SapGuiGrid("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER2_LAYO/shellcont/shell")
        ' Spaltenvorrat
        set lobjSpaltenvorrat = SapGui_Elemente.SF(1).SapGuiGrid("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell")
        ' Schaltfläche: nach angezeigte Spalten
        Set lobjSchaltflaeche = SapGui_Elemente.SF(1).SapGuiButton("id:=/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING")

        lobjAngezeigteSpalten.SelectAll
        SapGui_Schaltflaeche.Klick_Id "/app/con\[0\]/ses\[0\]/wnd\[1\]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_FL_SING", 1

        lobjSpaltenvorrat.SelectRow 1
        For lintNamenzaehler = 0 To UBound(Spaltennamen) Step 1
            set lobjReihenNummern = lobjSpaltenvorrat.FindAllRowsByCellContent("#1", Spaltennamen(lintNamenzaehler))
            For each lintReihennummer in lobjReihenNummern
                lobjSpaltenvorrat.ActivateRow(lintReihennummer)
            Next
        Next
        SapGui_Schaltflaeche.Gruener_Haken 1
    """
    raise NotImplementedError


def felder_fuer_selektion(anzuzeigende_elemente):
    """
        lReihenzaehler = 5;
        Elemente.Menueleiste().Select("Einstellungen;Felder für Selektion");
        Elemente.Schaltflaeche(SchaltflaecheID: 14, FensterID: 1).Click();
        ILabel llabBeschriftung = Elemente.Beschriftung(Reihe: lReihenzaehler, Spalte: 5, FensterID: 1);
        Do While(llabBeschriftung.Exists(2))
            if(Anzuzeigende_Elemente.Contains(llabBeschriftung.Text))
                Elemente.Checkbox(Reihe: lReihenzaehler, Spalte: 2, FensterID: 1).Set(True);
                Anzuzeigende_Elemente = Anzuzeigende_Elemente.Except(New[]{llabBeschriftung.Text}).ToArray();
            End if
            if(Anzuzeigende_Elemente.Length == 0)
                break;
            else:
                lReihenzaehler + +;
                llabBeschriftung = Elemente.Beschriftung(Reihe: lReihenzaehler, Spalte: 5, FensterID: 1);
            End if
        Loop

        Elemente.Schaltflaeche(SchaltflaecheID: 0, FensterID: 1).Click();
        """
    raise NotImplementedError


def hole_feld(feldname, bis):
    """
    For(lReihenzaehler=1; lReihenzaehler <= 40; lReihenzaehler + +)
        lstrFeldname = "I" + lReihenzaehler.To() + "-" + ((!bis) ? "LOW": "HIGH");
        IEditField lefFeld = Elemente.Edit_Feld(Technischer_Name: lstrFeldname, FensterID: 0);
        if(lefFeld.Exists(2))
            if(lefFeld.AttachedText == Feldname)
                return lefFeld;
            End if
        else:
            lReihenzaehler = 41;
        End if
    Next
    return Null;
    """
    raise NotImplementedError


def feld_befuellen(feldname, wert, bis):
    """
        IEditField lefFeld = Hole_Feld(Feldname, bis);
        if(lefFeld != Null)
            lefFeld.SetText(Wert);
        End if
        """
    raise NotImplementedError


def feldnamen(objekt):
    """
        Tabelle_Oeffne_Einstellungen Objekt, "Data Browser",
        SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[1\]").SapGuiButton("id:=/app/con\[[0-9]\]/ses\[[0-9]\]/wnd\[1\]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDNAME").set
        FensterX_gruenerHaken
        """
    raise NotImplementedError


def set_fieldtext():
    """Creates a new object of type checkbox.
        TODO: Richtige Beschreibung (setze Feldbezeichner)
        """
    active.session.findById("wnd[0]/mbar/menubar[3]/menubar[3]").select()
    active.session.findById("wnd[1]/usr/tabsG_TABSTRIP/tabp0400").select()
    active.session.findById(
        "wnd[1]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDTEXT").select()
    active.session.findById("wnd[1]/tbar[0]/btn[0]").press()


def zeige(objekt, was):
    """
        SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[1\]").SapGuiMenubar("guicomponenttype:=111").Select "Einstellungen;Benutzerparameter.",
        if(lcase(Was) = "feldname") Then
            SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[1\]").SapGuiButton("id:=/app/con[0]/ses\[[0-9]\]/wnd\[1\]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDNAME").Set
        else
            SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[1\]").SapGuiButton( "id:=/app/con[0]/ses\[[0-9]\]/wnd\[1\]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDTEXT").Set
        End if
        SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[1\]").SapGuiButton("guicomponenttype:=40", "name:=btn\[0\]", "containername:=tbar\[0\]").Click
        """
    raise NotImplementedError


def sortiere(objekt, spalte, richtung):
    """
        Set lobjReferenz = SapGuiSession("name:=ses\[[0-9]\]").Tabellen Objekt
        if typename(Spalte) Then
            lobjReferenz.SelectColumn Spalte
        else
            lobjReferenz.SelectColumn "#" & Spalte
        End if

        Select Case lcase(Richtung) {
            case "absteigend", "abs", "ab", "descending", "desc", "d",
                SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow(f(0)).SendKey CTRL_SHIFT_F4
            Case "aufsteigend", "afs", "auf", "ascending", "asc", "a",
                SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow(f(0)).SendKey CTRL_F4
        End Select
        """
    raise NotImplementedError


def erweiterte_sortierung(spalten, auf_absteigend):
    """
        Set lobjTabelle = Tabelle("")
        if isArray(Spalten) = true Then
            For each lmixSpalte in Spalten
                if typename(lmixSpalte) = "eger" Then
                    lmixSpalte = "#" & lmixSpalte
                End if
                lobjTabelle.ExtendColumn lstrSpalte
            Next
        else
            if typename(Spalten) = "eger" Then
                Spalten = "#" & Spalten
            End if
            lobjTabelle.SelectColumn Spalten
        End if
        """
    raise NotImplementedError


def sortierung(objekt, spalte, auf_absteigend):
    """
        if typeName(Spalte) = "eger" Then
            Spalte = "#" & Spalte
        End if
        Objekt.SelectColumn Spalte
        """
    raise NotImplementedError


def ausfuehren_und_sortieren(objekt, auf_absteigend):
    """
        Select Case lcase(AufAbsteigend)
            Case "a", "auf", "aufsteigend":
                Objekt.SapGuiButton("containername:=tbar\[1\]", "guicomponenttype:=40", "name:=btn\[28\]", "type:=GuIButton").Click
            Case "ab", "absteigend":
                Objekt.SapGuiButton("containername:=tbar\[1\]", "guicomponenttype:=40", "name:=btn\[40\]", "type:=GuIButton").Click
        End Select
        """
    raise NotImplementedError


def wert_aus_zelle(reihe, spalte):
    """
        Set Wert_aus_Zelle = SapGui_Tabellen.Objekt().GetCellData(Reihe, Spalte)
        return Wert_aus_Zelle(0, Spalte, FensterID);
        """
    raise NotImplementedError


def values_from_column(column: str, path: str = None, window_id: int = 0) -> list:
    """Reads the values from a defined column

        Parameters
        ----------
        column: int
            The column for the search
        path: str
            The path of the table. If not set, the default table will be used.
        window_id: int, default=0
            The ID of the window the checkbox is contained in
        Returns
        -------
            list
        """

    if path is None:
        path = elements.standard_table
    local_table = create(path, window_id)
    return [local_table.getCellValue(row_counter, column) for row_counter in range(local_table.rowCount)]


def sichtbar(fenster_id):
    """
        if(Elemente.Tabelle(FensterID).Exists())
            return True;
        End if
        return False;
        """
    raise NotImplementedError


def reihen(objekt):
    """
        Set lobjReferenz = Fenster_oder_Sitzung(Objekt)
        if lobjReferenz.SapGuiGrid("guicomponenttype:=201", "name:=shell").Exist(2) = true Then
            Tabelle_Reihen = lobjReferenz.SapGuiGrid("guicomponenttype:=201", "name:=shell").RowCount
        End if
        """
    raise NotImplementedError


def reklamationstabellen(objekt):
    """
        Tabellenobekt = false
        Set lobjReferenz = Fenster_oder_Sitzung(Objekt)
        lstrID = "id:=id:=/app/con\[[0-9]\]/ses\[[0-9]\]/wnd\[0\]/usr/ssubssubAREA06:SAPLCCM21:1001:SAPLCCM21:0101/tabsTABSTRIP/tabpAA_TAB7/ssubssubSUB_TAB:SAPLCCM21:1005:SAPLCCM21:0105/ssubCCM21_CUST_SUB:SAPLZJCFU_03_REKLAM:0100/cntlGV_ALV_0100_REKL_CONT/shellcont/shell",
        if lobjReferenz.SapGuiGrid(lstrID).Exist(2) = true Then
            set TabellenObjekt = lobjReferenz.SapGuiGrid(lstrID)
        else
            lobjReferenz.SapGuiTabStrip("guicomponenttype:=90", "name:=TABSTRIP", "type:=GuiTabStrip").select
            if lobjReferenz.SapGuiGrid(lstrID).Exist(2) = true Then
                set TabellenObjekt = lobjReferenz.SapGuiGrid(lstrID)
            End if
        End if
        """
    raise NotImplementedError


def auftragstabellen(objekt):
    """
        Tabellenobekt = false
        Set lobjReferenz = Fenster_oder_Sitzung(Objekt)
        larrIDs = array("1001-1005", "0101-0105")
        lstrID = id(0) & "usr/ssubAREA06:SAPLCCM21:" & SU & "01/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:" & SU & "05/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/cntlCONT_MSD_ORDER_0100/shellcont/shell",
        if lobjReferenz.SapGuiGrid(lstrID).Exist(2) = true Then
            set AuftragstabellenObjekt = lobjReferenz.SapGuiGrid(lstrID)
        else
            lobjReferenz.SapGuiTabStrip("guicomponenttype:=90", "name:=TABSTRIP", "type:=GuiTabStrip").select
            if lobjReferenz.SapGuiGrid(lstrID).Exist(2) = true Then
                set AuftragstabellenObjekt = lobjReferenz.SapGuiGrid(lstrID)
            End if
        End if
        """
    raise NotImplementedError


def finde_in_texttabelle(objekt, suchwert, fenster, spalte):
    """
        lReihenzaehler = 3
        do
            set lobjTextfeld = SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[" & Fenster & "\]").SapGuiLabel("id:=/app/con\[[0-9]\]/ses\[[0-9]\]/wnd\[1\]/usr/lbl\[" & Spalte & "," & lReihenzaehler & "\]")
            set lobjTextfeld_weiter = SapGuiSession("name:=ses\[[0-9]\]").SapGuiWindow("name:=wnd\[" & Fenster & "\]").SapGuiLabel("id:=/app/con\[[0-9]\]/ses\[[0-9]\]/wnd\[1\]/usr/lbl\[" & Spalte & "," & lReihenzaehler + 1 & "\]")
            if lobjTextfeld.GetROProperty("content") = Suchwert Then
                lobjTextfeld.SetFocus
                FensterX_gruenerHaken 1
                Exit do
            End if
            lReihenzaehler = lReihenzaehler + 1
        Loop while lobjTextfeld_weiter.Exist(2) = true
        """
    raise NotImplementedError


def find_row():
    pass


def standard_table_path() -> str:
    """Returns the path to the default table like the table in transaction se16.

        Returns
        -------
            str
        """
    return elements.standard_table


def is_displayed(path: str = None, window_id: int = 0) -> bool:
    """Checks if a table is displayed. If no path is set, the path of the default table is used.

        Parameters
        ----------
            path: str
                The path of the table. If not set, the path of the default table will be used.
            window_id: int, default=0
                The ID of the window the checkbox is contained in
            Returns
            -------
                bool
        """
    if path is None:
        path = elements.standard_table
    try:
        create(path, window_id)
        return True
    except Exception as ex:
        print(ex)
        return False
