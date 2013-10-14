from task import BundleMixin
import abc


class ModifiableMixin(object):
    def add_task(self, task):
        self._tasks.append(task)

    def add_task_after(self, task, cls):
        try:
            index = next(i for (i, x) in enumerate(self._tasks)
                    if x.__class__ == cls)
        except StopIteration:
            raise ValueError("Class %s not found in pipeline."
                    % cls.__name__)
        self._tasks.insert(task, index + 1)

    def add_task_before(self, task, cls):
        try:
            index = next(i for (i, x) in enumerate(self._tasks)
                    if x.__class__ == cls)
        except StopIteration:
            raise ValueError("Class %s not found in pipeline."
                    % cls.__name__)
        self._tasks.insert(task, index)

    def remove_task(self, cls):
        while  True:
            try:
                self._tasks.remove(cls)
            except ValueError:
                break


class PipelineAdvancer(object):
    def __init__(self, tasks, callback=None):
        self._tasks = tasks
        self._iterator = iter(self._tasks)
        self._callback = callback
        self.resume = self.__call__
        self.message = None

    def __call__(self, message):
        self.message = message
        try:
            return next(self._iterator)(message, self)
        except StopIteration:
            if callable(self._callback):
                self._callback(message)


class RepeatingPipelineAdvancer(PipelineAdvancer):
    def __init__(self, controller, initialisers,
                tasks, finalisers, callback=None):
        PipelineAdvancer.__init__(self, tasks, callback)
        self._controller = controller
        self._finaliser_pipe = PipelineAdvancer(finalisers, callback)
        self._body_pipe = PipelineAdvancer(self._tasks,
                self._finaliser_pipe)
        self._initialiser_pipe = PipelineAdvancer(initialisers,
                self._body_pipe)

    def begin(self, message):
        self._initialiser_pipe(message)
        return self._finaliser_pipe.message

    def __call__(self, message):
        while not self._controller.done(message):
            self.message = message
            try:
                return next(self._iterator)(message, self)
            except StopIteration:
                self._iterator = iter(self._tasks)
                continue
        self._finaliser_pipe(message)


class PipeController():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def done(self, message):
        raise NotImplementedError


class BundlePipeController(PipeController, BundleMixin):
    pass


class AsyncMixin(object):
    def execute(self, message, callback):
        advancer = PipelineAdvancer(self, self._tasks, callback)
        advancer(message)


class Pipeline(object):
    def __init__(self, tasks=[]):
        self._tasks = tasks[:]
        self._validate()

    def _validate(self):
        if not all([callable(t) for t in self._tasks]):
            raise TypeError("Pipeline failed to validate, " \
                "all Tasks must be Callable")

    def execute(self, message):
        advancer = PipelineAdvancer(self._tasks)
        advancer(message)
        return advancer.message


class RepeatingPipeline(Pipeline):
    def __init__(self, controller=None,
                initialisers=[], tasks=[], finalisers=[]):
        Pipeline.__init__(self, tasks)
        self._controller = controller
        self._initialisers = initialisers
        self._finalisers = finalisers

    def execute(self, message):
        advancer = RepeatingPipelineAdvancer(self._controller, \
                    self._initialisers[:], self._tasks[:], \
                    self._finalisers[:])
        advancer.begin(message)
        return advancer._finaliser_pipe.message


if __name__ == "__main__":
    import doctest
    doctest.testmod()
