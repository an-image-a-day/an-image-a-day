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

from .config import Config
from .api.wallpapers import WallpaperSourceManager, WallpaperService
from nr.databind.rest.flask import bind_resource
from nr.utils.flask.tasks import TaskManager
import flask
import logging
import os

config = Config.load()
app = flask.Flask(__name__, static_url_path='', static_folder=os.path.abspath('public'))
tasks = TaskManager()
wallpapers = WallpaperSourceManager(config.wallpapers)

tasks.register_task(
  'wallpaper-updater',
  wallpapers.update,
  restart='always',
  restart_cooldown=config.wallpapers.update_interval)

bind_resource(
  app,
  '/api/v1/wallpapers',
  WallpaperService(wallpapers),
)

if os.getenv('WERKZEUG_RUN_MAIN') == 'true' or os.getenv('ENVIRONMENT') == 'prod':
  logging.basicConfig(format='[%(asctime)s - %(levelname)s]: %(message)s', level=logging.INFO)
  tasks.start()
