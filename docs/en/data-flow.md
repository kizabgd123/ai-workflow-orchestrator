---
title: "Data Flows & Sequence Diagrams"
description: "Technical overview of orchestrator transaction flows, debate turns, veto limits, and self-healing overrides"
keywords: "data flow, sequence diagram, debate sequence, veto trigger, self-healing flow, mermaid"
robots: "index, follow"
---

# 🔄 Data Flows & Sequence Diagrams

This document visualizes how request vectors, agent states, and evaluation variables flow across the **AI Workflow Orchestrator**.

Using formal Mermaid sequence flows, we break down three core operational patterns: Standard execution consensus, Security Veto intercepts, and Autonomous Self-Healing loops.

---

## 🟢 1. Standard Execution Flow (Consensus Proceed)

The sequence map below demonstrates a standard execution pipeline where the adversarial arena resolves with high consensus confidence and no security anomalies:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / CLI / API Endpoint
    participant Engine as WorkflowOrchestrator
    participant Memory as Memory Controller (SQLite/Mongo)
    participant Arena as DebateManager
    participant Agg as DebateAggregator
    participant Exec as ExecutionManager
    participant Val as ValidationChecker

    User->>Engine: Submit Request (e.g. "deploy secure web app")
    Engine->>Engine: Assert Workspace (IdentityGuard)
    Engine->>Memory: load_memory_context() & retrieve_similar_workflows()
    Memory-->>Engine: Historic traces and agent Elo rankings
    Engine->>Engine: build_initial_plan()
    
    Engine->>Arena: Trigger Arena (run_debate)
    Note over Arena: Phase 1-5: Turn-based confrontation
    Arena->>Arena: 1. Analyst: Decomposes requirements & maps threats
    Arena->>Arena: 2. Solution: Drafts technical proposal plan
    Arena->>Arena: 3. Critic: Audits proposal and challenges flaws
    Arena->>Arena: 4. Security: Asserts sandbox permissions & bounds
    Arena->>Arena: 5. Optimizer: Recommends design refinements
    Note over Arena: Multi-Pass Heuristics ("Rule of 3" refinements)
    Arena-->>Engine: Structured arguments with confidence scores
    
    Engine->>Agg: Compute Consensus (calculate_consensus)
    Note over Agg: Weighting role priority + Elo ratings
    Agg->>Agg: Run Critic vs Solution Elo Duel (adjust ELO)
    Agg-->>Engine: Outcome (PROCEED: Consensus Reached, ELO updates)
    
    Engine->>Exec: execute_plan(final_decision)
    Exec->>Exec: Run sandboxed tasks (assert Admission Policies)
    Exec-->>Engine: Execution Report (Success)
    
    Engine->>Val: validate_results(execution_report)
    Val-->>Engine: Validation Report (Valid)
    
    Engine->>Memory: store_all_in_memory(outcome, trace, ELO)
    Memory-->>Engine: Commit confirmation
    Engine-->>User: Success response + Session Trace ID
```

---

## 🔴 2. Security Veto Intercept (Security Veto Triggered)

If the Security agent identifies a critical runtime privilege violation (such as mounting `/var/run/docker.sock` or hostPath volumes) with a confidence score $\ge 0.9$, the debate is immediately halted, execution plans are discarded, and penalties are applied:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / CLI / API Endpoint
    participant Engine as WorkflowOrchestrator
    participant Arena as DebateManager
    participant Agg as DebateAggregator
    participant Memory as Memory Controller

    User->>Engine: Submit Request ("run container mounting docker.sock")
    Engine->>Arena: Trigger Arena (run_debate)
    Arena->>Arena: Solution Agent proposes Docker socket mount
    Arena->>Arena: Security Agent detects Privilege Escalation (Confidence 0.95!)
    Arena-->>Engine: Debate arguments
    
    Engine->>Agg: Compute Consensus (calculate_consensus)
    Note over Agg: Security confidence >= 0.9 forces immediate VETO
    Agg->>Agg: Penalty duel: Solution ELO -50 points
    Agg->>Agg: Reward: Security ELO +25 points
    Agg-->>Engine: Outcome (REJECTED: Critical security risk detected)
    
    Engine->>Memory: store_all_in_memory()
    Engine->>Engine: Audit Log Final Decision (trace_id)
    Engine-->>User: Error response: Access denied under GKE admission rules!
```

---

## 🟡 3. Autonomous Self-Healing Loop

If post-execution verification fails (e.g. system reports syntax issues or port blockages), the orchestrator intercepts the error and routes the state to the **Self-Healing Loop** to automatically patch the plan:

```mermaid
sequenceDiagram
    autonumber
    participant Engine as WorkflowOrchestrator
    participant Exec as ExecutionManager
    participant Val as ValidationChecker
    participant Heal as SelfHealHook
    participant Critic as Critic Agent
    participant Sol as Solution Agent

    Engine->>Exec: Execute Plan
    Exec-->>Engine: Execution failure (Error: Port 80 already in use)
    
    Engine->>Val: validate_results()
    Val-->>Engine: Validation Report (Invalid - failures detected)
    
    Note over Engine: Intercept validation failure!
    Engine->>Heal: attempt_self_healing(execution_report)
    Heal->>Critic: Diagnose Failure (think: "Explain port 80 fail")
    Critic-->>Heal: Diagnosis (Port 80 occupied, switch to port 8080)
    
    Heal->>Sol: Propose Repair Patch (think: "Generate repaired proposal")
    Sol-->>Heal: Repair Plan ("PROCEED: run command on port 8080")
    
    Heal->>Exec: Re-execute patch plan
    Exec-->>Heal: New execution report (Success)
    
    Heal->>Val: Re-validate results
    Val-->>Heal: Validation Report (Valid)
    Heal-->>Engine: Self-healing complete!
```
