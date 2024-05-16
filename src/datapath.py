from enum import Enum

from src.exceptions import AluException
from src.isa import Instruction


class Register:
    def __init__(self, init_value):
        self.value = init_value

    def latch(self, value):
        self.value = value

    def get_value(self):
        return self.value


class Flag(str, Enum):
    NF = "negative flag"
    ZF = "positive flag"


class Alu:
    left: int
    right: int
    result: int
    def __init__(self):
        self.left = 0
        self.right = 0
        self.result = 0

    def latch_left(self, value):
        self.left = int(value)

    def latch_right(self, value):
        self.right = int(value)

    def add(self):
        self.result = self.right + self.left

    def subtract(self):
        self.result = self.left - self.right

    def divide(self):
        if self.right == 0: raise AluException("Деление на ноль - runtime error")
        self.result = int(self.left / self.right)

    def multiply(self):
        self.result = self.left * self.right

    def inc(self):
        self.result = self.left + 1

    def remainder_of_division(self):
        self.result = self.left % self.right

    def get_result(self):
        return self.result


class DataMemory:
    memory: list[int]
    address_in: int
    data_out: int

    def __init__(self, data_size: int, init_value: int):
        self.memory = [init_value] * data_size
        self.address_in = 0

    def latch_read(self):
        self.data_out = self.memory[self.address_in]

    def latch_in(self, address: int):
        self.address_in = address

    def latch_write(self, value: int):
        self.memory[self.address_in] = value

    def get_data_out(self):
        return self.data_out


class InstructionMemory:
    memory: list[Instruction]
    address_in: int
    instruction_out: Instruction

    def __init__(self, instructions: list[Instruction]):
        self.address_in = 0
        self.memory = instructions

    def latch_in(self, address: int):
        self.address_in = address

    def latch_read_instruction(self):
        self.instruction_out = self.memory[self.address_in]

    def get_instruction(self) -> Instruction:
        return self.instruction_out


class Datapath:
    flags: dict[Flag, bool]

    data_memory: DataMemory
    instruction_memory: InstructionMemory

    acc: Register
    ip_register: Register
    command_register: Register
    data_register: Register
    sp_register: Register

    alu: Alu

    def __init__(self, acc_value: int, ip_value: int, data_size: int, instructions: list[Instruction]):
        self.acc = Register(acc_value)
        self.ip_register = Register(ip_value)
        self.command_register = Register(0)
        self.data_register = Register(0)
        self.sp_register = Register(data_size)

        self.data_memory = DataMemory(data_size, 0)
        self.instruction_memory = InstructionMemory(instructions)

        self.flags = {Flag.NF: False, Flag.ZF: False}

        self.alu = Alu()

    def latch_flags(self):
        self.flags[Flag.NF] = self.alu.result < 0
        self.flags[Flag.ZF] = self.alu.result == 0