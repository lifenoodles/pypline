import sys
sys.path.append("..")
from pypline import pipeline, task

class GaSolution(object):
    def __init__(self, genes=[]):
        self.genes = genes
        self.fitness = sys.maxint


class StringGaData(object):
    def __init__(self, target, size):
        self.target = target
        self.population = []
        self.best = None
        import string
        self.allowed_genes = string.lowercase + " "
        self.generation = 0


class GaController(pipeline.PipeController):
    def __call__(self, data):
        data.generation += 1
        if data.best is not None:
            return "".join(data.best.genes) == data.target \
                    or data.generation > 100
        return False


class GaInitialiser(task.Task):
    def __init__(self, target, size):
        self.target = target
        self.size = size

    def __call__(self, data, pipeline):
        ga_data = StringGaData(self.target, self.size)
        import string, random
        genes = string.lowercase + " "
        for i in xrange(self.size):
            new_genes = [random.choice(genes) for
                    x in range(len(ga_data.target))]
            ga_data.population.append(GaSolution(new_genes))
        return ga_data


def evaluate(data, pipeline):
    for solution in data.population:
        fitness = 0
        for i, gene in enumerate(solution.genes):
            if gene != data.target[i]:
                fitness += 1
        solution.fitness = fitness
        data.best = max(data.population, key=lambda x: x.fitness)
    return data


def crossover(data, pipeline):
    import random
    # sort population and take best half
    size = len(data.population)
    data.population.sort(key=lambda x: x.fitness)
    midpoint = len(data.population) / 2
    parents = data.population[:midpoint]
    parents += parents
    random.shuffle(parents)
    parents = zip(parents[::2], parents[1::2])
    new_pop = []
    for a, b in parents:
        point = random.randint(1, len(a.genes) - 1)
        genes = a.genes[:point] + b.genes[point:]
        new_pop.append(GaSolution(genes))
        genes = b.genes[:point] + a.genes[point:]
        new_pop.append(GaSolution(genes))
    data.population = new_pop
    assert size == len(data.population)
    return data

class GaMutator(task.Task):
    def __init__(self, mutation_rate):
        self.mutation_rate = mutation_rate

    def __call__(self, data, pipeline):
        import random
        for solution in data.population:
            if random.random() < self.mutation_rate:
                solution.genes[random.randint(0, len(solution.genes) - 1)] = random.choice(data.allowed_genes)
        return data

class GaLogger(task.Task):
    def __init__(self, file_to_use):
        self.file = file_to_use

    def __call__(self, data, pipeline):
        with open(self.file, "a") as f:
            f.write("%s\n" % "".join(data.best.genes))
        return data

if __name__ == "__main__":
    #contruct pipeline
    controller = GaController()
    initialiser = GaInitialiser("this is a sample string", 100)
    mutator = GaMutator(0.1)
    open("logfile", "w").close()
    logger = GaLogger("logfile")

    ga = pipeline.RepeatingPipeline(controller,
            [initialiser],
            [evaluate, crossover, mutator, logger])
    ga.execute()
