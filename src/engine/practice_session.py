
from src.engine.adaptive_engine import (
    record_attempt,
    get_learning_status
)

from src.engine.practice_engine import get_adaptive_questions


def normalize_answer(answer):
    answer = str(answer).strip().lower()
    answer = answer.replace(" ", "")
    answer = answer.replace("**", "^")
    answer = answer.replace("×", "*")
    answer = answer.replace("−", "-")
    return answer


def get_mastery_topic(grade, topic):
    return f"Class {grade} | {topic}"


def start_practice_session(
    student_id,
    topic="Algebra",
    number=5,
    grade="8"
):
    grade = str(grade)
    number = max(1, min(int(number), 20))

    mastery_topic = get_mastery_topic(grade, topic)

    status = get_learning_status(
        student_id,
        mastery_topic
    )

    practice = get_adaptive_questions(
        topic=topic,
        grade=grade,
        mastery_score=status["mastery_score"],
        number=number
    )

    return {
        "student_id": student_id,
        "grade": grade,
        "topic": topic,
        "mastery_topic": mastery_topic,
        "mastery_score": status["mastery_score"],
        "difficulty": practice["difficulty"],
        "questions": practice["questions"],
        "question_count": practice["question_count"],
        "levels_used": practice["levels_used"]
    }


def submit_practice_answer(
    student_id,
    topic,
    question,
    student_answer,
    expected_answer,
    explanation=""
):
    submitted = normalize_answer(student_answer)
    expected = normalize_answer(expected_answer)

    is_correct = submitted == expected

    updated_progress = record_attempt(
        student_id=student_id,
        topic=topic,
        is_correct=is_correct
    )

    if is_correct:
        feedback = "Correct! Well done. Keep practising."
    else:
        feedback = (
            "Not quite right. Review the explanation "
            "below and understand the correct method."
        )

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "explanation": explanation,
        "expected_answer": expected_answer,
        "mastery_score": updated_progress["mastery_score"],
        "attempts": updated_progress["attempts"],
        "correct_answers": updated_progress["correct_answers"]
    }


def display_student_progress(student_id, topic):
    status = get_learning_status(student_id, topic)

    print("\nSTUDENT LEARNING PROGRESS")
    print("=" * 40)
    print("Student:", student_id)
    print("Topic:", topic)
    print("Mastery:", status["mastery_score"], "/ 100")
    print("Attempts:", status["attempts"])
    print("Correct answers:", status["correct_answers"])
    print("Current difficulty:", status["difficulty"])
