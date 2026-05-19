from typing import Dict, List, Optional, Any
import logging
from core.types import AgentRole, AgentMode, Argument, DebateOutcome
from agents.base_agent import BaseAgent
from debate.aggregator import DebateAggregator

logger = logging.getLogger("DebateManager")

class DebateManager:
    """
    Orchestrates the debate rounds between agents.
    Implements Multi-Pass Heuristics (Rule of 3) for refinement.
    """

    def __init__(self, aggregator: Optional[DebateAggregator] = None, db: Optional[Any] = None):
        self.aggregator = aggregator or DebateAggregator(db=db)
        self.db = db
        self.max_refinement_rounds = 3 # "Rule of 3" for adversarial refinements

    def _send_debate_event(self, job_id: Optional[str], agent: Any, arg: Argument):
        if not job_id:
            return
        try:
            from api.status_manager import job_manager
            
            elo = 1200.0
            if self.db:
                elo = self.db.get_agent_elo(agent.agent_id)
                
            job_manager.add_event(job_id, "debate_round", {
                "agent_id": agent.agent_id,
                "role": agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
                "round": arg.round,
                "content": arg.content,
                "confidence": arg.confidence,
                "is_pro": arg.is_pro,
                "elo": elo
            })
        except Exception as e:
            logger.warning(f"Failed to stream debate event: {e}")

    async def run_debate(
        self, 
        problem_statement: str, 
        agents: Dict[AgentRole, BaseAgent],
        memory_context: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> DebateOutcome:
        """
        Runs the full debate process with iterative refinement.
        Uses historical context to inform the debate.
        """
        
        arguments: List[Argument] = []
        debate_history: List[str] = [f"Problem Statement: {problem_statement}"]
        if memory_context:
            debate_history.append(f"Historical Context (Memory): {memory_context}")

        # Set all participating agents to DEBATE mode
        for agent in agents.values():
            agent.set_mode(AgentMode.DEBATE)

        # INITIAL ROUNDS
        
        # Round 1: Analysis
        if AgentRole.ANALYST in agents:
            analyst = agents[AgentRole.ANALYST]
            arg = await analyst.think(prompt=problem_statement, context="\n".join(debate_history))
            if isinstance(arg, Argument):
                arg.round = 1
                arguments.append(arg)
                debate_history.append(f"Analyst (R1): {arg.content}")
                self._send_debate_event(job_id, analyst, arg)

        # Round 2: Solution
        if AgentRole.SOLUTION in agents:
            solution_agent = agents[AgentRole.SOLUTION]
            arg = await solution_agent.think(prompt="Propose a detailed solution plan.", context="\n".join(debate_history))
            if isinstance(arg, Argument):
                arg.round = 2
                arguments.append(arg)
                debate_history.append(f"Solution Agent (R2): {arg.content}")
                self._send_debate_event(job_id, solution_agent, arg)

        # Round 3: Critic (Hard Adversarial)
        if AgentRole.CRITIC in agents:
            critic = agents[AgentRole.CRITIC]
            arg = await critic.think(prompt="Critique the proposed solution. Identify flaws and edge cases.", context="\n".join(debate_history))
            if isinstance(arg, Argument):
                arg.round = 3
                arguments.append(arg)
                debate_history.append(f"Critic Agent (R3): {arg.content}")
                self._send_debate_event(job_id, critic, arg)

        # Round 4: Security (Zero-Trust)
        if AgentRole.SECURITY in agents:
            security_agent = agents[AgentRole.SECURITY]
            arg = await security_agent.think(prompt="Perform a security audit on the proposal.", context="\n".join(debate_history))
            if isinstance(arg, Argument):
                arg.round = 4
                arguments.append(arg)
                debate_history.append(f"Security Agent (R4): {arg.content}")
                self._send_debate_event(job_id, security_agent, arg)

        # Round 5: Optimizer
        if AgentRole.OPTIMIZER in agents:
            optimizer = agents[AgentRole.OPTIMIZER]
            arg = await optimizer.think(prompt="Suggest optimizations or more efficient alternatives.", context="\n".join(debate_history))
            if isinstance(arg, Argument):
                arg.round = 5
                arguments.append(arg)
                debate_history.append(f"Optimizer Agent (R5): {arg.content}")
                self._send_debate_event(job_id, optimizer, arg)

        # ITERATIVE REFINEMENT LOOP (The "Refine Pass")
        for refinement_pass in range(self.max_refinement_rounds):
            current_outcome = self.aggregator.calculate_consensus(arguments)
            
            # Check for high-confidence consensus or definitive rejection
            if current_outcome.confidence_score > 0.85 or "REJECTED" in current_outcome.final_decision:
                logger.info(f"Refinement Loop exited early at pass {refinement_pass} (Confidence: {current_outcome.confidence_score:.2f})")
                break
                
            debate_history.append(f"--- REFINEMENT PASS {refinement_pass + 1} (Current Confidence: {current_outcome.confidence_score:.2f}) ---")
            debate_history.append(f"Identified Conflicts: {'; '.join(current_outcome.conflict_points)}")
            
            # Solution Agent attempts to fix concerns
            if AgentRole.SOLUTION in agents:
                solution_agent = agents[AgentRole.SOLUTION]
                arg = await solution_agent.think(
                    prompt=f"Revise your solution to address these conflicts: {current_outcome.conflict_points}",
                    context="\n".join(debate_history)
                )
                if isinstance(arg, Argument):
                    arg.round = 10 + refinement_pass
                    arguments.append(arg)
                    debate_history.append(f"Solution Agent (Refined): {arg.content}")
                    self._send_debate_event(job_id, solution_agent, arg)

        # FINAL ROUND: Aggregator
        if AgentRole.AGGREGATOR in agents:
            aggregator_agent = agents[AgentRole.AGGREGATOR]
            arg = await aggregator_agent.think(
                prompt="Provide the final definitive consensus based on the entire debate history.",
                context="\n".join(debate_history)
            )
            if isinstance(arg, Argument):
                arg.round = 100
                arguments.append(arg)
                self._send_debate_event(job_id, aggregator_agent, arg)

        # Final consensus calculation via the Aggregator logic
        final_outcome = self.aggregator.calculate_consensus(arguments)
        
        # Reset agents to EXECUTION mode for downstream tasks
        for agent in agents.values():
            agent.set_mode(AgentMode.EXECUTION)
            
        return final_outcome
