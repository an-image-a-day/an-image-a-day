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

from nr.interface import Interface, default, implements, override
from typing import Any, Callable, Union
import flask
import enum
import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)


class IMiddleware(Interface):

  @default
  def before_request(self):
    ...

  @default
  def after_request(self, response):
    ...

class Server:
  """
  Addon class (or rapper) for a Flask application that provides some useful functionality
  around it, such as background tasks and middlewares.
  """

  def __init__(self, app: flask.Flask):
    self.app = app
    self.middleware = []
    app.before_request(self._before_request)
    app.after_request(self._after_request)

  def _before_request(self):
    for middleware in self.middleware:
      response = middleware.before_request()
      if response is not None:
        return response
    return None

  def _after_request(self, response):
    for middleware in self.middleware:
      response = middleware.after_request(response)
    return response


  def add_middleware(self, middleware: IMiddleware) -> None:
    self.middleware.append(middleware)

  def run(self, *args, **kwargs):
    return self.app.run(*args, **kwargs)

  def __call__(self, environ, start_response):
    return self.app(environ, start_response)
