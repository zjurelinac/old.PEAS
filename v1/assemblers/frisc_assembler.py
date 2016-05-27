import os
import re
# import sys

from assemblers.assembler import Assembler
from utils.frisc_parsing import *


class FRISCAssembler(Assembler):
    """FRISC processor assembler, extending abstract class Assembler"""

    @classmethod
    def assemble(cls, file_name):
        """Assembles a file into FRISC processor machine code

        Takes a file path, creates .p and .e files containing machine code, and
        returns a (message, success) pair
        """
        constants = {}

        with open(file_name, 'r') as file:

            current_line_number = 0
            next_line_number = 0
            file_line_number = 1
            preprocessed_lines = []

            for line in file:
                preprocessed_line = {'original': line[:-1]}
                no_comments = line.upper().split(cls.config['LINE_COMMENT_START'], maxsplit=1)[0]

                if len(no_comments) > 0:
                    label, instruction_part = re.split('\s', no_comments, maxsplit=1) if not no_comments[0].isspace() else ['', no_comments]

                    tokens = split_on_tokens(instruction_part)

                    blank = len(tokens) == 0
                    pseudo = True
                    is_equ = False

                    if not blank:
                        try:
                            instruction = parse_instruction(tokens)
                        except SyntaxError:
                            print('Syntax error in line ' + str(file_line_number))
                            return None, False

                        parts = instruction.contents

                        preprocessed_line['instruction'] = instruction

                        if isinstance(instruction, OrgPseudoInstr):
                            next_line_number = get_int_from_tokens(parts[1:])

                        elif isinstance(instruction, EquPseudoInstr):
                            is_equ = True
                            constants[label] = get_int_from_tokens(parts[1:])

                        elif isinstance(instruction, SpacePseudoInstr):
                            next_line_number = current_line_number + FRISCAssembler._round_to_word(get_int_from_tokens(parts[1:]))

                        elif isinstance(instruction, DataPseudoInstr):
                            next_line_number = current_line_number + get_data_size(instruction) * get_data_length(instruction)
                            pseudo = False

                        else:
                            pseudo = False
                            next_line_number = current_line_number + 4

                    preprocessed_line['empty'] = blank or pseudo
                    preprocessed_line['line_number'] = current_line_number
                    preprocessed_line['label'] = label

                    if label and not is_equ:
                        constants[label] = current_line_number

                    current_line_number = next_line_number

                else:
                    preprocessed_line['empty'] = True
                    preprocessed_line['line_number'] = -1

                preprocessed_lines.append(preprocessed_line)
                file_line_number += 1

            file_path = os.path.abspath(file_name)
            base_name = file_path.rsplit('.', maxsplit=1)[0]

            with open(base_name + '.p', 'w') as pfile:
                for line in preprocessed_lines:

                    if not line['empty']:
                        line_number = Binary32(line['line_number']).to_hex_string()
                        try:
                            encoded = line['instruction'].encode(constants, line['line_number'])
                            machine_code = [cls._rearrange(Binary32.from_digits(list(enc)).to_pretty_hex_string()) for enc in encoded]
                        except Exception as e:
                            print(line)
                            print(constants)
                            raise e
                    else:
                        line_number = ''
                        encoded = ['']
                        machine_code = ['']

                    pfile.write(line_number.ljust(10) + machine_code[0].ljust(13) + line['original'] + '\n')

                    for mc in tail(machine_code):
                        pfile.write(mc.rjust(21) + '\n')

    def _rearrange(string):
        return ' '.join(reversed(string.split(' ')))

    def _round_to_word(number):
        return (number // 4 + 1) * 4 if number % 4 != 0 else number
