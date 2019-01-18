#!/usr/bin/python3
import json
import os
import shutil
import sys
from wand.image import Image

with open('emoji_settings.json') as f:
  data = json.load(f)
  settings = data['settings']
  sources = data['sources']

with open(settings['sprite_input']) as f:
  emoji_map = json.load(f)

with open(settings['copy_input']) as f:
  copy_map = json.load(f)

## EMOJI FILES STUFF
def do_files():
  count_found = 0
  count_missing = 0
  missing = []

  # iterate over every emoji in map file
  for emoji in copy_map.items():
    #print(emoji[1])
    codepoint = emoji[1]

    if codepoint == None:
      continue

    filename = find_source_svg(codepoint)
    
    if filename != None:
      count_found = count_found + 1
      shutil.copy2(filename, os.path.join(settings['destination'], codepoint + '.svg'))
    else:
      count_missing += 1
      missing += [codepoint]
      #print("!! NOT FOUND! !!")
  
  print("found: {:d}".format(count_found))
  print("missing: {:d}".format(count_missing))
  if count_missing:
    print(missing)

def find_source_svg(codepoint):
  if codepoint == None:
    return None

  # check each source in order for emoji
  for source in sources:
    bcodepoint = codepoint

    # replace to match source filename
    try:
      for key in source['replace']:
        bcodepoint = bcodepoint.replace(key, source['replace'][key])
    except KeyError:
      pass
    try:
      if not source['leading_zero']:
        bcodepoint = bcodepoint.lstrip('0')
    except KeyError:
      pass
    try:
      if source['lowercase']:
        bcodepoint = bcodepoint.lower()
    except KeyError:
      pass

    filename = os.path.join(source['folder'], source['filename'].replace("{codepoint}", bcodepoint))

    # source found
    if os.path.exists(filename):
      # check if emoji has skin modifiers
      current_emoji = [x for x in emoji_map if x['non_qualified'] == codepoint.upper() or x['unified'] == codepoint.upper()]
      if len(current_emoji) > 0:
        try:
          if current_emoji[0]['skin_variations']:
            # if it has, use the default skin modifier from settings
            new_filename = os.path.join(source['folder'], source['filename'].replace("{codepoint}", bcodepoint + source['default_skin']))
            if os.path.exists(new_filename):
              filename = new_filename
        except KeyError:
          pass

      #print("codepoint " + codepoint + " found in source " + filename)

      return filename
  
  return None

## SPRITESHEET STUFF
def do_spritesheet():
  count_found = 0
  count_missing = 0
  missing = []

  # init spritesheet
  # 1768 = 52x52 32px emojis with 1px padding on all sides each
  spritesheet = Image(width=1768, height=1768)

  # iterate over every emoji in map file
  for emoji in emoji_map:
    #print(emoji['name'])

    # TODO: fix code reuse here
    try:
      if emoji['skin_variations']:
        for skin in emoji['skin_variations']:
          skin_info = emoji['skin_variations'][skin]

          # find in svgs in public folder
          filename = find_sprite_svg(skin_info['unified'])
          if filename == None:
            filename = find_sprite_svg(skin_info['non_qualified'])
          
          if filename != None:
            count_found = count_found + 1
            add_to_spritesheet(filename, spritesheet, skin_info['sheet_x'], skin_info['sheet_y'])
          else:
            count_missing += 1
            missing += [skin_info['unified']]
    except KeyError:
      pass

    # find in svgs in public folder
    filename = find_sprite_svg(emoji['unified'])
    if filename == None:
      filename = find_sprite_svg(emoji['non_qualified'])
    
    if filename != None:
      count_found = count_found + 1
      add_to_spritesheet(filename, spritesheet, emoji['sheet_x'], emoji['sheet_y'])
    else:
      count_missing += 1
      missing += [emoji['unified']]
      #print("!! NOT FOUND! !!")

  print("found: {:d}".format(count_found))
  print("missing: {:d}".format(count_missing))
  if count_missing:
    print(missing)

  sprite_filename = os.path.join(settings['destination'], settings['sheet'])
  png_image = spritesheet.make_blob("png32")
  with open(sprite_filename, "wb") as out:
    out.write(png_image)

def find_sprite_svg(codepoint):
  if codepoint == None:
    return None

  ncodepoint = codepoint.lower().lstrip("0")

  # return filename if emoji exists in public
  filename = os.path.join(settings['destination'], ncodepoint + ".svg")

  if os.path.exists(filename):
    return filename
  
  return None

def add_to_spritesheet(filename, spreadsheet, x, y):
  im = Image(filename=filename)
  im.transform(resize="32x32")
  spreadsheet.composite(im, x*34+1, y*34+1)
  pass

## HELP
def print_help():
  print("usage:")
  print("  --skip-copy            skips copying files from source")
  print("  --skip-spritesheet     skips building spritesheet png")

if __name__ == "__main__":
  if "--help" in sys.argv:
    print_help()
    sys.exit()

  if "--skip-copy" not in sys.argv:
    print("Finding source SVGs to copy to {:s}".format(settings['destination']))
    do_files()
  
  if "--skip-spritesheet" not in sys.argv:
    print("Rebuilding spritesheet...")
    do_spritesheet()
