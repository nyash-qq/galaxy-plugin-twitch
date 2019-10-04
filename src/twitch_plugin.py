import json
import logging
import os
import sys
import webbrowser
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, TypeVar, Union
from urllib import parse

from galaxy.api.consts import LocalGameState, Platform
from galaxy.api.errors import InvalidCredentials
from galaxy.api.plugin import create_and_run_plugin, Plugin
from galaxy.api.types import Authentication, Game, LicenseInfo, LicenseType, LocalGame, NextStep
from galaxy.proc_tools import process_iter

from twitch_db_client import db_select, get_cookie
from twitch_launcher_client import TwitchLauncherClient


def is_windows() -> bool:
    return sys.platform == "win32"


T = TypeVar("T")


def os_specific(unknown, win: Optional[T] = None, mac: Optional[T] = None) -> Optional[T]:
    return {"win32": win, "darwin": mac}.get(sys.platform, unknown)


@dataclass
class InstalledGame(LocalGame):
    install_path: str


class TwitchPlugin(Plugin):

    @staticmethod
    def _read_manifest() -> str:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json")) as manifest:
            return json.load(manifest)

    @property
    def _db_owned_games(self) -> str:
        return str(os_specific(
            win=os.path.join(os.path.expandvars("%APPDATA%"), "Twitch", "Games", "Sql", "GameProductInfo.sqlite")
            , unknown=""
        ))

    @property
    def _db_installed_games(self) -> str:
        return str(os_specific(
            win=os.path.join(os.path.expandvars("%PROGRAMDATA%"), "Twitch", "Games", "Sql", "GameInstallInfo.sqlite")
            , unknown=""
        ))

    def _get_user_info(self) -> Optional[Dict[str, str]]:
        cookies_db_path = self._launcher_client.cookies_db_path
        if not cookies_db_path:
            logging.warning("Cookies db not found")
            return None

        user_info_cookie = get_cookie(cookies_db_path, "twilight-user.desklight")
        if not user_info_cookie:
            return {}

        user_info = json.loads(parse.unquote(user_info_cookie))
        if not user_info:
            return {}

        return user_info

    def _get_owned_games(self) -> Dict[str, Game]:
        try:
            return {
                row["ProductIdStr"]: Game(
                    game_id=row["ProductIdStr"]
                    , game_title=row["ProductTitle"]
                    , dlcs=None
                    , license_info=LicenseInfo(LicenseType.SinglePurchase)
                )
                for row in db_select(
                    db_path=self._db_owned_games
                    , query="select ProductIdStr, ProductTitle from DbSet"
                )
            }
        except Exception:
            logging.exception("Failed to get owned games")
            return {}

    def _update_owned_games(self) -> None:
        owned_games = self._get_owned_games()

        for game_id in self._owned_games_cache.keys() - owned_games.keys():
            self.remove_game(game_id)

        for game_id in (owned_games.keys() - self._owned_games_cache.keys()):
            self.add_game(owned_games[game_id])

        self._owned_games_cache = owned_games

    def _get_installed_games(self) -> Dict[str, InstalledGame]:
        try:
            return {
                row["Id"]: InstalledGame(
                    game_id=row["Id"]
                    , local_game_state=LocalGameState.Installed
                    , install_path=row["InstallDirectory"]
                )
                for row in db_select(
                    db_path=self._db_installed_games
                    , query="select Id, Installed, InstallDirectory from DbSet"
                )
                if row.get("Installed") and os.path.exists(row.get("InstallDirectory", ""))
            }
        except Exception:
            logging.exception("Failed to get local games")
            return {}

    def _get_local_games(self) -> Dict[str, InstalledGame]:
        installed_games = self._get_installed_games()
        if not installed_games:
            return installed_games

        running_processes = [
            proc_info.binary_path
            for proc_info in process_iter()
            if proc_info and proc_info.binary_path
        ]

        def is_game_running(game_install_path) -> bool:
            for process_path in running_processes:
                if process_path.startswith(game_install_path):
                    return True
            return False

        for installed_game in installed_games.values():
            if is_game_running(installed_game.install_path):
                installed_game.local_game_state |= LocalGameState.Running

        return installed_games

    def _update_local_games_state(self) -> None:
        local_games = self._get_local_games()

        for game_id in self._local_games_cache.keys() - local_games.keys():
            self.update_local_game_status(LocalGame(game_id, LocalGameState.None_))

        for game_id, local_game in local_games.items():
            old_game = self._local_games_cache.get(game_id)
            if old_game is None or old_game.local_game_state != local_game.local_game_state:
                self.update_local_game_status(LocalGame(game_id, local_game.local_game_state))

        self._local_games_cache = local_games

    def __init__(self, reader, writer, token):
        self._manifest = self._read_manifest()
        self._launcher_client = TwitchLauncherClient()
        self._owned_games_cache: Dict[str, Game] = {}
        self._local_games_cache: Dict[str, InstalledGame] = {}

        super().__init__(Platform(self._manifest["platform"]), self._manifest["version"], reader, writer, token)

    def handshake_complete(self) -> None:
        self._launcher_client.update_install_path()
        self._owned_games_cache = self._get_owned_games()
        self._local_games_cache = self._get_local_games()

    def tick(self) -> None:
        self._launcher_client.update_install_path()
        self._update_owned_games()
        self._update_local_games_state()

    async def authenticate(self, stored_credentials: Optional[Dict] = None) -> Union[NextStep, Authentication]:
        if not self._launcher_client.is_installed:
            webbrowser.open_new_tab("https://www.twitch.tv/downloads")
            raise InvalidCredentials

        def get_auth_info() -> Optional[Tuple[str, str]]:
            user_info = self._get_user_info()
            if not user_info:
                logging.warning("No user info")
                return None

            user_id = user_info.get("id")
            user_name = user_info.get("displayName")

            if not user_id or not user_name:
                logging.warning("No user id/name")
                return None

            return user_id, user_name

        auth_info = get_auth_info()
        if not auth_info:
            await self._launcher_client.start_launcher()
            raise InvalidCredentials

        self.store_credentials({"external-credentials": "force-reconnect-on-startup"})
        return Authentication(user_id=auth_info[0], user_name=auth_info[1])

    async def get_owned_games(self) -> List[Game]:
        return list(self._owned_games_cache.values())

    async def get_local_games(self) -> List[LocalGame]:
        return [
            LocalGame(game_id=game.game_id, local_game_state=game.local_game_state)
            for game in self._local_games_cache.values()
        ]

    async def install_game(self, game_id: str) -> None:
        return await self._launcher_client.launch_game(game_id)

    async def launch_game(self, game_id: str) -> None:
        return await self._launcher_client.launch_game(game_id)

    async def uninstall_game(self, game_id: str) -> None:
        return self._launcher_client.uninstall_game(game_id)

    if is_windows():
        async def launch_platform_client(self) -> None:
            return await self._launcher_client.start_launcher()

        async def shutdown_platform_client(self) -> None:
            return self._launcher_client.quit_launcher()


def main():
    create_and_run_plugin(TwitchPlugin, sys.argv)


if __name__ == "__main__":
    main()
