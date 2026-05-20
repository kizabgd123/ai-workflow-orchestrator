class BaseMeeseeksAgent:
    def __init__(self, name: str):
        self.name = name

    def shout(self, message: str):
        print(f"MR. MEESEEKS ({self.name}): {message}")

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Each Meeseeks must implement execute()!")
