
import json
import sys
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

SUPPORTED_GRADES = ["8", "9", "10"]


# --------------------------------------------------
# TEXT SPLITTER
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


# --------------------------------------------------
# LOAD EXTRACTED PDF PAGES
# --------------------------------------------------

def load_extracted_pages(grade):

    if grade not in SUPPORTED_GRADES:
        raise ValueError("Supported grades are 8, 9 and 10.")

    input_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / f"grade_{grade}"
        / "extracted_pages.jsonl"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Extracted PDF data not found: {input_file}"
        )

    pages = []

    with input_file.open("r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                pages.append(json.loads(line))

    if not pages:
        raise ValueError("No extracted pages available.")

    return pages


# --------------------------------------------------
# CHUNK EXTRACTED CONTENT
# --------------------------------------------------

def create_grade_chunks(grade):

    if grade not in SUPPORTED_GRADES:
        raise ValueError("Supported grades are 8, 9 and 10.")

    pages = load_extracted_pages(grade)

    all_chunks = []

    for page in pages:

        page_text = page["text"]
        page_metadata = page["metadata"]

        text_chunks = text_splitter.split_text(page_text)

        # Include PDF filename to avoid ID collisions
        source_name = Path(
            page_metadata["source"]
        ).stem

        for index, chunk_text in enumerate(text_chunks):

            if not chunk_text.strip():
                continue

            chunk_metadata = {
                **page_metadata,
                "chunk_index": index,
                "topic": "Unclassified",
                "chapter": "Unclassified"
            }

            all_chunks.append({

                "id": (
                    f"grade_{grade}_"
                    f"{source_name}_"
                    f"page_{page_metadata['page_number']}_"
                    f"chunk_{index}"
                ),

                "text": chunk_text,

                "metadata": chunk_metadata

            })

    return all_chunks


# --------------------------------------------------
# SAVE PROCESSED CHUNKS
# --------------------------------------------------

def save_grade_chunks(chunks, grade):

    output_directory = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / f"grade_{grade}"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_directory / "math_chunks.jsonl"

    with output_file.open("w", encoding="utf-8") as file:

        for chunk in chunks:

            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    return output_file


# --------------------------------------------------
# PROCESS A GRADE
# --------------------------------------------------

def process_grade(grade):

    print(f"\nProcessing Mathematics - Grade {grade}")
    print("=" * 45)

    pages = load_extracted_pages(grade)

    print("Pages loaded:", len(pages))

    chunks = create_grade_chunks(grade)

    print("Chunks generated:", len(chunks))

    output_file = save_grade_chunks(chunks, grade)

    print("Saved to:", output_file)

    if chunks:

        print("\nSAMPLE CHUNK")
        print("-" * 45)

        print(chunks[0]["text"][:400])

        print("\nSAMPLE METADATA")
        print(chunks[0]["metadata"])

    return chunks


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH GRADE-AWARE CHUNKER")
    print("=" * 45)

    if len(sys.argv) < 2:

        print("Usage:")
        print("python -m src.engine.grade_math_chunker 8")
        print("python -m src.engine.grade_math_chunker 9")
        print("python -m src.engine.grade_math_chunker 10")

        sys.exit(1)

    selected_grade = sys.argv[1]

    try:

        chunks = process_grade(selected_grade)

        print("\nCHUNKING COMPLETED")
        print("Total chunks:", len(chunks))

    except Exception as error:

        print("\nCHUNKING ERROR")
        print(error)
