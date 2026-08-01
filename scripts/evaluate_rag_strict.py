import sys
import os
import asyncio
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.db.session import AsyncSessionLocal
from app.rag.retriever import retrieve_context
from app.llm.providers import get_provider
from pydantic import BaseModel

class GroundednessScore(BaseModel):
    is_grounded: bool
    hallucination: bool
    unsupported: bool
    contradiction: bool
    reasoning: str

# 50 Benchmark Queries across 10 categories
QUERIES = [
    # 1. Exact fact lookup
    "What is the core principle of PLG according to the transcripts?",
    "Who said 'Growth is a system, not a tactic'?",
    "What specific metric does Amplitude use to measure retention?",
    "How does Figma define an active user?",
    "What was Airbnb's first major growth hack?",
    # 2. Multi-hop retrieval
    "Compare the growth strategies of Notion and Airtable.",
    "How did the transition from sales-led to product-led impact revenue for companies mentioned?",
    "What are the prerequisites for implementing a successful referral loop?",
    "Which two guests disagreed on the importance of paid acquisition?",
    "Connect the concept of 'magic moment' to 'time to value' using examples from the podcast.",
    # 3. Numerical facts
    "What percentage of revenue should come from enterprise in a mature PLG company?",
    "How many active users did Slack have when they launched their enterprise grid?",
    "What is considered a good Net Revenue Retention (NRR) rate?",
    "How much did customer acquisition cost (CAC) decrease after implementing SEO?",
    "What is the ideal ratio of LTV to CAC?",
    # 4. Date/time facts
    "In what year did Product-Led Growth become a mainstream term?",
    "When did Stripe launch their Atlas product?",
    "How long did it take for Dropbox to reach 1 million users?",
    "What month is usually the slowest for B2B SaaS sales?",
    "When should a startup typically hire their first Head of Growth?",
    # 5. Person-specific facts
    "What advice did Elena Verna give about B2B growth?",
    "How did Brian Balfour define the 'growth machine'?",
    "What was Casey Winters' main critique of traditional SEO?",
    "According to Andrew Chen, what is the 'Law of Shitty Clickthroughs'?",
    "What does Reforge teach about retention curves?",
    # 6. Product/growth concepts
    "Define 'activation rate'.",
    "What is a 'growth loop'?",
    "Explain the 'aha moment'.",
    "What is 'product-market fit'?",
    "Define 'viral coefficient'.",
    # 7. Comparative questions
    "What is the difference between PLG and SLG?",
    "Compare inbound vs outbound sales strategies.",
    "How does freemium compare to a free trial?",
    "What are the pros and cons of top-down vs bottom-up SaaS?",
    "Compare linear growth vs exponential growth in consumer apps.",
    # 8. Negative questions
    "Why shouldn't you focus on top-of-funnel acquisition early on?",
    "What is the danger of ignoring churn?",
    "Why did the 'growth hacker' title fall out of favor?",
    "What are the common pitfalls of paid acquisition?",
    "Why might a freemium model fail?",
    # 9. Ambiguous questions
    "How do you grow?",
    "What is the best metric?",
    "When is the right time?",
    "Who is right about marketing?",
    "Why does it work?",
    # 10. Out-of-domain questions
    "What is the capital of France?",
    "How do you bake a chocolate cake?",
    "Who won the 1998 World Cup?",
    "What is the theory of relativity?",
    "How do I fix a leaky faucet?"
]

async def check_groundedness(answer: str, context: str) -> dict:
    """Uses LLM as a strict judge to check hallucination."""
    provider = get_provider()
    
    prompt = f"""You are a precise JSON formatting bot. Your ONLY job is to evaluate if the Answer is strictly supported by the Context and output a single JSON object.

Answer:
{answer}

Context:
{context}

Rules:
1. Every factual statement must be in the context.
2. If evidence is missing, hallucination=true.
3. If evidence is partial, unsupported=true.
4. If evidence contradicts, contradiction=true.
5. If the answer correctly states "I don't know" or "I cannot find this", then it is grounded (is_grounded=true, hallucination=false).

Output EXACTLY this JSON structure and replace the values with your evaluation:
{{
    "is_grounded": <boolean>,
    "hallucination": <boolean>,
    "unsupported": <boolean>,
    "contradiction": <boolean>,
    "reasoning": "<string explaining your evaluation step-by-step>"
}}
"""
    try:
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = await provider.chat(messages, temperature=0.0)
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            clean_text = match.group(0)
            return json.loads(clean_text)
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        print(f"Error checking groundedness: {e}")
        print(f"RAW RESPONSE: {response}")
        return {"is_grounded": False, "hallucination": True, "unsupported": False, "contradiction": False, "reasoning": "Error evaluating"}

async def evaluate_retrieval(query: str, chunks: list) -> list[bool]:
    """Uses LLM to judge which retrieved chunks are actually relevant to the query."""
    if not chunks:
        return []
    
    provider = get_provider()
    
    chunks_text = ""
    for i, c in enumerate(chunks):
        chunks_text += f"--- Chunk {i} ---\n{c['content']}\n\n"
        
    prompt = f"""You are an objective relevance judge.
Determine which of the following chunks contain information that helps answer the query.

Query: {query}

{chunks_text}

Output EXACTLY a JSON array of booleans, where the index corresponds to the chunk index. For example, if Chunk 0 and Chunk 2 are relevant, but Chunk 1 is not, output: [true, false, true].
The array MUST have exactly {len(chunks)} elements.
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        response = await provider.chat(messages, temperature=0.0)
        import re
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            clean_text = match.group(0)
            relevance = json.loads(clean_text)
            if len(relevance) == len(chunks):
                return relevance
    except Exception as e:
        print(f"Error checking retrieval relevance: {e}")
    
    # Fallback if parsing fails or lengths mismatch
    return [False] * len(chunks)

async def run_evaluation():
    print("Starting Strict RAG Evaluation...")
    results = []
    
    total_mrr = 0.0
    total_hit_rate = 0.0
    total_precision_at_k = 0.0
    
    async with AsyncSessionLocal() as db:
        provider = get_provider()
        
        # Evaluate all queries for full hallucination baseline report
        for i, query in enumerate(QUERIES):
            print(f"[{i+1}/{len(QUERIES)}] Testing: {query}")
            
            # Retrieve
            context_chunks = await retrieve_context(query, db, top_k=8)
            context_str = "\n\n".join([f"[{c['source']}] {c['content']}" for c in context_chunks])
            
            # Generate Answer (using a strict prompt)
            system_prompt = f"""You are an expert product manager assistant.
You must answer the user's query strictly using ONLY the provided context.
If the provided context does not contain the information needed to answer the question, you must respond exactly with: "I don't know".
Do not include any outside knowledge, and do not make up answers.

Context:
{context_str}"""
            answer = await provider.chat(
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
                temperature=0.0
            )
            
            # Check Groundedness
            groundedness = await check_groundedness(answer, context_str)
            
            # Evaluate Retrieval
            relevance_flags = await evaluate_retrieval(query, context_chunks)
            
            hit = any(relevance_flags)
            mrr = 0.0
            if hit:
                first_relevant_idx = relevance_flags.index(True)
                mrr = 1.0 / (first_relevant_idx + 1)
            
            precision_at_k = sum(relevance_flags) / len(context_chunks) if context_chunks else 0.0
            
            total_hit_rate += 1 if hit else 0
            total_mrr += mrr
            total_precision_at_k += precision_at_k
            
            # Record
            result = {
                "query": query,
                "retrieved_count": len(context_chunks),
                "relevance_flags": relevance_flags,
                "hit": hit,
                "mrr": mrr,
                "precision_at_k": precision_at_k,
                "answer": answer,
                "groundedness": groundedness
            }
            results.append(result)
            
    # Calculate Metrics
    total = len(results)
    hallucinations = sum(1 for r in results if r["groundedness"]["hallucination"])
    unsupported = sum(1 for r in results if r["groundedness"]["unsupported"])
    
    avg_hit_rate = total_hit_rate / total if total > 0 else 0.0
    avg_mrr = total_mrr / total if total > 0 else 0.0
    avg_precision_at_k = total_precision_at_k / total if total > 0 else 0.0
    
    print("\n--- BASELINE METRICS ---")
    print(f"Total Queries: {total}")
    print(f"Hit Rate: {avg_hit_rate*100:.1f}%")
    print(f"Mean Reciprocal Rank (MRR): {avg_mrr:.3f}")
    print(f"Precision@k: {avg_precision_at_k:.3f}")
    print(f"Hallucination Rate: {(hallucinations/total)*100:.1f}%")
    print(f"Unsupported Rate: {(unsupported/total)*100:.1f}%")
    
    with open("rag_baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(run_evaluation())
