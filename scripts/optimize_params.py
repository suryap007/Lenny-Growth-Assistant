import os
import sys
import asyncio
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.rag.embeddings import generate_embeddings
import glob

# Try varying chunk sizes and overlaps
CHUNK_SIZES = [256, 512, 768]
OVERLAPS = [32, 128]
TOP_KS = [3, 5, 8]

# Sample queries
TEST_QUERIES = [
    "What is the core principle of PLG?",
    "How does Figma define an active user?",
    "What was Airbnb's first major growth hack?"
]

def split_text(text: str, target_tokens: int, overlap: int) -> list[str]:
    target_chars = target_tokens * 4
    overlap_chars = overlap * 4
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) > target_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap_chars:] + "\n\n" + para
        else:
            current_chunk += "\n\n" + para
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def evaluate_params():
    print("Starting Parameter Optimization (Sample)...")
    knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge_base"
    md_files = glob.glob(str(knowledge_dir / "**/*.md"), recursive=True)
    
    if not md_files:
        print("No files found.")
        return

    # Use only 1 file for quick testing
    test_file = md_files[0]
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    results = []
    
    for c_size in CHUNK_SIZES:
        for overlap in OVERLAPS:
            print(f"Testing Size: {c_size}, Overlap: {overlap}")
            chunks = split_text(content, c_size, overlap)
            
            # Embed chunks
            try:
                embeddings = await generate_embeddings(chunks)
            except Exception as e:
                print(f"Error embedding: {e}")
                continue
                
            # Embed queries
            try:
                q_embeddings = await generate_embeddings(TEST_QUERIES)
            except Exception as e:
                print(f"Error embedding queries: {e}")
                continue
                
            # For each query, calculate best match similarity (just as a proxy for retrieval quality)
            for k in TOP_KS:
                avg_top_similarity = 0.0
                for q_emb in q_embeddings:
                    # Calculate cosine similarity (dot product since normalized)
                    # For simplicity, we just use cosine distance proxy
                    import math
                    
                    def cosine_sim(v1, v2):
                        dot = sum(a*b for a, b in zip(v1, v2))
                        norm1 = math.sqrt(sum(a*a for a in v1))
                        norm2 = math.sqrt(sum(b*b for b in v2))
                        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
                        
                    sims = [cosine_sim(q_emb, c_emb) for c_emb in embeddings]
                    top_k_sims = sorted(sims, reverse=True)[:k]
                    avg_top_similarity += sum(top_k_sims) / len(top_k_sims) if top_k_sims else 0.0
                    
                avg_sim = avg_top_similarity / len(TEST_QUERIES)
                results.append({
                    "chunk_size": c_size,
                    "overlap": overlap,
                    "top_k": k,
                    "avg_similarity": float(avg_sim)
                })
                
    # Sort by best similarity
    results.sort(key=lambda x: x["avg_similarity"], reverse=True)
    
    print("\n--- OPTIMIZATION RESULTS ---")
    for r in results:
        print(f"Size: {r['chunk_size']} | Overlap: {r['overlap']} | Top_K: {r['top_k']} | Score: {r['avg_similarity']:.4f}")
        
    print("\nBest Configuration:")
    best = results[0]
    print(best)
    
    with open("optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(evaluate_params())
