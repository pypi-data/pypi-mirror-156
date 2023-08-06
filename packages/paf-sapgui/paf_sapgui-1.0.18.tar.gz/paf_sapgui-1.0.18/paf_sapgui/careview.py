"""ASIT - SES - SSO - Component - Careview

Provides different methods helping to work with sap gui checkboxes

    Date / user / action
    05.05.2022 / ckoeste1 / initial creation

Methods:

    * create
"""
from . import menubar
from .session import active


def select_by_contents(contents):
    """Creates a new object of type checkbox.

            Parameters
            ----------
            contents: Any
        """
    menubar.open_by_positions([3, 0])
    row_counter = 0
    if isinstance(contents, dict):
        contents = [contents]

    try:
        table_cell = active.session.findById(
            f'wnd[1]/usr/tblSAPLSVIXTCTRL_SEL_FLDS/txtFIELD_TB-SCRTEXT_L[0,{row_counter}]')
        for content_dict in contents:
            if content_dict.keys()[0] == table_cell.text:
                active.session.findById('wnd[1]/usr/tblSAPLSVIXTCTRL_SEL_FLDS').getAbsoluteRow(
                    row_counter).selected = -1

    except Exception as ex:
        print(ex)

    row_counter = 0
    for content_dict in contents:
        content_dict.values()
        active.session.findById(
            f'wnd[1]/usr/tblSAPLSVIXTCTRL_QUERY/txtQUERY_TAB-BUFFER[3,{row_counter}]').text = \
            content_dict.values()[0]

    active.session.findById('wnd[1]/tbar[0]/btn[8]').press()
