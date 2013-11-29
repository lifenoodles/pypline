import abc


class requires:
    def __init__(self, *args):
        self.args = args

    def __call__(self, cls):
        cls.requires = self.args
        return cls


class provides:
    def __init__(self, *args):
        self.args = args

    def __call__(self, cls):
        cls.provides = self.args
        return cls


class Task(object):
    __metaclass__ = abc.ABCMeta
    requires = []
    provides = []

    @abc.abstractmethod
    def process(self, message, pipeline):
        raise NotImplementedError


class AsyncTask(Task):
    # this makes me feel dirty
    _async_flag = True


class ParameterisedMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parameter_list(self):
        raise NotImplementedError
