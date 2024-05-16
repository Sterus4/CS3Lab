import json
from enum import Enum



class Addressing(str, Enum):
    DIR = "direct"  # Прямая загрузка
    MEM = "mem"  # Прямая адресация
    SP = "sp"  # Адресация относительно стека (Смещение 0 или -1)
    IND_MEM = "ind_mem"  # Косвенная адресация


class Opcode(str, Enum):
    # Арифметика

    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"

    INC = "inc"

    # Память
    LD = "ld"
    ST = "st"

    PUSH = "push"
    POP = "pop"

    # Переходы
    JMP = "jmp"

    JNZ = "jnz"
    JZ = "jz"
    JBZ = "jbz"
    JB = "jb"
    JAZ = "jaz"
    JA = "ja"

    HLT = "hlt"

    STUB = "stub"

    def __str__(self):
        return str(self.value)


class Instruction:

    def __init__(self, address: int, opcode: Opcode, operand=None, addressing=None):
        self.address = address
        self.opcode = opcode
        self.operand = operand
        self.addressing = addressing

    def __str__(self):
        return "Address: " + str(self.address) + ", Opcode: " + str(self.opcode) + ", Operand: " + str(
            self.operand) + ", Addressing: " + str(self.addressing) + '.'


def create_instr(json_dict: dict) -> Instruction:
    return Instruction(int(json_dict["address"]), Opcode(json_dict["opcode"]), json_dict["operand"],
                       json_dict["addressing"])


def write_code(file: str, instructions: list[Instruction]):
    with open(file, "w", encoding="utf-8") as f:
        buf = []
        for instruction in instructions:
            buf.append(json.dumps(
                {"address": instruction.address, "opcode": instruction.opcode, "operand": instruction.operand,
                 "addressing": instruction.addressing}))
        f.write("[" + ",\n".join(buf) + "]")


def read_code(file: str) -> list[Instruction]:
    instructions = []
    with open(file, "r", encoding="utf-8") as f:
        json_file = json.loads(f.read())
    for i in json_file:
        instructions.append(create_instr(i))
    return instructions
