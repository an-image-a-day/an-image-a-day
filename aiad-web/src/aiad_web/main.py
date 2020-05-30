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

from .api.wallpapers import IChannelProvider, WallpaperService
from .app import app
from .config import Config
from .core.server import IMiddleware, Server
from aiad_cli.database import WallpapersDatabase
from nr.databind.rest.flask import bind_resource
from nr.interface import implements, override
from typing import Iterable, List
import flask
import logging
import os
import subprocess


@implements(IChannelProvider, IMiddleware)
class AiadServer(Server):

  def __init__(self, app):
    super(AiadServer, self).__init__(app)
    self.config = Config.load()
    bind_resource(
      self.app,
      '/api/v1/wallpapers',
      WallpaperService(self),
    )
    self.add_task(
      'repository-updater',
      self._clone_or_pull_repository,
      restart='always',
      restart_cooldown=self.config.wallpapers.update_interval,
    )
    self.add_middleware(self)

  @property
  def wallpapers_repo(self):
    return os.path.join('var', 'data', 'wallpapers')

  @property
  def wallpapers_root(self):
    return os.path.join(self.wallpapers_repo, self.config.wallpapers.subdirectory)

  def _clone_or_pull_repository(self):
    if os.path.isdir(self.wallpapers_repo):
      command = ['git', 'pull']
      cwd = self.wallpapers_repo
    else:
      os.makedirs(os.path.dirname(self.wallpapers_root), exist_ok=True)
      command = ['git', 'clone', self.config.wallpapers.repository, self.wallpapers_repo]
      cwd = None
    subprocess.call(command, cwd=cwd)

  @override
  def get_channels(self) -> Iterable[str]:
    for name in os.listdir(self.wallpapers_root):
      if os.path.isdir(os.path.join(self.wallpapers_root, name)):
        yield name

  @override
  def get_channel_db(self, channel: str) -> WallpapersDatabase:
    return WallpapersDatabase(os.path.join(self.wallpapers_root, channel))

  @override
  def after_request(self, response):
    if os.getenv('FLASK_DEBUG') == 'true':
      response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if os.getenv('WERKZEUG_RUN_MAIN') == 'true':
  logging.basicConfig(format='[%(asctime)s - %(levelname)s]: %(message)s', level=logging.INFO)
  server = AiadServer(app)
  server.start_tasks()
