from abc import ABCMeta, abstractmethod


class Assembler(metaclass=ABCMeta):
    """Abstract base class for an assembler implementation

    Assembler is line-based, assembly language is supposed by default to have a
    certain structure, but it can be overriden if so desired.

    Structure:
    |LABEL      CMD ...
    |           CMD ...
        - words on the start of the line are considered to be labels, so instructions should always be indented
        - comments can begin anywhere, and should start with a LINE_COMMENT_START symbol
        - assembly source code is case insensitive

    Various parameters can be set in the config object.
    """

    config = {
        'WORD_SIZE_BYTES': 4,
        'WORD_SIZE_BITS': 32,
        'HALFWORD_SIZE_BYTES': 2,
        'HALFWORD_SIZE_BITS': 16,

        'LINE_COMMENT_START': ';',
        'PSEUDOCOMMAND_PREFIX': '',
        'REGISTERS_PREFIX': ''
    }

    @staticmethod
    @abstractmethod
    def assemble(file):
        """Assembles a file into specific processor machine code

        Takes a file path, creates .p and .e files containing machine code, and
        returns a (message, success) pair
        """
        pass
