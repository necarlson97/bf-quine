import glob
import sys
import test_interpreter

class Interpreter():
    """
    Brain fuck interpreter
    """

    # How many ticks will be allowed before an 'overflow' is thrown
    LIMIT = 2000

    # Maximum value in a cell - others seem to set to 255
    CELL_MAX = 255

    # Alphabet that decides what function each char has
    # Because we want this static, we use the getattr names
    # rather than the self. definitions
    ALPHAB = {
        '+': '_inc',
        '-': '_dec',

        '>': '_inc_pointer',
        '<': '_dec_pointer',

        '.': '_output',
        ',': '_input',

        '[': '_jump',
        ']': '_jump_back',
    }

    def __init__(self):
        """
        Initilize a new running enviorment for brain-fuck
        """

        # Replace the str names of the alphab functions
        # with the actual self. definitons
        self.alphab = {}
        for k, v in self.ALPHAB.items():
            self.alphab[k] = getattr(self, v)

        self.pointer = 0
        self.cells = {}

    def reset(self):
        """
        Reset the program state
        """
        self.pointer = 0
        self.cells = {}

        self.output = ""

    def interpret(self, source_code: str, reset=True):
        """
        Run a brain-fuck source code
        NOTE: Currently, you can implement more code ontop of the current
        program state, almost like a typical interpreter.
        (Usign reset=False)
        """
        if reset:
            self.reset()

        self.source_code = source_code
        self.source_pointer = 0
        self.ticks = 0

        while self.source_pointer < len(source_code):
            # Just skip stuff not a bf character
            c = self.source_code[self.source_pointer]
            if c in self.alphab:
                # Call the function at that char
                self.alphab[c]()

            self.source_pointer += 1
            self.ticks += 1

            if self.ticks > self.LIMIT:
                self._fucked()

        return str(self)

    def _inc(self):
        # Increment current cell value
        c, p = self.cells, self.pointer
        c[p] = c.get(p, 0) + 1
        # Set maximum
        c[p] = min(c[p], self.CELL_MAX)

    def _dec(self):
        # Decrement current cell value
        c, p = self.cells, self.pointer
        c[p] = c.get(p, 0) - 1
        # No negatives
        c[p] = max(c[p], 0)

    def _inc_pointer(self):
        # Increment cell position
        self.pointer += 1

    def _dec_pointer(self):
        # Decrement cell position
        self.pointer -= 1
        # No negatives!
        self.pointer = max(self.pointer, 0)

    def _output(self):
        # Add current cell to output string
        self.output += self.get_chr(self.cells.get(self.pointer, 0))

    def _input(self):
        # Take in user input, place in current cell
        i = ord(input('?: '))
        self.cells[self.pointer] = i
        raise NotImplementedError('Make this better before using it')

    def _jump(self):
        # If current cell == 0:
        # Move forward from '[' in source code to paired ']'

        if self.cells.get(self.pointer, 0) != 0:
            return

        # Number of open braces we need to close
        to_close = 1
        # The ammound that will be added to the source_pointer at the end
        to_add = 1

        for c in self.source_code[self.source_pointer:]:
            if c == '[':
                to_close += 1
            elif c == ']':
                to_close -= 1

            if to_close == 0:
                self.source_pointer += to_add
                return

            to_add += 1

    def _jump_back(self):
        # If current cell != 0:
        # Move backward from ']' in source code to paired '['

        if self.cells.get(self.pointer, 0) == 0:
            return

        # Number of closed braces we need to open
        to_open = 1
        # The ammound that will be added to the source_pointer at the end
        to_sub = 1

        rev_source_chunk = self.source_code[:self.source_pointer][::-1]
        for c in rev_source_chunk:
            if c == '[':
                to_open -= 1
            elif c == ']':
                to_open += 1

            if to_open == 0:
                self.source_pointer -= to_sub
                return

            to_sub += 1

    def get_chr(self, i):
        # Saftey wrapper around (chr), allows us to play
        # with larger cell values than chr allows
        # return the maximum allowed
        try:
            return chr(i)
        except ValueError as e:
            return chr(sys.maxunicode)

    def __str__(self):
        print('Brain Dump:')
        print(self._brain_dump())
        print('Output Dump:')
        print([ord(c) for c in self.output])
        return self.output

    def _brain_dump(self):
        # For every value in the cells list,
        # give the ascii
        return [self.get_chr(c) for c in self.cells.values()]

    def _fucked(self):
        raise ValueError(f'Fucked at {self.ticks} ticks.\n'
                         f'Pointer at: {self.pointer}\n'
                         f'Cells: {self.cells}\n'
                         f'Brain dump: {self._brain_dump()}\n')


def interpret(source_code: str):
    inter = Interpreter()

    # We are treating exceptions as a valid exit,
    # using what is currently in the prog env output
    # as the final output
    # Because I want to thats why!
    try:
        ret = inter.interpret(source_code)
    except ValueError as e:
        ret = str(inter)
    return ret


def clean(source_code):
    ret = ''
    for c in source_code:
        if c in Interpreter.ALPHAB:
            ret += c
    return ret


if __name__ == '__main__':
    """
    For every '.bf' (brain fuck) file in this dir,
    run the intereter to create a '.bfo'
    (brain fuck output)
    """
    for filename in glob.glob("*.bf"):
        with open(filename) as f:
            source = f.read()
            print(f'Interpreting:\n{filename}:\n{source}')
            print(f'Clean:\n{clean(source)}')
            try:
                out = interpret(source)
                print(f'Output:\n{out}')
                print()
                other_out = test_interpreter.evaluate(source)
                print(f'Other Interpeter:\n{other_out}')
                print()
            except ValueError as e:
                print(e)
