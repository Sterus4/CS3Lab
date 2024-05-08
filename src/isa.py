import json
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

    STUB = "stub"

    def __str__(self):
        return str(self.value)


class Instruction:

    def __init__(self, address: int, opcode: Opcode, operand = None, addressing = None):
        self.address = address
        self.opcode = opcode
        self.operand = operand
        self.addressing = addressing


def write_code(file: str, instructions: list[Instruction]):
    with open(file, "w", encoding="utf-8") as f:
        buf = []
        for instruction in instructions:
            buf.append(json.dumps({"address": instruction.address, "opcode": instruction.opcode, "operand": instruction.operand, "addressing": instruction.addressing}))
        f.write("[" + ",\n".join(buf) + "]")
