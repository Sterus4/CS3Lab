import pytest

from src.exceptions import VarException, InvalidToken
from src.translator import Translator


class TestTranslator:
    translator = Translator()

    def test_whitespaces(self):
        input = """
                     char[200] name;
            print(   "Enter your name:"    );
            char     new_line =    10;
              print(  new_line )    ;
            read(     name);
            print("Hello, "  );
            print ( name );
            """
        self.translator.translate(input)

    def test1(self):
        input = "int a = ;"
        pytest.raises(VarException, self.translator.translate, input)

    def test2(self):
        input = "int a = 0; if (a > 3) {}"
        self.translator.translate(input)

    def test3(self):
        input = "int a = 0; if a > 3) {}"
        pytest.raises(InvalidToken, self.translator.translate, input)

    def test4(self):
        input = "int a = 0; if (a > 3) { print(b) }"
        pytest.raises(VarException, self.translator.translate, input)
