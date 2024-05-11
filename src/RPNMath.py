import re

from exceptions import MathExpressionException


def toRPN(s: list) -> list:
    priority = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "(": -1, ")": 0}
    right_associative_operators = {"^"}
    li = []
    ops = ["+", "-", "*", "/", "(", ")", "%"]
    result = list()
    for i in s:
        if i in ops:
            if i == "(":
                li.append(i)
            else:
                while li and (
                        priority[li[-1]] > priority[i] or
                        priority[li[-1]] == priority[i] and i not in right_associative_operators
                ):
                    result.append(li.pop())
                if i == ')':
                    li.pop()
                else:
                    li.append(i)
        else:
            result.append(i)
    while li:
        result.append(li.pop())

    return result


def check_quotes(src: str) -> bool:
    i = 0
    for c in src:
        if c == '(':
            i += 1
        elif c == ')':
            i -= 1
        if i < 0:
            return False
    if i != 0:
        return False
    return True


def check_equation(src: list) -> bool:
    if len(src) == 0:
        return True
    var_count = 0
    ops = ["+", "-", "*", "/", "(", ")", "%"]
    for temp in src:
        if temp not in ops:
            var_count += 1
        else:
            if var_count < 2:
                return False
            var_count -= 1
    if var_count != 1:
        return False
    return True


def create_rpn_expression(src: str) -> list:
    src_copy = src
    if not re.fullmatch(r'[\s()0123456789\w*/%+-]+', src):
        raise MathExpressionException("Неизвестные символы в выражении: " + src)
    if not check_quotes(src):
        raise MathExpressionException("В выражении неправильно расставлены скобки: " + src)
    src = re.sub(r'\+', ' + ', src)
    src = re.sub(r'\*', ' * ', src)
    src = re.sub(r'-', ' - ', src)
    src = re.sub(r'/', ' / ', src)
    src = re.sub(r'\(', ' ( ', src)
    src = re.sub(r'\)', ' ) ', src)
    src = re.split(r'\s+', src)
    src = [i for i in src if i != '']
    src_copy = []
    for i in range(len(src)):
        if src[i] == '-':
            if i == 0 or src[i - 1] == '(':
                src_copy.append('0')
        src_copy.append(src[i])
    src = src_copy.copy()
    expression = toRPN(src)
    print(expression)

    if not check_equation(expression):
        raise MathExpressionException("Неверное математическое выражение: " + src)
    return expression
