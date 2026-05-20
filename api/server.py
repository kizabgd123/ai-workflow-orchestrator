"""
FastAPI REST API for AI Workflow Orchestrator
Google Cloud Rapid Agent Hackathon — MongoDB Track
"""

import os
import asyncio
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# 0. Setup Structured Logging (Zero Script QA)
from core.logging_setup import setup_logging
setup_logging()

# 1. Identity Check (Safety Pattern)
from core.identity import enforce_identity
enforce_identity()

app = FastAPI(
    title="AI Workflow Orchestrator",
    description="Multi-Agent Debate Engine — Google Cloud Rapid Agent Hackathon (MongoDB Track)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 2. Token Budget Circuit Breaker Middleware
from security.middleware import TokenBudgetMiddleware
app.add_middleware(TokenBudgetMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response Models ────────────────────────────────────────────────

class WorkflowRequest(BaseModel):
    request: str
    trace_id: Optional[str] = None

class PromptRequest(BaseModel):
    request: str

class PromptResponse(BaseModel):
    prompt: str

class WorkflowResponse(BaseModel):
    status: str
    trace_id: str
    workflow_id: str
    final_decision: Optional[str] = None
    confidence_score: Optional[float] = None
    debate_summary: Optional[Dict[str, Any]] = None
    message: str

class HealthResponse(BaseModel):
    status: str
    memory_backend: str
    gemini_model: str
    version: str

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Returns system health status including memory backend connection."""
    from memory.mongodb_atlas import MongoDBMemory
    
    memory = MongoDBMemory()
    health = memory.health_check()
    memory.close()
    
    return HealthResponse(
        status="operational",
        memory_backend=health.get("backend", "unknown"),
        gemini_model="gemini-2.5-flash",
        version="1.0.0"
    )

from api.status_manager import job_manager

@app.post("/api/workflow", status_code=202, tags=["Workflow"])
async def run_workflow(req: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Executes a full AI workflow with multi-agent debate asynchronously.
    """
    job_id = job_manager.create_job()
    
    async def task_wrapper(jid: str, request_text: str):
        try:
            from orchestrator.engine import WorkflowOrchestrator
            orchestrator = WorkflowOrchestrator()
            result = await orchestrator.process_request(request_text, job_id=jid)
            dumped_result = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
            job_manager.update_job(jid, "completed", dumped_result)
        except Exception as e:
            job_manager.update_job(jid, "failed", str(e))

    background_tasks.add_task(task_wrapper, job_id, req.request)
    return {"job_id": job_id, "status": "accepted"}

@app.post("/api/generate-prompt", response_model=PromptResponse, tags=["Workflow"])
async def generate_prompt(req: PromptRequest):
    """Generates a structured agent prompt from a user request."""
    prompt_text = f"""# AI Workflow Orchestrator Request

**Goal:** {req.request}

## Instructions for Agent
You are an execution agent within the AI Workflow Orchestrator. 
Your objective is to analyze the above request, formulate a plan, and execute it while adhering to the system's security and memory constraints. 

Please proceed with the initial analysis.
"""
    return {"prompt": prompt_text}

@app.get("/api/status/{job_id}", tags=["Workflow"])
async def get_job_status(job_id: str):
    """Polls the status of a debate job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/debates", tags=["Memory"])
async def get_recent_debates(limit: int = 5):
    """Returns recent debate sessions from MongoDB Atlas."""
    from memory.mongodb_atlas import MongoDBMemory
    memory = MongoDBMemory()
    debates = memory.get_recent_debates(limit=limit)
    health = memory.health_check()
    memory.close()
    return {
        "debates": debates,
        "backend": health.get("backend"),
        "count": len(debates)
    }

@app.get("/api/memory/health", tags=["Memory"])
async def memory_health():
    """Returns MongoDB Atlas connection status and collection stats."""
    from memory.mongodb_atlas import MongoDBMemory
    memory = MongoDBMemory()
    health = memory.health_check()
    memory.close()
    return health


@app.get("/api/huggingface/search", tags=["HuggingFace"])
async def huggingface_search(q: str = "gemma", limit: int = 10):
    """
    Search pre-trained models on Hugging Face Hub.
    Provides offline fallback to Gemma models if the official API is unreachable.
    """
    import urllib.request
    import urllib.parse
    import json

    if not q.strip():
        q = "gemma"

    try:
        url = f"https://huggingface.co/api/models?search={urllib.parse.quote(q)}&limit={limit}&sort=downloads&direction=-1"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Workflow-Orchestrator/1.0'}
        )
        # Timeout quickly to avoid UI blocking if user is offline or restricted
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())

        formatted = []
        for model in data:
            formatted.append({
                "id": model.get("id"),
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "pipeline_tag": model.get("pipeline_tag", "unknown"),
                "lastModified": model.get("lastModified"),
                "tags": model.get("tags", [])[:5]
            })
        return {"results": formatted, "count": len(formatted), "offline": False}
    except Exception as e:
        # Graceful fallback catalog
        offline_models = [
            {"id": "google/gemma-2-9b-it", "downloads": 245310, "likes": 1240, "pipeline_tag": "text-generation", "tags": ["gemma", "gemma2", "text-generation", "jax"]},
            {"id": "google/gemma-2-2b-it", "downloads": 185120, "likes": 988, "pipeline_tag": "text-generation", "tags": ["gemma", "gemma2", "text-generation", "edge-ai"]},
            {"id": "google/gemma-7b-it", "downloads": 320450, "likes": 1502, "pipeline_tag": "text-generation", "tags": ["gemma", "text-generation", "conversational"]},
            {"id": "google/gemma-2b-it", "downloads": 140180, "likes": 655, "pipeline_tag": "text-generation", "tags": ["gemma", "text-generation", "small-model"]},
            {"id": "google/code-gemma-7b-it", "downloads": 95130, "likes": 425, "pipeline_tag": "text-generation", "tags": ["gemma", "codegemma", "code-generation", "coding"]},
            {"id": "google/gemma-3-1b-it", "downloads": 395130, "likes": 2425, "pipeline_tag": "text-generation", "tags": ["gemma", "gemma3", "lightweight", "text-generation"]},
            {"id": "google/gemma-3-4b-it", "downloads": 495130, "likes": 3425, "pipeline_tag": "text-generation", "tags": ["gemma", "gemma3", "balanced", "text-generation"]}
        ]
        # Filter offline catalog based on query
        filtered = [m for m in offline_models if q.lower() in m["id"].lower()]
        if not filtered:
            # If no matches, return general top models
            filtered = offline_models[:4]
        return {"results": filtered, "count": len(filtered), "offline": True}

@app.get("/api/agents", tags=["Agents"])
async def list_agents():
    """Returns available agent definitions and their MCP tool schemas."""
    from memory.mongodb_atlas import MCP_TOOL_DEFINITIONS
    return {
        "agents": [
            {"id": "analyst", "role": "ANALYST", "mode": ["EXECUTION", "DEBATE"]},
            {"id": "solution", "role": "SOLUTION", "mode": ["EXECUTION", "DEBATE"]},
            {"id": "critic", "role": "CRITIC", "mode": ["DEBATE"]},
            {"id": "security", "role": "SECURITY", "mode": ["EXECUTION", "DEBATE"]},
            {"id": "optimizer", "role": "OPTIMIZER", "mode": ["DEBATE"]},
        ],
        "mcp_tools": MCP_TOOL_DEFINITIONS,
        "debate_rounds": 5,
        "model": "gemini-2.5-flash"
    }

# ─── Security & Budgeting Endpoints ───────────────────────────────────────────

class BudgetLimitRequest(BaseModel):
    limit: int

@app.get("/api/security/budget", tags=["Security"])
async def get_budget_stats():
    """Returns the current token budget stats and circuit breaker status."""
    from security.token_budget import TokenBudgetTracker
    tracker = TokenBudgetTracker()
    return tracker.get_stats()

@app.post("/api/security/budget/reset", tags=["Security"])
async def reset_budget():
    """Resets the token budget consumption back to zero."""
    from security.token_budget import TokenBudgetTracker
    tracker = TokenBudgetTracker()
    tracker.reset()
    return {"message": "Token budget reset successful.", "stats": tracker.get_stats()}

@app.post("/api/security/budget/limit", tags=["Security"])
async def update_budget_limit(req: BudgetLimitRequest):
    """Dynamically updates the token budget limit."""
    from security.token_budget import TokenBudgetTracker
    tracker = TokenBudgetTracker()
    tracker.set_limit(req.limit)
    return {"message": f"Token budget limit updated to {req.limit}.", "stats": tracker.get_stats()}

# ─── Static Frontend ──────────────────────────────────────────────────────────

import os as _os
_static = _os.path.join(_os.path.dirname(__file__), "..", "static")
if _os.path.isdir(_static):
    app.mount("/", StaticFiles(directory=_static, html=True), name="static")

# ─── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("api.server:app", host="0.0.0.0", port=port, reload=False)
