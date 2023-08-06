from enum import Enum


class FieldTypes(Enum):
    """Holds the different field types of the sap gui"""
    gui_c_text_field = 32,
    gui_text_field = 31,
    gui_label = 30,
    gui_tab_strip = 90,
    gui_check_box = 42,
    gui_radio_button = 41,
    gui_button = 40,
    gui_textarea = -2
    gui_control_button = -3
