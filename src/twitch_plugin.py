import json
import os
import sys
from typing import Optional

from galaxy.api.consts import Platform
from galaxy.api.plugin import create_and_run_plugin, Plugin


def is_windows():
    return sys.platform == "win32"


if is_windows():
    import winreg


class TwitchPlugin(Plugin):

    @staticmethod
    def _read_manifest():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json")) as manifest:
            return json.load(manifest)

    @staticmethod
    def get_client_install_location() -> Optional[str]:
        if is_windows():
            _CLIENT_DISPLAY_NAME = "Twitch"
            try:
                for h_root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                    with winreg.OpenKey(
                        h_root,
                        r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
                    ) as h_apps:
                        for idx in range(winreg.QueryInfoKey(h_apps)[0]):
                            try:
                                with winreg.OpenKeyEx(h_apps, winreg.EnumKey(h_apps, idx)) as h_app_info:
                                    def get_value(key):
                                        return winreg.QueryValueEx(h_app_info, key)[0]

                                    if get_value("DisplayName") == _CLIENT_DISPLAY_NAME:
                                        installer_path = get_value("InstallLocation")
                                        if os.path.exists(str(installer_path)):
                                            return installer_path

                            except (WindowsError, KeyError, ValueError):
                                continue

            except (WindowsError, KeyError, ValueError):
                return None
        else:
            return None

    @property
    def twitch_exe_path(self) -> Optional[str]:
        install_location = self.get_client_install_location()
        if not install_location:
            return None

        if is_windows():
            return os.path.join(install_location, "Bin", "Twitch.exe")

        return None

    def __init__(self, reader, writer, token):
        self._manifest = self._read_manifest()
        super().__init__(Platform(self._manifest["platform"]), self._manifest["version"], reader, writer, token)


def main():
    create_and_run_plugin(TwitchPlugin, sys.argv)


if __name__ == "__main__":
    main()
