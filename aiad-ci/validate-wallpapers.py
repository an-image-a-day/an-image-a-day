#!/usr/bin/env python3

"""
Validate the wallpaper database for all added JSON files between two commits.
"""

from aiad_cli.core import WallpaperSpec
from json import JSONDecodeError
from nr.databind.core import SerializationError
from typing import List, Optional, Tuple
import click
import fnmatch
import os
import requests
import subprocess
import sys
import termcolor


def _get_changed_files(rev_range: str) -> List[str]:
  return subprocess.getoutput('git diff --name-only {}'.format(rev_range)).splitlines()


def _get_bad_links(spec: WallpaperSpec) -> List[Tuple[str, int, Optional[str]]]:
  links = [(spec.source_url, 'text/html'), (spec.credit.author_url, 'text/html')]
  for image in spec.resolutions:
    links.append((image.image_url, 'image/*'))
  bad_links = []
  for link, content_type in links:
    response = requests.head(link)
    if response.status_code != 200:
      bad_links.append((link, response.status_code, None))
      continue
    has_content_type = response.headers['Content-type'].partition(';')[0]
    if not fnmatch.fnmatch(has_content_type, content_type):
      bad_links.append((link, 200, 'expected Content-type "{}", got "{}"'.format(
        content_type, has_content_type)))
      continue
  return bad_links


@click.command()
@click.argument('rev_range')
def main(rev_range: str) -> None:
  s_rev_range = termcolor.colored(rev_range, 'yellow')

  files = _get_changed_files(rev_range)
  files = [x for x in files if x.split(os.sep, 1)[0] == 'Wallpapers']
  if not files:
    print('No wallpaper specs changed in range', s_rev_range)
    return

  process_status = 0

  print('Checking', len(files), 'changed wallpaper spec(s) from range', s_rev_range)
  for filename in files:
    bad_links = []
    try:
      spec = WallpaperSpec.from_json(filename)
    except (JSONDecodeError, SerializationError) as exc:
      status = termcolor.colored('ERROR', 'red') + ' ({})'.format(exc)
      process_status = 1
    else:
      bad_links = _get_bad_links(spec)
      if bad_links:
        status = termcolor.colored('ERROR', 'red')
        process_status = 1
      else:
        status = termcolor.colored('OK', 'green')

    print('|', filename, status)
    for link, status_code, errmsg in bad_links:
      color = 'green' if status_code == 200 else 'red'
      status_code = termcolor.colored(status_code, color)
      print('| |', link, status_code, termcolor.colored(errmsg, 'red') if errmsg else '')

  sys.exit(process_status)


if __name__ == '__main__':
  main()
