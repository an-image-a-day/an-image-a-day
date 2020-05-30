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
from nr.databind.core import make_struct
from nr.databind.rest import NotFound, Page, Route, RouteParam, RouteResult, RouteReturn
from nr.interface import Interface, implements
from typing import List
import datetime


WallpaperSpecPageItem = make_struct('Item', {"date": datetime.date, "wallpaper": WallpaperSpec})
WallpaperSpecPage = Page[WallpaperSpecPageItem, datetime.date]


class IChannelProvider(Interface):

  def get_channels(self) -> List[str]:
    ...

  def get_channel_db(self, channel: str) -> WallpapersDatabase:
    ...


class WallpaperResource(Interface):

  @Route('GET /channels')
  def get_channels(self) -> List[str]:
    ...

  #@Route('GET /channels/{channel}')
  #def get_channel_metadata(self, channel: str) -> ...:
  #  ...

  @Route('GET /channels/{channel}/all')
  def get_wallpapers_for_channel(
    self,
    channel: str,
    year: RouteParam.Query(int) = None,
    month: RouteParam.Query(int) = None,
    start: RouteParam.Query(datetime.date) = None,
  ) -> WallpaperSpecPage:
    ...

  @Route('GET /channels/{channel}/{year}/{month}/{day}')
  def get_wallpaper(
    self,
    channel: str,
    year: int,
    month: int,
    day: int
  ) -> WallpaperSpec:
    ...

  @Route('GET /channels/{channel}/{year}/{month}/{day}/image-url')
  def get_wallpaper_url_for_resolution(
    self,
    channel: str,
    year: int,
    month: int,
    day: int,
    width: RouteParam.Query(int),
    height: RouteParam.Query(int),
    raw: RouteParam.Query(bool) = False,
  ) -> str:
    ...


@implements(WallpaperResource)
class WallpaperService:

  MAX_PAGE_SIZE = 20

  def __init__(self, channel_provider: IChannelProvider) -> None:
    self.channel_provider = channel_provider

  def get_channels(self):
    return self.channel_provider.get_channels()

  def get_wallpapers_for_channel(self, channel, year, month, start):
    db = self.channel_provider.get_channel_db(channel)
    page = WallpaperSpecPage([], None)
    for date in db.all(year, month, sorted=True):
      if len(page.items) >= self.MAX_PAGE_SIZE:
        page.next_page_token = date
        break
      if start is not None and date < start:
        continue
      page.items.append(WallpaperSpecPageItem(date, db.load(date)))
    return page

  def get_wallpaper(self, channel, year, month, day):
    db = self.channel_provider.get_channel_db(channel)
    return db.load(datetime.date(year, month, day))

  def get_wallpaper_url_for_resolution(self, channel, year, month, day, width, height, raw):
    db = self.channel_provider.get_channel_db(channel)
    spec = db.load(datetime.date(year, month, day))
    for image in reversed(spec.resolutions):  # Assuming descending order in image size
      if image.width >= width and image.height >= height:
        break
    else:
      raise NotFound('No image available for resolution {} x {}.'.format(width, height))
    if raw:
      return RouteResult(RouteReturn.Passthrough(), image.image_url)
    return image.image_url
