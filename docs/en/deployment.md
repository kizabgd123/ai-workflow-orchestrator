---
title: "Implementation & Deployment"
description: "Technical instructions for application containerization, deploying to Google Cloud Run / GKE, and configuring Hugging Face Spaces"
keywords: "dockerfile, deployment, cloud run, gke container, uvicorn port, environment setup"
robots: "index, follow"
---

# 🚀 Implementation & Deployment

The **AI Workflow Orchestrator** is built to be highly portable, secure, and compatible with modern container environments.

This manual outlines the process of building container images, deploying to **Google Cloud Run** and **Kubernetes (GKE)**, and configuring hosting parameters on **Hugging Face Spaces**.

---

## 📦 Containerization: Dockerfile

To pack the orchestrator layer, we utilize an optimized, multi-stage Dockerfile using official Python-slim images to reduce the system's runtime attack surface.

```dockerfile
# STAGE 1: Dependency resolution and compilation
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2: Lightweight runtime execution
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy compiled dependencies and local source
COPY --from=builder /root/.local /root/.local
COPY . .

# Setup local storage directory for audit logs
RUN mkdir -p storage/traces

# Expose Uvicorn API port (compatible with Hugging Face standard port 7860)
EXPOSE 7860

CMD ["python", "-m", "uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## ☁️ Google Cloud Platform (GCP) Deployment

The pipeline fits into standard GCP security profiles under a strict zero-trust operational model.

### 1. Google Cloud Run Setup
Google Cloud Run represents the recommended hosting option for the FastAPI endpoint, enabling auto-scaling and support for concurrent connections.

* **Submit build image (gcloud):**
  ```bash
  gcloud builds submit --tag gcr.io/sixth-hawk-492717-m1/ai-workflow-orchestrator:latest
  ```
* **Deploy to Cloud Run:**
  ```bash
  gcloud run deploy ai-workflow-orchestrator \
      --image gcr.io/sixth-hawk-492717-m1/ai-workflow-orchestrator:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars="GOOGLE_CLOUD_PROJECT=sixth-hawk-492717-m1,MONGODB_DATABASE=ai_workflow_orchestrator" \
      --update-secrets="GOOGLE_API_KEY=gemini-api-key:latest,MONGODB_URI=mongodb-connection-string:latest"
  ```

> [!IMPORTANT]
> You must define the `GOOGLE_CLOUD_PROJECT` and `MONGODB_DATABASE` environment variables. Otherwise, the zero-trust `IdentityGuard` block will prevent execution from starting.

### 2. GKE Admission Control Policies
When running on Google Kubernetes Engine (GKE), standard GKE Admission Controllers actively block unsafe operations:
* **HostPath restriction:** Pod specifications attempting to mount local node filesystems are blocked to prevent container escapes.
* **Privileged pods:** Pod configurations must assert security profiles using rootless parameters (`runAsNonRoot: true`).

---

## 🤗 Hosting on Hugging Face Spaces (HF Spaces)

Hugging Face Spaces offers a practical sandbox to showcase the Uvicorn web server and its rich Glassmorphism dashboard interface.

### Space-Specific Overrides:
1. **Port binding:** Spaces mandate that containers bind exclusively to port `7860`.
2. **CORS policies:** API endpoints must support incoming requests from `huggingface.co` origins. In `api/routes.py`, the following middleware is defined:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"], # Or specify explicit HF subdomains
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. **Bypassing GCP Environment Checks:** Because Hugging Face spaces lack GCP project parameters, the `IdentityGuard` would fail by default. To support public demonstrations, configure this environment flag in your space settings:
   ```env
   SKIP_IDENTITY_CHECK=true
   ```
   This maintains high security in the locked production cluster while permitting test executions on the public demo URL.

---

## 🧪 Local Testing & Quality Verification

Prior to pushing code shifts, run the full PyTest suite to verify component integrity.

* **Execute test suite:**
  ```bash
  pytest tests/ -v
  ```

* **Test Suite Blueprint:**
  1. `test_agents.py`: Asserts that specialized agents correctly structure debate claims into parsed JSON formats with confidence rankings.
  2. `test_elo.py`: Validates ELO point calculations during simulated debate matches, asserting correct persistence inside the local SQLite database.
  3. `test_circuit_breaker.py`: Asserts that session operations are terminated immediately with a budget error if total API token consumption crosses `100,000` tokens.
