"""ASIT - SES - SSO - Fields - Radiobuttons

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

from typing import Any

from .session import active
from . import window


def create(path_or_column: int | str, row: int = None, value: Any = None, window_id: int = 0):
    raise NotImplementedError()


def activate(path: str, window_id=0):
    """Activates a radiobutton.

            Parameters
            ----------
            path: str
                A path to the checkbox or the column number
            window_id: int, default=0
                The ID of the window the checkbox is contained in

            Returns
            -------
                bool
                    """
    path = window.check_id(path, window_id)
    active.session.findById(path).select()
