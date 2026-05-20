from src.agents.base_agent import BaseMeeseeksAgent

class TestAgent(BaseMeeseeksAgent):
    def __init__(self):
        super().__init__("Tester")

    def execute(self, code: str):
        self.shout("Running tests! Ooh yeah!")
        return "PASS"

class DebugAgent(BaseMeeseeksAgent):
    def __init__(self):
        super().__init__("Debugger")

    def execute(self, failures: str):
        self.shout("I'm fixing the bugs so I can die! AGHH!")
        return "Bug fixes applied"

class ReflectAgent(BaseMeeseeksAgent):
    def __init__(self):
        super().__init__("Reflector")

    def execute(self, iteration_history: str):
        self.shout("Reflecting on our progress... Are we there yet?!")
        return "Iteration reflection"
