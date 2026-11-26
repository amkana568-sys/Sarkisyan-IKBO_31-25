"""Tests for all syntax forms in educational language variant 23."""

import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config_parser import ConfigError, convert


class ConverterTests(unittest.TestCase):
    """Check parsing, nested values, constants and expressions."""

    def test_number(self):
        self.assertEqual(convert("123"), 123)

    def test_string(self):
        self.assertEqual(convert("q(hello)"), "hello")

    def test_array(self):
        self.assertEqual(convert("[1, 2, q(three)]"), [1, 2, "three"])

    def test_dictionary(self):
        text = "{name -> q(Ada). age -> 20.}"
        self.assertEqual(convert(text), {"name": "Ada", "age": 20})

    def test_empty_dictionary(self):
        self.assertEqual(convert("{}"), {})

    def test_nested_values(self):
        text = "{items -> [1, {x -> q(y).}].}"
        self.assertEqual(convert(text), {"items": [1, {"x": "y"}]})

    def test_multiline_comment(self):
        text = "/+ first\nsecond +/ [1, 2]"
        self.assertEqual(convert(text), [1, 2])

    def test_constant_reference(self):
        self.assertEqual(convert("var size = 12 |size|"), 12)

    def test_constant_inside_object(self):
        text = "var count = 7 {count -> |count|.}"
        self.assertEqual(convert(text), {"count": 7})

    def test_addition(self):
        self.assertEqual(convert("|+ 4 5|"), 9)

    def test_subtraction(self):
        self.assertEqual(convert("|- 9 5|"), 4)

    def test_multiplication(self):
        self.assertEqual(convert("|* 6 7|"), 42)

    def test_division(self):
        self.assertEqual(convert("|/ 9 3|"), 3)

    def test_nested_expression(self):
        self.assertEqual(convert("|+ * 2 3 4|"), 10)

    def test_print_function(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = convert("|print(q(hello))|")
        self.assertEqual(result, "hello")
        self.assertEqual(output.getvalue(), "hello\n")

    def test_concat_function(self):
        text = "|concat(q(hello), q(-), q(world))|"
        self.assertEqual(convert(text), "hello-world")

    def test_function_as_value(self):
        self.assertEqual(convert("concat(q(a), q(b))"), "ab")

    def test_duplicate_constant(self):
        with self.assertRaises(ConfigError):
            convert("var x = 1 var x = 2 |x|")

    def test_unknown_constant(self):
        with self.assertRaises(ConfigError):
            convert("|missing|")

    def test_division_by_zero(self):
        with self.assertRaises(ConfigError):
            convert("|/ 8 - 1 1|")

    def test_duplicate_dictionary_key(self):
        with self.assertRaises(ConfigError):
            convert("{x -> 1. x -> 2.}")

    def test_invalid_leading_zero(self):
        with self.assertRaises(ConfigError):
            convert("01")

    def test_missing_dictionary_dot(self):
        with self.assertRaises(ConfigError):
            convert("{x -> 1}")

    def test_missing_array_comma(self):
        with self.assertRaises(ConfigError):
            convert("[1 2]")

    def test_invalid_name(self):
        with self.assertRaises(ConfigError):
            convert("{name1 -> 1.}")

    def test_var_is_valid_identifier(self):
        self.assertEqual(convert("{var -> 1.}"), {"var": 1})

    def test_constant_can_be_array(self):
        text = "var data = [1, {ok -> q(yes).}] |concat(q(done-), q(ok))|"
        self.assertEqual(convert(text), "done-ok")

    def test_constant_expression_in_declaration(self):
        text = "var first = 4 var second = |+ first 3| |second|"
        self.assertEqual(convert(text), 7)


if __name__ == "__main__":
    unittest.main()
