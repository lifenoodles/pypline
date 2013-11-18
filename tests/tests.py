import unittest
import sys
sys.path.append("..")
import pypline
from pypline import managers


class Initialiser(pypline.Task):
    def process(self, message, pipeline):
        return "INIT\n"


class Finaliser(pypline.Task):
    def process(self, message, pipeline):
        return message + "FINAL\n"


class ControllerN(pypline.Task):
    def __init__(self, n):
        self.n = n

    def process(self, message, pipeline):
        self.n -= 1
        return self.n < 0


class GenericTask(pypline.Task):
    def __init__(self, number=0):
        self.number = number

    def process(self, message, pipeline):
        return message + "TASK %s\n" % self.number


class Cap(pypline.Task):
    def process(self, message, pipeline):
        return message.capitalize()


class Reverse(pypline.Task):
    def process(self, message, pipeline):
        return message[-1::-1]


class TimesN(pypline.Task):
    def __init__(self, n=2):
        self.n = n

    def process(self, message, pipeline):
        return message * self.n


class TestPipeLine(unittest.TestCase):
    def test_empty(self):
        p = pypline.Pipeline()
        p.execute()

    def test_simple(self):
        p = pypline.Pipeline([Cap(), Reverse()])
        self.assertTrue(p.execute("hello") == "olleH")

    def test_non_callable(self):
        self.assertRaises(TypeError, pypline.Pipeline, [1, 2])

    def test_repeating(self):
        p = pypline.RepeatingPipeline(
            ControllerN(3), [Initialiser()], [GenericTask(1), GenericTask(2)],
            [Finaliser()])
        self.assertTrue(p.execute() == "INIT\nTASK 1\nTASK 2\nTASK 1\n"
                        "TASK 2\nTASK 1\nTASK 2\nFINAL\n")


class TestPipelineBuilder(unittest.TestCase):
    def test_normal(self):
        b = managers.PipelineBuilder(
            "SamplePipe", [(GenericTask, "task1"), GenericTask])
        conf = managers.PipelineConfiguration(("GenericTask", 2))
        conf["task1"] = [1]
        p = b.build(conf)
        self.assertTrue(p.execute("") == "TASK 1\nTASK 2\n")

    def test_repeating(self):
        b = managers.RepeatingPipelineBuilder(
            "SamplePipe", (ControllerN, "controller"),
            [Initialiser],
            [(GenericTask, "task1"), (GenericTask, "task2")],
            [Finaliser])
        conf = managers.PipelineConfiguration()
        conf["controller"] = 2
        conf["task1"] = 1
        conf["task2"] = 2
        p = b.build(conf)
        self.assertTrue(p.execute() == "INIT\n"
                        "TASK 1\nTASK 2\nTASK 1\nTASK 2\nFINAL\n")


class TestPipeLineManager(unittest.TestCase):
    def test_create(self):
        manager = pypline.PipeLineManager()
        b = managers.PipelineBuilder(
            "SamplePipe",
            [Initialiser, (GenericTask, "task1"), (GenericTask, "task2")])
        conf_1 = managers.PipelineConfiguration()
        conf_1["task1"] = "C1T1"
        conf_1["task2"] = "C1T2"
        conf_2 = managers.PipelineConfiguration(("task1", "C2T1"), ("task2", "C2T2"))
        manager.register_pipeline_builder(b).register_configuration(
            "SamplePipe", conf_1).register_configuration(
            "SamplePipe", conf_2).generate_pipelines()
        result = ""
        for p in manager._pipelines:
            result += p.execute()
        self.assertTrue(result ==
                        "INIT\nTASK C1T1\nTASK C1T2\nINIT\nTASK C2T1\nTASK C2T2\n")


if __name__ == "__main__":
    unittest.main()
