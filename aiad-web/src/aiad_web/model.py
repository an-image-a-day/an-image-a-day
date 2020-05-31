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

from .api.wallpapers import IChannelProvider
from .config import WallpaperSourceConfig
from aiad_web.database import WallpapersDatabase
from typing import Iterable


@implements(IChannelProvider)
class WallpaperSourceManager:

  def __init__(self, config: WallpaperSourceConfig):
    self.config = config

  @property
  def repo_directory(self) -> str:
    return os.path.join('var', 'data', 'wallpapers')

  @property
  def channels_directory(self) -> str:
    return os.path.join(self.repo_directory, self.subdirectory)

  def update(self) -> None:
    if os.path.isdir(self.repo_directory):
      command = ['git', 'pull']
      cwd = self.wallpapers_repo
    else:
      os.makedirs(os.path.dirname(self.repo_directory), exist_ok=True)
      command = ['git', 'clone', self.config.repository, self.repo_directory]
      cwd = None
    subprocess.call(command, cwd=cwd)

  @override
  def get_channels(self) -> Iterable[str]:
    for name in os.listdir(self.wallpapers_root):
      if os.path.isdir(os.path.join(self.channels_directory, name)):
        yield name

  @override
  def get_channel_db(self, channel: str) -> WallpapersDatabase:
    return WallpapersDatabase(os.path.join(self.channels_directory, channel))
