from core.types import AgentRole
from agents.base_agent import BaseAgent
from core.key_manager import KeyManager
from orchestrator.router import ModelRouter

class TimelineAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        key_manager: KeyManager,
        model_router: ModelRouter,
    ):
        super().__init__(AgentRole.TIMELINE, agent_id, key_manager, model_router)

class FitAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        key_manager: KeyManager,
        model_router: ModelRouter,
    ):
        super().__init__(AgentRole.FIT, agent_id, key_manager, model_router)

class CorrelationAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        key_manager: KeyManager,
        model_router: ModelRouter,
    ):
        super().__init__(AgentRole.CORRELATION, agent_id, key_manager, model_router)

class GemmaAgent(BaseAgent):
    def __init__(
        self,
        role: AgentRole,
        agent_id: str,
        key_manager: KeyManager,
        model_router: ModelRouter,
    ):
        super().__init__(role, agent_id, key_manager, model_router)

class GemmaAgentA(GemmaAgent):
    def __init__(self, agent_id: str, key_manager: KeyManager, model_router: ModelRouter):
        super().__init__(AgentRole.GEMMA_A, agent_id, key_manager, model_router)

class GemmaAgentB(GemmaAgent):
    def __init__(self, agent_id: str, key_manager: KeyManager, model_router: ModelRouter):
        super().__init__(AgentRole.GEMMA_B, agent_id, key_manager, model_router)
