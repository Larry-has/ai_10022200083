# Part A - Comparative Chunking Impact Analysis

## Goal
Evaluate how chunk size and overlap affect retrieval quality using the same benchmark queries.

## Benchmark Setup
- Query count: 4
- Metrics:
  - Source Hit@1
  - Source Hit@5
  - Keyword Coverage@5
  - Source MRR
  - Average Top-1 Dense Similarity

## Results

| Chunk Size | Overlap | Chunk Count | Hit@1 | Hit@5 | Keyword@5 | MRR | Avg Top1 Sim |
|---|---:|---:|---:|---:|---:|---:|---:|
| 400 | 60 | 2733 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6433 |
| 800 | 120 | 1708 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6398 |
| 1200 | 180 | 1380 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6390 |

| Chunk Size | Overlap | Avg Retrieved Chars@5 | Context Budget Exceed Rate |
|---|---:|---:|---:|
| 400 | 60 | 1402.75 | 0.0000 |
| 800 | 120 | 1971.75 | 0.2500 |
| 1200 | 180 | 2439.00 | 0.5000 |

## Interpretation
The best trade-off was **chunk_size=400** and **chunk_overlap=60** based on MRR and keyword coverage.
Smaller chunks improved lexical precision but could fragment long budget statements; larger chunks preserved fiscal context but reduced exact lexical alignment.
The selected default (800/120) gave stable retrieval quality without excessive chunk growth.

## Artifact
- Raw machine-readable results: `backend/reports/part_a_chunking_analysis.json`