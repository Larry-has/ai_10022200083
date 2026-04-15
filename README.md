# Academic Insights Assistant (Next.js + FastAPI Manual RAG)

> **CS4241 – Introduction to Artificial Intelligence**  
> Academic City University — End of Second Semester Examination, 2026

**Student Name:** Lawrence Effah  
**Index Number:** 10022200083

This project is a full custom RAG chatbot system for academic evaluation, built without LangChain, LlamaIndex, or any prebuilt RAG framework.

Frontend:
- Next.js App Router UI for chat, retrieval inspection, prompt inspection, and logs.

Backend:
- FastAPI with manual ingestion, chunking, embeddings, FAISS indexing, hybrid retrieval, prompt construction, generation, and request-level logging.

## Live Deployment

- Frontend (production): [https://academic-insights-assistant-nextjs.vercel.app](https://academic-insights-assistant-nextjs.vercel.app)
- Backend API (production): [https://backend-lake-delta-78.vercel.app](https://backend-lake-delta-78.vercel.app)
- Backend API Docs (Swagger): [https://backend-lake-delta-78.vercel.app/docs](https://backend-lake-delta-78.vercel.app/docs)

## Rubric Coverage (A-G)

| Part | Requirement | Status | Primary Evidence |
|---|---|---|---|
| A | Comparative chunking impact analysis write-up | Complete | [part_a_chunking_analysis.md](backend/reports/part_a_chunking_analysis.md) |
| B | Advanced retrieval | Complete (hybrid TF-IDF + FAISS) | [retrieval.py](backend/retrieval.py) |
| C | Prompt experiments + evidence | Complete | [part_c_prompt_experiments.md](backend/reports/part_c_prompt_experiments.md) |
| D | End-to-end API pipeline and logs | Complete | [api.py](backend/api.py), [pipeline.py](backend/pipeline.py) |
| E | Adversarial testing + RAG vs pure-LLM | Complete | [part_e_adversarial_eval.md](backend/reports/part_e_adversarial_eval.md) |
| F | Architecture diagram + explanation | Complete | [part_f_architecture.md](backend/reports/part_f_architecture.md) |
| G | Innovation component | Complete (feedback-aware retrieval memory) | [part_g_innovation.md](backend/reports/part_g_innovation.md) |

## Repository Structure

```text
academic-insights-assistant-nextjs/
  app/                          # Next.js app entry
  src/                          # React UI components/screens/lib
  backend/
    api.py                      # FastAPI endpoints
    chunking.py                 # Manual chunking logic
    ingestion.py                # CSV + PDF ingestion
    embeddings.py               # Hugging Face embedding API + FAISS/TF-IDF artifacts
    retrieval.py                # Hybrid retrieval + score fusion + feedback boost
    prompt.py                   # Prompt templates + context selection
    pipeline.py                 # End-to-end RAG flow + logging + generation
    feedback.py                 # Innovation: retrieval feedback memory
    schemas.py                  # Request/response models
    experiments/                # Part A/C/E/G experiment scripts
    reports/                    # Submission evidence documents
    tests/                      # Unit/API tests
```

## Data Sources

The backend ingests these two documents:
- `~/Downloads/Ghana_Election_Result.csv`
- `~/Downloads/2025-Budget-Statement-and-Economic-Policy_v4.pdf`

They are copied into:
- `backend/data/raw/`

## Quick Start

### 1. Install frontend

```bash
cd <project-root>
npm install
```

### 2. Install backend

```bash
cd <project-root>
python3 -m venv .venv-backend
source .venv-backend/bin/activate
pip install -r backend/requirements.txt
```

### 3. Configure environment

Backend `.env`:
- `HF_TOKEN=...`
- `HUGGINGFACE_MODEL=meta-llama/Llama-3.1-8B-Instruct`

Frontend `.env.local`:
- `NEXT_PUBLIC_USE_MOCK=false`
- `NEXT_PUBLIC_API_BASE_URL=/api`
- `BACKEND_URL=http://localhost:8000/api`

Frontend (Vercel production env):
- `NEXT_PUBLIC_USE_MOCK=false`
- `NEXT_PUBLIC_API_BASE_URL=/api`
- `BACKEND_URL=https://backend-lake-delta-78.vercel.app/api`

### 4. Run backend

```bash
cd <project-root>
source .venv-backend/bin/activate
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run frontend

```bash
cd <project-root>
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## API Contract

### `POST /api/chat`

Request:

```json
{ "query": "What does the budget say about expenditure priorities?" }
```

Response:

```json
{
  "answer": "Grounded assistant answer...",
  "chunks": [
    {
      "id": "chunk-id",
      "source": "2025-Budget-Statement-and-Economic-Policy_v4.pdf",
      "text": "Retrieved text...",
      "similarityScore": 0.8123,
      "rank": 1
    }
  ],
  "finalPrompt": "Prompt sent to generation model...",
  "logs": [
    {
      "step": "query_received",
      "timestamp": "2026-04-15T18:00:00+00:00",
      "detail": "Query=\"...\""
    }
  ]
}
```

### `GET /api/logs`
- Returns recent flattened pipeline logs.

### `POST /api/feedback` (Innovation)

Request:

```json
{
  "query": "What did Mahama get in Ahafo?",
  "chunk_ids": ["chunk-abc"],
  "helpful": true,
  "notes": "This chunk answered my question well."
}
```

Response:

```json
{ "status": "ok", "recorded": 1 }
```

## Experimental Evidence

### Part A (Chunking)
- Compared `(400,60)`, `(800,120)`, `(1200,180)` chunk settings.
- Retrieval quality was tied on simple benchmark queries, but larger chunks increased context-budget pressure.
- Report: [part_a_chunking_analysis.md](backend/reports/part_a_chunking_analysis.md)

### Part C (Prompting)
- Same query, three prompt modes: `baseline_v1`, `grounded_v2`, `skeptical_v3`.
- `grounded_v2` had the best groundedness score and explicit source use.
- Report: [part_c_prompt_experiments.md](backend/reports/part_c_prompt_experiments.md)

### Part E (Adversarial + RAG vs pure LLM)
- Two adversarial queries were used.
- Compared abstention behavior, unsupported numeric claims, and consistency across repeated runs.
- Report: [part_e_adversarial_eval.md](backend/reports/part_e_adversarial_eval.md)

### Part F (Architecture)
- Full architecture diagram and rationale.
- Report: [part_f_architecture.md](backend/reports/part_f_architecture.md)

### Part G (Innovation)
- Query-aware feedback memory that reweights future retrieval results.
- Includes API support and demonstration artifact.
- Report: [part_g_innovation.md](backend/reports/part_g_innovation.md)

## Reproducing Experiment Reports

```bash
cd <project-root>
source .venv-backend/bin/activate

python -m backend.experiments.chunking_analysis
python -m backend.experiments.prompt_experiments
python -m backend.experiments.adversarial_eval
python -m backend.experiments.innovation_feedback_demo
```

Generated artifacts:
- `backend/reports/part_a_chunking_analysis.md`
- `backend/reports/part_c_prompt_experiments.md`
- `backend/reports/part_e_adversarial_eval.md`
- `backend/reports/part_f_architecture.md`
- `backend/reports/part_g_innovation.md`

## Test and Build Verification

```bash
cd <project-root>
source .venv-backend/bin/activate
pytest -q

npm run build
```

## Compliance Notes

- No LangChain/LlamaIndex used.
- Core RAG steps are implemented manually and transparently in dedicated modules.
- Logs expose query, retrieval outputs, selected context, prompt, and response for auditability.
