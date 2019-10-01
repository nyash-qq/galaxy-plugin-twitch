from unittest.mock import MagicMock, PropertyMock

import pytest

from twitch_plugin import TwitchPlugin


@pytest.fixture()
def invalid_path():
    return "invalid_path"


@pytest.fixture()
def os_path_exists_mock(mocker, invalid_path):
    return mocker.patch("os.path.exists", side_effect=lambda path: path and invalid_path not in path)


@pytest.fixture()
def manifest_mock(mocker):
    return mocker.patch("twitch_plugin.TwitchPlugin._read_manifest")


@pytest.fixture()
def mocked_install_path():
    return "mocked_install_path"


@pytest.fixture()
def get_cookie_mock(mocker):
    return mocker.patch("twitch_plugin.get_cookie")


@pytest.fixture()
def db_select_mock(mocker):
    return mocker.patch("twitch_plugin.db_select")


@pytest.fixture()
def webbrowser_opentab_mock(mocker):
    return mocker.patch("webbrowser.open_new_tab")


@pytest.fixture()
def process_open_mock(mocker):
    return mocker.patch("subprocess.Popen")


@pytest.fixture()
def is_launcher_installed_mock():
    return PropertyMock()


@pytest.fixture()
def cookies_db_path_mock():
    cookies_db_path = PropertyMock(return_value="cookies_db_path")
    yield cookies_db_path


@pytest.fixture()
def twitch_launcher_mock(is_launcher_installed_mock, cookies_db_path_mock):
    twitch_launcher = MagicMock(spec=())
    type(twitch_launcher).is_installed = is_launcher_installed_mock
    type(twitch_launcher).cookies_db_path = cookies_db_path_mock
    twitch_launcher.update_install_path = MagicMock()
    twitch_launcher.start_client = MagicMock()
    twitch_launcher.launch_game = MagicMock()
    twitch_launcher.uninstall_game = MagicMock()
    return twitch_launcher


@pytest.fixture()
def twitch_plugin_mock(manifest_mock) -> TwitchPlugin:
    manifest_mock.return_value = {
        "name": "Galaxy Twitch plugin"
        , "platform": "twitch"
        , "guid": "8b831aed-dd5f-c0c5-c843-41f9751f67a2"
        , "version": "0.1"
        , "description": "Galaxy Twitch plugin"
        , "author": "nyash"
        , "email": "nyash.qq@gmail.com"
        , "url": "https://github.com/nyash-qq/galaxy-plugin-twitch"
        , "script": "twitch_plugin.py"
    }
    return TwitchPlugin(MagicMock(), MagicMock(), "handshake_token")


@pytest.fixture()
async def twitch_plugin(twitch_plugin_mock) -> TwitchPlugin:
    yield twitch_plugin_mock

    await twitch_plugin_mock.shutdown()


@pytest.fixture()
async def installed_twitch_plugin(
    twitch_plugin_mock
    , twitch_launcher_mock
    , is_launcher_installed_mock
    , cookies_db_path_mock
    , os_path_exists_mock
) -> TwitchPlugin:
    is_launcher_installed_mock.return_value = True
    twitch_plugin_mock._launcher_client = twitch_launcher_mock

    yield twitch_plugin_mock

    await twitch_plugin_mock.shutdown()
