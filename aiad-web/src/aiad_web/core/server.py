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


class IScheduler(Interface):

  def schedule(self, func: Callable[[], Any], at: int) -> None:
    ...


class Restart(enum.Enum):
  no = 0
  on_failure = 1
  on_success = 2
  always = 3


class Task:

  def __init__(
    self,
    id_: str,
    func: Callable[[], Any],
    restart: Restart,
    restart_cooldown: int,
    scheduler: IScheduler,
  ) -> None:
    self.id = id_
    self.func = func
    self.restart = restart
    self.restart_cooldown = restart_cooldown
    self.scheduler = scheduler
    self.thread = None
    self.started_count = 0
    self.lock = threading.RLock()
    self.finished_callbacks = []

  def __repr__(self) -> str:
    return 'Task(id={!r}, restart={!r})'.format(self.id, self.restart)

  def _run(self) -> None:
    try:
      self.func()
      success = True
    except Exception:
      logger.exception('Exception in task %r (restart: %s)', self.id, self.restart)
      success = False
    finally:
      for callback in self.finished_callbacks:
        try:
          callback()
        except Exception:
          logger.exception('Exception in callback of task %r (callback: %r)', self.id, callback)
    with self.lock:
      self.thread = None
      if (success and self.restart == Restart.on_success) or \
          (not success and self.restart == Restart.on_failure) or \
          self.restart == Restart.always:
        self.scheduler.schedule(self.start, time.time() + self.restart_cooldown)

  def start(self) -> None:
    with self.lock:
      if self.thread and self.thread.isAlive():
        raise RuntimeError('Task.thread is still alive')
      self.thread = threading.Thread(target=self._run)
      self.thread.start()
      self.started_count += 1
      logger.info('Started task %r (thread-id: %s, started-count: %s)',
        self.id, self.thread.ident, self.started_count)

  def add_finished_callback(self, func: Callable[[], Any]) -> None:
    self.finished_callbacks.append(func)


@implements(IScheduler)
class SchedulerThread(threading.Thread):
  """
  This thread runs as daemon so it is killed when the process exits. While it is alive,
  it will restart threads that are expected to be restarted per the #Restart strategy.
  """

  # TODO (@NiklasRosenstein): Add stop method

  def __init__(self):
    super(SchedulerThread, self).__init__()
    self.daemon = True
    self.queue = queue.PriorityQueue()
    self.cond = threading.Condition()
    self.stop_event = threading.Event()

  @override
  def schedule(self, func: Callable[[], Any], at: int) -> None:
    with self.cond:
      self.queue.put((at, func))
      self.cond.notify()

  def run(self) -> None:
    logger.info('SchedulerThread started.')
    while not self.stop_event.is_set():
      at, func = self.queue.get()
      delta = at - time.time()
      if delta <= 0:
        try:
          func()
        except Exception:
          logger.exception('Error calling scheduled function %r.', func)
        continue
      with self.cond:
        self.cond.wait(delta)
        self.queue.put((at, func))

  def stop(self, wait: bool = True) -> None:
    with self.cond:
      self.stop_event.set()
      self.cond.notify()


class Server:
  """
  Addon class (or rapper) for a Flask application that provides some useful functionality
  around it, such as background tasks and middlewares.
  """

  def __init__(self, app: flask.Flask):
    self.app = app
    self.middleware = []
    self.tasks = {}
    self._tasks_started = False
    self._scheduler_thread = SchedulerThread()
    app.before_request(self._before_request)
    app.after_request(self._after_request)

  def _before_request(self):
    if not self._tasks_started:
      self.start_tasks()
    for middleware in self.middleware:
      response = middleware.before_request()
      if response is not None:
        return response
    return None

  def _after_request(self, response):
    for middleware in self.middleware:
      response = middleware.after_request(response)
    return response

  def start_tasks(self):
    if not self._scheduler_thread.isAlive():
      self._scheduler_thread.start()
    for task in self.tasks.values():
      if task.started_count == 0:
        task.start()

  def add_middleware(self, middleware: IMiddleware) -> None:
    self.middleware.append(middleware)

  def add_task(
    self,
    id_: str,
    func: Callable[[], Any],
    start_immediately: bool = False,
    restart: Union[Restart, str] = Restart.always,
    restart_cooldown: int = 0,
  ) -> Task:
    """
    Add a task to the server that will be started on the first request to the application,
    or immediately if *start_immediately* is set to True. If *restart* is set to True, the
    task will be restarted when it ended.
    """

    if isinstance(restart, str):
      restart = Restart[restart.lower().replace('-', '_')]

    if id_ in self.tasks:
      raise ValueError('task id {!r} already occupied'.format(id_))
    task = Task(id_, func, restart, restart_cooldown, self._scheduler_thread)
    self.tasks[id_] = task
    logger.info('Registered task %r.', id_)
    if start_immediately:
      task.start()
    return task

  def run(self, *args, **kwargs):
    return self.app.run(*args, **kwargs)

  def __call__(self, environ, start_response):
    return self.app(environ, start_response)
