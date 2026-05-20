import pytest
from debate.aggregator import DebateAggregator
from core.types import Argument, AgentRole, DebateOutcome
from uuid import uuid4

class MockDB:
    def __init__(self):
        self.elos = {}
    
    def get_agent_elo(self, agent_id):
        return self.elos.get(agent_id, 1200.0)

def test_elo_security_veto():
    db = MockDB()
    db.elos["sol-1"] = 1200.0
    db.elos["sec-1"] = 1200.0
    
    aggregator = DebateAggregator(db=db)
    
    args = [
        Argument(agent_id="sol-1", role=AgentRole.SOLUTION, content="Do something risky", confidence=0.9, round=1),
        Argument(agent_id="sec-1", role=AgentRole.SECURITY, content="VETO: Critical security leak detected!", confidence=0.9, round=1)
    ]
    
    outcome = aggregator.calculate_consensus(args)
    
    assert "REJECTED" in outcome.final_decision
    assert "sec-1" in outcome.agent_elo_updates
    assert "sol-1" in outcome.agent_elo_updates
    assert outcome.agent_elo_updates["sec-1"] > 1200.0
    assert outcome.agent_elo_updates["sol-1"] < 1200.0

def test_elo_calculation_standard_duel():
    db = MockDB()
    db.elos["sol-1"] = 1200.0
    db.elos["crit-1"] = 1200.0
    
    aggregator = DebateAggregator(db=db)
    
    # Scenario 1: Critic wins (high risk)
    args_critic_wins = [
        Argument(agent_id="sol-1", role=AgentRole.SOLUTION, content="Solution A", confidence=0.8, round=1),
        Argument(agent_id="crit-1", role=AgentRole.CRITIC, content="Fatal flaw found", confidence=0.9, round=1)
    ]
    
    outcome1 = aggregator.calculate_consensus(args_critic_wins)
    assert outcome1.agent_elo_updates["crit-1"] > 1200.0
    assert outcome1.agent_elo_updates["sol-1"] < 1200.0
    
    # Scenario 2: Solution wins (low risk)
    args_sol_wins = [
        Argument(agent_id="sol-1", role=AgentRole.SOLUTION, content="Solution B", confidence=0.9, round=1),
        Argument(agent_id="crit-1", role=AgentRole.CRITIC, content="Minor nitpick", confidence=0.2, round=1)
    ]
    
    outcome2 = aggregator.calculate_consensus(args_sol_wins)
    assert outcome2.agent_elo_updates["sol-1"] > 1200.0
    assert outcome2.agent_elo_updates["crit-1"] < 1200.0

def test_elo_weighting_impact():
    db = MockDB()
    # sol-high is very experienced, sol-low is a novice
    db.elos["sol-high"] = 1600.0
    db.elos["sol-low"] = 800.0
    
    aggregator = DebateAggregator(db=db)
    
    # Argument from high Elo agent should have more weight
    arg_high = Argument(agent_id="sol-high", role=AgentRole.SOLUTION, content="Strong solution", confidence=0.7, round=1)
    arg_low = Argument(agent_id="sol-low", role=AgentRole.SOLUTION, content="Weak solution", confidence=0.7, round=1)
    
    # We need to peek into the logic or infer from confidence_score
    # In current implementation, weight = max(0.5, min(1.5, elo / 1200.0))
    # sol-high weight = 1600/1200 = 1.33
    # sol-low weight = 800/1200 = 0.66
    
    outcome_high = aggregator.calculate_consensus([arg_high])
def test_elo_convergence():
    db = MockDB()
    # sol-1 is actually better (consistently low critic risk)
    # sol-2 is actually worse (consistently high critic risk)
    sol1_id = "sol-good"
    sol2_id = "sol-bad"
    crit_id = "crit-1"
    
    db.elos[sol1_id] = 1200.0
    db.elos[sol2_id] = 1200.0
    db.elos[crit_id] = 1200.0
    
    aggregator = DebateAggregator(db=db)
    
    # Simulate 10 duels for each
    for _ in range(10):
        # Good solution vs Critic (Solution wins)
        args1 = [
            Argument(agent_id=sol1_id, role=AgentRole.SOLUTION, content="Good", confidence=0.9, round=1),
            Argument(agent_id=crit_id, role=AgentRole.CRITIC, content="Weak critique", confidence=0.2, round=1)
        ]
        outcome1 = aggregator.calculate_consensus(args1)
        db.elos[sol1_id] = outcome1.agent_elo_updates[sol1_id]
        db.elos[crit_id] = outcome1.agent_elo_updates[crit_id]
        
        # Bad solution vs Critic (Critic wins)
        args2 = [
            Argument(agent_id=sol2_id, role=AgentRole.SOLUTION, content="Bad", confidence=0.5, round=1),
            Argument(agent_id=crit_id, role=AgentRole.CRITIC, content="Strong critique", confidence=0.9, round=1)
        ]
        outcome2 = aggregator.calculate_consensus(args2)
        db.elos[sol2_id] = outcome2.agent_elo_updates[sol2_id]
        db.elos[crit_id] = outcome2.agent_elo_updates[crit_id]
        
    assert db.elos[sol1_id] > 1200.0
    assert db.elos[sol2_id] < 1200.0
    # Critic balanced out somewhat but should be different from 1200
    assert db.elos[crit_id] != 1200.0
    print(f"\nFinal Elos: Good Sol: {db.elos[sol1_id]:.2f}, Bad Sol: {db.elos[sol2_id]:.2f}, Critic: {db.elos[crit_id]:.2f}")
