from core.key_manager import KeyManager
from orchestrator.router import ModelRouter
from typing import Optional
from agents.base_agent import BaseAgent
from core.types import AgentRole

class OptimizerAgent(BaseAgent):
    def __init__(self, agent_id: str, key_manager: KeyManager, model_router: ModelRouter):
        super().__init__(role=AgentRole.OPTIMIZER, agent_id=agent_id, key_manager=key_manager, model_router=model_router)
