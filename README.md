# galaxy-plugin-twitch
Twitch python plugin for GOG Galaxy 2.0

## Prerequisites
* `git`
* `python 3.6+` and `pip`

## Installation
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
* "Not compatible" grey "Install" button is an issue in the GLX itself and should be fixed soon
* "Twitch" platform does not exists in the GLX yet, so have to use "Amazon" instead. Will switch once "Twitch" is supported

### Plugin TODO
* Running games status
* Friends / chat
* Web-based (no client) library retrieval

## Acknowledgments
- [JosefNemec](https://github.com/JosefNemec) for [Playnite](https://github.com/JosefNemec/Playnite) reverse engineering
- [GOG](https://www.gog.com) for [Galaxy2.0 API](https://github.com/gogcom/galaxy-integrations-python-api)
