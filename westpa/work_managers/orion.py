import sys
from typing import Sequence

from westpa.work_managers.core import WorkManager, WMFuture


class OrionTask:

    __slots__ = ("func", "args", "kwargs", "task_id", "_result")

    def __init__(self, func, args, kwargs, task_id: str = None):
        self.func = func
        self.args = args or tuple()
        self.kwargs = kwargs or {}
        self.task_id = task_id
        self._result = None

    def run(self):
        self._result = self.func(*self.args, **self.kwargs)

    def has_result(self) -> bool:
        return self._result is not None

    def get_result(self) -> bool:
        if not self.has_result():
            self.run()
        return self._result


class OrionWorkManager(WorkManager):
    def __init__(self, emit_func, n_workers: int = 10):
        super().__init__()
        if not callable(emit_func):
            raise ValueError("Emit function must be callable")
        self._emit_func = emit_func
        self.n_workers = n_workers

    def submit(self, fn, args=None, kwargs=None) -> WMFuture:
        ft = WMFuture()
        try:
            result = fn(
                *(args if args is not None else ()),
                **(kwargs if kwargs is not None else {})
            )
        except Exception as e:
            ft._set_exception(e, sys.exc_info()[2])
        else:
            ft._set_result(result)
        return ft

    def submit_many(self, tasks) -> Sequence[WMFuture]:
        if self.futures is None:
            # We are shutting down
            raise RuntimeError("work manager is shutting down")
        futures = []
        for (fn, args, kwargs) in tasks:
            future = WMFuture()
            task = OrionTask(fn, args, kwargs, task_id=future.task_id)
            self.futures[task.task_id] = future
            self.outgoing_tasks.append(task)
            futures.append(future)

        return futures
