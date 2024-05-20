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
* Типы данных `char` и `int` по-умолчанию инициализируются нолями
* Указатели существуют только для `char`. Указатели являются неизменяемыми.
Их необходимо инициализировать при объявлении (либо оставить как буфер для чтения данных)
* Существует два способа считывания данных:
  * Считывание одного символа в переменную типа `char`
  * Считывание строки в переменную типа `char[]`

Статическая типизация, существует 3 типа данных:
* `int` - целое число
* `char` - символ - целое число от 0 до 128
* `char[size]` - массив символов, строка

### BNF

```bnf
<program> ::= <statement_list>

<statement_list> ::= <statement> | <statement> <statement_list>

<statement> ::= <declaration> 
    | <assignment> 
    | <while_loop> 
    | <if_statement> 
    | <print_statement>
    | <read_statement>

<declaration> ::= "int" <identifier> "=" <expression> ";"
    | "char" <identifier> "=" <char> ";"
    | "char[]" <identifier> "=" <string> ";"
    | "char[number]" <identifier> "=" <string> ";"
    | "char[number]" <identifier> ";"
   
<assignment> ::= <identifier> "=" <expression> ";"
    | <identifier> "=" <identifier> ";"
   
<while_loop> ::= "while" "(" <condition> ")" "{" <statement_list> "}"

<if_statement> ::= "if" "(" <condition> ")" "{" <statement_list> "}"

<print_statement> ::= "print" "(" <expression> | <identifier> ")" ";"

<read_statement> ::= "read" "(" <identifier> ")" ";"

<condition> ::= <expression> <comparison_op> <expression>

<expression> ::= <factor> 
    | <expression> "+" <expression> | 
    | <expression> "-" <expression>
    | <expression> "*" <expression>
    | <expression> "/" <expression>
    | <expression> "%" <expression>
    | "(" <expression> ")"


<factor> ::= <number> | <identifier>

<comparison_op> ::= "<" | "<=" | ">" | ">=" | "==" | "!="

<identifier> ::= <letter> {<letter> | <digit>}

<number> ::= <digit> {<digit>}

<string> ::= "\"" {<character>} "\""

<char> ::= "\'" <character> "\'"

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<letter> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" |
             "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"

<character> ::= <letter> | <digit> | <special_char>

<special_char> ::= " " | "," | "." | "!" | "?" | ":" | ";" | "'" | "\""
```
