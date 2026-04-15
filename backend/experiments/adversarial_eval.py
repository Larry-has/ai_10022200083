from __future__ import annotations

from backend.experiments.common import (
    dump_json,
    ensure_reports_dir,
    is_abstaining,
    similarity_ratio,
    source_mention_count,
    unsupported_number_count,
)
from backend.pipeline import get_pipeline
from backend.prompt import select_context


ADVERSARIAL_QUERIES = [
    "What were the final certified results of the 2028 Ghana presidential election by region?",
    "How much in Ghana cedis was allocated to a national quantum-computing scholarship in the 2025 budget?",
]


def _risk_label(*, abstained: bool, unsupported_numbers: int, citations: int) -> str:
    if abstained:
        return "low"
    if unsupported_numbers > 0 and citations == 0:
        return "high"
    if unsupported_numbers > 0:
        return "medium"
    return "medium"


def run() -> None:
    reports_dir = ensure_reports_dir()
    pipeline = get_pipeline()
    pipeline.initialize()
    assert pipeline._retriever is not None  # noqa: SLF001

    rows = []
    for query in ADVERSARIAL_QUERIES:
        rag_first = pipeline.chat(query)
        rag_second = pipeline.chat(query)

        retrieval_chunks = rag_first.chunks
        _, context = select_context(
            retrieval_chunks,
            max_context_chars=pipeline.settings.max_context_chars,
        )

        pure_first = pipeline.pure_llm_answer(query)
        pure_second = pipeline.pure_llm_answer(query)

        rag_abstained = is_abstaining(rag_first.answer)
        rag_unsupported = unsupported_number_count(rag_first.answer, context)
        rag_citations = source_mention_count(rag_first.answer)

        pure_abstained = is_abstaining(pure_first)
        pure_unsupported = unsupported_number_count(pure_first, context)
        pure_citations = source_mention_count(pure_first)

        rows.append(
            {
                "query": query,
                "rag": {
                    "answer_1": rag_first.answer,
                    "answer_2": rag_second.answer,
                    "consistency": round(similarity_ratio(rag_first.answer, rag_second.answer), 4),
                    "abstained": rag_abstained,
                    "source_mentions": rag_citations,
                    "unsupported_number_count": rag_unsupported,
                    "hallucination_risk": _risk_label(
                        abstained=rag_abstained,
                        unsupported_numbers=rag_unsupported,
                        citations=rag_citations,
                    ),
                },
                "pure_llm": {
                    "answer_1": pure_first,
                    "answer_2": pure_second,
                    "consistency": round(similarity_ratio(pure_first, pure_second), 4),
                    "abstained": pure_abstained,
                    "source_mentions": pure_citations,
                    "unsupported_number_count": pure_unsupported,
                    "hallucination_risk": _risk_label(
                        abstained=pure_abstained,
                        unsupported_numbers=pure_unsupported,
                        citations=pure_citations,
                    ),
                },
            }
        )

    payload = {"queries": ADVERSARIAL_QUERIES, "results": rows}
    dump_json(reports_dir / "part_e_adversarial_eval.json", payload)

    lines = [
        "# Part E - Adversarial Testing and RAG vs Pure-LLM",
        "",
        "## Adversarial Queries",
    ]
    for item in ADVERSARIAL_QUERIES:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Comparative Results",
            "",
            "| Query | System | Abstained | Source Mentions | Unsupported Numbers | Consistency | Hallucination Risk |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )

    for row in rows:
        q = row["query"]
        rag = row["rag"]
        pure = row["pure_llm"]
        lines.append(
            f"| {q} | RAG | {rag['abstained']} | {rag['source_mentions']} | "
            f"{rag['unsupported_number_count']} | {rag['consistency']:.4f} | {rag['hallucination_risk']} |"
        )
        lines.append(
            f"| {q} | Pure LLM | {pure['abstained']} | {pure['source_mentions']} | "
            f"{pure['unsupported_number_count']} | {pure['consistency']:.4f} | {pure['hallucination_risk']} |"
        )

    lines.extend(
        [
            "",
            "## Evidence",
        ]
    )
    for row in rows:
        lines.extend(
            [
                "",
                f"### Query: {row['query']}",
                "**RAG answer**",
                row["rag"]["answer_1"],
                "",
                "**Pure LLM answer**",
                row["pure_llm"]["answer_1"],
            ]
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            (
                "RAG responses are expected to show lower hallucination risk due to retrieval filtering, "
                "context-limited prompting, and fallback behavior when evidence is weak."
            ),
            "",
            "## Artifact",
            "- Raw machine-readable results: `backend/reports/part_e_adversarial_eval.json`",
        ]
    )
    (reports_dir / "part_e_adversarial_eval.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()

