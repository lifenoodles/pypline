import sys
sys.path.append("..")
import pypline


class TestController(pypline.Task):
    def __init__(self, count):
        self.count = count

    def process(self, message, pipeline):
        self.count -= 1
        return self.count < 0


class EmptyInitialiser(pypline.Task):
    def process(self, message, pipeline):
        return ""


class TestTask(pypline.Task):
    def __init__(self, string):
        self.string = string

    def process(self, message, pipeline):
        return message + "TASK %s\n" % self.string
