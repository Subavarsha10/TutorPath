# TutorPath
## Adaptive AI Mathematics Tutor with Misconception Diagnosis

### 1. Project Overview

TutorPath is an Agentic AI-powered adaptive mathematics tutoring platform designed to support school students studying Classes 8, 9 and 10 under the Karnataka State Board curriculum.

The platform combines textbook-based knowledge retrieval, AI-powered Socratic tutoring, misconception diagnosis and adaptive mathematics practice to provide a personalised learning experience.

Instead of directly providing answers, TutorPath encourages students to understand mathematical concepts through guided questions, hints and explanations.

### 2. Objectives

- Provide personalised mathematics learning support.
- Retrieve relevant information from prescribed mathematics textbooks.
- Guide students through Socratic questioning.
- Identify common mathematical misconceptions.
- Generate practice questions according to student proficiency.
- Track student performance through mastery scores.
- Provide learning analytics for students and teachers.

### 3. Key Features

**AI Mathematics Tutor**
- Interactive mathematics question-answering.
- Grade-specific textbook knowledge retrieval.
- Socratic hints and guided explanations.

**Misconception Diagnosis**
- Rule-based identification of common mathematical errors.
- Identification of incorrect mathematical reasoning.
- SymPy-based mathematical expression verification.

**Adaptive Practice**
- Grade and chapter selection.
- AI-generated textbook-grounded practice questions.
- Foundational, Intermediate and Advanced difficulty levels.
- Customisable practice sessions of 5, 10, 15 or 20 questions.

**Mastery Tracking**
- SQLite-based student progress storage.
- Chapter-wise and grade-wise mastery tracking.
- Adaptive difficulty recommendations.

**Learning Analytics Dashboard**
- Student performance overview.
- Teacher analytics.
- Student performance records.
- Mastery comparison charts.
- Identification of students requiring additional support.

### 4. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Frontend | Streamlit |
| AI Model | Groq API – GPT-OSS 20B |
| Vector Database | ChromaDB |
| Embedding Model | Sentence Transformers |
| Mathematical Verification | SymPy |
| Database | SQLite |
| Text Processing | LangChain Text Splitters |
| PDF Processing | PyMuPDF |
| Data Analysis | Pandas |

### 5. System Architecture

TutorPath follows a modular application architecture.

1. **Presentation Layer:** Streamlit provides the student interface, tutor interaction, practice interface and analytics dashboard.
2. **AI Application Layer:** Socratic tutoring, misconception diagnosis and adaptive practice modules manage learning interactions.
3. **Knowledge Retrieval Layer:** ChromaDB and Sentence Transformers retrieve relevant mathematics textbook content.
4. **Mathematical Verification Layer:** SymPy supports mathematical expression verification.
5. **Data Layer:** SQLite stores student mastery and practice performance.

### 6. Project Structure

```text
tutorpath/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
│
├── src/
│   ├── agents/
│   │   ├── socratic_agent.py
│   │   └── diagnostic_agent.py
│   │
│   ├── engine/
│   │   ├── math_engine.py
│   │   ├── adaptive_engine.py
│   │   ├── practice_engine.py
│   │   ├── practice_session.py
│   │   ├── grade_math_chunker.py
│   │   ├── grade_math_vectorstore.py
│   │   └── pdf_processor.py
│   │
│   ├── analytics/
│   │   └── analytics_engine.py
│   │
│   └── evaluation/
│       └── test_tutorpath.py
│
├── data/
│   ├── mathematics/
│   │   ├── algebra_basics.md
│   │   └── curriculum.json
│   ├── source_references/
│   └── processed/
│
├── database/
│   └── tutorpath.db
│
└── vectorstore/
```

### 7. Installation and Execution

**Prerequisites**
- Python 3.12
- Groq API key
- Visual Studio Code

**Step 1: Clone the repository**

```bash
git clone YOUR_REPOSITORY_URL
cd tutorpath
```

**Step 2: Create a virtual environment**

```bash
python -m venv venv
```

**Step 3: Activate the environment**

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

**Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 5: Configure environment variables**

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

**Step 6: Run the application**

```bash
streamlit run app.py
```

### 8. Project Limitations

- AI-generated questions require an active Groq API connection.
- Question quality depends on the retrieved textbook content and AI-generated answers.
- Mathematical answer evaluation currently uses normalised string comparison.
- Misconception diagnosis supports a limited set of common mathematical error patterns.
- The current application uses a demonstration student account rather than a complete authentication system.

### 9. Future Enhancements

- Student authentication and individual profiles.
- Expanded topic-wise mathematical question banks.
- More advanced mathematical answer evaluation.
- Teacher-managed classrooms and assignments.
- Detailed learning recommendations.
- Deployment as an accessible online learning platform.

### 10. Conclusion

TutorPath demonstrates how Agentic AI, retrieval-augmented generation, mathematical verification and adaptive learning techniques can be combined to support personalised mathematics education.

The platform aims to move beyond answer-based learning by encouraging conceptual understanding, independent reasoning and continuous improvement.