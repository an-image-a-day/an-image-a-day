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

from an_image_a_day.core import WallpaperSpec
from an_image_a_day.database import WallpapersDatabase
from an_image_a_day.resolvers import resolve_url
from nr.proxy import Proxy
from typing import Optional
import click
import datetime
import os
import pkg_resources
import sys
import termcolor


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
def cli():
  ...


@cli.command('save')
@click.argument('url')
@click.option('-c', '--channel', default='General', help='The database channel. Defaults to "General".')
@click.option('-n', '--name', help='Override the wallpaper name.')
@click.option('-k', '--keywords', help='Override the wallpaper keywords with a comma-separated list.')
def _cli_save(url, channel, name, keywords):
  """
  Resolve a URL and save it as the next daily wallpaper.
  """

  db = Proxy(lambda: make_db(channel), lazy=True)
  spec = Proxy(lambda: load_spec(url, name, keywords), lazy=True)

  date = next(db.all(reverse=True), None)
  if date:
    date = date + datetime.timedelta(days=1)
  else:
    date = datetime.date.today()

  if not spec.name:
    sys.exit('error: resolved wallpaper spec has no name, please specify -n,--name')
  if not spec.keywords:
    sys.exit('error: resolved wallpaper spec has no keywords, please specify -k,--keywords')
  filename = db.save(date, spec)
  print('Saved to', termcolor.colored(os.path.relpath(filename), 'cyan'))


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
