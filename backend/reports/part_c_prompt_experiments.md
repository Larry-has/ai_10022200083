# Part C - Prompt Experiments

## Query
What does the 2025 budget statement say about expenditure priorities?

## Prompt Modes
- baseline_v1: minimal instruction prompt.
- grounded_v2: strong grounding + source mention guidance.
- skeptical_v3: strict evidence-only rule with explicit fallback.

## Results

| Prompt Mode | Citations | Unsupported Numbers | Abstained | Groundedness Score |
|---|---:|---:|---:|---:|
| baseline_v1 | 0 | 0 | False | 0.0000 |
| grounded_v2 | 1 | 0 | False | 0.4000 |
| skeptical_v3 | 0 | 0 | True | 0.2000 |

## Evidence Snippets

### baseline_v1
The 2025 budget statement prioritizes containing public expenditure and bringing public finances back on a sustainable path by improving the quality and efficiency in public spending and rationalizing expenses.

### grounded_v2
The 2025 budget statement prioritizes containing public expenditure and bringing public finances back on a sustainable path by improving the quality and efficiency in public spending and rationalizing expenses. This information is supported by the following source:

Source=2025-Budget-Statement-and-Economic-Policy_v4.pdf

### skeptical_v3
Insufficient evidence in provided documents.

## Conclusion
The best-performing prompt mode was **grounded_v2**, measured by fewer unsupported numeric claims and stronger source-grounded response behavior.

## Artifact
- Raw machine-readable results: `backend/reports/part_c_prompt_experiments.json`