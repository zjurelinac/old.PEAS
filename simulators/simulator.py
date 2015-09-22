from abc import ABCMeta, abstractmethod
from enum import Enum

class SimulatorState( Enum ):
    UNINITIALIZED   = 0
    INITIALIZED     = 1
    LOADED          = 2
    RUNNING         = 3
    PAUSED          = 4
    TERMINATED      = 5


class Simulator( metaclass = ABCMeta ):
    """Abstract base class for a processor simulator implementation

    Besides a number of necessary methods, it must also contain a state variable,
    a memory array and a dictionary of named registers.

    Configuration object must contain all the properties listed below, modified
    to fit the processor wich is being simulated"""

    state = SimulatorState.UNINITIALIZED
    memory = []
    breakpoints = set()
    registers = {}

    config = {  # Default values, modify to model different processors
        'WORD_SIZE_BYTES'   : 4,
        'WORD_SIZE_BITS'    : 32,
        'MEMORY_SIZE_BYTES' : 4096,
        'MEMORY_SIZE_WORDS' : 1024
    }

    # Processor state procedures

    @abstractmethod
    def init( self ):
        pass

    @abstractmethod
    def load( self, program ):
        pass

    @abstractmethod
    def reset( self ):
        pass

    @abstractmethod
    def run( self ):
        pass

    @abstractmethod
    def run_step( self ):
        pass

    @abstractmethod
    def pause( self ):
        pass

    @abstractmethod
    def stop( self ):
        pass

    # Processor memory functions

    @abstractmethod
    def is_valid_address( self, address ):
        pass


    # Processor breakpoints functions

    def toggle_breakpoint( self, line_number ):
        if not self.is_valid_address( line_number ): raise ValueError( 'Invalid address for a breakpoint' )

        if line_number in self.breakpoints: self.breakpoints.remove( line_number )
        else: self.breakpoints.add( line_number )

    def is_breakpoint_at( self, line_number ):
        return line_number in self.breakpoints
