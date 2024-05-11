import re
from enum import Enum

from src.exceptions import *
from src.isa import Instruction, write_code, Opcode, Addressing
from RPNMath import create_rpn_expression


class DataType(str, Enum):
    INT = "int"
    CHAR = "char"
    POINTER = "pointer"


class TokenType(Enum):
    CREATE_NEW_VAR = 1
    CREATE_NEW_POINTER = 2
    STRING = 3
    WHILE = 4
    IF = 5
    QUOTE_ROUND_OPEN = 6
    QUOTE_ROUND_CLOSE = 7
    QUOTE_FIGURE_OPEN = 8
    QUOTE_FIGURE_CLOSE = 9
    COMPARISON = 10
    PRINT = 11
    READ = 12
    VAR_VALUE = 13
    UPDATE_VAR = 14
    MATH_EXPRESSION = 15


def recognise_token(src: str) -> TokenType:
    if src == '':
        raise UnknownToken("Пустая строка в качестве токена")
    if re.match(r'(int|char) \w+', src):
        return TokenType.CREATE_NEW_VAR
    if re.match(r'(int|char)\[[0123456789]*] \w+', src):
        return TokenType.CREATE_NEW_POINTER
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
    if re.match(r"^[\s()0123456789\w*/%+-]+(==|>|<|>=|<=)[\s()0123456789\w*/%+-]+$", src):
        return TokenType.COMPARISON
    if src == 'print':
        return TokenType.PRINT
    if src == 'read':
        return TokenType.READ
    if re.fullmatch(r'^\w+$', src):
        return TokenType.VAR_VALUE
    if re.match(r'^\w+\s*=', src):
        return TokenType.UPDATE_VAR
    if re.fullmatch(r'[\s()0123456789\w*/%+-]+', src):
        return TokenType.MATH_EXPRESSION
    raise UnknownToken("Несуществующий токен: " + src)


key_words = ["while", "if", "read", "print"]
variables: dict[str, tuple[DataType, int]] = dict()
current_free_data_address = 10
current_instruction_address = 0
result: list[Instruction] = list()


def is_char(src: str) -> bool:
    return len(src) == 3 and src[0] == '\'' and src[-1] == '\''


def create_math(statement):
    global current_instruction_address
    global current_free_data_address
    expression = create_rpn_expression(statement)
    print(expression)
    create_operation(Opcode.LD, int(statement), Addressing.DIR)


def create_code(code: list[str]):
    global current_instruction_address
    global current_free_data_address
    global variables
    i = 0
    while i < len(code):
        current_token = code[i]
        #print(recognise_token(current_token))
        match recognise_token(current_token):
            case TokenType.CREATE_NEW_VAR:
                var_type = current_token.split()[0]
                var_name = current_token.split()[1].split('=')[0].strip()
                if var_name in variables:
                    raise VarException("Переменная " + var_name + " уже существует")
                operand = None
                if '=' in current_token:
                    operand = current_token.split('=')[1].strip()
                    if operand == '': raise VarException(current_token + ": ожидалась инициализация")
                #print(var_type, var_name, operand)
                variables[var_name] = (DataType.CHAR if var_type == "char" else DataType.INT, current_free_data_address)
                if var_type == "int":
                    if operand is None:
                        create_operation(Opcode.LD, 0, Addressing.DIR)
                    else:
                        create_math(operand)
                elif var_type == "char":
                    if operand is None:
                        local_operand = 0
                    elif not operand.isdigit() and not is_char(operand):
                        raise VarException("Инициализировать char можно только числом или символом: " + current_token)
                    elif is_char(operand):
                        local_operand = ord(operand[1])
                    else:
                        if int(operand) < 0 or int(operand) > 255: raise VarException(
                            "В char нельзя сохранить число больше 255: " + current_token)
                        local_operand = operand
                    create_operation(Opcode.LD, local_operand, Addressing.DIR)
                create_operation(Opcode.ST, current_free_data_address)
                current_free_data_address += 1
            case TokenType.CREATE_NEW_POINTER:
                var_type = current_token.split('[')[0]
                if var_type != "char": raise VarException("В языке поддерживаются только char pointer: " + current_token)
                var_name = current_token.split(']')[1].split('=')[0].strip()
                if var_name in variables:
                    raise VarException("Переменная " + var_name + " уже существует")
                if current_token[current_token.find('[') + 1] == ']':
                    var_capacity = -1
                else:
                    var_capacity = int(current_token[current_token.find('[') + 1:current_token.find(']')])
                if var_capacity == 0: raise VarException("Нельзя проинициализировать массив из 0 элементов: " + current_token)
                operand = None
                if '=' in current_token:
                    operand = current_token.split('=')[1].strip()
                    if operand == '': raise VarException(current_token + ": ожидалась инициализация")
                variables[var_name] = (DataType.POINTER, current_free_data_address)
                if var_capacity == -1 and operand is None: raise InvalidToken("Неизвестный токен: " + current_token)
                if var_capacity == -1:
                    if recognise_token(operand) != TokenType.STRING: raise InvalidToken("Неизвестный токен: " + current_token)
                    create_operation(Opcode.LD, current_free_data_address + 1, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address)
                    current_free_data_address += 1
                    operand = operand[1:-1]
                    for char in operand:
                        create_operation(Opcode.LD, ord(char), Addressing.DIR)
                        create_operation(Opcode.ST, current_free_data_address)
                        current_free_data_address += 1
                    create_operation(Opcode.LD, 0, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address)
                    current_free_data_address += 1
                else:
                    if operand is not None and recognise_token(operand) != TokenType.STRING: raise InvalidToken("Неизвестный токен: " + current_token)
                    create_operation(Opcode.LD, current_free_data_address + 1, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address)
                    current_free_data_address += 1
                    if operand is not None:
                        local_free_data_address = current_free_data_address
                        operand = operand[1:-1]
                        print(len(operand))
                        count = 0
                        for char in operand:
                            if count >= min(var_capacity - 1, len(operand)):
                                break
                            count += 1
                            create_operation(Opcode.LD, ord(char), Addressing.DIR)
                            create_operation(Opcode.ST, local_free_data_address)
                            local_free_data_address += 1
                        create_operation(Opcode.LD, 0, Addressing.DIR)
                        create_operation(Opcode.ST, local_free_data_address)

                    current_free_data_address += var_capacity
                print(var_capacity, var_name, operand)
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
    code = []
    current = ""
    in_string = False
    for char in src:
        if char == ';' and not in_string:
            code.append(current)
            current = ''
            continue
        if (char == '{' or char == '}') and not in_string:
            code.append(current)
            code.append(char)
            current = ''
            continue
        elif char == '"':
            in_string = not in_string
        current += char
    code = [temp.strip() for temp in code if temp.strip() != '']
    code_modified = []
    for temp in code:
        modified = False
        for key_word in key_words:
            n = len(key_word)
            if temp[:n] != key_word:
                continue
            if temp[n] != '(' or temp[-1] != ')':
                raise InvalidToken("Ошибка в строке: " + temp)
            code_modified.extend([key_word, '(', temp[n + 1:-1].strip(), ')'])
            modified = True
        if not modified: code_modified.append(temp)
    code = code_modified.copy()
    # Код разбит на лексемы
    print(code)

    create_code(code)
    #for temp in variables:
    #    print(temp, ' : ', variables[temp][0], variables[temp][1])
    create_operation(Opcode.HLT)
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
