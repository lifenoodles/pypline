import pipeline


class NotRegisteredBuilderException(Exception): pass

class PipelineDefinition(object):
    def __init__(self, name, tasks):
        self.name = name
        self.tasks = tasks[:]


class RepeatingPipelineDefinition(object):
    def __init__(self, name, controller, initialisers, tasks, finalisers):
        self.name = name
        self.controller = controller
        self.initialisers = initialisers[:]
        self.tasks = tasks[:]
        self.finalisers = finalisers[:]


class PipelineFactory(object):
    def make_pipeline(self, pipeline_definition):
        raise NotImplementedError

    def make_repeating_pipeline(self, pipeline, definition):
        raise NotImplementedError


class PipeLineManager(object):
    def __init__(self, pipelines=[]):
        self.pipelines = []
        self.pipeline_defs = []
        self.task_builders = {}

    def add_pipeline(self, pipeline):
        self.pipelines.append(pipeline)
        return self

    def add_task_builder(self, builder):
        builder_name = str(builder).split('.')[-1]
        self.task_builders[builder_name] = builder
        return self

    def build_pipeline(self, builder_names, args):
        builders = []
        for i, builder in enumerate(builder_names):
            if self.task_builders.has_key(builder):
                builders[i] = self.task_builders[builder]
            else:
                raise NotRegisteredBuilderException("No registered "
                        "builder with that name")

        for i, (builder, args) in enumerate(zip(builders, args)):
            builders[i] = builder(*args)

        pipe = pipeline.Pipeline(builders)
        self.pipelines.append(pipe)
        # return self or pipe here?
        return self


