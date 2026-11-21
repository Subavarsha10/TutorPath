
import json
from pathlib import Path

import streamlit as st
import pandas as pd

from src.analytics.analytics_engine import (
    get_student_analytics,
    get_teacher_analytics,
    get_students_needing_support
)

from src.agents.socratic_agent import get_socratic_response

from src.engine.adaptive_engine import get_learning_status

from src.engine.practice_session import (
    start_practice_session,
    submit_practice_answer,
    get_mastery_topic
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TutorPath - AI Maths Tutor",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# LOAD CURRICULUM
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

CURRICULUM_PATH = (
    PROJECT_ROOT
    / "data"
    / "mathematics"
    / "curriculum.json"
)

with CURRICULUM_PATH.open("r", encoding="utf-8") as file:
    curriculum = json.load(file)

grades = curriculum["grades"]


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "practice_session" not in st.session_state:
    st.session_state.practice_session = None

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "practice_feedback" not in st.session_state:
    st.session_state.practice_feedback = None

if "student_id" not in st.session_state:
    st.session_state.student_id = "demo_student_ui"


student_id = st.session_state.student_id


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🎓 TutorPath")

    st.success("Learning Platform Active")

    st.markdown("### Learning Space")

    selected_grade = st.selectbox(
        "Select your class",
        options=["8", "9", "10"],
        format_func=lambda value: f"Class {value}",
        key="selected_grade"
    )

    available_topics = grades[selected_grade]["topics"]

    selected_topic = st.selectbox(
        "Select mathematics chapter",
        options=available_topics,
        key="selected_topic"
    )

    st.divider()

    st.write("📘 Mathematics")
    st.write("🧠 Socratic AI Tutor")
    st.write("🎯 Adaptive Practice")
    st.write("📊 Learning Dashboard")

    st.divider()

    st.caption("Karnataka State Board | English Medium")
    st.caption("TutorPath | AI-powered learning")


mastery_topic = get_mastery_topic(
    selected_grade,
    selected_topic
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🎓 TutorPath")

st.subheader("Adaptive AI Mathematics Learning Platform")

st.write(
    "Learn mathematics through personalised AI tutoring, "
    "guided hints and adaptive practice."
)

st.caption(
    f"Currently learning: Class {selected_grade} | {selected_topic}"
)

st.divider()


# --------------------------------------------------
# STUDENT PROGRESS
# --------------------------------------------------

status = get_learning_status(
    student_id,
    mastery_topic
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Subject", "Mathematics")

with col2:
    st.metric(
        "Mastery Score",
        f"{status['mastery_score']}/100"
    )

with col3:
    st.metric(
        "Current Difficulty",
        status["difficulty"]
    )

st.progress(status["mastery_score"] / 100)

st.divider()


# --------------------------------------------------
# MAIN APPLICATION TABS
# --------------------------------------------------

tutor_tab, practice_tab, dashboard_tab = st.tabs(
    [
        "🤖 AI Mathematics Tutor",
        "🎯 Adaptive Practice",
        "📊 Dashboard"
    ]
)


# ==================================================
# TAB 1: SOCRATIC AI TUTOR
# ==================================================

with tutor_tab:

    st.header("Ask Your Mathematics Tutor")

    st.caption(
        f"Your tutor is currently set to Class {selected_grade}. "
        "Ask a question or share your mathematical reasoning."
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask a mathematics question...",
        key="tutor_chat_input"
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        try:

            with st.spinner("TutorPath is thinking..."):

                response = get_socratic_response(
                    question=prompt,
                    grade=selected_grade
                )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as error:

            st.error(
                f"Unable to generate a response: {error}"
            )

        st.rerun()

    if st.button("Clear Conversation"):

        st.session_state.messages = []
        st.rerun()


# ==================================================
# TAB 2: ADAPTIVE PRACTICE
# ==================================================

with practice_tab:

    st.header("Adaptive Mathematics Practice")

    st.write(
        "Practise the selected chapter with questions "
        "adjusted to your current mathematics mastery."
    )

    st.info(
        f"Class {selected_grade} | {selected_topic}"
    )

    current_status = get_learning_status(
        student_id,
        mastery_topic
    )

    st.subheader("Your Learning Progress")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Mastery",
            f"{current_status['mastery_score']}/100"
        )

    with col2:
        st.metric(
            "Attempts",
            current_status["attempts"]
        )

    with col3:
        st.metric(
            "Correct Answers",
            current_status["correct_answers"]
        )

    st.progress(
        current_status["mastery_score"] / 100
    )

    st.info(
        f"Recommended difficulty: {current_status['difficulty']}"
    )

    st.divider()

    question_count = st.selectbox(
        "How many questions would you like?",
        options=[5, 10, 15, 20],
        index=0,
        key="practice_question_count"
    )

    if st.button(
        "Start New Practice Session",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Generating textbook-based practice questions..."
            ):

                st.session_state.practice_session = (
                    start_practice_session(
                        student_id=student_id,
                        topic=selected_topic,
                        grade=selected_grade,
                        number=question_count
                    )
                )

            st.session_state.question_index = 0
            st.session_state.practice_feedback = None

            st.rerun()

        except Exception as error:

            st.session_state.practice_session = None

            st.error(
                f"Unable to start practice: {error}"
            )

    practice = st.session_state.practice_session

    # Clear a session if the student changes class,
    # chapter or requested question count.

    if practice and (
        practice["grade"] != selected_grade
        or practice["topic"] != selected_topic
        or practice["question_count"] != question_count
    ):

        st.session_state.practice_session = None
        st.session_state.question_index = 0
        st.session_state.practice_feedback = None

        practice = None

    if practice:

        questions = practice["questions"]

        question_index = st.session_state.question_index

        st.subheader("Your Practice Questions")

        st.write(
            f"Difficulty: **{practice['difficulty']}**"
        )

        st.caption(
            f"Class {practice['grade']} | "
            f"{practice['topic']} | "
            f"{practice['question_count']} questions"
        )

        if question_index < len(questions):

            current_question = questions[question_index]

            st.progress(
                (question_index + 1) / len(questions)
            )

            st.markdown(
                f"### Question {question_index + 1} "
                f"of {len(questions)}"
            )

            st.caption(
                f"Difficulty: {current_question['difficulty']}"
            )

            st.write(current_question["question"])

            with st.expander("Need a hint?"):
                st.write(current_question["hint"])

            with st.form(
                key=f"answer_form_{question_index}"
            ):

                student_answer = st.text_input(
                    "Enter your answer"
                )

                submitted = st.form_submit_button(
                    "Submit Answer"
                )

                if submitted:

                    if not student_answer.strip():

                        st.warning(
                            "Please enter an answer."
                        )

                    else:

                        result = submit_practice_answer(
                            student_id=student_id,
                            topic=practice["mastery_topic"],
                            question=current_question["question"],
                            student_answer=student_answer,
                            expected_answer=current_question["answer"],
                            explanation=current_question["explanation"]
                        )

                        st.session_state.practice_feedback = result

                        st.session_state.question_index += 1

                        st.rerun()

        else:

            st.success(
                "Practice session completed! Well done."
            )

            if st.button("Start Another Session"):

                st.session_state.practice_session = None
                st.session_state.question_index = 0
                st.session_state.practice_feedback = None

                st.rerun()

    else:

        st.info(
            "Choose your class and chapter in the sidebar, "
            "select the number of questions, and start a new session."
        )

    # ----------------------------------------------
    # LATEST ANSWER FEEDBACK
    # ----------------------------------------------

    feedback = st.session_state.practice_feedback

    if feedback:

        st.divider()

        st.subheader("Latest Answer Feedback")

        if feedback["is_correct"]:
            st.success(feedback["feedback"])
        else:
            st.error(feedback["feedback"])

        st.write(
            "**Expected Answer:**",
            feedback["expected_answer"]
        )

        if feedback.get("explanation"):
            st.info(feedback["explanation"])

        st.metric(
            "Updated Mastery Score",
            f"{feedback['mastery_score']}/100"
        )

        st.caption(
            f"Attempts: {feedback['attempts']} | "
            f"Correct answers: {feedback['correct_answers']}"
        )


# ==================================================
# TAB 3: STUDENT AND TEACHER DASHBOARD
# ==================================================

with dashboard_tab:

    st.header("📊 Learning Analytics Dashboard")

    # ----------------------------------------------
    # STUDENT DASHBOARD
    # ----------------------------------------------

    st.subheader("Student Performance")

    student_data = get_student_analytics(student_id)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Mastery Score",
            f"{student_data['mastery_score']}/100"
        )

    with col2:
        st.metric(
            "Total Attempts",
            student_data["total_attempts"]
        )

    with col3:
        st.metric(
            "Correct Answers",
            student_data["correct_answers"]
        )

    with col4:
        st.metric(
            "Accuracy",
            f"{student_data['accuracy']}%"
        )

    st.progress(
        student_data["mastery_score"] / 100
    )

    st.divider()

    # ----------------------------------------------
    # TEACHER DASHBOARD
    # ----------------------------------------------

    st.subheader("Teacher Overview")

    teacher_data = get_teacher_analytics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Students",
            teacher_data["total_students"]
        )

    with col2:
        st.metric(
            "Total Attempts",
            teacher_data["total_attempts"]
        )

    with col3:
        st.metric(
            "Average Mastery",
            f"{teacher_data['average_mastery']}/100"
        )

    with col4:
        st.metric(
            "Average Accuracy",
            f"{teacher_data['average_accuracy']}%"
        )

    st.divider()

    # ----------------------------------------------
    # STUDENT PERFORMANCE TABLE
    # ----------------------------------------------

    st.subheader("Student Performance Records")

    if teacher_data["students"]:

        st.dataframe(
            teacher_data["students"],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No student records available yet.")

    st.divider()

    # ----------------------------------------------
    # STUDENT MASTERY COMPARISON CHART
    # ----------------------------------------------

    st.subheader("Student Mastery Comparison")

    if teacher_data["students"]:

        chart_data = pd.DataFrame(
            teacher_data["students"]
        )

        chart_data["Student and Topic"] = (
            chart_data["student_id"].astype(str)
            + " - "
            + chart_data["topic"].astype(str)
        )

        chart_data = chart_data.set_index(
            "Student and Topic"
        )

        st.bar_chart(
            chart_data["mastery_score"],
            x_label="Student and Topic",
            y_label="Mastery Score",
            height=350
        )

    else:

        st.info(
            "No performance data available for the chart."
        )

    # ----------------------------------------------
    # STUDENTS NEEDING SUPPORT
    # ----------------------------------------------

    st.subheader("Students Requiring Additional Support")

    support_students = get_students_needing_support()

    if support_students:

        st.warning(
            f"{len(support_students)} student-topic records "
            "have mastery below 40."
        )

        st.dataframe(
            support_students,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No students currently require foundational support."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "TutorPath | Adaptive AI Mathematics Learning Platform"
)
