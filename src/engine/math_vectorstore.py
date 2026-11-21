
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from src.engine.math_chunker import load_mathematics_documents


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_NAME = "tutorpath_mathematics"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTORSTORE_PATH = PROJECT_ROOT / "vectorstore"

DATA_PATH = PROJECT_ROOT / "data" / "mathematics"


# ---------------------------------------
# LOAD EMBEDDING MODEL
# ---------------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(MODEL_NAME)


# ---------------------------------------
# INITIALISE CHROMADB
# ---------------------------------------

client = chromadb.PersistentClient(
    path=str(VECTORSTORE_PATH)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


# ---------------------------------------
# CREATE MATHEMATICS VECTOR STORE
# ---------------------------------------

def create_math_vectorstore():

    print("\nLoading mathematics documents...")

    chunks = load_mathematics_documents(DATA_PATH)

    if not chunks:
        print("No mathematics chunks found.")
        return

    documents = [chunk["text"] for chunk in chunks]

    metadatas = [chunk["metadata"] for chunk in chunks]

    ids = [
        f"math_chunk_{index}"
        for index in range(len(chunks))
    ]

    print(f"Total chunks: {len(documents)}")

    print("\nGenerating embeddings...")

    embeddings = embedding_model.encode(
        documents,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("\nSaving embeddings to ChromaDB...")

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("\nMathematics vector store created!")

    print("Collection:", COLLECTION_NAME)

    print("Stored documents:", collection.count())


# ---------------------------------------
# SEARCH MATHEMATICS KNOWLEDGE
# ---------------------------------------

def search_math_knowledge(query, top_k=3):

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
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for index, document in enumerate(results["documents"][0]):

        matches.append({
            "text": document,
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return matches


# ---------------------------------------
# TESTING
# ---------------------------------------

if __name__ == "__main__":

    create_math_vectorstore()

    print("\nTesting mathematics retrieval...")

    query = "Explain the distributive property in algebra."

    results = search_math_knowledge(query)

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")

        print("Topic:", result["metadata"].get("Subtopic"))

        print("Content:", result["text"])

        print("Distance:", result["distance"])

        print("-" * 50)
