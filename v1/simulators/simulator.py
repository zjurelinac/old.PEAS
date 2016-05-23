from abc import ABCMeta, abstractmethod
from enum import Enum
from utils.binary import *


class SimulatorState(Enum):
    UNINITIALIZED = 0
    INITIALIZED = 1
    LOADED = 2
    RUNNING = 3
    PAUSED = 4
    TERMINATED = 5


class Simulator(metaclass=ABCMeta):
    """Abstract base class for a processor simulator implementation

    Besides a number of necessary methods, it must also contain a state variable,
    a memory array and a dictionary of named registers.

    Configuration object must contain all the properties listed below, modified
    to fit the processor wich is being simulated"""

    state = SimulatorState.UNINITIALIZED
    memory = []
    annotations = []
    breakpoints = set()
    registers = {}

    config = {  # Default values, modify to model different processors
        'ENDIANNESS': 'little',
        'WORD_SIZE_BYTES': 4,
        'WORD_SIZE_BITS': 32,
        'HALFWORD_SIZE_BYTES': 2,
        'HALFWORD_SIZE_BITS': 16,
        'ADDRESS_SIZE_BYTES': 4,
        'ADDRESS_SIZE_BITS': 32,
        'MEMORY_SIZE_BYTES': 65536,
        'MEMORY_SIZE_WORDS': 65536 // 4
    }

    # Processor state procedures

    @abstractmethod
    def init(self):
        pass

    # TODO:: Standardize .p file format
    def load(self, p_file_name):
        if self.state != SimulatorState.INITIALIZED:
            raise RuntimeError('Cannot load a program, processor in invalid state')

        with open(p_file_name, "r") as p_file:
            address_end_pos = 2 * self.config['ADDRESS_SIZE_BYTES']
            annotation_start_pos = address_end_pos + 3 * self.config['WORD_SIZE_BYTES'] + 1

            lines = [(line[:annotation_start_pos], line[annotation_start_pos:])
                     for line in p_file if line[:annotation_start_pos].rstrip()]

            last_line_number = 0
            for (code, annotation) in lines:
                current_line_number = (int(code[:address_end_pos], 16) if code[:address_end_pos].strip() else last_line_number + self.config['WORD_SIZE_BYTES'])

                self.annotations[current_line_number] = annotation

                if self.config['ENDIANNESS'] == 'little':
                    for i in range(0, self.config['WORD_SIZE_BYTES']):
                        self.memory[current_line_number + i] = Binary8.from_hex(code[address_end_pos + 2 + 3 * i: address_end_pos + 5 + 3 * i])
                else:
                    raise NotImplementedError('Big endian unsupported yet')

                last_line_number = current_line_number

            self.state = SimulatorState.LOADED

    def run(self):
        if self.state not in (SimulatorState.LOADED, SimulatorState.PAUSED):
            raise RuntimeError('Cannot run, processor in invalid state')

        self.state = SimulatorState.RUNNING
        while self.state == SimulatorState.RUNNING:
            self.execute_single()

    def run_step(self):
        if self.state not in (SimulatorState.LOADED, SimulatorState.PAUSED):
            raise RuntimeError('Cannot run a step, processor in invalid state')

        self.execute_single()

        if self.state != SimulatorState.TERMINATED:
            self.state = SimulatorState.PAUSED

    def pause(self):
        self.state = SimulatorState.PAUSED

    def stop(self):
        self.state = SimulatorState.TERMINATED

    # Execution procedures

    @abstractmethod
    def execute_single(self):
        pass

    @abstractmethod
    def execute_instruction(self, instruction):
        pass

    # Processor memory functions

    def is_valid_address(self, address):
        """Tests whether a given address is valid for a given processor

        Modify if neccessary for a specific processor, say if addressing in words,
        not bytes, or if address space is different"""
        return int(address) >= 0 and int(address) <= self.config['MEMORY_SIZE_BYTES']

    def get_word_from_memory(self, address):
        """Return a word from memory at a given address"""
        if not self.is_valid_address(address):
            raise ValueError('Invalid address provided, cannot load word from this memory location')

        if self.config['ENDIANNESS'] == 'little':
            word = self.memory[address]
            for i in range(1, self.config['WORD_SIZE_BYTES']):
                word = self.memory[address + i] // word
            return word
        else:
            raise NotImplementedError('Big endian not supported yet')

    def get_halfword_from_memory(self, address):
        """Return a halfword from memory at a given address"""
        if not self.is_valid_address(address):
            raise ValueError('Invalid address provided, cannot load byte from this memory location')

        if self.config['ENDIANNESS'] == 'little':
            word = self.memory[address]
            for i in range(1, self.config['HALFWORD_SIZE_BYTES']):
                word = self.memory[address + i] // word
            return word
        else:
            raise NotImplementedError('Big endian not supported yet')

    def get_byte_from_memory(self, address):
        """Return a byte from memory at a given address"""
        if not self.is_valid_address(address):
            raise ValueError('Invalid address provided, cannot load byte from this memory location')

        return self.memory[address]

    def set_word_in_memory(self, address, word):
        """Place a word into memory at a given address"""
        if not self.is_valid_address(address):
            raise ValueError('Invalid address provided, cannot store word to this memory location')

        if self.config['ENDIANNESS'] == 'little':
            for i in range(0, self.config['WORD_SIZE_BYTES']):
                self.memory[address + self.config['WORD_SIZE_BYTES'] - i - 1] = Binary8.from_digits(word[8 * i: 8 * (i + 1)])
        else:
            raise NotImplementedError('Big endian not supported yet')

    def set_halfword_in_memory(self, address, halfword):
        """Place a halfword into memory at a given address"""
        if not self.is_valid_address(address):
            raise ValueError('Invalid address provided, cannot store halfword to this memory location')

        if self.config['ENDIANNESS'] == 'little':
            for i in range(0, self.config['HALFWORD_SIZE_BYTES']):
                self.memory[address + self.config['HALFWORD_SIZE_BYTES'] - i - 1] = Binary8.from_digits(halfword[8 * i: 8 * (i + 1)])
        else:
            raise NotImplementedError('Big endian not supported yet')

    def set_byte_in_memory(self, address, byte):
        """Place a byte into memory at a given address"""
        if not self.is_valid_address(address):
            raise ValueError('Invalid address provided, cannot store byte from to memory location.')

        self.memory[address] = byte

    # Processor breakpoints functions

    def toggle_breakpoint(self, line_number):
        if not self.is_valid_address(line_number):
            raise ValueError('Invalid address for a breakpoint')

        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)

    def is_breakpoint_at(self, line_number):
        return line_number in self.breakpoints
