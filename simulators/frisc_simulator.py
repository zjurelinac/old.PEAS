from simulators.simulator import *
from utils.binary import *

class FRISCSimulator( Simulator ):
    """FRISC processor simulator, extending abstract class Simulator

    """

    def __init__( self, memory_size ):
        self.config[ 'MEMORY_SIZE_BYTES' ] = memory_size
        self.config[ 'MEMORY_SIZE_WORDS' ] = memory_size // self.config[ 'WORD_SIZE_BYTES' ]

        self.init()

    # State procedures

    def init( self ):
        self.memory = [ Binary8( 0 ) ] * self.config[ 'MEMORY_SIZE_BYTES' ]
        self.annotations = [ '' ] * self.config[ 'MEMORY_SIZE_BYTES' ]
        self.registers = { name : Binary32( 0 ) for name in [ 'PC', 'SR', 'R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7' ] }

        self.state = SimulatorState.INITIALIZED

    def run( self ):
        pass

    def run_step( self ):
        pass

    def pause( self ):
        pass

    def stop( self ):
        pass

    # Execution procedures

    def execute_single( self ):
        instruction = self.get_word_from_memory( self.registers[ 'PC' ] )
        self.registers[ 'PC' ] += 4

        self.execute_instruction( instruction )

    def execute_instruction( self, instruction ):
        opcode = ''.join( instruction[ 0:5 ] )
        funct = instruction[ 5 ]

        destination_register = self._register( ''.join( instruction[ 6:9 ] ) )
        source1_register = self._register( ''.join( instruction[ 9:12 ] ) )
        source2_register = self._register( ''.join( instruction[ 12:15 ] ) )

        immediate = Binary32.from_digits( instruction[ 12: ], True )

        condition = instruction[ 6:10 ]
        return_type = ''.join( instruction[ 30: ] )

        if opcode == '00000':
            if source1_register == 'R0':
                value = immediate if funct == '1' else self.registers[ source2_register ]

        elif opcode[ 0 ] == '0':
            operand1 = self.registers[ source1_register ]
            operand2 = self.registers[ source2_register ] if funct == '0' else immediate

            result = self._alu_operations[ opcode ]( operand1, operand2 )
            if opcode != '01101': self.registers[ destination_register ] = result   # If CMP command, don't save changes
            self.set_status_flags( result.get_flags() )

        elif opcode[ :2 ] == '10':



    def set_status_flags( self, flags ):
        self.registers[ 'SR' ][ 28: ] = flags

    # Memory methods
    # None yet


    _alu_operations = {
        '00001'     : lambda x, y: x | y,
        '00010'     : lambda x, y: x & y,
        '00011'     : lambda x, y: x ^ y,
        '00100'     : lambda x, y: x + y,
        '00101'     : lambda x, y, c: x.adc( y, c ),
        '00110'     : lambda x, y: x - y,
        '00111'     : lambda x, y, c: x.sbc( y, c ),
        '01000'     : lambda x, y: x.rotl( y ),
        '01001'     : lambda x, y: x.rotr( y ),
        '01010'     : lambda x, y: x << y,
        '01011'     : lambda x, y: x >> y,
        '01100'     : lambda x, y: x.ashr( y ),
        '01101'     : lambda x, y: x - y
    }

    _conditions = {                                  #ncvz
        '0000'      : lambda fs : match_binary_mask( 'xxxx', fs ),
        '0010'      : lambda fs : match_binary_mask( '0xxx', fs ),
        '0110'      : lambda fs : match_binary_mask( 'xx0x', fs ),
        '0100'      : lambda fs : match_binary_mask( 'x0xx', fs ),
        '1000'      : lambda fs : match_binary_mask( 'xxx0', fs ),
        '0001'      : lambda fs : match_binary_mask( '1xxx', fs ),
        '0011'      : lambda fs : match_binary_mask( 'x1xx', fs ),
        '0101'      : lambda fs : match_binary_mask( 'xx1x', fs ),
        '0111'      : lambda fs : match_binary_mask( 'xxx1', fs ),
        '1001'      : lambda fs : match_binary_mask( 'x0xx', fs ) or match_binary_mask( 'xxx1', fs ),
        '1010'      : lambda fs : match_binary_mask( 'x1x0', fs ),
        '1011'      : lambda fs : match_binary_mask( '1x0x', fs ) or match_binary_mask( '0x1x', fs ),
        '1100'      : lambda fs : match_binary_mask( '1x0x', fs ) or match_binary_mask( '0x1x', fs ) or match_binary_mask( 'xxx1', fs ),
        '1101'      : lambda fs : match_binary_mask( '0x0x', fs ) or match_binary_mask( '1x1x', fs ),
        '1110'      : lambda fs : match_binary_mask( '0x00', fs ) or match_binary_mask( '1x10', fs )
    }

    def _register( reg_code ):
        return 'R{}'.format( int( reg_code, 2 ) )

    def _get_carry( self ):
        return self.registers[ 'SR' ][ 30 ]
