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

|   IO    |
|:-------:|
|  Data   |
|  Stack  |

* `IO` - Адресное пространство, разделенное между памятью данных и внешними устройствам
  * Адрес 0 - Стандартный вывод
  * Адрес 1 - Стандартный ввод
* `Data` - Адресное пространство данных
  * Данные хранятся последовательно
  * 
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