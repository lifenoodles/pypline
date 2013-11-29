import abc


def requires(cls, *args):
    cls.requires = args
    return cls


def provides(cls, *args):
    cls.provides = args
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
