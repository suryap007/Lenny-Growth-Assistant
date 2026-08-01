import os
import sys
import glob
import asyncio
from pathlib import Path
import re

# Add backend directory to sys.path so we can import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.db.session import engine, AsyncSessionLocal
from app.db.models import Document, DocumentChunk
from app.rag.embeddings import generate_embeddings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

def clean_markdown(text: str) -> str:
    # Very basic clean up for transcript noise
    text = re.sub(r'\[\d+:\d+:\d+\]', '', text) # Remove timestamps like [01:23:45]
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) # Remove bolding for cleaner semantic text
    return text.strip()

def split_text(text: str, target_tokens: int = 600, overlap: int = 100) -> list[str]:
    # A naive semantic-ish chunker (splitting by paragraphs, grouping until target size)
    # 1 token ~ 4 chars
    target_chars = target_tokens * 4
    overlap_chars = overlap * 4
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > target_chars and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep the overlap from the end of the current_chunk
            current_chunk = current_chunk[-overlap_chars:] + "\n\n" + para
        else:
            current_chunk += "\n\n" + para
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

async def ingest_transcripts():
    knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge_base"
    
    if not knowledge_dir.exists():
        print(f"Directory {knowledge_dir} does not exist.")
        return
        
    md_files = glob.glob(str(knowledge_dir / "**/*.md"), recursive=True)
    if not md_files:
        print(f"No markdown files found in {knowledge_dir}")
        return

    async with AsyncSessionLocal() as session:
        for file_path in md_files:
            p = Path(file_path)
            file_name = p.name
            episode_dir = p.parent.name
            episode_title = episode_dir.replace('-', ' ').title()
            
            # Check if already ingested
            res = await session.execute(select(Document).where(Document.source == episode_dir))
            if res.scalar_one_or_none():
                print(f"Skipping {episode_title} ({episode_dir}), already ingested.")
                continue
                
            print(f"Ingesting {episode_title}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = clean_markdown(f.read())
                
            doc = Document(
                source=episode_dir, 
                title=episode_title,
                metadata_={
                    "guest_name": episode_title,
                    "content_type": "podcast_transcript",
                    "file_name": file_name
                }
            )
            session.add(doc)
            await session.flush() # Get ID
            
            chunks_text = split_text(content)
            
            # Generate embeddings in batches
            batch_size = 10
            for i in range(0, len(chunks_text), batch_size):
                batch_texts = chunks_text[i:i+batch_size]
                try:
                    embeddings = await generate_embeddings(batch_texts)
                    
                    for idx, (text, emb) in enumerate(zip(batch_texts, embeddings)):
                        chunk_index = i + idx
                        # Just approximating token count
                        token_count = len(text) // 4
                        
                        chunk = DocumentChunk(
                            document_id=doc.id,
                            chunk_index=chunk_index,
                            content=text,
                            token_count=token_count,
                            embedding=emb,
                            metadata_={"speaker": "unknown"}
                        )
                        session.add(chunk)
                except Exception as e:
                    print(f"Error embedding batch in {file_name}: {e}")
                    
            await session.commit()
            print(f"Successfully ingested {len(chunks_text)} chunks for {file_name}")

if __name__ == "__main__":
    asyncio.run(ingest_transcripts())
