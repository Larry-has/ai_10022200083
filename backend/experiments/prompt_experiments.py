from __future__ import annotations

from backend.experiments.common import (
    dump_json,
    ensure_reports_dir,
    is_abstaining,
    source_mention_count,
    unsupported_number_count,
)
from backend.pipeline import get_pipeline
from backend.prompt import build_prompt, select_context


def run() -> None:
    reports_dir = ensure_reports_dir()
    pipeline = get_pipeline()
    pipeline.initialize()
    assert pipeline._retriever is not None  # noqa: SLF001

    query = "What does the 2025 budget statement say about expenditure priorities?"
    retrieval = pipeline._retriever.retrieve(query, top_k=pipeline.settings.top_k)  # noqa: SLF001
    retrieved_chunks = retrieval.retrieved_chunks
    selected_chunks, context = select_context(
        retrieved_chunks,
        max_context_chars=pipeline.settings.max_context_chars,
    )

    prompt_modes = ["baseline_v1", "grounded_v2", "skeptical_v3"]
    experiment_rows = []

    for mode in prompt_modes:
        prompt, _ = build_prompt(
            query=query,
            chunks=retrieved_chunks,
            settings=pipeline.settings,
            prompt_mode=mode,
        )
        answer = pipeline.answer_from_prompt(prompt)

        unsupported_count = unsupported_number_count(answer, context)
        citation_count = source_mention_count(answer)
        abstained = is_abstaining(answer)
        groundedness_score = max(0.0, (citation_count * 0.4) - (unsupported_count * 0.5))
        if abstained:
            groundedness_score += 0.2

        experiment_rows.append(
            {
                "prompt_mode": mode,
                "answer": answer,
                "metrics": {
                    "citation_mentions": citation_count,
                    "unsupported_number_count": unsupported_count,
                    "abstained": abstained,
                    "groundedness_score": round(groundedness_score, 4),
                },
            }
        )

    best = max(experiment_rows, key=lambda row: row["metrics"]["groundedness_score"])
    payload = {
        "query": query,
        "context_chunk_count": len(selected_chunks),
        "results": experiment_rows,
        "best_prompt_mode": best["prompt_mode"],
    }
    dump_json(reports_dir / "part_c_prompt_experiments.json", payload)

    lines = [
        "# Part C - Prompt Experiments",
        "",
        "## Query",
        query,
        "",
        "## Prompt Modes",
        "- baseline_v1: minimal instruction prompt.",
        "- grounded_v2: strong grounding + source mention guidance.",
        "- skeptical_v3: strict evidence-only rule with explicit fallback.",
        "",
        "## Results",
        "",
        "| Prompt Mode | Citations | Unsupported Numbers | Abstained | Groundedness Score |",
        "|---|---:|---:|---:|---:|",
    ]

    for row in experiment_rows:
        metrics = row["metrics"]
        lines.append(
            f"| {row['prompt_mode']} | {metrics['citation_mentions']} | "
            f"{metrics['unsupported_number_count']} | {metrics['abstained']} | "
            f"{metrics['groundedness_score']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Snippets",
        ]
    )
    for row in experiment_rows:
        lines.extend(
            [
                "",
                f"### {row['prompt_mode']}",
                row["answer"],
            ]
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            (
                f"The best-performing prompt mode was **{best['prompt_mode']}**, measured by fewer unsupported "
                "numeric claims and stronger source-grounded response behavior."
            ),
            "",
            "## Artifact",
            "- Raw machine-readable results: `backend/reports/part_c_prompt_experiments.json`",
        ]
    )
    (reports_dir / "part_c_prompt_experiments.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()

