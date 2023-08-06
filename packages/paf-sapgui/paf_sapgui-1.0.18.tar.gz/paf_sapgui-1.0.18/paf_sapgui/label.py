"""ASIT - SES - SSO - Fields - Label

Provides different methods helping to work with sap gui labels

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


def create(column_or_path: int | str, row: int = None, window_id: int = 0) -> win32com.client.CDispatch:
    """Creates a new object of type label.

        Parameters
        ----------
        column_or_path: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is contained in
        Returns
        -------
            win32com.client.CDispatch
        """
    path = element.label_path(column_or_path, row, window_id)
    return active.session.findById(path)


def get_content(column_or_path: int | str, row: int = None, window_id: int = 0) -> str:
    """Returns the content of a label

        Parameters
        ----------
        column_or_path: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is contained in

        Returns
        -------
            str
            """
    local_label = create(column_or_path, row, window_id)
    return local_label.text


def set_focus(column_or_path: int | str, row: int = None, window_id: int = 0) -> None:
    """Sets the focus on a label

        Parameters
        ----------
        column_or_path: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is contained in

        Returns
        -------
            None
            """
    local_label = create(column_or_path, row, window_id)
    local_label.setFocus()


def exists(column_or_path: int | str, row: int = None, window_id: int = 0) -> bool:
    """Checks if a label exists

        Parameters
        ----------
        column_or_path: int | str
            A path to the checkbox or the column number
        row: int, optional
            The row. Only needed if a column (path_or_column) is provided.
        window_id: int, default=0
            The ID of the window the checkbox is contained in

        Returns
        -------
            bool
                """
    return create(column_or_path, row, window_id) is not None
