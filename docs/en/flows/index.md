---
title: "Orchestration & State Transitions"
description: "Technical specification of orchestrator states, transition tables, and decision gates"
keywords: "state machine, workflow steps, system state, state transition, decision logic"
robots: "index, follow"
---

# 🔄 Orchestration & State Transitions

The runtime cycle of the orchestrator is formally modeled as a **Finite State Machine (FSM)** with strictly defined states and transition triggers. This document explains each state shift and evaluation gate inside the system.

---

## 🗺️ System State Machine Diagram

The diagram below maps the FSM states traversed from request submission to memory audit logging:

```mermaid
stateDiagram-v2
    [*] --> Idle : System Initialization
    
    state Idle {
        [*] --> VerifyingIdentity : Request Submitted
        VerifyingIdentity --> IdentityVerified : Success (GCP & MongoDB locks match)
        VerifyingIdentity --> [*] : Identity Mismatch (Halt)
    }

    Idle --> LoadingContext : Reload past ELO and traces
    LoadingContext --> Classifying : Tagging & Cosine similarity lookups
    Classifying --> Planning : build_initial_plan()
    
    state Arena_Debate {
        Planning --> Round_1_Analyst : Trigger run_debate()
        Round_1_Analyst --> Round_2_Solution
        Round_2_Solution --> Round_3_Critic
        Round_3_Critic --> Round_4_Security
        Round_4_Security --> Round_5_Optimizer
        Round_5_Optimizer --> Multi_Pass_Check : Evaluate consensus confidence
        Multi_Pass_Check --> Round_2_Solution : Re-debate (Rule-of-3 if confidence < 0.8)
        Multi_Pass_Check --> Aggregating : Confidence threshold met / turn limit hit
    }
    
    state Aggregation_Engine {
        Aggregating --> CalculatingConsensus
        CalculatingConsensus --> ELODuels : Resolve Weights & duels
        ELODuels --> ResolvingDecision
    }

    ResolvingDecision --> SandboxedExecution : PROCEED (Consensus reached)
    ResolvingDecision --> Blocked : REJECT / VETO (Security anomaly found)
    
    state SandboxedExecution {
        [*] --> RunningTasks : execute_plan()
        RunningTasks --> ValidationCheck : Build execution report
        
        state ValidationCheck {
            [*] --> AssertingOutcomes
            AssertingOutcomes --> Success : All tasks returned success
            AssertingOutcomes --> Failure : Task returned error
        }

        Failure --> SelfHealingActive : Trigger Self-Healing
        SelfHealingActive --> RunningTasks : Repaired plan loaded
        SelfHealingActive --> RollbackActive : Repair aborted / failed
        RollbackActive --> [*] : Rollback complete
    }

    Success --> StoringMemory : store_all_in_memory()
    Blocked --> StoringMemory
    StoringMemory --> Auditing : audit_log()
    Auditing --> [*] : Output results & trace_id
```

---

## 📊 State Transition Specifications

| Initial State | Event / Triggering Condition | Next State | Functional Description |
|---|---|---|---|
| **`Idle`** | Request submitted by Client | **`VerifyingIdentity`** | Initiates zero-trust checking inside `IdentityGuard`. |
| **`VerifyingIdentity`** | Workspace variables mismatch | **`Aborted`** | Halts execution immediately (`sys.exit(1)`). |
| **`Planning`** | Baseline plan drafted | **`Round_1_Analyst`** | Commences turn-based adversarial debate rounds. |
| **`Multi_Pass_Check`** | Consensus $< 0.8$ and turns $< 3$ | **`Round_2_Solution`** | Solution agent receives Critic reviews and refines plan. |
| **`ResolvingDecision`** | Security confidence $\ge 0.9$ | **`Blocked`** | **VETO!** Immediate rejection of unsafe operations. |
| **`ValidationCheck`** | Task returns exit code $\ne 0$ | **`SelfHealingActive`** | Activates the autonomous self-healing diagnostics. |
| **`SelfHealingActive`** | Critic fails to diagnose failure | **`RollbackActive`** | Runs reverse-rollback operations. |
| **`Success`** | All validations passed | **`StoringMemory`** | Commits outputs to local SQLite and cloud Atlas collections. |

---

## ⚖️ Decision Rules for Proceed and Veto Transitions

When transitioning from **`ResolvingDecision`** to execution runs, the consensus engine validates the following criteria:

1. **Transition to `Blocked` (REJECT):**
   * If the Security Agent flags the plan with a confidence score $\ge 0.9$ (e.g. static regex flags SQL Injection attempts).
   * If the aggregate weighted consensus confidence score remains $< 0.6$ after all refinement passes are exhausted.
2. **Transition to `SandboxedExecution` (PROCEED):**
   * If the aggregate consensus confidence is $\ge 0.6$ and no active security block is triggered.
