
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTORSTORE_PATH = PROJECT_ROOT / "vectorstore"

COLLECTION_NAME = "tutorpath_grade_mathematics"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# --------------------------------------------------
# INITIALISE EMBEDDING MODEL
# --------------------------------------------------

print("Loading mathematics embedding model...")

embedding_model = SentenceTransformer(MODEL_NAME)


# --------------------------------------------------
# INITIALISE CHROMADB
# --------------------------------------------------

client = chromadb.PersistentClient(
    path=str(VECTORSTORE_PATH)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


# --------------------------------------------------
# LOAD GRADE CHUNKS
# --------------------------------------------------

def load_grade_chunks(grade):

    input_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / f"grade_{grade}"
        / "math_chunks.jsonl"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {input_file}"
        )

    chunks = []

    with input_file.open("r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                chunks.append(json.loads(line))

    return chunks


# --------------------------------------------------
# ADD GRADE CONTENT TO VECTOR STORE
# --------------------------------------------------

def index_grade_content(grade):

    print(f"\nIndexing Mathematics - Grade {grade}")

    chunks = load_grade_chunks(grade)

    if not chunks:
        print("No chunks available.")
        return 0

    documents = [
        chunk["text"] for chunk in chunks
    ]

    metadatas = [
        chunk["metadata"] for chunk in chunks
    ]

    ids = [
        chunk["id"] for chunk in chunks
    ]

    print("Generating embeddings...")

    embeddings = embedding_model.encode(
        documents,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("Saving content to ChromaDB...")

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("Indexed chunks:", len(chunks))

    return len(chunks)


# --------------------------------------------------
# SEARCH MATHEMATICS KNOWLEDGE
# --------------------------------------------------

def search_grade_knowledge(
    query,
    grade,
    top_k=3
):

    if grade not in ["8", "9", "10"]:
        raise ValueError("Grade must be 8, 9 or 10.")

    if collection.count() == 0:
        return []

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=min(top_k, collection.count()),
        where={"grade": grade},
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    matches = []

    if not results["documents"]:
        return matches

    for index, document in enumerate(results["documents"][0]):

        matches.append({

            "text": document,

            "metadata": results["metadatas"][0][index],

            "distance": results["distances"][0][index]

        })

    return matches


# --------------------------------------------------
# TEST VECTOR STORE
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTUTORPATH GRADE-AWARE VECTOR STORE")
    print("=" * 45)

    grade = input(
        "Enter grade to index (8, 9 or 10): "
    ).strip()

    try:

        total = index_grade_content(grade)

        print("\nIndexing completed.")
        print("Total chunks indexed:", total)

        query = input(
            "\nEnter a mathematics search query: "
        )

        results = search_grade_knowledge(
            query=query,
            grade=grade,
            top_k=3
        )

        print("\nSEARCH RESULTS")
        print("-" * 45)

        for index, result in enumerate(results, start=1):

            print(f"\nResult {index}")

            print("Grade:", result["metadata"]["grade"])

            print("Source:", result["metadata"]["source"])

            print("Page:", result["metadata"]["page_number"])

            print("Content:", result["text"][:300])

            print("Distance:", result["distance"])

        print("\nVector store test completed.")

    except Exception as error:

        print("\nVECTOR STORE ERROR")
        print(error)
def verify_all_grades():

    print("\nTUTORPATH VECTOR STORE VERIFICATION")
    print("=" * 45)

    print("Total chunks in collection:", collection.count())

    for grade in ["8", "9", "10"]:

        results = collection.get(
            where={"grade": grade},
            include=["metadatas"]
        )

        print(
            f"Class {grade}: {len(results['ids'])} chunks indexed"
        )

    print("\nVerification completed.")