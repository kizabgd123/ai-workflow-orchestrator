---
title: AI Workflow Orchestrator
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# AI Workflow Orchestrator

Production-grade AI system with multi-agent adversarial debate, memory integration, and execution tracing.

## Core Mechanisms

### 1. Adversarial Debate Engine
The system doesn't rely on a single agent's output. Every complex request triggers a multi-round debate:
- **Analyst**: Decomposes the problem.
- **Solution Agent**: Proposes an implementation.
- **Critic**: Hard adversarial attack on the proposal.
- **Security**: Zero-trust evaluation.
- **Optimizer**: Efficiency and refinement.
- **Aggregator**: Final decision based on weighted consensus and safety rules.

### 2. Memory-Integrated Decisions
The **Memory Engine** (SQLite backend) stores every debate as a "Decision Artifact".
- **Similarity Lookup**: Current debates load context from past similar conflicts.
- **Agent Elo**: Agents earn/lose reputation based on the validity of their arguments and final outcomes.
- **Conflict Tracking**: Recurring patterns of disagreement are recorded to improve future resolution strategies.

### 3. Workflow Pipeline
1. **Load Memory**: Retrieve historical context.
2. **Debate**: Execute multi-round adversarial reasoning.
3. **Resolve**: Final consensus with confidence scores.
4. **Execute**: Deployment or implementation via specialized runners.
5. **Validate**: Post-execution verification.
6. **Audit**: Complete trace logged to storage.

### 4. Hugging Face Model Discovery
The dashboard features an interactive model exploration portal that queries the Hugging Face Hub live:
- **Search Engine**: Dynamically queries the Hugging Face api to search for state-of-the-art models (like Gemma, Llama, DeepSeek).
- **Offline Fallback Catalog**: If internet connectivity is interrupted or restricted, the portal seamlessly fails over to a premium pre-cached local catalog of top-performing Google Gemma models.
- **One-Click Target Overlay**: Clicking "Apply to Orchestrator" on any discovered card will dynamically overlay and tag the model into the live job request input, routing the adversarial debate or execution step to leverage its target specifications.

### 5. Zero Script QA
The system implements the **Zero Script QA** methodology for autonomous verification:
- **Structured Logging**: All core modules emit logs in JSON format with event tags.
- **Pattern Verification**: Logs are verified against predefined patterns in `qa/patterns.json`.
- **Real-time Monitoring**: The `scripts/qa_monitor.py` tool performs live verification of system behavior.
- **Usage**:
  ```bash
  export SKIP_IDENTITY_CHECK=true && python main.py "task" | python scripts/qa_monitor.py
  ```

## Setup & Execution
...

### Prerequisites
- Python 3.10+
- Google Gemini API Key (GOOGLE_API_KEY)

### Running the Orchestrator
```bash
python main.py "deploy a secure database cluster on GKE"
```

### Configuration
Update configs/ for model routing and token budgets.

## 5. Deep Search Memory Power-Up (QMD)
To navigate this complex codebase and technical documentation efficiently, the project is integrated with **[QMD](https://github.com/tobi/qmd)**—a 100% local hybrid semantic search engine (BM25 keywords + Vector similarity via Gemma):
* **Active Collections:**
  * `docs` (`qmd://docs/`) — Index of project spec planning and design.
  * `agents` (`qmd://agents/`) — Specialized agent logic.
  * `orchestrator` (`qmd://orchestrator/`) — Core workflow engine.
* **Commands:**
  ```bash
  # Check index status
  qmd status
  
  # Search with keyword BM25 across docs/code
  qmd search "self-healing"
  
  # Semantic search using model embeddings
  qmd query "how are ELO ratings updated"
  ```

---
*Built with Security, Reliability, and Auditability as core mandates.*
