import asyncio
from unittest.mock import MagicMock

import pytest

from twitch_plugin import TwitchPlugin


@pytest.fixture()
def os_path_exists_mock(mocker):
    return mocker.patch("os.path.exists")


@pytest.fixture()
def manifest_mock(mocker):
    return mocker.patch("twitch_plugin.TwitchPlugin._read_manifest")


@pytest.fixture()
def mocked_install_path():
    return "mocked_install_path"


@pytest.fixture()
def db_cookies_path_mock(mocker):
    return mocker.patch("twitch_plugin.TwitchPlugin._db_cookies_path")


@pytest.fixture()
def get_cookie_mock(mocker):
    return mocker.patch("twitch_plugin.get_cookie")


@pytest.fixture()
def twitch_plugin_mock(manifest_mock) -> TwitchPlugin:
    manifest_mock.return_value = {
        "name": "Galaxy Twitch plugin"
        , "platform": "generic"
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

    twitch_plugin_mock.shutdown()
    await asyncio.sleep(0)


@pytest.fixture()
async def installed_twitch_plugin(twitch_plugin_mock, mocked_install_path, os_path_exists_mock) -> TwitchPlugin:
    twitch_plugin_mock._client_install_path = mocked_install_path
    os_path_exists_mock.return_value = True
    yield twitch_plugin_mock

    twitch_plugin_mock.shutdown()
    await asyncio.sleep(0)
