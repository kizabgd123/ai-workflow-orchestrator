import uuid
from typing import List, Dict, Any
from core.base import DebateParticipant

class DebateEngine:
    def __init__(self, memory_system):
        self.memory = memory_system

    async def run_debate(self, objective: str, participants: List[DebateParticipant], context: Dict[str, Any]) -> Dict[str, Any]:
        debate_id = str(uuid.uuid4())
        arguments = []
        
        # 1. Sequential contribution based on roles
        # Analyst first
        for agent in participants:
            arg = await agent.provide_argument(context, objective)
            arguments.append(arg)

        # 2. Final aggregation logic (Aggregation Engine)
        consensus = self._calculate_consensus(arguments)
        
        debate_result = {
            "id": debate_id,
            "context": str(context),
            "objective": objective,
            "arguments": arguments,
            "consensus_decision": consensus["decision"],
            "confidence_score": consensus["score"],
            "reasoning_trace": consensus["trace"],
            "conflict_points": consensus["conflicts"],
            "rejected_alternatives": consensus["rejected"]
        }
        
        # Store in memory
        self.memory.store_debate(debate_result)
        
        return debate_result

    def _calculate_consensus(self, arguments: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Multi-agent decision logic with memory-based weighting
        # For now, a weighted average based on confidence scores and is_pro/is_contra
        
        pro_score = 0.0
        contra_score = 0.0
        trace = []
        conflicts = []
        
        for arg in arguments:
            score = arg.get('confidence_score', 0.5)
            if arg.get('is_pro', True):
                pro_score += score
            else:
                contra_score += score
                conflicts.append(f"{arg['agent_name']}: {arg['argument']}")
            
            trace.append(f"{arg['agent_name']} ({score}): {arg['argument']}")

        decision = "APPROVED" if pro_score > contra_score else "REJECTED"
        
        return {
            "decision": decision,
            "score": pro_score / (pro_score + contra_score) if (pro_score + contra_score) > 0 else 0.0,
            "trace": "\n".join(trace),
            "conflicts": conflicts,
            "rejected": ["Alternative A"] if decision == "APPROVED" else ["Original Proposal"]
        }
