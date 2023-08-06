"""ASIT - SES - SSO - Fields

This is the basic package for the _fields that makes it possible to create a field with the provided type.

    Date / user / action
    06.05.2022 / ckoeste1 / initial creation

classes:
    * field_types

Methods:

    * create

"""
import contextlib
import re
from typing import Any, NoReturn

import win32com.client

from ..session import active
from .types import FieldTypes
from .. import button, checkbox, radiobutton, tab, textfield, table


class Field:
    def __init__(self):
        try:
            self._path = None
            self._object = None
            self._type = None
            self._additional = None
        except Exception as ex:
            print(ex)

    def _definition_checks(self):
        if self._path is None:
            raise ValueError("Missing the basic value for the path, cannot go on!")
        self._the_type()
        self._the_object()

    def _the_object(self):
        if self._object is None:
            self._object = active.session.findById(self._path)

    def _the_type(self):
        if self._type is not None:
            return
        if "ctxt" in self._path:
            self._type = FieldTypes.gui_c_text_field
        if "txt" in self._path and "ctxt" not in self._path:
            self._type = FieldTypes.gui_text_field
        if "btn" in self._path:
            self._type = FieldTypes.gui_button
        if "cntl" in self._path:
            if "__" not in self._path:
                self._type = FieldTypes.gui_textarea
            if "__" in self._path:
                self._additional = self._path[self._path.index("__"):].replace("__", "")
                self._path = self._path.replace(f"__{self._additional}", "")
                self._type = FieldTypes.gui_control_button

    def type(self):
        self._definition_checks()
        return self._type

    def path(self):
        self._definition_checks()
        return self._path()

    def object(self):
        self._definition_checks()
        return self._object

    def _set_value(self, value: Any = None):
        if isinstance(self._type, (type(types.FieldTypes.gui_c_text_field), type(types.FieldTypes.gui_text_field))):
            self._object.text = value
        return self

    def _get_value(self):
        if isinstance(self._type, (type(types.FieldTypes.gui_c_text_field), type(types.FieldTypes.gui_text_field))):
            return self._object.text

    def value(self, value: Any = None):
        try:
            self._definition_checks()
            if value is None:
                return self._get_value()
            self._set_value(value)
        except ValueError as ex:
            print(f"An error occurred while setting the value {value} of the element '{self._path}' ({ex})")

    def click_cell(self, row_number: int, column: str, double_click: bool = False):
        try:
            self._definition_checks()
            if double_click:
                self._object.doubleClick(str(row_number), column)
            else:
                self._object.click(str(row_number), column)
            return self
        except Exception as ex:
            print(f"An error occurred while clicking the cell in row {row_number} and column {column} of"
                  f" the element '{self._path}' ({ex})")

    def row(self, row_number: int):
        try:
            self._definition_checks()
            self._object.selectedRows = str(row_number)
            return self
        except Exception as ex:
            print(f"An error occurred while setting the row {row_number} of the element '{self._path}' ({ex})")
            return self

    def activate_row(self, search_value: str | None):
        self._definition_checks()
        if search_value is not None:
            self.find_row(search_value=search_value)
        self._object.doubleClickCurrentCell()

    def find_row(self, search_value: str, activate: bool = False):
        self._definition_checks()
        self._object.selectedRows = "0"
        active.session.findById("wnd[0]").sendVKey(71)
        active.session.findById("wnd[1]/usr/txtGS_SEARCH-VALUE").text = search_value
        active.session.findById("wnd[1]/usr/txtGS_SEARCH-VALUE").caretPosition = 7
        active.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        active.session.findById("wnd[1]/tbar[0]/btn[12]").press()
        if activate:
            self.activate_row(search_value=None)

    def find_row_by_list(self, search_values: list):
        self._definition_checks()
        found_row = None
        for row in range(self._object.rowCount):
            found = []
            for search_value in search_values:
                value_from_row = self._object.getCellValue(row, search_value["column"])
                if value_from_row == search_value["value"]:
                    found.append(True)
                else:
                    found.append(False)
            if False not in found:
                return row

        return None

    def caret_position(self, position: int = None):
        try:
            if position is None:
                return self._object.caretPosition
            self._object.caretPosition = position
        except Exception as ex:
            if position is None:
                print(
                    f"An error occurred while getting the caret position of element '{self._path}' ({ex})")
            else:
                print(
                    f"An error occurred while setting the caret position to {position} of element '{self._path}' ({ex})")

    def row_count(self) -> int:
        try:
            self._definition_checks()
            return self._object.rowCount
        except Exception as ex:
            print(f"An error occurred while getting the row count of element '{self._path}'")

    def click(self):
        try:
            self._definition_checks()
            if self._additional is not None:
                self._object.pressButton(self._additional)
            else:
                self._object.press()
        except Exception as ex:
            print(f"An error occurred while trying to click the element '{self._path}' ({ex})")

    def select(self):
        try:
            self._definition_checks()
            self._object.select()
        except Exception as ex:
            print(f"An error occurred while selecting the tab '{self._path}' ({ex})")

    def get_values_from_columns_by_search_string(self, search_string, columns: dict):
        return_values = []
        self._definition_checks()
        self._object.selectedRows = "0"
        active.session.findById("wnd[0]").sendVKey(71)
        active.session.findById("wnd[1]/usr/txtGS_SEARCH-VALUE").text = search_string
        active.session.findById("wnd[1]/usr/chkGS_SEARCH-SHOW_HITS").selected = -1
        active.session.findById("wnd[1]/usr/txtGS_SEARCH-VALUE").text = search_string
        active.session.findById("wnd[1]/usr/chkGS_SEARCH-SHOW_HITS").setFocus()
        active.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        active.session.findById("wnd[1]/usr/txtGS_SEARCH-SEARCH_INFO").setFocus()
        hits = int(re.sub("\D.*: 1 von ", "", active.session.findById("wnd[1]/usr/txtGS_SEARCH-SEARCH_INFO").text))
        active.session.findById("wnd[1]/tbar[0]/btn[12]").press()
        row = self._object.currentCellRow

        for counter in range(hits):
            row += counter
            self._object.selectedRows = str(row)
            temp_dict = {key: self._object.getCellValue(row, columns[key]) for key in columns}

            return_values.append(temp_dict)

    def position_in_text(self, char_from: int, char_to: int) -> NoReturn:
        # Set in text
        try:
            self._definition_checks()
            self._object.setSelectionIndexes(char_from, char_to)
        except Exception as ex:
            print(f"An error occurred while trying to set the cursor to the position from {char_from} to {char_to} in "
                  f"the text of element '{self._path}' ({ex})")


def set_value(path: str, value: Any, field_type: types.FieldTypes = None, window_id: int = 0) -> NoReturn:
    create(path=path, value=value, field_type=field_type, window_id=window_id)


def create(path: str, field_type: types.FieldTypes = None, value: Any = None,
           window_id: int = 0) -> win32com.client.CDispatch:
    """Creates a new field

            Parameters
            ----------
            path: str
                A path to the checkbox or the column number
            field_type: field_types, default = None
                The type of the new field. If no type is provided, the new field will be of type gui_c_text_field
            value: Any, optional
                If a value is set, the new field will get that value
            window_id: int, default=0
                The ID of the window the checkbox is contained in
            Returns
            -------
                win32com.client.CDispatch
        """

    if field_type is None:
        # ctx = Textfield
        # btn = Button
        # tbar =
        if "ctx" in path:
            field_type = types.FieldTypes.gui_c_text_field
        if "btn" in path:
            field_type = types.FieldTypes.gui_button
    if field_type == types.FieldTypes.gui_c_text_field:
        return textfield.create(path_or_position=path, value=value, window_id=window_id)
    if field_type == types.FieldTypes.gui_tab_strip:
        return tab.create(path, value, window_id)
    if field_type == types.FieldTypes.gui_check_box:
        return checkbox.create(path, value, window_id)
    if field_type == types.FieldTypes.gui_radio_button:
        return radiobutton.create(path, value, window_id)
    if field_type == types.FieldTypes.gui_button:
        if value is not None:
            return button.create(path_or_number=path, window_id=window_id, click_it=value)
        return button.create(path_or_number=path, window_id=window_id)
