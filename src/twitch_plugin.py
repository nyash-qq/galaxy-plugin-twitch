import json
import os
import sys

from galaxy.api.consts import Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin


class TwitchPlugin(Plugin):

    @staticmethod
    def _read_manifest():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json")) as manifest:
            return json.load(manifest)

    def __init__(self, reader, writer, token):
        self._manifest = self._read_manifest()
        super().__init__(Platform(self._manifest["platform"]), self._manifest["version"], reader, writer, token)


def main():
    create_and_run_plugin(TwitchPlugin, sys.argv)


if __name__ == "__main__":
    main()
