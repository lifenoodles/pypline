import collections
import pipeline
import re
import types


def extract_class(cls):
    match = re.search("__\.(.*)'", str(cls))
    if match is None or len(match.groups()) != 1:
        raise TypeError("%s is not a class!" % cls)
    return match.groups()[0]


def class_and_name(cls):
    if isinstance(cls, types.TupleType):
        return cls
    else:
        return (cls, extract_class(cls))


class NoRegisteredBuilderException(Exception):
    pass


class PipelineConfiguration(collections.defaultdict):
    def __init__(self, *args):
        super(PipelineConfiguration, self).__init__(list)
        for k, v in args:
            self[k] = v

    def __setitem__(self, k, v):
        if not isinstance(v, types.ListType):
            v = [v]
        super(PipelineConfiguration, self).__setitem__(k, v)


class PipelineBuilder(object):
    def __init__(self, name, task_builders):
        self.name = name
        self._task_builders = []
        self._task_names = []
        for task in task_builders:
            builder, builder_name = class_and_name(task)
            self._task_builders.append(builder)
            self._task_names.append(builder_name)

    def build(self, configuration):
        tasklist = []
        for task, key in zip(self._task_builders, self._task_names):
            args = configuration[key]
            tasklist.append(task(*args))
        return pipeline.Pipeline(tasklist)


class RepeatingPipelineBuilder(PipelineBuilder):
    def __init__(self, name, controller_builder=None,
                 initialiser_builders=[], task_builders=[],
                 finaliser_builders=[]):
        super(RepeatingPipelineBuilder, self).__init__(name, task_builders)
        self._controller_builder, self._controller_name =  \
            class_and_name(controller_builder)
        self._init_builders = []
        self._init_names = []
        self._final_builders = []
        self._final_names = []

        for task in initialiser_builders:
            builder, builder_name = class_and_name(task)
            self._init_builders.append(builder)
            self._init_names.append(builder_name)

        for task in finaliser_builders:
            builder, builder_name = class_and_name(task)
            self._final_builders.append(builder)
            self._final_names.append(builder_name)

    def build(self, configuration):
        initialisers, tasklist, finalisers = [], [], []
        controller = self._controller_builder(
            *configuration[self._controller_name])

        for task, key in zip(self._init_builders, self._init_names):
            args = configuration[key]
            initialisers.append(task(*args))

        for task, key in zip(self._task_builders, self._task_names):
            args = configuration[key]
            tasklist.append(task(*args))

        for task, key in zip(self._final_builders, self._final_names):
            args = configuration[key]
            finalisers.append(task(*args))

        return pipeline.RepeatingPipeline(
            controller, initialisers, tasklist, finalisers)


class PipelineFactory(object):
    def make_pipeline(self, pipeline_definition):
        raise NotImplementedError

    def make_repeating_pipeline(self, pipeline, definition):
        raise NotImplementedError


class PipeLineManager(object):
    def __init__(self, pipelines=[], run_count=1):
        self.run_count = run_count
        self.error_handler = None
        self.pipelines = []
        self._pipeline_builders = {}
        self._configurations = collections.defaultdict(list)

    def register_pipeline(self, pipeline):
        self.pipelines.append(pipeline)
        return self

    def register_pipeline_builder(self, builder):
        self._pipeline_builders[builder.name] = builder
        return self

    def register_configuration(self, name, config):
        self._configurations[name].append(config)
        return self

    def generate_pipelines(self):
        for builder in self._pipeline_builders.values():
            for config in self._configurations[builder.name]:
                self.pipelines.append(builder.build(config))
        return self

    def clear(self):
        self.pipelines = []
        self._pipeline_builders.clear()
        self._configurations.clear()

    def execute(self, init=None, verbose=False):
        for p, pipeline in enumerate(self.pipelines):
            if verbose:
                print "Starting pipeline %i" % (p + 1)
            for run in xrange(self.run_count):
                if verbose:
                    print "Run %i" % (run + 1)
                if self.error_handler is None:
                    pipeline.execute(init)
                else:
                    try:
                        pipeline.execute(init)
                    except Exception, e:
                        self.error_handler(e)
