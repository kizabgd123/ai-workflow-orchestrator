---
title: "Baza Podataka & Memorijski Sloj"
description: "Tehnički opis SQLite lokalnog bafera i MongoDB Atlas forenzičkog i vektorskog sloja pamćenja"
keywords: "database schema, sqlite, mongodb atlas, vector search, database index, memory layer"
robots: "index, follow"
---

# 💾 Baza Podataka & Memorijski Sloj

Sistem primenjuje **hibridnu dvo-slojnu arhitekturu memorije** (Multi-Tier Memory Engine) kako bi garantovao nultu latenciju tokom debata i trajnu perzistenciju/pretragu sličnosti u oblaku.

---

## 🏛️ Pregled Memorijskog Sloja

```
                    [ Korisnički Upit ]
                             │
                             ▼
               [ 🧠 MEMORIJSKI KONTROLER ]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [ 💻 SQLite Lokalni Sloj ]      [ ☁️ MongoDB Atlas Sloj ]
   - Ekstremno niska latencija     - Semantička Vektorska Pretraga
   - Čuvanje ELO rejtinga          - Globalni Audit Trace-ova
   - Istorija replika po sesiji    - Failover režim preko SQLite-a
```

---

## 💻 1. Lokalni Sloj: SQLite Baza podataka

Lokalno skladište se nalazi u `storage/memory.db`. Njegova osnovna uloga je čuvanje agent ELO ratinga i logova debata u realnom vremenu sa latencijom $< 1\text{ms}$.

### Tabela: `agent_elo`
Čuva reputacioni ELO rejting i broj odigranih mečeva (debata) za svakog agenta.
* **SQL Definicija:**
  ```sql
  CREATE TABLE IF NOT EXISTS agent_elo (
      agent_id TEXT PRIMARY KEY,
      elo REAL DEFAULT 1200.0,
      matches INTEGER DEFAULT 0
  );
  ```

### Tabela: `debates`
Beleži metapodatke svake završene debate sesije.
* **SQL Definicija:**
  ```sql
  CREATE TABLE IF NOT EXISTS debates (
      id TEXT PRIMARY KEY,
      workflow_id TEXT,
      status TEXT,
      final_decision TEXT,
      confidence_score REAL,
      rejected_alternatives TEXT,
      conflict_points TEXT,
      reasoning_trace TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

### Tabela: `arguments`
Čuva pojedinačne argumente agenata po rundama za svaku debatu.
* **SQL Definicija:**
  ```sql
  CREATE TABLE IF NOT EXISTS arguments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      debate_id TEXT,
      agent_id TEXT,
      role TEXT,
      content TEXT,
      confidence REAL,
      round INTEGER,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(debate_id) REFERENCES debates(id)
  );
  ```

### Tabela: `decision_history`
Sadrži istorijske odluke sa verifikovanim ishodima, koje se koriste za pretragu sličnosti konteksta.
* **SQL Definicija:**
  ```sql
  CREATE TABLE IF NOT EXISTS decision_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      context_hash TEXT UNIQUE,
      problem_statement TEXT,
      decision_taken TEXT,
      outcome_verified BOOLEAN DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

---

## ☁️ 2. Globalni Sloj: MongoDB Atlas

MongoDB Atlas služi kao robusni forenzički sloj za globalno skladištenje i pretragu celokupnih audit tragova, integrisan sa **Atlas Vector Search** za semantičku analizu.

### 📁 Atlas Kolekcije (Collections)
1. **`debates`**: Metapodatci debate i istorija konsenzusa.
2. **`arguments`**: Pojedinačne replike agenata sa konfidencijom i round brojem.
3. **`decision_history`**: Odluke i verifikovani statusi.
4. **`agent_opinions`**: Praćenje pojedinačnih mišljenja agenata.
5. **`agent_elo`**: Rejtinzi agenata sinhronizovani iz SQLite baze.
6. **`workflows`**: Kompletan trace-log izvršenja koraka workflow-a.

### 🔍 Indeksi i Optimizacija Performansi
Za ubrzanje upita na Atlasu kreirani su sledeći indeksi:
```javascript
// Brza pretraga debate po ID-ju toka rada i datumu kreiranja
db.debates.createIndex({ "workflow_id": 1, "created_at": -1 });

// Brzo učitavanje argumenata za određenu debatu i specifičnog agenta
db.arguments.createIndex({ "debate_id": 1, "agent_id": 1 });

// Pretragu sličnosti kroz jedinstveni hash konteksta
db.decision_history.createIndex({ "context_hash": 1 });
```

---

## 🔍 Atlas Vector Search & Semantička Pretraga

MongoDB Atlas omogućava pronalaženje istorijskih debata na osnovu semantičke sličnosti problema (problem statement). 

### 1. Konfiguracija Indeksa za Vektorsku Pretragu (Atlas Vector Search Index)
Na kolekciji `decision_history` definisan je indeks pod nazivom `vector_index` sa sledećim JSON mapiranjem:
```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "problem_embedding": {
        "dimensions": 1536,
        "similarity": "cosine",
        "type": "knnVector"
      }
    }
  }
}
```

### 2. Agregacioni Pipeline za Semantičko Učitavanje Konteksta
U orkestratoru, slični workflow-i se učitavaju pokretanjem sledećeg MongoDB Atlas agregacionog koda:
```python
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "problem_embedding",
            "queryVector": problem_vector,
            "numCandidates": 10,
            "limit": 3
        }
    },
    {
        "$project": {
            "_id": 0,
            "problem_statement": 1,
            "decision_taken": 1,
            "outcome_verified": 1,
            "score": { "$meta": "vectorSearchScore" }
        }
    }
]
results = list(db.decision_history.aggregate(pipeline))
```

---

## 🛠️ MCP (Model Context Protocol) Integracija

MongoDB Atlas se integriše kao MCP server, nudeći agentima bezbedan skup alata (Tools) za manipulaciju memorijom:

* **`store_debate_outcome`**: Upisuje ishod debate.
* **`search_similar_decisions`**: Pokreće vektorsku pretragu za pronalaženje analognih konflikata.
* **`get_agent_reliability`**: Pokreće agregacioni upit nad kolekcijom `arguments` za računanje istorijskog proseka konfidencije:
  ```python
  pipeline = [
      {"$match": {"agent_id": agent_id}},
      {"$group": {
          "_id": "$agent_id",
          "avg_confidence": {"$avg": "$confidence"}
      }}
  ]
  ```
  Ovaj istorijski prosek direktno utiče na dinamičku težinu agenta u debatnoj areni.
