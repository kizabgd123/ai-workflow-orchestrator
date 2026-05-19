# Implementation Plan: AI Workflow Orchestrator - Refinement & Hardening

## Objective
Harden the existing AI Workflow Orchestrator codebase to meet production-grade standards. This includes improving agent reasoning, robustifying the debate consensus mechanism, enhancing memory-integrated lookups, and ensuring full execution auditability.

## Key Files & Context
- `orchestrator/engine.py`: Core 11-step pipeline.
- `debate/aggregator.py` & `debate/rounds.py`: Debate logic and consensus.
- `memory/database.py` & `memory/system.py`: SQLite-backed memory and similarity.
- `agents/`: Specialized agent implementations and base logic.
- `core/prompts.py` & `core/types.py`: System-wide prompts and data models.

## Implementation Steps

### Phase 1: Core & Agents Hardening
1. **Prompts Enhancement:** Centralize and refine prompts in `core/prompts.py`. Ensure role-specific mandates (e.g., Critic's hard adversarial focus) are explicit.
2. **BaseAgent Robustness:** Implement standard JSON output parsing and validation in `agents/base_agent.py`. Add retry logic for malformed LLM outputs.
3. **Identity Verification:** Ensure `core/identity.py` and `enforce_identity()` are rigorously applied at system entry.

### Phase 2: Advanced Debate & Aggregation
1. **Aggregator Upgrade:** Refactor `debate/aggregator.py` to:
    - Implement contradiction detection between `Solution` and `Critic`/`Security`.
    - Use historical agent accuracy (retrieved from `memory/database.py`) as a weighting factor.
    - Formalize decision thresholds (Consensus vs. Doubt vs. Deadlock).
2. **Debate rounds refinement:** Ensure `debate/rounds.py` correctly handles memory context injection and iterative refinement loops.

### Phase 3: Memory System & Similarity
1. **Memory Integration:** Update `memory/database.py` to store "Decision Artifacts" (full debate state + verified outcome).
2. **Similarity Lookup:** Enhance `get_similar_decisions` to use better weighting or multiple lookup strategies (initially keyword-dense LIKE, with structure for future vector extensions).
3. **Elo System:** Ensure Elo updates are correctly applied based on verified outcomes (Decision Artifacts).

### Phase 4: Orchestrator Pipeline & Audit
1. **11-Step Workflow Implementation:** Complete any missing logic in the 11-step sequence within `orchestrator/engine.py`.
2. **Execution Tracing:** Systematically integrate `log_execution_step` across all modules. Ensure every workflow has a unique `trace_id`.
3. **Self-Healing Logic:** Robustify `observability/self_heal_hook.py` to handle common failure patterns identified in the debate/memory loop.

## Verification & Testing
- **Unit Tests:** Add/Update tests for `DebateAggregator` (consensus logic) and `MemorySystem` (storage and retrieval).
- **Integration Test:** Run a full "End-to-End" workflow using a complex prompt (e.g., "deploy secure cluster") and verify the log output via `qa_monitor.py`.
- **Audit Verification:** Query `memory.db` after execution to ensure all traces, arguments, and consensus results are correctly persisted.

## Mandate 12 Checklist
- [ ] GOOGLE_API_KEY is verified and set.
- [ ] All participants have DEBATE and EXECUTION modes confirmed.
- [ ] No mocks used in final verification.
