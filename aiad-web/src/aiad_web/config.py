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

from nr.databind.core import Field, FieldName, ObjectMapper, Struct
from nr.databind.json import JsonModule
import os
import yaml

MAPPER = ObjectMapper(JsonModule())


class WallpaperSourceConfig(Struct):
  repository = Field(str)
  subdirectory = Field(str, default=None)
  update_interval = Field(int, FieldName('update-interval'), default=10)


class Config(Struct):
  wallpapers = Field(WallpaperSourceConfig)

  @classmethod
  def load(cls, filename: str = None) -> 'Config':
    if not filename:
      filename = os.getenv('AIAD_WEB_CONFIG_FILENAME') or 'config.yaml'
    with open(filename) as fp:
      data = yaml.safe_load(fp)
    return MAPPER.deserialize(data, cls, filename=filename)
