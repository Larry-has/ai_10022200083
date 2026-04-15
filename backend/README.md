# Backend - Manual RAG (FastAPI)

**Student Name:** Lawrence Effah  
**Index Number:** 10022200083

This backend is the core academic deliverable and implements a complete RAG pipeline manually:
- ingestion
- chunking
- embeddings
- FAISS + TF-IDF retrieval
- prompt construction
- generation
- request logging
- adversarial/ablation experiment scripts

No LangChain, LlamaIndex, or hidden RAG framework abstractions are used.

## Live Deployment

- Backend API (production): [https://backend-lake-delta-78.vercel.app](https://backend-lake-delta-78.vercel.app)
- Backend API Docs (Swagger): [https://backend-lake-delta-78.vercel.app/docs](https://backend-lake-delta-78.vercel.app/docs)
- Frontend app (production): [https://academic-insights-assistant-nextjs.vercel.app](https://academic-insights-assistant-nextjs.vercel.app)

## Module Map

```text
backend/
  api.py                  # FastAPI endpoints (/api/chat, /api/logs, /api/feedback)
  config.py               # Env-driven settings and paths
  schemas.py              # Pydantic contracts
  chunking.py             # Sliding-window chunking
  ingestion.py            # CSV row normalization + PDF page chunking
  embeddings.py           # Hugging Face embedding API + FAISS/TF-IDF persistence
  retrieval.py            # Hybrid retrieval + fusion + threshold filtering
  prompt.py               # Prompt templates + context selector
  feedback.py             # Innovation: feedback memory for retrieval boosts
  pipeline.py             # End-to-end orchestration + logging + generation
  experiments/            # Part A/C/E/G reproducible experiment scripts
  reports/                # Submission write-ups and JSON artifacts
  tests/                  # Unit/API tests
```

## Input Data

Expected files in `backend/data/raw/`:
- `Ghana_Election_Result.csv`
- `2025-Budget-Statement-and-Economic-Policy_v4.pdf`

Processed outputs:
- `backend/data/processed/chunks.jsonl`
- `backend/store/faiss.index`
- `backend/store/tfidf_matrix.npz`
- `backend/store/tfidf_vectorizer.pkl`
- `backend/store/manifest.json`
- `backend/store/feedback.jsonl`

## Setup

```bash
cd <project-root>
python3 -m venv .venv-backend
source .venv-backend/bin/activate
pip install -r backend/requirements.txt
```

## Environment Variables

Required:
- `HF_TOKEN`

Model selection:
- `HUGGINGFACE_MODEL` (default: `meta-llama/Llama-3.1-8B-Instruct`)

RAG tuning:
- `RAG_CHUNK_SIZE` (default `800`)
- `RAG_CHUNK_OVERLAP` (default `120`)
- `RAG_TOP_K` (default `5`)
- `RAG_DENSE_WEIGHT` (default `0.7`)
- `RAG_SPARSE_WEIGHT` (default `0.3`)
- `RAG_MIN_DENSE_SIMILARITY` (default `0.2`)
- `RAG_MAX_CONTEXT_CHARS` (default `3600`)
- `RAG_PROMPT_MODE` (`baseline_v1` | `grounded_v2` | `skeptical_v3`)
- `RAG_FEEDBACK_BOOST_SCALE` (default `0.15`)

## Run API

```bash
cd <project-root>
source .venv-backend/bin/activate
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### `POST /api/chat`
Input:

```json
{ "query": "What does the 2025 budget say about expenditure priorities?" }
```

Output:
- `answer`
- `chunks[]` with `id/source/text/similarityScore/rank`
- `finalPrompt`
- `logs[]`

### `GET /api/logs`
- Returns recent structured logs.

### `POST /api/feedback`
Input:

```json
{
  "query": "What did Mahama get in Ahafo?",
  "chunk_ids": ["chunk-abc"],
  "helpful": true,
  "notes": "Useful retrieval"
}
```

Output:

```json
{ "status": "ok", "recorded": 1 }
```

## Experiment Scripts (For Submission Evidence)

```bash
cd <project-root>
source .venv-backend/bin/activate

python -m backend.experiments.chunking_analysis
python -m backend.experiments.prompt_experiments
python -m backend.experiments.adversarial_eval
python -m backend.experiments.innovation_feedback_demo
```

Generated reports:
- `backend/reports/part_a_chunking_analysis.md`
- `backend/reports/part_c_prompt_experiments.md`
- `backend/reports/part_e_adversarial_eval.md`
- `backend/reports/part_f_architecture.md`
- `backend/reports/part_g_innovation.md`

## Testing

```bash
cd <project-root>
source .venv-backend/bin/activate
pytest -q
```

## Frontend Integration

Frontend `.env.local`:

```bash
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_BASE_URL=/api
BACKEND_URL=http://localhost:8000/api
```

Frontend Vercel production env:

```bash
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_BASE_URL=/api
BACKEND_URL=https://backend-lake-delta-78.vercel.app/api
```
