---
title: "Procesi Orkestracije i Stanja"
description: "Tehnički pregled stanja sistema, prelaza i logike donošenja odluka"
keywords: "state machine, workflow steps, system state, state transition, decision logic"
robots: "index, follow"
---

# 🔄 Procesi Orkestracije i Stanja

Rad orkestratora je modelovan kao **konačni automat (Finite State Machine - FSM)** sa precizno definisanim stanjima i prelazima. Ovaj dokument objašnjava svaku promenu stanja i logiku donošenja odluka u sistemu.

---

## 🗺️ Dijagram Stanja Sistema (System State Machine)

Sledeći dijagram prikazuje stanja kroz koja sistem prolazi od prihvatanja zahteva do čuvanja audita u memoriju:

```mermaid
stateDiagram-v2
    [*] --> Idle : Pokretanje
    
    state Idle {
        [*] --> VerifyingIdentity : Primljen Zahtev
        VerifyingIdentity --> IdentityVerified : Uspeh (GCP + Mongo)
        VerifyingIdentity --> [*] : Greška (Prekid rada)
    }

    Idle --> LoadingContext : Učitaj dugoročnu memoriju
    LoadingContext --> Classifying : Klasifikacija & Pretraga sličnosti
    Classifying --> Planning : build_initial_plan()
    
    state Arena_Debate {
        Planning --> Round_1_Analyst : Pokreni run_debate()
        Round_1_Analyst --> Round_2_Solution
        Round_2_Solution --> Round_3_Critic
        Round_3_Critic --> Round_4_Security
        Round_4_Security --> Round_5_Optimizer
        Round_5_Optimizer --> Multi_Pass_Check : Evaluacija konfidencije
        Multi_Pass_Check --> Round_2_Solution : Ponavljanje ("Rule of 3" ako je < 0.8)
        Multi_Pass_Check --> Aggregating : Konfidencija OK / Limit popunjen
    }
    
    state Aggregation_Engine {
        Aggregating --> CalculatingConsensus
        CalculatingConsensus --> ELODuels : Izračunaj težine & ELO
        ELODuels --> ResolvingDecision
    }

    ResolvingDecision --> SandboxedExecution : PROCEED (Konsenzus)
    ResolvingDecision --> Blocked : REJECT / VETO (Sigurnosni rizik)
    
    state SandboxedExecution {
        [*] --> RunningTasks : execute_plan()
        RunningTasks --> ValidationCheck : Izveštaj gotov
        
        state ValidationCheck {
            [*] --> AssertingOutcomes
            AssertingOutcomes --> Success : Sve komande prošle
            AssertingOutcomes --> Failure : Detektovana greška
        }

        Failure --> SelfHealingActive : Pokreni Self-Healing
        SelfHealingActive --> RunningTasks : Hotfix Plan spreman
        SelfHealingActive --> RollbackActive : Greška se ne može popraviti
        RollbackActive --> [*] : Rollback izvršen
    }

    Success --> StoringMemory : store_all_in_memory()
    Blocked --> StoringMemory
    StoringMemory --> Auditing : audit_log()
    Auditing --> [*] : Gotovo (Vrati rezultat)
```

---

## 📊 Tabela Tranzicija Stanja (State Transition Table)

| Početno Stanje | Događaj / Uslov | Sledeće Stanje | Opis |
|---|---|---|---|
| **`Idle`** | Korisnik šalje zahtev | **`VerifyingIdentity`** | Pokreće se nulta provera `IdentityGuard`-a. |
| **`VerifyingIdentity`** | Neuspeh u GCP projektu | **`Aborted`** | Sigurnosni prekid rada (sys.exit). |
| **`Planning`** | Plan spreman | **`Round_1_Analyst`** | Pokreće se prva runda adversarial debate. |
| **`Multi_Pass_Check`** | Konfidencija $< 0.8$ i krug $< 3$ | **`Round_2_Solution`** | Solution agent dobija primedbe i prepravlja plan. |
| **`ResolvingDecision`** | Security konfidencija $\ge 0.9$ | **`Blocked`** | **VETO!** Plan se odbija bez prava na izvršenje. |
| **`ValidationCheck`** | Bilo koja komanda vrati exit code $\ne 0$ | **`SelfHealingActive`** | Pokreće se asinhrono samoisceljenje. |
| **`SelfHealingActive`** | Critic ne može dijagnostikovati kvar | **`RollbackActive`** | Pokreće se obrnuta rollback sekvenca. |
| **`Success`** | Svi testovi prošli | **`StoringMemory`** | Ishod se trajno upisuje u SQLite i MongoDB Atlas. |

---

## ⚖️ Pravila Tranzicije za Konsenzus i Veto

Prilikom prelaska iz stanja **`ResolvingDecision`** u izvršenje, agregator primenjuje sledeće tranzicione formule:

1. **Tranzicija u `Blocked` (REJECT):**
   * Ako Security Agent ima konfidenciju $\ge 0.9$ (npr. detektovana SQL Injection string interpolacija).
   * Ako je ukupna težinski-prosečna konfidencija debata $< 0.6$ nakon svih rundi rafinisanja.
2. **Tranzicija u `SandboxedExecution` (PROCEED):**
   * Ako je ukupna konfidencija $\ge 0.6$ i nema aktivnih sigurnosnih pretnji.
