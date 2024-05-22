import sys
from src.isa import read_code
from src.control_unit import ControlUnit
from src.datapath import Datapath

data_memory_size = 8000


def main(target_program, input_src):
    instructions = read_code(target_program)
    with open(input_src) as input_file:
        input_char_list = [ord(i) for i in input_file.read()]
        input_char_list.append(0)

    datapath = Datapath(0, instructions[0].address, 1000, instructions, input_char_list)
    control_unit = ControlUnit(datapath, 10_000)
    control_unit.simulate()


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <program> <source_file>"
    main(sys.argv[1], sys.argv[2])
