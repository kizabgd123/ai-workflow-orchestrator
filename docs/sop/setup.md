---
title: "SOP-001: Instalacija & Setup Vodič"
description: "Vodič za konfigurisanje i prvo pokretanje sistema AI Workflow Orchestrator"
keywords: "installation guide, environment setup, python uvicorn, api rotation, key manager, mongodb setup"
robots: "index, follow"
---

# 🛠️ SOP-001: Instalacija & Setup Vodič

Ovaj operativni priručnik (Runbook) obezbeđuje sveobuhvatne korake za instalaciju zavisnosti, konfigurisanje modela, rotaciju API ključeva i bezbedno pokretanje **AI Workflow Orchestrator** sistema.

---

## 📋 1. Preduslovi i Sistemski Zahtevi

Sistem zahteva sledeće komponente instalirane na host mašini:
* **OS:** Linux (Ubuntu 20.04+ preporučeno) ili macOS.
* **Python verzija:** `3.10` ili novija (kompatibilno sa `3.11`).
* **Slobodan prostor:** Minimalno `500MB` slobodnog prostora za traces i SQLite bazu podataka.

---

## 💾 2. Kloniranje i Instalacija Zavisnosti

Pratite sledeće korake za preuzimanje repozitorijuma i instalaciju paketa:

1. **Klonirajte repozitorijum:**
   ```bash
   git clone https://github.com/kiza101288/ai-workflow-orchestrator.git
   cd ai-workflow-orchestrator
   ```

2. **Kreirajte i aktivirajte virtuelno okruženje:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalirajte Python pakete:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🔑 3. Podešavanje API Ključeva i Rotacija

Sistem koristi napredni **KeyManager** za upravljanje Gemini API ključevima. U slučaju prekoračenja limita (Rate Limit - HTTP 429), KeyManager automatski detektuje blokadu, privremeno uklanja neispravan ključ i rotira na sledeći dostupan ključ iz liste.

### Konfigurisanje ključeva preko Env varijabli:
Prosledite ključeve kao listu odvojenu zarezima u env promenljivoj `GOOGLE_API_KEY`:
```bash
export GOOGLE_API_KEY="AIzaSyA1...,AIzaSyA2...,AIzaSyA3..."
```
KeyManager u [key_manager.py](file:///home/kizabgd/.gemini/extensions/ai-workflow-orchestrator/core/key_manager.py) će automatski parsirati ove ključeve i rotirati ih po "round-robin" principu tokom rada agenata.

---

## ☁️ 4. Integracija MongoDB Atlas Memorije

Za dugoročno forenzičko pamćenje i vektorsku pretragu sličnih konflikata, orkestrator koristi MongoDB Atlas.

1. **Preuzmite MongoDB URI iz Atlas konzole** (obezbedite da je dozvoljena IP adresa kontejnera u Network Access sekciji).
2. **Postavite env varijablu:**
   ```bash
   export MONGODB_URI="mongodb+srv://<korisnik>:<lozinka>@cluster.mongodb.net/?retryWrites=true&w=majority"
   ```
3. **Podešavanje baze i kolekcija:** Naziv baze u kodu je definisan kao `ai_workflow_orchestrator`. Prilikom prve konekcije, MongoDBMemory klasa će automatski kreirati indekse na kolekcijama `debates`, `arguments` i `decision_history`.

*Ukoliko `MONGODB_URI` nije definisan ili mrežna konekcija ne uspe, sistem se bezbedno prebacuje na lokalnu SQLite bazu na putanji `storage/memory.db`.*

---

## 🔒 5. Zaobilaženje Identity Provere u Netipičnim Sredinama

Nulti-stepeni `IdentityGuard` u `core/identity.py` po defaultu zahteva da vrednost varijable `GOOGLE_CLOUD_PROJECT` bude `sixth-hawk-492717-m1` i `MONGODB_DATABASE` bude `ai_workflow_orchestrator`. 

Ako sistem pokrećete u lokalnom test okruženju ili na javnoj demonstraciji (npr. Hugging Face Spaces), identity provera će zaustaviti proces. Da biste je bezbedno zaobišli, postavite env flag:
```bash
export SKIP_IDENTITY_CHECK=true
```

---

## 🏃 6. Pokretanje Sistema

Sistem nudi dva načina pokretanja:

### A) Pokretanje preko CLI-ja (Komandna Linija)
Za izvršavanje pojedinačnog zahteva uz kompletnu adversarial debatu i ispis trace-a u terminalu:
```bash
python main.py "deploy a secure database cluster on GKE"
```

### B) Pokretanje API-ja i Web Dashboard-a
Za pokretanje FastAPI servera koji poslužuje Glassmorphism dashboard na portu `7860`:
```bash
python -m uvicorn api.routes:app --host 0.0.0.0 --port 7860 --reload
```
Nakon pokretanja, otvorite brauzer na `http://localhost:7860` kako biste pristupili premium dashboardu sa real-time vizuelizacijom debate i trace-ova.
