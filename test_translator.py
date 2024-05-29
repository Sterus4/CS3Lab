import pytest

from src.exceptions import VarException, InvalidToken, MathExpressionException
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
        instructions, ast = self.translator.translate(input)
        ast = str(ast)
        assert (
            ast
            == """Program : {
	pointer Definition : {
		type : char;
		name : name;
		value : "None";
		capacity : 200;
	}
	IO call : {
		print : "Enter your name:";
	}
	variable definition : {
		type : char;
		name : new_line;
		value : 10;
	}
	IO call : {
		print : new_line;
	}
	IO call : {
		read : name;
	}
	IO call : {
		print : "Hello, ";
	}
	IO call : {
		print : name;
	}
}"""
        )

    def test1(self):
        input = "int a = ;"
        pytest.raises(VarException, self.translator.translate, input)

    def test2(self):
        input = "int a = 0; if (a > 3) {}"
        ins, ast = self.translator.translate(input)
        ast = str(ast)
        assert (
            ast
            == """Program : {
	variable definition : {
		type : int;
		name : a;
		value : 0;
	}
	if statement : {
		condition : {
			left : ['a'];
			right : ['3'];
			sign : >;
		}
		body : {
		}
	}
}"""
        )

    def test3(self):
        input = "int a = 0; if a > 3) {}"
        pytest.raises(InvalidToken, self.translator.translate, input)

    def test4(self):
        input = "int a = 0; if (a > 3) { print(b) }"
        pytest.raises(VarException, self.translator.translate, input)

    def test_math(self):
        input = "int a = 231 - ;"
        pytest.raises(MathExpressionException, self.translator.translate, input)
