from src import translator

import pytest

from src.exceptions import VarException, InvalidToken
from src.translator import Translator


class TestTranslator:

    def test_whitespaces(self):
        translator = Translator()
        input = """
                     char[200] name;
            print(   "Enter your name:"    );
            char new_line =    10;
              print(new_line)    ;
            read(     name);
            print("Hello, "  );
            print(name);
            """
        translator.translate(input)

    def test1(self):
        translator = Translator()
        input = "int a = ;"
        pytest.raises(VarException, translator.translate, input)

    def test2(self):
        translator = Translator()
        input = "int a = 0; if (a > 3) {}"
        translator.translate(input)

    def test3(self):
        translator = Translator()
        input = "int a = 0; if a > 3) {}"
        pytest.raises(InvalidToken, translator.translate, input)

    def test4(self):
        translator = Translator()
        input = "int a = 0; if (a > 3) { print(b) }"
        pytest.raises(VarException, translator.translate, input)
