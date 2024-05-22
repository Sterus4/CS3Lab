# Лабораторная работа #3 АК
***
Выполнил Нигаматуллин Степан P3234

Вариант: `alg -> asm | acc | harv | hw | instr | struct | stream | mem | cstr | prob2 | cache`

Базовый

## Язык программирования
***
* Алгоритмический язык программирования, синтаксис совпадает с синтаксисом С.
* Все символы от '#' до конца строки будут расценены как комментарии
* Каждое выражение должно заканчиваться знаком `;`. 
* Поддерживаются математические выражения.
* Стратегия вычисления: последовательная
* Все переменные объявляются в глобальной зоне видимости
* Типы данных `char` и `int` по-умолчанию инициализируются нолями
* Указатели существуют только для `char`. Указатели являются неизменяемыми.
Их необходимо инициализировать при объявлении (либо оставить как буфер для чтения данных)

Статическая типизация, существует 3 типа данных:
* `int` - целое число
* `char` - символ - целое число от 0 до 128
* `char[size]` - массив символов, строка

### BNF

```BNF
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

<print_statement> ::= "print" "(" <expression> | <identifier> | <string> | <character>")" ";"

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
* Вызов функций, кроме встроенных, не предусмотрен (ну в целом и не необходим) 
* Функции read и print перегружены:
  * print:
    * Выводит результат математического выражения
    * Выводит переменную типа `char[]` как строку
    * Выводит данный символ
  * read:
    * Считывание одного символа в переменную типа `char`
    * Считывание строки в переменную типа `char[]`
* Цикл `while` и условный переход `if` в качестве аргумента принимают `condition`
  * `condition` проверяет на равенство или неравенство два математических выражения, поддерживаемые сравнения:
    * `==, !=, >, <, <=, >=`
  * `break` или `else` не предусмотрены
* Поддерживаются математические выражения, поддерживаемые операции:
  * `+, -, *, /, %`
  * Любые правильные скобочные последовательности
* Литералы:
  * Целые числа
  * Строки `"<string>"`
  * Символы `'<character>'`

## Организация памяти

Модель памяти: `harv` - Гарвардская архитектура

### Память команд

| Address           | Instruction  |
|-------------------|--------------|
| start_address     | instruction1 |
| start_address + 1 | instruction2 |
| ...               |
| N                 | halt         |


* Все команды хранятся последовательно
* Адрес начала выставлен в трансляторе, при желании его можно поменять
* В конец всегда добавляется инструкция `hlt`

### Память данных

Память Данных разделена на 3 секции:
```
+---------+
|   IO    |
+---------+
|  Data   |
+---------+
|  Stack  |
+---------+
```
* `IO` - Адресное пространство, разделенное между памятью данных и внешними устройствам
  * Адрес 0 - Стандартный вывод
  * Адрес 1 - Стандартный ввод
* `Data` - Адресное пространство данных
  * Данные хранятся последовательно
  * `char[]` указатели хранятся в виде ссылок на первый `char` в конец каждой строки добавляется \0
* `Stack` - Адресное пространство стека. Для работы с ним существует регистр `sp`, указывающий на вершину стека

#### Математические выражения

Так как модель процессора построена вокруг использования `acc`, но необходимо было поддерживать математические выражения, было принято гениальное решение:
Каждое математическое выражение сначала будет приведено в обратную польскую нотацию, а затем посчитано с помощью стека.

У этого подхода есть довольно много плюсов, основной case вот такой:
Так как нет большого количества регистров общего назначения, чтобы посчитать выражение только в них, промежуточный результат все равно придется очень часто сохранять в память.
Чтобы не делать это в случайном месте, будем делать это в стеке, попутно вычисляя итоговое значение выражения

Так же стек используется для:
* Сохранения числа в виде последовательности символов при использовании функции `print` числа в стандартный поток вывода
* Сохранения адреса прочитанного символа при чтении в `char[]`



## Система команд

* Система команд построена вокруг аккумулятора `ACC`
* Операнд каждой команды, если он ей необходим - целое число
* Ввод вывод осуществляется штатными командами работы с памятью, через `ACC`
* Поток управления:
  * На момент Выборки команды, Регистр `IP` указывает на адрес следующей команды
  * Когда команда выбрана, `IP` увеличивается на 1
  * Поддерживаются команды ветвления

Существует 4 этапа исполнения команды:
* Цикл выборки инструкции
* Цикл выборки адреса (Если необходим)
* Цикл выборки операнда (Если необходим)
* Цикл исполнения

Для выборки адреса существует 4 вида адресации:

| Мнемоника | Описание                 | Операнд      | Схема                   |
|-----------|--------------------------|--------------|-------------------------|
| `DIR`     | прямая загрузка операнда | -            | DR <- operand           |
| `MEM`     | Абсолютная адресация     | Адрес        | DR <- mem(operand)      |
| `IND`     | Косвенная адресация      | Адрес адреса | DR <- mem(mem(operand)) |
| `SP`      | Адресация относительно   | Смещение     | DR <- mem(SP + operand) |


Существует 3 типа команд:
* Адресные
* Безадресные
* Команды ветвления
  * Адресация команд ветвления всегда абсолютная. Операнд - адрес инструкции.
  * Производят загрузку операнда в `IP` при выставленных флагах результата:
    * NF = ACC < 0
    * ZF = ACC == 0

### Адресные команды
```
| Мнемоника | Описание       |
|-----------|----------------|
| LD A      | ACC <- A       |
| ST A      | ACC -> mem(A)  |
| ADD A     | ACC <- ACC + A |
| SUB A     | ACC <- ACC - A |
| MUL A     | ACC <- ACC * A |
| DIV A     | ACC <- ACC / A |
| MOD A     | ACC <- ACC % A |
```
### Безадресные команды
```
| Мнемоника | Описание                      |
|-----------|-------------------------------|
| INC       | ACC <- ACC + 1                |
| NEG       | ACC <- -ACC                   |
| PUSH      | SP <- SP - 1 ; ACC -> mem(SP) |
| POP       | ACC <- mem(SP) ; SP <- SP + 1 |
```
### Команды ветвления
```
| Мнемоника | Условие перехода    |
|-----------|---------------------|
| JMP       | Безусловный переход |
| JNZ       | ZF = 0              |
| JZ        | ZF = 1              |
| JBZ       | ZF = 1 || NF = 1    |
| JB        | ZF = 0 && NF = 1    |
| JAZ       | ZF = 1 || NF = 0    |
| JA        | ZF = 0 && NF = 1    |
```
### Кодирование инструкций

Каждая инструкция представлена в виде Json объекта (по варианту)
* Пример адресной команды:
```json
{
  "address": 224, 
  "opcode": "sub",
  "operand": 14, 
  "addressing": "mem"
}
```

* Пример безадресной команды:
```json
{
  "address": 391, 
  "opcode": "neg", 
  "operand": null, 
  "addressing": null
}
```

* Пример команды ветвления:
```json
{
  "address": 405, 
  "opcode": "ja",
  "operand": 408, 
  "addressing": null
}
```
Реализацию смотреть в [isa](src/isa.py)

## Транслятор

Реализован а [translator](src/translator.py)

Сценарий использования:
* `translator.py <input_file> <target_file>`, где: 
  * `<input_file>` - Код программы
  * `<target_file>` - Название файла для машинного кода

Трансляция происходит в несколько этапов:
* Удаление комментариев
* Разделение исходного кода на массив лексем (токенов)
* Определение типов токенов
* Для каждого токена:
  * Разделение его на составные части, если они имеются
  * Создание машинного кода токена

## Модель процессора

Модель реализована в [machine](src/machine.py), которая использует:
* [datapath](src/datapath.py)
* [control unit](src/control_unit.py)

### Datapath
![datapath](resources/datapath.svg)

### Control Unit

## Тестирование

В CI находятся две работы:
* Тестирование 
* Проверка форматирования и линтер

Для алгоритмов реализованы golden-тесты:
* [Hello world](golden/hello_world.yml)
* [Cat](golden/cat.yml)
* [Greet User](golden/greet_user.yml)
* [Prob2](golden/prob2.yml)

### Подробный разбор программы Prob2

Код программы:
```C
# Инициализируем изначальные переменные
int a = 1;
int b = 1;
int sum = 0;
int temp;

while (b < 4000000){ # Цикл до максимального значения ряда Фибоначчи
    if(b % 2 == 0){ # Если число четное, складываем его
        sum = sum + b;
    }

    temp = b;
    b = a + b;
    a = temp; # Считаем следующий член ряда
}
print("Сумма всех четных чисел Фибоначчи, которые меньше 4.000.000 = ");
print(sum); # Выводим результаты
```
Транслированный машинный код:

``` json
[{"address": 200, "opcode": "ld", "operand": "1", "addressing": "direct"},
{"address": 201, "opcode": "st", "operand": 10, "addressing": "mem"},
{"address": 202, "opcode": "ld", "operand": "1", "addressing": "direct"},
{"address": 203, "opcode": "st", "operand": 11, "addressing": "mem"},
{"address": 204, "opcode": "ld", "operand": "0", "addressing": "direct"},
{"address": 205, "opcode": "st", "operand": 12, "addressing": "mem"},
{"address": 206, "opcode": "ld", "operand": 0, "addressing": "direct"},
{"address": 207, "opcode": "st", "operand": 13, "addressing": "mem"},
{"address": 208, "opcode": "ld", "operand": "4000000", "addressing": "direct"},
{"address": 209, "opcode": "st", "operand": 14, "addressing": "mem"},
{"address": 210, "opcode": "ld", "operand": 11, "addressing": "mem"},
{"address": 211, "opcode": "sub", "operand": 14, "addressing": "mem"},
{"address": 212, "opcode": "jaz", "operand": 251, "addressing": null},
{"address": 213, "opcode": "ld", "operand": "0", "addressing": "direct"},
{"address": 214, "opcode": "st", "operand": 14, "addressing": "mem"},
{"address": 215, "opcode": "ld", "operand": 11, "addressing": "mem"},
{"address": 216, "opcode": "push", "operand": null, "addressing": null},
{"address": 217, "opcode": "ld", "operand": "2", "addressing": "direct"},
{"address": 218, "opcode": "push", "operand": null, "addressing": null},
{"address": 219, "opcode": "pop", "operand": null, "addressing": null},
{"address": 220, "opcode": "ld", "operand": 0, "addressing": "sp"},
{"address": 221, "opcode": "mod", "operand": -1, "addressing": "sp"},
{"address": 222, "opcode": "st", "operand": 0, "addressing": "sp"},
{"address": 223, "opcode": "pop", "operand": null, "addressing": null},
{"address": 224, "opcode": "sub", "operand": 14, "addressing": "mem"},
{"address": 225, "opcode": "jnz", "operand": 236, "addressing": null},
{"address": 226, "opcode": "ld", "operand": 12, "addressing": "mem"},
{"address": 227, "opcode": "push", "operand": null, "addressing": null},
{"address": 228, "opcode": "ld", "operand": 11, "addressing": "mem"},
{"address": 229, "opcode": "push", "operand": null, "addressing": null},
{"address": 230, "opcode": "pop", "operand": null, "addressing": null},
{"address": 231, "opcode": "ld", "operand": 0, "addressing": "sp"},
{"address": 232, "opcode": "add", "operand": -1, "addressing": "sp"},
{"address": 233, "opcode": "st", "operand": 0, "addressing": "sp"},
{"address": 234, "opcode": "pop", "operand": null, "addressing": null},
{"address": 235, "opcode": "st", "operand": 12, "addressing": "mem"},
{"address": 236, "opcode": "ld", "operand": 11, "addressing": "mem"},
{"address": 237, "opcode": "st", "operand": 13, "addressing": "mem"},
{"address": 238, "opcode": "ld", "operand": 10, "addressing": "mem"},
{"address": 239, "opcode": "push", "operand": null, "addressing": null},
{"address": 240, "opcode": "ld", "operand": 11, "addressing": "mem"},
{"address": 241, "opcode": "push", "operand": null, "addressing": null},
{"address": 242, "opcode": "pop", "operand": null, "addressing": null},
{"address": 243, "opcode": "ld", "operand": 0, "addressing": "sp"},
{"address": 244, "opcode": "add", "operand": -1, "addressing": "sp"},
{"address": 245, "opcode": "st", "operand": 0, "addressing": "sp"},
{"address": 246, "opcode": "pop", "operand": null, "addressing": null},
{"address": 247, "opcode": "st", "operand": 11, "addressing": "mem"},
{"address": 248, "opcode": "ld", "operand": 13, "addressing": "mem"},
{"address": 249, "opcode": "st", "operand": 10, "addressing": "mem"},
{"address": 250, "opcode": "jmp", "operand": 208, "addressing": null},
{"address": 251, "opcode": "ld", "operand": 1057, "addressing": "direct"},
{"address": 252, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 253, "opcode": "ld", "operand": 1091, "addressing": "direct"},
{"address": 254, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 255, "opcode": "ld", "operand": 1084, "addressing": "direct"},
{"address": 256, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 257, "opcode": "ld", "operand": 1084, "addressing": "direct"},
{"address": 258, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 259, "opcode": "ld", "operand": 1072, "addressing": "direct"},
{"address": 260, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 261, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 262, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 263, "opcode": "ld", "operand": 1074, "addressing": "direct"},
{"address": 264, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 265, "opcode": "ld", "operand": 1089, "addressing": "direct"},
{"address": 266, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 267, "opcode": "ld", "operand": 1077, "addressing": "direct"},
{"address": 268, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 269, "opcode": "ld", "operand": 1093, "addressing": "direct"},
{"address": 270, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 271, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 272, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 273, "opcode": "ld", "operand": 1095, "addressing": "direct"},
{"address": 274, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 275, "opcode": "ld", "operand": 1077, "addressing": "direct"},
{"address": 276, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 277, "opcode": "ld", "operand": 1090, "addressing": "direct"},
{"address": 278, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 279, "opcode": "ld", "operand": 1085, "addressing": "direct"},
{"address": 280, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 281, "opcode": "ld", "operand": 1099, "addressing": "direct"},
{"address": 282, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 283, "opcode": "ld", "operand": 1093, "addressing": "direct"},
{"address": 284, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 285, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 286, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 287, "opcode": "ld", "operand": 1095, "addressing": "direct"},
{"address": 288, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 289, "opcode": "ld", "operand": 1080, "addressing": "direct"},
{"address": 290, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 291, "opcode": "ld", "operand": 1089, "addressing": "direct"},
{"address": 292, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 293, "opcode": "ld", "operand": 1077, "addressing": "direct"},
{"address": 294, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 295, "opcode": "ld", "operand": 1083, "addressing": "direct"},
{"address": 296, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 297, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 298, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 299, "opcode": "ld", "operand": 1060, "addressing": "direct"},
{"address": 300, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 301, "opcode": "ld", "operand": 1080, "addressing": "direct"},
{"address": 302, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 303, "opcode": "ld", "operand": 1073, "addressing": "direct"},
{"address": 304, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 305, "opcode": "ld", "operand": 1086, "addressing": "direct"},
{"address": 306, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 307, "opcode": "ld", "operand": 1085, "addressing": "direct"},
{"address": 308, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 309, "opcode": "ld", "operand": 1072, "addressing": "direct"},
{"address": 310, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 311, "opcode": "ld", "operand": 1095, "addressing": "direct"},
{"address": 312, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 313, "opcode": "ld", "operand": 1095, "addressing": "direct"},
{"address": 314, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 315, "opcode": "ld", "operand": 1080, "addressing": "direct"},
{"address": 316, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 317, "opcode": "ld", "operand": 44, "addressing": "direct"},
{"address": 318, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 319, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 320, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 321, "opcode": "ld", "operand": 1082, "addressing": "direct"},
{"address": 322, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 323, "opcode": "ld", "operand": 1086, "addressing": "direct"},
{"address": 324, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 325, "opcode": "ld", "operand": 1090, "addressing": "direct"},
{"address": 326, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 327, "opcode": "ld", "operand": 1086, "addressing": "direct"},
{"address": 328, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 329, "opcode": "ld", "operand": 1088, "addressing": "direct"},
{"address": 330, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 331, "opcode": "ld", "operand": 1099, "addressing": "direct"},
{"address": 332, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 333, "opcode": "ld", "operand": 1077, "addressing": "direct"},
{"address": 334, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 335, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 336, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 337, "opcode": "ld", "operand": 1084, "addressing": "direct"},
{"address": 338, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 339, "opcode": "ld", "operand": 1077, "addressing": "direct"},
{"address": 340, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 341, "opcode": "ld", "operand": 1085, "addressing": "direct"},
{"address": 342, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 343, "opcode": "ld", "operand": 1100, "addressing": "direct"},
{"address": 344, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 345, "opcode": "ld", "operand": 1096, "addressing": "direct"},
{"address": 346, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 347, "opcode": "ld", "operand": 1077, "addressing": "direct"},
{"address": 348, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 349, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 350, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 351, "opcode": "ld", "operand": 52, "addressing": "direct"},
{"address": 352, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 353, "opcode": "ld", "operand": 46, "addressing": "direct"},
{"address": 354, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 355, "opcode": "ld", "operand": 48, "addressing": "direct"},
{"address": 356, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 357, "opcode": "ld", "operand": 48, "addressing": "direct"},
{"address": 358, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 359, "opcode": "ld", "operand": 48, "addressing": "direct"},
{"address": 360, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 361, "opcode": "ld", "operand": 46, "addressing": "direct"},
{"address": 362, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 363, "opcode": "ld", "operand": 48, "addressing": "direct"},
{"address": 364, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 365, "opcode": "ld", "operand": 48, "addressing": "direct"},
{"address": 366, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 367, "opcode": "ld", "operand": 48, "addressing": "direct"},
{"address": 368, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 369, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 370, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 371, "opcode": "ld", "operand": 61, "addressing": "direct"},
{"address": 372, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 373, "opcode": "ld", "operand": 32, "addressing": "direct"},
{"address": 374, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 375, "opcode": "ld", "operand": 12, "addressing": "mem"},
{"address": 376, "opcode": "st", "operand": 15, "addressing": "mem"},
{"address": 377, "opcode": "ja", "operand": 379, "addressing": null},
{"address": 378, "opcode": "neg", "operand": null, "addressing": null},
{"address": 379, "opcode": "st", "operand": 14, "addressing": "mem"},
{"address": 380, "opcode": "ld", "operand": 0, "addressing": "direct"},
{"address": 381, "opcode": "push", "operand": null, "addressing": null},
{"address": 382, "opcode": "ld", "operand": 14, "addressing": "mem"},
{"address": 383, "opcode": "mod", "operand": 10, "addressing": "direct"},
{"address": 384, "opcode": "add", "operand": 48, "addressing": "direct"},
{"address": 385, "opcode": "push", "operand": null, "addressing": null},
{"address": 386, "opcode": "ld", "operand": 14, "addressing": "mem"},
{"address": 387, "opcode": "div", "operand": 10, "addressing": "direct"},
{"address": 388, "opcode": "jz", "operand": 391, "addressing": null},
{"address": 389, "opcode": "st", "operand": 14, "addressing": "mem"},
{"address": 390, "opcode": "jmp", "operand": 383, "addressing": null},
{"address": 391, "opcode": "ld", "operand": 15, "addressing": "mem"},
{"address": 392, "opcode": "ja", "operand": 395, "addressing": null},
{"address": 393, "opcode": "ld", "operand": 45, "addressing": "direct"},
{"address": 394, "opcode": "push", "operand": null, "addressing": null},
{"address": 395, "opcode": "pop", "operand": null, "addressing": null},
{"address": 396, "opcode": "jz", "operand": 399, "addressing": null},
{"address": 397, "opcode": "st", "operand": 0, "addressing": "mem"},
{"address": 398, "opcode": "jmp", "operand": 395, "addressing": null},
{"address": 399, "opcode": "hlt", "operand": null, "addressing": null}]
```

Из-за acc модели процессора мы можем наблюдать большое количество операций `st` и `ld`

Лог работы процессора:
```
DEBUG    root:control_unit.py:43  Tick: 0, IP: 201, SP: 1000, DR: 0, AR: 0. Instruction: < ld -> 1 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 1, IP: 201, SP: 1000, DR: 1, AR: 0. Instruction: < ld -> 1 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 2, IP: 201, SP: 1000, DR: 1, AR: 0. Instruction: < ld -> 1 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 3, IP: 202, SP: 1000, DR: 1, AR: 0. Instruction: < st -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 4, IP: 202, SP: 1000, DR: 1, AR: 10. Instruction: < st -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 5, IP: 202, SP: 1000, DR: 1, AR: 10. Instruction: < st -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 6, IP: 203, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 1 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 7, IP: 203, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 1 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 8, IP: 203, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 1 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 9, IP: 204, SP: 1000, DR: 1, AR: 10. Instruction: < st -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 10, IP: 204, SP: 1000, DR: 1, AR: 11. Instruction: < st -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 11, IP: 204, SP: 1000, DR: 1, AR: 11. Instruction: < st -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 12, IP: 205, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 0 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 13, IP: 205, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 0 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 14, IP: 205, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 15, IP: 206, SP: 1000, DR: 0, AR: 11. Instruction: < st -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 16, IP: 206, SP: 1000, DR: 0, AR: 12. Instruction: < st -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 17, IP: 206, SP: 1000, DR: 0, AR: 12. Instruction: < st -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 18, IP: 207, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 19, IP: 207, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 20, IP: 207, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 21, IP: 208, SP: 1000, DR: 0, AR: 12. Instruction: < st -> 13 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 22, IP: 208, SP: 1000, DR: 0, AR: 13. Instruction: < st -> 13 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 23, IP: 208, SP: 1000, DR: 0, AR: 13. Instruction: < st -> 13 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 24, IP: 209, SP: 1000, DR: 0, AR: 13. Instruction: < ld -> 4000000 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 25, IP: 209, SP: 1000, DR: 4000000, AR: 13. Instruction: < ld -> 4000000 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 26, IP: 209, SP: 1000, DR: 4000000, AR: 13. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 27, IP: 210, SP: 1000, DR: 4000000, AR: 13. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 28, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 29, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 30, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 31, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 32, IP: 211, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 33, IP: 211, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 34, IP: 212, SP: 1000, DR: 1, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 35, IP: 212, SP: 1000, DR: 1, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 36, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 37, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999999
DEBUG    root:control_unit.py:43  Tick: 38, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999999
DEBUG    root:control_unit.py:43  Tick: 39, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999999
DEBUG    root:control_unit.py:43  Tick: 40, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999999
DEBUG    root:control_unit.py:43  Tick: 41, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 42, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 43, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 44, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 45, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 46, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 47, IP: 216, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 48, IP: 216, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 49, IP: 217, SP: 1000, DR: 1, AR: 11. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 50, IP: 217, SP: 999, DR: 1, AR: 999. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 51, IP: 217, SP: 999, DR: 1, AR: 999. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 52, IP: 218, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 53, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 54, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 55, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 56, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 57, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 58, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 59, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 60, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 61, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 62, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 63, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 64, IP: 221, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 65, IP: 221, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 66, IP: 222, SP: 999, DR: 1, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 67, IP: 222, SP: 999, DR: 1, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 68, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 69, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 70, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 71, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 72, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 73, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 74, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 75, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 76, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 77, IP: 225, SP: 1000, DR: 1, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 78, IP: 225, SP: 1000, DR: 1, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 79, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 80, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 81, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 82, IP: 236, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 83, IP: 237, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 84, IP: 237, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 85, IP: 237, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 86, IP: 237, SP: 1000, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 87, IP: 238, SP: 1000, DR: 1, AR: 11. Instruction: < st -> 13 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 88, IP: 238, SP: 1000, DR: 1, AR: 13. Instruction: < st -> 13 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 89, IP: 238, SP: 1000, DR: 1, AR: 13. Instruction: < st -> 13 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 90, IP: 239, SP: 1000, DR: 1, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 91, IP: 239, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 92, IP: 239, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 93, IP: 239, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 94, IP: 240, SP: 1000, DR: 1, AR: 10. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 95, IP: 240, SP: 999, DR: 1, AR: 999. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 96, IP: 240, SP: 999, DR: 1, AR: 999. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 97, IP: 241, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 98, IP: 241, SP: 999, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 99, IP: 241, SP: 999, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 100, IP: 241, SP: 999, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 101, IP: 242, SP: 999, DR: 1, AR: 11. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 102, IP: 242, SP: 998, DR: 1, AR: 998. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 103, IP: 242, SP: 998, DR: 1, AR: 998. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 104, IP: 243, SP: 998, DR: 1, AR: 998. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 105, IP: 243, SP: 999, DR: 1, AR: 998. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 106, IP: 243, SP: 999, DR: 1, AR: 998. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 107, IP: 243, SP: 999, DR: 1, AR: 998. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 108, IP: 244, SP: 999, DR: 1, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 109, IP: 244, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 110, IP: 244, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 111, IP: 244, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 112, IP: 245, SP: 999, DR: 1, AR: 999. Instruction: < add -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 113, IP: 245, SP: 999, DR: 1, AR: 998. Instruction: < add -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 114, IP: 245, SP: 999, DR: 1, AR: 998. Instruction: < add -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 115, IP: 245, SP: 999, DR: 1, AR: 998. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 116, IP: 246, SP: 999, DR: 1, AR: 998. Instruction: < st -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 117, IP: 246, SP: 999, DR: 1, AR: 999. Instruction: < st -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 118, IP: 246, SP: 999, DR: 1, AR: 999. Instruction: < st -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 119, IP: 247, SP: 999, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 120, IP: 247, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 121, IP: 247, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 122, IP: 247, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 123, IP: 248, SP: 1000, DR: 2, AR: 999. Instruction: < st -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 124, IP: 248, SP: 1000, DR: 2, AR: 11. Instruction: < st -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 125, IP: 248, SP: 1000, DR: 2, AR: 11. Instruction: < st -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 126, IP: 249, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 127, IP: 249, SP: 1000, DR: 2, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 128, IP: 249, SP: 1000, DR: 1, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 129, IP: 249, SP: 1000, DR: 1, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 130, IP: 250, SP: 1000, DR: 1, AR: 13. Instruction: < st -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 131, IP: 250, SP: 1000, DR: 1, AR: 10. Instruction: < st -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 132, IP: 250, SP: 1000, DR: 1, AR: 10. Instruction: < st -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 133, IP: 251, SP: 1000, DR: 1, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 134, IP: 208, SP: 1000, DR: 1, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 135, IP: 209, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 136, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 137, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 138, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 139, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 140, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 141, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 142, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 143, IP: 211, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 144, IP: 211, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 145, IP: 212, SP: 1000, DR: 2, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 146, IP: 212, SP: 1000, DR: 2, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 147, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 148, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999998
DEBUG    root:control_unit.py:43  Tick: 149, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999998
DEBUG    root:control_unit.py:43  Tick: 150, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999998
DEBUG    root:control_unit.py:43  Tick: 151, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999998
DEBUG    root:control_unit.py:43  Tick: 152, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 153, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 154, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 155, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 156, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 157, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 158, IP: 216, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 159, IP: 216, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 160, IP: 217, SP: 1000, DR: 2, AR: 11. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 161, IP: 217, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 162, IP: 217, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 163, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 164, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 165, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 166, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 167, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 168, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 169, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 170, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 171, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 172, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 173, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 174, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 175, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 176, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 177, IP: 222, SP: 999, DR: 2, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 178, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 179, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 180, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 181, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 182, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 183, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 184, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 185, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 186, IP: 224, SP: 1000, DR: 0, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 187, IP: 224, SP: 1000, DR: 0, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 188, IP: 225, SP: 1000, DR: 0, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 189, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 190, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 191, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 192, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 193, IP: 227, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 194, IP: 227, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 195, IP: 227, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 196, IP: 227, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 197, IP: 228, SP: 1000, DR: 0, AR: 12. Instruction: < push -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 198, IP: 228, SP: 999, DR: 0, AR: 999. Instruction: < push -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 199, IP: 228, SP: 999, DR: 0, AR: 999. Instruction: < push -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 200, IP: 229, SP: 999, DR: 0, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 201, IP: 229, SP: 999, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 202, IP: 229, SP: 999, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 203, IP: 229, SP: 999, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 204, IP: 230, SP: 999, DR: 2, AR: 11. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 205, IP: 230, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 206, IP: 230, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 207, IP: 231, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 208, IP: 231, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 209, IP: 231, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 210, IP: 231, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 211, IP: 232, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 212, IP: 232, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 213, IP: 232, SP: 999, DR: 0, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 214, IP: 232, SP: 999, DR: 0, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 215, IP: 233, SP: 999, DR: 0, AR: 999. Instruction: < add -> -1 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 216, IP: 233, SP: 999, DR: 0, AR: 998. Instruction: < add -> -1 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 217, IP: 233, SP: 999, DR: 2, AR: 998. Instruction: < add -> -1 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 218, IP: 233, SP: 999, DR: 2, AR: 998. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 219, IP: 234, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 220, IP: 234, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 221, IP: 234, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 222, IP: 235, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 223, IP: 235, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 224, IP: 235, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 225, IP: 235, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 226, IP: 236, SP: 1000, DR: 2, AR: 999. Instruction: < st -> 12 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 227, IP: 236, SP: 1000, DR: 2, AR: 12. Instruction: < st -> 12 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 228, IP: 236, SP: 1000, DR: 2, AR: 12. Instruction: < st -> 12 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 229, IP: 237, SP: 1000, DR: 2, AR: 12. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 230, IP: 237, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 231, IP: 237, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 232, IP: 237, SP: 1000, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 233, IP: 238, SP: 1000, DR: 2, AR: 11. Instruction: < st -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 234, IP: 238, SP: 1000, DR: 2, AR: 13. Instruction: < st -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 235, IP: 238, SP: 1000, DR: 2, AR: 13. Instruction: < st -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 236, IP: 239, SP: 1000, DR: 2, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 237, IP: 239, SP: 1000, DR: 2, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 238, IP: 239, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 239, IP: 239, SP: 1000, DR: 1, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 240, IP: 240, SP: 1000, DR: 1, AR: 10. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 241, IP: 240, SP: 999, DR: 1, AR: 999. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 242, IP: 240, SP: 999, DR: 1, AR: 999. Instruction: < push -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 243, IP: 241, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 244, IP: 241, SP: 999, DR: 1, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 245, IP: 241, SP: 999, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 246, IP: 241, SP: 999, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 247, IP: 242, SP: 999, DR: 2, AR: 11. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 248, IP: 242, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 249, IP: 242, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 250, IP: 243, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 251, IP: 243, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 252, IP: 243, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 253, IP: 243, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 254, IP: 244, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 255, IP: 244, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 256, IP: 244, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 257, IP: 244, SP: 999, DR: 1, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 258, IP: 245, SP: 999, DR: 1, AR: 999. Instruction: < add -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 259, IP: 245, SP: 999, DR: 1, AR: 998. Instruction: < add -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 260, IP: 245, SP: 999, DR: 2, AR: 998. Instruction: < add -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 261, IP: 245, SP: 999, DR: 2, AR: 998. Instruction: < add -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 262, IP: 246, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 263, IP: 246, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 264, IP: 246, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 265, IP: 247, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 266, IP: 247, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 267, IP: 247, SP: 1000, DR: 3, AR: 999. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 268, IP: 247, SP: 1000, DR: 3, AR: 999. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 269, IP: 248, SP: 1000, DR: 3, AR: 999. Instruction: < st -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 270, IP: 248, SP: 1000, DR: 3, AR: 11. Instruction: < st -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 271, IP: 248, SP: 1000, DR: 3, AR: 11. Instruction: < st -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 272, IP: 249, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 273, IP: 249, SP: 1000, DR: 3, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 274, IP: 249, SP: 1000, DR: 2, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 275, IP: 249, SP: 1000, DR: 2, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 276, IP: 250, SP: 1000, DR: 2, AR: 13. Instruction: < st -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 277, IP: 250, SP: 1000, DR: 2, AR: 10. Instruction: < st -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 278, IP: 250, SP: 1000, DR: 2, AR: 10. Instruction: < st -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 279, IP: 251, SP: 1000, DR: 2, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 280, IP: 208, SP: 1000, DR: 2, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 281, IP: 209, SP: 1000, DR: 2, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 282, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 283, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 284, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 285, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 286, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 287, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 288, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 289, IP: 211, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 290, IP: 211, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 291, IP: 212, SP: 1000, DR: 3, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 292, IP: 212, SP: 1000, DR: 3, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 293, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 294, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999997
DEBUG    root:control_unit.py:43  Tick: 295, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999997
DEBUG    root:control_unit.py:43  Tick: 296, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999997
DEBUG    root:control_unit.py:43  Tick: 297, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999997
DEBUG    root:control_unit.py:43  Tick: 298, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 299, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 300, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 301, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 302, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 303, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 304, IP: 216, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 305, IP: 216, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 306, IP: 217, SP: 1000, DR: 3, AR: 11. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 307, IP: 217, SP: 999, DR: 3, AR: 999. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 308, IP: 217, SP: 999, DR: 3, AR: 999. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 309, IP: 218, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 310, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 311, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 312, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 313, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 314, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 315, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 316, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 317, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 318, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 319, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 320, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 321, IP: 221, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 322, IP: 221, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 323, IP: 222, SP: 999, DR: 3, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 324, IP: 222, SP: 999, DR: 3, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 325, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 326, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 327, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 328, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 329, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 330, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 331, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 332, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 333, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 334, IP: 225, SP: 1000, DR: 1, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 335, IP: 225, SP: 1000, DR: 1, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 336, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 337, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 338, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 339, IP: 236, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 340, IP: 237, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 341, IP: 237, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 342, IP: 237, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 343, IP: 237, SP: 1000, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 344, IP: 238, SP: 1000, DR: 3, AR: 11. Instruction: < st -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 345, IP: 238, SP: 1000, DR: 3, AR: 13. Instruction: < st -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 346, IP: 238, SP: 1000, DR: 3, AR: 13. Instruction: < st -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 347, IP: 239, SP: 1000, DR: 3, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 348, IP: 239, SP: 1000, DR: 3, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 349, IP: 239, SP: 1000, DR: 2, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 350, IP: 239, SP: 1000, DR: 2, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 351, IP: 240, SP: 1000, DR: 2, AR: 10. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 352, IP: 240, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 353, IP: 240, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 354, IP: 241, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 355, IP: 241, SP: 999, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 356, IP: 241, SP: 999, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 357, IP: 241, SP: 999, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 358, IP: 242, SP: 999, DR: 3, AR: 11. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 359, IP: 242, SP: 998, DR: 3, AR: 998. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 360, IP: 242, SP: 998, DR: 3, AR: 998. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 361, IP: 243, SP: 998, DR: 3, AR: 998. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 362, IP: 243, SP: 999, DR: 3, AR: 998. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 363, IP: 243, SP: 999, DR: 3, AR: 998. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 364, IP: 243, SP: 999, DR: 3, AR: 998. Instruction: < pop -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 365, IP: 244, SP: 999, DR: 3, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 366, IP: 244, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 367, IP: 244, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 368, IP: 244, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 369, IP: 245, SP: 999, DR: 2, AR: 999. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 370, IP: 245, SP: 999, DR: 2, AR: 998. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 371, IP: 245, SP: 999, DR: 3, AR: 998. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 372, IP: 245, SP: 999, DR: 3, AR: 998. Instruction: < add -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 373, IP: 246, SP: 999, DR: 3, AR: 998. Instruction: < st -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 374, IP: 246, SP: 999, DR: 3, AR: 999. Instruction: < st -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 375, IP: 246, SP: 999, DR: 3, AR: 999. Instruction: < st -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 376, IP: 247, SP: 999, DR: 3, AR: 999. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 377, IP: 247, SP: 1000, DR: 3, AR: 999. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 378, IP: 247, SP: 1000, DR: 5, AR: 999. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 379, IP: 247, SP: 1000, DR: 5, AR: 999. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 380, IP: 248, SP: 1000, DR: 5, AR: 999. Instruction: < st -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 381, IP: 248, SP: 1000, DR: 5, AR: 11. Instruction: < st -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 382, IP: 248, SP: 1000, DR: 5, AR: 11. Instruction: < st -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 383, IP: 249, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 384, IP: 249, SP: 1000, DR: 5, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 385, IP: 249, SP: 1000, DR: 3, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 386, IP: 249, SP: 1000, DR: 3, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 387, IP: 250, SP: 1000, DR: 3, AR: 13. Instruction: < st -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 388, IP: 250, SP: 1000, DR: 3, AR: 10. Instruction: < st -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 389, IP: 250, SP: 1000, DR: 3, AR: 10. Instruction: < st -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 390, IP: 251, SP: 1000, DR: 3, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 391, IP: 208, SP: 1000, DR: 3, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 392, IP: 209, SP: 1000, DR: 3, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 393, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 394, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 395, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 396, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 397, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 398, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 399, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 400, IP: 211, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 401, IP: 211, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 402, IP: 212, SP: 1000, DR: 5, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 403, IP: 212, SP: 1000, DR: 5, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 404, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 405, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999995
DEBUG    root:control_unit.py:43  Tick: 406, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999995
DEBUG    root:control_unit.py:43  Tick: 407, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999995
DEBUG    root:control_unit.py:43  Tick: 408, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999995
DEBUG    root:control_unit.py:43  Tick: 409, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 410, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 411, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 412, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 413, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 414, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 415, IP: 216, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 416, IP: 216, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 417, IP: 217, SP: 1000, DR: 5, AR: 11. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 418, IP: 217, SP: 999, DR: 5, AR: 999. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 419, IP: 217, SP: 999, DR: 5, AR: 999. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 420, IP: 218, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 421, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 422, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 423, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 424, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 425, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 426, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 427, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 428, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 429, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 430, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 431, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 432, IP: 221, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 433, IP: 221, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 434, IP: 222, SP: 999, DR: 5, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 435, IP: 222, SP: 999, DR: 5, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 436, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 437, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 438, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 439, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 440, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 441, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 442, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 443, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 444, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 445, IP: 225, SP: 1000, DR: 1, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 446, IP: 225, SP: 1000, DR: 1, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 447, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 448, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 449, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 450, IP: 236, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 451, IP: 237, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 452, IP: 237, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 453, IP: 237, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 454, IP: 237, SP: 1000, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 455, IP: 238, SP: 1000, DR: 5, AR: 11. Instruction: < st -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 456, IP: 238, SP: 1000, DR: 5, AR: 13. Instruction: < st -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 457, IP: 238, SP: 1000, DR: 5, AR: 13. Instruction: < st -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 458, IP: 239, SP: 1000, DR: 5, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 459, IP: 239, SP: 1000, DR: 5, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 460, IP: 239, SP: 1000, DR: 3, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 461, IP: 239, SP: 1000, DR: 3, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 462, IP: 240, SP: 1000, DR: 3, AR: 10. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 463, IP: 240, SP: 999, DR: 3, AR: 999. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 464, IP: 240, SP: 999, DR: 3, AR: 999. Instruction: < push -> None | None >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 465, IP: 241, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 466, IP: 241, SP: 999, DR: 3, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 467, IP: 241, SP: 999, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 468, IP: 241, SP: 999, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 469, IP: 242, SP: 999, DR: 5, AR: 11. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 470, IP: 242, SP: 998, DR: 5, AR: 998. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 471, IP: 242, SP: 998, DR: 5, AR: 998. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 472, IP: 243, SP: 998, DR: 5, AR: 998. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 473, IP: 243, SP: 999, DR: 5, AR: 998. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 474, IP: 243, SP: 999, DR: 5, AR: 998. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 475, IP: 243, SP: 999, DR: 5, AR: 998. Instruction: < pop -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 476, IP: 244, SP: 999, DR: 5, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 477, IP: 244, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 478, IP: 244, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 479, IP: 244, SP: 999, DR: 3, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 480, IP: 245, SP: 999, DR: 3, AR: 999. Instruction: < add -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 481, IP: 245, SP: 999, DR: 3, AR: 998. Instruction: < add -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 482, IP: 245, SP: 999, DR: 5, AR: 998. Instruction: < add -> -1 | sp >, ACC: 3
DEBUG    root:control_unit.py:43  Tick: 483, IP: 245, SP: 999, DR: 5, AR: 998. Instruction: < add -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 484, IP: 246, SP: 999, DR: 5, AR: 998. Instruction: < st -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 485, IP: 246, SP: 999, DR: 5, AR: 999. Instruction: < st -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 486, IP: 246, SP: 999, DR: 5, AR: 999. Instruction: < st -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 487, IP: 247, SP: 999, DR: 5, AR: 999. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 488, IP: 247, SP: 1000, DR: 5, AR: 999. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 489, IP: 247, SP: 1000, DR: 8, AR: 999. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 490, IP: 247, SP: 1000, DR: 8, AR: 999. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 491, IP: 248, SP: 1000, DR: 8, AR: 999. Instruction: < st -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 492, IP: 248, SP: 1000, DR: 8, AR: 11. Instruction: < st -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 493, IP: 248, SP: 1000, DR: 8, AR: 11. Instruction: < st -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 494, IP: 249, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 495, IP: 249, SP: 1000, DR: 8, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 496, IP: 249, SP: 1000, DR: 5, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 497, IP: 249, SP: 1000, DR: 5, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 498, IP: 250, SP: 1000, DR: 5, AR: 13. Instruction: < st -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 499, IP: 250, SP: 1000, DR: 5, AR: 10. Instruction: < st -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 500, IP: 250, SP: 1000, DR: 5, AR: 10. Instruction: < st -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 501, IP: 251, SP: 1000, DR: 5, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 502, IP: 208, SP: 1000, DR: 5, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 503, IP: 209, SP: 1000, DR: 5, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 504, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 505, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 506, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 507, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 508, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 509, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 510, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 511, IP: 211, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 512, IP: 211, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 513, IP: 212, SP: 1000, DR: 8, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 514, IP: 212, SP: 1000, DR: 8, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 515, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 516, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999992
DEBUG    root:control_unit.py:43  Tick: 517, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999992
DEBUG    root:control_unit.py:43  Tick: 518, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999992
DEBUG    root:control_unit.py:43  Tick: 519, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999992
DEBUG    root:control_unit.py:43  Tick: 520, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 521, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 522, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 523, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 524, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 525, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 526, IP: 216, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 527, IP: 216, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 528, IP: 217, SP: 1000, DR: 8, AR: 11. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 529, IP: 217, SP: 999, DR: 8, AR: 999. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 530, IP: 217, SP: 999, DR: 8, AR: 999. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 531, IP: 218, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 532, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 533, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 534, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 535, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 536, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 537, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 538, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 539, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 540, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 541, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 542, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 543, IP: 221, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 544, IP: 221, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 545, IP: 222, SP: 999, DR: 8, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 546, IP: 222, SP: 999, DR: 8, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 547, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 548, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 549, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 550, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 551, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 552, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 553, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 554, IP: 224, SP: 1000, DR: 0, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 555, IP: 224, SP: 1000, DR: 0, AR: 999. Instruction: < pop -> None | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 556, IP: 225, SP: 1000, DR: 0, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 557, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 558, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 559, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 560, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 561, IP: 227, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 562, IP: 227, SP: 1000, DR: 0, AR: 12. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 563, IP: 227, SP: 1000, DR: 2, AR: 12. Instruction: < ld -> 12 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 564, IP: 227, SP: 1000, DR: 2, AR: 12. Instruction: < ld -> 12 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 565, IP: 228, SP: 1000, DR: 2, AR: 12. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 566, IP: 228, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 567, IP: 228, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 568, IP: 229, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 569, IP: 229, SP: 999, DR: 2, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 570, IP: 229, SP: 999, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 571, IP: 229, SP: 999, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 572, IP: 230, SP: 999, DR: 8, AR: 11. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 573, IP: 230, SP: 998, DR: 8, AR: 998. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 574, IP: 230, SP: 998, DR: 8, AR: 998. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 575, IP: 231, SP: 998, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 576, IP: 231, SP: 999, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 577, IP: 231, SP: 999, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 578, IP: 231, SP: 999, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 579, IP: 232, SP: 999, DR: 8, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 580, IP: 232, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 581, IP: 232, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 582, IP: 232, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 583, IP: 233, SP: 999, DR: 2, AR: 999. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 584, IP: 233, SP: 999, DR: 2, AR: 998. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 585, IP: 233, SP: 999, DR: 8, AR: 998. Instruction: < add -> -1 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 586, IP: 233, SP: 999, DR: 8, AR: 998. Instruction: < add -> -1 | sp >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 587, IP: 234, SP: 999, DR: 8, AR: 998. Instruction: < st -> 0 | sp >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 588, IP: 234, SP: 999, DR: 8, AR: 999. Instruction: < st -> 0 | sp >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 589, IP: 234, SP: 999, DR: 8, AR: 999. Instruction: < st -> 0 | sp >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 590, IP: 235, SP: 999, DR: 8, AR: 999. Instruction: < pop -> None | None >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 591, IP: 235, SP: 1000, DR: 8, AR: 999. Instruction: < pop -> None | None >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 592, IP: 235, SP: 1000, DR: 10, AR: 999. Instruction: < pop -> None | None >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 593, IP: 235, SP: 1000, DR: 10, AR: 999. Instruction: < pop -> None | None >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 594, IP: 236, SP: 1000, DR: 10, AR: 999. Instruction: < st -> 12 | mem >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 595, IP: 236, SP: 1000, DR: 10, AR: 12. Instruction: < st -> 12 | mem >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 596, IP: 236, SP: 1000, DR: 10, AR: 12. Instruction: < st -> 12 | mem >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 597, IP: 237, SP: 1000, DR: 10, AR: 12. Instruction: < ld -> 11 | mem >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 598, IP: 237, SP: 1000, DR: 10, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 599, IP: 237, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 10
DEBUG    root:control_unit.py:43  Tick: 600, IP: 237, SP: 1000, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 601, IP: 238, SP: 1000, DR: 8, AR: 11. Instruction: < st -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 602, IP: 238, SP: 1000, DR: 8, AR: 13. Instruction: < st -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 603, IP: 238, SP: 1000, DR: 8, AR: 13. Instruction: < st -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 604, IP: 239, SP: 1000, DR: 8, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 605, IP: 239, SP: 1000, DR: 8, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 606, IP: 239, SP: 1000, DR: 5, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 607, IP: 239, SP: 1000, DR: 5, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 608, IP: 240, SP: 1000, DR: 5, AR: 10. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 609, IP: 240, SP: 999, DR: 5, AR: 999. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 610, IP: 240, SP: 999, DR: 5, AR: 999. Instruction: < push -> None | None >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 611, IP: 241, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 612, IP: 241, SP: 999, DR: 5, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 613, IP: 241, SP: 999, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 614, IP: 241, SP: 999, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 615, IP: 242, SP: 999, DR: 8, AR: 11. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 616, IP: 242, SP: 998, DR: 8, AR: 998. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 617, IP: 242, SP: 998, DR: 8, AR: 998. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 618, IP: 243, SP: 998, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 619, IP: 243, SP: 999, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 620, IP: 243, SP: 999, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 621, IP: 243, SP: 999, DR: 8, AR: 998. Instruction: < pop -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 622, IP: 244, SP: 999, DR: 8, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 623, IP: 244, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 624, IP: 244, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 625, IP: 244, SP: 999, DR: 5, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 626, IP: 245, SP: 999, DR: 5, AR: 999. Instruction: < add -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 627, IP: 245, SP: 999, DR: 5, AR: 998. Instruction: < add -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 628, IP: 245, SP: 999, DR: 8, AR: 998. Instruction: < add -> -1 | sp >, ACC: 5
DEBUG    root:control_unit.py:43  Tick: 629, IP: 245, SP: 999, DR: 8, AR: 998. Instruction: < add -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 630, IP: 246, SP: 999, DR: 8, AR: 998. Instruction: < st -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 631, IP: 246, SP: 999, DR: 8, AR: 999. Instruction: < st -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 632, IP: 246, SP: 999, DR: 8, AR: 999. Instruction: < st -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 633, IP: 247, SP: 999, DR: 8, AR: 999. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 634, IP: 247, SP: 1000, DR: 8, AR: 999. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 635, IP: 247, SP: 1000, DR: 13, AR: 999. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 636, IP: 247, SP: 1000, DR: 13, AR: 999. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 637, IP: 248, SP: 1000, DR: 13, AR: 999. Instruction: < st -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 638, IP: 248, SP: 1000, DR: 13, AR: 11. Instruction: < st -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 639, IP: 248, SP: 1000, DR: 13, AR: 11. Instruction: < st -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 640, IP: 249, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 641, IP: 249, SP: 1000, DR: 13, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 642, IP: 249, SP: 1000, DR: 8, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 643, IP: 249, SP: 1000, DR: 8, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 644, IP: 250, SP: 1000, DR: 8, AR: 13. Instruction: < st -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 645, IP: 250, SP: 1000, DR: 8, AR: 10. Instruction: < st -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 646, IP: 250, SP: 1000, DR: 8, AR: 10. Instruction: < st -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 647, IP: 251, SP: 1000, DR: 8, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 648, IP: 208, SP: 1000, DR: 8, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 649, IP: 209, SP: 1000, DR: 8, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 650, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 651, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 652, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 653, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 654, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 655, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 656, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 657, IP: 211, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 658, IP: 211, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 659, IP: 212, SP: 1000, DR: 13, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 660, IP: 212, SP: 1000, DR: 13, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 661, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 662, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999987
DEBUG    root:control_unit.py:43  Tick: 663, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999987
DEBUG    root:control_unit.py:43  Tick: 664, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999987
DEBUG    root:control_unit.py:43  Tick: 665, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999987
DEBUG    root:control_unit.py:43  Tick: 666, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 667, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 668, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 669, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 670, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 671, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 672, IP: 216, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 673, IP: 216, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 674, IP: 217, SP: 1000, DR: 13, AR: 11. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 675, IP: 217, SP: 999, DR: 13, AR: 999. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 676, IP: 217, SP: 999, DR: 13, AR: 999. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 677, IP: 218, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 678, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 679, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 680, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 681, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 682, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 683, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 684, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 685, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 686, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 687, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 688, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 689, IP: 221, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 690, IP: 221, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 691, IP: 222, SP: 999, DR: 13, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 692, IP: 222, SP: 999, DR: 13, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 693, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 694, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 695, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 696, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 697, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 698, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 699, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 700, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 701, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 702, IP: 225, SP: 1000, DR: 1, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 703, IP: 225, SP: 1000, DR: 1, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 704, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 705, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 706, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 707, IP: 236, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 708, IP: 237, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 709, IP: 237, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 710, IP: 237, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 711, IP: 237, SP: 1000, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 712, IP: 238, SP: 1000, DR: 13, AR: 11. Instruction: < st -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 713, IP: 238, SP: 1000, DR: 13, AR: 13. Instruction: < st -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 714, IP: 238, SP: 1000, DR: 13, AR: 13. Instruction: < st -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 715, IP: 239, SP: 1000, DR: 13, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 716, IP: 239, SP: 1000, DR: 13, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 717, IP: 239, SP: 1000, DR: 8, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 718, IP: 239, SP: 1000, DR: 8, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 719, IP: 240, SP: 1000, DR: 8, AR: 10. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 720, IP: 240, SP: 999, DR: 8, AR: 999. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 721, IP: 240, SP: 999, DR: 8, AR: 999. Instruction: < push -> None | None >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 722, IP: 241, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 723, IP: 241, SP: 999, DR: 8, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 724, IP: 241, SP: 999, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 725, IP: 241, SP: 999, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 726, IP: 242, SP: 999, DR: 13, AR: 11. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 727, IP: 242, SP: 998, DR: 13, AR: 998. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 728, IP: 242, SP: 998, DR: 13, AR: 998. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 729, IP: 243, SP: 998, DR: 13, AR: 998. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 730, IP: 243, SP: 999, DR: 13, AR: 998. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 731, IP: 243, SP: 999, DR: 13, AR: 998. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 732, IP: 243, SP: 999, DR: 13, AR: 998. Instruction: < pop -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 733, IP: 244, SP: 999, DR: 13, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 734, IP: 244, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 735, IP: 244, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 736, IP: 244, SP: 999, DR: 8, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 737, IP: 245, SP: 999, DR: 8, AR: 999. Instruction: < add -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 738, IP: 245, SP: 999, DR: 8, AR: 998. Instruction: < add -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 739, IP: 245, SP: 999, DR: 13, AR: 998. Instruction: < add -> -1 | sp >, ACC: 8
DEBUG    root:control_unit.py:43  Tick: 740, IP: 245, SP: 999, DR: 13, AR: 998. Instruction: < add -> -1 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 741, IP: 246, SP: 999, DR: 13, AR: 998. Instruction: < st -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 742, IP: 246, SP: 999, DR: 13, AR: 999. Instruction: < st -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 743, IP: 246, SP: 999, DR: 13, AR: 999. Instruction: < st -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 744, IP: 247, SP: 999, DR: 13, AR: 999. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 745, IP: 247, SP: 1000, DR: 13, AR: 999. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 746, IP: 247, SP: 1000, DR: 21, AR: 999. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 747, IP: 247, SP: 1000, DR: 21, AR: 999. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 748, IP: 248, SP: 1000, DR: 21, AR: 999. Instruction: < st -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 749, IP: 248, SP: 1000, DR: 21, AR: 11. Instruction: < st -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 750, IP: 248, SP: 1000, DR: 21, AR: 11. Instruction: < st -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 751, IP: 249, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 752, IP: 249, SP: 1000, DR: 21, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 753, IP: 249, SP: 1000, DR: 13, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 754, IP: 249, SP: 1000, DR: 13, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 755, IP: 250, SP: 1000, DR: 13, AR: 13. Instruction: < st -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 756, IP: 250, SP: 1000, DR: 13, AR: 10. Instruction: < st -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 757, IP: 250, SP: 1000, DR: 13, AR: 10. Instruction: < st -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 758, IP: 251, SP: 1000, DR: 13, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 759, IP: 208, SP: 1000, DR: 13, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 760, IP: 209, SP: 1000, DR: 13, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 761, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 762, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 763, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 764, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 765, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 766, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 767, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 768, IP: 211, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 769, IP: 211, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 770, IP: 212, SP: 1000, DR: 21, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 771, IP: 212, SP: 1000, DR: 21, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 772, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 773, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999979
DEBUG    root:control_unit.py:43  Tick: 774, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999979
DEBUG    root:control_unit.py:43  Tick: 775, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999979
DEBUG    root:control_unit.py:43  Tick: 776, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999979
DEBUG    root:control_unit.py:43  Tick: 777, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 778, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 779, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 780, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 781, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 782, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 783, IP: 216, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 784, IP: 216, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 785, IP: 217, SP: 1000, DR: 21, AR: 11. Instruction: < push -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 786, IP: 217, SP: 999, DR: 21, AR: 999. Instruction: < push -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 787, IP: 217, SP: 999, DR: 21, AR: 999. Instruction: < push -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 788, IP: 218, SP: 999, DR: 21, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 789, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 790, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 791, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 792, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 793, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 794, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 795, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 796, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 797, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 798, IP: 221, SP: 999, DR: 2, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 799, IP: 221, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 800, IP: 221, SP: 999, DR: 21, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 801, IP: 221, SP: 999, DR: 21, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 802, IP: 222, SP: 999, DR: 21, AR: 999. Instruction: < mod -> -1 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 803, IP: 222, SP: 999, DR: 21, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 804, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 805, IP: 222, SP: 999, DR: 2, AR: 998. Instruction: < mod -> -1 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 806, IP: 223, SP: 999, DR: 2, AR: 998. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 807, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 808, IP: 223, SP: 999, DR: 2, AR: 999. Instruction: < st -> 0 | sp >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 809, IP: 224, SP: 999, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 810, IP: 224, SP: 1000, DR: 2, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 811, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 812, IP: 224, SP: 1000, DR: 1, AR: 999. Instruction: < pop -> None | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 813, IP: 225, SP: 1000, DR: 1, AR: 999. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 814, IP: 225, SP: 1000, DR: 1, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 815, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 816, IP: 225, SP: 1000, DR: 0, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 817, IP: 226, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 818, IP: 236, SP: 1000, DR: 0, AR: 14. Instruction: < jnz -> 236 | None >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 819, IP: 237, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 820, IP: 237, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 821, IP: 237, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 1
DEBUG    root:control_unit.py:43  Tick: 822, IP: 237, SP: 1000, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 823, IP: 238, SP: 1000, DR: 21, AR: 11. Instruction: < st -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 824, IP: 238, SP: 1000, DR: 21, AR: 13. Instruction: < st -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 825, IP: 238, SP: 1000, DR: 21, AR: 13. Instruction: < st -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 826, IP: 239, SP: 1000, DR: 21, AR: 13. Instruction: < ld -> 10 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 827, IP: 239, SP: 1000, DR: 21, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 828, IP: 239, SP: 1000, DR: 13, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 829, IP: 239, SP: 1000, DR: 13, AR: 10. Instruction: < ld -> 10 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 830, IP: 240, SP: 1000, DR: 13, AR: 10. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 831, IP: 240, SP: 999, DR: 13, AR: 999. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 832, IP: 240, SP: 999, DR: 13, AR: 999. Instruction: < push -> None | None >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 833, IP: 241, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 834, IP: 241, SP: 999, DR: 13, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 835, IP: 241, SP: 999, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 836, IP: 241, SP: 999, DR: 21, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 837, IP: 242, SP: 999, DR: 21, AR: 11. Instruction: < push -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 838, IP: 242, SP: 998, DR: 21, AR: 998. Instruction: < push -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 839, IP: 242, SP: 998, DR: 21, AR: 998. Instruction: < push -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 840, IP: 243, SP: 998, DR: 21, AR: 998. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 841, IP: 243, SP: 999, DR: 21, AR: 998. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 842, IP: 243, SP: 999, DR: 21, AR: 998. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 843, IP: 243, SP: 999, DR: 21, AR: 998. Instruction: < pop -> None | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 844, IP: 244, SP: 999, DR: 21, AR: 998. Instruction: < ld -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 845, IP: 244, SP: 999, DR: 21, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 846, IP: 244, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 847, IP: 244, SP: 999, DR: 13, AR: 999. Instruction: < ld -> 0 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 848, IP: 245, SP: 999, DR: 13, AR: 999. Instruction: < add -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 849, IP: 245, SP: 999, DR: 13, AR: 998. Instruction: < add -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 850, IP: 245, SP: 999, DR: 21, AR: 998. Instruction: < add -> -1 | sp >, ACC: 13
DEBUG    root:control_unit.py:43  Tick: 851, IP: 245, SP: 999, DR: 21, AR: 998. Instruction: < add -> -1 | sp >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 852, IP: 246, SP: 999, DR: 21, AR: 998. Instruction: < st -> 0 | sp >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 853, IP: 246, SP: 999, DR: 21, AR: 999. Instruction: < st -> 0 | sp >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 854, IP: 246, SP: 999, DR: 21, AR: 999. Instruction: < st -> 0 | sp >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 855, IP: 247, SP: 999, DR: 21, AR: 999. Instruction: < pop -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 856, IP: 247, SP: 1000, DR: 21, AR: 999. Instruction: < pop -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 857, IP: 247, SP: 1000, DR: 34, AR: 999. Instruction: < pop -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 858, IP: 247, SP: 1000, DR: 34, AR: 999. Instruction: < pop -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 859, IP: 248, SP: 1000, DR: 34, AR: 999. Instruction: < st -> 11 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 860, IP: 248, SP: 1000, DR: 34, AR: 11. Instruction: < st -> 11 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 861, IP: 248, SP: 1000, DR: 34, AR: 11. Instruction: < st -> 11 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 862, IP: 249, SP: 1000, DR: 34, AR: 11. Instruction: < ld -> 13 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 863, IP: 249, SP: 1000, DR: 34, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 864, IP: 249, SP: 1000, DR: 21, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 865, IP: 249, SP: 1000, DR: 21, AR: 13. Instruction: < ld -> 13 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 866, IP: 250, SP: 1000, DR: 21, AR: 13. Instruction: < st -> 10 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 867, IP: 250, SP: 1000, DR: 21, AR: 10. Instruction: < st -> 10 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 868, IP: 250, SP: 1000, DR: 21, AR: 10. Instruction: < st -> 10 | mem >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 869, IP: 251, SP: 1000, DR: 21, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 870, IP: 208, SP: 1000, DR: 21, AR: 10. Instruction: < jmp -> 208 | None >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 871, IP: 209, SP: 1000, DR: 21, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 872, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 21
DEBUG    root:control_unit.py:43  Tick: 873, IP: 209, SP: 1000, DR: 4000000, AR: 10. Instruction: < ld -> 4000000 | direct >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 874, IP: 210, SP: 1000, DR: 4000000, AR: 10. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 875, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 876, IP: 210, SP: 1000, DR: 4000000, AR: 14. Instruction: < st -> 14 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 877, IP: 211, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 878, IP: 211, SP: 1000, DR: 4000000, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 879, IP: 211, SP: 1000, DR: 34, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 4000000
DEBUG    root:control_unit.py:43  Tick: 880, IP: 211, SP: 1000, DR: 34, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 881, IP: 212, SP: 1000, DR: 34, AR: 11. Instruction: < sub -> 14 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 882, IP: 212, SP: 1000, DR: 34, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 883, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 884, IP: 212, SP: 1000, DR: 4000000, AR: 14. Instruction: < sub -> 14 | mem >, ACC: -3999966
DEBUG    root:control_unit.py:43  Tick: 885, IP: 213, SP: 1000, DR: 4000000, AR: 14. Instruction: < jaz -> 251 | None >, ACC: -3999966
DEBUG    root:control_unit.py:43  Tick: 886, IP: 214, SP: 1000, DR: 4000000, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999966
DEBUG    root:control_unit.py:43  Tick: 887, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: -3999966
DEBUG    root:control_unit.py:43  Tick: 888, IP: 214, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 0 | direct >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 889, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 890, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 891, IP: 215, SP: 1000, DR: 0, AR: 14. Instruction: < st -> 14 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 892, IP: 216, SP: 1000, DR: 0, AR: 14. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 893, IP: 216, SP: 1000, DR: 0, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 894, IP: 216, SP: 1000, DR: 34, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 0
DEBUG    root:control_unit.py:43  Tick: 895, IP: 216, SP: 1000, DR: 34, AR: 11. Instruction: < ld -> 11 | mem >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 896, IP: 217, SP: 1000, DR: 34, AR: 11. Instruction: < push -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 897, IP: 217, SP: 999, DR: 34, AR: 999. Instruction: < push -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 898, IP: 217, SP: 999, DR: 34, AR: 999. Instruction: < push -> None | None >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 899, IP: 218, SP: 999, DR: 34, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 900, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 34
DEBUG    root:control_unit.py:43  Tick: 901, IP: 218, SP: 999, DR: 2, AR: 999. Instruction: < ld -> 2 | direct >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 902, IP: 219, SP: 999, DR: 2, AR: 999. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 903, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 904, IP: 219, SP: 998, DR: 2, AR: 998. Instruction: < push -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 905, IP: 220, SP: 998, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
DEBUG    root:control_unit.py:43  Tick: 906, IP: 220, SP: 999, DR: 2, AR: 998. Instruction: < pop -> None | None >, ACC: 2
```

### Аналитика

```
|           Full name             | alg            | loc | bytes | instr | exec_instr | tick |                                            variant                                             |
| Нигаматуллин Степан Русланович  | hello_world    | 1   | -     | 27    | 27         | 79   |     alg -> asm | acc | harv | hw | instr | struct | stream | mem | cstr | prob2 | cache        |
| Нигаматуллин Степан Русланович  | greet_user     | 7   | -     | 73    | 133        | 408  |     alg -> asm | acc | harv | hw | instr | struct | stream | mem | cstr | prob2 | cache        |
| Нигаматуллин Степан Русланович  | prob2          | 17  | -     | 200   | 1396       | 4604 |     alg -> asm | acc | harv | hw | instr | struct | stream | mem | cstr | prob2 | cache        |
```