from unittest.mock import ANY

import pytest
from galaxy.api.errors import InvalidCredentials
from galaxy.api.types import Authentication


@pytest.mark.asyncio
async def test_client_not_installed(twitch_plugin, webbrowser_opentab_mock):
    with pytest.raises(InvalidCredentials):
        await twitch_plugin.authenticate()

    webbrowser_opentab_mock.assert_called_once_with("https://www.twitch.tv/downloads")


@pytest.mark.asyncio
async def test_cookies_db_not_found(
    installed_twitch_plugin
    , twitch_launcher_mock
    , cookies_db_path_mock
    , os_path_exists_mock
):
    with pytest.raises(InvalidCredentials):
        await installed_twitch_plugin.authenticate()

    cookies_db_path_mock.assert_called_once_with()
    os_path_exists_mock.assert_called_once_with(cookies_db_path_mock.return_value)
    twitch_launcher_mock.start_client.assert_called_once_with()


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
    , twitch_launcher_mock
):
    get_cookie_mock.return_value = cookie

    with pytest.raises(InvalidCredentials):
        await installed_twitch_plugin.authenticate()

    get_cookie_mock.assert_called_once_with(ANY, "twilight-user.desklight")
    twitch_launcher_mock.start_client.assert_called_once_with()


@pytest.mark.asyncio
async def test_authenticated(
    installed_twitch_plugin
    , get_cookie_mock
    , mocker
):
    get_cookie_mock.return_value = "{%22displayName%22:%22test_name%22%2C%22id%22:%224815162342%22%2C%22version%22:2}"
    store_credentials_mock = mocker.patch("twitch_plugin.TwitchPlugin.store_credentials")

    assert Authentication(user_id="4815162342", user_name="test_name") == await installed_twitch_plugin.authenticate()

    get_cookie_mock.assert_called_once_with(ANY, "twilight-user.desklight")
    store_credentials_mock.assert_called_once()
