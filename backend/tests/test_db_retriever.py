import pytest
from sqlalchemy import select
from unittest.mock import patch
from app.db.models import ChatSession, Message
from app.rag.retriever import retrieve_context

@pytest.mark.asyncio
async def test_db_session_message_relationship(test_db):
    session = test_db
    # Create session
    new_session = ChatSession(title="DB Test Session")
    session.add(new_session)
    await session.commit()
    await session.refresh(new_session)

    # Add message
    msg1 = Message(session_id=new_session.id, role="user", content="Hello test")
    msg2 = Message(session_id=new_session.id, role="assistant", content="Hi there!")
    session.add_all([msg1, msg2])
    await session.commit()

    # Query back
    res = await session.execute(
        select(ChatSession).where(ChatSession.id == new_session.id)
    )
    fetched_session = res.scalar_one()
    assert fetched_session.title == "DB Test Session"

    # Cascade Delete
    await session.delete(fetched_session)
    await session.commit()

    # Verify messages deleted
    msg_res = await session.execute(
        select(Message).where(Message.session_id == new_session.id)
    )
    assert len(msg_res.scalars().all()) == 0

@pytest.mark.asyncio
@patch("app.rag.retriever.generate_embeddings")
async def test_retriever_query_execution(mock_gen_embeddings, test_db):
    session = test_db
    mock_gen_embeddings.return_value = [[0.05] * 768]
    
    results = await retrieve_context("growth strategy", session, top_k=3, threshold=0.0)
    assert isinstance(results, list)
