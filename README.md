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

* Twitch App has some problems to automatically start the installation process

### TODO
* Running games status
* MacOS support
* GameTime tracking
* Friends / chat
* Web-based (no client) library retrieval

## Acknowledgments
- [JosefNemec](https://github.com/JosefNemec) for [Playnite](https://github.com/JosefNemec/Playnite) reverse engineering
- [GOG](https://www.gog.com) for [Galaxy2.0 API](https://github.com/gogcom/galaxy-integrations-python-api)
