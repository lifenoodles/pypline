import sys
sys.path.append("..")
import pypline.pipeline
reload(pypline.pipeline)
from pypline.pipeline import Pipeline, PipeController, RepeatingPipeline


if __name__ == "__main__":
    def cap(message, pipeline):
        assert type(message) == type("")
        pipeline.resume(message.capitalize())

    def rev(message, pipeline):
        pipeline(message[-1::-1])

    def wait(message, pipeline):
        import time
        time.sleep(0)
        pipeline(message)

    pipe1 = Pipeline([cap, rev, wait])
    y = pipe1.execute("hello")
    print y

    class LengthController(PipeController):
        def done(self, message):
            print "Controller: %s" % message
            return len(message) > 10

    def addLetter(message, pipeline):
        import random, string
        pipeline(message + random.choice(string.lowercase))


    def init(message, pipeline):
        print "INIT: %s" % message
        pipeline(message)


    def final(message, pipeline):
        print "FINAL: %s" % message
        pipeline(message)


    pipe2 = RepeatingPipeline(LengthController(), [init], [addLetter], [final])
    y = pipe2.execute("hello")
    print y
