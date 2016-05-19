def get_breakpoint_symbol( b ):
    """Return a corresponding Unicode symbol for active (b = True) or inactive( b = False) breakpoint"""
    return '●' if b else '○'

def rev_str( s ):
    """Reverse the given string"""
    return ''.join( reversed( s ) )

def match_binary_mask( mask, binary_list ):
    """Test whether a binary_list matches the given mask"""
    if len( mask ) != len( binary_list ): raise ValueError( 'Arguments not of equal length, cannot attempt a match' )
    return all( [ mask[ i ] == binary_list[ i ] for i in range( 0, len( mask ) ) if mask[ i ] != 'x' ] )
