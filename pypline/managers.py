import collections
import pipeline
import re


class NoRegisteredBuilderException(Exception): pass


class PipelineDefinition(object):
    def __init__(self, name, tasks):
        self.name = name
        self.task_builders = tasks[:]


class RepeatingPipelineDefinition(object):
    def __init__(self, name, controller, initialisers, tasks, finalisers):
        self.name = name
        self.controller = controller
        self.initialiser_builders = initialisers[:]
        self.task_builders = tasks[:]
        self.finaliser_builders = finalisers[:]


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

    def _extract_class(self, cls):
        match = re.search("__\.(.*)'", str(cls))
        if match is None or len(match.groups()) != 1:
            raise TypeError ("%s is not a class!" % cls)
        return match.groups()[0]

    def add_pipeline(self, pipeline):
        self._pipelines.append(pipeline)
        return self

    def register_task(self, builder):
        builder_name = self._extract_class(builder)
        print builder_name
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



