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

"""
Logic that manages the Wallpapers database directory.
"""

from an_image_a_day.core import WallpaperSpec
from typing import Iterable, List
import builtins
import datetime
import os
import re


def _listdir(path: str) -> List[str]:
  try:
    return os.listdir(path)
  except FileNotFoundError:
    return []


class DateNotFoundError(ValueError):
  pass


class WallpapersDatabase:
  """
  Models a directory database of #WallpaperSpec files structured as follows:

      <yyyy>/
        <mm>/
          <dd>.json
          <dd>-<arbitrary>.json
  """

  def __init__(self, directory: str) -> None:
    self.directory = directory

  def years(self) -> Iterable[int]:
    """
    Iterates over which years have entries in the database.
    """

    for name in _listdir(self.directory):
      if name.isdigit() and len(name) == 4 and len(name.lstrip('0')) == 4:
        yield int(name)

  def months(self, year: int) -> Iterable[int]:
    """
    Iterates over which months have entries in the database for the specified *year*.
    """

    valid_months = set(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
    for name in _listdir(os.path.join(self.directory, str(year))):
      if name in valid_months:
        yield int(name.lstrip('0'))

  def days(self, year: int, month: int) -> Iterable[int]:
    """
    Iterates over which days have entries in the specified year and month.
    """

    valid_days = set('{:0>2}'.format(i) for i in range(1, 32))
    directory = os.path.join(self.directory, '{:0>2}'.format(year), '{:0>2}'.format((month)))
    for name in _listdir(directory):
      if not name.endswith('.json'):
        continue
      day_num = name[:-5]
      if '-' in day_num:
        day_num = day_num.partition('-')[0]
      if day_num not in valid_days:
        continue
      day = int(day_num.lstrip('0'))
      try:
        datetime.date(year, month, day)
      except ValueError:
        # Not a valid day in the Gregorian calendar.
        continue
      yield day

  def all(
    self,
    year: int = None,
    month: int = None,
    sorted: bool = True,
    reverse: bool = False
  ) -> Iterable[datetime.date]:
    """
    Iterates over all days in the database, or the days matching the specified *year* and *month*.
    """

    _sort = (lambda x: builtins.sorted(x, reverse=reverse)) if sorted else (lambda x: x)
    for curr_year in [year] if year is not None else _sort(self.years()):
      for curr_month in [month] if month is not None else _sort(self.months(curr_year)):
        for curr_day in _sort(self.days(curr_year, curr_month)):
          yield datetime.date(curr_year, curr_month, curr_day)

  def load(self, date: datetime.date) -> WallpaperSpec:
    directory = os.path.join(self.directory, '{:0>2}'.format(date.year), '{:0>2}'.format(date.month))
    formatted = '{:0>2}'.format(date.day)
    for name in os.listdir(directory):
      if name == (formatted + '.json') or (name.startswith(formatted + '-') and name.endswith('.json')):
        break
    else:
      raise DateNotFoundError(date)
    filename = os.path.join(directory, name)
    return WallpaperSpec.from_json(filename)

  def save(self, date: datetime.date, spec: WallpaperSpec) -> str:
    filename = os.path.join(self.directory, '{:0>4}'.format(date.year),
      '{:0>2}'.format(date.month), '{:0>2}'.format(date.day))
    if spec.name:
      filename += '-' + re.sub('[^\w\d]+', '-', spec.name.lower())
    filename += '.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    spec.to_json(filename, indent=2)
    return filename
