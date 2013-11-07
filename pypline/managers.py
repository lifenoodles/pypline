import collections
import pipeline
import re
import types


def extract_class(cls):
    match = re.search("__\.(.*)'", str(cls))
    if match is None or len(match.groups()) != 1:
        raise TypeError ("%s is not a class!" % cls)
    return match.groups()[0]


def class_and_name(cls):
    if type(cls) == types.TupleType:
        return cls
    else:
        return (cls, extract_class(cls))


class NoRegisteredBuilderException(Exception): pass


class PipelineConfiguration(collections.defaultdict):
    def __init__(self, *args):
        super(PipelineConfiguration, self).__init__(list)
        for k, v in args:
            self[k] = v

    def __setitem__(self, k, v):
        if type(v) != types.ListType:
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
    def __init__(self, name, controller_builder=None, \
            initialiser_builders=[], task_builders=[], \
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
        controller = self._controller_builder( \
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

        return pipeline.RepeatingPipeline(controller, \
                initialisers, tasklist, finalisers)


class PipelineFactory(object):
    def make_pipeline(self, pipeline_definition):
        raise NotImplementedError

    def make_repeating_pipeline(self, pipeline, definition):
        raise NotImplementedError


class PipeLineManager(object):
    def __init__(self, pipelines=[]):
        self._pipelines = []
        self.pipeline_defs = []
        self.task_builders = collections.defaultdict(list)
        self.controller_builders = collections.defaultdict(list)

    def _validate_task_key(self, key):
        if not self.task_builders.has_key(key):
            raise NoRegisteredBuilderException("No registered "
                    "builder with the name: %s" % key)

    def add_pipeline(self, pipeline):
        self._pipelines.append(pipeline)
        return self

    def register_task(self, builder):
        builder_name = extract_class(builder)
        self.task_builders[builder_name] = builder
        return self

    def register_arguments(self, task_name, *args):
        self._validate_task_key(task_name)
        for arg in args:
            self.task_builders.append(arg)
        return self

    def register_controller(self, builder):
        builder_name = str(builder).split('.')[-1]
        self.task_builders[builder_name] = builder
        return self

    def build_pipeline(self, *args):
        """
        Builds a pipeline given a list of tuples of the form:
        (builder, argument list)
        """
        builders = []
        for i, (builder, arguments) in enumerate(args):
            self._validate_task_key(builder)
            builders.append(self.task_builders[builder](*arguments))


        pipe = pipeline.Pipeline(builders)
        self._pipelines.append(pipe)
        # return self or pipe here?
        return pipe



