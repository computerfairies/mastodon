# emoji-tools

this is a script i made to build emoji packs for mastodon

`emoji_settings.json` drives `build_spritesheet.py`

`emoji_pretty.json` comes from [emoji-data](https://github.com/iamcal/emoji-data/blob/master/emoji_pretty.json)

it's supposed to look for emoji in order of priority (looks in following folders if hasn't found in previous), then copy all found emoji to `../public/emoji` and build a spritesheet based on `emoji_pretty.json`

**work in progress!!** does not build spritesheet yet, only find and copy emoji files

emoji svgs are not uploaded to this repo cause they're big. supply your own!

## how to use:
1. run `bundle exec rails emojis:generate[ignore_existing=true]` to generate a map of all emoji 11.0 unicode codepoints
2. run `build_spritesheet.py` to find svgs in designated folders corresponding to said codepoints
3. run `bundle exec rails emojis:generate` (no argument this time) in order to match emoji only to available files and avoid broken images

TODO:
- build spritesheet