# from itertools import chain
from utils.binary import *
from utils.peg import *


class Integer(Token):
    base = 0

    def __int__(self):
        return int(self.contents, self.base)

    def encode(self, constants=None, line_number=None, **kwargs):
        return str(BinaryNumber(int(self), 20))


class Binary(Integer):
    base = 2
    pattern = '(\+|-)?[0-1]+'


class Octal(Integer):
    base = 8
    pattern = '(\+|-)?[0-7]+'


class Decimal(Integer):
    base = 10
    pattern = '(\+|-)?[0-9]+'


class Hexadecimal(Integer):
    base = 16
    pattern = '(\+|-)?[0-9][0-9A-F]*'


class BinaryGroup(Sequence):
    items = Forgetable(Token(pattern='%B')), Binary()


class OctalGroup(Sequence):
    items = Forgetable(Token(pattern='%O')), Octal()


class DecimalGroup(Sequence):
    items = Forgetable(Token(pattern='%D')), Decimal()


class HexadecimalGroup(Sequence):
    items = Optional(Forgetable(Token(pattern='%H'))), Hexadecimal()


class Numeric(Or):
    items = BinaryGroup(), OctalGroup(), DecimalGroup(), HexadecimalGroup()


class Sign(Token):
    pattern = '\+|-'


class Comma(Token):
    pattern = ','


class Underscore(Token):
    pattern = '_'


class LParens(Token):
    pattern = '\('


class RParens(Token):
    pattern = '\)'


class Label(Token):
    pattern = '[A-Za-z_][A-Za-z0-9_]*'

    def encode(self, constants=None, line_number=None, **kwargs):
        b = BinaryNumber(constants[self.contents], 32)
        if len(list(filter(lambda x: x != b[0], b[1:12]))) != 0:
            raise ValueError('Constant cannot fit into 20 bits immediate.')
        return ''.join(b[12:])


class Constant(Or):
    items = Label(), Numeric()


class GeneralRegister(Token):
    pattern = 'R[0-7]|SP'

    def encode(self, constants=None, line_number=None, **kwargs):
        return '111' if self.contents == 'SP' else '{:0>3b}'.format(int(self.contents[1]))


class StatusRegister(Token):
    pattern = 'SR'

    def encode(self, constants=None, line_number=None, **kwargs):
        return '000'


class Register(Or):
    items = GeneralRegister(), StatusRegister()


class Condition(Token):
    pattern = 'C|NC|Z|NZ|V|NV|N|NN|M|P|EQ|NE|UGT|UGE|ULE|ULT|SGT|SGE|SLE|SLT'

    def encode(self, constants=None, line_number=None, **kwargs):
        return self._codes[self.contents]

    _codes = {
        'C': '0011', 'NC': '0100', 'Z': '0111',
        'NZ': '1000', 'V': '0101', 'NV': '0110',
        'N': '0001', 'NN': '0010', 'M': '0001',
        'P': '0010', 'EQ': '0111', 'NE': '1000',
        'UGT': '1010', 'UGE': '0100', 'ULE': '1001',
        'ULT': '0011', 'SGT': '1110', 'SGE': '1101',
        'SLE': '1100', 'SLT': '1011'
    }


class ALInstrName(Token):
    pattern = 'ADD|ADC|SUB|SBC|AND|OR|XOR|SHL|SHR|ASHR|ROTL|ROTR|CMP'


class MemInstrName(Token):
    pattern = 'LOAD(B|H)?|STORE(B|H)?'


class RetInstrName(Token):
    pattern = 'HALT|RET(I|N)?'


class StackInstrName(Token):
    pattern = 'PUSH|POP'


class JumpInstrName(Token):
    pattern = 'JP|CALL'


class DataPseudoInstrName(Token):
    pattern = 'D(B|H|W)'


class Instruction(Group):

    def purge(self):
        self.contents = [i for i in self.contents if i]
        return self

    def encode(self, constants=None, line_number=None, **kwargs):
        return None


class ALInstr(Instruction):
    items = ALInstrName(), GeneralRegister(), Comma(), Or(GeneralRegister(), Constant()), Optional(Sequence(Comma(), GeneralRegister()))

    def encode(self, constants=None, line_number=None, **kwargs):
        return [self._opcodes[self[0].contents] +
                ('1' if isinstance(self[3], Integer) else '0') +
                (self[5].encode() if len(self) == 6 else '000') +
                self[1].encode() +
                self[3].encode() + ('0' * 17 if isinstance(self[3], GeneralRegister) else '')
                ]

    _opcodes = {
        'OR': '00001', 'AND': '00010', 'XOR': '00011',
        'ADD': '00100', 'ADC': '00101', 'SUB': '00110',
        'SBC': '00111', 'ROTL': '01000', 'ROTR': '01001',
        'SHL': '01010', 'SHR': '01011', 'ASHR': '01100',
        'CMP': '01101'
    }


class MemInstr(Instruction):
    items = (MemInstrName(), GeneralRegister(), Comma(), LParens(), Or(Sequence(GeneralRegister(), Sign(), Numeric()),
             GeneralRegister(), Constant()), RParens())

    def encode(self, constants=None, line_number=None, **kwargs):
        return [self._opcodes[self[0].contents] +
                ('1' if isinstance(self[4], Integer) else '0') +
                self[1].encode() +
                (self[4].encode() if isinstance(self[4], GeneralRegister) else '000') +
                (self[6].encode() if len(self) > 6 else self[4].encode(constants))
                ]

    _opcodes = {
        'LOADB': '10010', 'STOREB': '10011', 'LOADH': '10100',
        'STOREH': '10101', 'LOAD': '10110', 'STORE': '10111'
    }


class StackInstr(Instruction):
    items = StackInstrName(), GeneralRegister()

    def encode(self, constants=None, line_number=None, **kwargs):
        return [self._opcodes[self[0].content] +
                '0' +
                self[1].encode() +
                '0' * 23
                ]

    _opcodes = {'PUSH': '10001', 'POP': '10000'}


class MoveInstr(Instruction):
    items = Token(pattern='MOVE'), Or(Register(), Constant()), Comma(), Register()

    def encode(self, constants=None, line_number=None, **kwargs):
        return ['00000' +
                ('1' if isinstance(self[1], Integer) else '0') +
                self[3].encode() +
                '0' +
                ('1' if isinstance(self[1], StatusRegister) else '0') +
                ('1' if isinstance(self[3], StatusRegister) else '0') +
                self[1].encode(constants=constants) +
                ('' if isinstance(self[1], Integer) or isinstance(self[1], Label) else ('0' * 17))
                ]


class JumpInstr(Instruction):
    items = JumpInstrName(), Optional(Sequence(Underscore(), Condition())), Or(Constant(), Sequence(LParens(), GeneralRegister(), RParens()))

    def encode(self, constants=None, line_number=None, **kwargs):
        has_condition = Constant in [type(x) for x in self.contents]
        i = 3 if has_condition else 1
        address = self[i + 1] if isinstance(self[i], LParens) else self[i]
        return [self._opcodes[self[0].contents] +
                ('1' if not isinstance(address, GeneralRegister) else '0') +
                (self[2].encode() if has_condition else '0000') +
                '00' +
                address.encode(constants) +
                ('0' * 17 if isinstance(address, GeneralRegister) else '')
                ]

    _opcodes = {'JP': '11000', 'CALL': '11001'}


class JRInstr(Instruction):
    items = Token(pattern='JR'), Optional(Sequence(Underscore(), Condition())), Constant()

    def encode(self, constants=None, line_number=None, **kwargs):
        has_condition = Constant in [type(x) for x in self.contents]
        i = 3 if has_condition else 1
        address = self[i].encode() - (line_number + 4 if isinstance(self[i], Label) else 0)
        return ['11000' +
                '1' +
                (self[2].encode() if has_condition else '0000') +
                '00' +
                str(BinaryNumber(address, 20))
                ]


class RetInstr(Instruction):
    items = RetInstrName(), Optional(Sequence(Underscore(), Condition()))

    def encode(self, constants=None, line_number=None, **kwargs):
        return [self._opcodes[self[0].contents] +
                '0' +
                (self.content[2].encode() if len(self) > 1 else '0000') +
                '0' * 20 +
                self._types[self[0].contents]
                ]

    _opcodes = {'RET': '11011', 'RETI': '11011', 'RETN': '11011', 'HALT': '11111'}
    _types = {'RET': '00', 'RETI': '01', 'RETN': '11', 'HALT': '00'}


class OrgPseudoInstr(Instruction):
    items = Token(pattern='ORG'), Numeric()


class EquPseudoInstr(Instruction):
    items = Token(pattern='EQU'), Numeric()


class SpacePseudoInstr(Instruction):
    items = Token(pattern='DS'), Numeric()


class DataPseudoInstr(Instruction):
    items = DataPseudoInstrName(), Numeric(), Multiple(Sequence(Comma(), Numeric()))

    def encode(self, constants=None, line_number=None, **kwargs):
        values = ''.join([str(BinaryNumber(int(x), self._data_size[self[0].contents]))
                          for x in reversed(self[1:]) if isinstance(x, Integer)])
        values = '0' * ((32 - len(values) % 32) % 32) + values
        return [values[32 * i: 32 * (i + 1)] for i in range(len(values) // 32 - 1, -1, -1)]

    _data_size = {'DW': 32, 'DH': 16, 'DB': 8}


class FRISCInstr(Or):
    items = ALInstr(), MemInstr(), MoveInstr(), StackInstr(), JumpInstr(), JRInstr(), RetInstr(), OrgPseudoInstr(), EquPseudoInstr(), SpacePseudoInstr(), DataPseudoInstr()


def parse_instruction(arguments):
    parsed = FRISCInstr()(arguments)
    if parsed[1]:
        raise SyntaxError('Extra tokens at the end of instruction')
    return parsed[0].purge()


def split_on_tokens(line):
    tokens = [x for x in re.split('\s|(,)|(\()|(\))|(?<!\s)(\+)|(?<!\s)(\-)', line) if x]
    return re.split('(_)', tokens[0], maxsplit=1) + tail(tokens) if len(tokens) > 0 else []


def get_int_from_tokens(tokens):
    if isinstance(tokens[0], Integer):
        value = int(tokens[0])
    elif isinstance(tokens[1], Integer):
        value = int(tokens[1])
    else:
        raise TypeError('Cannot return an integer, wrong type of token')
    return value


def get_data_size(instruction):
    # TODO: Rewrite
    instr_name = instruction[0].contents

    if instr_name == 'DW':
        value = 4
    elif instr_name == 'DH':
        value = 2
    elif instr_name == 'DB':
        value = 1
    else:
        raise ValueError('Unknown data instruction')
    return value


def get_data_length(instruction):
    return len([1 for t in instruction.contents if isinstance(t, Integer)])
