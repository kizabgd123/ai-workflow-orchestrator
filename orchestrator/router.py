from core.types import AgentRole
from typing import Dict, Any, Optional

class ModelRouter:
    def __init__(self):
        self.tiers = [
            "models/gemini-3.1-flash-lite",
            "models/gemini-3.1-flash",
            "models/gemini-3.1-pro",
            "models/gemini-3-deep-think",
            "models/gemma-2-9b-it",
            "models/gemma-2-27b-it"
        ]
        self.current_tier = 0

    def get_model(self, role: Optional[AgentRole] = None) -> str:
        if role in [AgentRole.GEMMA_A, AgentRole.GEMMA_B]:
            return "models/gemma-2-27b-it"
        return self.tiers[self.current_tier]

    def fallback(self):
        if self.current_tier < len(self.tiers) - 1:
            self.current_tier += 1
