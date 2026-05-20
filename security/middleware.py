import logging
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from security.token_budget import TokenBudgetTracker

logger = logging.getLogger("TokenBudgetMiddleware")

class TokenBudgetMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks token budget state.
    Acts as a circuit breaker for API requests if the budget is tripped.
    """
    async def dispatch(self, request: Request, call_next):
        tracker = TokenBudgetTracker()
        
        # Check if the circuit breaker is tripped
        if tracker.is_tripped():
            # Allow reset requests even if the budget is tripped
            if request.url.path == "/api/security/budget/reset" and request.method == "POST":
                logger.warning("[CIRCUIT BREAKER] Bypassing circuit breaker for budget reset request.")
                return await call_next(request)
                
            # Allow health checking and other system/status queries so the UI doesn't completely die
            if request.url.path in ["/api/health", "/api/security/budget", "/api/memory/health", "/api/agents"]:
                return await call_next(request)
            
            logger.error("[CIRCUIT BREAKER] Request blocked: Token budget exceeded!")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "detail": "Service Temporarily Unavailable: AI agent token budget limit exceeded (Circuit Breaker active).",
                    "stats": tracker.get_stats()
                }
            )
            
        response = await call_next(request)
        return response
