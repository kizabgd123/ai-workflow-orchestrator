---
title: "FastAPI REST API Referenca"
description: "Sveobuhvatna API referenca za AI Workflow Orchestrator, definicije ruta, sheme zahtjeva i primjere integracije"
keywords: "API reference, FastAPI endpoints, request schema, REST API, SSE stream, JSON response"
robots: "index, follow"
---

# 🔌 FastAPI REST API Referenca

 FastAPi sloj (definisan u [api/server.py](file:///home/kizabgd/.gemini/extensions/ai-workflow-orchestrator/api/server.py)) obezbeđuje kompletan REST interfejs za asinhrono podnošenje workflow zahteva, nadgledanje procesa debata, upite nad forenzičkom memorijom i kontrolu token budžeta.

---

## 🚀 Bazne Rute i Swagger Dokumentacija

Kada se server pokrene lokalno (npr. preko `python -m uvicorn api.server:app --port 7860`), interaktivna dokumentacija je dostupna na:
* **Swagger UI:** `http://localhost:7860/api/docs`
* **ReDoc:** `http://localhost:7860/api/redoc`

---

## 📊 Pregled API Endpoint-ova

Sve rute su grupisane po funkcionalnim slojevima (Tagovima):

### 1. Grupa: `System` (Sistem)

#### `GET /api/health`
Vraća status operativnosti celokupnog sistema, uključujući status konekcije sa perzistentnim memorijskim slojem (MongoDB Atlas / SQLite).
* **Shema Odgovora (HealthResponse):**
  ```json
  {
    "status": "operational",
    "memory_backend": "MongoDB Atlas",
    "gemini_model": "gemini-2.5-flash",
    "version": "1.0.0"
  }
  ```

---

### 2. Grupa: `Workflow` (Tokovi rada)

#### `POST /api/workflow`
Asinhrono pokreće kompletan 11-stepeni orkestracioni pipeline. Korisnički zahtev se prosleđuje u Background Task, a API odmah vraća ID posla (HTTP 202 Accepted) radi sprečavanja blokiranja niti.
* **Telo Zahteva (WorkflowRequest):**
  ```json
  {
    "request": "Izgradi bezbednu Kubernetes admission kontrolu na GKE",
    "trace_id": "opciono-uuid-v4-string"
  }
  ```
* **Odgovor (HTTP 202):**
  ```json
  {
    "job_id": "job_9b1deb4d-3b7d-4bad-9bdd-2b0e7b3d2b0e",
    "status": "accepted"
  }
  ```

#### `GET /api/status/{job_id}`
Omogućava "polling" (periodične upite) statusa pokrenutog debatnog posla.
* **Statusi poslova:** `created`, `running`, `completed`, `failed`.
* **Primer Odgovora (completed):**
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

### 3. Grupa: `Memory` (Memorija)

#### `GET /api/debates`
Vraća najnovije zabeležene debate i trace-ove direktno iz MongoDB Atlasa (ili lokalnog SQLite-a u slučaju failover-a).
* **Query Parametri:** `limit` (Default: 5).
* **Primer Odgovora:**
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
Detektuje i prikazuje tačan broj dokumenata u Atlas kolekcijama (`debates`, `arguments`, `decision_history`).
* **Primer Odgovora:**
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

### 4. Grupa: `Security` (Sigurnost & Tokeni)

#### `GET /api/security/budget`
Vraća statistiku o potrošnji tokena Gemini modela u tekućoj sesiji i status prekidača (Circuit Breaker).
* **Primer Odgovora:**
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
Ručno resetuje brojač sesijskih tokena na nulu, čime se otključava rad sistema nakon tripping incidenta.
* **Odgovor:**
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
Omogućava dinamičku promenu token limita bez zaustavljanja ili restartovanja servera.
* **Telo Zahteva (BudgetLimitRequest):**
  ```json
  {
    "limit": 200000
  }
  ```
