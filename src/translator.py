import re
import sys
from enum import Enum

from src.exceptions import *
from src.isa import Instruction, write_code, Opcode, Addressing
from RPNMath import create_rpn_expression

IO_OUT_MEM = 0  # Адрес вывода
IO_IN_MEM = 1  # Адрес ввода


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
    CHAR = 16


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
    if is_char(src):
        return TokenType.CHAR
    if re.match(r"^[\s()0123456789\w*/%+-]+(==|>|<|>=|<=)[\s()0123456789\w*/%+-]+$", src):
        return TokenType.COMPARISON
    if src == 'print':
        return TokenType.PRINT
    if src == 'read':
        return TokenType.READ
    if re.fullmatch(r'^\w*[a-zA-Z]\w*$', src):
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
    global variables
    expression = create_rpn_expression(statement.strip())
    for i in expression:
        if i.isdigit():
            create_operation(Opcode.LD, i, Addressing.DIR)
            if len(expression) == 1: break
            create_operation(Opcode.PUSH)
        elif re.fullmatch('^\w+$', i):
            if i not in variables or variables[i][0] == DataType.POINTER:
                raise VarException("Переменная: " + i + " не существует, или не является числом: " + statement)
            create_operation(Opcode.LD, variables[i][1], Addressing.MEM)
            if len(expression) == 1: break
            create_operation(Opcode.PUSH)
        else:
            create_operation(Opcode.POP)
            create_operation(Opcode.LD, 0, Addressing.SP)
            match i:
                case '+':
                    create_operation(Opcode.ADD, -1, Addressing.SP)
                case '-':
                    create_operation(Opcode.SUB, -1, Addressing.SP)
                case '*':
                    create_operation(Opcode.MUL, -1, Addressing.SP)
                case '/':
                    create_operation(Opcode.DIV, -1, Addressing.SP)
                case '%':
                    create_operation(Opcode.MOD, -1, Addressing.SP)
                case _:
                    raise MathExpressionException("Неизвестный знак выражения: " + i)
            create_operation(Opcode.ST, 0, Addressing.SP)
    if len(expression) != 1: create_operation(Opcode.POP)


def create_comparison(left: str, right: str):
    global current_instruction_address
    global current_free_data_address
    global variables
    create_math(right)
    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
    create_math(left)
    create_operation(Opcode.SUB, current_free_data_address, Addressing.MEM)


def find_end_of_block(code: list[str], start_position: int) -> int:
    i = start_position + 1
    count = 1
    while i < len(code):
        if code[i] == '}':
            count -= 1
            if count == 0: return i
        if code[i] == '{':
            count += 1
        i += 1
    raise TranslateException("Не хватает закрывающей фигурной скобки для блока")


def add_print_char(src: chr):
    create_operation(Opcode.LD, ord(src), Addressing.DIR)
    create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)


def add_print_string(src: str):
    src = src[1:-1]
    for i in src:
        add_print_char(i)


def add_print_pointer():  # В Acc адрес начала строки
    global current_instruction_address
    global current_free_data_address
    global variables
    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
    index_to_jump = len(result)
    create_operation(Opcode.LD, current_free_data_address, Addressing.IND_MEM)

    #TODO как будем делать LD? Через алу?
    create_operation(Opcode.SUB, 0, Addressing.DIR)
    #TODO УБЕРИ ЭТО ЕСЛИ РАЗОБРАЛСЯ + Поправь адреса без одной команды
    create_operation(Opcode.JZ, current_instruction_address + 6)
    create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)
    create_operation(Opcode.LD, current_free_data_address, Addressing.MEM)
    create_operation(Opcode.INC)
    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
    create_operation(Opcode.JMP, index_to_jump)


def add_print_number():  # Число уже находится в аккумуляторе
    global current_instruction_address
    global current_free_data_address
    global variables
    create_operation(Opcode.ST, current_free_data_address + 1, Addressing.MEM)
    create_operation(Opcode.JA, current_instruction_address + 2)
    create_operation(Opcode.NEG)
    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
    create_operation(Opcode.LD, 0, Addressing.DIR)
    create_operation(Opcode.PUSH)
    create_operation(Opcode.LD, current_free_data_address, Addressing.MEM)
    index_to_jump = result[-1].address + 1
    create_operation(Opcode.MOD, 10, Addressing.DIR)
    create_operation(Opcode.ADD, 48, Addressing.DIR)
    create_operation(Opcode.PUSH)
    create_operation(Opcode.LD, current_free_data_address, Addressing.MEM)
    create_operation(Opcode.DIV, 10, Addressing.DIR)
    create_operation(Opcode.JZ, current_instruction_address + 3)
    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
    create_operation(Opcode.JMP, index_to_jump)
    create_operation(Opcode.LD, current_free_data_address + 1, Addressing.MEM)
    create_operation(Opcode.JA, current_instruction_address + 3)
    create_operation(Opcode.LD, 45, Addressing.DIR)
    create_operation(Opcode.PUSH)
    # После того как число оказалось в стеке, выводим его
    index_to_jump = result[-1].address + 1
    create_operation(Opcode.POP)
    create_operation(Opcode.JZ, current_instruction_address + 3)
    create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)
    create_operation(Opcode.JMP, index_to_jump)


def add_read_pointer(variable_address: int):
    global current_instruction_address
    global current_free_data_address
    global variables
    create_operation(Opcode.LD, variable_address, Addressing.MEM)
    create_operation(Opcode.PUSH)
    index_to_jump = len(result)

    create_operation(Opcode.LD, IO_IN_MEM, Addressing.MEM)
    create_operation(Opcode.ST, variable_address, Addressing.IND_MEM)
    # TODO как будем делать LD? Через алу?
    create_operation(Opcode.SUB, 0, Addressing.DIR)
    # TODO УБЕРИ ЭТО ЕСЛИ РАЗОБРАЛСЯ + Поправь адреса без одной команды
    create_operation(Opcode.JZ, current_instruction_address + 5)
    create_operation(Opcode.LD, variable_address, Addressing.MEM)
    create_operation(Opcode.INC)
    create_operation(Opcode.ST, variable_address, Addressing.MEM)
    create_operation(Opcode.JMP, index_to_jump)

    create_operation(Opcode.POP)
    create_operation(Opcode.ST, variable_address, Addressing.MEM)


def create_reverse_sign(comparison_sign: str):
    current_command: Opcode = Opcode.JZ
    match comparison_sign:
        case '==':
            current_command = Opcode.JNZ
        case '!=':
            current_command = Opcode.JZ
        case '>':
            current_command = Opcode.JBZ
        case '<':
            current_command = Opcode.JAZ
        case '>=':
            current_command = Opcode.JB
        case '<=':
            current_command = Opcode.JA
    create_operation(current_command)


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
                create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
                current_free_data_address += 1
            case TokenType.CREATE_NEW_POINTER:
                var_type = current_token.split('[')[0]
                if var_type != "char": raise VarException(
                    "В языке поддерживаются только char pointer: " + current_token)
                var_name = current_token.split(']')[1].split('=')[0].strip()
                if var_name in variables:
                    raise VarException("Переменная " + var_name + " уже существует")
                if current_token[current_token.find('[') + 1] == ']':
                    var_capacity = -1
                else:
                    var_capacity = int(current_token[current_token.find('[') + 1:current_token.find(']')])
                if var_capacity == 0: raise VarException(
                    "Нельзя проинициализировать массив из 0 элементов: " + current_token)
                operand = None
                if '=' in current_token:
                    operand = current_token[current_token.find('=') + 1:].strip()
                    if operand == '': raise VarException(current_token + ": ожидалась инициализация")
                variables[var_name] = (DataType.POINTER, current_free_data_address)
                if var_capacity == -1 and operand is None: raise InvalidToken("Неизвестный токен: " + current_token)
                if var_capacity == -1:
                    print(operand)
                    if recognise_token(operand) != TokenType.STRING: raise InvalidToken(
                        "Неизвестный токен: " + current_token)
                    create_operation(Opcode.LD, current_free_data_address + 1, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
                    current_free_data_address += 1
                    operand = operand[1:-1]
                    for char in operand:
                        create_operation(Opcode.LD, ord(char), Addressing.DIR)
                        create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
                        current_free_data_address += 1
                    create_operation(Opcode.LD, 0, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
                    current_free_data_address += 1
                else:
                    if operand is not None and recognise_token(operand) != TokenType.STRING: raise InvalidToken(
                        "Неизвестный токен: " + current_token)
                    create_operation(Opcode.LD, current_free_data_address + 1, Addressing.DIR)
                    create_operation(Opcode.ST, current_free_data_address, Addressing.MEM)
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
                            create_operation(Opcode.ST, local_free_data_address, Addressing.MEM)
                            local_free_data_address += 1
                        create_operation(Opcode.LD, 0, Addressing.DIR)
                        create_operation(Opcode.ST, local_free_data_address, Addressing.MEM)

                    current_free_data_address += var_capacity
                print(var_capacity, var_name, operand)
            case TokenType.UPDATE_VAR:
                var_name, operand = current_token.split('=')[0].strip(), current_token.split('=')[1].strip()
                if var_name not in variables: raise VarException(
                    "Переменной " + var_name + " не существует: " + current_token)
                if variables[var_name][0] == DataType.POINTER: raise VarException(
                    "Нельзя изменить указатель: " + current_token)  #TODO (Возможно поправить, если надо будет уметь изменять указатели)
                if variables[var_name][0] == DataType.CHAR:
                    if is_char(operand):
                        create_operation(Opcode.LD, ord(operand[1]), Addressing.DIR)
                    elif operand.isdigit() and 0 <= int(operand) <= 255:
                        create_operation(Opcode.LD, operand, Addressing.DIR)
                    else:
                        raise VarException(
                            "Инициализировать char можно только числом от 0 до 255 или символом: " + current_token)
                else:
                    create_math(operand)
                create_operation(Opcode.ST, variables[var_name][1], Addressing.MEM)
            case TokenType.IF:
                if (recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN
                        or recognise_token(code[i + 2]) != TokenType.COMPARISON
                        or recognise_token(code[i + 3]) != TokenType.QUOTE_ROUND_CLOSE
                        or recognise_token(code[i + 4]) != TokenType.QUOTE_FIGURE_OPEN):
                    raise TranslateException("Неправильный формат if выражения: " + str(code[i:i + 4]))
                start_of_block, end_of_block = i + 4, find_end_of_block(code, i + 4)
                left, comparison_sign, right = re.split(r'(==|>=|<=|>|<)', code[i + 2])
                create_comparison(left, right)
                comparison_index = len(result)
                create_reverse_sign(comparison_sign)
                create_code(code[start_of_block + 1: end_of_block])
                result[comparison_index].operand = current_instruction_address
                i = end_of_block
            case TokenType.WHILE:
                if (recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN
                        or recognise_token(code[i + 2]) != TokenType.COMPARISON
                        or recognise_token(code[i + 3]) != TokenType.QUOTE_ROUND_CLOSE
                        or recognise_token(code[i + 4]) != TokenType.QUOTE_FIGURE_OPEN):
                    raise TranslateException("Неправильный формат while выражения: " + str(code[i:i + 4]))
                start_of_block, end_of_block = i + 4, find_end_of_block(code, i + 4)
                left, comparison_sign, right = re.split(r'(==|>=|<=|>|<)', code[i + 2])
                while_start = current_instruction_address
                create_comparison(left, right)
                comparison_index = len(result)
                create_reverse_sign(comparison_sign)
                create_code(code[start_of_block + 1: end_of_block])
                result[comparison_index].operand = current_instruction_address + 1
                create_operation(Opcode.JMP, while_start)
                i = end_of_block
            case TokenType.PRINT:
                if recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN or recognise_token(
                        code[i + 3]) != TokenType.QUOTE_ROUND_CLOSE:
                    raise TranslateException("Неправильный формат: " + current_token)
                match recognise_token(code[i + 2]):
                    case TokenType.STRING:
                        add_print_string(code[i + 2])
                    case TokenType.CHAR:
                        add_print_char(code[i + 2][1])
                    case TokenType.VAR_VALUE:
                        if code[i + 2] not in variables: raise VarException("Переменной не существует: " + code[i + 2])
                        match variables[code[i + 2]][0]:
                            case DataType.CHAR:
                                create_operation(Opcode.LD, variables[code[i + 2]][1], Addressing.MEM)
                                create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)
                            case DataType.INT:
                                create_operation(Opcode.LD, variables[code[i + 2]][1], Addressing.MEM)
                                add_print_number()
                            case DataType.POINTER:
                                create_operation(Opcode.LD, variables[code[i + 2]][1], Addressing.MEM)
                                add_print_pointer()
                    case _:
                        create_math(code[i + 2])
                        add_print_number()
                i += 3

            case TokenType.READ:
                if recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN or recognise_token(
                        code[i + 3]) != TokenType.QUOTE_ROUND_CLOSE or recognise_token(
                    code[i + 2]) != TokenType.VAR_VALUE:
                    raise TranslateException("Неправильный формат: " + current_token)
                var_name = code[i + 2]
                if var_name not in variables: raise VarException("Переменной не существует: " + code[i + 2])
                match variables[var_name][0]:
                    case DataType.CHAR:
                        create_operation(Opcode.LD, IO_IN_MEM, Addressing.MEM)
                        create_operation(Opcode.ST, variables[var_name][1], Addressing.MEM)
                    case DataType.POINTER:
                        add_read_pointer(variables[var_name][1])
                    case _:
                        raise VarException("Считать можно либо в символ, либо в указатель: " + current_token)
                i += 3

            case _:
                raise TranslateException("Неизвестный токен: " + current_token)
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
            if '(' not in temp or temp[-1] != ')':
                raise InvalidToken("Ошибка в строке: " + temp)
            code_modified.extend([key_word, '(', temp[temp.find('(') + 1:-1].strip(), ')'])
            modified = True
        if not modified: code_modified.append(temp)
    code = code_modified.copy()
    # Код разбит на лексемы
    print(code)

    create_code(code)
    for temp in variables:
        print(temp, ' : ', variables[temp][0], variables[temp][1])
    create_operation(Opcode.HLT)
    return result


def main(source: str, target: str):
    with open(source, 'r', encoding='utf-8') as f:
        source = f.read()
    code = translate(source)
    write_code(target, code)
    print("Файл транслирован")


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    main(sys.argv[1], sys.argv[2])
