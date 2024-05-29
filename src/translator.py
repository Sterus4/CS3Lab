import re
import sys
from enum import Enum

from src.exceptions import (
    UnknownToken,
    VarException,
    MathExpressionException,
    TranslateException,
    InvalidToken,
)
from src.isa import Instruction, write_code, Opcode, Addressing
from src.rpn_math import create_rpn_expression

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


def is_char(src: str) -> bool:
    return len(src) == 3 and src[0] == "'" and src[-1] == "'"


class AstExpression:
    name: str
    body: str

    def __init__(self, name: str, body: str):
        self.name = name
        self.body = body

    def __str__(self):
        return self.name + " : " + self.body


class AstNode:
    name: str
    body_expression: list

    def __init__(self, name: str, body_exp: list):
        self.name = name
        self.body_expression = body_exp

    def __str__(self):
        result = self.name + " : {\n"
        for i in self.body_expression:
            if isinstance(i, AstExpression):
                result += "\t" + str(i) + ";\n"
            else:
                for j in str(i).split("\n"):
                    result += "\t" + str(j) + "\n"
        return result + "}"


class Translator:
    def __init__(self):
        self.key_words = ["while", "if", "read", "print"]
        self.variables: dict[str, tuple[DataType, int]] = dict()
        self.current_free_data_address = 10
        self.current_instruction_address = 200
        self.result: list[Instruction] = list()
        self.result_data: list[Instruction] = list()

    def recognise_token(self, src: str) -> TokenType:
        if src == "":
            raise UnknownToken("Пустая строка в качестве токена")
        if re.match(r"(int|char)\s+\w+", src):
            return TokenType.CREATE_NEW_VAR
        if re.match(r"(int|char)\[[0123456789]*]\s+\w+", src):
            return TokenType.CREATE_NEW_POINTER
        if src[0] == '"' and src[-1] == '"' and len(src) > 1:
            return TokenType.STRING
        if src == "while":
            return TokenType.WHILE
        if src == "if":
            return TokenType.IF
        if src == "{":
            return TokenType.QUOTE_FIGURE_OPEN
        if src == "}":
            return TokenType.QUOTE_FIGURE_CLOSE
        if src == "(":
            return TokenType.QUOTE_ROUND_OPEN
        if src == ")":
            return TokenType.QUOTE_ROUND_CLOSE
        if is_char(src):
            return TokenType.CHAR
        if re.match(
            r"^[\s()0123456789\w*/%+-]+(!=|==|>|<|>=|<=)[\s()0123456789\w*/%+-]+$", src
        ):
            return TokenType.COMPARISON
        if src == "print":
            return TokenType.PRINT
        if src == "read":
            return TokenType.READ
        if re.fullmatch(r"^\w*[a-zA-Z]\w*$", src):
            return TokenType.VAR_VALUE
        if re.match(r"^\w+\s*=", src):
            return TokenType.UPDATE_VAR
        if re.fullmatch(r"[\s()0123456789\w*/%+-]+", src):
            return TokenType.MATH_EXPRESSION
        raise UnknownToken("Несуществующий токен: " + src)

    def create_math(self, statement):
        expression = create_rpn_expression(statement.strip())
        for i in expression:
            if i.isdigit():
                self.create_operation(Opcode.LD, i, Addressing.DIR)
                if len(expression) == 1:
                    break
                self.create_operation(Opcode.PUSH)
            elif re.fullmatch(r"^\w+$", i):
                if i not in self.variables or self.variables[i][0] == DataType.POINTER:
                    raise VarException(
                        "Переменная: "
                        + i
                        + " не существует, или не является числом: "
                        + statement
                    )
                self.create_operation(Opcode.LD, self.variables[i][1], Addressing.MEM)
                if len(expression) == 1:
                    break
                self.create_operation(Opcode.PUSH)
            else:
                self.create_operation(Opcode.POP)
                self.create_operation(Opcode.LD, 0, Addressing.SP)
                match i:
                    case "+":
                        self.create_operation(Opcode.ADD, -1, Addressing.SP)
                    case "-":
                        self.create_operation(Opcode.SUB, -1, Addressing.SP)
                    case "*":
                        self.create_operation(Opcode.MUL, -1, Addressing.SP)
                    case "/":
                        self.create_operation(Opcode.DIV, -1, Addressing.SP)
                    case "%":
                        self.create_operation(Opcode.MOD, -1, Addressing.SP)
                    case _:
                        raise MathExpressionException(
                            "Неизвестный знак выражения: " + i
                        )
                self.create_operation(Opcode.ST, 0, Addressing.SP)
        if len(expression) != 1:
            self.create_operation(Opcode.POP)
        return expression

    def create_comparison(self, left: str, right: str):
        right_math = self.create_math(right)
        self.create_operation(Opcode.PUSH)
        left_math = self.create_math(left)
        self.create_operation(Opcode.SUB, 0, Addressing.SP)
        self.create_operation(Opcode.ST, 0, Addressing.SP)
        self.create_operation(Opcode.POP)
        return left_math, right_math

    def find_end_of_block(self, code: list[str], start_position: int) -> int:
        i = start_position + 1
        count = 1
        while i < len(code):
            if code[i] == "}":
                count -= 1
                if count == 0:
                    return i
            if code[i] == "{":
                count += 1
            i += 1
        raise TranslateException("Не хватает закрывающей фигурной скобки для блока")

    def add_print_char(self, src: chr):
        self.create_operation(Opcode.LD, ord(src), Addressing.DIR)
        self.create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)

    def add_print_string(self, src: str):
        src = src[1:-1]
        for i in src:
            self.add_print_char(i)

    def add_print_pointer(self, address: int):  # Address - адрес pointer'a
        # self.create_operation(Opcode.ST, self.current_free_data_address, Addressing.MEM)
        self.create_operation(Opcode.LD, address, Addressing.MEM)
        self.create_operation(Opcode.PUSH)

        index_to_jump = self.result[-1].address + 1
        self.create_operation(Opcode.LD, address, Addressing.IND_MEM)

        self.create_operation(Opcode.JZ, self.current_instruction_address + 6)
        self.create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)
        self.create_operation(Opcode.LD, address, Addressing.MEM)
        self.create_operation(Opcode.INC)
        self.create_operation(Opcode.ST, address, Addressing.MEM)
        self.create_operation(Opcode.JMP, index_to_jump)
        self.create_operation(Opcode.POP)
        self.create_operation(Opcode.ST, address, Addressing.MEM)

    def add_print_number(self):  # Число уже находится в аккумуляторе
        self.create_operation(Opcode.PUSH)
        self.create_operation(Opcode.LD, self.current_free_data_address, Addressing.MEM)
        self.create_operation(Opcode.PUSH)
        self.create_operation(
            Opcode.LD, self.current_free_data_address + 1, Addressing.MEM
        )
        self.create_operation(Opcode.PUSH)
        self.create_operation(Opcode.LD, 2, Addressing.SP)
        self.create_operation(
            Opcode.ST, self.current_free_data_address + 1, Addressing.MEM
        )
        self.create_operation(Opcode.JA, self.current_instruction_address + 2)
        self.create_operation(Opcode.NEG)
        self.create_operation(Opcode.ST, self.current_free_data_address, Addressing.MEM)
        self.create_operation(Opcode.LD, 0, Addressing.DIR)
        self.create_operation(Opcode.PUSH)
        self.create_operation(Opcode.LD, self.current_free_data_address, Addressing.MEM)
        index_to_jump = self.result[-1].address + 1
        self.create_operation(Opcode.MOD, 10, Addressing.DIR)
        self.create_operation(Opcode.ADD, 48, Addressing.DIR)
        self.create_operation(Opcode.PUSH)
        self.create_operation(Opcode.LD, self.current_free_data_address, Addressing.MEM)
        self.create_operation(Opcode.DIV, 10, Addressing.DIR)
        self.create_operation(Opcode.JZ, self.current_instruction_address + 3)
        self.create_operation(Opcode.ST, self.current_free_data_address, Addressing.MEM)
        self.create_operation(Opcode.JMP, index_to_jump)
        self.create_operation(
            Opcode.LD, self.current_free_data_address + 1, Addressing.MEM
        )
        self.create_operation(Opcode.JAZ, self.current_instruction_address + 3)
        self.create_operation(Opcode.LD, 45, Addressing.DIR)
        self.create_operation(Opcode.PUSH)
        # После того как число оказалось в стеке, выводим его
        index_to_jump = self.result[-1].address + 1
        self.create_operation(Opcode.POP)
        self.create_operation(Opcode.JZ, self.current_instruction_address + 3)
        self.create_operation(Opcode.ST, IO_OUT_MEM, Addressing.MEM)
        self.create_operation(Opcode.JMP, index_to_jump)
        self.create_operation(Opcode.POP)
        self.create_operation(
            Opcode.ST, self.current_free_data_address + 1, Addressing.MEM
        )
        self.create_operation(Opcode.POP)
        self.create_operation(Opcode.ST, self.current_free_data_address, Addressing.MEM)
        self.create_operation(Opcode.POP)

    def add_read_pointer(self, variable_address: int):
        self.create_operation(Opcode.LD, variable_address, Addressing.MEM)
        self.create_operation(Opcode.PUSH)
        index_to_jump = self.result[-1].address + 1

        self.create_operation(Opcode.LD, IO_IN_MEM, Addressing.MEM)
        self.create_operation(Opcode.ST, variable_address, Addressing.IND_MEM)
        self.create_operation(Opcode.JZ, self.current_instruction_address + 5)
        self.create_operation(Opcode.LD, variable_address, Addressing.MEM)
        self.create_operation(Opcode.INC)
        self.create_operation(Opcode.ST, variable_address, Addressing.MEM)
        self.create_operation(Opcode.JMP, index_to_jump)

        self.create_operation(Opcode.POP)
        self.create_operation(Opcode.ST, variable_address, Addressing.MEM)

    def create_reverse_sign(self, comparison_sign: str):
        current_command: Opcode = Opcode.JZ
        match comparison_sign:
            case "==":
                current_command = Opcode.JNZ
            case "!=":
                current_command = Opcode.JZ
            case ">":
                current_command = Opcode.JBZ
            case "<":
                current_command = Opcode.JAZ
            case ">=":
                current_command = Opcode.JB
            case "<=":
                current_command = Opcode.JA
        self.create_operation(current_command)

    def create_code(self, code: list[str]):
        ast = list()
        i = 0
        while i < len(code):
            current_token = code[i]
            match self.recognise_token(current_token):
                case TokenType.CREATE_NEW_VAR:
                    var_type = current_token.split()[0]
                    var_name = current_token.split()[1].split("=")[0].strip()
                    if var_name in self.variables:
                        raise VarException("Переменная " + var_name + " уже существует")
                    operand = None
                    if "=" in current_token:
                        operand = current_token.split("=")[1].strip()
                        if operand == "":
                            raise VarException(
                                current_token + ": ожидалась инициализация"
                            )
                    self.variables[var_name] = (
                        DataType.CHAR if var_type == "char" else DataType.INT,
                        self.current_free_data_address,
                    )
                    if var_type == "int":
                        if operand is None:
                            self.create_operation_data(
                                self.current_free_data_address, 0
                            )
                            self.current_free_data_address += 1
                        elif re.fullmatch(r"[+-]?[0-9]+", operand):
                            operand = int(operand)
                            self.create_operation_data(
                                self.current_free_data_address, operand
                            )
                            self.current_free_data_address += 1
                        else:
                            self.create_operation_data(
                                self.current_free_data_address, 0
                            )
                            operand = self.create_math(operand)
                            self.create_operation(
                                Opcode.ST,
                                self.current_free_data_address,
                                Addressing.MEM,
                            )
                            self.current_free_data_address += 1
                    elif var_type == "char":
                        if operand is None:
                            local_operand = 0
                        elif not operand.isdigit() and not is_char(operand):
                            raise VarException(
                                "Инициализировать char можно только числом или символом: "
                                + current_token
                            )
                        elif is_char(operand):
                            local_operand = ord(operand[1])
                        else:
                            if int(operand) < 0 or int(operand) > 255:
                                raise VarException(
                                    "В char нельзя сохранить число больше 255: "
                                    + current_token
                                )
                            local_operand = operand
                        self.create_operation_data(
                            self.current_free_data_address, local_operand
                        )
                        self.current_free_data_address += 1
                    ast.append(
                        AstNode(
                            "Variable definition",
                            [
                                AstExpression(name="type", body=var_type),
                                AstExpression(name="name", body=var_name),
                                AstExpression("value", str(operand)),
                            ],
                        )
                    )
                case TokenType.CREATE_NEW_POINTER:
                    var_type = current_token.split("[")[0]
                    if var_type != "char":
                        raise VarException(
                            "В языке поддерживаются только char pointer: "
                            + current_token
                        )
                    var_name = current_token.split("]")[1].split("=")[0].strip()
                    if var_name in self.variables:
                        raise VarException("Переменная " + var_name + " уже существует")
                    if current_token[current_token.find("[") + 1] == "]":
                        var_capacity = -1
                    else:
                        var_capacity = int(
                            current_token[
                                current_token.find("[") + 1 : current_token.find("]")
                            ]
                        )
                    if var_capacity == 0:
                        raise VarException(
                            "Нельзя проинициализировать массив из 0 элементов: "
                            + current_token
                        )
                    operand = None
                    if "=" in current_token:
                        operand = current_token[current_token.find("=") + 1 :].strip()
                        if operand == "":
                            raise VarException(
                                current_token + ": ожидалась инициализация"
                            )
                    self.variables[var_name] = (
                        DataType.POINTER,
                        self.current_free_data_address,
                    )
                    if var_capacity == -1 and operand is None:
                        raise InvalidToken("Неизвестный токен: " + current_token)
                    if var_capacity == -1:
                        if self.recognise_token(operand) != TokenType.STRING:
                            raise InvalidToken("Неизвестный токен: " + current_token)
                        # self.create_operation(
                        #    Opcode.LD,
                        #    self.current_free_data_address + 1,
                        #    Addressing.DIR,
                        # )
                        # self.create_operation(
                        #    Opcode.ST, self.current_free_data_address, Addressing.MEM
                        # )
                        self.create_operation_data(
                            self.current_free_data_address,
                            self.current_free_data_address + 1,
                        )
                        self.current_free_data_address += 1
                        operand = operand[1:-1]
                        for char in operand:
                            self.create_operation_data(
                                self.current_free_data_address, ord(char)
                            )
                            self.current_free_data_address += 1
                        self.create_operation_data(self.current_free_data_address, 0)
                        self.current_free_data_address += 1
                    else:
                        if (
                            operand is not None
                            and self.recognise_token(operand) != TokenType.STRING
                        ):
                            raise InvalidToken("Неизвестный токен: " + current_token)
                        # self.create_operation(
                        #    Opcode.LD,
                        #    self.current_free_data_address + 1,
                        #    Addressing.DIR,
                        # )
                        # self.create_operation(
                        #    Opcode.ST, self.current_free_data_address, Addressing.MEM
                        # )
                        # self.current_free_data_address += 1
                        self.create_operation_data(
                            self.current_free_data_address,
                            self.current_free_data_address + 1,
                        )
                        self.current_free_data_address += 1
                        if operand is not None:
                            local_free_data_address = self.current_free_data_address
                            operand = operand[1:-1]
                            count = 0
                            for char in operand:
                                if count >= min(var_capacity - 1, len(operand)):
                                    break
                                count += 1
                                self.create_operation_data(
                                    local_free_data_address, ord(char)
                                )
                                local_free_data_address += 1
                                # self.create_operation(
                                #    Opcode.LD, ord(char), Addressing.DIR
                                # )
                                # self.create_operation(
                                #    Opcode.ST, local_free_data_address, Addressing.MEM
                                # )
                                # local_free_data_address += 1
                            # self.create_operation(Opcode.LD, 0, Addressing.DIR)
                            # self.create_operation(
                            #    Opcode.ST, local_free_data_address, Addressing.MEM
                            # )
                            self.create_operation_data(local_free_data_address, 0)

                        self.current_free_data_address += var_capacity
                    ast.append(
                        AstNode(
                            "Pointer Definition",
                            [
                                AstExpression(name="type", body=var_type),
                                AstExpression(name="name", body=var_name),
                                AstExpression("value", '"' + str(operand) + '"'),
                                AstExpression("capacity", str(var_capacity)),
                            ],
                        )
                    )
                case TokenType.UPDATE_VAR:
                    var_name, operand = (
                        current_token.split("=")[0].strip(),
                        current_token.split("=")[1].strip(),
                    )
                    if var_name not in self.variables:
                        raise VarException(
                            "Переменной "
                            + var_name
                            + " не существует: "
                            + current_token
                        )
                    if self.variables[var_name][0] == DataType.POINTER:
                        raise VarException(
                            "Нельзя изменить указатель: " + current_token
                        )
                    if self.variables[var_name][0] == DataType.CHAR:
                        if is_char(operand):
                            self.create_operation(
                                Opcode.LD, ord(operand[1]), Addressing.DIR
                            )
                        elif operand.isdigit() and 0 <= int(operand) <= 255:
                            self.create_operation(Opcode.LD, operand, Addressing.DIR)
                        else:
                            raise VarException(
                                "Инициализировать char можно только числом от 0 до 255 или символом: "
                                + current_token
                            )
                    else:
                        operand = self.create_math(operand)
                    self.create_operation(
                        Opcode.ST, self.variables[var_name][1], Addressing.MEM
                    )
                    ast.append(
                        AstNode(
                            "Variable update",
                            [
                                AstExpression(name="name", body=var_name),
                                AstExpression("value", str(operand)),
                            ],
                        )
                    )
                case TokenType.IF:
                    if (
                        self.recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN
                        or self.recognise_token(code[i + 2]) != TokenType.COMPARISON
                        or self.recognise_token(code[i + 3])
                        != TokenType.QUOTE_ROUND_CLOSE
                        or self.recognise_token(code[i + 4])
                        != TokenType.QUOTE_FIGURE_OPEN
                    ):
                        raise TranslateException(
                            "Неправильный формат if выражения: " + str(code[i : i + 4])
                        )
                    start_of_block, end_of_block = (
                        i + 4,
                        self.find_end_of_block(code, i + 4),
                    )
                    left, comparison_sign, right = re.split(
                        r"(!=|==|>=|<=|>|<)", code[i + 2]
                    )
                    left, right = self.create_comparison(left, right)
                    comparison_index = self.result[-1].address + 1
                    self.create_reverse_sign(comparison_sign)
                    if_ast = self.create_code(code[start_of_block + 1 : end_of_block])
                    self.result[
                        comparison_index - self.result[0].address
                    ].operand = self.current_instruction_address
                    i = end_of_block
                    ast.append(
                        AstNode(
                            "if statement",
                            [
                                AstNode(
                                    "condition",
                                    [
                                        AstExpression("left", str(left)),
                                        AstExpression("right", str(right)),
                                        AstExpression("sign", comparison_sign),
                                    ],
                                ),
                                AstNode("body", if_ast),
                            ],
                        )
                    )
                case TokenType.WHILE:
                    if (
                        self.recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN
                        or self.recognise_token(code[i + 2]) != TokenType.COMPARISON
                        or self.recognise_token(code[i + 3])
                        != TokenType.QUOTE_ROUND_CLOSE
                        or self.recognise_token(code[i + 4])
                        != TokenType.QUOTE_FIGURE_OPEN
                    ):
                        raise TranslateException(
                            "Неправильный формат while выражения: "
                            + str(code[i : i + 4])
                        )
                    start_of_block, end_of_block = (
                        i + 4,
                        self.find_end_of_block(code, i + 4),
                    )
                    left, comparison_sign, right = re.split(
                        r"(==|>=|<=|>|<)", code[i + 2]
                    )
                    while_start = self.current_instruction_address
                    left, right = self.create_comparison(left, right)
                    comparison_index = self.result[-1].address + 1
                    self.create_reverse_sign(comparison_sign)
                    while_ast = self.create_code(
                        code[start_of_block + 1 : end_of_block]
                    )
                    self.result[comparison_index - self.result[0].address].operand = (
                        self.current_instruction_address + 1
                    )
                    self.create_operation(Opcode.JMP, while_start)
                    i = end_of_block
                    ast.append(
                        AstNode(
                            "while statement",
                            [
                                AstNode(
                                    "condition",
                                    [
                                        AstExpression("left", str(left)),
                                        AstExpression("right", str(right)),
                                        AstExpression("sign", comparison_sign),
                                    ],
                                ),
                                AstNode("body", while_ast),
                            ],
                        )
                    )

                case TokenType.PRINT:
                    para = code[i + 2]
                    if (
                        self.recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN
                        or self.recognise_token(code[i + 3])
                        != TokenType.QUOTE_ROUND_CLOSE
                    ):
                        raise TranslateException(
                            "Неправильный формат: " + current_token
                        )
                    match self.recognise_token(code[i + 2]):
                        case TokenType.STRING:
                            self.add_print_string(code[i + 2])
                        case TokenType.CHAR:
                            self.add_print_char(code[i + 2][1])
                        case TokenType.VAR_VALUE:
                            if code[i + 2] not in self.variables:
                                raise VarException(
                                    "Переменной не существует: " + code[i + 2]
                                )
                            match self.variables[code[i + 2]][0]:
                                case DataType.CHAR:
                                    self.create_operation(
                                        Opcode.LD,
                                        self.variables[code[i + 2]][1],
                                        Addressing.MEM,
                                    )
                                    self.create_operation(
                                        Opcode.ST, IO_OUT_MEM, Addressing.MEM
                                    )
                                case DataType.INT:
                                    self.create_operation(
                                        Opcode.LD,
                                        self.variables[code[i + 2]][1],
                                        Addressing.MEM,
                                    )
                                    self.add_print_number()
                                case DataType.POINTER:
                                    self.add_print_pointer(
                                        self.variables[code[i + 2]][1]
                                    )
                        case _:
                            para = self.create_math(code[i + 2])
                            self.add_print_number()
                    ast.append(AstNode("IO call", [AstExpression("print", para)]))
                    i += 3
                case TokenType.READ:
                    if (
                        self.recognise_token(code[i + 1]) != TokenType.QUOTE_ROUND_OPEN
                        or self.recognise_token(code[i + 3])
                        != TokenType.QUOTE_ROUND_CLOSE
                        or self.recognise_token(code[i + 2]) != TokenType.VAR_VALUE
                    ):
                        raise TranslateException(
                            "Неправильный формат: " + current_token
                        )
                    var_name = code[i + 2]
                    if var_name not in self.variables:
                        raise VarException("Переменной не существует: " + code[i + 2])
                    match self.variables[var_name][0]:
                        case DataType.CHAR:
                            self.create_operation(Opcode.LD, IO_IN_MEM, Addressing.MEM)
                            self.create_operation(
                                Opcode.ST, self.variables[var_name][1], Addressing.MEM
                            )
                        case DataType.POINTER:
                            self.add_read_pointer(self.variables[var_name][1])
                        case _:
                            raise VarException(
                                "Считать можно либо в символ, либо в указатель: "
                                + current_token
                            )
                    ast.append(AstNode("IO call", [AstExpression("read", code[i + 2])]))
                    i += 3
                case _:
                    raise TranslateException("Неизвестный токен: " + current_token)
            i += 1
        return ast

    def create_operation(self, opcode, operand=None, addressing=None):
        self.result.append(
            Instruction(self.current_instruction_address, opcode, operand, addressing)
        )
        self.current_instruction_address += 1

    def create_operation_data(self, address: int, operand=None, addressing=None):
        self.result_data.append(Instruction(address, Opcode.WORD, operand, addressing))

    def translate(self, src: str) -> tuple[list[Instruction], list[AstNode]]:
        self.key_words = ["while", "if", "read", "print"]
        self.variables: dict[str, tuple[DataType, int]] = dict()
        self.current_free_data_address = 10
        self.current_instruction_address = 200
        self.result: list[Instruction] = list()

        if src.count('"') % 2 != 0:
            raise TranslateException("Неправильно расставлены кавычки для строк")
        code = []
        current = ""
        in_string = False
        for char in src:
            if char == ";" and not in_string:
                code.append(current)
                current = ""
                continue
            if (char == "{" or char == "}") and not in_string:
                code.append(current)
                code.append(char)
                current = ""
                continue
            elif char == '"':
                in_string = not in_string
            current += char
        code = [temp.strip() for temp in code if temp.strip() != ""]
        code_modified = []
        for temp in code:
            modified = False
            for key_word in self.key_words:
                n = len(key_word)
                if temp[:n] != key_word:
                    continue
                if "(" not in temp or temp[-1] != ")":
                    raise InvalidToken("Ошибка в строке: " + temp)
                code_modified.extend(
                    [key_word, "(", temp[temp.find("(") + 1 : -1].strip(), ")"]
                )
                modified = True
            if not modified:
                code_modified.append(temp)
        code = code_modified.copy()
        # Код разбит на лексемы
        # print(code)

        result_ast = self.create_code(code)
        self.create_operation(Opcode.HLT)
        self.result.extend(self.result_data)
        return self.result, result_ast


def main(source: str, target: str):
    with open(source, "r", encoding="utf-8") as f:
        source = f.read()
    source = re.sub(r"#.*\n", "", source)
    translator = Translator()
    code, string_ast = translator.translate(source)
    write_code(target, code)
    print("Файл транслирован, полученное AST:")
    for i in string_ast:
        print(i)


if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "Wrong arguments: translator.py <input_file> <target_file>"
    main(sys.argv[1], sys.argv[2])
