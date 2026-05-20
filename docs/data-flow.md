---
title: "Tokovi Podataka & Sekvencijalni Dijagrami"
description: "Tehnički pregled protoka informacija kroz orkestrator, faze debata, veto sisteme i samoisceljenje"
keywords: "data flow, sequence diagram, debate sequence, veto trigger, self-healing flow, mermaid"
robots: "index, follow"
---

# 🔄 Tokovi Podataka & Sekvencijalni Dijagrami

Ovaj priručnik detaljno prikazuje kako podaci i kontrolni tokovi cirkulišu kroz **AI Workflow Orchestrator**. 

Kroz sekvencijalne dijagrame, dokument objašnjava tri ključna scenarija: standardno izvršenje sa debatom, sigurnosni veto i asinhrono samoisceljenje (Self-Healing) u slučaju kvara.

---

## 🟢 1. Standardni Orkestracioni Tok (Consensus Proceed)

Sledeći sekvencijalni dijagram prikazuje standardni krug rada kada agenti postignu visok stepen poverenja i konsenzus bez bezbednosnih alarma:

```mermaid
sequenceDiagram
    autonumber
    actor Korisnik as Korisnik / CLI / API
    participant Engine as WorkflowOrchestrator
    participant Memory as Memory Controller (SQLite/Mongo)
    participant Arena as DebateManager
    participant Agg as DebateAggregator
    participant Exec as ExecutionManager
    participant Val as ValidationChecker

    Korisnik->>Engine: Pošalji Zahtev (npr. "deploy secure web app")
    Engine->>Engine: Verifikuj Identitet (IdentityGuard)
    Engine->>Memory: load_memory_context() & retrieve_similar_workflows()
    Memory-->>Engine: Istorijski trace-ovi i ELO rating agenata
    Engine->>Engine: build_initial_plan()
    
    Engine->>Arena: Pokreni Debatu (run_debate)
    Note over Arena: Faza 1-5: Sukobljavanje Agencija
    Arena->>Arena: 1. Analyst: Razlaže zahtev i pretnje
    Arena->>Arena: 2. Solution: Predlaže plan izvršenja
    Arena->>Arena: 3. Critic: Napada plan i traži greške
    Arena->>Arena: 4. Security: Proverava privilegije i portove
    Arena->>Arena: 5. Optimizer: Nudi efikasnije alternative
    Note over Arena: Multi-Pass Heuristics ("Rule of 3" rafinacija)
    Arena-->>Engine: Lista argumenata sa konfidencijom
    
    Engine->>Agg: Izračunaj Konsenzus (calculate_consensus)
    Note over Agg: Ponderisanje preko uloga + ELO ocena
    Agg->>Agg: Duel Critic vs Solution (ažuriraj ELO)
    Agg-->>Engine: Outcome (PROCEED: Consensus Reached, ELO updates)
    
    Engine->>Exec: execute_plan(final_decision)
    Exec->>Exec: Sandboxed izvršenje komandi (GKE Admission checks)
    Exec-->>Engine: Izveštaj o izvršenju (Success)
    
    Engine->>Val: validate_results(execution_report)
    Val-->>Engine: Validation Report (Valid)
    
    Engine->>Memory: store_all_in_memory(outcome, trace, ELO)
    Memory-->>Engine: Potvrda upisa
    Engine-->>Korisnik: Uspešan Rezultat + Trace ID
```

---

## 🔴 2. Sigurnosni Veto (Security Veto Triggered)

Ukoliko Security agent prepozna ozbiljan rizik (npr. montiranje `/var/run/docker.sock` ili privilegovani `hostPath` u Kubernetes pod-u) sa konfidencijom $\ge 0.9$, debata se odmah prekida, plan odbija i sprovode se kaznene mere:

```mermaid
sequenceDiagram
    autonumber
    actor Korisnik as Korisnik / CLI / API
    participant Engine as WorkflowOrchestrator
    participant Arena as DebateManager
    participant Agg as DebateAggregator
    participant Memory as Memory Controller

    Korisnik->>Engine: Pošalji Zahtev ("run container mounting docker.sock")
    Engine->>Arena: Pokreni Debatu (run_debate)
    Arena->>Arena: Solution Agent predlaže montiranje sock fajla
    Arena->>Arena: Security Agent detektuje Privilege Escalation (Confidence 0.95!)
    Arena-->>Engine: Lista argumenata
    
    Engine->>Agg: Izračunaj Konsenzus (calculate_consensus)
    Note over Agg: Security konfidencija >= 0.9 pokreće VETO
    Agg->>Agg: Kazneni duel: Solution ELO -50 bodova
    Agg->>Agg: Nagrada: Security ELO +25 bodova
    Agg-->>Engine: Outcome (REJECTED: Critical security risk detected)
    
    Engine->>Memory: store_all_in_memory()
    Engine->>Engine: Audit Log Final Decision (trace_id)
    Engine-->>Korisnik: Greška: Odbijeno iz bezbednosnih razloga!
```

---

## 🟡 3. Asinhrono Samoisceljenje (Self-Healing Loop)

Ukoliko validation check ne uspe nakon izvršenja komande (npr. greška u portu ili sintaksi), orkestrator aktivira **Self-Healing Loop** za automatsko rešavanje problema:

```mermaid
sequenceDiagram
    autonumber
    participant Engine as WorkflowOrchestrator
    participant Exec as ExecutionManager
    participant Val as ValidationChecker
    participant Heal as SelfHealHook
    participant Critic as Critic Agent
    participant Sol as Solution Agent

    Engine->>Exec: Izvrši plan
    Exec-->>Engine: Izveštaj sa greškom (Error: Port 80 already in use)
    
    Engine->>Val: validate_results()
    Val-->>Engine: Validation Report (Invalid - failures detected)
    
    Note over Engine: Aktivacija samoisceljenja!
    Engine->>Heal: attempt_self_healing(execution_report)
    Heal->>Critic: Dijagnostikuj kvar (think: "Zašto port 80 ne radi?")
    Critic-->>Heal: Objašnjenje (Port 80 je zauzet, promeniti na 8080)
    
    Heal->>Sol: Predloži patch (think: "Kako popraviti port?")
    Sol-->>Heal: Generisani hotfix plan ("PROCEED: run command on port 8080")
    
    Heal->>Exec: Re-execute patch plan
    Exec-->>Heal: Izveštaj o novom izvršenju (Success)
    
    Heal->>Val: Re-validate results
    Val-->>Heal: Validation Report (Valid)
    Heal-->>Engine: Samoisceljenje uspešno!
```
