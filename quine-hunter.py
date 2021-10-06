import random as rand
from abc import ABC
from fuck_interpreter import interpret
import sys


class Hunter(ABC):
    """
    A class for searching out brain-fuck quines,
    using the interpeter.
    """

    # The largest value possible in a cell, as anything larger
    # is not a character representable in python
    MAX_CELL_VALUE = 1114112

    @staticmethod
    def evaluate(source_arr):
        """
        Run the source code, and give a score array
        on it's 'quine-ness'. This is most importantly how similar the source
        code is to its own output, and secondarily its size.
        """

        # Turn source array to source str
        source = ''.join(source_arr)

        # TODO to calculate actual size, remove non-aplhab characters
        # source = source.replace
        out = interpret(source)
        diff_score = Hunter.score_difference(out, source)

        # Simmilarity is most important, then quine size
        return (diff_score, len(source))

    @staticmethod
    def score_difference(a, b):
        """
        Given two strings, score how different they are
        (between 0-1). 0 = same, 1 = very different
        Can swap this func out, but we use ascii distance for now.
        """
        # The 'worst' distance possible
        max_len = max(len(a), len(b))
        max_score = max_len * sys.maxunicode

        # Helper function for getting an character's numeric value,
        # given a string and an index in that string.
        # Gives the 'worst' possible value, if index > string length
        def get_chr_i(s, i):
            if i >= len(s):
                return sys.maxunicode
            else:
                return ord(s[i])

        diff_score = 0
        for i in range(max_len):

            ai = get_chr_i(a, i)
            bi = get_chr_i(b, i)

            diff_score += abs(ai - bi)

        return diff_score / max_score


class GeneticHunter(Hunter):
    """
    A genetic based implementation
    """

    # The mutation likleyhood for characters
    # Note: currently use 0 for ', input', as this
    # quine will not use it, but next goal should be
    # to see what is the smallest quine with the users
    # help!
    # Note: we have a space ' ' there as a way of leting
    # the hunter choose to have < max source code length
    # NOTE: the values here total to 1
    # TODO could make choosing a bracket automatically
    # create a pairing bracket somewhere else
    likleyhoods = {
        '+': .16,
        '-': .16,

        '>': .16,
        '<': .16,

        '.': .16,
        ',': 0,

        '[': .08,
        ']': .08,

        '': .04
    }

    # Length of source codes allowed
    SOURCE_LEN = 5  # TODO LONGER

    # Default number of generations to run
    DEFAULT_GENS = 100  # TODO LONGER

    # Default number of brain-fuck genes in the gene pool population
    DEFAULT_POP_SIZE = 500  # TODO LARGER

    # Percentage of the population to kill after each generation
    KILL_RATIO = .5

    # Likleyhood of any individual char to be mutated per generation
    RADIATION = .01

    # The likleyhood a char being inherited from your 'primary' parent
    INHERITENCE = .9

    def __init__(self, pop_size=None):
        """
        Create this hunter with empty parameters
        """

        if pop_size is None:
            pop_size = self.DEFAULT_POP_SIZE
        self.pop_size = pop_size

        # The souce code genes to be tested / mutated / killed and sexed
        self.population = [self.random_source()
                           for i in range(self.pop_size)]

    def random_source(self):
        """
        Create a tottally random source code array
        """
        chars = [self.get_mutation()
                 for i in range(self.SOURCE_LEN)]
        return chars

    def get_mutation(self):
        """
        Return a random character from the
        set of likleyhoods (dependent on their likleyhood)
        """
        # TODO optimize?
        r = rand.random()
        bar = 0
        for k, v in self.likleyhoods.items():
            bar += v
            if r <= bar:
                return k

    def run(self, n=None):
        """
        Run the genetic algorythm for a set number of generations,
        returning the best solution at the end
        """

        if n is None:
            n = self.DEFAULT_GENS

        print(f'Running for {n} generations')
        for i in range(n):
            self.step()
            best = self.population[-1]
            score = self.evaluate(best)
            print(f'  {i}: {"".join(best[:5])} {score}')
            for p in self.population:
                print('    ', "".join(p), interpret(p), self.evaluate(p))
            print()

        print(f'Best found {self.evaluate(best)}:')
        print('Source:')
        print(''.join(best))
        print('Output:')
        print(interpret(best))
        return best

    def step(self):
        # NOTE: I do this first so I by the end of 'step',
        # the population is sorted and ready to be pulled from
        # self.radiate()

        # Kill off the low performing genes,
        # then reporduce to fill the population gap
        self.purge()

    def radiate(self):
        # Sprinkle in some random mutations to each kid
        for i in range(len(self.population)):
            p = self.population[i]
            self.population[i] = self.mutate(p)

    def sort_pop(self):
        """
        Sort population from worst to best
        """
        self.population = sorted(self.population, key=self.evaluate)

    def purge(self):
        """
        Kill off the botom % of the population.
        TODO: dont make a perfect slice, but allow some
        variation in the middle
        """
        self.sort_pop()
        pop = self.population

        sex_cutoff = int(self.pop_size * self.KILL_RATIO)

        # sex_cutoff must be even for this impl
        if sex_cutoff % 2 == 1:
            sex_cutoff += 1

        sexy_pairs = []
        sexy_pop = []
        for i in range(sex_cutoff // 2):

            # Any time we run out of viable pairs, replenish & shuffle
            if len(sexy_pop) == 0:
                sexy_pop = pop[sex_cutoff:]
                rand.shuffle(sexy_pop)

            pair = (sexy_pop.pop(), sexy_pop.pop())
            sexy_pairs.append(pair)

        # Check to see some expectations hold true
        assert (len(sexy_pairs) == sex_cutoff // 2,
                f'Number of new pairs: {len(sexy_pairs)} '
                f'must replenish purged: {sex_cutoff}')

        for i in range(0, sex_cutoff, 2):
            parent_a, parent_b = sexy_pairs[i // 2]
            kid_a, kid_b = self.sex(parent_a, parent_b)
            pop[i] = kid_a
            pop[i + 1] = kid_b

        self.population = pop

    def sex(self, source_a, source_b):
        """
        TODO: not sure how I should decide what percentage
        comes from each parten (could also just be 50/50)
        """

        # Helper function for getting a character at index i from
        # either parent (dependent on inheritence)
        def get_char(primary, secondary, i):
            if rand.random() < self.INHERITENCE:
                return primary[i]
            return secondary[i]

        kid_a = [get_char(source_a, source_b, i)
                 for i in range(len(source_a))]
        kid_b = [get_char(source_b, source_a, i)
                 for i in range(len(source_b))]

        return kid_a, kid_b

    def mutate(self, source):
        """
        Apply random mutatuons to a source code's genes
        """
        for i in range(len(source)):
            if rand.random() < self.RADIATION:
                source[i] = self.get_mutation()
        return source


if __name__ == '__main__':
    h = GeneticHunter()
    best = h.run()
