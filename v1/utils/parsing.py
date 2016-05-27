import re

from abc import ABCMeta, abstractmethod
from utils.helpers import tail

# TODO: Take care about reuse of items - later uses currently can override previous ones


class Item(metaclass=ABCMeta):
    """A base class for all Items out of which a grammar is constructed

    Call method expects a list of arguments, and upon successful parsing
    should return ( Item, remains ), but if it fails, raise a SyntaxError"""
    @abstractmethod
    def __call__(self, arg_list):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


class Token(Item, metaclass=ABCMeta):
    """A terminating symbol of a grammar"""

    def __init__(self):
        self.content = None

    def __call__(self, arg_list):
        if not arg_list:
            raise SyntaxError('{}: nothing to parse'.format(self.__class__.__name__))
        if self.matches(arg_list[0]):
            self.content = arg_list[0]
            return self, tail(arg_list)
        else:
            raise SyntaxError('{} is not a {}'.format(arg_list[0], self.__class__.__name__))

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.content)

    @abstractmethod
    def matches(self, word):
        pass


class RToken(Token):
    """A token defined by a given regex"""

    def __init__(self, regex=''):
        self.regex = re.compile(regex)
        self.content = ''

    def matches(self, word):
        return re.fullmatch(self.regex, word) is not None


class Word(RToken):
    """A single word token"""

    def __init__(self, word):
        super().__init__(re.escape(word))


class Symbol(Word):
    """A single symbol token"""
    pass


class Combinator(Item):
    """A combination of tokens"""

    def __init__(self, *args):
        self.items = args
        self.content = ''

    def __str__(self):
        return '{}: [{}]'.format(self.__class__.__name__, ', '.join([str(i) for i in self.items]))


class Or(Combinator):
    """OR combinator, attempts to match any of a given list of Items to the input"""

    def __call__(self, arg_list):
        for item in self.items:
            try:
                return item(arg_list)
            except Exception:
                pass
        raise SyntaxError('{} is not a {}'.format(arg_list[0], str(self)))


class Sequence(Combinator):
    """List combinator, attempts to match a sequence of given items"""

    def __call__(self, arg_list):
        returns = []
        for item in self.items:
            ret, arg_list = item(arg_list)
            if isinstance(ret, list):
                returns += ret
            else:
                returns.append(ret)
        return returns, arg_list


class PSequence(Combinator):
    """Same as Sequence above, only stores matched elements into itself"""

    def __call__(self, arg_list):
        returns = []
        for item in self.items:
            ret, arg_list = item(arg_list)
            if isinstance(ret, list):
                returns += ret
            else:
                returns.append(ret)
        self.content = returns
        return self, arg_list

    def purge(self):
        self.content = [i for i in self.content if i]
        return self

    def __str__(self):
        return '{}: [{}]'.format(self.__class__.__name__, ', '.join([str(i) for i in self.content]))


class Modifier(Item):
    """A modifier of a basic item"""

    def __init__(self, item):
        self.item = item

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.item)


class Possible(Modifier):
    """Attempts to match an item, but failure to do so is not fatal (no exception,
    returns ( None, arg_list ) )"""

    def __call__(self, arg_list):
        try:
            return self.item(arg_list)
        except Exception:
            return (None, arg_list)


class Repeatable(Modifier):
    """Match as many instances of item in a row as possible; cannot fail"""

    def __call__(self, arg_list):
        returns = []
        while True:
            try:
                ret, arg_list = self.item(arg_list)
                if isinstance(ret, list):
                    returns += ret
                else:
                    returns.append(ret)
            except Exception as e:
                break
        return returns, arg_list
