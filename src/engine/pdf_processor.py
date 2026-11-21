
import json
import sys
from pathlib import Path

import pymupdf


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUPPORTED_GRADES = ["8", "9", "10"]


# --------------------------------------------------
# EXTRACT CONTENT FROM ONE PDF
# --------------------------------------------------

def extract_pdf_pages(pdf_path, grade):

    pdf_path = Path(pdf_path)

    if grade not in SUPPORTED_GRADES:
        raise ValueError("Only Grades 8, 9 and 10 are supported.")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    extracted_pages = []

    with pymupdf.open(pdf_path) as document:

        if document.is_encrypted:
            raise ValueError("PDF is password protected.")

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text").strip()

            if not text:
                continue

            extracted_pages.append({

                "text": text,

                "metadata": {

                    "source": pdf_path.name,
                    "grade": grade,
                    "board": "Karnataka State Board",
                    "subject": "Mathematics",
                    "medium": "English",
                    "page_number": page_number,
                    "book_part": pdf_path.stem

                }

            })

    return extracted_pages


# --------------------------------------------------
# SAVE EXTRACTED CONTENT AS JSONL
# --------------------------------------------------

def save_extracted_pages(pages, grade):

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

    output_file = output_directory / "extracted_pages.jsonl"

    with output_file.open("w", encoding="utf-8") as file:

        for page in pages:

            file.write(
                json.dumps(page, ensure_ascii=False) + "\n"
            )

    return output_file


# --------------------------------------------------
# PROCESS ALL PDF FILES FOR A GRADE
# --------------------------------------------------

def process_grade_pdfs(grade):

    if grade not in SUPPORTED_GRADES:
        raise ValueError("Supported grades are 8, 9 and 10.")

    source_directory = (
        PROJECT_ROOT
        / "data"
        / "source_references"
        / f"grade_{grade}"
    )

    if not source_directory.exists():
        raise FileNotFoundError(
            f"Source directory not found: {source_directory}"
        )

    pdf_files = sorted(source_directory.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {source_directory}"
        )

    all_pages = []

    for pdf_file in pdf_files:

        print(f"\nProcessing: {pdf_file.name}")

        pages = extract_pdf_pages(
            pdf_path=pdf_file,
            grade=grade
        )

        print(f"Extracted pages: {len(pages)}")

        if not pages:
            print(
                "Warning: No selectable text found. "
                "This PDF may require OCR."
            )

        all_pages.extend(pages)

    if not all_pages:
        raise ValueError(
            "No text could be extracted from the available PDFs."
        )

    output_file = save_extracted_pages(
        all_pages,
        grade
    )

    print("\nEXTRACTION SUMMARY")
    print("-" * 40)
    print("Grade:", grade)
    print("PDF files processed:", len(pdf_files))
    print("Pages extracted:", len(all_pages))
    print("Output file:", output_file)

    return all_pages


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH MATHEMATICS PDF PROCESSOR")
    print("=" * 45)

    if len(sys.argv) < 2:

        print("Usage:")
        print("python -m src.engine.pdf_processor 8")
        print("python -m src.engine.pdf_processor 9")
        print("python -m src.engine.pdf_processor 10")

        sys.exit(1)

    selected_grade = sys.argv[1]

    try:

        pages = process_grade_pdfs(selected_grade)

        print("\nSAMPLE EXTRACTED CONTENT")
        print("-" * 40)

        print(pages[0]["text"][:500])

        print("\nPDF processing completed successfully.")

    except Exception as error:

        print("\nPROCESSING ERROR")
        print(error)
