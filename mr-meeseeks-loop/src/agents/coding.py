from src.agents.base_agent import BaseMeeseeksAgent

class PlanAgent(BaseMeeseeksAgent):
    def __init__(self):
        super().__init__("Planner")

    def execute(self, objective: str):
        self.shout(f"I'm planning how to {objective}! Caaaan do!")
        return f"Refined plan for {objective}"

class ImplementAgent(BaseMeeseeksAgent):
    def __init__(self):
        super().__init__("Implementer")

    def execute(self, plan: str):
        self.shout(f"I'm writing the code based on the plan! Look at me!")
        return "New code changes"
