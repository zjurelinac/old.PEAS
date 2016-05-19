import re

from abc import ABCMeta, abstractmethod

class Item( metaclass = ABCMeta ):
    """Item base class, extend to define other items"""

    @abstractmethod
    def __call__( self, word ):
        pass

    def __str__( self ):
        return self.__class__.__name__

    def __repr__( self ):
        return str( self )


class RegexItem( Item ):
    """An Item that matches a given regex"""
    regex = ''

    def __init__( self ):
        self.regex = re.compile( self.regex )
        self.content = None

    def __call__( self, string ):
        if re.fullmatch( self.regex, string ) is not None:
            self.content = string
            return self
        else: raise SyntaxError( string + ' is not a ' + self.__class__.__name__ + ' item' )

    def __str__( self ):
        return self.__class__.__name__ + ': ' + self.content

class VariantsItem:
    """An Item that fits one of a given list of simpler Items"""
    variants = []

    def __call__( self, string ):
        for item in self.variants:
            try: return item( string )
            except Exception: pass
        raise SyntaxError( str( string ) + ' is not a ' + self.__class__.__name__ + ' item' )


class SequenceItem( Item ):
    """An Item that fits all Items in a given list in that order"""
    sequence = []

    def __call__( self, _list ):
        if len( self.sequence ) == len( _list ):
            self.content = []
            for i in range( 0, len( self.sequence ) ):
                self.content.append( self.sequence[ i ]( _list[ i ] ) )
            return self
        else: raise SyntaxError( str( _list ) + 'is not a ' + self.__class__.__name__ + ' item'  )

    def __str__( self ):
        return self.__class__.__name__ + ': ' + str( self.content )

class Hex( RegexItem ):     regex = '(\+|-)?[0-9][0-9A-F]*'
class Dec( RegexItem ):     regex = '(\+|-)?[0-9]+'
class Oct( RegexItem ):     regex = '(\+|-)?[0-7+]'
class Bin( RegexItem ):     regex = '(\+|-)?[0-1]+'

class Symbol( RegexItem ):
    def __init__( self, symbol ):
        self.regex = re.escape( symbol )
        super().__init__()

class Word( Symbol ):
    pass
