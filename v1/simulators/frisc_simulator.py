from simulators.simulator import *
from utils.binary import *
from utils.helpers import match_binary_mask


class FRISCSimulator(Simulator):
    """FRISC processor simulator, extending abstract class Simulator

    IO units are not supported yet."""

    def __init__(self, memory_size):
        self.config['MEMORY_SIZE_BYTES'] = memory_size
        self.config['MEMORY_SIZE_WORDS'] = memory_size // self.config['WORD_SIZE_BYTES']

        self.init()

    # State procedures

    def init(self):
        self.memory = [Binary8(0)] * self.config['MEMORY_SIZE_BYTES']
        self.annotations = [''] * self.config['MEMORY_SIZE_BYTES']
        self.registers = {name: Binary32(0) for name in ['PC', 'SR', 'R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']}
        self.flags = {'IIF': True}

        self.state = SimulatorState.INITIALIZED

    # Execution procedures

    def execute_single(self):
        instruction = self.get_word_from_memory(self.registers['PC'])
        self.registers['PC'] += 4

        self.execute_instruction(instruction)

    def execute_instruction(self, instruction):
        opcode = ''.join(instruction[0:5])
        funct = instruction[5]

        destination_register = self._register(''.join(instruction[6:9]))
        source1_register = self._register(''.join(instruction[9:12]))
        source2_register = self._register(''.join(instruction[12:15]))

        immediate = Binary32.from_digits(instruction[12:], True)

        operand1 = self.registers[source1_register]
        operand2 = self.registers[source2_register] if funct == '0' else immediate

        condition = ''.join(instruction[6:10])
        return_type = ''.join(instruction[30:])

        if opcode == '00000':
            if source1_register != 'R0':
                if instruction[10] == '1':
                    destination_register = 'SR'
                if instruction[13] == '1':
                    operand2 = self.registers['SR']

            self.registers[destination_register] = operand2

        elif opcode[0] == '0':
            try:
                result = self._alu_operations[opcode](operand1, operand2, self._get_carry())
                if opcode != '01101':
                    self.registers[destination_register] = result   # If CMP command, don't save changes
                self.set_status_flags(result.get_flags())
            except KeyError:
                raise ValueError('Unknown ALU operation')

        elif opcode[:2] == '10':
            address = immediate if funct == '0' else operand1 + immediate

            if opcode == '10000':
                self.registers[destination_register] = self.pop_from_stack()
            elif opcode == '10001':
                self.push_to_stack(self.registers[destination_register])
            elif opcode == '10010':
                self.registers[destination_register] = self.get_byte_from_memory(address)
            elif opcode == '10011':
                self.set_byte_in_memory(address, self.registers[destination_register][24:])
            elif opcode == '10100':
                self.registers[destination_register] = self.get_halfword_from_memory(self._round_to_halfword(address))
            elif opcode == '10101':
                self.set_halfword_in_memory(self._round_to_halfword(address), self.registers[destination_register][16:])
            elif opcode == '10110':
                self.registers[destination_register] = self.get_word_from_memory(self._round_to_word(address))
            elif opcode == '10111':
                self.set_word_in_memory(self._round_to_word(address), self.registers[destination_register])
            else:
                raise ValueError('Unknown memory operation, cannot execute')

        elif opcode[:2] == '11' and self._conditions[condition](self.get_status_flags()):

            if opcode == '11000':
                self.registers['PC'] = operand2
            elif opcode == '11001':
                self.push_on_stack(self.registers['PC'])
                self.registers['PC'] = operand2
            elif opcode == '11010':
                self.registers['PC'] += immediate
            elif opcode == '11011':
                self.registers['PC'] = self.pop_from_stack()
                if return_type == '01':
                    self.registers['SR'][27] = '1'
                elif return_type == '11':
                    self.flags['IIF'] = True
            elif opcode == '11111':
                self.state = SimulatorState.TERMINATED

        else:
            raise ValueError('Unknown instruction, cannot execute')

    def set_status_flags(self, flags):
        self.registers['SR'][28:] = flags

    def get_status_flags(self):
        return list(reversed(self.registers['SR'][28:]))

    # Memory methods

    def push_on_stack(self, word):
        self.registers['R7'] -= 4
        self.set_word_in_memory(self.registers['R7'], word)

    def pop_from_stack(self):
        word = self.get_word_from_memory(self.registers['R7'])
        self.registers['R7'] += 4
        return word

    # Auxilliary functions and data

    _alu_operations = {
        '00001': lambda x, y, c: x | y,
        '00010': lambda x, y, c: x & y,
        '00011': lambda x, y, c: x ^ y,
        '00100': lambda x, y, c: x + y,
        '00101': lambda x, y, c: x.adc(y, c),
        '00110': lambda x, y, c: x - y,
        '00111': lambda x, y, c: x.sbc(y, c),
        '01000': lambda x, y, c: x.rotl(y),
        '01001': lambda x, y, c: x.rotr(y),
        '01010': lambda x, y, c: x << y,
        '01011': lambda x, y, c: x >> y,
        '01100': lambda x, y, c: x.ashr(y),
        '01101': lambda x, y, c: x - y
    }

    _conditions = {                         # ncvz
        '0000': lambda fs: match_binary_mask('xxxx', fs),
        '0010': lambda fs: match_binary_mask('0xxx', fs),
        '0110': lambda fs: match_binary_mask('xx0x', fs),
        '0100': lambda fs: match_binary_mask('x0xx', fs),
        '1000': lambda fs: match_binary_mask('xxx0', fs),
        '0001': lambda fs: match_binary_mask('1xxx', fs),
        '0011': lambda fs: match_binary_mask('x1xx', fs),
        '0101': lambda fs: match_binary_mask('xx1x', fs),
        '0111': lambda fs: match_binary_mask('xxx1', fs),
        '1001': lambda fs: match_binary_mask('x0xx', fs) or match_binary_mask('xxx1', fs),
        '1010': lambda fs: match_binary_mask('x1x0', fs),
        '1011': lambda fs: match_binary_mask('1x0x', fs) or match_binary_mask('0x1x', fs),
        '1100': lambda fs: match_binary_mask('1x0x', fs) or match_binary_mask('0x1x', fs) or match_binary_mask('xxx1', fs),
        '1101': lambda fs: match_binary_mask('0x0x', fs) or match_binary_mask('1x1x', fs),
        '1110': lambda fs: match_binary_mask('0x00', fs) or match_binary_mask('1x10', fs)
    }

    def _register(self, reg_code):
        return 'R{}'.format(int(reg_code, 2))

    def _get_carry(self):
        return self.registers['SR'][30]

    def _round_to_halfword(self, address):
        address[-1] = '0'
        return address

    def _round_to_word(self, address):
        address[-1] = address[-2] = '0'
        return address
