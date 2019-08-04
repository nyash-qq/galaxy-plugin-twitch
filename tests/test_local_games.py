import pytest
from galaxy.api.types import LocalGame, LocalGameState


def _db_installed_game(asin: str, is_installed: bool):
    return {
        "Id": asin
        , "Installed": int(is_installed)
    }


def _installed_game(game_id):
    return LocalGame(game_id, LocalGameState.Installed)


@pytest.mark.asyncio
@pytest.mark.parametrize("db_response, owned_games", [
    (Exception, [])
    , ([], [])
    , (
        [
            _db_installed_game("0c0126bf-8d56-46c0-ac10-fa07a4f2ad70", False)
            , _db_installed_game("8530321b-a8dd-4a74-baa3-24a247454c36", True)
        ]
        , [LocalGame("8530321b-a8dd-4a74-baa3-24a247454c36", LocalGameState.Installed)]
    )
])
async def test_owned_games(db_response, owned_games, installed_twitch_plugin, db_select_mock):
    db_select_mock.side_effect = [db_response]

    assert await installed_twitch_plugin.get_local_games() == owned_games

    db_select_mock.assert_called_once()
