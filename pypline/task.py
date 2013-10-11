import abc

class Task(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, message, pipeline):
        raise NotImplementedError


class ParameterisedMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parameter_list(self, message, pipeline):
        raise NotImplementedError


class BundleMixin(object):
    __metaclass__ = abc.ABCMeta

    def requires(self):
        return []

    def provides(self):
        return []


class Parameter(object):
    """
    >>> Parameter(int, "Name").is_ok(2)
    True
    >>> Parameter(str, "Name").is_ok(3)
    False
    >>> Parameter(float, "Name").is_ok(2.2)
    True
    """
    def __init__(self, cls, name):
        self.cls = cls
        self.name = name

    def is_ok(self, param):
        return issubclass(param.__class__, self.cls)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
