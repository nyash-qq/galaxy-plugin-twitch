import pytest
from galaxy.api.consts import LicenseType
from galaxy.api.types import Game, LicenseInfo


def _db_owned_game(game_id, title):
    return {
        "ProductIdStr": game_id
        , "ProductTitle": title
    }


def _owned_game(game_id, game_title):
    return Game(game_id, game_title, None, LicenseInfo(LicenseType.SinglePurchase))


@pytest.fixture()
def get_local_games_mock(mocker):
    return mocker.patch("twitch_plugin.TwitchPlugin._get_local_games")


@pytest.mark.asyncio
@pytest.mark.parametrize("db_response, owned_games", [
    (Exception, [])
    , ([], [])
    , (
        [
            _db_owned_game("0c0126bf-8d56-46c0-ac10-fa07a4f2ad70", "The Banner Saga")
            , _db_owned_game("8530321b-a8dd-4a74-baa3-24a247454c36", "The Banner Saga 2")
            , _db_owned_game("f41d91c5-83b4-40e1-869e-01a0d6056f97", "Gone Home")
        ], [
            _owned_game("0c0126bf-8d56-46c0-ac10-fa07a4f2ad70", "The Banner Saga")
            , _owned_game("8530321b-a8dd-4a74-baa3-24a247454c36", "The Banner Saga 2")
            , _owned_game("f41d91c5-83b4-40e1-869e-01a0d6056f97", "Gone Home")
        ]
    )
])
async def test_owned_games(
    db_response
    , owned_games
    , installed_twitch_plugin
    , db_select_mock
    , get_local_games_mock
):
    db_select_mock.side_effect = [db_response]

    installed_twitch_plugin.handshake_complete()

    assert await installed_twitch_plugin.get_owned_games() == owned_games

    db_select_mock.assert_called_once()


_GAME_ID = "game-id"
_GAME_TITLE = "game title"


@pytest.mark.asyncio
@pytest.mark.parametrize("old_game_state, new_game_state, expected_calls", [
    # not owned -> not owned
    ([], [], [])
    # not owned -> owned
    , ([], [_db_owned_game(_GAME_ID, _GAME_TITLE)], ["add"])
    # owned -> owned
    , (
        [_db_owned_game(_GAME_ID, _GAME_TITLE)]
        , [_db_owned_game(_GAME_ID, _GAME_TITLE)]
        , []
    )
    # owned -> not owned
    , ([_db_owned_game(_GAME_ID, _GAME_TITLE)], [], ["remove"])
])
async def test_owned_game_update(
    old_game_state
    , new_game_state
    , expected_calls
    , installed_twitch_plugin
    , db_select_mock
    , get_local_games_mock
    , mocker
):
    # prepare
    db_select_mock.return_value = old_game_state
    game_added_mock = mocker.patch("twitch_plugin.TwitchPlugin.add_game")
    game_removed_mock = mocker.patch("twitch_plugin.TwitchPlugin.remove_game")

    installed_twitch_plugin.handshake_complete()
    assert db_select_mock.call_count == 1

    # test
    db_select_mock.return_value = new_game_state

    installed_twitch_plugin.tick()
    assert db_select_mock.call_count == 2

    if "add" in expected_calls:
        game_added_mock.assert_called_once_with(_owned_game(_GAME_ID, _GAME_TITLE))
    else:
        game_added_mock.assert_not_called()

    if "remove" in expected_calls:
        game_removed_mock.assert_called_once_with(_GAME_ID)
    else:
        game_removed_mock.assert_not_called()
