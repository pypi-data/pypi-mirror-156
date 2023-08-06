"""ASIT - SES - SSO - Session - Transaction

Provides different methods for paf-sapgui-eltrans

    Date / user / action
    05.05.2022 / ckoeste1 / initial creation

Methods:

    * open
    * get_field_object
    * get_current

"""
import win32com.client

from ..session import active
from . import elements


def open(transaction_code: str):
    """Opens a transaction

        Parameters
        ----------
        transaction_code: str
            The transaction itself (with or without /n)

        """
    if "/n" not in transaction_code:
        transaction_code = f"/n{transaction_code}"

    active.session.findById(elements.ok_code).text = transaction_code
    active.session.findById("wnd[0]").sendVKey(0)


def get_field_object() -> win32com.client.CDispatch:
    """Returns the field as an object

        Returns
        -------
            win32com.client.CDispatch
        """
    return active.session.findById(elements.ok_code)


def get_current() -> str:
    """Should get the current transaction (when this method is implemented)

        Returns
        -------
            str
        """
    raise NotImplementedError
