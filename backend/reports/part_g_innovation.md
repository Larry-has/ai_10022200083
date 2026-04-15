# Part G - Innovation Component

## Feature: Feedback-Aware Retrieval Memory
A signed feedback signal is persisted for `(query, chunk_id)` pairs and reused during future retrieval. Similar historical queries contribute a bounded positive/negative boost to candidate chunks before final ranking.

## Why This Is Novel In This Project
- Hybrid retrieval is Part B baseline.
- This feature adds adaptive retrieval behavior from user supervision over time.
- It improves relevance without introducing opaque framework abstractions.

## Demo Outcome
- Ranking before feedback: `['c1', 'c2']`
- Ranking after feedback: `['c2', 'c1']`
- Feedback pushed the explicitly marked chunk upward.

## API Surface
- `POST /api/feedback` with `{query, chunk_ids, helpful, notes}`
- Feedback log persistence: `backend/store/feedback.jsonl`

## Artifact
- Raw machine-readable results: `backend/reports/part_g_innovation_demo.json`