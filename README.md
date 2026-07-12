![Uploading image.png…]()


# 📚 Reading Room — PDF Question Answering with RAG

Ask questions of your PDF documents, powered by a Retrieval-Augmented Generation (RAG) pipeline. Upload a document, and get accurate, source-grounded answers pulled directly from its content.

**Live demo:** deployed on AWS EC2 (backend) + Netlify (frontend)

---

## ✨ Features

- 📄 **PDF ingestion** — upload any PDF and it's automatically chunked and indexed
- 🔍 **Semantic search** — vector similarity search over document chunks using [Supabase](https://supabase.com) + `pgvector`
- 🎯 **Per-document scoping** — questions automatically stay scoped to the most recently uploaded document, or search across everything
- 🧠 **Mistral AI** — embeddings (`mistral-embed`) and answer generation (`mistral-small-latest`)
- 📊 **LangSmith tracing** — full observability into every retrieval and generation step
- 🔒 **Security layer** — API key authentication, rate limiting, and input validation
- 🗑️ **Document management** — delete a document and all its chunks on demand
- 🌐 **HTTPS everywhere** — Caddy + Let's Encrypt on the backend, Netlify on the frontend

---

## 🏗️ Architecture

```
PDF upload
    │
    ▼
Recursive text splitter (chunking)
    │
    ▼
Mistral embeddings ──────► Supabase (pgvector storage)
                                  │
User question ──► embed query ──► similarity search (scoped by document metadata)
                                  │
                                  ▼
                        Retrieved context chunks
                                  │
                                  ▼
                        Mistral LLM (answer generation)
                                  │
                                  ▼
                        Answer + cited sources
```

All requests pass through a security layer (API key check → rate limiter → input validation) before reaching the retrieval/generation logic, and every call is traced in LangSmith.

---

## 🛠️ Tech stack

| Layer            | Technology                          |
|-------------------|--------------------------------------|
| Backend framework  | FastAPI                             |
| Vector database    | Supabase (PostgreSQL + `pgvector`)  |
| Embeddings & LLM   | Mistral AI (`mistral-embed`, `mistral-small-latest`) |
| Text splitting     | LangChain `RecursiveCharacterTextSplitter` |
| Observability      | LangSmith                           |
| Rate limiting      | `slowapi`                           |
| Package manager    | `uv`                                |
| Deployment         | AWS EC2 (backend), Netlify (frontend), Caddy (HTTPS reverse proxy) |
| Frontend           | Vanilla HTML/CSS/JS                 |

---

## 📁 Project structure

```
├── config.py               # Loads environment variables
├── ingest.py                # PDF loading, chunking, embedding, Supabase insertion
├── retriever.py              # Vector similarity search via Supabase RPC
├── security.py               # API key check, rate limiter, input validation
├── main.py                   # FastAPI app — all endpoints
├── supabase_setup.sql        # One-time Supabase schema + search function
└── data/                       # Temporary storage for uploaded PDFs
```

---

## 🚀 Getting started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2. Install dependencies
```bash
uv sync
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```env
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-service-key
MISTRAL_API_KEY=your-mistral-api-key
APP_API_KEY=choose-your-own-secret-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=your-project-name
```

### 4. Set up the Supabase database
Run the contents of `supabase_setup.sql` in your Supabase project's SQL Editor. This creates the `documents` table, enables the `pgvector` extension, and sets up the `match_documents` similarity search function.

### 5. Run the server
```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.


---

## 🔌 API endpoints

| Method | Endpoint              | Description                                  |
|--------|------------------------|-----------------------------------------------|
| `POST`   | `/upload`               | Upload a PDF — chunks, embeds, and stores it |
| `POST`   | `/query`                | Ask a question, optionally scoped to a file  |
| `GET`    | `/documents`             | List all uploaded document names             |
| `DELETE` | `/documents/{filename}` | Remove a document and all its chunks         |

All endpoints require an `x-api-key` header matching `APP_API_KEY`.

---

## 🔒 Security notes

This is a **medium-complexity** implementation suitable for personal projects, prototypes, and small-scale deployments. For production use at scale, consider adding:
- Per-user authentication (rather than a single shared API key)
- Row-level security policies in Supabase
- A managed rate-limiting layer (e.g. Redis-backed)
- Duplicate-upload detection

---

## 📬 Contact

Built by **Mohd Ali**
📧 mohdalisaad868@gmail.com

Feel free to reach out with questions, feedback, or collaboration ideas!
