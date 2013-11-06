import unittest
import sys
sys.path.append("..")
import pypline


class Initialiser(pypline.Task):
    def __call__(self, message, pipeline):
        return "INIT\n"


class ControllerN(pypline.Task):
    pass


class Cap(pypline.Task):
    def __call__(self, message, pipeline):
        return message.capitalize()


class Reverse(pypline.Task):
    def __call__(self, message, pipeline):
        return message[-1::-1]


class TimesN(pypline.Task):
    def __init__(self, n=2):
        self.n = n

    def __call__(self, message, pipeline):
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


if __name__ == "__main__":
    unittest.main()

    class MyStr(pypline.Task):
        def __call__(self, message, pipe):
            return str(message)

    class MyInt(pypline.Task):
        def __call__(self, message, pipe):
            return int(message)

    p = pypline.Pipeline([MyStr(), MyInt()])
    p.add_task_after(MyStr(), MyInt)
    print p.execute(1)
