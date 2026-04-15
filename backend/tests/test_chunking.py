from backend.chunking import normalize_whitespace, sliding_window_chunk


def test_normalize_whitespace_collapses_repeated_spacing():
    assert normalize_whitespace("A   line\n\nwith\tspaces") == "A line with spaces"


def test_sliding_window_chunk_is_deterministic_and_overlapping():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = sliding_window_chunk(text, chunk_size=10, chunk_overlap=2)

    assert chunks == ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"]
