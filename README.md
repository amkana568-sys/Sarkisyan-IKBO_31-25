# Вариант 23 — конфигурационный язык в JSON

Учебная программа читает описание конфигурации из стандартного ввода,
проверяет синтаксис, вычисляет константы и записывает результат в JSON-файл.

## Возможности

- многострочные комментарии `/+ ... +/`;
- целые положительные числа по правилу `[1-9][0-9]*`;
- строки в виде `q(текст)`;
- массивы `[значение, значение, ...]`;
- словари `{ имя -> значение. ... }`;
- константы `var имя = значение`;
- префиксные выражения `|+ имя 1|`, `|- имя 1|`, `|* имя 2|`, `|/ имя 2|`;
- функции `print(значение)` и `concat(значение, значение, ...)`;
- вложенные массивы и словари.

Синтаксический разбор выполняется библиотекой **Lark** по грамматике
LALR. JSON формируется стандартным модулем `json`.

## Требования

- Python 3.10 или новее;
- pip.

## Установка

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установить библиотеку:

```bash
python -m pip install -r requirements.txt
```

## Запуск

Программа обязательно получает путь выходного файла через `-o` или
`--output`. Входной текст передаётся через stdin.

Linux/macOS:

```bash
python src/main.py --output result.json < examples/computer.cfg
```

Windows PowerShell:

```powershell
Get-Content -Raw examples/computer.cfg | python src/main.py -o result.json
```

При успехе JSON сохраняется в указанный файл. Диагностика ошибок
выводится в stderr, код возврата при ошибке — `1`.

## Синтаксис и примеры

### Комментарии

```text
/+ Это комментарий
   в несколько строк +/
```

### Массивы и словари

```text
[
    10,
    q(text),
    { enabled -> 1. }
]
```

```text
{
    host -> q(localhost).
    ports -> [8080, 8081].
}
```

### Константы и вычисления

```text
var workers = 4
var bonus = 2
{
    workers -> |workers|.
    total -> |+ workers bonus|.
    doubled -> |* workers 2|.
}
```

### Функции

`print(значение)` выводит текстовое представление значения в stdout и
возвращает это значение. `concat(a, b, ...)` склеивает текстовые
представления аргументов без разделителя. Обе функции можно вызывать
самостоятельно или внутри `|...|`.

Арифметические операции принимают два числа. Деление выполняется как
обычное числовое деление; деление на ноль является ошибкой.

## Два примера предметных областей

1. `examples/computer.cfg` — конфигурация компьютера.
2. `examples/library.cfg` — конфигурация библиотеки с вложенным словарём.

## Тесты

Запустить все тесты:

```bash
python -m unittest discover -s tests -v
```

Тесты проверяют комментарии, числа, строки, массивы, словари, вложенность,
объявление и использование констант, четыре арифметические операции,
`print()`, `concat()` и сообщения об ошибках.

## Замечания о правилах языка

- Имена состоят только из латинских букв и `_`; цифры в именах не
  допускаются. Имя `var` зарезервировано для объявления констант.
- Число `0` и числа с ведущим нулём не соответствуют заданному правилу.
- В массиве должен быть хотя бы один элемент; словарь может быть пустым.
- Каждая запись словаря заканчивается точкой.
- Константа должна быть объявлена до использования. Повторное объявление
  константы и повторение ключа словаря считаются ошибками.
- Для `print()` используется один аргумент, для `concat()` — два или более.
  Типы аргументов `concat()` преобразуются в текст; массивы и словари
  преобразуются в компактный JSON.

## Структура проекта

```text
variant23/
├── src/
│   ├── config_parser.py
│   └── main.py
├── tests/
│   ├── test_converter.py
│   └── test_examples.py
├── examples/
│   ├── computer.cfg
│   └── library.cfg
├── .gitignore
├── Makefile
├── README.md
├── requirements.txt
├── run.sh
└── run.bat
```

## Быстрые команды

В Linux/macOS после установки зависимостей:

```bash
make test
make example
```

Либо запустить конвертер напрямую:

```bash
./run.sh result.json < examples/library.cfg
```

В Windows можно использовать `run.bat`:

```powershell
Get-Content -Raw examples/library.cfg | .\run.bat result.json
```

## Публикация в GitHub / GitLab

Создайте пустой публичный репозиторий на выбранном Git-сервисе.
Затем откройте терминал в корне распакованного проекта и выполните:

```bash
git init
git add requirements.txt .gitignore Makefile run.sh run.bat
git commit -m "chore: add project setup"
git add src/
git commit -m "feat(parser): implement variant 23 parser"
git add tests/
git commit -m "test: cover syntax and nested values"
git add examples/ README.md
git commit -m "docs: add usage guide and configuration examples"
git branch -M main
git remote add origin https://github.com/USERNAME/variant23.git
git push -u origin main
```

Вместо `USERNAME` и адреса GitHub укажите свой аккаунт и URL созданного
репозитория. Для GitLab замените URL на адрес репозитория GitLab.
Коммиты оформлены в стиле Conventional Commits и показывают этапы работы.
