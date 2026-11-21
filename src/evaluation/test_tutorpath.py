
from src.engine.math_engine import (
    verify_expression,
    verify_equation
)

from src.agents.diagnostic_agent import (
    diagnose_misconception
)

from src.engine.adaptive_engine import (
    get_recommended_difficulty,
    record_attempt,
    get_learning_status
)

import src.engine.practice_engine as practice_engine


# --------------------------------------------------
# TEST RESULTS
# --------------------------------------------------

passed = 0
failed = 0


def run_test(test_name, condition):

    global passed, failed

    if condition:
        print(f"[PASS] {test_name}")
        passed += 1
    else:
        print(f"[FAIL] {test_name}")
        failed += 1


# --------------------------------------------------
# 1. MATHEMATICAL VERIFICATION
# --------------------------------------------------

print("\n1. MATHEMATICAL VERIFICATION")
print("-" * 45)

result = verify_expression("2(x + 3)", "2x + 6")

run_test(
    "Equivalent expressions",
    result["success"] and result["is_correct"]
)

result = verify_expression("2(x + 3)", "2x + 3")

run_test(
    "Non-equivalent expressions",
    result["success"] and not result["is_correct"]
)

result = verify_equation("2x + 4 = 12", "x = 4")

run_test(
    "Equivalent equation solutions",
    result["success"] and result["is_correct"]
)


# --------------------------------------------------
# 2. MISCONCEPTION DIAGNOSIS
# --------------------------------------------------

print("\n2. MISCONCEPTION DIAGNOSIS")
print("-" * 45)

result = diagnose_misconception(
    "Expand 2(x + 3)",
    "2x + 3",
    "2x + 6"
)

run_test(
    "Incomplete distribution diagnosis",
    result["detected"]
    and result["misconception"] == "Incomplete distribution"
)

result = diagnose_misconception(
    "Simplify 2x + 3y",
    "5xy",
    "2x + 3y"
)

run_test(
    "Unlike terms diagnosis",
    result["detected"]
    and result["misconception"] == "Combining unlike terms"
)


# --------------------------------------------------
# 3. ADAPTIVE LEARNING
# --------------------------------------------------

print("\n3. ADAPTIVE LEARNING")
print("-" * 45)

run_test(
    "Foundational difficulty",
    get_recommended_difficulty(20) == "Foundational"
)

run_test(
    "Intermediate difficulty",
    get_recommended_difficulty(50) == "Intermediate"
)

run_test(
    "Advanced difficulty",
    get_recommended_difficulty(85) == "Advanced"
)


# --------------------------------------------------
# 4. ADAPTIVE PRACTICE
# --------------------------------------------------

print("\n4. ADAPTIVE PRACTICE")
print("-" * 45)

# Use a controlled question generator so this test
# does not require a Groq API call or vector retrieval.

original_generator = practice_engine.generate_practice_questions


def mock_question_generator(
    grade,
    topic,
    difficulty,
    number=5
):
    return [
        {
            "question": f"Test question {index + 1}",
            "answer": "5",
            "hint": "Use the relevant mathematical rule.",
            "explanation": "This is a controlled test question.",
            "difficulty": difficulty
        }
        for index in range(number)
    ]


practice_engine.generate_practice_questions = mock_question_generator

try:

    result = practice_engine.get_adaptive_questions(
        topic="Algebra Play",
        grade="8",
        mastery_score=20,
        number=5
    )

    run_test(
        "Class 8 chapter practice generated",
        result["grade"] == "8"
        and result["topic"] == "Algebra Play"
        and result["question_count"] == 5
    )

    run_test(
        "Foundational difficulty selected",
        result["difficulty"] == "Foundational"
    )

    result = practice_engine.get_adaptive_questions(
        topic="Polynomials",
        grade="9",
        mastery_score=85,
        number=5
    )

    run_test(
        "Class 9 chapter practice generated",
        result["grade"] == "9"
        and result["topic"] == "Polynomials"
        and result["question_count"] == 5
    )

    run_test(
        "Advanced difficulty selected",
        result["difficulty"] == "Advanced"
    )

finally:

    practice_engine.generate_practice_questions = original_generator


# --------------------------------------------------
# 5. DATABASE AND PROGRESS
# --------------------------------------------------

print("\n5. DATABASE AND PROGRESS")
print("-" * 45)

test_student = "evaluation_test_student"

test_topic = "Class 8 | Algebra Play"

before = get_learning_status(
    test_student,
    test_topic
)

after = record_attempt(
    test_student,
    test_topic,
    True
)

run_test(
    "Student progress saved",
    after["attempts"] == before["attempts"] + 1
)

run_test(
    "Mastery updated",
    after["mastery_score"] == min(
        100,
        before["mastery_score"] + 10
    )
)


# --------------------------------------------------
# FINAL TEST SUMMARY
# --------------------------------------------------

print("\n" + "=" * 45)
print("TUTORPATH TEST SUMMARY")
print("=" * 45)

print("Tests passed:", passed)
print("Tests failed:", failed)
print("Total tests:", passed + failed)

if failed == 0:
    print("\nALL TESTS PASSED!")
else:
    print("\nSOME TESTS FAILED. REVIEW THE ERRORS.")

print("=" * 45)
