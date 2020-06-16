# -*- coding: utf8 -*-
# Copyright (c) 2020 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from aiad_cli.core import WallpaperSpec
from aiad_cli.database import WallpapersDatabase
from aiad_cli.resolvers import resolve_url
from nr.proxy import Proxy
from typing import Optional
import click
import datetime
import logging
import os
import pkg_resources
import sys
import termcolor

ENV_FILE = os.path.expanduser('~/.config/aiad-cli.env')


def parse_date(s: str) -> datetime.date:
  return datetime.datetime.strptime(s, '%Y-%m-%d').date()


def make_db(channel: str) -> WallpapersDatabase:
  if not os.path.isdir('Wallpapers'):
    sys.exit('error: directory "Wallpapers" does not exist.')
  return WallpapersDatabase(os.path.join('Wallpapers', channel))


def load_spec(url: str, name: Optional[str], keywords: Optional[str]) -> WallpaperSpec:
  spec = resolve_url(url)
  spec.normalize()
  if name:
    spec.name = name
  if keywords:
    spec.keywords = map(str.strip, keywords.lower().split(','))
  return spec


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-q', '--quiet', is_flag=True)
def cli(verbose, quiet):
  if verbose:
    level = logging.INFO
  elif quiet:
    level = logging.ERROR
  else:
    level = logging.WARN
  logging.basicConfig(format='[%(levelname)s]: %(message)s', level=level)

  if os.path.isfile(ENV_FILE):
    with open(ENV_FILE) as fp:
      for line in fp:
        if '=' in line:
          key, value = line.partition('=')[::2]
          os.environ[key.strip()] = value.strip()


@cli.command('save')
@click.argument('url')
@click.option('-c', '--channel', default='General', help='The database channel. Defaults to "General".')
@click.option('-n', '--name', help='Override the wallpaper name.')
@click.option('-k', '--keywords', help='Override the wallpaper keywords with a comma-separated list.')
@click.option('-d', '--date', type=parse_date, help='Specify the date for which to save the wallpaper.')
@click.option('-f', '--force', is_flag=True, help='Force save if the image for the day already exists.')
def _cli_save(url, channel, name, keywords, date, force):
  """
  Resolve a URL and save it as the next daily wallpaper.
  """

  db = Proxy(lambda: make_db(channel), lazy=True)
  spec = Proxy(lambda: load_spec(url, name, keywords), lazy=True)

  if not date:
    date = next(db.all(reverse=True), None)
    if date:
      date = date + datetime.timedelta(days=1)
    else:
      date = datetime.date.today()

  if db.exists(date):
    if not force:
      sys.exit('error: wallpaper for date "{}" already exists.'.format(date))
    filename = db.delete(date)
    print('Deleted', termcolor.colored(os.path.relpath(filename), 'red'))

  if not spec.name:
    sys.exit('error: resolved wallpaper spec has no name, please specify -n,--name')
  if not spec.keywords:
    sys.exit('error: resolved wallpaper spec has no keywords, please specify -k,--keywords')

  filename = db.save(date, spec)
  print('Saved to', termcolor.colored(os.path.relpath(filename), 'cyan'))


@cli.command('resave')
@click.argument('dates', nargs=-1, type=parse_date)
@click.option('-c', '--channel', default='General', help='The database channel. Defaults to "General".')
def _cli_resave(dates, channel):
  """
  Re-save the Wallpaper specs for the specified dates.
  """

  db = Proxy(lambda: make_db(channel), lazy=True)

  specs_to_reload = []
  for date in dates:
    specs_to_reload.append((date, db.load(date)))

  for date, spec in specs_to_reload:
    spec = load_spec(spec.source_url, spec.name, ','.join(spec.keywords))
    db.save(date, spec)


@cli.command('resolve')
@click.argument('url')
def _cli_resolve(url):
  """
  Resolve a URL to a Wallpaper spec and dump it as JSON to stdout.
  """

  spec=  load_spec(url, None, None)
  spec.to_json(sys.stdout, indent=2)
  print()


if __name__ == '__main__':
  cli()
