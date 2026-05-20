---
title: "SOP-002: Dijagnostika & Otklanjanje Grešaka"
description: "Vodič za rješavanje tehničkih problema, otključavanje SQLite baza, token limite i ELO manipulacije"
keywords: "troubleshooting, database locked, token budget exceeded, rate limit, self-healing log, agent ELO reset"
robots: "index, follow"
---

# 🛠️ SOP-002: Dijagnostika & Otklanjanje Grešaka

Ovaj operativni priručnik (Runbook) sadrži standardne procedure za brzo dijagnostikovanje i otklanjanje problema u radu **AI Workflow Orchestrator** sistema.

---

## 🔒 1. Problem: SQLite Baza je Zaključana (Database is Locked)

Usled visoke konkurentnosti asinhronih agent poziva, može doći do SQLite greške `sqlite3.OperationalError: database is locked`.

### Koraci za rešavanje:
1. **Identifikujte procese** koji drže zaključan fajl:
   ```bash
   fuser storage/memory.db
   ```
2. **Zaustavite blokirajuće procese** (zamijenite `<PID>` stvarnim ID-jem procesa):
   ```bash
   kill -9 <PID>
   ```
3. **Omogućite WAL (Write-Ahead Logging) režim** za SQLite kako biste omogućili paralelno čitanje i pisanje bez zaključavanja:
   ```bash
   sqlite3 storage/memory.db "PRAGMA journal_mode=WAL;"
   ```
   WAL režim dramatično povećava performanse i otklanja rizik od zaključavanja tokom intenzivnih multi-agent debata.

---

## 🔌 2. Problem: Prekoračen Budžet Tokena (Token Budget Exceeded)

FastAPI Token Budget Middleware servira kao automatski prekidač. Ako ukupna LLM potrošnja pređe `100,000` tokena u sesiji, agenti odmah prekidaju rad sa greškom:
`ValueError: Agent aborted: Token budget exceeded.`

### Koraci za rešavanje:
1. **Resetujte sesijsku potrošnju** (ukoliko vršite ručne testove u terminalu) tako što ćete restartovati FastAPI server proces:
   ```bash
   kill -9 $(pgrep -f uvicorn)
   python -m uvicorn api.routes:app --host 0.0.0.0 --port 7860
   ```
2. **Povećajte maksimalni budžet** za kompleksne workflow-e izmenom parametra `LIMIT` u datoteci `security/token_budget.py` (npr. sa `100000` na `200000` tokena):
   ```python
   # Privremeni patch za hitne slučajeve
   self.max_input_tokens = 200000
   self.max_output_tokens = 50000
   ```

---

## 🔑 3. Problem: Greška pri Povezivanju sa Modelom (HTTP 429 / 401)

Greške `429 Too Many Requests` ili `401 Unauthorized` ukazuju na probleme sa API ključevima.

### Koraci za rešavanje:
1. **Proverite važenje ključeva** pokretanjem proste Python test skripte:
   ```python
   import os
   from google import genai
   client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
   response = client.models.generate_content(model="gemini-2.5-flash", contents="Hi")
   print(response.text)
   ```
2. Ako skripta vrati grešku, zamenite blokirane ključeve u env listi.
3. **KeyManager automatski detektuje 429 grešku** i isključuje ključ na 60 sekundi. Ukoliko su svi ključevi potrošeni, sistem će stati sa radom. U tom slučaju, dodajte nove ključeve u listu:
   ```bash
   export GOOGLE_API_KEY="novi_kljuc_1,novi_kljuc_2"
   ```

---

## 🔄 4. Pregled Logova Samoisceljenja (Self-Healing Traces)

Ukoliko validation check ne uspe, orkestrator aktivira automatski self-healing proces. Kompletan tok popravke je auditabilan i čuva se u JSON formatu pod jedinstvenim trace_id-jem.

### Gde se nalaze logovi:
Svi audit tragovi i logovi se čuvaju u:
`storage/traces/<trace_id>.json`

### Kako analizirati log kvara:
Otvorite najnoviji trace fajl da biste videli dijagnozu Critic agenta i hotfix plan Solution agenta:
```bash
cat $(ls -t storage/traces/*.json | head -n 1) | jq .
```
Potražite ključ `"self_healing"` unutar JSON objekta koji sadrži polja:
* `"critic_diagnosis"`: Objašnjenje zašto je komanda propala.
* `"solution_patch"`: Popravljeni plan koji je ponovo pokrenut.
* `"healed_successfully"`: Boolean status uspešnosti popravke.

---

## ⚖️ 5. Ručno Podešavanje ELO Rejtinga Agenata

Ponekad je za potrebe testiranja ili kalibracije debate potrebno ručno resetovati ili izmeniti ELO rejting nekog agenta.

### Resetovanje svih ELO rejtinga na podrazumevanih 1200:
Pokrenite sledeću sqlite3 naredbu u terminalu:
```bash
sqlite3 storage/memory.db "UPDATE agent_elo SET elo = 1200.0, matches = 0;"
```

### Ručna promena rejtinga određenog agenta (npr. povećanje Security agenta na 1400):
```bash
sqlite3 storage/memory.db "UPDATE agent_elo SET elo = 1400.0 WHERE agent_id = 'agent_security';"
```
*Ova promena će odmah povećati ulogu i uticaj glasa Security agenta u debatnoj areni.*
