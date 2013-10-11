class PipeController:
    INSTRUCTION_CONTINUE = "continue"
    INSTRUCTION_STOP = "stop"

    def get_instruction(self, memory):
        return PipeController.INSTRUCTION_CONTINUE

class Pipeline:
    def __init__(self, controller=PipeController()):
        self.__controller = controller
        self.__operators = []
        self.__memory = dict()

    def execute(self):
        for operator in self.__operators:
            operator.execute(self.__memory)
