import sys
sys.path.append("..")
import pypline.pipeline
import timeit
reload(pypline.pipeline)
reload(pypline.task)
from pypline.pipeline import Pipeline, PipeController, RepeatingPipeline
from pypline.task import AsyncTask


if __name__ == "__main__":
    def cap(message, pipeline):
        assert type(message) == type("")
        return message.capitalize()

    def rev(message, pipeline):
        return message[-1::-1]

    def wait(message, pipeline):
        import time
        time.sleep(0)
        return message

    class GetKeyboardInput(AsyncTask):
        def __call__(self, message, pipeline, callback):
            from threading import Thread
            def get_inp():
                x = raw_input()
                callback(x)
            Thread(target=get_inp).start()
            print "LOOK MA THREADS"


    pipe1 = Pipeline([GetKeyboardInput(), cap, rev])
    y = pipe1.execute()
    print y

    # class LengthController(PipeController):
    #     def done(self, message):
    #         print "Cont: %s" % message
    #         return len(message) > 10000

    # def addLetter(message, pipeline):
    #     import random, string
    #     pipeline(message + random.choice(string.lowercase))

    # def addLetter2(message):
    #     import random, string
    #     return message + random.choice(string.lowercase)


    # def init(message, pipeline):
    #     pipeline(message)


    # def final(message, pipeline):
    #     pipeline(message)


    # pipe2 = RepeatingPipeline(LengthController(), [init], [addLetter], [final])
    # now = timeit.default_timer()
    # y = pipe2.execute("hello")
    # print y
    # print timeit.default_timer() - now

    # now = timeit.default_timer()
    # msg = "hello"
    # cont = LengthController()
    # while not cont.done(msg):
    #     msg = addLetter2(msg)
    # print msg
    # print timeit.default_timer() - now
