from . import key
from .session import active
from . import transaction


def open(table_name: str = None):
    transaction.open('se16')
    if table_name is not None:
        active.session.findById(elements.se16_table_name_field).text = table_name
        key.enter()
