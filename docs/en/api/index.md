---
title: "FastAPI REST API Reference"
description: "Comprehensive API reference for the AI Workflow Orchestrator system, route definitions, schemas, and usage examples"
keywords: "API reference, FastAPI endpoints, request schema, REST API, SSE stream, JSON response"
robots: "index, follow"
---

# 🔌 FastAPI REST API Reference

The FastAPI HTTP application layer (defined in [api/server.py](file:///home/kizabgd/.gemini/extensions/ai-workflow-orchestrator/api/server.py)) provides a robust REST interface for asynchronously submitting workflow plans, querying live debate states, inspecting forensic databases, and resetting session token thresholds.

---

## 🚀 Base Endpoints & Swagger Specifications

When booting the server locally (e.g. via `python -m uvicorn api.server:app --port 7860`), interactive documentation pages are available at:
* **Interactive Swagger UI:** `http://localhost:7860/api/docs`
* **Structured ReDoc specification:** `http://localhost:7860/api/redoc`

---

## 📊 REST Endpoint Blueprints

Endpoints are partitioned by functional tags:

### Tag Group 1: `System`

#### `GET /api/health`
Inspects overall status, verifying whether the persistent memory controllers are connected to MongoDB Atlas or executing SQLite fallback loops.
* **Response Body Schema (HealthResponse):**
  ```json
  {
    "status": "operational",
    "memory_backend": "MongoDB Atlas",
    "gemini_model": "gemini-2.5-flash",
    "version": "1.0.0"
  }
  ```

---

### Tag Group 2: `Workflow`

#### `POST /api/workflow`
Asynchronously triggers the 11-step orchestration pipeline. Requests are immediately queued as Background Tasks, returning a unique job identifier (HTTP 202 Accepted) to avoid blocking threads during Gemini API reasoning loops.
* **Request Body Payload (WorkflowRequest):**
  ```json
  {
    "request": "Implement a secure Kubernetes Admission Controller on GKE",
    "trace_id": "optional-uuid-v4-string"
  }
  ```
* **Response Body (HTTP 202):**
  ```json
  {
    "job_id": "job_9b1deb4d-3b7d-4bad-9bdd-2b0e7b3d2b0e",
    "status": "accepted"
  }
  ```

#### `GET /api/status/{job_id}`
Retrieves current execution variables for an active background job.
* **Job States:** `created`, `running`, `completed`, `failed`.
* **Example Response (completed job):**
  ```json
  {
    "job_id": "job_9b1deb4d-3b7d-4bad-9bdd-2b0e7b3d2b0e",
    "status": "completed",
    "result": {
      "trace_id": "673fbbfa-2fcd-40a2-9477-9be7365691c2",
      "workflow_id": "workflow_589b3f",
      "final_decision": "PROCEED: Consensus reached. Plan: Deploy securityContext with runAsNonRoot: true...",
      "confidence_score": 0.88,
      "message": "Workflow completed successfully"
    }
  }
  ```

---

### Tag Group 3: `Memory`

#### `GET /api/debates`
Retrieves a list of recent debate decisions directly from the MongoDB Atlas database (or local SQLite during offline fallbacks).
* **Query Parameters:** `limit` (Default: 5).
* **Response Structure:**
  ```json
  {
    "debates": [
      {
        "debate_id": "673fbbfa-2fcd-40a2-9477-9be7365691c2",
        "final_decision": "PROCEED: Consensus reached...",
        "confidence_score": 0.88,
        "created_at": "2026-05-18T17:05:30Z"
      }
    ],
    "backend": "MongoDB Atlas",
    "count": 1
  }
  ```

#### `GET /api/memory/health`
Returns exact document counts across active Atlas Collections (`debates`, `arguments`, `decision_history`).
* **Example Response:**
  ```json
  {
    "status": "connected",
    "backend": "MongoDB Atlas",
    "database": "ai_workflow_orchestrator",
    "collections": {
      "debates": 142,
      "arguments": 710,
      "decisions": 48
    }
  }
  ```

---

### Tag Group 4: `Security`

#### `GET /api/security/budget`
Inspects current LLM API token consumption stats and asserts whether the Circuit Breaker is tripped.
* **Example Response:**
  ```json
  {
    "input_tokens_consumed": 24050,
    "output_tokens_consumed": 8900,
    "total_tokens_consumed": 32950,
    "limit": 100000,
    "is_tripped": false
  }
  ```

#### `POST /api/security/budget/reset`
Resets the session token accumulator counters back to zero, unlocking agent reasoning paths after a tripping incident.
* **Response:**
  ```json
  {
    "message": "Token budget reset successful.",
    "stats": {
      "input_tokens_consumed": 0,
      "output_tokens_consumed": 0,
      "total_tokens_consumed": 0,
      "limit": 100000,
      "is_tripped": false
    }
  }
  ```

#### `POST /api/security/budget/limit`
Enables dynamically adjusting the token limit threshold at runtime without stopping or restarting Uvicorn processes.
* **Request Payload (BudgetLimitRequest):**
  ```json
  {
    "limit": 200000
  }
  ```
