import{c as s,Q as i,j as n,m as e}from"./chunks/framework.BPKcPtvA.js";const h=JSON.parse('{"title":"Tokovi Podataka & Sekvencijalni Dijagrami","description":"Tehnički pregled protoka informacija kroz orkestrator, faze debata, veto sisteme i samoisceljenje","frontmatter":{"title":"Tokovi Podataka & Sekvencijalni Dijagrami","description":"Tehnički pregled protoka informacija kroz orkestrator, faze debata, veto sisteme i samoisceljenje","keywords":"data flow, sequence diagram, debate sequence, veto trigger, self-healing flow, mermaid","robots":"index, follow"},"headers":[],"relativePath":"data-flow.md","filePath":"data-flow.md","lastUpdated":null}'),t={name:"data-flow.md"};function l(p,a,r,E,k,o){return i(),n("div",null,[...a[0]||(a[0]=[e(`<h1 id="🔄-tokovi-podataka-sekvencijalni-dijagrami" tabindex="-1">🔄 Tokovi Podataka &amp; Sekvencijalni Dijagrami <a class="header-anchor" href="#🔄-tokovi-podataka-sekvencijalni-dijagrami" aria-label="Permalink to &quot;🔄 Tokovi Podataka &amp; Sekvencijalni Dijagrami&quot;">​</a></h1><p>Ovaj priručnik detaljno prikazuje kako podaci i kontrolni tokovi cirkulišu kroz <strong>AI Workflow Orchestrator</strong>.</p><p>Kroz sekvencijalne dijagrame, dokument objašnjava tri ključna scenarija: standardno izvršenje sa debatom, sigurnosni veto i asinhrono samoisceljenje (Self-Healing) u slučaju kvara.</p><hr><h2 id="🟢-1-standardni-orkestracioni-tok-consensus-proceed" tabindex="-1">🟢 1. Standardni Orkestracioni Tok (Consensus Proceed) <a class="header-anchor" href="#🟢-1-standardni-orkestracioni-tok-consensus-proceed" aria-label="Permalink to &quot;🟢 1. Standardni Orkestracioni Tok (Consensus Proceed)&quot;">​</a></h2><p>Sledeći sekvencijalni dijagram prikazuje standardni krug rada kada agenti postignu visok stepen poverenja i konsenzus bez bezbednosnih alarma:</p><div class="language-mermaid vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">mermaid</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">sequenceDiagram</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    autonumber</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    actor Korisnik as Korisnik / CLI / API</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Engine as WorkflowOrchestrator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Memory as Memory Controller (SQLite/Mongo)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Arena as DebateManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Agg as DebateAggregator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Exec as ExecutionManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Val as ValidationChecker</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Korisnik-&gt;&gt;Engine: Pošalji Zahtev (npr. &quot;deploy secure web app&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Engine: Verifikuj Identitet (IdentityGuard)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Memory: load_memory_context() &amp; retrieve_similar_workflows()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Memory--&gt;&gt;Engine: Istorijski trace-ovi i ELO rating agenata</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Engine: build_initial_plan()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Arena: Pokreni Debatu (run_debate)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Arena: Faza 1-5: Sukobljavanje Agencija</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 1. Analyst: Razlaže zahtev i pretnje</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 2. Solution: Predlaže plan izvršenja</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 3. Critic: Napada plan i traži greške</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 4. Security: Proverava privilegije i portove</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 5. Optimizer: Nudi efikasnije alternative</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Arena: Multi-Pass Heuristics (&quot;Rule of 3&quot; rafinacija)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena--&gt;&gt;Engine: Lista argumenata sa konfidencijom</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Agg: Izračunaj Konsenzus (calculate_consensus)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Agg: Ponderisanje preko uloga + ELO ocena</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg-&gt;&gt;Agg: Duel Critic vs Solution (ažuriraj ELO)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg--&gt;&gt;Engine: Outcome (PROCEED: Consensus Reached, ELO updates)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Exec: execute_plan(final_decision)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec-&gt;&gt;Exec: Sandboxed izvršenje komandi (GKE Admission checks)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec--&gt;&gt;Engine: Izveštaj o izvršenju (Success)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Val: validate_results(execution_report)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Val--&gt;&gt;Engine: Validation Report (Valid)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Memory: store_all_in_memory(outcome, trace, ELO)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Memory--&gt;&gt;Engine: Potvrda upisa</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine--&gt;&gt;Korisnik: Uspešan Rezultat + Trace ID</span></span></code></pre></div><hr><h2 id="🔴-2-sigurnosni-veto-security-veto-triggered" tabindex="-1">🔴 2. Sigurnosni Veto (Security Veto Triggered) <a class="header-anchor" href="#🔴-2-sigurnosni-veto-security-veto-triggered" aria-label="Permalink to &quot;🔴 2. Sigurnosni Veto (Security Veto Triggered)&quot;">​</a></h2><p>Ukoliko Security agent prepozna ozbiljan rizik (npr. montiranje <code>/var/run/docker.sock</code> ili privilegovani <code>hostPath</code> u Kubernetes pod-u) sa konfidencijom $\\ge 0.9$, debata se odmah prekida, plan odbija i sprovode se kaznene mere:</p><div class="language-mermaid vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">mermaid</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">sequenceDiagram</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    autonumber</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    actor Korisnik as Korisnik / CLI / API</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Engine as WorkflowOrchestrator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Arena as DebateManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Agg as DebateAggregator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Memory as Memory Controller</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Korisnik-&gt;&gt;Engine: Pošalji Zahtev (&quot;run container mounting docker.sock&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Arena: Pokreni Debatu (run_debate)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: Solution Agent predlaže montiranje sock fajla</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: Security Agent detektuje Privilege Escalation (Confidence 0.95!)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena--&gt;&gt;Engine: Lista argumenata</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Agg: Izračunaj Konsenzus (calculate_consensus)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Agg: Security konfidencija &gt;= 0.9 pokreće VETO</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg-&gt;&gt;Agg: Kazneni duel: Solution ELO -50 bodova</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg-&gt;&gt;Agg: Nagrada: Security ELO +25 bodova</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg--&gt;&gt;Engine: Outcome (REJECTED: Critical security risk detected)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Memory: store_all_in_memory()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Engine: Audit Log Final Decision (trace_id)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine--&gt;&gt;Korisnik: Greška: Odbijeno iz bezbednosnih razloga!</span></span></code></pre></div><hr><h2 id="🟡-3-asinhrono-samoisceljenje-self-healing-loop" tabindex="-1">🟡 3. Asinhrono Samoisceljenje (Self-Healing Loop) <a class="header-anchor" href="#🟡-3-asinhrono-samoisceljenje-self-healing-loop" aria-label="Permalink to &quot;🟡 3. Asinhrono Samoisceljenje (Self-Healing Loop)&quot;">​</a></h2><p>Ukoliko validation check ne uspe nakon izvršenja komande (npr. greška u portu ili sintaksi), orkestrator aktivira <strong>Self-Healing Loop</strong> za automatsko rešavanje problema:</p><div class="language-mermaid vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">mermaid</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">sequenceDiagram</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    autonumber</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Engine as WorkflowOrchestrator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Exec as ExecutionManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Val as ValidationChecker</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Heal as SelfHealHook</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Critic as Critic Agent</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Sol as Solution Agent</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Exec: Izvrši plan</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec--&gt;&gt;Engine: Izveštaj sa greškom (Error: Port 80 already in use)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Val: validate_results()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Val--&gt;&gt;Engine: Validation Report (Invalid - failures detected)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Engine: Aktivacija samoisceljenja!</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Heal: attempt_self_healing(execution_report)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Critic: Dijagnostikuj kvar (think: &quot;Zašto port 80 ne radi?&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Critic--&gt;&gt;Heal: Objašnjenje (Port 80 je zauzet, promeniti na 8080)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Sol: Predloži patch (think: &quot;Kako popraviti port?&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Sol--&gt;&gt;Heal: Generisani hotfix plan (&quot;PROCEED: run command on port 8080&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Exec: Re-execute patch plan</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec--&gt;&gt;Heal: Izveštaj o novom izvršenju (Success)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Val: Re-validate results</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Val--&gt;&gt;Heal: Validation Report (Valid)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal--&gt;&gt;Engine: Samoisceljenje uspešno!</span></span></code></pre></div>`,15)])])}const c=s(t,[["render",l]]);export{h as __pageData,c as default};
