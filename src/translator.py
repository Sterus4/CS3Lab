import re
from enum import Enum

from src.exceptions import *
from src.isa import Instruction, write_code, Opcode, Addressing


class DataType(str, Enum):
    INT = "int"
    STRING = "string"


class TokenType(Enum):
    CREATE_NEW_VAR = 1
    STRING = 2
    WHILE = 3
    IF = 4
    QUOTE_ROUND_OPEN = 5
    QUOTE_ROUND_CLOSE = 6
    QUOTE_FIGURE_OPEN = 7
    QUOTE_FIGURE_CLOSE = 8
    COMPARISON = 9
    PRINT = 10
    READ = 11
    INT_VALUE = 12
    VAR_VALUE = 13
    UPDATE_VAR = 14
    MATH_EXPRESSION = 15


def recognise_token(src: str) -> TokenType:
    if src == '':
        raise UnknownToken("Пустая строка в качестве токена")
    if re.match(r'var \w+\s*=', src):
        return TokenType.CREATE_NEW_VAR
    if src[0] == '"' and src[-1] == '"' and len(src) > 1:
        return TokenType.STRING
    if src == "while":
        return TokenType.WHILE
    if src == "if":
        return TokenType.IF
    if src == '{':
        return TokenType.QUOTE_FIGURE_OPEN
    if src == '}':
        return TokenType.QUOTE_FIGURE_CLOSE
    if src == '(':
        return TokenType.QUOTE_ROUND_OPEN
    if src == ')':
        return TokenType.QUOTE_ROUND_CLOSE
    if re.match(r"^[\s0123456789\w*/%+-]+ (==|>|<|>=|<=) [\s0123456789\w*/%+-]+$", src):
        return TokenType.COMPARISON
    if src == 'print':
        return TokenType.PRINT
    if src == 'read':
        return TokenType.READ
    if re.fullmatch(r'^[0-9]+$', src):
        return TokenType.INT_VALUE
    if re.fullmatch(r'^\w+$', src):
        return TokenType.VAR_VALUE
    if re.match(r'^\w+\s*=', src):
        return TokenType.UPDATE_VAR
    if re.fullmatch(r'[\s0123456789\w*/%+-]+', src):
        return TokenType.MATH_EXPRESSION
    raise UnknownToken("Несуществующий токен: " + src)


key_words = ["while", "if", "print", "read"]
#Название переменной, которое соответствует типу переменной и адресу в памяти
variables: dict[str, tuple[DataType, int]] = dict()
current_free_data_address = 10
current_instruction_address = 0
result: list[Instruction] = list()


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


def create_math(statement):
    global current_instruction_address
    global current_free_data_address
    result.append(Instruction(current_instruction_address, Opcode.LD, int(statement), Addressing.DIR))
    current_instruction_address += 1


def create_code(code: list[str]):
    global current_instruction_address
    global current_free_data_address
    global variables
    i = 0
    while True:
        if i >= len(code):
            return
        current_token = code[i]
        match recognise_token(current_token):
            case TokenType.CREATE_NEW_VAR:
                new_variable_name = current_token[3:current_token.index('=')].strip()
                if new_variable_name in variables:
                    raise VarException("Переменная: " + new_variable_name + " уже определена")
                if current_token[-1] == '=' and recognise_token(code[i + 1]) == TokenType.STRING:
                    #Проинициализировали новую строку
                    variables[new_variable_name] = (DataType.STRING, current_free_data_address)
                    new_string = code[i + 1][1:-1]
                    create_operation(Opcode.LD, current_free_data_address + 1, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address)
                    current_free_data_address += 1
                    for char in new_string:
                        create_operation(Opcode.LD, ord(char), Addressing.DIR)
                        create_operation(Opcode.ST, current_free_data_address)
                        current_free_data_address += 1
                    create_operation(Opcode.LD, 0, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address)
                    current_free_data_address += 1
                    i += 1
                else:
                    statement = current_token[current_token.index('=') + 1:].strip()
                    if recognise_token(statement) == TokenType.VAR_VALUE:
                        if statement not in variables:
                            raise VarException("Переменная: " + statement + " не определена")
                        if variables[statement][0] == DataType.STRING:
                            create_operation(Opcode.LD, variables[statement][1], Addressing.MEM)
                            create_operation(Opcode.ST, current_free_data_address)
                            variables[new_variable_name] = (DataType.STRING, current_free_data_address)
                            current_free_data_address += 1
                        else:
                            create_operation(Opcode.LD, variables[statement][1], Addressing.MEM)
                            create_operation(Opcode.ST, current_free_data_address)
                            variables[new_variable_name] = (DataType.INT, current_free_data_address)
                            current_free_data_address += 1
                    else:
                        create_math(statement)
                        result.append(Instruction(current_instruction_address, Opcode.ST, current_free_data_address))
                        variables[new_variable_name] = (DataType.INT, current_free_data_address)
                        current_instruction_address += 1
                        current_free_data_address += 1

        i += 1


def create_operation(opcode, operand=None, addressing=None):
    global current_instruction_address
    global current_free_data_address
    global result
    global variables
    result.append(Instruction(current_instruction_address, opcode, operand, addressing))
    current_instruction_address += 1


def translate(src: str) -> list[Instruction]:
    if src.count('"') % 2 != 0:
        raise TranslateException("Неправильно расставлены кавычки для строк")

    code = split_by_symbol([src], '"')
    code_modified = []
    i = 0
    while i < len(code):
        temp = code[i]
        if temp[0] == '"':
            if(code[i + 1])[0] != '"':
                code_modified.append('"' + code[i + 1] + '"')
                i += 3
            else:
                code_modified.append('""')
                i += 2
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
    create_code(code)
    for temp in variables:
        print(temp, ' : ', variables[temp][0], variables[temp][1])
    result.append(Instruction(current_instruction_address, Opcode.HLT, None, None))

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
