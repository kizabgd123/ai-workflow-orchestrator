---
title: "Implementacija & Deployment"
description: "Tehničke instrukcije za kontejnerizaciju, deployment na Google Cloud Run / GKE i podešavanje Hugging Face Spaces"
keywords: "dockerfile, deployment, cloud run, gke container, uvicorn port, environment setup"
robots: "index, follow"
---

# 🚀 Implementacija & Deployment

Sistem **AI Workflow Orchestrator** je projektovan da bude potpuno prenosiv i bezbedan za izvršavanje unutar kontejnerizovanih okruženja. 

Ovaj priručnik pruža instrukcije za Docker pakovanje, postavljanje na **Google Cloud Run** i **Kubernetes (GKE)**, kao i specifične konfiguracije za hosting na **Hugging Face Spaces**.

---

## 📦 Kontejnerizacija: Dockerfile

Za pakovanje aplikacije koristi se optimizovan, višefazni (multi-stage) Dockerfile zasnovan na zvaničnoj Python slim slici radi minimizacije napadačke površine.

```dockerfile
# 1. FAZA: Izgradnja i instalacija zavisnosti
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 2. FAZA: Pokretanje u laganom okruženju
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Kopiranje instaliranih paketa iz builder faze
COPY --from=builder /root/.local /root/.local
COPY . .

# Kreiranje foldera za perzistentnu lokalnu memoriju i logove
RUN mkdir -p storage/traces

# Pokretanje aplikacije preko Uvicorn servera na portu 7860 (HF Spaces kompatibilno)
EXPOSE 7860

CMD ["python", "-m", "uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## ☁️ Deployment na Google Cloud Platform (GCP)

Sistem je u potpunosti kompatibilan sa GCP servisima pod nultim bezbednosnim modelom.

### 1. Cloud Run Deployment
Google Cloud Run je idealan izbor za hostovanje FastAPI sloja orkestratora zbog automatskog skaliranja i podrške za asinhroni prenos.

* **Naredba za izgradnju slike (gcloud):**
  ```bash
  gcloud builds submit --tag gcr.io/sixth-hawk-492717-m1/ai-workflow-orchestrator:latest
  ```
* **Naredba za deployment na Cloud Run:**
  ```bash
  gcloud run deploy ai-workflow-orchestrator \
      --image gcr.io/sixth-hawk-492717-m1/ai-workflow-orchestrator:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars="GOOGLE_CLOUD_PROJECT=sixth-hawk-492717-m1,MONGODB_DATABASE=ai_workflow_orchestrator" \
      --update-secrets="GOOGLE_API_KEY=gemini-api-key:latest,MONGODB_URI=mongodb-connection-string:latest"
  ```

> [!IMPORTANT]
> Obavezno je proslediti env varijable `GOOGLE_CLOUD_PROJECT` i `MONGODB_DATABASE` kako bi nulti-stepeni `IdentityGuard` uspešno verifikovao pokretanje kontejnera u produkciji.

### 2. GKE Admission Control Policies
Prilikom deploymenta na GKE, admission kontroleri blokiraju nebezbedna izvršenja koja orkestrator može pokušati. Konkretno:
* **HostPath blokada:** Zabranjeno je montiranje host direktorijuma u pod-ove radi sprečavanja bega iz sandbox-a.
* **Privileged pods:** Pod-ovi se moraju pokretati pod ne-privilegovanim korisnikom (`runAsNonRoot: true`).

---

## 🤗 Hosting na Hugging Face Spaces (HF Spaces)

Hugging Face Spaces pruža odlično okruženje za javne demonstracije FastAPI servera sa frontend Glassmorphism kontrolnom tablom.

### Specifične Konfiguracije:
1. **Port binding:** HF Spaces zahteva da kontejner sluša isključivo na portu `7860`.
2. **CORS zaobilaznica:** API kontroleri moraju eksplicitno dozvoliti `huggingface.co` origines. U `api/routes.py` integrisan je CORS middleware:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"], # Ili specifične HF pod-domene
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. **Zaobilaženje Identity Guards-a:** Na HF Spaces-u, pošto ne postoji GCP okruženje, `IdentityGuard` bi po defaultu blokirao start. Kako bi se omogućila demonstracija na HF Spaces, postavlja se sledeća env varijabla u HF postavkama:
   ```env
   SKIP_IDENTITY_CHECK=true
   ```
   Ovo omogućava demonstraciju bez ugrožavanja bezbednosti pravog GCP produkcionog okruženja.

---

## 🧪 Lokalno Testiranje i Verifikacija koda

Pre svakog push-a na produkcione grane, obavezno je pokrenuti sveobuhvatni testni paket preko PyTest-a kako bi se verifikovala celovitost sistema.

* **Pokretanje svih testova:**
  ```bash
  pytest tests/ -v
  ```

* **Struktura testnog paketa:**
  1. `test_agents.py`: Proverava da li Gemini uspešno prima sistemske prompte i odgovara u ispravnom JSON formatu sa konfidencijom.
  2. `test_elo.py`: Simulira uspešne i neuspešne ishode debata i proverava da li se ELO rejtinzi agenata u SQLite bazi menjaju po tačnim matematičkim formulama.
  3. `test_circuit_breaker.py`: Simulira potrošnju više od 100,000 tokena i potvrđuje da `TokenBudgetTracker` trenutno blokira dalji rad orkestratora i baca odgovarajući izuzetak.
