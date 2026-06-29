# IntelliPolicy AI

**Agentic AI platform for healthcare policy intelligence, claims validation, and rule automation.**

Built as a proof-of-concept for Cotiviti — IntelliPolicy AI transforms dense healthcare policy PDFs into actionable intelligence using a multi-agent AI pipeline with citation-grounded answers, deterministic claims validation, and real-time risk insights.

---

## Features

- **AI Policy Assistant** — Ask natural-language questions about any uploaded policy document. Every answer is grounded in page-level citations with relevance scoring and confidence metrics.
- **Claims Validator** — Validate CPT + ICD-10 claims against extracted policy rules with a two-stage pipeline: deterministic rule matching first, vector-search fallback second.
- **Rule Extraction** — Convert unstructured policy text into structured JSON business rules (CPT codes, plan types, prior auth requirements, documentation checklists).
- **Policy Comparison** — Detect version-to-version policy changes with risk scoring (high / medium / low) and side-by-side diff.
- **Audit Trail** — Full AI reasoning trace for every Q&A session, with step-by-step transparency logs.
- **Real-time Dashboard** — Live AI agent status, activity charts, and risk insights derived from actual session data — no hardcoded mocks.
- **Document Persistence** — Uploaded documents and their vector embeddings survive backend restarts via disk-backed storage.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                         │
│  Dashboard · Assistant · Claims · Rules · Compare · Audit       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                          │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Intake Agent│  │  QA Agent    │  │   Rule Agent       │    │
│  │ PDF parsing │  │ RAG pipeline │  │ Claims validator   │    │
│  │ chunking    │  │ LLM + cite   │  │ Rule extractor     │    │
│  └──────┬──────┘  └──────┬───────┘  └────────┬───────────┘    │
│         │                │                    │                 │
│         ▼                ▼                    ▼                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          InMemoryVectorStore (BAAI/bge-small-en-v1.5)    │  │
│  │          384-dim embeddings · cosine similarity          │  │
│  │          Persisted to .doc_store.json on disk            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  LLM: Anthropic Claude / OpenAI / Google Gemini (configurable) │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS v4, Framer Motion |
| Backend | FastAPI, Python 3.13, Pydantic v2 |
| Embeddings | `sentence-transformers` · `BAAI/bge-small-en-v1.5` |
| LLM Providers | Anthropic Claude, OpenAI, Google Gemini |
| PDF Processing | PyMuPDF |
| Vector Search | Custom in-memory store (cosine similarity) |
| Testing | pytest · starlette TestClient |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- An API key from Anthropic, OpenAI, or Google Gemini

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The backend starts on `http://localhost:8000`. On first run it loads any previously saved document store from `.doc_store.json`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev
```

Open `http://localhost:3000`.

### Environment Variables

**Backend** (`backend/.env`):

```env
# Optional — set via the dashboard UI instead
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend** (`frontend/.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker (optional)

```bash
docker-compose up --build
```

---

## Running Tests

```bash
cd backend
python3 -m pytest tests/ -v
```

17 integration tests covering all major API routes.

---

## Deployment

### Frontend → Vercel

```bash
cd frontend
npx vercel --prod
```

Set `NEXT_PUBLIC_API_URL` in the Vercel project settings to point to your deployed backend URL.

### Backend → Render / Railway

The FastAPI backend requires a persistent server (sentence-transformers + in-memory vector store are not compatible with serverless).

**Render (recommended for free tier):**
1. Create a new Web Service pointing to the `backend/` folder
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the Render dashboard

**Railway:**
1. `railway init` → select the `backend/` directory
2. `railway up`

After deploying the backend, update `NEXT_PUBLIC_API_URL` in your Vercel project settings and redeploy the frontend.

---

## Project Structure

```
intellipolicy-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # Intake, QA, Rule, Comparison agents
│   │   ├── api/             # FastAPI route handlers
│   │   ├── models/          # Pydantic schemas
│   │   └── services/        # LLM service, vector store
│   ├── tests/               # pytest integration tests
│   ├── sample_docs/         # Sample healthcare policy PDFs
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js App Router pages
│   │   ├── dashboard/
│   │   ├── assistant/
│   │   ├── claims/
│   │   ├── rules/
│   │   ├── compare/
│   │   └── audit/
│   ├── components/          # Shared UI components
│   └── lib/                 # API client, types, context
├── docker-compose.yml
└── README.md
```

---

## Key Design Decisions

**Two-stage claims validation** — Deterministic CPT/keyword rule matching runs first with no LLM involvement. The LLM is only called for reason generation when a rule is definitively matched, or for a vector-search fallback when no structured rule applies. This prevents hallucinated `rule_matched: true` responses.

**Retrieval guardrails** — Vector search results are filtered through a cosine threshold (≥ 0.15), a relevance guardrail (chunk must contain CPT code, procedure keyword, or policy keyword), and a reranking score threshold (≥ 55). This eliminates irrelevant chunks (e.g. GME funding text appearing for an MRI claim).

**Document persistence** — The document registry and all vector embeddings are serialized to `.doc_store.json` after every upload and reloaded on backend startup. Selected document ID is persisted to `localStorage` on the frontend.

---

## License

MIT
