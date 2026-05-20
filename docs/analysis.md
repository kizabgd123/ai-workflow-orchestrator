---
title: "Analiza Koda & Otisak Sistema"
description: "Tehnički pregled repozitorijuma, modulskih zavisnosti i orkestracione strukture"
keywords: "codebase analysis, folder structure, python dependency, code architecture"
robots: "index, follow"
---

# 📊 Analiza Koda & Otisak Sistema

Dokumentacija sprovodi detaljan arhitektonski i strukturni pregled koda projekta **AI Workflow Orchestrator**. 

Ceo sistem je projektovan kao Python monolitski repozitorijum sa modularno razdvojenim slojevima odgovornosti, prateći nulto-poverenje (Zero-Trust) i visoku auditabilnost.

---

## 📂 Struktura Direktorijuma (System Footprint)

Sledeći dijagram prikazuje kompletnu strukturu direktorijuma repozitorijuma i svrhu svakog od modula:

```
ai-workflow-orchestrator/
├── main.py                    # CLI ulazna tačka sistema (enforce_identity + WorkflowOrchestrator)
├── requirements.txt           # Definicije spoljnih biblioteka (FastAPI, google-genai, pymongo, sqlite3)
├── prd.md                     # Definicija zahteva proizvoda (Product Requirements Document)
├── SUBMISSION.md              # Zvanični dokument za Rapid Agent Hackathon predaju
│
├── core/                      # Osnovne deljene definicije i sigurnosni slojevi
│   ├── types.py               # Enumi za AgentRole, AgentMode, DebateOutcome, Argument
│   ├── identity.py            # IdentityGuard (Zero-trust provera za sixth-hawk-492717-m1)
│   └── key_manager.py         # KeyManager za rotiranje i upravljanje API ključevima
│
├── orchestrator/              # Glavni orkestracioni mozak
│   ├── engine.py              # WorkflowOrchestrator (11-stepeni orkestracioni pipeline)
│   └── router.py              # ModelRouter za Vertex AI / Gemini modele (gemini-2.5-flash)
│
├── debate/                    # Mašina za multi-agent debatu (Adversarial Layer)
│   ├── rounds.py              # DebateManager (Upravljanje rundama i "Rule of 3" rafinacijom)
│   └── aggregator.py          # DebateAggregator (Izračunavanje konsenzusa, konflikata i ELO ratinga)
│
├── agents/                    # Specijalizovane agent agenture
│   ├── base_agent.py          # BaseAgent sa podrškom za EXECUTION i DEBATE režime rada
│   ├── factory.py             # AgentFactory (Dinamičko kreiranje instanci agenata)
│   └── [specialized].py       # Analyst, Solution, Critic, Security, Optimizer, Aggregator agenti
│
├── memory/                    # Dugoročno i kratkoročno pamćenje (Memory Layer)
│   ├── database.py            # Database (SQLite perzistencija, istorija odluka, ELO tabela)
│   └── mongodb_atlas.py       # MongoDB Atlas integracija (Vektorska pretraga i agregacija e-reputacije)
│
├── execution/                 # Modul za bezbedno izvršenje planova
│   ├── manager.py             # ExecutionManager (Koordinacija izvršenja i Rollback sekvenca)
│   └── runner.py              # ExecutionRunner (Pokretanje CLI/SQL operacija uz sandboxing)
│
├── validation/                # Provera rezultata nakon izvršenja
│   └── checker.py             # ValidationChecker (Verifikacija ispravnosti i formiranje izveštaja)
│
├── security/                  # Dodatni sigurnosni mehanizmi
│   └── token_budget.py        # TokenBudgetTracker i TokenBudgetMiddleware (Circuit Breaker na 100k tokena)
│
├── observability/             # Nadgledanje i samoisceljenje
│   └── self_heal_hook.py      # Autonomni mehanizam za popravku neuspelih operacija na nivou OS
│
├── api/                       # FastAPI Web Interfejs
│   ├── routes.py              # HTTP rute za pokretanje workflow-a i pretragu memorije
│   └── status_manager.py      # JobStatusManager za real-time strimovanje stanja preko SSE
│
├── dashboard/                 # Frontend Web Kontrolna Tabla
│   └── index.html             # Premium Glassmorphism UI (Tailwind + CSS mikro-animacije)
│
└── tests/                     # Testni paket (PyTest)
    ├── test_agents.py         # Verifikacija model generisanja i ponašanja agenata
    ├── test_elo.py            # Simulacija ELO promena tokom debata
    └── test_circuit_breaker.py # Provera okidanja token barijere
```

---

## ⚙️ Analiza Glavnih Modula i Zavisnosti

Sistem se oslanja na čist prenos stanja između modula bez cikličnih zavisnosti:

| Modul | Primarna Odgovornost | Ključne Zavisnosti |
|---|---|---|
| **`core.identity`** | Sigurnosna nulta verifikacija pre bilo koje operacije. | Bez spoljnih zavisnosti (čita `os.environ`). |
| **`orchestrator.engine`** | Upravlja 11-stepenim tokom izvršenja od učitavanja memorije do audita. | `debate`, `execution`, `validation`, `memory`, `core.identity`. |
| **`debate.rounds`** | Vodi strukturisanu konfrontaciju argumenata u rundama. | `agents.factory`, `debate.aggregator`, `memory.database`. |
| **`memory.database`** | SQLite perzistencija odluka i istorijskog konteksta. | `core.types`, `sqlite3`. |
| **`memory.mongodb_atlas`** | Vektorska pretraga konflikata i globalni audit. | `pymongo.MongoClient`. |
| **`execution.manager`** | Izvršava odobreni plan i po potrebi radi **Rollback** unazad. | `execution.runner`. |
| **`security.token_budget`** | Sprečava beskonačne LLM petlje i finansijsko probijanje. | Singleton obrazac za celokupnu sesiju. |

---

## 🔒 Sigurnosni Standardi Koda

Primenjeni su strogi sigurnosni principi:
1. **Nema curenja tokena:** `TokenBudgetTracker` sprečava sesije sa više od `100,000` tokena. Svaki poziv ka `aio.models.generate_content` se registruje i odbija ukoliko je budžet prekoračen.
2. **Admission Control:** `ExecutionRunner` u [runner.py:30-56](file:///home/kizabgd/.gemini/extensions/ai-workflow-orchestrator/execution/runner.py#L30-L56) skenira komande i blokira priviligovane kubernetes kontejnere, SQL injekcije i montiranje docker sock-a na nivou statičke analize pre izvršenja naredbe.
3. **Auditabilni Reasoning Chain:** Svaki korak je povezan sa `trace_id` (UUIDv4) i memorijski je perzistentan, omogućavajući 100% determinističku rekonstrukciju debate.
