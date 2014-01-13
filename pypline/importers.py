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

    def build_repeating(self, pipe_spec, tasks):
        task_names = set()
        parameter_lists = []

        def process_task(task):
            inc = 1
            name = task["name"]
            modified_name = name
            while modified_name in task_names:
                modified_name = name + str(inc)
                inc += 1
            task_names.add(modified_name)
            if "params" in task:
                parameter_lists.append(map(
                    lambda x: (modified_name, x), task["params"]))
            return (tasks[name], modified_name)

        pipe_name = pipe_spec["name"]
        controller = process_task(pipe_spec["controller"])
        initialisers, main_tasks, finalisers = [], [], []

        for init in pipe_spec["initialisers"]:
            initialisers.append(process_task(init))
        for task in pipe_spec["tasks"]:
            main_tasks.append(process_task(task))
        for final in pipe_spec["finalisers"]:
            finalisers.append(process_task(final))

        builder = managers.RepeatingPipelineBuilder(
            pipe_name, controller, initialisers, main_tasks, finalisers)

        configs = []
        config_combos = [c for c in itertools.product(*parameter_lists)]
        for combo in config_combos:
            config = managers.PipelineConfiguration()
            for (name, c) in combo:
                config[name] = c
            configs.append(config)
        return (builder, configs)

    def build_pipeline(self, spec):
        raise NotImplementedError

    def build_manager(self, spec):
        modules = spec["modules"]
        run_count = spec["runs"]
        importer = ModuleTaskImporter()

        for module in modules:
            importer.import_tasks(module)

        manager = managers.PipeLineManager(run_count=int(run_count))
        for pipe in spec["pipelines"]:
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


class PythonManagerBuilder(ManagerBuilder):
    def build_manager(self, filename):
        spec_module = import_file(filename)
        return super(PythonManagerBuilder, self).build_manager(spec_module.spec)


class YamlManagerBuilder(ManagerBuilder):
    def build_manager(self, filename):
        import yaml
        spec = {}
        with open(filename) as f:
            spec = yaml.load(f)
        return super(YamlManagerBuilder, self).build_manager(spec)

if __name__ == "__main__":
    x = YamlManagerBuilder().build_manager("../tests/test_pipeline_conf.yaml")
    x.generate_pipelines()
    x.execute(verbose=True)
