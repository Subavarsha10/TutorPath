
from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

HEADERS_TO_SPLIT = [
    ("#", "Main Topic"),
    ("##", "Subtopic")
]


# ---------------------------------------
# MATHEMATICS DOCUMENT CHUNKER
# ---------------------------------------

def chunk_markdown_file(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Mathematics file not found: {file_path}"
        )

    if file_path.suffix.lower() != ".md":
        raise ValueError("Only Markdown files are supported.")

    # Read mathematics document
    text = file_path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("The mathematics document is empty.")

    # Split document based on Markdown headings
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT
    )

    sections = markdown_splitter.split_text(text)

    # Split large sections into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for section in sections:

        section_chunks = text_splitter.split_text(
            section.page_content
        )
curriculum.json
        for content in section_chunks:

            if content.strip():

                chunks.append({
                    "text": content,
                    "metadata": {
                        **section.metadata,
                        "source": file_path.name,
                        "subject": "Mathematics",
                        "grade": "8-10",
                        "topic": "Algebra"
                    }
                })

    return chunks


# ---------------------------------------
# LOAD ALL MATHEMATICS DOCUMENTS
# ---------------------------------------

def load_mathematics_documents(directory):

    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    markdown_files = list(directory.glob("*.md"))

    if not markdown_files:
        raise ValueError(
            "No Markdown mathematics documents found."
        )

    all_chunks = []

    for file_path in markdown_files:

        chunks = chunk_markdown_file(file_path)

        all_chunks.extend(chunks)

    return all_chunks


# ---------------------------------------
# TESTING
# ---------------------------------------

if __name__ == "__main__":

    data_directory = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "mathematics"
    )

    chunks = load_mathematics_documents(data_directory)

    print("\nTutorPath Mathematics Chunking")
    print("--------------------------------")

    print(f"Total chunks created: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):

        print(f"\nChunk {index}")
        print("Topic:", chunk["metadata"].get("Subtopic"))
        print("Source:", chunk["metadata"]["source"])
        print("Content:", chunk["text"][:200])
        print("--------------------------------")
