# galaxy-plugin-twitch
Twitch python plugin for GOG Galaxy 2.0

## Installation
### Instaling releases
1. Download [latest](https://github.com/nyash-qq/galaxy-plugin-twitch/releases/latest) release of the plugin for your platform.
2. Create plugin folder (if it does not exists yet):
	- Windows: `%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\twitch_8b831aed-dd5f-c0c5-c843-41f9751f67a2`
	- MacOS: `${HOME}/Library/Application Support/GOG.com/Galaxy/plugins/installed/twitch_8b831aed-dd5f-c0c5-c843-41f9751f67a2`
3. Disconnect `Twitch` plugin if it's already running, or shutdown the GLX
4. Unpack (and replace) plugin archive to the plugin folder created in 3.
5. Re-connect(or re-start) the GLX

### Installing from sources
⚠️ Make sure you know what you are doing.

Prerequisites:
* `git`
* `python 3.6+` and `pip`

```
git clone https://github.com/nyash-qq/galaxy-plugin-twitch.git
cd galaxy-plugin-twitch
pip install invoke
inv install
```

## Authentication
In order to use this plugin you have to be authenticated in [Twitch App](https://www.twitch.tv/downloads)

## Known issues and limitations

### Twitch app
* DB contains columns for the game time tracking, but app doesn't update them. So game time tracking is not possible until GLX implements it
* App has some problems starting games installation process automatically
* No support for games on MacOS

### Galaxy Client
* "Not compatible" grey "Install" button is an issue in the GLX itself and should be fixed soon™

### Plugin TODO
* Friends / chat
* Web-based (no client) library retrieval

## Acknowledgments
- [JosefNemec](https://github.com/JosefNemec) for [Playnite](https://github.com/JosefNemec/Playnite) reverse engineering
- [GOG](https://www.gog.com) for [Galaxy2.0 API](https://github.com/gogcom/galaxy-integrations-python-api)
