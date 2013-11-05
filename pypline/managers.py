import pipeline


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

    def add_pipeline(self, pipeline):
        self.pipelines.append(pipeline)

