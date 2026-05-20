import os
from typing import List, Optional

class KeyManager:
    def __init__(self, keys: List[str]):
        self.keys = keys
        self.index = 0
        self.failed_keys = set()

    @classmethod
    def from_env(cls) -> 'KeyManager':
        # Using the two keys provided by the user + any in ENV
        keys = [
            "AIzaSyAt6lxVZtbLiR2rwLHtHTwkGAZ3M-K2o1k",
            "AIzaSyBhVpDAL3GZHYAUFsqK122b3fAlLB31_sY"
        ]
        if os.environ.get("GOOGLE_API_KEY"):
            keys.append(os.environ.get("GOOGLE_API_KEY"))
        return cls(keys)

    def get_next_key(self) -> str:
        # Simple round-robin that skips failed keys
        if not self.keys:
            raise ValueError("No API keys available.")
        
        for _ in range(len(self.keys)):
            key = self.keys[self.index % len(self.keys)]
            self.index += 1
            if key not in self.failed_keys:
                return key
        
        # If all failed, reset failed keys and return the first one
        self.failed_keys.clear()
        return self.keys[0]

    def report_failure(self, key: str):
        self.failed_keys.add(key)
