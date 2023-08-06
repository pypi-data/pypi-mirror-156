"""ASIT - SES - SSO - Fields - Checkbox

Provides different methods helping to work with sap gui checkboxes

    Date / user / action
    05.05.2022 / ckoeste1 / initial creation

Methods:

    * create
    * activate
    * deactivate
    * activate_if_deactivated
    * deactivate_if_activated
    * get_status
    * check_if_is_activated
    * check_if_is_deactivated

"""

import win32com.client

from .session import active
from . import element


def create(path_or_column: int | str, activate_cbx: bool = None, row: int = None, window_id: int = 0) \
        -> win32com.client.CDispatch:
    """Creates a new object of type checkbox.

        Parameters
        ----------
        path_or_column: int | str
            A path to the checkbox or the column number
        activate_cbx: bool, default = None
            If a value is provided, the checkbox is activated or deactivated
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is contained in
        Returns
        -------
            win32com.client.CDispatch
    """
    path = element.checkbox_path(path_or_column, row, window_id)

    local_field = active.session.findById(path)

    if activate_cbx is not None:
        value = 1 if activate_cbx else 0
        local_field.selected = value

    return local_field


def activate(path_or_column: int | str, row: int = None, window_id: int = 0):
    """Activates a checkbox

            Parameters
            ----------
            path_or_column: int | str
                A path to the checkbox or the column number
            row: int, optional
                The row. Only needed if a column (path_or_column) is provided.
            window_id: int, default=0
                The ID of the window the checkbox is contained in
            Returns
            -------
                None
            """
    local_field = create(path_or_column, row, window_id)

    local_field.selected = 1


def deactivate(path_or_column: int | str, row: int = None, window_id: int = 0):
    """Deactivates a checkbox

            Parameters
            ----------
            path_or_column: int | str
                A path to the checkbox or the column number
            row: int, optional
                The row. Only needed if a column (path_or_column) is provided.
            window_id: int, default=0
                The ID of the window the checkbox is contained in
            Returns
            -------
                None
        """
    path = element.checkbox_path(path_or_column, row, window_id)
    local_field = create(path, row, window_id)
    local_field.selected = -1


def activate_if_deactivated(path_or_column: int | str, row: int = None, window_id: int = 0):
    """Deactivates a checkbox

        Parameters
        ----------
        path_or_column: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is contained in
        Returns
        -------
            None
    """
    path = element.checkbox_path(path_or_column, row, window_id)
    local_field = create(path, row, window_id)
    if local_field.selected == -1:
        local_field.selected = 0


def deactivate_if_activated(path_or_column: int | str, row: int = None, window_id: int = 0):
    """Deactivates a checkbox only if it is activated

        Parameters
        ----------
        path_or_column: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is displayed in
        Returns
        -------
            bool
    """
    path = element.checkbox_path(path_or_column, row, window_id)
    local_field = create(path, row, window_id)
    if local_field.selected == 0:
        local_field.selected = -1


def get_status(path_or_column: int | str, row: int = None, window_id: int = 0) -> bool:
    """Gets the status of the provided checkbox. If it is activated, true is returned. If it is NOT activated, false
        is returned.

        Parameters
        ----------
        path_or_column: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is displayed in
        Returns
        -------
            bool
        """
    path = element.checkbox_path(path_or_column, row, window_id)
    local_field = create(path, row, window_id)
    return local_field.selected != -1


def check_if_is_activated(path_or_column: int | str, row: int = None, window_id: int = 0) -> bool:
    """Checks if the provided checkbox is active and returns true. Otherwise, false is returned
            is returned.

            Parameters
            ----------
            path_or_column: int | str
                A path to the checkbox or the column number
            row: int, optional
                The row. Only needed if a column (path_or_column) is provided.
            window_id: int, default=0
                The ID of the window the checkbox is displayed in
            Returns
            -------
                bool
            """
    path = element.checkbox_path(path_or_column, row, window_id)
    local_field = create(path, row, window_id)
    return local_field.selected == 0


def check_if_is_deactivated(path_or_column: int | str, row: int = None, window_id: int = 0) -> bool:
    """Checks if the provided checkbox is deactivated and returns true. Otherwise, false is returned
                is returned.

                Parameters
                ----------
                path_or_column: int | str
                    A path to the checkbox or the column number
                row: int, optional
                    The row. Only needed if a column (path_or_column) is provided.
                window_id: int, default=0
                    The ID of the window the checkbox is displayed in
                Returns
                -------
                    bool
                """
    path = element.checkbox_path(path_or_column, row, window_id)
    local_field = create(path, row, window_id)
    return local_field.selected == -1
