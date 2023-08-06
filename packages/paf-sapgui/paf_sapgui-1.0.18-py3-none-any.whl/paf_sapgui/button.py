from .session import active
from . import window


def create(path_or_number: str | int, container: int = None, window_id: int = 0, click_it: bool = False):
    """
    Method to create a new button object. Such an object can be identified by a path (without including the session) or
    the number of the button. In SAP, many buttons are located in a container and are numbered. So if a number is used
    to identify the button, you also need to give the number of the container. In many cases, this is 0.
    :param path_or_number: Number as int, Path as str
    :param container: Only needed if a number is given, Int
    :param window_id: Optional, default is 0
    :param click_it: Boolean, default false. If is true the newly created button object is also clicked
    :return: The button
    """
    if isinstance(path_or_number, int):
        path_or_number = f'wnd[{window_id}]/tbar[{container}]/btn[{str(path_or_number)}]'
    local_element = active.session.findById(path_or_number)
    if click_it not in {False, None}:
        local_element.press()
    return local_element


def green_tick(window_id: int = 0):
    """
    Clicks the green tick button if it is included in the current mask
    :param window_id: The id of the window, default is 0
    :return: the button
    """
    return create(0, 0, window_id).press()


def execute(window_id: int = 0):
    """
    The execute button.
    :param window_id: The id of the window, default is 0
    :return: the button
    """
    return create(path_or_number=8, container=1, window_id=window_id).press()


def cancel(window_id: int = 0):
    """
    The cancel button
    :param window_id: The id of the window, default is 0
    :return: the button
    """
    return create(path_or_number=12, container=1, window_id=window_id).press()


def close(window_id: int = 0):
    """
    The close button
    :param window_id: The id of the window, default is 0
    :return: the button
    """
    return create(path_or_number=15, container=1, window_id=window_id).press()


def back(window_id: int = 0):
    """
    The back button
    :param window_id: The id of the window, default is 0
    :return: the button
    """
    return create(path_or_number=3, container=0, window_id=window_id).press()


def exists(path_or_number: str | int, container: int = 0, window_id: int = 0) -> bool:
    """
    Checks if a button, identified by the path or the number in combination with the container, exists and returns,
    true if the button is existing, otherwise it returns false
    :param path_or_number: Number as int, Path as str
    :param container: Only needed if a number is given, Int
    :param window_id: Optional, default is 0
    :return: True if button exists, false if not
    """
    try:
        create(path_or_number, container, window_id)
        return True
    except Exception as ex:
        print(ex)
        return False


def click(path_or_number: str | int, container: int = None, window_id: int = 0):
    """
    Clicks the button that is identified by its path or the number in combination with the container. Also returns
    the button object
    :param path_or_number: Number as int, Path as str
    :param container: Only needed if a number is given, Int
    :param window_id: Optional, default is 0
    :return the button
    """
    return create(path_or_number, container, window_id).press()


def get_object(path_or_number: str | int, container: int = None, window_id: int = 0):
    """
    This method is an alias for the create method. It returns the button object.
    :param path_or_number: Number as int, Path as str
    :param container: Only needed if a number is given, Int
    :param window_id: Optional, default is 0
    :return: the button
    """
    return create(path_or_number, container, window_id)


def save(window_id: int = 0):
    return create(11, 0, window_id).press()


def selection_options(window_id=0):
    create(2, 1, window_id).press()
