import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

def embed_note_and_save_faiss(text: str, index_path: str = "faiss_index"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    db = FAISS.from_texts(chunks, embedding=embeddings)

    db.save_local(index_path)
    print(f"FAISS index zapisany do: {index_path}")
    
def search_in_faiss(query: str, index_path: str = "faiss_index", k: int = 3) -> list[str]:
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    results = db.similarity_search(query, k=k)
    return [r.page_content for r in results]