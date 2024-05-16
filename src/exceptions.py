class TranslateException(Exception):
    """Выбрасывается, если обнаружена ошибка в коде во время трансляции"""


class UnknownToken(Exception):
    """Выбрасывается, если обнаружен неизвестный токен во время трансляции"""


class InvalidToken(Exception):
    """Выбрасывается, если обнаруженный токен стоит не на своем месте"""


class VarException(Exception):
    """Выбрасывается, если обнаружена ошибка с переменной"""


class MathExpressionException(Exception):
    """Выбрасывается, если обнаружена ошибка в математическом выражении"""


class AluException(Exception):
    """Выбрасывается, если обнаружена ошибка в АЛУ"""
