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

from aiad_cli.core import ImageCredit, ImageWithResolution, IWallpaperSpecResolver, WallpaperSpec
from aiad_cli.utils import get_user_agent
from nr.interface import implements, override
import os
import re
import requests
import urllib.parse


@implements(IWallpaperSpecResolver)
class UnsplashWallpaperSpecResolver:

  _regex = re.compile(r'^https://(?:www\.)?unsplash.com/photos/([^/]+)/?$')
  _bad_keywords = set(['android', 'wallpaper', 'ios', 'iphone'])

  @override
  def match_url(self, url: str) -> bool:
    return self._regex.match(url)

  @override
  def resolve(self, url: str) -> WallpaperSpec:
    access_key = os.getenv('UNSPLASH_ACCESS_KEY')
    if not access_key:
      raise EnvironmentError('UNSPLASH_ACCESS_KEY is not set.')

    photo_id = self._regex.match(url).group(1)
    response = requests.get('https://api.unsplash.com/photos/' + photo_id,
      headers={'Authorization': 'Client-ID ' + access_key, 'User-Agent': get_user_agent()})
    response.raise_for_status()
    data = response.json()
    name = data['alt_description'] or data['description']

    def _with_filename(height: int, width: int, url: str) -> ImageWithResolution:
      headers = requests.head(url, headers={'User-Agent': get_user_agent()}).headers
      content_type = headers['Content-Type']
      if not content_type.startswith('image/'):
        raise RuntimeError('unexpected non-image content-type: {!r}'.format(content_type))
      suffix = content_type.lstrip('image/')
      filename = '{}-{}-{}.{}'.format(re.sub(r'[\s,\.]+', '-', name), width, height, suffix)
      return ImageWithResolution(height, width, url, filename)

    resolutions = []
    #resolutions.append(_with_filename(data['height'], data['width'], data['urls']['raw']))

    for key, url in data['urls'].items():
      if key == 'raw':
        continue
      query_params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
      width = int(query_params.get('w', [data['width']])[0])
      height = int(round(width / data['width'] * data['height']))
      resolutions.append(_with_filename(height, width, url))

    tags = (x['title'] for x in data['tags'] if x['type'] == 'search')
    tags = (x.strip('#') for x in tags if not any(y in x for y in self._bad_keywords))

    return WallpaperSpec(
      name=name,
      keywords=tags,
      source_url=data['links']['html'],
      credit=ImageCredit(
        text='This Photo was taken by {} on Unsplash.'.format(data['user']['name']),
        author_url=data['user']['links']['html'],
        author=data['user']['name'],
      ),
      resolutions=resolutions,
    )
