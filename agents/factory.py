from typing import Optional
from core.types import AgentRole
from agents.analysis import AnalysisAgent
from agents.generation import GenerationAgent
from agents.coding import CodingAgent
from agents.cli import CLIAgent
from agents.validation import ValidationAgent
from agents.solution import SolutionAgent
from agents.critic import CriticAgent
from agents.security import SecurityAgent
from agents.optimizer import OptimizerAgent
from agents.aggregator import AggregatorAgent
from agents.google_services import TimelineAgent, FitAgent, CorrelationAgent, GemmaAgentA, GemmaAgentB
from agents.base_agent import BaseAgent
from core.key_manager import KeyManager
from orchestrator.router import ModelRouter

class AgentFactory:
    @staticmethod
    def create_agent(role: AgentRole, agent_id: str, key_manager: KeyManager, model_router: ModelRouter) -> BaseAgent:
        """Factory method to create specialized agents based on role."""
        agents = {
            AgentRole.ANALYST: AnalysisAgent,
            AgentRole.GENERATION: GenerationAgent,
            AgentRole.CODING: CodingAgent,
            AgentRole.CLI: CLIAgent,
            AgentRole.VALIDATION: ValidationAgent,
            AgentRole.SOLUTION: SolutionAgent,
            AgentRole.CRITIC: CriticAgent,
            AgentRole.SECURITY: SecurityAgent,
            AgentRole.OPTIMIZER: OptimizerAgent,
            AgentRole.AGGREGATOR: AggregatorAgent,
            AgentRole.TIMELINE: TimelineAgent,
            AgentRole.FIT: FitAgent,
            AgentRole.CORRELATION: CorrelationAgent,
            AgentRole.GEMMA_A: GemmaAgentA,
            AgentRole.GEMMA_B: GemmaAgentB,
        }
        
        agent_class = agents.get(role)
        if not agent_class:
            raise ValueError(f"Unknown agent role: {role}")
            
        return agent_class(agent_id=agent_id, key_manager=key_manager, model_router=model_router)
