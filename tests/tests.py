import unittest
import sys
sys.path.append("..")
import pypline


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
    def __init__(self, number):
        self.number = number;

    def process(self, message, pipeline):
        return message + "TASK %d\n" % self.number


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
        p = pypline.RepeatingPipeline(ControllerN(3), \
                [Initialiser()], \
                [GenericTask(1), GenericTask(2)], \
                [Finaliser()])
        self.assertTrue(p.execute() == "INIT\nTASK 1\nTASK 2\nTASK 1\n" \
                "TASK 2\nTASK 1\nTASK 2\nFINAL\n")

if __name__ == "__main__":
    unittest.main()
