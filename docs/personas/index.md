---
title: "Persone Kupaca i Korisnika"
description: "Definisanje ključnih persona korisnika i donosilaca odluka za AI Workflow Orchestrator"
keywords: "buyer persona, user persona, target audience, customer profiles"
robots: "index, follow"
---

# 👤 Persone Kupaca i Korisnika

Da bismo osigurali da **AI Workflow Orchestrator** rešava stvarne poslovne i tehničke probleme, definisali smo dve ključne persone: **Kupca** (donosioca odluke o kupovini) i **Korisnika** (inženjera koji svakodnevno koristi sistem).

---

## 👔 1. Buyer Persona: Donosilac Odluke o Nabavci

* **Ime:** Marko Jovanović
* **Uloga:** VP of Security & Infrastructure (Potpredsednik za sigurnost i infrastrukturu)
* **Kompanija:** Srednja fintech kompanija sa brzim rastom
* **Demografija:** 42 godine, magistar elektrotehnike, živi u Beogradu.

```
                  [ MARKO JOVANOVIĆ — VP OF SECURITY ]
   Cilj: 100% usklađenost, bezbednost podataka, kontrolisana AI automatizacija.
   Bolna tačka: Tradicionalni AI agenti koji slepo izvršavaju skripte i rizikuju curenje podataka.
```

### Ciljevi i Motivi:
* **Usklađenost i Auditabilnost:** Zahteva da svaka automatska akcija u oblaku ima jasan i retroaktivno proverljiv "reasoning chain" (lanac razmišljanja) radi PCI-DSS usklađenosti.
* **Eliminacija rizika:** Želi sistem koji ne dozvoljava nijednom pojedinačnom AI agentu da samostalno izvrši kod bez unutrašnjeg preispitivanja i provere.
* **Finansijska predvidivost:** Zahteva čvrste limite potrošnje tokena kako bi sprečio finansijska iznenađenja.

### Ključne Bolne Tačke (Pain Points):
* **Strah od curenja podataka:** Ne veruje standardnim "black-box" agentima koji mogu poslati osetljive podatke kompanije spoljnim LLM provajderima.
* **Nebezbedne konfiguracije:** Ranija negativna iskustva sa AI kod generisanjem koje je kreiralo privilegovane Kubernetes kontejnere sa otvorenim portovima.

---

## 👩‍💻 2. User Persona: Svakodnevni Korisnik

* **Ime:** Jelena Nikolić
* **Uloga:** Lead DevOps & Site Reliability Engineer (SRE)
* **Kompanija:** Isti fintech startup
* **Demografija:** 29 godina, inženjer informacionih tehnologija, živi u Novom Sadu.

```
                   [ JELENA NIKOLIĆ — LEAD SRE ]
   Cilj: Brza orkestracija, bezbedni planovi, automatsko otklanjanje kvarova.
   Bolna tačka: Ručno popravljanje sitnih grešaka u konfiguracionim skriptama.
```

### Ciljevi i Motivi:
* **Brza automatizacija:** Želi da delegira kompleksne zadatke (poput postavljanja klastera) sistemu koji samostalno piše planove i izvršava ih.
* **Smanjenje ručnog rada:** Želi da AI sistem sam dijagnostikuje i ispravi sitne greške pri podizanju sistema bez njenog učešća (Self-Healing).
* **Jednostavna integracija:** Zahteva čist REST API i SSE strimovanje stanja kako bi integrisala sistem sa postojećim Slack botovima.

### Ključne Bolne Tačke (Pain Points):
* **Umnožavanje grešaka:** Gubitak vremena na analizu logova kada AI skripta pukne na produkciji.
* **Komplikovano debugovanje:** Teškoća u praćenju istorijskih odluka koje su dovele do trenutnog stanja infrastrukture.
