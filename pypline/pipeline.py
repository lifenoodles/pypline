import threading


class DependencyError(Exception):
    pass


class ModifiableMixin(object):
    def _is_match(self, task, cls):
        return task == cls or \
            (hasattr(task, "__class__") and task.__class__ == cls)

    def add_task(self, task):
        self._tasks.append(task)
        return self

    def add_task_after(self, new_task, cls):
        for i, task in enumerate(self._tasks):
            if self._is_match(task, cls):
                self._tasks.insert(i + 1, new_task)
                return self

    def add_task_before(self, new_task, cls):
        for i, task in enumerate(self._tasks):
            if self._is_match(task, cls):
                self._tasks.insert(i, new_task)
                return self

    def remove_task(self, cls):
        while True:
            try:
                self._tasks.remove(cls)
            except ValueError:
                break


class PipelineRunner(ModifiableMixin):
    def __init__(self, tasks):
        super(PipelineRunner, self).__init__()
        self._tasks = tasks[:]
        self._event = threading.Event()

    def run(self, message):
        return self.execute(message, self._tasks)

    def execute(self, message, tasks):
        self.message = message
        for task in iter(tasks):
            if hasattr(task.__class__, "_async_flag"):
                task.process(self.message, self, self.resume)
                self._event.wait()
            else:
                self.message = task.process(self.message, self)
        return self.message

    def resume(self, message):
        self.message = message
        self._event.set()


class RepeatingPipelineRunner(PipelineRunner):
    def __init__(self, controller, initialisers,
                 tasks, finalisers):
        super(RepeatingPipelineRunner, self).__init__(tasks)
        self._controller = controller
        self._initialisers = initialisers[:]
        self._finalisers = finalisers[:]

    def run(self, message):
        self.message = self.execute(message, self._initialisers)
        while True:
            self.message = self.execute(self.message, self._tasks)
            if self._controller.process(self.message, self._tasks):
                break
        self.message = self.execute(self.message, self._finalisers)
        return self.message


class AsyncMixin(object):
    def execute(self, callback, message=None):
        def run_in_thread():
            result = super(AsyncMixin, self).execute(message)
            callback(result)
        threading.Thread(run_in_thread).start()


class Pipeline(ModifiableMixin):
    def __init__(self, tasks=[]):
        self._tasks = tasks[:]
        self._validate(self._tasks)

    def _validate(self, tasks):
        # check that all tasks are can process
        for task in tasks:
            if not hasattr(task, "process"):
                raise TypeError("Task: %s has no attribute 'process'"
                                % str(task))

    def _ensure_provides(self, tasks):
        provided = set()
        for task in tasks:
            if hasattr(task, "provides"):
                provided.update(task.provides)
            if hasattr(task, "requires"):
                for req in task.requires:
                    if req not in provided:
                        raise DependencyError(
                            "Task %s requires that '%s' should be provided." %
                            (task.__class__.__name__, req))

    def execute(self, message=None):
        self._ensure_provides(self._tasks)
        runner = PipelineRunner(self._tasks)
        return runner.run(message)


class AsyncPipeline(Pipeline, AsyncMixin):
    pass


class RepeatingPipeline(Pipeline):
    def __init__(self, controller=None,
                 initialisers=[], tasks=[], finalisers=[]):
        super(RepeatingPipeline, self).__init__(tasks)
        self._controller = controller
        self._initialisers = initialisers[:]
        self._finalisers = finalisers[:]
        self._validate(self._initialisers)
        self._validate(self._finalisers)

    def execute(self, message=None):
        self._ensure_provides(
            self._initialisers + self._tasks + self._finalisers)
        runner = RepeatingPipelineRunner(
            self._controller, self._initialisers[:], self._tasks[:],
            self._finalisers[:])
        return runner.run(message)


class AsyncRepeatingPipeline(RepeatingPipeline, AsyncMixin):
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    import task

    class MyStr(task.Task):
        def process(self, message, pipe):
            return str(message)

    class MyInt(task.Task):
        def process(self, message, pipe):
            return int(message)

    class Double(task.Task):
        def process(self, message, pipe):
            return message * 2

    p = Pipeline([MyStr(), MyInt(), Double()])
    p.add_task_after(Double(), Double)
    assert p.execute(1) == 4
