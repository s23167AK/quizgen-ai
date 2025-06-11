import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging
logger = logging.getLogger(__name__)

load_dotenv()

def embed_note_and_save_faiss(text: str, index_path: str = "faiss_index"):
    logger.info("Embedding text into FAISS index at %s", index_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    documents = [Document(page_content=chunk, metadata={"full_text": text}) for chunk in chunks]

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    db = FAISS.from_documents(documents, embedding=embeddings)

    db.save_local(index_path)
    print(f"FAISS index zapisany do: {index_path}")
    logger.info("FAISS index saved to %s", index_path)
