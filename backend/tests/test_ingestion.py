from backend.config import get_settings
from backend.ingestion import ingest_csv


def test_csv_rows_are_normalized_into_atomic_chunks():
    settings = get_settings()
    chunks = ingest_csv(settings)

    assert chunks
    first_chunk = chunks[0]
    assert first_chunk.source == "Ghana_Election_Result.csv"
    assert "Candidate:" in first_chunk.text
    assert "Vote Share:" in first_chunk.text
    assert first_chunk.metadata["source_type"] == "csv"
