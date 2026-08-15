# 🤖 AI Workflow Orchestrator

**Production-grade multi-agent orchestration with adversarial debate, dynamic reputation, and zero-trust guards.**

[![HF Space](https://img.shields.io/badge/🤗_Space-ai--workflow--orchestrator-ffd21e?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/kizabgd123/ai-workflow-orchestrator)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Why this exists

Most agent frameworks execute a single model's output blindly. This orchestrator treats every
non-trivial request as a **formal adversarial validation problem**: specialized agents debate the
solution, a weighted-consensus aggregator decides, and a zero-trust guard can veto the result
before anything executes. The goal is *deterministic, auditable* behavior from probabilistic models.

> Built for production AI teams that need governance, not demos.

---

## What it does

| Capability | Description |
|---|---|
| 🤝 **Multi-Agent Debate Engine** | Analyst → Solution → Critic → Security → Optimizer challenge and refine the plan before execution is permitted |
| ⚖️ **Dynamic Elo Reputation** | Agents earn/lose reputation (weight 0.5–1.5) from validated debate outcomes |
| 💾 **Forensic Memory** | SQLite + MongoDB Atlas; semantically retrieves past conflicts to learn from failures |
| 🛡️ **Zero-Trust Identity Guard** | Environment-level verification; halts on cross-project data contamination |
| ⚡ **Token Budget Circuit Breaker** | FastAPI middleware trips if a session exceeds 100k tokens |
| 🔄 **Autonomous Self-Healing** | On failure, Critic diagnoses, Solution builds a repaired plan, executes under re-validation |

---

## Architecture

```
User Request ─▶ Classification & Identity ─▶ Semantic Memory
                       │
                       ▼
            [ 🤝 MULTI-AGENT DEBATE ENGINE ]
   Analyst ─▶ Solution ─▶ Critic ─▶ Security ─▶ Optimizer
                       │
                       ▼
         [ ⚖️ CONSENSUS AGGREGATOR & ELO WEIGHTS ]
              PROCEED ───────┴────── REJECT/VETO
                 │                  │
                 ▼                  ▼
        [ 🏃 EXECUTOR RUNNER ]   [ 🛡️ SECURITY VETO ]
                 │
                 ▼
        [ 🧪 VALIDATION ] ─▶ [ 💾 MEMORY PERSIST ]
```

Full spec → [`docs/architecture.md`](docs/architecture.md) · [Live docs site](https://ai-workflow-orchestrator.pages.dev/en/)

---

## Quickstart

```bash
# Prerequisites: Python 3.10+, Google Gemini API key
export GOOGLE_API_KEY=your_key

git clone https://github.com/kizabgd123/ai-workflow-orchestrator.git
cd ai-workflow-orchestrator
pip install -r requirements.txt   # or: pip install -e .

# Run an orchestrated task
python main.py "deploy a secure database cluster on GKE"
```

> Configuration (model routing, token budgets) lives in `configs/`.

---

## Project layout

| Path | Responsibility |
|---|---|
| `agents/` | Specialized agent roles (analysis, solution, critic, security, optimizer, aggregator) |
| `debate/` | Debate manager & consensus aggregation |
| `core/` | Identity guard, key manager, logging, types |
| `api/` | FastAPI server + token-budget middleware |
| `dashboard/` | Observability UI |
| `docs/` | Architecture, data-flow, database, SOP, API specs |

---

## Related

- [`judge-guard-core`](https://github.com/kizabgd123/judge-guard-core) — commit-time JudgeGuard enforcement
- [HF Space demo](https://huggingface.co/spaces/kizabgd123/ai-workflow-orchestrator)

---

*Built with Security, Reliability, and Auditability as core mandates.*
