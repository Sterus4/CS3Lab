from src.datapath import Datapath, Flag
from src.isa import Instruction, Opcode, Addressing


def is_instruction_address(instruction: Instruction):
    return instruction.opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD, Opcode.LD, Opcode.ST]


class ControlUnit:
    output: list[chr]
    datapath: Datapath
    instruction_limit: int
    new_symbol_on_output: bool
    current_input_index: int

    def __init__(self, source_input: list[int], datapath: Datapath, instruction_limit: int):
        self.source_input = source_input
        self.datapath = datapath
        self.output = []
        self.instruction_limit = instruction_limit
        self.new_symbol_on_output = False
        self.current_input_index = 0

        if len(self.source_input) > 0: self.datapath.data_memory.memory[1] = source_input[self.current_input_index]
        self.current_input_index += 1

    def instruction_fetch(self):
        self.datapath.instruction_memory.latch_in(self.datapath.ip_register.get_value())
        self.datapath.instruction_memory.latch_read_instruction()
        self.datapath.ip_register.latch(self.datapath.ip_register.get_value() + 1)
        self.datapath.command_register.latch(self.datapath.instruction_memory.get_instruction())

    def address_fetch(self, instruction: Instruction):
        operand = instruction.operand
        match instruction.addressing:
            case Addressing.MEM:
                self.datapath.alu.latch_left(0)
                self.datapath.alu.latch_right(operand)
                self.datapath.alu.add()
                self.datapath.data_memory.latch_in(self.datapath.alu.get_result())
            case Addressing.SP:
                self.datapath.alu.latch_left(self.datapath.sp_register.get_value())
                self.datapath.alu.latch_right(operand)
                self.datapath.alu.add()
                self.datapath.data_memory.latch_in(self.datapath.alu.get_result())
            case Addressing.IND_MEM:
                self.datapath.alu.latch_left(0)
                self.datapath.alu.latch_right(operand)
                self.datapath.alu.add()
                self.datapath.data_memory.latch_in(self.datapath.alu.get_result())

                self.datapath.data_memory.latch_read()
                self.datapath.data_register.latch(self.datapath.data_memory.get_data_out())

                self.datapath.alu.latch_left(0)
                self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                self.datapath.alu.add()
                self.datapath.data_memory.latch_in(self.datapath.alu.get_result())

    def jump_to(self, operand: int):
        self.datapath.alu.latch_left(0)
        self.datapath.alu.latch_right(operand)
        self.datapath.alu.add()
        self.datapath.ip_register.latch(self.datapath.alu.get_result())

    def operand_fetch(self):
        self.datapath.data_memory.latch_read()
        self.datapath.data_register.latch(self.datapath.data_memory.get_data_out())

    def show_output(self):
        print("Вывод программы: ")
        print('--------')
        out = [chr(i) for i in self.output]
        print(''.join(out))
        print('--------')

    def simulate(self):
        i = 0
        while i < self.instruction_limit:
            self.instruction_fetch()
            current_instruction: Instruction = self.datapath.command_register.get_value()

            if is_instruction_address(current_instruction):
                self.address_fetch(current_instruction)
            if is_instruction_address(current_instruction) and current_instruction.opcode != Opcode.ST:
                if current_instruction.addressing == Addressing.DIR:
                    self.datapath.data_register.latch(self.datapath.command_register.get_value().operand)
                else:
                    self.operand_fetch()

            match current_instruction.opcode:
                case Opcode.ADD:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.add()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.SUB:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.subtract()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.MUL:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.multiply()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.DIV:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.divide()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.MOD:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.remainder_of_division()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.LD:
                    self.datapath.alu.latch_left(0)
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.add()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    if current_instruction.operand == 1 and current_instruction.addressing == Addressing.MEM:
                        if self.current_input_index < len(self.source_input):
                            self.datapath.data_memory.memory[1] = self.source_input[self.current_input_index]
                            self.current_input_index += 1
                    self.datapath.latch_flags()
                case Opcode.ST:
                    if current_instruction.addressing == Addressing.DIR: raise Exception(
                        "Невозможно провести операцию ST При прямой адрессации: " + str(current_instruction))
                    if current_instruction.operand == 0 and current_instruction.addressing == Addressing.MEM: self.new_symbol_on_output = True
                    self.datapath.data_memory.latch_write(self.datapath.acc.get_value())
                case Opcode.PUSH:
                    self.datapath.data_memory.latch_in(self.datapath.sp_register.get_value() - 1)
                    self.datapath.sp_register.latch(self.datapath.sp_register.get_value() - 1)
                    self.datapath.data_memory.latch_write(self.datapath.acc.get_value())
                case Opcode.POP:
                    self.datapath.data_memory.latch_in(self.datapath.sp_register.get_value())
                    self.datapath.sp_register.latch(self.datapath.sp_register.get_value() + 1)
                    self.datapath.data_memory.latch_read()
                    self.datapath.data_register.latch(self.datapath.data_memory.get_data_out())

                    self.datapath.alu.latch_left(0)
                    self.datapath.alu.latch_right(self.datapath.data_register.get_value())
                    self.datapath.alu.add()
                    self.datapath.acc.latch(self.datapath.alu.get_result())

                    self.datapath.latch_flags()
                case Opcode.INC:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.inc()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.NEG:
                    self.datapath.alu.latch_left(self.datapath.acc.get_value())
                    self.datapath.alu.neg()
                    self.datapath.acc.latch(self.datapath.alu.get_result())
                    self.datapath.latch_flags()
                case Opcode.JMP:
                    self.jump_to(current_instruction.operand)
                case Opcode.JZ:
                    if self.datapath.flags[Flag.ZF] == True: self.jump_to(current_instruction.operand)
                case Opcode.JNZ:
                    if self.datapath.flags[Flag.ZF] == False: self.jump_to(current_instruction.operand)
                case Opcode.JBZ:
                    if self.datapath.flags[Flag.ZF] == True or self.datapath.flags[Flag.NF] == True: self.jump_to(
                        current_instruction.operand)
                case Opcode.JB:
                    if self.datapath.flags[Flag.ZF] == False and self.datapath.flags[Flag.NF] == True: self.jump_to(
                        current_instruction.operand)
                case Opcode.JAZ:
                    if self.datapath.flags[Flag.ZF] == True or self.datapath.flags[Flag.NF] == False: self.jump_to(
                        current_instruction.operand)
                case Opcode.JA:
                    if self.datapath.flags[Flag.ZF] == False and self.datapath.flags[Flag.NF] == False: self.jump_to(
                        current_instruction.operand)
                case Opcode.HLT:
                    self.show_output()
                    return
            print('--------')
            print("Номер итерации: " + str(i))
            print(current_instruction)
            print("ACC: " + str(self.datapath.acc.get_value()) + ", IP: " + str(self.datapath.ip_register.get_value()) + ", SP: " + str(self.datapath.sp_register.get_value()))
            if self.new_symbol_on_output:
                self.new_symbol_on_output = False
                self.output.append(self.datapath.data_memory.memory[0])
            i += 1
