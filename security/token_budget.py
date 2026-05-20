import threading
import logging
from typing import Dict, Any

logger = logging.getLogger("TokenBudgetTracker")

class TokenBudgetTracker:
    """
    Thread-safe Singleton that tracks token consumption across all agent tasks.
    Acts as a circuit breaker when the maximum budget is exceeded.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TokenBudgetTracker, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, limit: int = 100000):
        if self._initialized:
            return
        self.limit = limit
        self.consumed_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self._lock = threading.Lock()
        self._initialized = True
        logger.info(f"Initialized TokenBudgetTracker with limit={limit}")

    def consume(self, input_tokens: int, output_tokens: int):
        """Records token usage and checks if budget is exceeded."""
        with self._lock:
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens
            self.consumed_tokens += (input_tokens + output_tokens)
            logger.info(
                f"[TOKEN BUDGET] Consumed {input_tokens} input, {output_tokens} output. "
                f"Total: {self.consumed_tokens}/{self.limit} tokens."
            )

    def is_tripped(self) -> bool:
        """Returns True if the token limit has been reached or exceeded."""
        with self._lock:
            return self.consumed_tokens >= self.limit

    def reset(self):
        """Resets the token tracker metrics back to zero."""
        with self._lock:
            self.consumed_tokens = 0
            self.input_tokens = 0
            self.output_tokens = 0
            logger.info("[TOKEN BUDGET] Tracker reset successfully.")

    def set_limit(self, limit: int):
        """Dynamically updates the token budget limit."""
        with self._lock:
            self.limit = limit
            logger.info(f"[TOKEN BUDGET] Budget limit updated to {limit} tokens.")

    def get_stats(self) -> Dict[str, Any]:
        """Returns the current token consumption metrics."""
        with self._lock:
            return {
                "limit": self.limit,
                "consumed_tokens": self.consumed_tokens,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "remaining_tokens": max(0, self.limit - self.consumed_tokens),
                "is_tripped": self.consumed_tokens >= self.limit
            }
