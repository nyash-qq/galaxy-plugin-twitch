import asyncio
import logging
import os
import subprocess
import sys
import webbrowser
from typing import List, Optional, TypeVar
from galaxy.proc_tools import process_iter


def is_windows() -> bool:
    return sys.platform == "win32"


if is_windows():
    import winreg
    import ctypes

T = TypeVar("T")


def os_specific(unknown, win: Optional[T] = None, mac: Optional[T] = None) -> Optional[T]:
    return {"win32": win, "darwin": mac}.get(sys.platform, unknown)


class TwitchLauncherClient:
    _LAUNCHER_DISPLAY_NAME = "Twitch"

    def _find_launcher_window(self) -> Optional[str]:
        return ctypes.windll.user32.FindWindowW(None, self._LAUNCHER_DISPLAY_NAME) or None

    @property
    def _is_launcher_agent_running(self) -> bool:
        for proc_info in process_iter():
            if proc_info.binary_path and proc_info.binary_path.endswith("TwitchAgent.exe"):
                return True
        return False

    @property
    def _is_launcher_running(self) -> bool:
        return bool(self._find_launcher_window())

    def _hide_launcher(self) -> bool:
        h_launcher_wnd = self._find_launcher_window()
        if not h_launcher_wnd:
            return False

        if ctypes.windll.user32.IsWindowVisible(h_launcher_wnd):
            ctypes.windll.user32.ShowWindow(h_launcher_wnd, 0x0000)
            return True

        return False

    def _get_launcher_install_path(self) -> Optional[str]:
        if is_windows():

            try:
                for h_root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                    with winreg.OpenKey(h_root, r"Software\Microsoft\Windows\CurrentVersion\Uninstall") as h_apps:
                        for idx in range(winreg.QueryInfoKey(h_apps)[0]):
                            try:
                                with winreg.OpenKeyEx(h_apps, winreg.EnumKey(h_apps, idx)) as h_app_info:
                                    def get_value(key):
                                        return winreg.QueryValueEx(h_app_info, key)[0]

                                    if get_value("DisplayName") == self._LAUNCHER_DISPLAY_NAME:
                                        installer_path = get_value("InstallLocation")
                                        if os.path.exists(str(installer_path)):
                                            return installer_path

                            except (WindowsError, KeyError, ValueError):
                                continue

            except (WindowsError, KeyError, ValueError):
                logging.exception("Failed to get client install location")
                return None
        else:
            return None

    @property
    def _launcher_path(self) -> Optional[str]:
        if not self._launcher_install_path:
            return None

        return str(os_specific(
            win=os.path.join(self._launcher_install_path, "Bin", "Twitch.exe")
            , unknown=None
        ))

    @property
    def _game_remover_path(self) -> str:
        return str(os_specific(
            win=os.path.join(
                os.path.expandvars("%PROGRAMDATA%"), "Twitch", "Games", "Uninstaller", "TwitchGameRemover.exe"
            )
            , unknown=""
        ))

    @staticmethod
    def _exec(executable: str, cwd: str = None, args: List[str] = None) -> None:
        subprocess.Popen(
            [executable, *(args or [])]
            , creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
            , cwd=cwd
            , shell=True
        )

    def __init__(self):
        self._launcher_install_path: Optional[str] = None

    @property
    def is_installed(self) -> bool:
        return self._launcher_path is not None and os.path.exists(self._launcher_path)

    @property
    def cookies_db_path(self) -> Optional[str]:
        if not self._launcher_install_path:
            return None

        return os.path.join(self._launcher_install_path, "Electron3", "Cookies")

    def update_install_path(self) -> None:
        if not self._launcher_install_path or not os.path.exists(self._launcher_install_path):
            self._launcher_install_path = self._get_launcher_install_path()

    async def start_launcher(self) -> None:
        if self._is_launcher_running:
            return

        self._exec(self._launcher_path, cwd=self._launcher_install_path)
        while not self._hide_launcher():
            await asyncio.sleep(0.1)

    def quit_launcher(self) -> None:
        if not self._is_launcher_running:
            return

        self._exec(self._launcher_path, cwd=self._launcher_install_path, args=["/exit"])

    async def launch_game(self, game_id: str) -> None:
        if not self._is_launcher_running:
            await self.start_launcher()
            # even after launcher is started, we still have to wait some time, otherwise it ignores game launch commands
            await asyncio.sleep(3)

        webbrowser.open_new_tab(f"twitch://fuel-launch/{game_id}")

    def uninstall_game(self, game_id: str) -> None:
        self._exec(self._game_remover_path, args=["-m", "Game", "-p", game_id])
