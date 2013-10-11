from task import BundleMixin


class PipeController():
    def done(self, message):
        return True


class BundlePipeController(PipeController, BundleMixin):
    def done(self, message):
        return True


class Pipeline(object):
    def __init__(self, message, tasks=[]):
        self.message = message
        self.__tasks = tasks

    def validate(self):
        return all([callable(t) for t in self.__tasks])

    def execute(self):
        if not self.validate():
            raise TypeError("Pipeline failed to validate, " \
                " all Tasks must be Callable")
        for task in self.__tasks:
            task(self.message, self)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
