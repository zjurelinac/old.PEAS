from math import ceil, log

class BinaryNumber:
    """Binary number representation as a fixed width string, together with
    basic arithmetic operations on them.

    NOTICE: Highest value bit is on the left, position 0"""


    def __init__( self, int_value, width ):
        self.WIDTH = width
        self.digits = list( ( '{:0>' + str( width ) + 'b}' ).format( abs( int_value ) ) )
        self.flags = ()

        if int_value < 0: self.digits = (-self).digits


    # Conversions and display functions

    def __int__( self ):
        return -( int( str( ~self ), 2 ) + 1 ) if self.is_negative() else int( str( self ), 2 )

    def __index__( self ):
        """Indexing arrays by a binary number"""
        return int( self )

    @classmethod
    def from_digits( cls, digit_list ):
        number = cls( 0, len( digit_list ) )
        number.digits = digit_list
        return number

    @classmethod
    def extend( cls, x, width ):
        return cls( '0'*( width - len( str( x ) ) ) + str( x ), width )

    def to_binary_string( self ):
        return ''.join( self.digits )

    def to_hex_string( self ):
        return ( '{:0>' + str( self.WIDTH // 4 ) + 'X}' ).format( int( self ) )

    def to_pretty_hex_string( self ):
        xstring = self.to_hex_string()
        return ' '.join( [ xstring[ i : i+2 ] for i in range( 0, len( xstring ), 2 ) ] )

    def __str__( self ):
        return self.to_binary_string()

    def __repr__( self ):
        return str( self.__class__.__name__ ) + ': ' + str( self ) + ' = ' + str( int( self ) )

    # Arithmetic and logical operations

    def __invert__( self ):
        """One's complement of a given number"""
        new_digits = [ ( '0' if d == '1' else '1' ) for d in self.digits ]
        return self.__class__.from_digits( new_digits )

    def __neg__( self ):
        """Two's complement of a given number"""
        return self.__class__( 2 ** self.WIDTH - int( self ) ) if not self.is_zero() else self

    def __add__( self, x ):     # TODO: add with carry?
        if isinstance( x, BinaryNumber ):
            if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

            carries, sums = [ '0' ] * self.WIDTH, [ '0' ] * self.WIDTH
            for i in range( self.WIDTH-1, -1, -1 ):
                sums[ i ], carries[ i ] = BinaryNumber._add2( self[ i ], x[ i ], carries[ i+1 ] if i < self.WIDTH-1 else '0' )

            result = self.__class__.from_digits( sums )
            result.flags = carries[ 0 ], BinaryNumber._xor2( carries[ 0 ], carries[ 1 ] ), result.is_negative(), result.is_zero()

            return result

        elif isinstance( x, int ):
            return self + self.__class__( x )
        else: raise TypeError( 'One operand not a binary number' )

    def __sub__( self, x ):    # TODO: sub with carry?
        if isinstance( x, BinaryNumber ):
            if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

            carries, sums = [ '0' ] * self.WIDTH, [ '0' ] * self.WIDTH
            for i in range( self.WIDTH-1, -1, -1 ):
                sums[ i ], carries[ i ] = BinaryNumber._sub2( self[ i ], x[ i ], carries[ i+1 ] if i < self.WIDTH-1 else '0' )

            result = self.__class__.from_digits( sums )
            result.flags = carries[ 0 ], BinaryNumber._xor2( carries[ 0 ], carries[ 1 ] ), result.is_negative(), result.is_zero()

            return result

        elif isinstance( x, int ):
            return self - self.__class__( x )
        else: raise TypeError( 'One operand not a binary number' )

    def __and__( self, x ):
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        result = self.__class__.from_digits( [ '1' if self[ i ] == '1' and x[ i ] == '1' else '0' for i in range( 0, self.WIDTH ) ] )
        result.flags = '0', '0', result.is_negative(), result.is_zero()

        return result

    def __or__( self, x ):
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        result = self.__class__.from_digits( [ '1' if self[ i ] == '1' or x[ i ] == '1' else '0' for i in range( 0, self.WIDTH ) ] )
        result.flags = '0', '0', result.is_negative(), result.is_zero()

        return result

    def __xor__( self, x ):
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        result = self.__class__.from_digits( [ str( int( self[ i ] != x[ i ] ) ) for i in range( 0, self.WIDTH ) ] )
        result.flags = '0', '0', result.is_negative(), result.is_zero()

        return result

    def __lshift__( self, x ):
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        int_x = int( x )
        if int_x < 0: return self >> ( -x )

        result = self.__class__.from_digits( self[ int_x: ] + [ '0' ] * int_x if int_x < self.WIDTH else [ '0' ] * self.WIDTH )
        result.flags = x[ int_x - 1 ] if int_x > 0 and int_x <= self.WIDTH else '0', '0', result.is_negative(), result.is_zero()

        return result

    def __rshift__( self, x ):
        """Logical shift right"""
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        int_x = int( x )
        if int_x < 0: return self << ( -x )

        result = self.__class__.from_digits( [ '0' ] * int_x + x [ : -int_x ] if int_x < self.WIDTH else [ '0' ] * self.WIDTH )
        result.flags = x[ -int_x ] if int_x > 0 and int_x <= self.WIDTH else '0', '0', result.is_negative(), result.is_zero()

        return result

    def arshift( self, x ):
        """Arithmetic shift right"""
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        int_x = int( x )
        if int_x < 0: return self << ( -x )

        result = self.__class__.from_digits( [ self[ 0 ] ] * int_x + self[ : -int_x ] if int_x < self.WIDTH else [ self[ 0 ] ] * self.WIDTH )
        result.flags = x[ -int_x ] if int_x > 0 and int_x <= self.WIDTH else '0', '0', result.is_negative(), result.is_zero()

        return result

    def rotl( self, x ):
        """Right rotation"""
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        int_x = int( x ) % 32
        if int_x < 0: return self.rotr( -x )

        result = self.__class__.from_digits( self[ int_y : ] + self[ : int_y ] )
        result.flags = self[ int_x - 1 ], '0', self.is_negative(), self.is_zero()

        return result

    def rotr( self, x ):
        """Left rotation"""
        if not isinstance( x, BinaryNumber ): raise TypeError( 'One operand not a binary number' )
        if len( self ) != len( x ): raise TypeError( 'Incompatible binary numbers - different lengths' )

        int_x = int( x ) % 32
        if int_x < 0: return self.rotl( x )

        result = self.__class__.from_digits( self[ -int_x : ] + self[ : -int_x ] )
        result.flags = self[ -int_x ], '0', self.is_negative(), self.is_zero()

        return result

    def adc( self, x, c ):
        pass

    def sbc( self, x, c ):
        pass

    # List operators

    def __len__( self ):
        return self.WIDTH

    def __getitem__( self, key ):
        return self.digits[ key ]

    def __setitem__( self, key, value ):
        self.digits[ key ] = value

    def __floordiv__( self, x ):
        """Define // operator to concatenate two binary numbers into a larger one"""
        return BinaryNumber.from_digits( self.digits + x.digits )

    # Flag tests and operations

    def clear_flags( self ):
        self.flags = ()

    def is_zero( self ):
        return len( list( filter( lambda x: x == '1', self.digits ) ) ) == 0

    def is_negative( self ):
        return self.digits[ 0 ] == '1'

    # Private helper functions

    @staticmethod
    def _add2( a, b, c ):
        z = int( a, 2 ) + int( b, 2 ) + int( c, 2 )
        return str( z % 2 ), str( z // 2 )

    @staticmethod
    def _sub2( a, b, c ):
        z = int( a, 2 ) - int( b, 2 ) - int( c, 2 )
        return ( str( z ), '0' ) if z >= 0 else ( '1' if z == -1 else '0', '1' )

    @staticmethod
    def _xor2( a, b ):
        return str( int( a != b ) )


class Binary8( BinaryNumber ):
    """8-bit binary number representation"""

    def __init__( self, int_value ):
        super().__init__( int_value, 8 )

    @classmethod
    def from_digits( cls, digit_list ):
        if len( digit_list ) > 8:
            raise ValueError( 'Too many digits given, cannot fit into 16 bits.' )

        number = cls( 0 )
        number.digits = [ '0' ] * ( 8 - len( digit_list ) ) + digit_list
        return number

    @classmethod
    def __instancecheck__( self, other ):
        return other.width == 8 if isinstance( other, BinaryNumber ) else False


class Binary16( BinaryNumber ):
    """16-bit binary number representation"""

    def __init__( self, int_value ):
        super().__init__( int_value, 16 )

    @classmethod
    def from_digits( cls, digit_list ):
        if len( digit_list ) > 16:
            raise ValueError( 'Too many digits given, cannot fit into 16 bits.' )

        number = cls( 0 )
        number.digits = [ '0' ] * ( 16 - len( digit_list ) ) + digit_list
        return number

    @classmethod
    def __instancecheck__( self, other ):
        return other.width == 16 if isinstance( other, BinaryNumber ) else False


class Binary32( BinaryNumber ):
    """32-bit binary number representation"""

    def __init__( self, int_value ):
        super().__init__( int_value, 32 )

    @classmethod
    def from_digits( cls, digit_list ):
        if len( digit_list ) > 32:
            raise ValueError( 'Too many digits given, cannot fit into 32 bits.' )
        number = cls( 0 )
        number.digits = [ '0' ] * ( 32 - len( digit_list ) ) + digit_list
        return number


    @classmethod
    def __instancecheck__( self, other ):
        return other.width == 32 if isinstance( other, BinaryNumber ) else False
