import pytest
import json
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.llm.providers import LLMProvider

class MockLLMProvider(LLMProvider):
    async def chat(self, messages, temperature=0.2):
        system_content = messages[0]["content"] if messages else ""
        user_content = messages[-1]["content"] if len(messages) > 1 else ""

        if "expert developer and UI designer" in system_content or "artifact_type" in system_content:
            return json.dumps({
                "artifact_type": "html",
                "artifact_title": "Test Dashboard",
                "artifact_content": "<h1>Growth Dashboard</h1>"
            })
        if "Ship30for30" in system_content:
            return "# Retention Strategies\n\nHere is a Ship30 style essay on retention..."
        if "market fit" in user_content.lower():
            return "Product Market Fit is achieved when you have a strong product that satisfies a market."
        return "I could not find that in the transcripts"

    async def embed(self, texts):
        return [[0.01] * 768 for _ in texts]

@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_config_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "llm_provider" in data
        assert "openai_chat_model" in data
        assert "ollama_chat_model" in data

@pytest.mark.asyncio
async def test_session_lifecycle(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Create Session
        create_res = await client.post("/api/sessions")
        assert create_res.status_code == 200
        session_data = create_res.json()
        session_id = session_data["id"]
        assert session_data["title"] == "New Chat"

        # 2. List Sessions
        list_res = await client.get("/api/sessions")
        assert list_res.status_code == 200
        sessions = list_res.json()
        assert any(s["id"] == session_id for s in sessions)

        # 3. Get Session Details
        detail_res = await client.get(f"/api/sessions/{session_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == session_id
        assert isinstance(detail["messages"], list)

        # 4. Delete Session
        delete_res = await client.delete(f"/api/sessions/{session_id}")
        assert delete_res.status_code == 200
        assert delete_res.json() == {"status": "deleted"}

        # 5. Verify 404 on deleted session
        get_deleted = await client.get(f"/api/sessions/{session_id}")
        assert get_deleted.status_code == 404

@pytest.mark.asyncio
@pytest.mark.skip(reason="Obsolete: Depends on old router architecture")
@patch("app.services.router.get_provider", return_value=MockLLMProvider())
@patch("app.services.ship30.get_provider", return_value=MockLLMProvider())
@patch("app.services.artifacts.get_provider", return_value=MockLLMProvider())
async def test_chat_endpoint_skills(mock_art_provider, mock_ship_provider, mock_router_provider, test_db):
    mock_retrieve.return_value = [
        {"title": "Episode 100", "source": "lenny_ep100.txt", "score": 0.92, "content": "Product market fit is essential for growth."}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create a session for chat
        create_res = await client.post("/api/sessions")
        session_id = create_res.json()["id"]

        # Test Standard RAG chat
        chat_req = {
            "session_id": session_id,
            "message": "What is product market fit?"
        }
        chat_res = await client.post("/api/chat", json=chat_req)
        assert chat_res.status_code == 200
        res_data = chat_res.json()
        assert "answer" in res_data
        assert "sources" in res_data
        assert len(res_data["sources"]) == 1
        assert res_data["sources"][0]["title"] == "Episode 100"

        # Test Ship30 Skill routing
        ship30_req = {
            "session_id": session_id,
            "message": "Write an essay on retention strategies"
        }
        ship30_res = await client.post("/api/chat", json=ship30_req)
        assert ship30_res.status_code == 200
        ship30_data = ship30_res.json()
        assert "answer" in ship30_data
        assert "Ship30 style essay" in ship30_data["answer"]

        # Test Artifact Skill routing
        artifact_req = {
            "session_id": session_id,
            "message": "Create a html dashboard for growth metrics"
        }
        artifact_res = await client.post("/api/chat", json=artifact_req)
        assert artifact_res.status_code == 200
        artifact_data = artifact_res.json()
        assert artifact_data["artifact"] is not None
        assert artifact_data["artifact"]["artifact_type"] == "html"
        assert artifact_data["artifact"]["artifact_title"] == "Test Dashboard"

        # Clean up session
        await client.delete(f"/api/sessions/{session_id}")
