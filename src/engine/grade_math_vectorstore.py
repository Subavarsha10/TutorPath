
import json
import os
import zipfile
from pathlib import Path

import chromadb
import streamlit as st
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORSTORE_PATH = PROJECT_ROOT / "vectorstore"

COLLECTION_NAME = "tutorpath_grade_mathematics"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

HF_REPO_ID = "subavarsha10/tutorpath-vectorstore"
HF_FILENAME = "tutorpath_vectorstore.zip"


def ensure_vectorstore():
    db_file = VECTORSTORE_PATH / "chroma.sqlite3"

    if db_file.exists():
        return

    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)

    token = st.secrets.get("HF_TOKEN")

    if not token:
        raise RuntimeError("HF_TOKEN is missing from Streamlit Secrets.")

    archive_path = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=HF_FILENAME,
        repo_type="model",
        token=token
    )

    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(VECTORSTORE_PATH)

    if not db_file.exists():
        raise RuntimeError(
            "The downloaded ZIP does not contain chroma.sqlite3 "
            "at the expected location."
        )


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(MODEL_NAME)


ensure_vectorstore()

embedding_model = load_embedding_model()

client = chromadb.PersistentClient(
    path=str(VECTORSTORE_PATH)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def load_grade_chunks(grade):
    chunk_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / f"grade_{grade}"
        / "math_chunks.jsonl"
    )

    if not chunk_file.exists():
        return []

    chunks = []

    with open(chunk_file, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def index_grade_content(grade):
    chunks = load_grade_chunks(grade)

    if not chunks:
        return 0

    documents = [chunk["text"] for chunk in chunks]

    embeddings = embedding_model.encode(
        documents,
        show_progress_bar=False
    ).tolist()

    ids = [
        f"grade_{grade}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            **chunk.get("metadata", {}),
            "grade": str(grade)
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_grade_knowledge(query, grade, top_k=3):
    grade = str(grade)

    if grade not in ["8", "9", "10"]:
        return []

    if collection.count() == 0:
        return []

    query_embedding = embedding_model.encode(
        [query],
        show_progress_bar=False
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        where={"grade": grade},
        include=["documents", "metadatas", "distances"]
    )

    output = []

    for i, document in enumerate(results["documents"][0]):
        output.append({
            "text": document,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return output
