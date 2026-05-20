from core.key_manager import KeyManager
from orchestrator.router import ModelRouter
from typing import Optional, Union
from agents.base_agent import BaseAgent
from core.types import AgentRole, Argument

class AnalysisAgent(BaseAgent):
    def __init__(self, agent_id: str, key_manager: KeyManager, model_router: ModelRouter):
        super().__init__(role=AgentRole.ANALYST, agent_id=agent_id, key_manager=key_manager, model_router=model_router)

    async def analyze_problem(self, problem: str) -> str:
        """Specific analysis method to structure the problem."""
        prompt = f"Decompose this problem and identify key risks: {problem}"
        return await self.think(prompt)
