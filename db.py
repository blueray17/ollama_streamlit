import sqlite3
import os
from datetime import datetime

DB_PATH = "/app/rag_documents.db"  # Path ke database dalam container
UPLOAD_FOLDER = "/app/uploaded_docs"  # Path folder upload dalam container

# Pastikan folder upload tersedia
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inisialisasi dan buat tabel jika belum ada
def init_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            content TEXT,
            uploaded_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Fungsi menyimpan dokumen ke SQLite
def save_document_to_db(filename, content, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO documents (filename, content, uploaded_at)
        VALUES (?, ?, ?)
    """, (filename, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Fungsi membaca semua isi dokumen dari DB
def load_all_documents_from_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT content FROM documents")
    results = c.fetchall()
    conn.close()
    return "\n".join([row[0] for row in results])
