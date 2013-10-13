import sys
sys.path.append("..")
from pypline.pipeline import Pipeline
from pypline.task import Task


if __name__ == "__main__":
    def cap(message, resume, pipeline):
        assert type(message) == type("")
        resume(message.capitalize())

    def rev(message, resume, pipeline):
        resume(message[-1::-1])

    def wait(message, resume, pipeline):
        import time
        time.sleep(1)
        resume(message)

    pipe1 = Pipeline(rev, cap, rev, wait)
    y = pipe1.execute("hello")
    print y
