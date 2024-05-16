import sys
from isa import read_code
from src.control_unit import ControlUnit

data_memory_size = 8000


def main(target_program, input_src):
    data_memory = [0] * data_memory_size
    instructions = read_code(target_program)

    with open(input_src) as input_file:
        input_char_list = [ord(i) for i in input_file.read()]
        input_char_list.append(0)
    for i in instructions:
        print(i)
    print(input_char_list)

    control_unit = ControlUnit(instructions, data_memory, input_char_list, 0)
    control_unit.simulate()


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <program> <source_file>"
    main(sys.argv[1], sys.argv[2])
