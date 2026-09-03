"""
actions/calculator.py
=====================
Safe mathematical expression parser and evaluator.
Evaluates arithmetic expressions without using raw eval().
"""
from __future__ import annotations

import ast
import math
import re

from utils.logger import get_logger

logger = get_logger(__name__)


def _safe_eval(node: ast.AST) -> float | int:
    """Recursively evaluate an AST math expression safely."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _safe_eval(node.operand)
        return +operand if isinstance(node.op, ast.UAdd) else -operand
    elif isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif isinstance(node.op, ast.Mod):
            return left % right
        elif isinstance(node.op, ast.Pow):
            return left ** right
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        func_name = node.func.id.lower()
        args = [_safe_eval(arg) for arg in node.args]
        if func_name == "sqrt" and len(args) == 1:
            return math.sqrt(args[0])
        elif func_name == "abs" and len(args) == 1:
            return abs(args[0])
        elif func_name == "round" and len(args) in (1, 2):
            return round(*args)

    raise ValueError(f"Unsupported mathematical expression element: {ast.dump(node)}")


def calculate(expression: str) -> str:
    """
    Safely parse and calculate *expression*.

    Supports natural phrasing like:
      - "what is 25 times 4" -> 100
      - "calculate 15 percent of 800" -> 120
      - "square root of 144" -> 12
    """
    if not expression:
        return "Please provide a mathematical calculation."

    cleaned = expression.lower().strip()

    # Preprocessing natural language math terms
    cleaned = re.sub(r"\bplus\b", "+", cleaned)
    cleaned = re.sub(r"\bminus\b", "-", cleaned)
    cleaned = re.sub(r"\btimes\b|\bmultiplied by\b|\bx\b", "*", cleaned)
    cleaned = re.sub(r"\bdivided by\b|\bover\b", "/", cleaned)
    cleaned = re.sub(r"\bsquare root of\b|\bsqrt of\b", "sqrt", cleaned)

    # Handle "X percent of Y" -> (X / 100) * Y
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s*of\s*(\d+(?:\.\d+)?)", cleaned)
    if pct_match:
        pct, val = float(pct_match.group(1)), float(pct_match.group(2))
        res = (pct / 100.0) * val
        return f"{expression} is {res:g}."

    # Handle "sqrt N" -> "sqrt(N)"
    cleaned = re.sub(r"sqrt\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", cleaned)

    # Keep only valid math characters
    sanitised = re.sub(r"[^\d\+\-\*\/\%\(\)\.\,\s\w]", "", cleaned)

    try:
        parsed_ast = ast.parse(sanitised, mode="eval")
        result = _safe_eval(parsed_ast)
        # Format as int if whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        logger.info(f"Calculated: '{expression}' -> {result}")
        return f"The answer is {result}."
    except ZeroDivisionError:
        return "Division by zero is undefined."
    except Exception as e:
        logger.warning(f"Calculation failed for '{expression}': {e}")
        return f"Sorry, I could not calculate '{expression}'."
