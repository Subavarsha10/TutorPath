
import sqlite3
from pathlib import Path


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "tutorpath.db"


# --------------------------------------------------
# GET ALL STUDENT RECORDS
# --------------------------------------------------

def get_all_student_records():

    if not DATABASE_PATH.exists():
        return []

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            student_id,
            topic,
            mastery_score,
            attempts,
            correct_answers
        FROM mastery_records
        ORDER BY student_id, topic
    """)

    records = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return records


# --------------------------------------------------
# GET STUDENT DASHBOARD DATA
# --------------------------------------------------

def get_student_analytics(student_id):

    records = get_all_student_records()

    student_records = [
        record for record in records
        if record["student_id"] == student_id
    ]

    if not student_records:
        return {
            "student_id": student_id,
            "topics": 0,
            "mastery_score": 0,
            "total_attempts": 0,
            "correct_answers": 0,
            "accuracy": 0
        }

    total_attempts = sum(
        record["attempts"] for record in student_records
    )

    correct_answers = sum(
        record["correct_answers"] for record in student_records
    )

    average_mastery = round(
        sum(record["mastery_score"] for record in student_records)
        / len(student_records)
    )

    accuracy = round(
        (correct_answers / total_attempts) * 100
    ) if total_attempts else 0

    return {
        "student_id": student_id,
        "topics": len(student_records),
        "mastery_score": average_mastery,
        "total_attempts": total_attempts,
        "correct_answers": correct_answers,
        "accuracy": accuracy
    }


# --------------------------------------------------
# GET TEACHER DASHBOARD DATA
# --------------------------------------------------

def get_teacher_analytics():

    records = get_all_student_records()

    if not records:
        return {
            "total_students": 0,
            "total_attempts": 0,
            "average_mastery": 0,
            "average_accuracy": 0,
            "students": []
        }

    student_ids = set(
        record["student_id"] for record in records
    )

    total_attempts = sum(
        record["attempts"] for record in records
    )

    total_correct = sum(
        record["correct_answers"] for record in records
    )

    average_mastery = round(
        sum(record["mastery_score"] for record in records)
        / len(records)
    )

    average_accuracy = round(
        (total_correct / total_attempts) * 100
    ) if total_attempts else 0

    return {
        "total_students": len(student_ids),
        "total_attempts": total_attempts,
        "average_mastery": average_mastery,
        "average_accuracy": average_accuracy,
        "students": records
    }


# --------------------------------------------------
# IDENTIFY STUDENTS NEEDING SUPPORT
# --------------------------------------------------

def get_students_needing_support():

    records = get_all_student_records()

    students = []

    for record in records:

        if record["mastery_score"] < 40:

            students.append({
                "student_id": record["student_id"],
                "topic": record["topic"],
                "mastery_score": record["mastery_score"],
                "reason": "Foundational support recommended"
            })

    return students


# --------------------------------------------------
# TEST ANALYTICS ENGINE
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH ANALYTICS ENGINE")
    print("=" * 45)

    student_data = get_student_analytics(
        "demo_student_ui"
    )

    print("\nSTUDENT ANALYTICS")
    print(student_data)

    teacher_data = get_teacher_analytics()

    print("\nTEACHER ANALYTICS")
    print("Total students:", teacher_data["total_students"])
    print("Total attempts:", teacher_data["total_attempts"])
    print("Average mastery:", teacher_data["average_mastery"])
    print("Average accuracy:", teacher_data["average_accuracy"])

    print("\nSTUDENTS NEEDING SUPPORT")

    for student in get_students_needing_support():
        print(student)

    print("\nAnalytics engine test completed.")
