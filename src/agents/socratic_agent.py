
import os

from dotenv import load_dotenv
from groq import Groq

from src.engine.grade_math_vectorstore import search_grade_knowledge
from src.agents.diagnostic_agent import diagnose_misconception


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"

SUPPORTED_GRADES = ["8", "9", "10"]


# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------

def get_groq_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please configure your .env file."
        )

    return Groq(api_key=api_key)


# --------------------------------------------------
# SOCRATIC TUTOR SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are TutorPath, an intelligent and patient mathematics tutor
for students in Classes 8 to 10 following the Karnataka State Board.

Your teaching approach is based on Socratic learning.

YOUR RESPONSIBILITIES:

1. Understand the student's mathematics question.
2. Identify the mathematical concept involved.
3. Examine the student's working carefully.
4. Use the provided misconception analysis as a possible clue.
5. Guide the student using questions and hints instead of immediately
   providing the final answer.
6. Acknowledge correct steps and explain mistakes patiently.
7. Give one useful hint at a time.
8. Use simple language suitable for school students.
9. Never assume a misconception is certain without sufficient evidence.
10. If the student remains stuck after multiple attempts, provide
    a more detailed explanation.

IMPORTANT TEACHING RULES:

- Never immediately reveal the final answer.
- Encourage students to think independently.
- Break complex problems into smaller steps.
- Use examples when they help explain a concept.
- Be encouraging, patient and supportive.
- Do not invent mathematical rules or facts.
- Prefer retrieved learning material when relevant.
- If the retrieved material does not cover the question,
  use reliable mathematical knowledge carefully.
"""


# --------------------------------------------------
# GRADE-AWARE KNOWLEDGE RETRIEVAL
# --------------------------------------------------

def retrieve_grade_knowledge(question, student_work, grade):

    search_query = f"{question} {student_work}".strip()

    results = search_grade_knowledge(
        query=search_query,
        grade=str(grade),
        top_k=3
    )

    if not results:
        return ""

    context_parts = []

    for result in results:

        text = result.get("text", "")
        metadata = result.get("metadata", {})

        if text:

            source = metadata.get(
                "source",
                "Mathematics learning material"
            )

            page = metadata.get("page_number", "Unknown")

            context_parts.append(
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{text}"
            )

    return "\n\n".join(context_parts)


# --------------------------------------------------
# SOCRATIC RESPONSE GENERATION
# --------------------------------------------------

def get_socratic_response(question, student_work="", grade="8"):

    question = question.strip()
    student_work = student_work.strip()
    grade = str(grade)

    if not question:
        return "Please enter a mathematics question."

    if grade not in SUPPORTED_GRADES:
        return "Please select a valid class: 8, 9 or 10."

    # STEP 1: Retrieve grade-specific knowledge

    try:

        context = retrieve_grade_knowledge(
            question=question,
            student_work=student_work,
            grade=grade
        )

    except Exception as error:

        print("Knowledge retrieval error:", error)

        return (
            "I couldn't access the mathematics learning material "
            "right now. Please try again."
        )

    if not context:

        context = (
            "No specific textbook reference was retrieved. "
            "Use reliable mathematical knowledge and explain "
            "the concept at the student's class level."
        )

    # STEP 2: Diagnose possible misconceptions

    try:

        diagnosis = diagnose_misconception(
            question=question,
            student_work=student_work
        )

        if diagnosis["detected"]:

            diagnosis_context = f"""
Possible misconception: {diagnosis['misconception']}

Mathematical concept: {diagnosis['concept']}

Explanation: {diagnosis['explanation']}

Suggested hint: {diagnosis['hint']}

Confidence: {diagnosis['confidence']}
"""

        else:

            diagnosis_context = """
No specific misconception has been confidently identified.

Examine the student's reasoning carefully.
Do not assume that the student has made a mistake.
"""

    except Exception as error:

        print("Misconception diagnosis error:", error)

        diagnosis_context = """
Misconception analysis is temporarily unavailable.
Examine the student's working independently.
Do not assume that the student has made a mistake.
"""

    # STEP 3: Initialise Groq

    try:

        client = get_groq_client()

        # STEP 4: Generate Socratic response

        response = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": f"""
STUDENT'S CLASS:

Class {grade}


RELEVANT MATHEMATICS LEARNING MATERIAL:

{context}


STUDENT QUESTION:

{question}


STUDENT'S WORKING:

{student_work if student_work else "Not provided"}


MISCONCEPTION ANALYSIS:

{diagnosis_context}


YOUR TASK:

Use the retrieved mathematics material and possible
misconception analysis to guide the student.

Give one useful Socratic hint at a time.

Explain the underlying concept when necessary.

Do not immediately reveal the final answer.

If the diagnosis is uncertain, ask the student to explain
their reasoning before identifying a specific mistake.

Keep your explanation appropriate for Class {grade}.
"""
                }
            ],

            temperature=0.4,
            max_completion_tokens=500
        )

        answer = response.choices[0].message.content

        if not answer:
            return "I couldn't generate a response. Please try again."

        return answer.strip()

    except Exception as error:

        print("Groq response generation error:", error)

        return (
            "I'm having trouble generating a response right now. "
            "Please check your API configuration and try again."
        )


# --------------------------------------------------
# MODULE TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH SOCRATIC AI TUTOR")
    print("=" * 45)

    grade = input("Enter class (8, 9 or 10): ").strip()

    question = input("Enter mathematics question: ").strip()

    student_work = input(
        "Enter your working (optional): "
    ).strip()

    print("\nGenerating AI response...")

    answer = get_socratic_response(
        question=question,
        student_work=student_work,
        grade=grade
    )

    print("\nTUTORPATH RESPONSE")
    print("-" * 45)
    print(answer)
    print("-" * 45)
