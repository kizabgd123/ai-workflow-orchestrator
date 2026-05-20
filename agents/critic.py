from core.key_manager import KeyManager
from orchestrator.router import ModelRouter
from typing import Optional
from agents.base_agent import BaseAgent
from core.types import AgentRole

class CriticAgent(BaseAgent):
    def __init__(self, agent_id: str, key_manager: KeyManager, model_router: ModelRouter):
        super().__init__(role=AgentRole.CRITIC, agent_id=agent_id, key_manager=key_manager, model_router=model_router)
