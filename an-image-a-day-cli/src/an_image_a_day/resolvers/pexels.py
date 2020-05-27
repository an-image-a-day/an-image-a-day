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

from an_image_a_day.core import ImageCredit, ImageWithResolution, IWallpaperSpecResolver, WallpaperSpec
from nr.interface import implements, override
import os
import re
import requests
import urllib.parse


@implements(IWallpaperSpecResolver)
class PexelsWallpaperSpecResolver:

  _regex = re.compile(r'^https://(?:www\.)?pexels.com/photo/([^/]+)-(\d+)/?$')

  @override
  def match_url(self, url: str) -> bool:
    return self._regex.match(url)

  @override
  def resolve(self, url: str) -> WallpaperSpec:
    api_token = os.getenv('PEXELS_TOKEN')
    if not api_token:
      raise EnvironmentError('PEXELS_TOKEN is not set.')

    name, photo_id = self._regex.match(url).groups()
    response = requests.get('https://api.pexels.com/v1/photos/' + photo_id,
      headers={'Authorization': api_token})
    response.raise_for_status()
    data = response.json()

    def _with_filename(height: int, width: int, url: str) -> ImageWithResolution:
      suffix = urllib.parse.urlsplit(url).path.rpartition('.')[2]
      filename = '{}-{}-{}.{}'.format(name, width, height, suffix)
      return ImageWithResolution(height, width, url, filename)

    resolutions = []
    resolutions.append(_with_filename(data['height'], data['width'], data['src']['original']))

    for key, url in data['src'].items():
      if key == 'original':
        continue
      query_params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
      dpr = int(query_params.get('dpr', [1])[0])
      height = int(query_params['h'][0]) * dpr
      if 'w' in query_params:
        width = int(query_params['w'][0]) * dpr
      else:
        width = int(round(height / data['height'] * data['width']))
      resolutions.append(_with_filename(height, width, url))

    return WallpaperSpec(
      name=name,
      keywords=[],
      source_url=data['url'],
      credit=ImageCredit(
        text='This Photo was taken by {} on Pexels.'.format(data['photographer']),
        author_url=data['photographer_url'],
        author=data['photographer'],
      ),
      resolutions=resolutions,
    )
