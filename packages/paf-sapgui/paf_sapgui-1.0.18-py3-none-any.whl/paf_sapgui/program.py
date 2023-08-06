"""ASIT - SES - SSO - Programs - Program

Provides different methods helping to work with sap gui paf_sapgui_elprog

    Date / user / action
    05.05.2022 / ckoeste1 / initial creation

Methods:

    * start

"""

from . import transaction
from .session import active


def start(program_name: str, variant: str = None):
    """Starts a program. If a variant is provided, this variant is selected

        Parameters
        ----------
        program_name: str
            The name of the program
        variant: str, default = None
            Should set a variant if one is provided.
        """
    transaction.open('sa38')
    active.session.findById('wnd[0]/usr/lblRS38M-PROGRAMM').activate(program_name)
    if variant is not None:
        active.session.findById("wnd[0]/tbar[1]/btn[18]").press()
        active.session.findById("wnd[1]/usr/ctxtRS38M-SELSET").text = variant
        active.session.findById("wnd[1]/usr/ctxtRS38M-SELSET").caretPosition = 7
        active.session.findById("wnd[1]/tbar[0]/btn[0]").press()
