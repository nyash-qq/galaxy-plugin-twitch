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
async def test_owned_games(db_response, owned_games, installed_twitch_plugin, db_select_mock):
    db_select_mock.side_effect = [db_response]

    assert await installed_twitch_plugin.get_owned_games() == owned_games

    db_select_mock.assert_called_once()
