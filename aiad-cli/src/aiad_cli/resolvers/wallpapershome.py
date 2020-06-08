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
import bs4
import logging
import os
import posixpath
import re
import requests
import urllib.parse

logger = logging.getLogger(__name__)


@implements(IWallpaperSpecResolver)
class WallpapersHomeSpecResolver:

  _regex = re.compile(r'^https://(?:www\.)?wallpapershome.com/.*/([^/]+)\-\d+\.html')
  _bad_keywords = frozenset(['hd', 'fullhd', 'fhd', '2k', '4k', '5k', '8k', 'wide', 'wide screen'])

  @override
  def match_url(self, url: str) -> bool:
    return self._regex.match(url)

  @override
  def resolve(self, url: str) -> WallpaperSpec:
    response = requests.get(url, headers={'User-Agent': get_user_agent()})
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    resolutions = []
    broken_resolutions = []
    node = soup.find('div', {'class': 'block-download__resolutions--6'})
    for item in node.find_all('p'):
      name = item.find('span').text
      res = item.find('a').text
      width, height = res.lower().partition('x')[::2]
      image_url = urllib.parse.urljoin(url, item.find('a')['href'])

      # Test if the URL is valid. Often times WP-Home download links are broken and
      # instead redirect to /wallpapers/.
      response = requests.head(image_url, allow_redirects=False)
      if response.status_code != 200 or not response.headers.get('Content-type').startswith('image/'):
        logger.warning('Download link for resolution %s is broken (%s).', name, response.status_code)
        continue

      resolutions.append(ImageWithResolution(
        int(height), int(width), image_url, posixpath.basename(image_url)))

    if not resolutions:
      raise ValueError('all download links are broken')

    tags = soup.find('p', {'class': 'tags'}).find_all('a')
    tags = (x.text.lower().strip() for x in tags)
    tags = [x for x in tags if sorted(x.split()) == sorted(set(x.split()) - self._bad_keywords)]

    author_parent = soup.find('p', {'class': 'author'})
    if '|' in author_parent.text:
      author, uploader = author_parent.find_all('a')
    else:
      author = None
      uploader, = author_parent.find_all('a')

    credit = ImageCredit(
      text='Uploaded by {} on WallpapersHome'.format(uploader.text),
      author_url=urllib.parse.urljoin(url, (author or uploader)['href']),
      author=(author or uploader).text,
    )
    if author:
      credit.text = '© ' + author.text + ' | ' + credit.text

    # Sanitize the name, removing any of the bad keywords.
    name = self._regex.match(url).group(1).lower()
    for keyword in self._bad_keywords:
      if '-' + keyword in name:
        name = name.replace('-' + keyword, '')
      else:
        name = name.replace(keyword + '-', '')

    return WallpaperSpec(
      name=name,
      keywords=tags,
      source_url=url,
      credit=credit,
      resolutions=resolutions,
    )
