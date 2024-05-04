from enum import Enum


class Addressing(str, Enum):
    DIR = "direct"
    MEM = "mem"


class Opcode(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"

    LD = "ld"
    ST = "st"

    HLT = "hlt"

    JMP = "jmp"
    JNZ = "jnz"
    JZ = "jz"
    JAZ = "jaz"

    def __str__(self):
        return str(self.value)


class Instruction:

    def __init__(self, address: int, opcode: Opcode, operand, addressing: Addressing):
        self.address = address
        self.opcode = opcode
        self.operand = operand
        self.addressing = addressing
