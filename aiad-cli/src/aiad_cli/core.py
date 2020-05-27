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

from collections import OrderedDict
from nr.databind.core import Field, ObjectMapper, Struct
from nr.databind.json import JsonModule
from nr.interface import Interface
from typing import Optional, TextIO, Union
import json

MAPPER = ObjectMapper(JsonModule())
RESOLUTION_ALIASES = OrderedDict([
  ('HD', (1280, 720)),
  ('FHD', (1920, 1080)),
  ('2K', (2560, 1440)),
  ('4K', (3840, 2160)),
  ('5K', (5120, 2880)),
  ('8K', (7680, 4320)),
])


def get_closest_resolution_alias(width: int, height: int) -> Optional[str]:
  """
  Returns the closest alias for the specified resolution.
  """

  for alias, (alias_width, alias_height) in reversed(RESOLUTION_ALIASES.items()):
    if width >= alias_width and height >= alias_height:
      return alias

  return None


class ImageWithResolution(Struct):
  """
  Represents an actual URL to an image and it's resolution.
  """

  height = Field(int)
  width = Field(int)
  image_url = Field(str)
  filename = Field(str)


class ImageCredit(Struct):
  """
  Data to credit the author or photographer of a wallpaper.
  """

  #: Text that can be printed / displayed to credit the author.
  text = Field(str)

  #: Name of the author.
  author = Field(str)

  #: Url to the author's webpage.
  author_url = Field(str)


class WallpaperSpec(Struct):
  """
  Represents the resolved data for a wallpaper.
  """

  #: The name of the wallpaper.
  name = Field(str)

  #: A list of keywords for this wallpaper.
  keywords = Field([str])

  #: Source URL of this wallpaper. This should be the URL to a standard webpage that can
  #: be viewed in the browser (not a JSON payload or just the raw image). Usually this
  #: points at the main page on the wallpaper host.
  source_url = Field(str)

  #: Credit to the author/photographer for this wallpaper.
  credit = Field(ImageCredit)

  #: Available image resolutions, sorted from highest to lowest.
  resolutions = Field([ImageWithResolution])

  #: A mapping of the closest resolution alias to the image and its actual resolution.
  #: Usually this is automatically generated from #resolutions, but it is stored in the
  #: object as a cache.
  resolution_aliases = Field(dict(value_type=ImageWithResolution), default=dict)

  def normalize(self) -> None:
    """
    Normalize the contents by sorting #resolutions and re-generating #resolution_aliases.
    """

    self.resolutions.sort(key=lambda x: x.width * x.height, reverse=True)
    self.resolution_aliases = {}

    # Find the closest matching resolution alias for the available resolutions.
    for alias, (width, height) in RESOLUTION_ALIASES.items():
      for image in self.resolutions:
        if image.width >= width and image.height >= height:
          self.resolution_aliases[alias] = image
          continue

  def to_json(self, out: Union[TextIO, str, None], **kwargs) -> dict:
    if isinstance(out, str):
      with open(out, 'w') as fp:
        return self.to_json(fp, **kwargs)
    data = MAPPER.serialize(self, WallpaperSpec)
    if out:
      json.dump(data, out, **kwargs)
    return data

  @classmethod
  def from_json(cls, in_: Union[TextIO, str, dict], filename: str = None) -> 'WallpaperSpec':
    filename = filename or getattr(in_, 'name', None)
    if isinstance(in_, str):
      with open(in_) as fp:
        return cls.from_json(fp)
    elif hasattr(in_, 'read'):
      in_ = json.load(in_)
    return MAPPER.deserialize(in_, cls, filename=filename)


class IWallpaperSpecResolver(Interface):
  """
  An interface for resolvers that can match a URL and resolve it to a #WallpaperSpec.
  """

  def match_url(self, url: str) -> bool:
    """
    True if the URL can be resolved.
    """

  def resolve(self, url: str) -> WallpaperSpec:
    """
    Resolve a URL to a #WallpaperSpec.
    """
