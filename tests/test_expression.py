"""
Unit Tests for Stack-Based Expression Parser and Evaluator.
Validates parenthesis balancing, Infix to Postfix RPN, and formula evaluation.
"""

import unittest
from src.expression_parser import ExpressionParser


class TestExpressionParser(unittest.TestCase):
    def test_parenthesis_balancing(self):
        # Valid balanced expressions
        self.assertTrue(ExpressionParser.is_balanced("(a + b) * (c - d)"))
        self.assertTrue(ExpressionParser.is_balanced("{[a + b] * (c - d)}"))
        self.assertTrue(ExpressionParser.is_balanced("((weight * 0.40) + (loc * 0.30))"))
        self.assertTrue(ExpressionParser.is_balanced("no_brackets_here"))

        # Invalid unbalanced expressions
        self.assertFalse(ExpressionParser.is_balanced("(a + b * (c - d)"))
        self.assertFalse(ExpressionParser.is_balanced("([a + b)]"))
        self.assertFalse(ExpressionParser.is_balanced("((a + b)"))
        self.assertFalse(ExpressionParser.is_balanced("a + b)("))

    def test_infix_to_postfix(self):
        # Standard arithmetic
        rpn1 = ExpressionParser.infix_to_postfix("3 + 4 * 2")
        self.assertEqual(rpn1, ["3", "4", "2", "*", "+"])

        # With parentheses
        rpn2 = ExpressionParser.infix_to_postfix("(3 + 4) * 2")
        self.assertEqual(rpn2, ["3", "4", "+", "2", "*"])

        # With exponentiation
        rpn3 = ExpressionParser.infix_to_postfix("2 ^ 3 + 4")
        self.assertEqual(rpn3, ["2", "3", "^", "4", "+"])

    def test_formula_evaluation_arithmetic(self):
        res1 = ExpressionParser.evaluate("(10 + 20) * 2 - 5")
        self.assertEqual(res1, 55.0)

        res2 = ExpressionParser.evaluate("2 ^ 3 + 10 / 2")
        self.assertEqual(res2, 13.0)

    def test_dynamic_scoring_formula(self):
        # Confidence score formula
        formula = "(category_score * 0.40) + (location_score * 0.35) + (desc_score * 0.25)"
        variables = {
            "category_score": 100.0,
            "location_score": 80.0,
            "desc_score": 90.0
        }
        # Expected: (100 * 0.40) + (80 * 0.35) + (90 * 0.25) = 40 + 28 + 22.5 = 90.5
        score = ExpressionParser.evaluate(formula, variables)
        self.assertAlmostEqual(score, 90.5, places=2)

    def test_storage_fee_formula(self):
        # Storage fee formula
        formula = "(days_held * 5.0) + (item_value * 0.05) - discount"
        variables = {
            "days_held": 4.0,
            "item_value": 200.0,
            "discount": 10.0
        }
        # Expected: (4 * 5.0) + (200 * 0.05) - 10.0 = 20 + 10 - 10 = 20.0
        fee = ExpressionParser.evaluate(formula, variables)
        self.assertEqual(fee, 20.0)


if __name__ == "__main__":
    unittest.main()
