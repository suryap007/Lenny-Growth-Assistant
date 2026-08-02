# Agent Transcripts & Testing Logs

This directory contains the automated evaluation logs and testing transcripts for the **Lenny Growth Assistant**. Our testing methodology focuses on two critical pillars of an agentic RAG application: **Routing Accuracy** and **Contextual Groundedness**.

## 📁 File Manifest

| File | Purpose |
|------|---------|
| `mixed_50_results.json` | 50-query evaluation suite testing the Pi Orchestrator's intent classification routing. |
| `rag_baseline_results.json` | Groundedness and hallucination evaluation of the primary RAG pipeline. |
| `rag_output.txt` | Raw conversational outputs generated during the baseline RAG tests for qualitative human review. |

---

## 🧪 Testing Process: Agentic Routing Accuracy

**File:** `mixed_50_results.json`

Because the Lenny Growth Assistant uses an LLM-based Zero-Shot classifier to route queries, it is imperative that the router does not get confused by ambiguous phrasing. 

### Methodology
We constructed a suite of 50 diverse queries explicitly designed to test the boundaries between:
1. **`pi_code`**: Requests requiring software generation, debugging, or UI component design.
2. **`ship30`**: Requests for viral, formatted essays or long-form posts.
3. **`qa`**: Standard questions intended to hit the RAG vector database.

### Results
- **Total Tests:** 50
- **Passed:** 50
- **Failed:** 0
- **Pass Rate:** **100%**

The `pi_orchestrator` flawlessly classified every query. For example, the query *"Debug this javascript promise chain"* correctly routed to `pi_code`, while *"write an essay on the cold start problem"* accurately triggered the `ship30` workflow, bypassing the RAG pipeline entirely to preserve contextual limits.

---

## 🛡️ Testing Process: RAG Groundedness & Anti-Hallucination

**File:** `rag_baseline_results.json`

The most common failure mode in enterprise RAG systems is the LLM hallucinating answers when the retrieved context is insufficient or out-of-domain. We implemented strict negative-boundary tests to ensure the assistant declines to answer when it doesn't possess factual backing.

### Methodology
We passed highly specific and potentially adversarial questions to the `qa_skill` pipeline, ensuring that the retrieved `pgvector` chunks (Top-K=8) did not explicitly contain the answer. We then evaluated the LLM's response using an automated groundedness framework that checks for contradictions and unsupported claims.

### Example Test Cases & Results
- **Query:** *"What specific metric does Amplitude use to measure retention?"*
  - **LLM Response:** "I don't know."
  - **Evaluator Logic:** `is_grounded: true, hallucination: false`. The context did not provide this information, and the LLM correctly deferred rather than making up a generic answer.
- **Query:** *"Who said 'Growth is a system, not a tactic'?"*
  - **LLM Response:** "I don't know."
  - **Evaluator Logic:** `is_grounded: true, hallucination: false`.

### Conclusion
The baseline RAG system is highly conservative and firmly grounded in the transcribed context. It will not hallucinate facts outside the provided scope, ensuring the highest level of trustworthiness for users interacting with Lenny's content.
