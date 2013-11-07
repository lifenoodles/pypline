import abc
import imp
import inspect
import os


class TaskImporter(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self.tasks = {}

    @abc.abstractmethod
    def import_tasks(self):
        raise NotImplementedError


class ModuleTaskImporter(TaskImporter):
    def __init__(self):
        super(ModuleTaskImporter, self).__init__()

    def import_tasks(self, modulefile):
        path = os.path.dirname(modulefile)
        name = os.path.splitext(os.path.basename(modulefile))[0]
        results = imp.find_module(name, [path])
        module = imp.load_module(name, results[0], results[1], results[2])
        classes = inspect.getmembers(module, inspect.isclass)
        for name, cls in classes:
            if hasattr(cls, "process"):
                self.tasks[name] = cls
        return self


if __name__ == "__main__":
    print ModuleTaskImporter().import_tasks("task").tasks
