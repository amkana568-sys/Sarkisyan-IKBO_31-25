"""Parser and evaluator for educational configuration language, variant 23."""

from __future__ import annotations

import json
import math
import sys
from typing import Any

from lark import Lark, Token, Tree
from lark.exceptions import UnexpectedInput


GRAMMAR = r"""
start: declaration* value

declaration: VAR NAME "=" value

?value: NUMBER                 -> number
      | STRING                 -> string
      | array
      | object
      | expression
      | function

array: "[" value ("," value)* "]"
object: "{" pair* "}"
pair: NAME "->" value "."

expression: "|" expr "|"

?expr: "+" expr expr          -> add
     | "-" expr expr          -> subtract
     | "*" expr expr          -> multiply
     | "/" expr expr          -> divide
     | NAME                   -> reference
     | NUMBER                 -> number
     | STRING                 -> string
     | expression
     | function

function: "print" "(" value ")"       -> print_call
        | "concat" "(" value "," value ("," value)* ")" -> concat_call

VAR.2: "var"
NAME: /[_a-zA-Z]+/
NUMBER: /[1-9][0-9]*/
STRING: /q\([^()\r\n]*\)/
COMMENT: /\/\+[\s\S]*?\+\//
%ignore COMMENT
%ignore /[ \t\f\r\n]+/
"""


class ConfigError(Exception):
    """An error in the source language or during constant evaluation."""


PARSER = Lark(
    GRAMMAR,
    parser="lalr",
    lexer="contextual",
    propagate_positions=True,
)


class Evaluator:
    """Evaluate declarations and the final configuration value."""

    def __init__(self) -> None:
        """Create an evaluator with an empty constant table."""
        self.constants: dict[str, Any] = {}

    def run(self, tree: Tree) -> Any:
        """Evaluate declarations in order, then return the final value."""
        result: Any = None
        for item in tree.children:
            if isinstance(item, Tree) and item.data == "declaration":
                self.declare(item)
            else:
                result = self.evaluate(item)
        return result

    def declare(self, node: Tree) -> None:
        """Evaluate and store one constant declaration."""
        name = str(node.children[1])
        if name in self.constants:
            raise ConfigError(f"Константа '{name}' объявлена повторно")
        self.constants[name] = self.evaluate(node.children[2])

    def evaluate(self, node: Any) -> Any:
        """Evaluate one parsed value or expression."""
        if not isinstance(node, Tree):
            raise ConfigError("Внутренняя ошибка разбора")
        rule = str(node.data)
        args = node.children
        if rule == "number":
            return int(str(args[0]))
        if rule == "string":
            return str(args[0])[2:-1]
        if rule == "array":
            return [self.evaluate(item) for item in args]
        if rule == "object":
            return self.evaluate_object(args)
        if rule == "pair":
            return str(args[0]), self.evaluate(args[1])
        if rule == "expression":
            return self.evaluate(args[0])
        if rule == "reference":
            return self.get_constant(str(args[0]))
        if rule in {"add", "subtract", "multiply", "divide"}:
            return self.calculate(rule, args)
        if rule == "print_call":
            return self.print_value(args[0])
        if rule == "concat_call":
            return self.concat_values(args)
        raise ConfigError(f"Неизвестная конструкция: {rule}")

    def evaluate_object(self, pairs: list[Any]) -> dict[str, Any]:
        """Evaluate dictionary entries and reject duplicate names."""
        result: dict[str, Any] = {}
        for pair in pairs:
            key, value = self.evaluate(pair)
            if key in result:
                raise ConfigError(f"Ключ '{key}' указан повторно")
            result[key] = value
        return result

    def get_constant(self, name: str) -> Any:
        """Return a previously declared constant."""
        if name not in self.constants:
            raise ConfigError(f"Неизвестная константа: '{name}'")
        return self.constants[name]

    def calculate(self, operation: str, args: list[Any]) -> Any:
        """Calculate an arithmetic operation with two numeric arguments."""
        left = self.evaluate(args[0])
        right = self.evaluate(args[1])
        if not self.is_number(left) or not self.is_number(right):
            raise ConfigError("Для арифметики нужны два числа")
        if operation == "add":
            return left + right
        if operation == "subtract":
            return left - right
        if operation == "multiply":
            return left * right
        if right == 0:
            raise ConfigError("Деление на ноль")
        return left / right

    @staticmethod
    def is_number(value: Any) -> bool:
        """Check for an integer or a finite floating-point number."""
        if type(value) is int:
            return True
        return isinstance(value, float) and math.isfinite(value)

    def print_value(self, node: Any) -> Any:
        """Print one value to stdout and return that value."""
        value = self.evaluate(node)
        print(self.to_text(value))
        return value

    def concat_values(self, nodes: list[Any]) -> str:
        """Concatenate the textual representations of two or more values."""
        return "".join(self.to_text(self.evaluate(item)) for item in nodes)

    @staticmethod
    def to_text(value: Any) -> str:
        """Convert a value to text for print() and concat()."""
        if isinstance(value, str):
            return value
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)


def convert(source: str) -> Any:
    """Parse and evaluate one source document."""
    try:
        tree = PARSER.parse(source)
    except UnexpectedInput as error:
        line = getattr(error, "line", 1)
        column = getattr(error, "column", 1)
        context = error.get_context(source, span=30).strip()
        details = f"\n{context}" if context else ""
        raise ConfigError(
            f"Синтаксическая ошибка, строка {line}, столбец {column}"
            f"{details}"
        ) from error
    return Evaluator().run(tree)
