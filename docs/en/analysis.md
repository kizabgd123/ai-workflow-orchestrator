---
title: "Codebase Analysis & System Footprint"
description: "Technical audit of the repository, module dependency flow, and orchestration components"
keywords: "codebase analysis, folder structure, python dependency, code architecture"
robots: "index, follow"
---

# 📊 Codebase Analysis & System Footprint

This document provides a comprehensive architectural and structural audit of the **AI Workflow Orchestrator** repository.

The entire system is designed as a modular Python monorepo with strictly separated layers of responsibility, emphasizing zero-trust security and persistent execution auditability.

---

## 📂 Directory Structure (System Footprint)

The diagram below represents the repository's directory structure and the core purpose of each component:

```
ai-workflow-orchestrator/
├── main.py                    # CLI entry point (enforce_identity + WorkflowOrchestrator run)
├── requirements.txt           # External dependencies (FastAPI, google-genai, pymongo, sqlite3)
├── prd.md                     # Product Requirements Document
├── SUBMISSION.md              # Rapid Agent Hackathon Submission Package
│
├── core/                      # Shared core types and security utilities
│   ├── types.py               # Shared Enums: AgentRole, AgentMode, DebateOutcome, Argument
│   ├── identity.py            # IdentityGuard (Zero-trust verify for sixth-hawk-492717-m1)
│   └── key_manager.py         # KeyManager for API key rotation & failover
│
├── orchestrator/              # Central Orchestration Engine
│   ├── engine.py              # WorkflowOrchestrator (11-step execution pipeline)
│   └── router.py              # ModelRouter for Vertex AI / Gemini models (gemini-2.5-flash)
│
├── debate/                    # Multi-Agent Debate Arena (Adversarial Layer)
│   ├── rounds.py              # DebateManager (Round logic, Rule-of-3 refinement loops)
│   └── aggregator.py          # DebateAggregator (Consensus, conflict points, ELO updates)
│
├── agents/                    # Specialized agent entities
│   ├── base_agent.py          # BaseAgent (supports EXECUTION and DEBATE modes)
│   ├── factory.py             # AgentFactory (dynamic runtime instantiation)
│   └── [specialized].py       # Analyst, Solution, Critic, Security, Optimizer, Aggregator agents
│
├── memory/                    # Multi-tier memory layer (SQLite & MongoDB Atlas)
│   ├── database.py            # Database (SQLite perzistencija, decision history, ELO rankings)
│   └── mongodb_atlas.py       # MongoDB Atlas (Vector search conflicts & global trace logs)
│
├── execution/                 # Secure execution sandbox
│   ├── manager.py             # ExecutionManager (coordinated steps & reverse-rollback)
│   └── runner.py              # ExecutionRunner (sandboxed CLI / database command execution)
│
├── validation/                # Post-execution verification layer
│   └── checker.py             # ValidationChecker (assert outcome results & build verification reports)
│
├── security/                  # System hardening
│   └── token_budget.py        # TokenBudgetTracker & Middleware (100k token session circuit breaker)
│
├── observability/             # Monitoring and reliability
│   └── self_heal_hook.py      # Autonomously intercept & repair execution failures at system level
│
├── api/                       # FastAPI HTTP Server Layer
│   ├── routes.py              # Endpoint routing (triggering workflow, memory vector retrieval)
│   └── status_manager.py      # JobStatusManager (streaming real-time pipeline events via SSE)
│
├── dashboard/                 # Frontend User Interface
│   └── index.html             # Rich Glassmorphism Web Dashboard (Tailwind + CSS animations)
│
└── tests/                     # Verification test suite (PyTest)
    ├── test_agents.py         # Verification of LLM models generating valid agent outputs
    ├── test_elo.py            # Elo simulation and score updates during agent arguments
    └── test_circuit_breaker.py # Assert session termination on budget boundaries
```

---

## ⚙️ Core Modules and Dependencies

The orchestration pipeline strictly ensures unidirectional data transfers to prevent circular dependency problems:

| Module | Core Responsibility | Primary Dependencies |
|---|---|---|
| **`core.identity`** | Absolute zero-trust verification of current GCP/Mongo environments. | Independent (reads `os.environ` settings). |
| **`orchestrator.engine`** | Drives the 11-step pipeline from memory reload to audit logging. | `debate`, `execution`, `validation`, `memory`, `core.identity`. |
| **`debate.rounds`** | Coordinates structured adversarial arguments across multiple passes. | `agents.factory`, `debate.aggregator`, `memory.database`. |
| **`memory.database`** | SQLite storage for localized past decisions, traces, and reputation. | `core.types`, `sqlite3`. |
| **`memory.mongodb_atlas`** | High-performance vector retrieval and distributed cloud tracing. | `pymongo.MongoClient`. |
| **`execution.manager`** | Stepwise execution of approved proposals with automatic rollback logic. | `execution.runner`. |
| **`security.token_budget`** | Protects API limits by halting runaway agent debate cycles. | Singleton pattern shared across the pipeline session. |

---

## 🔒 Codebase Security Hardening

To ensure production-grade safety, the code complies with key security policies:
1. **No Token Runaways:** The `TokenBudgetTracker` monitors all Gemini API generate requests. If the current thread exceeds `100,000` tokens, further executions are immediately aborted.
2. **Execution Admission Controls:** Before executing shell operations or CLI commands, `ExecutionRunner` in [runner.py:30-56](file:///home/kizabgd/.gemini/extensions/ai-workflow-orchestrator/execution/runner.py#L30-L56) enforces structural checks that actively reject SQL Injections, hostPath volumes, Docker socket mounting, and unauthorized root logins.
3. **Determinstic Audits:** All transactions are logged using persistent `trace_id` mappings, permitting security teams to completely reconstruct any multi-agent debate history for inspection.
