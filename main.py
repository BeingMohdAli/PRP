from fastapi import FastAPI, UploadFile, File, Depends, Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_mistralai import ChatMistralAI
from slowapi.errors import RateLimitExceeded
import shutil
import os
import config
from retriever import hybrid_retrieve
from ingest import ingest_documents
from security import verify_api_key, validate_query, limiter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded, slow down"})


class QueryRequest(BaseModel):
    question: str
    filename: str | None = None   # metadata.source to scope search to


@app.post("/query")
@limiter.limit("10/minute")
def query(request: Request, body: QueryRequest, auth: None = Depends(verify_api_key)):
    validate_query(body.question)

    results = hybrid_retrieve(body.question, k=5, filename=body.filename)
    context = "\n\n".join(r["content"] for r in results)

    prompt = f"""Answer the question based only on the context below.

Context:
{context}

Question: {body.question}
"""

    llm = ChatMistralAI(model="mistral-small-latest", api_key=config.MISTRAL_API_KEY)
    response = llm.invoke(prompt)

    return {"answer": response.content, "sources": results}


@app.post("/upload")
@limiter.limit("5/minute")
async def upload_pdf(request: Request, file: UploadFile = File(...), auth: None = Depends(verify_api_key)):
    save_path = os.path.join("./data", file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader(save_path)
    docs = loader.load()

    count = ingest_documents(docs)
    return {"filename": file.filename, "chunks_ingested": count}


@app.get("/documents")
def list_documents(auth: None = Depends(verify_api_key)):
    from supabase import create_client
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    response = supabase.table("documents").select("metadata").execute()
    sources = set()
    for row in response.data:
        src = row["metadata"].get("source")
        if src:
            sources.add(src)
    return {"documents": sorted(sources)}

from fastapi import Path

@app.delete("/documents/{filename}")
def delete_document(filename: str, auth: None = Depends(verify_api_key)):
    from supabase import create_client
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

    response = supabase.table("documents").delete().eq("metadata->>source", filename).execute()

    deleted_count = len(response.data) if response.data else 0
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'")

    return {"filename": filename, "chunks_deleted": deleted_count}