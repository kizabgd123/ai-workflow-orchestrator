---
layout: home
title: AI Workflow Orchestrator
description: "Siguran, audita-bilan i otporan višestruki agent sistem sa debatom i memorijom"
keywords: "AI, agent, orchestrator, debate engine, mongodb, sqlite, fastapi"
robots: "index, follow"
hero:
  name: "AI Workflow Orchestrator"
  text: "Sigurna orkestracija AI tokova rada"
  tagline: "Rezonovanje zasnovano na debati agenata sa dugoročnom memorijom, reputacijom i nultim poverenjem."
  actions:
    - theme: brand
      text: "Tehnička Analiza"
      link: "/analysis"
    - theme: alt
      text: "Arhitektura Sistema"
      link: "/architecture"
    - theme: alt
      text: "GitHub Izvor"
      link: "https://github.com/kiza101288/ai-workflow-orchestrator"
features:
  - icon: "🤝"
    title: "Multi-Agent Debate Engine"
    details: "Specijalizovani agenti (Analyst, Solution, Critic, Security, Optimizer) se suočavaju u debatama pre nego što se donese bilo koja konačna odluka."
  - icon: "💾"
    title: "Forenzička Memorija"
    details: "Perzistentno pamćenje kroz SQLite i MongoDB Atlas. Učitava slične istorijske debate i konflikte kako bi sistem učio iz prošlih grešaka."
  - icon: "🛡️"
    title: "Nulto Poverenje (Identity Guard)"
    details: "Verifikacija identiteta na nivou okruženja (GCP i MongoDB) koja blokira curenje podataka ili kontaminaciju pre izvršenja."
  - icon: "⚡"
    title: "Dinamički Agent ELO Rating"
    details: "Agenti imaju Elo reputaciju (između 0.5 i 1.5) koja raste ili opada na osnovu verifikovanih ishoda debata, što direktno utiče na njihov glas."
  - icon: "🔌"
    title: "Zaštita Token Budžeta"
    details: "Middleware u FastAPi-ju služi kao automatski prekidač (circuit breaker) koji blokira dalji rad ukoliko sesija pređe 100,000 tokena."
  - icon: "🔄"
    title: "Automatsko Samolečenje (Self-Healing)"
    details: "Ako izvršenje naredbe ne uspe, Critic agent dijagnostikuje kvar, a Solution agent generiše popravljeni plan koji se ponovo bezbedno izvršava."
---

<div class="content-section">
  <h2>Brzi Pregled Arhitekture</h2>
  <p>Za razliku od tradicionalnih "black-box" rešenja koja slepo izvršavaju korisničke instrukcije, naš orkestrator uvodi formalni adversarial sloj:</p>

```
Korisnički Zahtev ➔ Identifikacija & Klasifikacija ➔ Istorijski Kontekst
                             │
                             ▼
              [ 🤝 DEBATNA ARENA IZMEĐU AGENATA ]
      Analyst ➔ Solution ➔ Critic ➔ Security ➔ Optimizer
                             │
                             ▼
         [ ⚖️ KONSENZUS AGREGATOR & ELO MULTIPLIKATORI ]
                             │
            PROCEED ─────────┴───────── REJECT/VETO
               │                               │
               ▼                               ▼
    [ 🏃 EXECUTOR RUNNER ]              [ 🛡️ SIGURNI VETO ]
               │
               ▼
    [ 🧪 VALIDATION CHECK ] ➔ [ 💾 MEMORY PERSISTENCE ]
```
</div>
