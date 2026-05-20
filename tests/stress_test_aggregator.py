import pytest
from debate.aggregator import DebateAggregator
from core.types import Argument, AgentRole, DebateOutcome
from uuid import uuid4

class MockDB:
    def get_agent_elo(self, agent_id):
        return 1200.0

def test_empty_arguments():
    """System should handle zero arguments without crashing."""
    agg = DebateAggregator(db=MockDB())
    outcome = agg.calculate_consensus([])
    assert "No solution proposed" in outcome.final_decision
    assert outcome.confidence_score == 0.0

def test_zero_confidence_agents():
    """System should handle 0.0 confidence without crash."""
    agg = DebateAggregator(db=MockDB())
    args = [
        Argument(agent_id="sol", role=AgentRole.SOLUTION, content="Plan", confidence=0.0, round=1),
        Argument(agent_id="crit", role=AgentRole.CRITIC, content="Con", confidence=0.0, round=2)
    ]
    outcome = agg.calculate_consensus(args)
    assert outcome.confidence_score == 0.0

def test_extreme_elo_overflow():
    """Verify that very high Elo is capped by weight limits."""
    class ExtremeDB:
        def get_agent_elo(self, agent_id): return 1000000.0 # God-like Elo
    
    agg = DebateAggregator(db=ExtremeDB())
    args = [Argument(agent_id="sol", role=AgentRole.SOLUTION, content="P", confidence=1.0, round=1)]
    outcome = agg.calculate_consensus(args)
    # Weight is capped at 1.5. Solution weight is 0.4.
    # 1.0 (conf) * 1.5 (weight) * 0.4 (role weight) = 0.6
    assert outcome.confidence_score == 0.6

def test_division_by_zero_risk():
    """Ensure no division by zero when solution_score is 0."""
    agg = DebateAggregator(db=MockDB())
    args = [
        Argument(agent_id="sol", role=AgentRole.SOLUTION, content="P", confidence=0.0, round=1),
        Argument(agent_id="crit", role=AgentRole.CRITIC, content="C", confidence=1.0, round=2)
    ]
    # In code: if critic_risk > 0.5 * solution_score: 
    # 0.3 > 0.5 * 0 -> Should be True.
    outcome = agg.calculate_consensus(args)
    assert outcome.agent_elo_updates["sol"] < 1200.0 # Solution lost
    assert outcome.agent_elo_updates["crit"] > 1200.0 # Critic won
