import pytest
import unittest.mock as mock
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request
from security.token_budget import TokenBudgetTracker
from security.middleware import TokenBudgetMiddleware
from agents.base_agent import BaseAgent
from core.types import AgentRole, AgentMode

# Simple mock FastAPI app to test middleware in isolation
app = FastAPI()
app.add_middleware(TokenBudgetMiddleware)

@app.get("/api/test-workflow")
async def workflow_route():
    return {"status": "success"}

@app.post("/api/security/budget/reset")
async def reset_route():
    tracker = TokenBudgetTracker()
    tracker.reset()
    return {"status": "reset"}

@pytest.fixture(autouse=True)
def reset_tracker():
    """Ensure the singleton budget tracker is reset before each test."""
    TokenBudgetTracker().reset()
    TokenBudgetTracker().set_limit(100000)

def test_tracker_singleton():
    t1 = TokenBudgetTracker()
    t2 = TokenBudgetTracker()
    assert t1 is t2

def test_tracker_consumption():
    tracker = TokenBudgetTracker()
    tracker.consume(100, 200)
    stats = tracker.get_stats()
    assert stats["consumed_tokens"] == 300
    assert stats["input_tokens"] == 100
    assert stats["output_tokens"] == 200
    assert stats["remaining_tokens"] == stats["limit"] - 300
    assert not stats["is_tripped"]

def test_tracker_circuit_breaker_tripped():
    tracker = TokenBudgetTracker()
    tracker.set_limit(50)
    tracker.consume(30, 30) # Total 60 > 50
    assert tracker.is_tripped()
    stats = tracker.get_stats()
    assert stats["is_tripped"]
    assert stats["remaining_tokens"] == 0

def test_middleware_blocks_when_tripped():
    tracker = TokenBudgetTracker()
    tracker.set_limit(10)
    tracker.consume(5, 10) # Total 15 > 10, trips budget

    client = TestClient(app)
    
    # Non-exempt endpoint should be blocked
    response = client.get("/api/test-workflow")
    assert response.status_code == 503
    data = response.json()
    assert "token budget limit exceeded" in data["detail"].lower()
    assert data["stats"]["is_tripped"]

    # Reset endpoint should still bypass and succeed
    response = client.post("/api/security/budget/reset")
    assert response.status_code == 200
    assert not tracker.is_tripped()

@pytest.mark.asyncio
async def test_agent_aborts_when_tripped():
    tracker = TokenBudgetTracker()
    tracker.set_limit(10)
    tracker.consume(6, 6) # Total 12 > 10, trips budget

    mock_key_manager = mock.Mock()
    mock_model_router = mock.Mock()
    
    agent = BaseAgent(
        role=AgentRole.CRITIC,
        agent_id="test-critic",
        key_manager=mock_key_manager,
        model_router=mock_model_router
    )

    with pytest.raises(ValueError) as excinfo:
        await agent.think("some prompt")
    
    assert "Token budget exceeded" in str(excinfo.value)
