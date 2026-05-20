import pytest
import unittest.mock as mock
from agents import (
    BaseAgent,
    AnalysisAgent,
    SolutionAgent,
    CriticAgent,
    SecurityAgent,
    OptimizerAgent,
)
from core.types import AgentRole, AgentMode, Argument
import json


class MockResponse:
    def __init__(self, text):
        self.text = text


@pytest.fixture
def mock_genai():
    with mock.patch("google.genai.Client") as mock_client:
        yield mock_client


@pytest.mark.asyncio
async def test_base_agent_execution_mode(mock_genai):
    # Setup mock
    mock_client = mock_genai.return_value
    mock_client.aio.models.generate_content = mock.AsyncMock(
        return_value=MockResponse("Test response")
    )

    mock_key_manager = mock.Mock()
    mock_model_router = mock.Mock()

    agent = BaseAgent(
        role=AgentRole.ANALYST,
        agent_id="test-analyst",
        key_manager=mock_key_manager,
        model_router=mock_model_router,
    )
    response = await agent.think("test prompt")

    assert response == "Test response"
    assert agent.mode == AgentMode.EXECUTION
    assert "ANALYST" in agent.system_prompt


@pytest.mark.asyncio
async def test_base_agent_debate_mode(mock_genai):
    # Setup mock with JSON response
    debate_json = json.dumps({"content": "Adversarial point", "confidence_score": 0.9})
    mock_client = mock_genai.return_value
    mock_client.aio.models.generate_content = mock.AsyncMock(
        return_value=MockResponse(debate_json)
    )

    mock_key_manager = mock.Mock()
    mock_model_router = mock.Mock()

    agent = BaseAgent(
        role=AgentRole.CRITIC,
        agent_id="test-critic",
        key_manager=mock_key_manager,
        model_router=mock_model_router,
    )
    agent.set_mode(AgentMode.DEBATE)

    result = await agent.think("critique this")

    assert isinstance(result, Argument)
    assert result.content == "Adversarial point"
    assert result.confidence == 0.9
    assert result.role == AgentRole.CRITIC


@pytest.mark.asyncio
async def test_specialized_agents(mock_genai):
    mock_client = mock_genai.return_value
    mock_client.aio.models.generate_content = mock.AsyncMock(
        return_value=MockResponse("OK")
    )

    mock_key_manager = mock.Mock()
    mock_model_router = mock.Mock()

    agents = [
        AnalysisAgent(
            agent_id="a1", key_manager=mock_key_manager, model_router=mock_model_router
        ),
        SolutionAgent(
            agent_id="s1", key_manager=mock_key_manager, model_router=mock_model_router
        ),
        CriticAgent(
            agent_id="c1", key_manager=mock_key_manager, model_router=mock_model_router
        ),
        SecurityAgent(
            agent_id="sec1",
            key_manager=mock_key_manager,
            model_router=mock_model_router,
        ),
        OptimizerAgent(
            agent_id="o1", key_manager=mock_key_manager, model_router=mock_model_router
        ),
    ]

    for agent in agents:
        assert agent.agent_id in ["a1", "s1", "c1", "sec1", "o1"]
        response = await agent.think("hi")
        assert response == "OK"


@pytest.mark.asyncio
async def test_parse_debate_response_fallback(mock_genai):
    # Test fallback when LLM fails to return valid JSON
    mock_client = mock_genai.return_value
    mock_client.aio.models.generate_content = mock.AsyncMock(
        return_value=MockResponse("Not a JSON")
    )

    mock_key_manager = mock.Mock()
    mock_model_router = mock.Mock()

    agent = BaseAgent(
        role=AgentRole.SECURITY,
        agent_id="test-sec",
        key_manager=mock_key_manager,
        model_router=mock_model_router,
    )
    agent.set_mode(AgentMode.DEBATE)

    result = await agent.think("check this")

    assert isinstance(result, Argument)
    assert "Error parsing response" in result.content
    assert result.confidence == 0.1
