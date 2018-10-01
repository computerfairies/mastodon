# emoji-tools

this is a script i made to build emoji packs for mastodon

`emoji_settings.json` drives `build_spritesheet.py`

`emoji_pretty.json` comes from [emoji-data](https://github.com/iamcal/emoji-data/blob/master/emoji_pretty.json)

it's supposed to look for emoji in order of priority (looks in following folders if hasn't found in previous), then copy all found emoji to `../public/emoji` and build a spritesheet based on `emoji_pretty.json`

**work in progress!!** does not build spritesheet yet, only find and copy emoji files

emoji svgs are not uploaded to this repo cause they're big. supply your own!

TODO:
- build spritesheet
- instead of using emoji-data spritesheet info to build emoji files actually use data from [this](https://github.com/tootsuite/mastodon/blob/master/lib/tasks/emojis.rake) which will be more complete