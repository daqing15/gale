import collections
from functools import partial

class Task():

    _running = 0
    def __init__(self, callback=None, max_running=None):
        self._callback = callback
        self._max_running = max_running
        self._tasks = collections.deque()

    def generate_task(self, func, *args, **kwargs):
        _origin_callback = kwargs.pop('callback')
        return partial(func,
               callback=partial(self.task_callback, _origin_callback=_origin_callback),
               *args, **kwargs)

    def task_callback(self, *args, **kwargs):
        _origin_callback = kwargs.pop('_origin_callback')
        _origin_callback(*args, **kwargs)
        self.done()

    def done(self):
        Task._running -= 1
        if self._tasks:
            self.run()
        elif Task._running == 0:
            self._callback()

    def add(self, func, *args, **kwargs):
        self._tasks.append(self.generate_task(func, *args, **kwargs))

    def patch(self, func):
        def wrapper(*args, **kwargs):
            self.add(func, *args, **kwargs)
        return wrapper

    def run(self):
        while self._tasks and (self._max_running is None or \
                Task._running < self._max_running):
            task = self._tasks.popleft()
            Task._running += 1
            task()
            print 'run'
