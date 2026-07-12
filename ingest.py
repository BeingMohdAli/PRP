from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_mistralai import MistralAIEmbeddings
from supabase import create_client
import os
import config


def ingest_documents(raw_docs):
    if not raw_docs:
        print("No documents to ingest — check your ./data folder.")
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    chunks = splitter.split_documents(raw_docs)

    if not chunks:
        print("Documents loaded but produced no usable text chunks.")
        return 0

    # Clean the source path down to just the filename so metadata matches
    # exactly what the frontend sends back after upload.
    for chunk in chunks:
        if "source" in chunk.metadata:
            chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])

    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    embeddings = MistralAIEmbeddings(model="mistral-embed", api_key=config.MISTRAL_API_KEY)

    for chunk in chunks:
        vector = embeddings.embed_query(chunk.page_content)
        supabase.table("documents").insert({
            "content": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": vector
        }).execute()

    print(f"Ingested {len(chunks)} chunks into Supabase.")
    return len(chunks)


def load_pdfs_from_folder(folder_path):
    raw_docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, filename))
            raw_docs.extend(loader.load())
    return raw_docs


if __name__ == "__main__":
    docs = load_pdfs_from_folder("./data")
    ingest_documents(docs)