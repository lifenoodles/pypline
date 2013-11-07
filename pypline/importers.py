import abc
import imp
import inspect
import managers
import os


def import_file(filename):
    path = os.path.abspath(os.path.dirname(filename))
    name = os.path.splitext(os.path.basename(filename))[0]
    results = imp.find_module(name, [path])
    module = imp.load_module(name, results[0], results[1], results[2])
    return module


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
        module = import_file(modulefile)
        classes = inspect.getmembers(module, inspect.isclass)
        for name, cls in classes:
            if hasattr(cls, "process"):
                if self.tasks.has_key(name):
                    raise KeyError("Task %s defined in multiple modules!" % name)
                self.tasks[name] = cls
        return self


class ManagerBuilder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build_manager(self):
        raise NotImplementedError


class PythonManagerBuilder(ManagerBuilder):
    def build_repeating(self, pipespec):
        pass

    def build_pipeline(self, pipespec):
        pass

    def build_manager(self, filename):
        spec = import_file(filename)
        modules = spec.modules
        importer = ModuleTaskImporter()

        for module in modules:
            importer.import_tasks(module)

        manager = managers.PipeLineManager()
        for pipe in spec.pipelines:
            if pipe.has_key("controller"):
                pipe_builder, configs = self.build_repeating(pipe)
            else:
                pipe_builder, configs = self.build_pipeline(pipe)
            manager.register_pipeline_builder(pipe_builder)
            for conf in configs:
                manager.register_configuration(pipe_builder.name, conf)
        return manager




if __name__ == "__main__":
    PythonManagerBuilder().build_manager("../tests/test_pipeline_conf.py")
