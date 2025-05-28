import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import subprocess
from db import load_all_documents_from_db

VECTORSTORE_FOLDER = "/app/vectorstore"  # Path vectorstore dalam container
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # Model untuk embedding

# Fungsi untuk membangun vectorstore
def build_vectorstore():
    raw_text = load_all_documents_from_db()  # Ambil teks dari DB
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(raw_text)

    if os.path.exists(VECTORSTORE_FOLDER):
        shutil.rmtree(VECTORSTORE_FOLDER)

    embed = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vectordb = Chroma.from_texts(chunks, embedding=embed, persist_directory=VECTORSTORE_FOLDER)
    vectordb.persist()
    return vectordb

# Fungsi untuk menjawab pertanyaan
def jawab_pertanyaan(query, model, vectordb):
    docs = vectordb.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Gunakan informasi berikut untuk menjawab pertanyaan:

{context}

Pertanyaan: {query}
Jawaban:
    """

    result = subprocess.run(["ollama", "run", model, prompt], stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()
