import threading


class ModifiableMixin(object):
    def _is_match(self, task, cls):
        return task == cls or (hasattr(task, "__class__") and
                    task.__class__ == cls)

    def add_task(self, task):
        self._tasks.append(task)

    def add_task_after(self, task, cls):
        i = 0
        while i < len(self._tasks):
            if self._is_match(self[i], cls):
                self._tasks.insert(i + 1)
                i += 1
            i += 1

    def add_task_before(self, task, cls):
        i = 0
        while i < len(self._tasks):
            if self._is_match(self[i], cls):
                self._tasks.insert(i)
                i += 1
            i += 1

    def remove_task(self, cls):
        while  True:
            try:
                self._tasks.remove(cls)
            except ValueError:
                break


class PipelineRunner(ModifiableMixin):
    def __init__(self, tasks):
        super(PipelineRunner, self).__init__()
        self._tasks = tasks
        self._event = threading.Event()

    def run(self, message):
        return self.execute(message, self._tasks)

    def execute(self, message, tasks):
        self.message = message
        for task in iter(tasks):
            if hasattr(task.__class__, "_async_flag"):
                task(self.message, self, self.resume)
                self._event.wait()
            else:
                self.message = task(self.message, self)
        return self.message

    def resume(self, message):
        self.message = message
        self._event.set()


class RepeatingPipelineRunner(PipelineRunner):
    def __init__(self, controller, initialisers,
                tasks, finalisers):
        super(RepeatingPipelineRunner, self).__init__(tasks)
        self._controller = controller
        self._initialisers = initialisers
        self._finalisers = finalisers

    def run(self, message):
        self.message = self.execute(message, self._initialisers)
        while not self._controller(self.message):
            self.message = self.execute(self.message, self._tasks)
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
        self._validate()

    def _validate(self):
        for task in self._tasks:
            if not callable(task):
                raise TypeError("Task: %s is not callable" % str(task))

    def execute(self, message=None):
        advancer = PipelineRunner(self._tasks)
        return advancer.run(message)


class RepeatingPipeline(Pipeline):
    def __init__(self, controller=None,
                initialisers=[], tasks=[], finalisers=[]):
        self._controller = controller
        self._initialisers = initialisers
        self._finalisers = finalisers
        Pipeline.__init__(self, tasks)

    def _validate(self):
        for task in self._initialisers + self._tasks + self._finalisers:
            if not callable(task):
                raise TypeError("Task: %s is not callable" % str(task))

    def execute(self, message=None):
        advancer = RepeatingPipelineRunner(self._controller, \
                    self._initialisers[:], self._tasks[:], \
                    self._finalisers[:])
        return advancer.run(message)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    import task
    class MyStr(task.Task):
        def __call__(self, message, pipe):
            return str(message)

    class MyInt(task.Task):
        def __call__(self, message, pipe):
            return int(message)

    p = Pipeline([MyStr(), MyInt()])
    p.add_task_after(MyStr(), MyInt)
    print p.execute(1)
