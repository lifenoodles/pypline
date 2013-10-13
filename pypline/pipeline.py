from task import BundleMixin
import abc


class PipelineAdvancer(object):
    def __init__(self, pipeline, tasks):
        self.__pipeline = pipeline
        self.__iterator = iter(tasks)
        self.message = None

    def __call__(self, message):
        self.message = message
        try:
            return next(self.__iterator)(message, self, self.__pipeline)
        except StopIteration:
            pass

class PipeController():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def done(self, message):
        raise NotImplementedError


class BundlePipeController(PipeController, BundleMixin):
    pass


class Pipeline(object):
    def __init__(self, *tasks):
        self.__tasks = tasks
        self.__validate()

    def __validate(self):
        if not all([callable(t) for t in self.__tasks]):
            raise TypeError("Pipeline failed to validate, " \
                "all Tasks must be Callable")

    def execute(self, message):
        advancer = PipelineAdvancer(self, self.__tasks)
        advancer(message)
        return advancer.message


class RepeatingPipeline(Pipeline):
    def __init__(self, controller=None, tasks=[]):
        Pipeline.__init__(self, tasks)
        self.controller = controller

    def execute(self, message):
        while not self.controller.done():
            for task in self.__tasks:
                task(message, self)


class ModifiableMixin(object):
    def add_task(self, task):
        self.__tasks.append(task)

    def add_task_after(self, task, cls):
        index = next(i for (i, x) in enumerate(self.__tasks)
            if x.__class__ == cls)
        self.__tasks.insert(task, index + 1)

    def add_task_before(self, task, cls):
        index = next(i for (i, x) in enumerate(self.__tasks)
            if x.__class__ == cls)
        self.__tasks.insert(task, index)

    def remove_task(self, cls):
        index = next(i for (i, x) in enumerate(self.__tasks)
            if x.__class__ == cls)
        self.__tasks = self.__tasks[:index] + self.__tasks[index + 1:]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
