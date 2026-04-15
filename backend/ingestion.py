from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

try:
    from .chunking import normalize_whitespace, sliding_window_chunk
    from .config import CHUNKS_PATH, Settings
    from .schemas import ChunkRecord
except ImportError:  # pragma: no cover
    from chunking import normalize_whitespace, sliding_window_chunk
    from config import CHUNKS_PATH, Settings
    from schemas import ChunkRecord


def _stable_chunk_id(source: str, locator: str, text: str) -> str:
    digest = hashlib.sha1(f"{source}|{locator}|{text}".encode("utf-8")).hexdigest()
    return digest


def _normalize_vote_share(value: str) -> str:
    cleaned = normalize_whitespace(value.replace("\ufeff", ""))
    return cleaned


def ingest_csv(settings: Settings) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []

    with settings.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader):
            source = settings.csv_filename
            text = (
                f"Year: {normalize_whitespace(row['Year'])} | "
                f"Old Region: {normalize_whitespace(row['Old Region'])} | "
                f"New Region: {normalize_whitespace(row['New Region'])} | "
                f"Code: {normalize_whitespace(row['Code'])} | "
                f"Candidate: {normalize_whitespace(row['Candidate'])} | "
                f"Party: {normalize_whitespace(row['Party'])} | "
                f"Votes: {normalize_whitespace(row['Votes'])} | "
                f"Vote Share: {_normalize_vote_share(row['Votes(%)'])}"
            )
            locator = f"row-{row_index}"
            records.append(
                ChunkRecord(
                    id=_stable_chunk_id(source, locator, text),
                    source=source,
                    text=text,
                    metadata={
                        "source_type": "csv",
                        "row_index": row_index,
                        "year": normalize_whitespace(row["Year"]),
                        "old_region": normalize_whitespace(row["Old Region"]),
                        "new_region": normalize_whitespace(row["New Region"]),
                        "candidate": normalize_whitespace(row["Candidate"]),
                        "party": normalize_whitespace(row["Party"]),
                    },
                )
            )

    return records


def ingest_pdf(settings: Settings) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []
    reader = PdfReader(str(settings.pdf_path))

    for page_index, page in enumerate(reader.pages):
        page_text = normalize_whitespace(page.extract_text() or "")
        if not page_text:
            continue

        chunks = sliding_window_chunk(
            page_text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        for chunk_index, chunk_text in enumerate(chunks):
            source = settings.pdf_filename
            locator = f"page-{page_index + 1}-chunk-{chunk_index}"
            records.append(
                ChunkRecord(
                    id=_stable_chunk_id(source, locator, chunk_text),
                    source=source,
                    text=chunk_text,
                    metadata={
                        "source_type": "pdf",
                        "page": page_index + 1,
                        "chunk_index": chunk_index,
                    },
                )
            )

    return records


def ingest_documents(settings: Settings) -> list[ChunkRecord]:
    chunks = ingest_csv(settings) + ingest_pdf(settings)
    persist_chunks(chunks, CHUNKS_PATH)
    return chunks


def persist_chunks(chunks: list[ChunkRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")


def load_chunks(chunks_path: Path = CHUNKS_PATH) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            chunks.append(ChunkRecord.model_validate_json(line))
    return chunks
