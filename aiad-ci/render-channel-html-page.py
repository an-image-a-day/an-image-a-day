#!/usr/bin/env python3

"""
Validate the wallpaper database for all added JSON files between two commits.
"""

from aiad_cli.core import WallpaperSpec
from aiad_cli.database import WallpapersDatabase
from typing import Iterable
import click
import datetime
import jinja2
import os
import sys

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
  'October', 'November', 'December',
]


class _Image:
  def __init__(self, day: datetime.date, db: WallpapersDatabase) -> None:
    self._day = day
    self._db = db
    self._spec = None
  @property
  def spec(self) -> WallpaperSpec:
    if not self._spec:
      self._spec = self._db.load(self._day)
    return self._spec
  @property
  def url(self) -> str:
    return self.spec.resolutions[-1].image_url


class _Month:
  def __init__(self, year: int, month: int, db: WallpapersDatabase) -> None:
    self._year = year
    self._month = month
    self._db = db
  def __str__(self):
    return str(self._month)
  def __repr__(self):
    return '_Month({!r}, {!r})'.format(self._year, self._month)
  @property
  def images(self) -> Iterable[_Image]:
    return [_Image(d, self._db) for d in sorted(self._db.all(self._year, self._month), reverse=True)]
  @property
  def name(self) -> str:
    return MONTH_NAMES[self._month]


class _Year:
  def __init__(self, year: int, db: WallpapersDatabase) -> None:
    self._year = year
    self._db = db
  def __str__(self):
    return str(self._year)
  def __repr__(self):
    return '_Year({!r})'.format(self._year)
  @property
  def months(self) -> Iterable[_Month]:
    return [_Month(self._year, m, self._db) for m in sorted(self._db.months(self._year), reverse=True)]


@click.command()
@click.option('-c', '--channel', default='General')
def main(channel):
  db = WallpapersDatabase(os.path.join('Wallpapers', channel))
  years = [_Year(y, db) for y in sorted(db.years(), reverse=True)]
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))
  template = env.get_template('channel-images.html')
  template.stream(channel=channel, years=years).dump(sys.stdout)


if __name__ == '__main__':
  main()
