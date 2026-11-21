
import ast
import re

from sympy import (
    Symbol,
    Integer,
    Rational,
    Add,
    Mul,
    Pow,
    simplify,
    solve
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

x = Symbol("x")

MAX_EXPRESSION_LENGTH = 200
MAX_EXPONENT = 20


# --------------------------------------------------
# NORMALIZE MATHEMATICAL INPUT
# --------------------------------------------------

def normalize_input(expression):

    expression = str(expression).strip()

    if not expression:
        raise ValueError("Expression cannot be empty.")

    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")

    expression = (
        expression
        .replace("^", "**")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace(" ", "")
    )

    # Support basic implicit multiplication:
    # 2x -> 2*x
    # 2(x+3) -> 2*(x+3)
    # x(x+1) -> x*(x+1)

    expression = re.sub(r"(\d)(x)", r"\1*\2", expression)
    expression = re.sub(r"(\d)\(", r"\1*(", expression)
    expression = re.sub(r"(x)\(", r"\1*(", expression)
    expression = re.sub(r"\)(\d|x|\()", r")*\1", expression)

    return expression


# --------------------------------------------------
# SAFE AST EXPRESSION CONVERTER
# --------------------------------------------------

def convert_ast_to_sympy(node):

    if isinstance(node, ast.Expression):
        return convert_ast_to_sympy(node.body)

    if isinstance(node, ast.Constant):

        if isinstance(node.value, bool):
            raise ValueError("Boolean values are not supported.")

        if isinstance(node.value, int):
            return Integer(node.value)

        if isinstance(node.value, float):
            return Rational(str(node.value))

        raise ValueError("Unsupported mathematical value.")

    if isinstance(node, ast.Name):

        if node.id == "x":
            return x

        raise ValueError(
            "Only the variable x is supported."
        )

    if isinstance(node, ast.UnaryOp):

        value = convert_ast_to_sympy(node.operand)

        if isinstance(node.op, ast.UAdd):
            return value

        if isinstance(node.op, ast.USub):
            return -value

        raise ValueError("Unsupported unary operator.")

    if isinstance(node, ast.BinOp):

        left = convert_ast_to_sympy(node.left)
        right = convert_ast_to_sympy(node.right)

        if isinstance(node.op, ast.Add):
            return Add(left, right)

        if isinstance(node.op, ast.Sub):
            return Add(left, -right)

        if isinstance(node.op, ast.Mult):
            return Mul(left, right)

        if isinstance(node.op, ast.Div):

            if right == 0:
                raise ValueError("Division by zero is not allowed.")

            return left / right

        if isinstance(node.op, ast.Pow):

            if right.is_number is not True:
                raise ValueError(
                    "Variable exponents are not supported."
                )

            if abs(float(right)) > MAX_EXPONENT:
                raise ValueError("Exponent is too large.")

            return Pow(left, right)

        raise ValueError("Unsupported mathematical operator.")

    raise ValueError("Unsupported expression format.")


# --------------------------------------------------
# PARSE MATHEMATICAL EXPRESSION
# --------------------------------------------------

def parse_math_expression(expression):

    expression = normalize_input(expression)

    if "=" in expression:
        raise ValueError(
            "Use equation verification for expressions "
            "containing an equals sign."
        )

    try:

        syntax_tree = ast.parse(
            expression,
            mode="eval"
        )

        return convert_ast_to_sympy(syntax_tree)

    except (SyntaxError, TypeError, ValueError) as error:

        raise ValueError(
            f"Invalid mathematical expression: {error}"
        ) from error


# --------------------------------------------------
# VERIFY ALGEBRAIC EXPRESSIONS
# --------------------------------------------------

def verify_expression(student_expression, expected_expression):

    try:

        student = parse_math_expression(student_expression)

        expected = parse_math_expression(expected_expression)

        difference = simplify(student - expected)

        is_correct = difference == 0

        return {
            "success": True,
            "is_correct": is_correct,
            "student_expression": str(student),
            "expected_expression": str(expected),
            "message": (
                "Correct mathematical expression."
                if is_correct
                else "The expressions are not equivalent."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "is_correct": False,
            "message": str(error)
        }


# --------------------------------------------------
# PARSE LINEAR EQUATION
# --------------------------------------------------

def parse_linear_equation(equation):

    equation = str(equation).strip()

    if equation.count("=") != 1:
        raise ValueError(
            "Enter an equation with exactly one equals sign."
        )

    left, right = equation.split("=")

    lhs = parse_math_expression(left)
    rhs = parse_math_expression(right)

    return lhs, rhs


# --------------------------------------------------
# VERIFY EQUATIONS
# --------------------------------------------------

def verify_equation(student_equation, expected_equation):

    try:

        student_lhs, student_rhs = parse_linear_equation(
            student_equation
        )

        expected_lhs, expected_rhs = parse_linear_equation(
            expected_equation
        )

        student_solution = solve(
            student_lhs - student_rhs,
            x
        )

        expected_solution = solve(
            expected_lhs - expected_rhs,
            x
        )

        student_solutions = sorted(
            student_solution,
            key=str
        )

        expected_solutions = sorted(
            expected_solution,
            key=str
        )

        is_correct = (
            len(student_solutions) == len(expected_solutions)
            and all(
                simplify(a - b) == 0
                for a, b in zip(
                    student_solutions,
                    expected_solutions
                )
            )
        )

        return {
            "success": True,
            "is_correct": is_correct,
            "student_solution": [
                str(value) for value in student_solutions
            ],
            "expected_solution": [
                str(value) for value in expected_solutions
            ],
            "message": (
                "The equations have the same solution."
                if is_correct
                else "The equations have different solutions."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "is_correct": False,
            "message": str(error)
        }


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH MATHEMATICS ENGINE")
    print("=" * 45)

    expression_tests = [
        ("2(x + 3)", "2x + 6"),
        ("2(x + 3)", "2x + 3"),
        ("3x + 2x", "5x"),
        ("2x + 3", "5x")
    ]

    print("\nEXPRESSION VERIFICATION")

    for student, expected in expression_tests:

        result = verify_expression(student, expected)

        print(f"\nStudent: {student}")
        print(f"Expected: {expected}")
        print("Result:", result["message"])

    equation_tests = [
        ("2x + 4 = 12", "x = 4"),
        ("2x + 3 = 14", "2x + 6 = 14"),
        ("3x = 15", "x = 5")
    ]

    print("\nEQUATION VERIFICATION")

    for student, expected in equation_tests:

        result = verify_equation(student, expected)

        print(f"\nStudent equation: {student}")
        print(f"Reference equation: {expected}")
        print("Result:", result["message"])

    # Input validation test
    print("\nINPUT VALIDATION")

    invalid_test = verify_expression(
        "__import__('os')",
        "x"
    )

    print("Invalid input:", invalid_test["message"])
