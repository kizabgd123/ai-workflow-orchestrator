---
title: "Database & Memory Layer"
description: "Technical specification of the SQLite local cache and MongoDB Atlas cloud forensic memory system"
keywords: "database schema, sqlite, mongodb atlas, vector search, database index, memory layer"
robots: "index, follow"
---

# 💾 Database & Memory Layer

The system implements a **hybrid two-tier memory architecture** (Multi-Tier Memory Engine) to guarantee zero-latency execution during live debates while ensuring persistent cloud auditing and semantic similarity lookups.

---

## 🏛️ Memory Engine Architecture Overview

```
                    [ User Input Request ]
                              │
                              ▼
                  [ 🧠 MEMORY CONTROLLER ]
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
   [ 💻 SQLite Local Cache ]           [ ☁️ MongoDB Atlas Layer ]
   - Latency profile < 1ms             - Semantic Vector Search
   - High-speed ELO storage            - Global Trace Audit Logs
   - Session argument replays          - Automatic SQLite Failover
```

---

## 💻 1. Local Cache Layer: SQLite Database

The local caching engine resides in `storage/memory.db`. Its primary purpose is to capture agent opinion rounds and Elo reputation updates with sub-millisecond latency.

### Table: `agent_elo`
Tracks the dynamic Elo ratings and total debate matches resolved for each agent.
* **SQL Definition:**
  ```sql
  CREATE TABLE IF NOT EXISTS agent_elo (
      agent_id TEXT PRIMARY KEY,
      elo REAL DEFAULT 1200.0,
      matches INTEGER DEFAULT 0
  );
  ```

### Table: `debates`
Records overall metadata and consensus resolutions for completed debates.
* **SQL Definition:**
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

### Table: `arguments`
Persists individual agent argument submissions per turn in a given debate session.
* **SQL Definition:**
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

### Table: `decision_history`
Maintains verified historical decisions linked to context hashes, supporting rapid static similarity checks.
* **SQL Definition:**
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

## ☁️ 2. Distributed Cloud Layer: MongoDB Atlas

MongoDB Atlas operates as a highly resilient forensic audit repository, leveraging **Atlas Vector Search** to conduct contextual similarity scans across past debate nodes.

### 📁 Atlas Collection Mapping
1. **`debates`**: Debate-level metadata, confidence scores, and consensus statuses.
2. **`arguments`**: Granular turn-by-turn agent positions, ELO levels, and confidence records.
3. **`decision_history`**: Historically verified architectural solutions.
4. **`agent_opinions`**: Session-level tracking of specific agent opinions.
5. **`agent_elo`**: Replicated agent ELO configurations.
6. **`workflows`**: Raw transaction step logs detailing the full execution footprint.

### 🔍 Secondary Database Indexing
To ensure high-performance lookups in Atlas, the following indexes are actively built:
```javascript
// High-speed debate checks filtering by workflow run and insertion date
db.debates.createIndex({ "workflow_id": 1, "created_at": -1 });

// Optimize round-level agent argument lookups
db.arguments.createIndex({ "debate_id": 1, "agent_id": 1 });

// Ensure fast hash-level duplicate checking
db.decision_history.createIndex({ "context_hash": 1 });
```

---

## 🔍 Atlas Vector Search Engine

MongoDB Atlas permits the system to locate contextually similar past conflicts by computing semantic distance between problem descriptions.

### 1. Vector Index Configuration (Atlas Vector Search Index)
On the `decision_history` collection, a dynamic k-NN index named `vector_index` is configured with the following definition:
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

### 2. Context Loading Aggregation Pipeline
During Step 3 of the orchestration pipeline, matching historical designs are semantically loaded using this query structure:
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

## 🛠️ MCP (Model Context Protocol) Integration

MongoDB Atlas exposes a secured Model Context Protocol tool interface, granting specialized agents controlled database operations:

* **`store_debate_outcome`**: Commits completed debate meta metrics.
* **`search_similar_decisions`**: Initiates semantic cosine queries over past resolution nodes.
* **`get_agent_reliability`**: Performs real-time pipeline aggregation to calculate long-term agent confidence coefficients:
  ```python
  pipeline = [
      {"$match": {"agent_id": agent_id}},
      {"$group": {
          "_id": "$agent_id",
          "avg_confidence": {"$avg": "$confidence"}
      }}
  ]
  ```
  The computed rating coefficient directly affects the agent's voting multiplier in the debate room.
