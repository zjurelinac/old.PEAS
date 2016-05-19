import re
import sys

from assemblers.assembler import Assembler
from utils.frisc_parsing import *

class FRISCAssembler( Assembler ):
    """FRISC processor assembler, extending abstract class Assembler"""

    @staticmethod
    def assemble( file_name ):
        """Assembles a file into FRISC processor machine code

        Takes a file path, creates .p and .e files containing machine code, and
        returns a (message, success) pair
        """
        constants = {}

        with open( file_name, 'r' ) as file:

            current_line_number = 0
            preprocessed_lines = []

            for line in file:
                preprocessed_line = { 'original' : line }
                no_comments = line.upper().split( FRISCAssembler.config[ 'LINE_COMMENT_START' ], maxsplit = 1 )[ 0 ]

                if len( no_comments ) > 0:
                    label, instruction_part = re.split( '\s', no_comments, maxsplit = 1 ) if not no_comments[ 0 ].isspace() else [ '', no_comments ]

                    tokens = split_on_tokens( instruction_part )

                    if len( tokens ) > 0:
                        instruction_parser = Instruction()
                        instruction = instruction_parser( tokens )

                        print( instruction )

                        if isinstance( instruction, OrgInstruction ):
                            pass#print( int( instruction.content[ 1 ] ) )
                        elif isinstance( instruction, DDInstruction ):
                            pass
                        elif isinstance( instruction, DSInstruction ):
                            pass
                        else:
                            pass

                    preprocessed_line[ 'empty' ] = len( instruction_part ) > 0
                    preprocessed_line[ 'label' ] = label
                    preprocessed_line[ 'line_number' ] = current_line_number

                    constants[ label ] = current_line_number
                    current_line_number += 4

                else:
                    preprocessed_line[ 'empty' ] = True
                    preprocessed_line[ 'line_number' ] = -1
