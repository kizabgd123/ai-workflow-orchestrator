---
title: "SOP-001: Installation & Setup Guide"
description: "SOP guide to install, configure, and boot the AI Workflow Orchestrator application"
keywords: "installation guide, environment setup, python uvicorn, api rotation, key manager, mongodb setup"
robots: "index, follow"
---

# 🛠️ SOP-001: Installation & Setup Guide

This Standard Operating Procedure (SOP) runbook provides step-by-step instructions for setting up workspace environments, installing dependencies, binding LLM API keys, managing rotation schemas, and executing the **AI Workflow Orchestrator**.

---

## 📋 1. Prerequisites & System Constraints

Ensure the host environment meets the following specifications:
* **OS:** Linux (Ubuntu 20.04+ recommended) or macOS.
* **Python version:** `3.10` or newer (`3.11` compatible).
* **Disk Space:** At least `500MB` available space for runtime logs, trace artifacts, and SQLite database storage.

---

## 💾 2. Clone Workspace & Install Requirements

Execute the following terminal commands to fetch the repository and resolve packages:

1. **Clone the code repository:**
   ```bash
   git clone https://github.com/kiza101288/ai-workflow-orchestrator.git
   cd ai-workflow-orchestrator
   ```

2. **Scaffold and load a dedicated Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install pinned dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🔑 3. API Key Mapping & Rotation Schemas

The orchestration core integrates a dynamic **KeyManager** to manage Gemini API credentials. If an API request trips rate limit boundaries (HTTP 429), the KeyManager automatically flags the blocked credential, removes it from the active rotation pool, and transparently routes execution to the next available key.

### Loading API credentials via environment variables:
Inject your Gemini credentials as a comma-separated array inside the `GOOGLE_API_KEY` configuration:
```bash
export GOOGLE_API_KEY="AIzaSyA1...,AIzaSyA2...,AIzaSyA3..."
```
The KeyManager inside [key_manager.py](file:///home/kizabgd/.gemini/extensions/ai-workflow-orchestrator/core/key_manager.py) will dynamically split these strings and rotate them using a round-robin schema during agent turns.

---

## ☁️ 4. MongoDB Atlas Cloud Memory Integration

To index long-term forensic logs and execute Vector similarity lookups of past arguments, the orchestrator connects to MongoDB Atlas.

1. **Fetch your MongoDB connection URI from the Atlas Console** (verify that your host or container IP address is whitelisted in the Network Access security tab).
2. **Inject the environment variable:**
   ```bash
   export MONGODB_URI="mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority"
   ```
3. **Database and Collections Scaffold:** The database target is set to `ai_workflow_orchestrator`. Upon initial connection, the MongoDBMemory connector automatically indexes the `debates`, `arguments`, and `decision_history` collections.

*If `MONGODB_URI` remains empty or network connections fail, the memory layer automatically activates a local failover cache pointing to the SQLite database at `storage/memory.db`.*

---

## 🔒 5. Bypassing Workspace Verification in Non-Production Envs

The zero-trust `IdentityGuard` in `core/identity.py` verifies environment parameters before starting. It expects `GOOGLE_CLOUD_PROJECT` to map exactly to `sixth-hawk-492717-m1` and `MONGODB_DATABASE` to `ai_workflow_orchestrator`.

If you run the application in a local testing sandbox or public demonstration environment (e.g. Hugging Face Spaces), the identity check will block startup. To bypass this lock safely:
```bash
export SKIP_IDENTITY_CHECK=true
```

---

## 🏃 6. Running the System

You can run the orchestrator through two interfaces:

### Interface A: CLI Runner (Terminal Execution)
To submit a single natural language task and display the multi-round debate sequence in your terminal:
```bash
python main.py "deploy a secure database cluster on GKE"
```

### Interface B: FastAPI Server & Web Dashboard
To start the FastAPI web server serving Uvicorn bindings and host the HTML frontend dashboard on port `7860`:
```bash
python -m uvicorn api.routes:app --host 0.0.0.0 --port 7860 --reload
```
Once initialized, navigate your browser to `http://localhost:7860` to access the premium glassmorphism dashboard, displaying real-time debate flows, agent opinons, and pipeline traces.
