import unittest

from lark import Tree

from feyn._context import Context
from feyn._query import Parser


class TestFeynQueryParsing(unittest.TestCase):
    def setUp(self):
        self.context = Context()

    def test_special_opcode_meanings(self):
        self.assertEqual(Parser._translate_ast(self.context, Tree("register_any", [])), 0)
        self.assertEqual(Parser._translate_ast(self.context, Tree("interact1", [])), 1)
        self.assertEqual(Parser._translate_ast(self.context, Tree("interact2", [])), 2)
        self.assertEqual(Parser._translate_ast(self.context, Tree("wildcard", [])), 3)
        self.assertEqual(Parser._translate_ast(self.context, Tree("exclude", [])), 4)

    def test_wildcard_parsing(self):
        xcode, ycode = self.context.get_codes(0, ["x", "y"])
        output_code = self.context.lookup_by_fname("out", 0)

        with self.subTest("Wildcard with no parameters"):
            query = "_"
            _, qcodes = Parser.query_to_codes(self.context, "out", query)
            self.assertEqual([output_code, 3, 80], qcodes[:3])

        with self.subTest("Wildcard requiring input presence"):
            query = "_['x']"
            _, qcodes = Parser.query_to_codes(self.context, "out", query)
            self.assertEqual([output_code, 3, xcode, 80], qcodes[:4])

        with self.subTest("Wildcard disallowing input presence"):
            query = "_[!'x']"
            _, qcodes = Parser.query_to_codes(self.context, "out", query)
            self.assertEqual([output_code, 3, 4, xcode, 80], qcodes[:5])

        with self.subTest("Wildcard requesting at most 9 edges"):
            query = "_[9]"
            _, qcodes = Parser.query_to_codes(self.context, "out", query)
            self.assertEqual([output_code, 3, 59], qcodes[:3])

        with self.subTest("Complicated wildcard query"):
            query = "_['x', !'y', 3]"
            _, qcodes = Parser.query_to_codes(self.context, "out", query)
            self.assertEqual([output_code, 3, xcode, 4, ycode, 53], qcodes[:6])

    def test_expected_query_program(self):
        xcode, ycode, zcode = self.context.get_codes(0, ["x", "y", "z"])
        output_code = self.context.lookup_by_fname("out", 0)

        query1 = "'y' * _[!'z', 2] + 'x'"
        _, qcodes1 = Parser.query_to_codes(self.context, "out", query1)
        add_code = self.context.lookup_by_fname("add", 2)
        mul_code = self.context.lookup_by_fname("multiply", 2)

        expected_seq = [output_code, add_code, mul_code, ycode, 3, 4, zcode, 52, xcode]
        self.assertEqual(expected_seq, qcodes1[:9])

        query2 = "func('x') * log('y' + ?)"
        _, qcodes2 = Parser.query_to_codes(self.context, "out", query2)
        log_code = self.context.lookup_by_fname("log", 1)

        expected_seq = [output_code, mul_code, 1, xcode, log_code, add_code, ycode, 0]
        self.assertEqual(expected_seq, qcodes2[:8])

    def test_missing_input_raises_valueerror(self):
        context = Context()
        context.get_codes(0, ["x", "y"])

        # outside wc
        with self.assertRaises(ValueError):
            Parser.query_to_codes(self.context, "out", "'x' + 'z'")

        # in wc
        with self.assertRaises(ValueError):
            Parser.query_to_codes(self.context, "out", "'x' + _['z']")

    def test_query_complexity(self):
        self.context.get_codes(0, ["x", "y", "z"])
        self.context.lookup_by_fname("out", 0)
        n1, _ = Parser.query_to_codes(self.context, "out", "func('x')")
        n2, _ = Parser.query_to_codes(self.context, "out", "'x' + func('y')")
        n3, _ = Parser.query_to_codes(self.context, "out", "_['x', 'y']")
        n4, _ = Parser.query_to_codes(self.context, "out", "_['x', 'y', !'z']")

        self.assertEqual(n1, 2)
        self.assertEqual(n2, 4)
        self.assertEqual(n3, 2)
        self.assertEqual(n4, 2)

    def test_wildcard_complexity(self):
        self.context.get_codes(0, ["x", "y", "z"])
        self.context.lookup_by_fname("out", 0)

        with self.assertRaises(ValueError):
            Parser.query_to_codes(self.context, "out", "_['x', 'y', 1]")

        try:
            Parser.query_to_codes(self.context, "out", "_['x', 'y', 2]")
        except ValueError:
            self.fail("Wildcard raised unexpected ValueError.")

    def test_wildcard_inconsistency(self):
        self.context.get_codes(0, ["x", "y", "z"])
        self.context.lookup_by_fname("out", 0)

        with self.assertRaises(ValueError):
            Parser.query_to_codes(self.context, "out", "_['x', !'x']")

        try:
            Parser.query_to_codes(self.context, "out", "_['x', !'y']")
        except ValueError:
            self.fail("Wildcard raised unexpected ValueError.")
