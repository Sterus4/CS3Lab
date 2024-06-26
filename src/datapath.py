from enum import Enum

from src.exceptions import AluException
from src.isa import Instruction, Opcode


class IODevice:
    address: int
    data: list[int]
    current_index_read: int

    def __init__(self, address: int):
        self.address = address
        self.data = list()
        self.current_index_read = 0

    def get_address(self):
        return self.address

    def set_data(self, data: list[int]):
        self.data = data

    def get_data(self):
        self.current_index_read += 1
        return self.data[self.current_index_read - 1]

    def get_all(self):
        return self.data

    def write_data(self, value: int):
        self.data.append(value)


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
        if self.right == 0:
            raise AluException("Деление на ноль - runtime error")
        self.result = int(self.left / self.right)

    def multiply(self):
        self.result = self.left * self.right

    def inc(self):
        self.result = self.left + 1

    def neg(self):
        self.result = -self.left

    def remainder_of_division(self):
        self.result = self.left % self.right

    def get_result(self):
        return self.result


class DataMemory:
    memory: list[int]
    address_in: int
    data_out: int
    address_register: Register

    def __init__(self, address_register: Register, data_size: int, init_value: int):
        self.memory = [init_value] * data_size
        self.address_in = 0
        self.address_register = address_register

    def latch_read(self):
        self.data_out = self.memory[self.address_in]

    def latch_in(self):
        self.address_in = self.address_register.get_value()

    def latch_write(self, value: int):
        self.memory[self.address_in] = value

    def get_data_out(self):
        return self.data_out


class InstructionMemory:
    memory: list[Instruction]
    address_in: int
    instruction_out: Instruction
    start_address: int

    def __init__(self, instructions: list[Instruction], start_address: int):
        self.address_in = 0
        self.memory = instructions
        self.start_address = start_address

    def latch_in(self, address: int):
        self.address_in = address

    def latch_read_instruction(self):
        self.instruction_out = self.memory[self.address_in - self.start_address]

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
    data_address_register: Register

    standart_out_io: IODevice
    standart_input_io: IODevice

    source_input: list[int]

    alu: Alu

    def write_data(self):
        if self.data_address_register.get_value() == self.standart_out_io.get_address():
            self.standart_out_io.write_data(self.acc.get_value())
        else:
            self.data_memory.latch_write(self.acc.get_value())

    def read_operand(self):
        if (
            self.data_address_register.get_value()
            == self.standart_input_io.get_address()
        ):
            self.data_register.latch(self.standart_input_io.get_data())
        else:
            self.data_memory.latch_read()
            self.data_register.latch(self.data_memory.get_data_out())

    def init_memory(self, instructions: list[Instruction]):
        ind = len(instructions)
        for i in range(len(instructions)):
            if instructions[i].opcode == Opcode.WORD:
                ind = i
                break
        self.instruction_memory = InstructionMemory(
            instructions[:ind], instructions[0].address
        )
        for data in instructions[ind:]:
            self.data_memory.memory[data.address] = data.operand

    def __init__(
        self,
        acc_value: int,
        ip_value: int,
        data_size: int,
        instructions: list[Instruction],
        source_input: list[int],
    ):
        self.acc = Register(acc_value)
        self.ip_register = Register(ip_value)
        self.command_register = Register(0)
        self.data_register = Register(0)
        self.data_address_register = Register(0)
        self.sp_register = Register(data_size)
        self.source_input = source_input

        self.data_memory = DataMemory(self.data_address_register, data_size, 0)
        self.init_memory(instructions)
        self.standart_out_io = IODevice(0)
        self.standart_input_io = IODevice(1)
        self.standart_input_io.set_data(source_input)

        self.flags = {Flag.NF: False, Flag.ZF: False}

        self.alu = Alu()

    def latch_flags(self):
        self.flags[Flag.NF] = self.alu.result < 0
        self.flags[Flag.ZF] = self.alu.result == 0
