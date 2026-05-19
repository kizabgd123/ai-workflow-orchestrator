import json
import logging
from typing import List, Dict, Any, Optional
from core.types import Argument, DebateOutcome, AgentRole
import uuid

logger = logging.getLogger("DebateAggregator")

class DebateAggregator:
    def __init__(self, db: Any = None):
        self.db = db

    def calculate_consensus(self, arguments: List[Argument]) -> DebateOutcome:
        """
        Aggregates arguments to reach a consensus decision.
        Implements weighted voting based on agent Elo, role specificity, 
        and historical accuracy from memory.
        """
        if not arguments:
            return DebateOutcome(
                debate_id=uuid.uuid4(),
                final_decision="REJECTED: No arguments provided.",
                confidence_score=0.0,
                arguments=[],
                rejected_alternatives=[],
                conflict_points=["Insufficient participation"],
                reasoning_trace="Debate failed due to lack of arguments."
            )

        # 1. Role Weights
        role_weights = {
            AgentRole.ANALYST: 1.0,
            AgentRole.SOLUTION: 1.2,
            AgentRole.CRITIC: 1.5,
            AgentRole.SECURITY: 2.0,
            AgentRole.OPTIMIZER: 0.8,
            AgentRole.AGGREGATOR: 1.0,
            AgentRole.VALIDATION: 1.3
        }

        pro_votes = 0.0
        contra_votes = 0.0
        total_weight = 0.0
        agent_elo_updates = {}

        # 2. Weighted Voting Logic
        for arg in arguments:
            # Base Elo from DB or default
            elo = 1200.0
            historical_accuracy = 1.0
            
            if self.db:
                elo = self.db.get_agent_elo(arg.agent_id)
                historical_accuracy = self.db.get_agent_historical_accuracy(arg.agent_id)
            
            # Reputation Multiplier: Elo (0.5 - 1.5) * Historical Accuracy (0.5 - 1.5)
            elo_multiplier = max(0.5, min(1.5, elo / 1200.0))
            weight = role_weights.get(arg.role, 1.0) * elo_multiplier * historical_accuracy
            
            vote_contribution = arg.confidence * weight
            if arg.is_pro:
                pro_votes += vote_contribution
            else:
                contra_votes += vote_contribution
            
            total_weight += weight
            agent_elo_updates[arg.agent_id] = elo

        # 3. Conflict & Contradiction Detection
        conflicts = []
        solution_args = [a for a in arguments if a.role == AgentRole.SOLUTION]
        critic_args = [a for a in arguments if a.role == AgentRole.CRITIC]
        security_args = [a for a in arguments if a.role == AgentRole.SECURITY]

        # Detect High-Confidence Contradictions
        for critic in critic_args:
            if not critic.is_pro and critic.confidence > 0.7:
                conflicts.append(f"Critic {critic.agent_id} raised high-confidence objection: {critic.content[:100]}...")
                # Adjust Elo based on conflict intensity
                for sol in solution_args:
                    agent_elo_updates[sol.agent_id] -= 5
                agent_elo_updates[critic.agent_id] += 10

        for security in security_args:
            if not security.is_pro and security.confidence >= 0.8:
                conflicts.append(f"Security Alert from {security.agent_id}: {security.content[:100]}...")
                # Security veto weight adjustment (dynamic)
                contra_votes += security.confidence * 5.0 
                agent_elo_updates[security.agent_id] += 20

        # 4. Decision Logic (Hard Thresholds Pattern)
        # Consensus Score = Pro / (Pro + Contra)
        total_votes = pro_votes + contra_votes
        consensus_score = pro_votes / total_votes if total_votes > 0 else 0.0
        
        # Hard Security Veto
        security_veto = any(not s.is_pro and s.confidence >= 0.9 for s in security_args)
        
        if security_veto:
            final_decision = "REJECTED: Critical security risk detected (Zero-Trust Veto)."
            logger.warning(f"Consensus REJECTED: {final_decision}", extra={"event": "debate.consensus", "status": "rejected", "confidence": consensus_score, "reason": "security_veto"})
        elif consensus_score < 0.40:
            final_decision = f"DEADLOCK: Consensus score ({consensus_score:.2f}) too low. Plan is rejected."
            logger.error(f"Consensus DEADLOCK: {final_decision}", extra={"event": "debate.consensus", "status": "deadlock", "confidence": consensus_score})
        elif consensus_score < 0.75:
            final_decision = f"ESCALATE: Significant doubt ({consensus_score:.2f}). Conflicts: {len(conflicts)}. Manual review required."
            logger.warning(f"Consensus DOUBT: {final_decision}", extra={"event": "debate.consensus", "status": "doubt", "confidence": consensus_score})
        else:
            final_decision = f"PROCEED: Consensus reached ({consensus_score:.2f}). Moving to execution."
            logger.info(f"Consensus REACHED: {final_decision}", extra={"event": "debate.consensus", "status": "success", "confidence": consensus_score})

        # 5. Reasoning Trace Construction
        trace = []
        for arg in arguments:
            support = "PRO" if arg.is_pro else "CON"
            trace.append(f"[{arg.role.value}] {support} | Confidence: {arg.confidence:.2f} | Reasoning: {arg.content[:150]}...")

        return DebateOutcome(
            debate_id=uuid.uuid4(),
            final_decision=final_decision,
            confidence_score=consensus_score,
            arguments=arguments,
            rejected_alternatives=[],
            conflict_points=conflicts,
            reasoning_trace="\n".join(trace),
            agent_elo_updates=agent_elo_updates
        )
