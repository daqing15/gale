import collections
from functools import partial

class Task():

    _running = 0
    def __init__(self, callback=None, num=None, max_running=None):
        self._callback = callback
        self._max_running = max_running
        self._tasks = collections.deque()
        self._num = num
        self._called = False

    def generate_task(self, func, *args, **kwargs):
        _origin_callback = kwargs.pop('callback')
        return partial(func,
               callback=partial(self.task_callback, _origin_callback=_origin_callback),
               *args, **kwargs)

    def task_callback(self, *args, **kwargs):
        _origin_callback = kwargs.pop('_origin_callback')
        try:
            _origin_callback(*args, **kwargs)
        except Exception, e:
            raise e
        finally:
            self.done()

    def done(self):
        if self._num is None:
            Task._running -= 1
            if self._tasks:
                self.run()
            elif not self._called:
                self._called = True
                self._callback()
        else:
            self._num -= 1
            if self._num == 0:
                self._callback()

    def add(self, func, *args, **kwargs):
        self._tasks.append(self.generate_task(func, *args, **kwargs))

    def patch(self, func):
        def wrapper(*args, **kwargs):
            self.add(func, *args, **kwargs)
        return wrapper

    def run(self):
        self._called = False
        while self._tasks and (self._max_running is None or \
                Task._running < self._max_running):
            task = self._tasks.popleft()
            Task._running += 1
            task()
