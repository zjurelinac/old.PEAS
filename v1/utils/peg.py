import re

from abc import ABCMeta, abstractmethod
from utils.helpers import tail

# Token-based PEG parsing


class Item(metaclass=ABCMeta):

    @abstractmethod
    def __call__(self, arguments):
        pass

    def __repr__(self):
        return str(self)


class Token(Item):
    pattern = ''

    def __init__(self, contents=None, pattern=None):
        self.pattern = re.compile(pattern if pattern is not None else self.pattern)
        self.contents = contents

    def __call__(self, arguments):
        if not arguments:
            raise SyntaxError('{} :: Nothing to parse', self)
        if re.fullmatch(self.pattern, arguments[0]):
            return self.__class__(arguments[0]), tail(arguments)
        else:
            raise SyntaxError('{} :: Cannot match {}', self, arguments)

    def __str__(self):
        if self.contents is not None:
            return '{}: {}'.format(self.__class__.__name__, self.contents)
        else:
            return '{}: {} :: <Unmatched>'.format(self.__class__.__name__, self.pattern)


class Modifier(Item):

    def __init__(self, item):
        self.item = item

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.item)


class Combinator(Item):
    items = ()

    def __init__(self, *args):
        if args:
            self.items = tuple(args)

    def __str__(self):
        return '{}: [{}]'.format(self.__class__.__name__, str(self.items))


# Combinators

class Or(Combinator):

    def __call__(self, arguments):
        for item in self.items:
            try:
                return item(arguments)
            except Exception:
                pass
        raise SyntaxError('{} :: Cannot match {}'.format(self, arguments))


class Sequence(Combinator):

    def __call__(self, arguments):
        matches = []
        for item in self.items:
            match, arguments = item(arguments)
            if isinstance(match, list):
                matches += match
            else:
                matches.append(match)
        return matches, arguments


class Group(Combinator):

    def __init__(self, contents=None):
        super().__init__()
        self.contents = contents

    def __call__(self, arguments):
        matches = []
        for item in self.items:
            match, arguments = item(arguments)
            if isinstance(match, list):
                matches += match
            else:
                matches.append(match)
        return self.__class__(matches), arguments

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, key):
        return self.contents[key]

    def __str__(self):
        if self.contents is not None:
            return '{}: {}'.format(self.__class__.__name__, self.contents)
        else:
            return '{}: {} :: <Unmatched>'.format(self.__class__.__name__, self.items)

# Modifiers


class Optional(Modifier):

    def __call__(self, arguments):
        try:
            return self.item(arguments)
        except Exception:
            return None, arguments


class Multiple(Modifier):

    def __call__(self, arguments):
        matches = []
        try:
            while True:
                match, arguments = self.item(arguments)
                if isinstance(match, list):
                    matches += match
                else:
                    matches.append(match)
        except Exception:
            return matches, arguments


class Forgetable(Modifier):

    def __call__(self, arguments):
        return None, self.item(arguments)[1]
