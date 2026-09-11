"""
Stack-based Expression Parser and Formula Evaluator.
Satisfies syllabus requirement: Applying stack for simple expression handling (basic level).

Implements:
1. Delimiter / Parenthesis balancing validation via LinkedStack.
2. Infix to Postfix (RPN) conversion via Shunting-Yard Algorithm.
3. Postfix expression evaluation with dynamic variable resolution via Operand Stack.
"""

from typing import Dict, List, Optional, Union
import re
from src.stack import LinkedStack


class ExpressionParser:
    """
    Evaluates dynamic arithmetic and weighted scoring formulas using stack data structures.
    """

    # Operator precedence and associativity
    PRECEDENCE = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2,
        "%": 2,
        "^": 3,
    }

    MATCHING_BRACKETS = {
        ")": "(",
        "]": "[",
        "}": "{"
    }

    @classmethod
    def is_balanced(cls, expression: str) -> bool:
        """
        Validate if parentheses, brackets, and braces in the expression are balanced.
        Uses LinkedStack to maintain open delimiters.
        Time Complexity: O(N)
        """
        stack: LinkedStack[str] = LinkedStack()
        open_delimiters = set("({[")
        close_delimiters = set(")}]")

        for char in expression:
            if char in open_delimiters:
                stack.push(char)
            elif char in close_delimiters:
                if stack.is_empty():
                    return False
                top_char = stack.pop()
                if top_char != cls.MATCHING_BRACKETS[char]:
                    return False

        return stack.is_empty()

    @classmethod
    def tokenize(cls, expression: str) -> List[str]:
        """
        Tokenize mathematical expression supporting numbers, variables, operators, and parentheses.
        """
        # Matches numbers (including floats), variable names, operators, and parentheses
        token_pattern = r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)\[\]\{\}]'
        tokens = re.findall(token_pattern, expression)
        return tokens

    @classmethod
    def infix_to_postfix(cls, expression: str) -> List[str]:
        """
        Convert Infix expression to Postfix (Reverse Polish Notation) using Dijkstra's Shunting-Yard algorithm.
        Time Complexity: O(N)
        """
        if not cls.is_balanced(expression):
            raise ValueError("Invalid Expression: Unbalanced parentheses or brackets.")

        tokens = cls.tokenize(expression)
        output_queue: List[str] = []
        operator_stack: LinkedStack[str] = LinkedStack()

        open_brackets = {"(", "[", "{"}
        close_brackets = {")": "(", "]": "[", "}": "{"}

        for token in tokens:
            # Check if token is number or variable
            if re.match(r'^\d+(\.\d+)?$', token) or re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
                output_queue.append(token)
            elif token in open_brackets:
                operator_stack.push(token)
            elif token in close_brackets:
                matched_open = close_brackets[token]
                while not operator_stack.is_empty() and operator_stack.peek() != matched_open:
                    output_queue.append(operator_stack.pop())
                if not operator_stack.is_empty():
                    operator_stack.pop()  # Discard the opening bracket
            elif token in cls.PRECEDENCE:
                curr_prec = cls.PRECEDENCE[token]
                # Right associative for exponentiation '^'
                is_right_assoc = (token == "^")

                while (not operator_stack.is_empty() and
                       operator_stack.peek() in cls.PRECEDENCE and
                       ((cls.PRECEDENCE[operator_stack.peek()] > curr_prec) or
                        (cls.PRECEDENCE[operator_stack.peek()] == curr_prec and not is_right_assoc))):
                    output_queue.append(operator_stack.pop())

                operator_stack.push(token)
            else:
                raise ValueError(f"Unknown token in expression: '{token}'")

        while not operator_stack.is_empty():
            output_queue.append(operator_stack.pop())

        return output_queue

    @classmethod
    def evaluate_postfix(cls, postfix_tokens: List[str], variables: Optional[Dict[str, float]] = None) -> float:
        """
        Evaluate a Postfix token list using an operand LinkedStack.
        Time Complexity: O(N)
        """
        variables = variables or {}
        operand_stack: LinkedStack[float] = LinkedStack()

        for token in postfix_tokens:
            # Check if number
            if re.match(r'^\d+(\.\d+)?$', token):
                operand_stack.push(float(token))
            # Check if variable
            elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
                if token not in variables:
                    raise KeyError(f"Variable '{token}' not provided in evaluation context.")
                operand_stack.push(float(variables[token]))
            # Operator
            elif token in cls.PRECEDENCE:
                if len(operand_stack) < 2:
                    raise ValueError(f"Malformed expression: Insufficient operands for operator '{token}'.")
                b = operand_stack.pop()
                a = operand_stack.pop()

                if token == "+":
                    res = a + b
                elif token == "-":
                    res = a - b
                elif token == "*":
                    res = a * b
                elif token == "/":
                    if b == 0:
                        raise ZeroDivisionError("Division by zero in formula evaluation.")
                    res = a / b
                elif token == "%":
                    res = a % b
                elif token == "^":
                    res = a ** b
                else:
                    raise ValueError(f"Unsupported operator: {token}")

                operand_stack.push(res)
            else:
                raise ValueError(f"Invalid token '{token}' in postfix expression.")

        if len(operand_stack) != 1:
            raise ValueError("Malformed expression: Operator/operand mismatch.")

        return operand_stack.pop()

    @classmethod
    def evaluate(cls, expression: str, variables: Optional[Dict[str, float]] = None) -> float:
        """
        End-to-end evaluator: Validate -> Infix to Postfix -> Evaluate.
        """
        postfix = cls.infix_to_postfix(expression)
        return cls.evaluate_postfix(postfix, variables)
