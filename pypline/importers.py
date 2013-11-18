import abc
import itertools
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
                if name in self.tasks:
                    raise KeyError("Task %s defined in multiple modules!" % name)
                self.tasks[name] = cls
        return self


class ManagerBuilder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build_manager(self):
        raise NotImplementedError


class PythonManagerBuilder(ManagerBuilder):
    def build_repeating(self, spec, tasks):
        task_names = set()
        parameter_lists = []
        parameter_names = []

        def process_task(task):
            inc = 1
            name = task["name"]
            modified_name = name
            while modified_name in task_names:
                modified_name = name + str(inc)
                inc += 1
            task_names.add(modified_name)
            parameter_lists.append(task["params"])
            parameter_names.append(modified_name)
            return (tasks[name], modified_name)

        pipe_name = spec["name"]
        controller = process_task(spec["controller"])
        initialisers, main_tasks, finalisers = [], [], []

        for init in spec["initialisers"]:
            initialisers.append(process_task(init))
        for task in spec["tasks"]:
            main_tasks.append(process_task(task))
        for final in spec["finalisers"]:
            finalisers.append(process_task(final))

        builder = managers.RepeatingPipelineBuilder(
            pipe_name, controller, initialisers, main_tasks, finalisers)

        configs = []
        config_combos = [c for c in itertools.product(*parameter_lists)]
        for combo in config_combos:
            config = managers.PipelineConfiguration()
            for name, c in zip(parameter_names, combo):
                config[name] = c
            print config
        return (builder, configs)

    def build_pipeline(self, spec):
        pass

    def build_manager(self, filename):
        spec = import_file(filename)
        modules = spec.modules
        importer = ModuleTaskImporter()

        for module in modules:
            importer.import_tasks(module)

        manager = managers.PipeLineManager()
        for pipe in spec.pipelines:
            if "controller" in pipe:
                pipe_builder, configs = self.build_repeating(
                    pipe, importer.tasks)
            else:
                pipe_builder, configs = self.build_pipeline(
                    pipe, importer.tasks)
            manager.register_pipeline_builder(pipe_builder)
            for conf in configs:
                manager.register_configuration(pipe_builder.name, conf)
        return manager

if __name__ == "__main__":
    x = PythonManagerBuilder().build_manager("../tests/test_pipeline_conf.py")
