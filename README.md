# AarogyaAid — AI-Powered Insurance Recommendation Platform

An AI agent that reads real health insurance policy documents and gives personalised, grounded, empathetic recommendations based on a user's health and financial profile.

Built as part of the AarogyaAid Engineering Assessment.

---

## What It Does

- **User Portal** — 6-field health profile form → AI recommendation with peer comparison table, coverage detail table, and personalised explanation → persistent chat explainer
- **Admin Panel** — upload, view, edit, and delete policy documents (PDF/JSON/TXT) with immediate vector store removal

---

## Tech Stack

| Layer | Choice | Justification |
|---|---|---|
| Frontend | React + Vite | Component-based UI fits the form + tables + chat on one page requirement |
| Backend | FastAPI (Python) | Async-first, fast iteration, native Pydantic validation |
| AI Agent | LangChain | Provides tool definitions, RAG wiring, session memory, and streaming support out of the box |
| LLM | Groq (LLaMA 3.1 8B Instant) | Free tier, sub-second latency, sufficient for structured insurance recommendation output |
| Vector Store | Chroma | Simple setup, supports immediate document deletion by ID — required by the spec |
| PDF Parsing | PyMuPDF | Handles text-native PDFs reliably; faster than pdfplumber for dense policy documents |
| Database | SQLite (dev) / PostgreSQL (prod) | Policy metadata and session state; SQL fits the structured nature of the data |

### Why LangChain over Google ADK

Google ADK is purpose-built for agents running inside Google Cloud and works best when integrated with Vertex AI and Google's managed tooling. This project runs locally and on Render — no Google Cloud dependency. LangChain provides the same core capabilities (tool definitions, retrieval chains, session memory, streaming) with broader LLM provider support and a simpler local development story. The `retrieve_policy_chunks` tool and session context injection map cleanly to LangChain's tool/agent architecture.

---

## Project Structure

```
aarogya-aid/
├── frontend/              # React + Vite app
│   └── src/
│       ├── components/
│       ├── pages/
│       └── api/
├── backend/               # FastAPI app
│   └── app/
│       ├── main.py
│       ├── core/
│       │   └── config.py
│       ├── api/
│       │   └── routes/
│       │       ├── recommend.py
│       │       ├── chat.py
│       │       └── admin.py
│       ├── services/
│       │   ├── rag_service.py
│       │   ├── recommendation_service.py
│       │   └── policy_parser.py
│       └── agents/
│           └── insurance_agent.py
├── policies/              # Sample policy docs (PDF/JSON/TXT)
├── tests/                 # Unit tests for recommendation logic
├── PRD.md
├── README.md
└── .env.example
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # fill in your values
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.

---

## Environment Variables

See `.env.example` for all required variables.

```
GROQ_API_KEY=           # Groq API key
GROQ_MODEL=             # e.g. llama-3.1-8b-instant
ADMIN_USERNAME=         # Admin panel username
ADMIN_PASSWORD=         # Admin panel password
CHROMA_PERSIST_DIR=     # Path for Chroma vector store
DATABASE_URL=           # SQLite or PostgreSQL connection string
```

---

## Recommendation Logic

See `PRD.md` for the full logic breakdown. In brief:

1. User submits 6-field profile (name, age, lifestyle, pre-existing conditions, income band, city/tier)
2. Agent queries Chroma vector store with a profile-aware retrieval query
3. Retrieved policy chunks are ranked by suitability against the profile
4. Agent generates all three required output sections grounded in the retrieved chunks
5. Chat interface persists profile + recommended policy context across turns

---

## Document Parsing Approach

Policy PDFs are parsed using PyMuPDF. Text is chunked at ~500 tokens with 50-token overlap to preserve clause continuity. Each chunk is embedded using Groq-compatible embeddings and stored in Chroma with metadata (policy name, insurer, file type, upload date). Deletion removes all chunks by document ID immediately.

---

## Demo

_Demo video link will be added before final submission._
