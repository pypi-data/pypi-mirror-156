import os
import time

import win32com.client

from . import active
from .types import SapSystems


def session_data(system: SapSystems = None, user: str = None, password: str = None,
                 client: str = None, language: str = None) -> dict:
    """

    :param system:
    :param user:
    :param password:
    :param client:
    :param language:
    :return:
    """
    return_data = {}
    if system is not None:
        active.session_data["system"] = system
    return_data = {'system': active.session_data["system"]}
    if user is not None:
        active.session_data["user"] = user
    return_data = {'user': active.session_data["user"]}
    if password is not None:
        active.session_data["password"] = password
    return_data = {'password': active.session_data["password"]}
    if client is not None:
        active.session_data["client"] = client
    return_data = {'client': active.session_data["client"]}
    if language is not None:
        active.session_data["language"] = language
    return_data = {'language': active.session_data["language"]}

    return return_data


def destroy():
    """

    :return:
    """
    active.session = None
    active.session_data = {}
    print("I have just destroyed the session")


def error():
    """

    :return:
    """
    # Close the sap _session and exit the application
    raise NotImplementedError


def _wait_for_sap_gui() -> win32com.client.CDispatch:
    """

    :return:
    """
    wait_in_seconds = 2
    tries = 10
    for _ in range(tries):
        try:
            return win32com.client.GetObject("SAPGUI")
        except Exception:
            print(f"SAP Gui still not found. Waiting another {wait_in_seconds} seconds!")
        time.sleep(wait_in_seconds)
    print('Cannot start SAP GUI')
    exit(0)


def _open_sap_gui():
    """

    :return:
    """
    killed = os.system("tskill saplogon.exe")
    print(f"Killed {killed}")

    string_for_sapshcut = f"start sapshcut.exe " \
                          f"-system=\"{active.session_data['system'].value}\" " \
                          f"-sysname=\"{active.session_data['system'].value}\" " \
                          f"-language={active.session_data['language']} " \
                          f"-client={active.session_data['client']} " \
                          f"-user={active.session_data['user']} " \
                          f"-password={active.session_data['password']} " \
                          f"-maxgui " \
                          f"-type=\"Transaction\" " \
                          f"-command=\"SESSION_MANAGER\" " \
                          f"-title=\"Automation\""

    os.system(string_for_sapshcut)
    # os.system(
    # f"start sapshcut.exe -system=\"{active.session_data['system'].value}\" "
    # f"-sysname=\"{active.session_data['system'].value}\" -language={active.session_data['language']} "
    # f"-client={active.session_data['client']} -user={active.session_data['user']} "
    # f"-password={active.session_data['password']} -maxgui -type=\"Transaction\" -command=\"SESSION_MANAGER\" "
    # f"-title=\"Automation\"")


def _get_application(sap_gui_auto: win32com.client.CDispatch) -> win32com.client.CDispatch:
    """

    :param sap_gui_auto:
    :return:
    """
    if type(sap_gui_auto) != win32com.client.CDispatch:
        print('It was not possible to get the application')
        exit(1)

    application = sap_gui_auto.GetScriptingEngine
    if type(application) != win32com.client.CDispatch:
        print('It was not possible to get the application')
        exit(1)

    return application


def _get_connection(application: win32com.client.CDispatch) -> win32com.client.CDispatch:
    """

    :param application:
    :return:
    """
    seconds_to_wait = 2
    tries = 10
    connection = None

    for _ in range(tries):
        try:
            connection = application.Children(0)
            if connection is not None:
                break
        except Exception:
            print(
                f'I had problems finding the connection. Waiting another {seconds_to_wait} seconds and '
                f'trying again.')
        time.sleep(seconds_to_wait)

    if type(connection) != win32com.client.CDispatch:
        print('It was not possible to get the connection')
        exit(1)

    return connection


def _get_session(connection: win32com.client.CDispatch):
    """

    :param connection:
    :return:
    """
    wait_in_seconds = 2
    tries = 10

    for _ in range(tries):
        try:
            active.session = connection.Children(0)
            break
        except Exception:
            print(
                f'Up to now, I have found no _session. Waiting for another {wait_in_seconds} seconds and '
                f'trying again.')
        time.sleep(wait_in_seconds)
    if type(active.session) != win32com.client.CDispatch:
        print('It was not possible to get the _session')
        exit(1)

    print("Session is starting")


def create():
    """
        SAP wird über sapshcut mit den SAP Credentials gestartet. Bei SSO wird IMMER der Login vom SSO-User genutzt,
        abweichende Login-Daten sind nicht möglich. Da müsste man so wie bei AA ein Login-Script bauen.
        Sollte bereits eine SAP Session existieren dann wird sich dort draufgehangen
        und keine neue SAP-Instanz geöffnet.

        Parameter:

        Rückgabewerte:
            - Erfolgreich = True + Log in einer Liste
            - nicht Erfolgreich = False + Log in einer Liste
    """

    try:
        _create()
    except Exception as ex:
        print(f'Unbekannter Fehler beim Start von SAP ({ex})')


def _create():
    if _check_for_open_sessions():  # Existiert bereits eine Session wird sich mit der verbunden
        print("SAP Session existiert bereits, verbunden")
        return
    if _preconditions() is False:
        print('Preconditions where not met!')
        exit(1)

    _open_sap_gui()

    sap_gui_auto = _wait_for_sap_gui()

    # Ab hier folgt grundsätzlich eine 1:1 Übersetzung aus den üblichen VBS Scripten
    # mit zusätzlichen Fehlerabfragen und Delays

    application = _get_application(sap_gui_auto)

    connection = _get_connection(application)

    _get_session(connection)


def _check_for_open_sessions() -> bool:
    """

    :rtype: bool
    :return:
    """
    try:
        sap_gui = win32com.client.GetObject("SAPGUI")
        application = sap_gui.GetScriptingEngine
        connection = application.Children(0)
        active.session = connection.Children(0)
        return True
    except Exception as ex:
        print(ex)
        return False


def _preconditions():
    """
    """
    if active.session_data["system"] is None:
        print("You need to set the system we should log on.")
        return False

    if active.session_data["user"] is None:
        print("No user name was provided!")
        return False

    if active.session_data["password"] is None:
        print("The password is missing")
        return False

    if active.session_data["client"] == "":
        active.session_data["client"] = "010"

    if active.session_data["language"] in {"", None}:
        active.session_data["language"] = "DE"

    return True
