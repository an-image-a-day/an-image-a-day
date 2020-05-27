#!/usr/bin/env python3

"""
Validate the wallpaper database for all added JSON files between two commits.
"""

from aiad_cli.core import WallpaperSpec
from json import JSONDecodeError
from nr.databind.core import SerializationError
from typing import List
import click
import os
import subprocess
import sys
import termcolor


def _get_changed_files(rev_range: str) -> List[str]:
  return subprocess.getoutput('git diff --name-only {}'.format(rev_range)).splitlines()


@click.command()
@click.argument('rev_range')
def main(rev_range: str) -> None:
  s_rev_range = termcolor.colored(rev_range, 'yellow')

  files = _get_changed_files(rev_range)
  files = [x for x in files if x.split(os.sep, 1)[0] == 'Wallpapers']
  if not files:
    print('No wallpaper specs changed in range', s_rev_range)
    return

  print('Checking', len(files), 'wallpaper spec(s) which changed in range', s_rev_range, '...')
  status_code = 0
  for filename in files:
    try:
      spec = WallpaperSpec.from_json(filename)
    except (JSONDecodeError, SerializationError) as exc:
      status = termcolor.colored('ERROR', 'red') + ' ({})'.format(exc)
      status_code = 1
    else:
      # TODO (@NiklasRosenstein): Ensure all links in the spec work.
      status = termcolor.colored('OK', 'green')
    print(' ', filename, status)

  sys.exit(status_code)


if __name__ == '__main__':
  main()
