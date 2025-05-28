import os
import streamlit as st
from db import save_document_to_db, init_db
from rag_logic import build_vectorstore, jawab_pertanyaan
import shutil
import subprocess
from datetime import datetime

# Path direktori yang digunakan
UPLOAD_FOLDER = "/app/uploaded_docs"
VECTORSTORE_FOLDER = "/app/vectorstore"
RIWAYAT_FILE = "/app/jawaban.txt"

# Inisialisasi database dan folder
init_db()

# Fungsi untuk menghapus dokumen
def hapus_dokumen(nama_file):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, nama_file))
        return True
    except Exception as e:
        return False

# Fungsi untuk menampilkan daftar dokumen yang diupload
def tampilkan_dokumen_dan_opsi_hapus():
    st.sidebar.subheader("🗂️ Dokumen Diunggah")
    dokumen = os.listdir(UPLOAD_FOLDER)
    if dokumen:
        for file in dokumen:
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                st.markdown(f"- {file}")
            with col2:
                if st.button("❌", key=file):
                    if hapus_dokumen(file):
                        st.sidebar.success(f"{file} dihapus.")
                        st.cache_resource.clear()  # Reset cache vectorstore
                        st.experimental_rerun()
    else:
        st.sidebar.info("Belum ada dokumen.")

# Setup Streamlit UI
st.set_page_config(page_title="Tanya Dokumen | RAG Lokal", layout="wide")
st.title("📚 Tanya Dokumen Modular | RAG Lokal")

# Sidebar: Upload dan Pilih Model
st.sidebar.header("⚙️ Konfigurasi")
selected_model = st.sidebar.selectbox("Model Ollama", ["llama3", "mistral", "gemma", "llama2"])

uploaded_files = st.sidebar.file_uploader("📥 Upload PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        with open(os.path.join(UPLOAD_FOLDER, file.name), "wb") as f:
            f.write(file.read())
    st.sidebar.success("File berhasil diunggah. Refresh halaman jika tidak muncul.")

tampilkan_dokumen_dan_opsi_hapus()

# Bangun vectorstore jika ada dokumen
if os.listdir(UPLOAD_FOLDER):
    vectordb = build_vectorstore()
else:
    st.warning("Silakan unggah minimal satu dokumen PDF atau TXT terlebih dahulu.")
    st.stop()

# Kolom utama: Tanya dan Riwayat
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("❓ Ajukan Pertanyaan")
    query = st.text_input("Pertanyaan", placeholder="Contoh: Apa isi buku pedoman?")
    if st.button("Tanyakan"):
        with st.spinner("Sedang mencari jawaban..."):
            jawaban = jawab_pertanyaan(query, selected_model, vectordb)
            st.markdown(f"**Jawaban:**\n\n{jawaban}")

            # Simpan riwayat pertanyaan dan jawaban
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(RIWAYAT_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}]\nPertanyaan: {query}\nJawaban: {jawaban}\n{'='*60}\n")

with col2:
    st.subheader("📜 Riwayat Tanya Jawab")
    if os.path.exists(RIWAYAT_FILE):
        with open(RIWAYAT_FILE, "r", encoding="utf-8") as f:
            history = f.read()
        st.text_area("Riwayat", value=history, height=500)
    else:
        st.info("Belum ada pertanyaan sebelumnya.")
