import{c as a,Q as n,j as i,m as e}from"./chunks/framework.BPKcPtvA.js";const c=JSON.parse('{"title":"Data Flows & Sequence Diagrams","description":"Technical overview of orchestrator transaction flows, debate turns, veto limits, and self-healing overrides","frontmatter":{"title":"Data Flows & Sequence Diagrams","description":"Technical overview of orchestrator transaction flows, debate turns, veto limits, and self-healing overrides","keywords":"data flow, sequence diagram, debate sequence, veto trigger, self-healing flow, mermaid","robots":"index, follow"},"headers":[],"relativePath":"en/data-flow.md","filePath":"en/data-flow.md","lastUpdated":null}'),t={name:"en/data-flow.md"};function l(p,s,r,E,o,h){return n(),i("div",null,[...s[0]||(s[0]=[e(`<h1 id="🔄-data-flows-sequence-diagrams" tabindex="-1">🔄 Data Flows &amp; Sequence Diagrams <a class="header-anchor" href="#🔄-data-flows-sequence-diagrams" aria-label="Permalink to &quot;🔄 Data Flows &amp; Sequence Diagrams&quot;">​</a></h1><p>This document visualizes how request vectors, agent states, and evaluation variables flow across the <strong>AI Workflow Orchestrator</strong>.</p><p>Using formal Mermaid sequence flows, we break down three core operational patterns: Standard execution consensus, Security Veto intercepts, and Autonomous Self-Healing loops.</p><hr><h2 id="🟢-1-standard-execution-flow-consensus-proceed" tabindex="-1">🟢 1. Standard Execution Flow (Consensus Proceed) <a class="header-anchor" href="#🟢-1-standard-execution-flow-consensus-proceed" aria-label="Permalink to &quot;🟢 1. Standard Execution Flow (Consensus Proceed)&quot;">​</a></h2><p>The sequence map below demonstrates a standard execution pipeline where the adversarial arena resolves with high consensus confidence and no security anomalies:</p><div class="language-mermaid vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">mermaid</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">sequenceDiagram</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    autonumber</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    actor User as User / CLI / API Endpoint</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Engine as WorkflowOrchestrator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Memory as Memory Controller (SQLite/Mongo)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Arena as DebateManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Agg as DebateAggregator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Exec as ExecutionManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Val as ValidationChecker</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    User-&gt;&gt;Engine: Submit Request (e.g. &quot;deploy secure web app&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Engine: Assert Workspace (IdentityGuard)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Memory: load_memory_context() &amp; retrieve_similar_workflows()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Memory--&gt;&gt;Engine: Historic traces and agent Elo rankings</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Engine: build_initial_plan()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Arena: Trigger Arena (run_debate)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Arena: Phase 1-5: Turn-based confrontation</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 1. Analyst: Decomposes requirements &amp; maps threats</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 2. Solution: Drafts technical proposal plan</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 3. Critic: Audits proposal and challenges flaws</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 4. Security: Asserts sandbox permissions &amp; bounds</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: 5. Optimizer: Recommends design refinements</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Arena: Multi-Pass Heuristics (&quot;Rule of 3&quot; refinements)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena--&gt;&gt;Engine: Structured arguments with confidence scores</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Agg: Compute Consensus (calculate_consensus)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Agg: Weighting role priority + Elo ratings</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg-&gt;&gt;Agg: Run Critic vs Solution Elo Duel (adjust ELO)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg--&gt;&gt;Engine: Outcome (PROCEED: Consensus Reached, ELO updates)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Exec: execute_plan(final_decision)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec-&gt;&gt;Exec: Run sandboxed tasks (assert Admission Policies)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec--&gt;&gt;Engine: Execution Report (Success)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Val: validate_results(execution_report)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Val--&gt;&gt;Engine: Validation Report (Valid)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Memory: store_all_in_memory(outcome, trace, ELO)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Memory--&gt;&gt;Engine: Commit confirmation</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine--&gt;&gt;User: Success response + Session Trace ID</span></span></code></pre></div><hr><h2 id="🔴-2-security-veto-intercept-security-veto-triggered" tabindex="-1">🔴 2. Security Veto Intercept (Security Veto Triggered) <a class="header-anchor" href="#🔴-2-security-veto-intercept-security-veto-triggered" aria-label="Permalink to &quot;🔴 2. Security Veto Intercept (Security Veto Triggered)&quot;">​</a></h2><p>If the Security agent identifies a critical runtime privilege violation (such as mounting <code>/var/run/docker.sock</code> or hostPath volumes) with a confidence score $\\ge 0.9$, the debate is immediately halted, execution plans are discarded, and penalties are applied:</p><div class="language-mermaid vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">mermaid</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">sequenceDiagram</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    autonumber</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    actor User as User / CLI / API Endpoint</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Engine as WorkflowOrchestrator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Arena as DebateManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Agg as DebateAggregator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Memory as Memory Controller</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    User-&gt;&gt;Engine: Submit Request (&quot;run container mounting docker.sock&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Arena: Trigger Arena (run_debate)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: Solution Agent proposes Docker socket mount</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena-&gt;&gt;Arena: Security Agent detects Privilege Escalation (Confidence 0.95!)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Arena--&gt;&gt;Engine: Debate arguments</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Agg: Compute Consensus (calculate_consensus)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Agg: Security confidence &gt;= 0.9 forces immediate VETO</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg-&gt;&gt;Agg: Penalty duel: Solution ELO -50 points</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg-&gt;&gt;Agg: Reward: Security ELO +25 points</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Agg--&gt;&gt;Engine: Outcome (REJECTED: Critical security risk detected)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Memory: store_all_in_memory()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Engine: Audit Log Final Decision (trace_id)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine--&gt;&gt;User: Error response: Access denied under GKE admission rules!</span></span></code></pre></div><hr><h2 id="🟡-3-autonomous-self-healing-loop" tabindex="-1">🟡 3. Autonomous Self-Healing Loop <a class="header-anchor" href="#🟡-3-autonomous-self-healing-loop" aria-label="Permalink to &quot;🟡 3. Autonomous Self-Healing Loop&quot;">​</a></h2><p>If post-execution verification fails (e.g. system reports syntax issues or port blockages), the orchestrator intercepts the error and routes the state to the <strong>Self-Healing Loop</strong> to automatically patch the plan:</p><div class="language-mermaid vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">mermaid</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">sequenceDiagram</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    autonumber</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Engine as WorkflowOrchestrator</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Exec as ExecutionManager</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Val as ValidationChecker</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Heal as SelfHealHook</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Critic as Critic Agent</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    participant Sol as Solution Agent</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Exec: Execute Plan</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec--&gt;&gt;Engine: Execution failure (Error: Port 80 already in use)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Val: validate_results()</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Val--&gt;&gt;Engine: Validation Report (Invalid - failures detected)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Note over Engine: Intercept validation failure!</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Engine-&gt;&gt;Heal: attempt_self_healing(execution_report)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Critic: Diagnose Failure (think: &quot;Explain port 80 fail&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Critic--&gt;&gt;Heal: Diagnosis (Port 80 occupied, switch to port 8080)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Sol: Propose Repair Patch (think: &quot;Generate repaired proposal&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Sol--&gt;&gt;Heal: Repair Plan (&quot;PROCEED: run command on port 8080&quot;)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Exec: Re-execute patch plan</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Exec--&gt;&gt;Heal: New execution report (Success)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    </span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal-&gt;&gt;Val: Re-validate results</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Val--&gt;&gt;Heal: Validation Report (Valid)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">    Heal--&gt;&gt;Engine: Self-healing complete!</span></span></code></pre></div>`,15)])])}const k=a(t,[["render",l]]);export{c as __pageData,k as default};
