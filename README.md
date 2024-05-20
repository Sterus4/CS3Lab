# Лабораторная работа #3 АК
***
Выполнил Нигаматуллин Степан P3234

Вариант: `alg -> asm | acc | harv | hw | instr | struct | stream | mem | cstr | prob2 | cache`

Базовый

## Язык программирования
***
* Алгоритмический язык программирования, синтаксис совпадает с синтаксисом С.
* Каждое выражение должно заканчиваться знаком `;`. 
* Поддерживаются математические выражения.
* Стратегия вычисления: последовательная
* Все переменные объявляются в глобальной зоне видимости

Статическая типизация, существует 3 типа данных:
* `int` - целое число
* `char` - символ - целое число от 0 до 128
* `char[size]` - массив символов, строка

### BNF

```bnf
<program> ::= <declarations> <statements>

<declarations> ::= <declaration> | <declaration> <declarations>
<declaration> ::= <type> <identifier> "=" <expression> ";" | <type> <identifier> "[" <number> "]" ";" | <type> <identifier> "[" "]" "=" <string> ";"

<type> ::= "int" | "char" | "char[]"
<identifier> ::= <letter> | <letter> <identifier>
<letter> ::= "a" | "b" | "c" | ... | "z" | "A" | "B" | "C" | ... | "Z"
<number> ::= <digit> | <digit> <number>
<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<string> ::= "\"" <chars> "\""
<chars> ::= <char> | <char> <chars>
<char> ::= <letter> | <digit> | " " | "!"

<statements> ::= <statement> | <statement> <statements>
<statement> ::= <assignment> ";" | <function_call> ";" | <while_loop> | <if_statement>

<assignment> ::= <identifier> "=" <expression>
<function_call> ::= <identifier> "(" <arguments> ")"
<arguments> ::= <argument> | <argument> "," <arguments>
<argument> ::= <expression> | <string>

<expression> ::= <term> | <term> "+" <expression> | <term> "*" <expression>
<term> ::= <factor> | <factor> "%" <term>
<factor> ::= <identifier> | <number> | "(" <expression> ")"

<while_loop> ::= "while" "(" <condition> ")" "{" <statements> "}"
<if_statement> ::= "if" "(" <condition> ")" "{" <statements> "}"

<condition> ::= <expression> <relational_operator> <expression>
<relational_operator> ::= "<" | ">" | "<=" | ">=" | "==" | "!="
```
