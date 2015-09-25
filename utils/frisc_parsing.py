"""FRISC Assembler source parsing functions module

Basic instruction format:
=======================================
|LABEL      CMD (arguments)   ; A comment

Grammar:
    REGISTER        <=  R[0-7] | SR | SP
    NUMERIC         <=  (%B|%O|%D|%H)? [0-9][0-9A-F]*
    LABEL           <=  [_A-Z][_0-9A-Z]*
    INSTR_NAME      <=  [A-Z][A-Z0-9]*
    CONDITION       <=  _[A-Z]*

    CONSTANT        <=  NUMERIC | LABEL

    ALU             <=  INSTR_NAME REGISTER, REGISTER, REGISTER
                     |  INSTR_NAME REGISTER, CONSTANT, REGISTER
    MEMORY          <=  INSTR_NAME REGISTER, (CONSTANT)
                     |  INSTR_NAME REGISTER, (REGISTER+CONSTANT)
                     |  INSTR_NAME REGISTER, (REGISTER-CONSTANT)
    MOVE            <=  INSTR_NAME REGISTER, REGISTER
                     |  INSTR_NAME CONSTANT, REGISTER
    STACK           <=  INSTR_NAME REGISTER

    JP              <=  INSTR_NAME CONSTANT
    JR              <=  INSTR_NAME
"""

from utils.parsing import *

class HexConst( RegexItem ):
    regex = '(%H\s*)?(\+|-)?[0-9][0-9A-F]*'

    def __int__( self ):
        return int( self.content, 16 )

class DecConst( RegexItem ):
    regex = '(%D\s*)?(\+|-)?[0-9]+'

    def __int__( self ):
        return int( self.content, 10 )

class OctConst( RegexItem ):
    regex = '(%O\s*)?(\+|-)?[0-7]+'

    def __int__( self ):
        return int( self.content, 8 )

class BinConst( RegexItem ):
    regex = '(%B\s*)?(\+|-)?[0-1]+'

    def __int__( self ):
        return int( self.content, 2 )

class Sign( VariantsItem ):         variants = [ Symbol( '+' ), Symbol( '-' ) ]

class Numeric( VariantsItem ):      variants = [ HexConst(), DecConst(), OctConst(), BinConst() ]
class Label( RegexItem ):           regex = '[_A-Z][_0-9A-Z]*'

class Constant( VariantsItem ):     variants = [ Numeric(), Label() ]

class GeneralRegister( RegexItem ): regex = 'R[0-7]|SP'
class StatusRegister( RegexItem ):  regex = 'SR'
class Register( VariantsItem ):     variants = [ GeneralRegister(), StatusRegister() ]

class InstructionName( RegexItem ): regex = '[A-Z][A-Z0-9]*'
class Condition( RegexItem ):       regex = 'C|NC|Z|NZ|V|NV|N|NN|EQ|NE|M|P|ULE|UGT|ULT|UGE|SLE|SLT|SGT|SGE'

class ALOperand2( VariantsItem ):   variants = [ GeneralRegister(), Constant() ]
class MoveOperand1( VariantsItem ): variants = [ Register(), Constant() ]

class DataDefinition( VariantsItem ):       variants = [ Word( 'DW' ), Word( 'DH' ), Word( 'DB' ) ]
class OrgInstruction( SequenceItem ):       sequence = [ Word( 'ORG' ), Constant() ]
class DDInstruction( SequenceItem ):        sequence = [ DataDefinition(), Constant() ]
class DSInstruction( SequenceItem ):        sequence = [ Word( 'DS' ), Constant() ]
# TODO: Make DD's variable length

class ALInstruction( SequenceItem ):        sequence = [ InstructionName(), GeneralRegister(), Symbol( ',' ), ALOperand2(), Symbol( ',' ), GeneralRegister() ]
class StackInstruction( SequenceItem ):     sequence = [ InstructionName(), GeneralRegister() ]
class MoveInstruction( SequenceItem ):      sequence = [ InstructionName(), MoveOperand1(), Symbol( ',' ), Register() ]
class MemoryInstruction1( SequenceItem ):   sequence = [ InstructionName(), GeneralRegister(), Symbol( ',' ), Symbol( '(' ), Constant(), Symbol( ')' ) ]
class MemoryInstruction2( SequenceItem ):   sequence = [ InstructionName(), GeneralRegister(), Symbol( ',' ), Symbol( '(' ), GeneralRegister(), Symbol( ')' ) ]
class MemoryInstruction3( SequenceItem ):   sequence = [ InstructionName(), GeneralRegister(), Symbol( ',' ), Symbol( '(' ), GeneralRegister(), Sign(), Constant(), Symbol( ')' ) ]
class ReturnInstruction1( SequenceItem ):   sequence = [ InstructionName(), Symbol( '_' ), Condition() ]
class ReturnInstruction2( SequenceItem ):   sequence = [ InstructionName() ]
class JumpInstruction1( SequenceItem ):     sequence = [ InstructionName(), Constant() ]
class JumpInstruction2( SequenceItem ):     sequence = [ InstructionName(), Symbol( '_' ), Condition(), Constant() ]
class JumpInstruction3( SequenceItem ):     sequence = [ InstructionName(), Symbol( '(' ), GeneralRegister(), Symbol( ')' ) ]
class JumpInstruction4( SequenceItem ):     sequence = [ InstructionName(), Symbol( '_' ), Condition(), Symbol( '(' ), GeneralRegister(), Symbol( ')' ) ]

class Instruction( VariantsItem ):
    variants = [ OrgInstruction(), DDInstruction(), DSInstruction(),
        ALInstruction(), StackInstruction(), MoveInstruction(),
        MemoryInstruction1(), MemoryInstruction2(), MemoryInstruction3(),
        ReturnInstruction1(), ReturnInstruction2(), JumpInstruction1(),
        JumpInstruction2(), JumpInstruction3(), JumpInstruction4() ]

def split_on_tokens( line ):
    return merge_tokens( [ x for x in re.split( '\s|(?<=JP)(_)|(?<=RET)(_)|(?<=CALL|RETI|RETN)(_)|(,)|(\()|(\))|(?<=-\()(\+)|(?<=-\()(\-)', line ) if x ] )

def merge_tokens( token_list ):
    new_list, store = [], ''
    for i in range( 0, len( token_list ) ):
        if token_list[ i ][ 0 ] == '%':
            store = token_list[ i ]
        elif store:
            new_list.append( store + ' ' + token_list[ i ] )
            store = ''
        else: new_list.append( token_list[ i ] )
    return new_list
