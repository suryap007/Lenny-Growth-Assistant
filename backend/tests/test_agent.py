import pytest
from unittest.mock import patch, MagicMock
from app.agents.intents import classify_intent, Intent
from app.agents.pi_orchestrator import route_query

@pytest.mark.asyncio
@patch('app.agents.intents.run_agent')
async def test_classify_intent_ship30(mock_run_agent):
    mock_run_agent.return_value = "ship30"
    intent = await classify_intent("Write a ship30 essay")
    assert intent == Intent.SHIP30

@pytest.mark.asyncio
@patch('app.agents.intents.run_agent')
async def test_classify_intent_code(mock_run_agent):
    mock_run_agent.return_value = "code"
    intent = await classify_intent("Write a python script")
    assert intent == Intent.CODE

@pytest.mark.asyncio
@patch('app.agents.intents.run_agent')
async def test_classify_intent_qa(mock_run_agent):
    mock_run_agent.return_value = "qa"
    intent = await classify_intent("What is product market fit?")
    assert intent == Intent.QA

@pytest.mark.asyncio
@patch('app.agents.pi_orchestrator.classify_intent')
@patch('app.agents.pi_orchestrator.run_ship30_skill')
async def test_route_query_ship30(mock_ship30, mock_classify):
    mock_classify.return_value = Intent.SHIP30
    mock_ship30.return_value = {
        "content": "Here is your essay",
        "sources": [],
        "artifact": {"type": "markdown", "title": "Essay", "content": "Test"}
    }
    
    result = await route_query("write essay", session_id="123")
    assert result["intent"] == "ship30"
    assert result["content"] == "Here is your essay"
    assert result["artifact"]["type"] == "markdown"
