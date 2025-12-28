# ingest_pdfs.py
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain-chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

if not os.path.exists("data"):
    os.makedirs("data")

loader = PyPDFDirectoryLoader("data/")
docs = loader.load()

if not docs:
    print("⚠️ No PDFs in data/ — creating empty Chroma DB.")
    docs = [{"page_content": "Default residency context.", "metadata": {}}]

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="chroma_db"
)
print("✅ Chroma DB built.")
