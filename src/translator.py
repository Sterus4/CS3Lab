from enum import Enum

from src.exceptions import TranslateException
from src.isa import Instruction, write_code, Opcode, Addressing


class DataType(str, Enum):
    INT = "int"
    STRING = "string"


key_words = ["while", "if", "print", "read"]
variables = dict[
    str, tuple[DataType, int]]  #Название переменной, которое соответствует типу переменной и адресу в памяти
current_free_data_address = 0


def split_by_symbol(code: list, symbol: chr):
    code_modified = []
    for temp in code:
        if temp[0] == '"' or symbol not in temp:
            code_modified.append(temp)
            continue
        while symbol in temp:
            code_modified.append(temp[:temp.index(symbol)].strip())
            code_modified.append(symbol)
            temp = temp[temp.index(symbol) + 1:]
        code_modified.append(temp.strip())
    code_modified = [temp for temp in code_modified if temp != '']
    return code_modified


def check_string(string: str):
    return string[0] == '"' or string[-1] == '"'


def check_math_expression(expression: str):
    pass


def check_while(code: list, index: int):
    pass


def check_if(code: list, index: int):
    pass


def check():
    pass


def valid_code(code):
    pass


def translate(src: str) -> list[Instruction]:
    result: list[Instruction] = list()

    if src.count('"') % 2 != 0:
        raise TranslateException("Неправильно расставлены кавычки для строк")

    code = split_by_symbol([src], '"')
    code_modified = []
    i = 0
    while i < len(code):
        temp = code[i]
        if temp[0] == '"':
            code_modified.append('"' + code[i + 1] + '"')
            i += 3
        else:
            i += 1
            code_modified.append(temp)
    code = code_modified.copy()
    code = split_by_symbol(code, ';')
    code = [temp for temp in code if temp != '' and temp != ';']
    code = split_by_symbol(code, '{')
    code = split_by_symbol(code, '}')
    code = split_by_symbol(code, '(')
    code = split_by_symbol(code, ')')
    # Разделили код на блоки
    print(code)
    # Проверим код на валидность
    valid_code(code)

    return result


def main(source: str, target: str):
    with open(source, 'r', encoding='utf-8') as f:
        source = f.read()
    code = translate(source)
    write_code(target, code)
    print("Файл транслирован")


if __name__ == '__main__':
    #assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    #main(sys.argv[1], sys.argv[2])
    main("input.txt", "output.txt")
