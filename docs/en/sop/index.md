---
title: "SOP Operational Guides"
description: "Standard Operating Procedures (SOP) for starting, configuring, and debugging the orchestrator system"
keywords: "SOP, runbook, operational guide, setup protocol, troubleshooting guide"
robots: "index, follow"
---

# 📋 SOP Operational Guides

Welcome to the **Standard Operating Procedures (SOP)** index. This section houses detailed operational runbooks designed for Site Reliability Engineers (SREs) and system administrators responsible for operating and scaling the **AI Workflow Orchestrator**.

---

## 🗂️ Operational Runbook Directory

Our guides are separated into two distinct focus areas:

### 1. [SOP-001: Installation & Setup Guide](/en/sop/setup)
Step-by-step instructions for booting the environment, binding API keys, setting up databases, and enforcing zero-trust boundaries.
* **Topics covered:** API key rotation schemas, session token budgeting, MongoDB Atlas vector configuration, and sandbox environments verification.
* **Status:** 🟢 Active & Verified.

### 2. [SOP-002: Diagnostics & Troubleshooting Guide](/en/sop/troubleshooting)
Runbooks for recovering from system errors, repairing corrupt database files, resolving connection drops, and analyzing runtime trace logs.
* **Topics covered:** Resetting agent ELO ratings, SQLite file recovery, debugging budget trips, and intercepting self-healing logs inside the `storage/traces/` directory.
* **Status:** 🟢 Active & Verified.

---

## 🛡️ Core Rules for System Operators

Before initiating any manual terminal command or configuration change, adhere to the following safety policies:
1. **Never hardcode secrets:** All sensitive resources (such as Google API keys or MongoDB URIs) must be injected as encrypted environment variables or loaded from secret stores (e.g. GCP Secret Manager).
2. **Back up databases before rating updates:** Any manual ELO reputation adjust operations must be preceded by an offline file backup (`cp storage/memory.db storage/memory_backup.db`).
3. **Inspect Critic traces before manual intervention:** Always analyze trace summaries of failed workflow runs to leverage the Critic agent's automated diagnosis before building manual hotfixes.
