import unittest
import sys
sys.path.append("..")
import pypline

class Cap(pypline.Task):
    def __call__(self, message, pipeline):
        return message.capitalize()

def rev(message, pipeline):
    return message[-1::-1]


def make_simple_pipe():
    return pypline.Pipeline([Cap(), rev])


class TestPipeLine(unittest.TestCase):
    def test_empty(self):
        p = pypline.Pipeline()
        p.execute()

    def test_simple(self):
        p = make_simple_pipe()
        self.assertTrue(p.execute("hello") == "olleH")

    def test_non_callable(self):
        self.assertRaises(TypeError, pypline.Pipeline, [1, 2])


if __name__ == "__main__":
    unittest.main()
    pass
