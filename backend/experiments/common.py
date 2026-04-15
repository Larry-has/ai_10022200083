from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


NUMBER_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?%?\b")
SOURCE_HINTS = (
    "Ghana_Election_Result.csv",
    "2025-Budget-Statement-and-Economic-Policy_v4.pdf",
)
ABSTAIN_HINTS = (
    "insufficient evidence",
    "could not find",
    "not supported",
    "cannot determine",
    "uncertain",
)


def ensure_reports_dir() -> Path:
    reports_dir = Path(__file__).resolve().parents[1] / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def similarity_ratio(left: str, right: str) -> float:
    return SequenceMatcher(a=left, b=right).ratio()


def extract_numbers(text: str) -> set[str]:
    return {match.group(0) for match in NUMBER_RE.finditer(text)}


def unsupported_number_count(answer: str, context: str) -> int:
    answer_numbers = extract_numbers(answer)
    context_numbers = extract_numbers(context)
    return len(answer_numbers - context_numbers)


def source_mention_count(answer: str) -> int:
    answer_lower = answer.lower()
    return sum(1 for source in SOURCE_HINTS if source.lower() in answer_lower)


def is_abstaining(answer: str) -> bool:
    lowered = answer.lower()
    return any(token in lowered for token in ABSTAIN_HINTS)

