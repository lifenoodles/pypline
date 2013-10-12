from task import BundleMixin


class PipeController():
    def done(self, message):
        return True


class BundlePipeController(PipeController, BundleMixin):
    def done(self, message):
        return True


class Pipeline(object):
    def __init__(self, tasks=[]):
        self.__tasks = tasks
        self.__validate()

    def add_task(self, task):
        self.__tasks.append(task)


    def add_task_after(self, task, cls):
        index = next(i for (i, x) in enumerate(self.__tasks)
            if x.__class__ == cls)
        self.__tasks.insert(task, index)


    def __validate(self):
        if not all([callable(t) for t in self.__tasks]):
            raise TypeError("Pipeline failed to validate, " \
                " all Tasks must be Callable")

    def execute(self, message):
        for task in self.__tasks:
            task(message, self)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
