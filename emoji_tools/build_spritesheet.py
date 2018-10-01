#!/usr/bin/python3
import json
import os
import shutil

with open('emoji_settings.json') as f:
  data = json.load(f)
  settings = data['settings']
  sources = data['sources']

with open(settings['input']) as f:
  emoji_map = json.load(f)

count_found = 0
count_missing = 0
missing = []

# iterate over every emoji in map file
for emoji in emoji_map:
  print(emoji['name'])
  found = False

  # check each source in order for emoji
  for source in sources:
    # what field in emoji map to search for
    source_type = source['type']
    codepoint = emoji[source_type]
    if codepoint == None:
      codepoint = emoji['unified']

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

    # source found, copy emoji over and add it to the sheet
    if os.path.exists(filename):
      # debug
      print(filename)
      found = True
      count_found += 1
      if settings['copy_sources']:
        shutil.copy2(filename, os.path.join(settings['destination'], codepoint_original.lower().lstrip('0') + '.svg'))
      break

  # source not found, warn
  if not found:
    count_missing += 1
    missing += [emoji['unified']]
    print("!! NOT FOUND! !!")

print("found: {:d}".format(count_found))
print("missing: {:d}".format(count_missing))
if count_missing:
  print(missing)