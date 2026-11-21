
import re

from src.engine.math_engine import verify_expression


# --------------------------------------------------
# NORMALIZE MATHEMATICAL INPUT
# --------------------------------------------------

def normalize_expression(expression):

    return (
        re.sub(r"\s+", "", str(expression).lower())
        .replace("×", "*")
        .replace("−", "-")
        .replace("–", "-")
        .replace("**", "^")
    )


def extract_math_expression(question):

    text = normalize_expression(question)

    # Remove common question instructions.
    text = re.sub(
        r"^(expand|simplify|calculate|solve|evaluate|find):?",
        "",
        text
    )

    return text


# --------------------------------------------------
# CREATE STANDARD DIAGNOSIS
# --------------------------------------------------

def create_diagnosis(
    detected,
    misconception,
    concept,
    explanation,
    hint,
    confidence
):

    return {
        "detected": detected,
        "misconception": misconception,
        "concept": concept,
        "explanation": explanation,
        "hint": hint,
        "confidence": confidence
    }


# --------------------------------------------------
# MISCONCEPTION DIAGNOSIS
# --------------------------------------------------

def diagnose_misconception(
    question,
    student_work,
    expected_answer=None
):

    question_text = extract_math_expression(question)
    student_text = normalize_expression(student_work)

    # --------------------------------------------------
    # CHECK 1: INSUFFICIENT WORKING
    # --------------------------------------------------

    if not student_text:

        return create_diagnosis(
            False,
            "Insufficient working",
            "Mathematical reasoning",
            "The student has not provided enough working to identify an error.",
            "Show your calculation steps so we can understand your approach.",
            "Low"
        )

    # --------------------------------------------------
    # CHECK 2: DISTRIBUTIVE PROPERTY
    # --------------------------------------------------

    distribution_match = re.fullmatch(
        r"(\d+)\(([a-z])([+-])(\d+)\)",
        question_text
    )

    if distribution_match:

        coefficient = int(distribution_match.group(1))
        variable = distribution_match.group(2)
        sign = distribution_match.group(3)
        constant = int(distribution_match.group(4))

        correct_constant = coefficient * constant

        expected_variable_term = f"{coefficient}{variable}"
        incorrect_constant = f"{sign}{constant}"
        correct_constant_term = f"{sign}{correct_constant}"

        if (
            expected_variable_term in student_text
            and incorrect_constant in student_text
            and correct_constant_term not in student_text
        ):

            return create_diagnosis(
                True,
                "Incomplete distribution",
                "Distributive property",
                (
                    "The coefficient appears to have been multiplied "
                    "by the variable but not by the constant inside "
                    "the brackets."
                ),
                (
                    "When removing brackets, what must the outside "
                    "number multiply?"
                ),
                "Medium"
            )

    # --------------------------------------------------
    # CHECK 3: COMBINING UNLIKE TERMS
    # --------------------------------------------------

    unlike_terms_pattern = re.fullmatch(
        r"\d+[a-z][+-]\d+[a-z]",
        question_text
    )

    combined_term_pattern = re.fullmatch(
        r"\d+[a-z]{2,}",
        student_text
    )

    if unlike_terms_pattern and combined_term_pattern:

        return create_diagnosis(
            True,
            "Combining unlike terms",
            "Algebraic terms",
            (
                "Terms containing different variables cannot "
                "be combined into a single like term."
            ),
            (
                "Can you combine terms that have different variables?"
            ),
            "Medium"
        )

    # --------------------------------------------------
    # CHECK 4: FRACTION ADDITION
    # --------------------------------------------------

    fraction_pattern = re.fullmatch(
        r"(\d+)/(\d+)\+(\d+)/(\d+)",
        question_text
    )

    if fraction_pattern and "/" in student_text:

        if expected_answer:

            try:

                result = verify_expression(
                    student_work,
                    expected_answer
                )

                if (
                    result.get("success")
                    and not result.get("is_correct")
                ):

                    return create_diagnosis(
                        True,
                        "Fraction addition error",
                        "Addition of fractions",
                        (
                            "The result is not equivalent to the "
                            "expected fraction. Check whether you "
                            "found a common denominator."
                        ),
                        (
                            "Before adding the numerators, what "
                            "should you do with the denominators?"
                        ),
                        "Medium"
                    )

            except Exception:
                pass

    # --------------------------------------------------
    # CHECK 5: GENERAL MATHEMATICAL VERIFICATION
    # --------------------------------------------------

    if expected_answer:

        try:

            result = verify_expression(
                student_work,
                expected_answer
            )

            if (
                result.get("success")
                and result.get("is_correct")
            ):

                return create_diagnosis(
                    False,
                    "No misconception detected",
                    "Mathematical reasoning",
                    (
                        "Your expression is mathematically equivalent "
                        "to the expected expression."
                    ),
                    (
                        "Good work! Can you explain why your method works?"
                    ),
                    "High"
                )

            if (
                result.get("success")
                and not result.get("is_correct")
            ):

                return create_diagnosis(
                    True,
                    "Unclassified algebraic error",
                    "Algebraic manipulation",
                    (
                        "Your expression is not mathematically "
                        "equivalent to the expected expression."
                    ),
                    (
                        "Review the operation you applied in your "
                        "last calculation step."
                    ),
                    "Low"
                )

        except Exception:
            pass

    # --------------------------------------------------
    # CHECK 6: NO CLEAR MISCONCEPTION
    # --------------------------------------------------

    return create_diagnosis(
        False,
        "No clear misconception identified",
        "General mathematics",
        (
            "The available working is not sufficient to identify "
            "a specific mathematical misconception."
        ),
        (
            "Show your calculation steps so we can examine "
            "your reasoning."
        ),
        "Low"
    )


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH MISCONCEPTION DIAGNOSIS")
    print("=" * 50)

    test_cases = [

        {
            "question": "Expand 2(x + 3)",
            "student_work": "2x + 3",
            "expected_answer": "2x + 6"
        },

        {
            "question": "Simplify 2x + 3y",
            "student_work": "5xy",
            "expected_answer": "2x + 3y"
        },

        {
            "question": "Calculate 1/2 + 1/3",
            "student_work": "2/5",
            "expected_answer": "5/6"
        },

        {
            "question": "Expand 3(x + 4)",
            "student_work": "3x + 12",
            "expected_answer": "3x + 12"
        },

        {
            "question": "Simplify 4x + 2x",
            "student_work": "6x",
            "expected_answer": "6x"
        }

    ]

    for index, test in enumerate(test_cases, start=1):

        result = diagnose_misconception(
            question=test["question"],
            student_work=test["student_work"],
            expected_answer=test["expected_answer"]
        )

        print(f"\nTEST {index}")
        print("Question:", test["question"])
        print("Student work:", test["student_work"])
        print("Diagnosis:", result["misconception"])
        print("Detected:", result["detected"])
        print("Concept:", result["concept"])
        print("Explanation:", result["explanation"])
        print("Hint:", result["hint"])
        print("Confidence:", result["confidence"])
        print("-" * 50)
