---
title: "SOP-002: Diagnostics & Troubleshooting Guide"
description: "SOP guide for resolving database locks, budget trips, API rate limits, and ELO rating calibrations"
keywords: "troubleshooting, database locked, token budget exceeded, rate limit, self-healing log, agent ELO reset"
robots: "index, follow"
---

# 🛠️ SOP-002: Diagnostics & Troubleshooting Guide

This Standard Operating Procedure (SOP) runbook provides step-by-step diagnostic paths to resolve common system anomalies inside the **AI Workflow Orchestrator**.

---

## 🔒 1. Issue: SQLite File Lockups (Database is Locked)

Due to concurrent async execution blocks during agent debate rounds, SQLite may occasionally report file access errors: `sqlite3.OperationalError: database is locked`.

### Recovery Steps:
1. **Identify active processes** locking the database file:
   ```bash
   fuser storage/memory.db
   ```
2. **Halt blocking processes** (replace `<PID>` with the actual process ID):
   ```bash
   kill -9 <PID>
   ```
3. **Enable Write-Ahead Logging (WAL)** to allow simultaneous read/write cycles without locks:
   ```bash
   sqlite3 storage/memory.db "PRAGMA journal_mode=WAL;"
   ```
   WAL mode resolves concurrent access block issues during intense debate iterations.

---

## 🔌 2. Issue: Token Budget Trips (Token Budget Exceeded)

The FastAPI Token Budget Middleware triggers a runtime circuit breaker. If aggregate API consumption crosses `100,000` tokens during a session, all active tasks are terminated:
`ValueError: Agent aborted: Token budget exceeded.`

### Recovery Steps:
1. **Reset Session Budgets** by restarting the Uvicorn web server process:
   ```bash
   kill -9 $(pgrep -f uvicorn)
   python -m uvicorn api.routes:app --host 0.0.0.0 --port 7860
   ```
2. **Increase Budget Thresholds** inside the `security/token_budget.py` configuration file (e.g. updating limits from `100000` to `200000` tokens):
   ```python
   # Temporary configuration adjustment for complex operations
   self.max_input_tokens = 200000
   self.max_output_tokens = 50000
   ```

---

## 🔑 3. Issue: Model Connection Errors (HTTP 429 / 401)

Errors such as `429 Too Many Requests` or `401 Unauthorized` indicate issues with LLM API credentials.

### Recovery Steps:
1. **Verify credential validity** by running a basic python connection test:
   ```python
   import os
   from google import genai
   client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
   response = client.models.generate_content(model="gemini-2.5-flash", contents="Hi")
   print(response.text)
   ```
2. If the test script fails, update the active key strings in your env parameters.
3. The **KeyManager automatically intercepts 429 exceptions** and blocks the failing key for 60 seconds. If all configured keys are blocked, execution will stop. In this scenario, inject fresh API keys:
   ```bash
   export GOOGLE_API_KEY="new_key_1,new_key_2"
   ```

---

## 🔄 4. Auditing Self-Healing Traces

If a task execution verification fails, the orchestrator triggers automated recovery. The complete diagnostics and repair flow is captured inside JSON trace objects.

### File Locations:
All traces are written to the local storage:
`storage/traces/<trace_id>.json`

### Reading Self-Healing Diagnostics:
Read the newest trace file using `jq` to inspect Critic recommendations and Solution repairs:
```bash
cat $(ls -t storage/traces/*.json | head -n 1) | jq .
```
Verify the `"self_healing"` nested parameters within the JSON object:
* `"critic_diagnosis"`: Explanation of what caused the command execution failure.
* `"solution_patch"`: Repaired execution commands routed back to the sandboxed runner.
* `"healed_successfully"`: Boolean value indicating recovery success.

---

## ⚖️ 5. Manual Calibration of Agent ELO Ratings

For QA testing or debate tuning, administrators may manually alter or reset agent ELO reputation coefficients.

### Resetting all agent ratings to the default 1200:
Execute the following SQLite command in your terminal:
```bash
sqlite3 storage/memory.db "UPDATE agent_elo SET elo = 1200.0, matches = 0;"
```

### Boosting specific agent ratings (e.g. promoting the Security agent to 1400 ELO):
```bash
sqlite3 storage/memory.db "UPDATE agent_elo SET elo = 1400.0 WHERE agent_id = 'agent_security';"
```
*Altering Elo ratings immediately increases the agent's voting multiplier in consensus calculations.*
