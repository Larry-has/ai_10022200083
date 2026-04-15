# Part E - Adversarial Testing and RAG vs Pure-LLM

## Adversarial Queries
- What were the final certified results of the 2028 Ghana presidential election by region?
- How much in Ghana cedis was allocated to a national quantum-computing scholarship in the 2025 budget?

## Comparative Results

| Query | System | Abstained | Source Mentions | Unsupported Numbers | Consistency | Hallucination Risk |
|---|---|---:|---:|---:|---:|---|
| What were the final certified results of the 2028 Ghana presidential election by region? | RAG | True | 0 | 1 | 1.0000 | low |
| What were the final certified results of the 2028 Ghana presidential election by region? | Pure LLM | False | 0 | 2 | 0.8984 | high |
| How much in Ghana cedis was allocated to a national quantum-computing scholarship in the 2025 budget? | RAG | True | 0 | 0 | 1.0000 | low |
| How much in Ghana cedis was allocated to a national quantum-computing scholarship in the 2025 budget? | Pure LLM | False | 0 | 0 | 0.9768 | medium |

## Evidence

### Query: What were the final certified results of the 2028 Ghana presidential election by region?
**RAG answer**
The provided contexts do not contain any information about the 2028 Ghana presidential election results by region. The documents appear to be related to budget statements and economic policies, not election results. Therefore, the answer is not supported by the retrieved documents.

**Pure LLM answer**
As of my last update, the 2028 Ghana presidential election results have not been certified yet. Ghana's elections typically take place every four years, and the most recent election was in 2024. For the most accurate and up-to-date information on the 2028 election results, you should check the latest reports from Ghana's Electoral Commission or reliable news sources.

### Query: How much in Ghana cedis was allocated to a national quantum-computing scholarship in the 2025 budget?
**RAG answer**
The answer is not supported by the retrieved documents. The contexts provided do not mention any allocation for a national quantum-computing scholarship in the 2025 budget.

**Pure LLM answer**
I do not have specific information about the exact allocation in Ghana cedis for a national quantum-computing scholarship in the 2025 budget. Budget allocations for specific programs can vary and are not always publicly detailed or widely reported. For accurate and up-to-date information, you would need to refer to the official budget documents or press releases from the Ghanaian government for the 2025 fiscal year.

## Conclusion
RAG responses are expected to show lower hallucination risk due to retrieval filtering, context-limited prompting, and fallback behavior when evidence is weak.

## Artifact
- Raw machine-readable results: `backend/reports/part_e_adversarial_eval.json`