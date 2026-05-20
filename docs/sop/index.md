---
title: "SOP Operativna Uputstva"
description: "Standardne operativne procedure (SOP) za pokretanje, konfigurisanje i otklanjanje grešaka u radu orkestratora"
keywords: "SOP, runbook, operational guide, setup protocol, troubleshooting guide"
robots: "index, follow"
---

# 📋 SOP Operativna Uputstva

Dobrodošli u odeljak za **Standardne Operativne Procedure (SOP)**. Ovde se nalaze detaljni koraci i operativni priručnici (Runbooks) namenjeni inženjerima za pouzdanost sistema (SRE) i administratorima za upravljanje i održavanje **AI Workflow Orchestrator** sistema.

---

## 🗂️ Sadržaj Operativnih Vodiča

Operativna uputstva su podeljena u dve ključne kategorije:

### 1. [SOP-001: Instalacija & Setup Vodič](/sop/setup)
Kompletan vodič za inicijalno pokretanje sistema, podešavanje API ključeva, konfigurisanje baze podataka i bezbednosne pre-kondicije.
* **Ključne teme:** Rotacija API ključeva, definisanje token limita, integracija sa MongoDB Atlasom i zaobilaženje IdentityGuard provere u netipičnim sredinama.
* **Status:** 🟢 Aktivno i Verifikovano.

### 2. [SOP-002: Dijagnostika & Otklanjanje Grešaka (Troubleshooting)](/sop/troubleshooting)
Priručnik za rešavanje vanrednih stanja u sistemu, ručnu popravku SQLite baza, detekciju curenja LLM tokena i konfigurisanje self-healing parametara.
* **Ključne teme:** Reset ELO rejtinga agenata, otključavanje baze pod lock-om, i analiza trace logova u `storage/traces/` direktorijumu.
* **Status:** 🟢 Aktivno i Verifikovano.

---

## 🛡️ Sigurnosna Pravila za Operatere

Pre pokretanja bilo koje operativne procedure, uverite se da se pridržavate sledećih pravila:
1. **Nema produkcionih ključeva u kodu:** Svi API ključevi za Gemini i MongoDB URI moraju biti prosleđeni isključivo kroz enkriptovane env tajne (npr. Google Cloud Secret Manager).
2. **Obavezan backup pre ELO resetovanja:** Ručne manipulacije nad SQLite bazom u cilju menjanja ELO ocena agenata moraju biti praćene kreiranjem kopije datoteke (`cp storage/memory.db storage/memory_backup.db`).
3. **Analiza logova pre ručnih patch-eva:** Uvek proverite trace izveštaje neuspešnog workflow-a pre pokretanja ručnih commands, kako biste videli dijagnozu Critic agenta.
