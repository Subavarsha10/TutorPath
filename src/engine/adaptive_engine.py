
import sqlite3
from pathlib import Path


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "tutorpath.db"


# --------------------------------------------------
# INITIALISE DATABASE
# --------------------------------------------------

def initialize_database():

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mastery_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            mastery_score INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            UNIQUE(student_id, topic)
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# GET STUDENT MASTERY
# --------------------------------------------------

def get_mastery(student_id, topic):

    initialize_database()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT mastery_score, attempts, correct_answers
        FROM mastery_records
        WHERE student_id = ? AND topic = ?
    """, (student_id, topic))

    record = cursor.fetchone()
    connection.close()

    if record is None:
        return {
            "mastery_score": 0,
            "attempts": 0,
            "correct_answers": 0
        }

    return {
        "mastery_score": record[0],
        "attempts": record[1],
        "correct_answers": record[2]
    }


# --------------------------------------------------
# UPDATE MASTERY AFTER AN ATTEMPT
# --------------------------------------------------

def record_attempt(student_id, topic, is_correct):

    initialize_database()

    current = get_mastery(student_id, topic)

    score = current["mastery_score"]
    attempts = current["attempts"]
    correct_answers = current["correct_answers"]

    attempts += 1

    if is_correct:
        score += 10
        correct_answers += 1
    else:
        score -= 5

    # Keep mastery between 0 and 100
    score = max(0, min(100, score))

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO mastery_records (
            student_id,
            topic,
            mastery_score,
            attempts,
            correct_answers
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(student_id, topic)
        DO UPDATE SET
            mastery_score = excluded.mastery_score,
            attempts = excluded.attempts,
            correct_answers = excluded.correct_answers
    """, (
        student_id,
        topic,
        score,
        attempts,
        correct_answers
    ))

    connection.commit()
    connection.close()

    return get_mastery(student_id, topic)


# --------------------------------------------------
# RECOMMEND PRACTICE DIFFICULTY
# --------------------------------------------------

def get_recommended_difficulty(mastery_score):

    if mastery_score < 40:
        return "Foundational"

    elif mastery_score < 70:
        return "Intermediate"

    else:
        return "Advanced"


# --------------------------------------------------
# GET COMPLETE LEARNING STATUS
# --------------------------------------------------

def get_learning_status(student_id, topic):

    progress = get_mastery(student_id, topic)

    difficulty = get_recommended_difficulty(
        progress["mastery_score"]
    )

    return {
        **progress,
        "difficulty": difficulty
    }


# --------------------------------------------------
# TEST THE ADAPTIVE ENGINE
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH ADAPTIVE LEARNING ENGINE")
    print("=" * 45)

    student_id = "demo_student"
    topic = "Algebra"

    initialize_database()

    print("\nRecording practice attempts...")

    for attempt in range(1, 6):

        result = record_attempt(
            student_id,
            topic,
            is_correct=True
        )

        print(f"\nAttempt {attempt}")
        print("Mastery:", result["mastery_score"])
        print(
            "Recommended difficulty:",
            get_recommended_difficulty(result["mastery_score"])
        )

    print("\nFINAL LEARNING STATUS")
    print("-" * 45)

    status = get_learning_status(student_id, topic)

    print("Student:", student_id)
    print("Topic:", topic)
    print("Mastery:", status["mastery_score"])
    print("Total attempts:", status["attempts"])
    print("Correct answers:", status["correct_answers"])
    print("Difficulty:", status["difficulty"])

    print("\nAdaptive engine test completed.")
