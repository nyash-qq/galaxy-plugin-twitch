import os
import subprocess
from unittest.mock import ANY, call

import pytest
from galaxy.api.errors import InvalidCredentials
from galaxy.api.types import Authentication


@pytest.fixture()
def mocked_client_open(process_open_mock, mocked_install_path):
    yield process_open_mock

    twitch_exe_path = os.path.join(mocked_install_path, "Bin", "Twitch.exe")
    process_open_mock.assert_called_once_with(
        [twitch_exe_path]
        , creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        , cwd=mocked_install_path
        , shell=True
    )


@pytest.mark.asyncio
async def test_client_not_installed(
    twitch_plugin
    , os_path_exists_mock
    , webbrowser_opentab_mock
):
    with pytest.raises(InvalidCredentials):
        twitch_plugin._client_install_path = None
        await twitch_plugin.authenticate()

    os_path_exists_mock.assert_not_called()
    webbrowser_opentab_mock.assert_called_once_with("https://www.twitch.tv/downloads")


@pytest.mark.asyncio
async def test_client_not_found(
    installed_twitch_plugin
    , mocked_install_path
    , os_path_exists_mock
    , webbrowser_opentab_mock
):
    os_path_exists_mock.return_value = False

    with pytest.raises(InvalidCredentials):
        await installed_twitch_plugin.authenticate()

    os_path_exists_mock.assert_called_once_with(os.path.join(mocked_install_path, "Bin", "Twitch.exe"))
    webbrowser_opentab_mock.assert_called_once_with("https://www.twitch.tv/downloads")


@pytest.mark.asyncio
async def test_cookies_db_not_found(
    installed_twitch_plugin
    , mocked_install_path
    , os_path_exists_mock
    , mocked_client_open
):
    os_path_exists_mock.side_effect = [True, False]

    with pytest.raises(InvalidCredentials):
        await installed_twitch_plugin.authenticate()

    os_path_exists_mock.assert_has_calls([
        call(os.path.join(mocked_install_path, "Bin", "Twitch.exe"))
        , call(os.path.join(mocked_install_path, "Electron3", "Cookies"))
    ])


@pytest.mark.asyncio
@pytest.mark.parametrize("cookie", [
    None
    , ""
    , "{}"
    , "{%22id%22:%224815162342%22%2C%22version%22:2}"
    , "{%22displayName%22:%22test_name%22%2C%22version%22:2}"
])
async def test_no_user_info(
    cookie
    , installed_twitch_plugin
    , get_cookie_mock
    , mocked_client_open
):
    get_cookie_mock.return_value = cookie

    with pytest.raises(InvalidCredentials):
        await installed_twitch_plugin.authenticate()

    get_cookie_mock.assert_called_once_with(ANY, "twilight-user.desklight")


@pytest.mark.asyncio
async def test_authenticated(
    installed_twitch_plugin
    , get_cookie_mock
):
    get_cookie_mock.return_value = "{%22displayName%22:%22test_name%22%2C%22id%22:%224815162342%22%2C%22version%22:2}"

    assert Authentication(user_id="4815162342", user_name="test_name") == await installed_twitch_plugin.authenticate()

    get_cookie_mock.assert_called_once_with(ANY, "twilight-user.desklight")
