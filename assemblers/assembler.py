from abc import ABCMeta, abstractmethod

class Assembler( ABC ):
    """Abstract base class for an assembler implementation"""

    @abstractmethod
    @staticmethod
    def assemble( file ):
        """Assembles a file into specific processor machine code

        Takes a file path, creates .p and .e files containing machine code, and
        returns a (message, success) pair
        """
        pass
