import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.db.session import AsyncSessionLocal
from app.rag.retriever import retrieve_context

queries = [
    "What is Product-Market Fit?",
    "How to build a growth loop?",
    "What did Brian Chesky say about design?",
    "How to run an effective meeting?",
    "Tips for B2B sales motion."
]

async def evaluate():
    async with AsyncSessionLocal() as db:
        print("Starting RAG Evaluation...\n" + "-"*40)
        
        for q in queries:
            print(f"\nQuery: {q}")
            results = await retrieve_context(q, db, top_k=3, threshold=0.0) # lower threshold for testing
            
            if not results:
                print("  -> No chunks retrieved.")
                continue
                
            for idx, r in enumerate(results):
                score = r['score']
                title = r['title']
                snippet = r['content'][:100].replace('\n', ' ')
                print(f"  [{idx+1}] (Score: {score:.3f}) {title} - {snippet}...")
                
        print("\nEvaluation Complete.")

if __name__ == "__main__":
    asyncio.run(evaluate())
