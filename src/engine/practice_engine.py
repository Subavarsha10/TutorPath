
import json
import random
import re

from src.engine.grade_math_vectorstore import search_grade_knowledge
from src.agents.socratic_agent import get_groq_client, MODEL_NAME


SUPPORTED_GRADES = ["8", "9", "10"]

SUPPORTED_DIFFICULTIES = [
    "Foundational",
    "Intermediate",
    "Advanced"
]


def get_difficulty(mastery_score):
    from src.engine.adaptive_engine import get_recommended_difficulty
    return get_recommended_difficulty(mastery_score)


def retrieve_practice_context(grade, topic):
    results = search_grade_knowledge(
        query=f"Class {grade} Mathematics chapter {topic}: definitions, concepts, worked examples and exercises",
        grade=str(grade),
        top_k=5
    )

    context = []

    for result in results:
        metadata = result.get("metadata", {})
        text = result.get("text", "")

        if text:
            context.append(
                f"Source: {metadata.get('source', 'Textbook')}\n"
                f"Page: {metadata.get('page_number', 'Unknown')}\n"
                f"{text}"
            )

    return "\n\n".join(context)


def parse_generated_questions(content):
    content = content.strip()

    # Remove Markdown code fences if the model includes them.
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    data = json.loads(content)

    if isinstance(data, dict):
        questions = data.get("questions", [])
    elif isinstance(data, list):
        questions = data
    else:
        questions = []

    valid_questions = []

    for item in questions:
        if not isinstance(item, dict):
            continue

        required = ["question", "answer", "hint", "explanation"]

        if all(
            isinstance(item.get(key), str) and item[key].strip()
            for key in required
        ):
            valid_questions.append({
                "question": item["question"].strip(),
                "answer": item["answer"].strip(),
                "hint": item["hint"].strip(),
                "explanation": item["explanation"].strip(),
                "difficulty": item.get("difficulty", "Intermediate")
            })

    return valid_questions


def generate_practice_questions(
    grade,
    topic,
    difficulty,
    number=5
):
    grade = str(grade)

    if grade not in SUPPORTED_GRADES:
        raise ValueError("Select Class 8, 9 or 10.")

    if difficulty not in SUPPORTED_DIFFICULTIES:
        raise ValueError("Invalid practice difficulty.")

    number = max(1, min(int(number), 20))

    context = retrieve_practice_context(grade, topic)

    if not context:
        raise ValueError(
            f"No textbook content was retrieved for Class {grade}, "
            f"chapter '{topic}'. Please check the indexed textbook material."
        )

    difficulty_guidance = {
        "Foundational": (
            "Focus on basic definitions, direct calculations and "
            "simple applications."
        ),
        "Intermediate": (
            "Use multi-step problems and applications of the chapter concepts."
        ),
        "Advanced": (
            "Use challenging, multi-step and reasoning-based problems "
            "appropriate for the selected class."
        )
    }

    client = get_groq_client()

    prompt = f"""
You are generating mathematics practice questions for TutorPath.

STUDENT CLASS: {grade}
CURRICULUM: Karnataka State Board
SUBJECT: Mathematics
CHAPTER: {topic}
TARGET DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {number}

TEXTBOOK MATERIAL:
{context}

DIFFICULTY GUIDANCE:
{difficulty_guidance[difficulty]}

INSTRUCTIONS:
1. Generate exactly {number} original practice questions.
2. Questions must be appropriate for Class {grade}.
3. Keep every question relevant to the selected chapter.
4. Use the supplied textbook material as the primary reference.
5. Do not introduce concepts from higher classes.
6. Provide a mathematically correct answer for each question.
7. Include a short hint without revealing the answer.
8. Include a clear step-by-step explanation.
9. Avoid duplicate or nearly identical questions.
10. Assign each question one of these difficulty labels:
    Foundational, Intermediate, Advanced.
11. Return valid JSON only. Do not include Markdown or additional text.

REQUIRED JSON FORMAT:
{{
  "questions": [
    {{
      "question": "Question text",
      "answer": "Correct answer",
      "hint": "A useful hint",
      "explanation": "Explanation of the solution",
      "difficulty": "{difficulty}"
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful school mathematics question setter. "
                    "Check mathematical answers before returning questions. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_completion_tokens=5000
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("The AI did not return any practice questions.")

    questions = parse_generated_questions(content)

    if len(questions) != number:
        raise ValueError(
            f"The AI returned {len(questions)} valid questions instead "
            f"of {number}. Please start the session again."
        )

    for question in questions:
        if question["difficulty"] not in SUPPORTED_DIFFICULTIES:
            question["difficulty"] = difficulty

    random.shuffle(questions)

    return questions


def get_adaptive_questions(
    topic,
    mastery_score,
    number=5,
    grade="8"
):
    difficulty = get_difficulty(mastery_score)

    questions = generate_practice_questions(
        grade=grade,
        topic=topic,
        difficulty=difficulty,
        number=number
    )

    actual_levels = list(dict.fromkeys(
        question["difficulty"] for question in questions
    ))

    return {
        "grade": str(grade),
        "topic": topic,
        "mastery_score": mastery_score,
        "difficulty": difficulty,
        "questions": questions,
        "question_count": len(questions),
        "levels_used": actual_levels
    }
