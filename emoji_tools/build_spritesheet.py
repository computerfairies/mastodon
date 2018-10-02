#!/usr/bin/python3
import json
import os
import shutil

with open('emoji_settings.json') as f:
  data = json.load(f)
  settings = data['settings']
  sources = data['sources']

with open(settings['sprite_input']) as f:
  emoji_map = json.load(f)

with open(settings['copy_input']) as f:
  copy_map = json.load(f)

def find_codepoint(codepoint):
  # check each source in order for emoji
  for source in sources:
    codepoint_original = codepoint

    # replace to match source filename
    try:
      for key in source['replace']:
        codepoint = codepoint.replace(key, source['replace'][key])
    except KeyError:
      pass
    try:
      if not source['leading_zero']:
        codepoint = codepoint.lstrip('0')
    except KeyError:
      pass
    try:
      if source['lowercase']:
        codepoint = codepoint.lower()
    except KeyError:
      pass
    filename = os.path.join(source['folder'], source['filename'].replace("{codepoint}", codepoint))

    # source found
    if os.path.exists(filename):
      return filename
  
  return None

# EMOJI FILES STUFF
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

    filename = find_codepoint(codepoint)
    
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

# SPRITESHEET STUFF
def do_spritesheet():
  # iterate over every emoji in map file
  for emoji in emoji_map:
    print(emoji['name'])

    # try unified then non qualified
    filename = find_codepoint('unified')
    if filename == None: find_codepoint('non_qualified')
    
    if filename != None:
      count_found = count_found + 1
    else:
      count_missing += 1
      missing += [emoji['unified']]
      print("!! NOT FOUND! !!")

if __name__ == "__main__":
  if settings['copy_sources']:
    do_files()