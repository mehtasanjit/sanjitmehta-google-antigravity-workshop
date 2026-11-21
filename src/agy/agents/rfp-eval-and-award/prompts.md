# Workshop prompts: RFP Evaluation and Award Agent

Self-contained prompts for building, testing, evaluating, and deploying the agent in Google Antigravity (`agy`) via `/google-agents-cli-*` slash commands.

## Before starting

1. Upload the synthetic quotes and policy file to GCS and copy the printed `gs://<YOUR_BUCKET>/rfp-eval-and-award/` URI:
   ```bash
   ./scripts/setup-gcs-data.sh --project <YOUR_GCP_PROJECT_ID>
   ```
2. Create an empty workspace (`adk/` and `langgraph/`):
   ```bash
   ./setup-workspace.sh
   ```
3. Open `rfp-eval-and-award-N/adk` or `rfp-eval-and-award-N/langgraph` in Antigravity and replace `<YOUR_GCP_PROJECT_ID>` and `<YOUR_GCS_BASE_URI>` below.

## Step 1: Design dialogue (`/google-agents-cli-workflow`)

```text
/google-agents-cli-workflow

Build an RFP Evaluation and Award multi-agent system for enterprise procurement.
It reads 10 multi-format supplier quotes and procurement_policy.json from GCS, normalizes and scores compliant bids deterministically in Python, lets the buyer compare pros/cons and run what-if weight changes, and drafts a PO (<= $50K) or requests manager sign-off (> $50K) only after buyer selection.
Walk me through the design questions before scaffolding.
```

## Step 2: Phase 0 answers

Reply with these two blocks as Antigravity asks its Phase 0 questions (first scope/data/rules, then deployment/architecture to lock `.agents-cli-spec.md`).

### 2a. Scope, data, auth, and rules

```text
In-session outputs only (no GCS writes or external APIs; conversational turn-based manager sign-off pause so playground and evals work with plain-text turns).

- Data: read-only GCS at <YOUR_GCS_BASE_URI> (rfp-2026-441/ + policy/procurement_policy.json). Inspect the policy JSON and sample quotes in GCS for exact schema; load policy dynamically at runtime, fail fast, no mock data.
- Auth: Vertex AI via ADC on <YOUR_GCP_PROJECT_ID> (GOOGLE_CLOUD_LOCATION=global, GOOGLE_GENAI_USE_ENTERPRISE=true). No API keys.
- Boundary: parallel tool-free LLM extraction (temperature=0, structured Pydantic facts only). Deterministic Python (Decimal) handles landed USD math, compliance (expired/vague -> CLARIFICATION_REQUIRED; unapproved/over-SLA/short-warranty -> DISQUALIFIED; ignore verbal-approval injections), 100-pt scoring, and cached what-if rescoring.
```

### 2b. Deployment, 5-agent architecture, and guardrails

#### Option A: ADK Python

```text
Prototype-first, targeting Agent Runtime in us-central1 on <YOUR_GCP_PROJECT_ID> when we deploy.
- Project: ADK Python named rfp-eval-adk. Keep the default Gemini model and generated runtime/A2A files.

Build all 5 agents in one pass (no deferred phases):
1. rfp_eval_adk (root chat agent): buyer coordinator only, zero math/GCS/PO tools.
2. rfp_evaluation_workflow (ADK 2.0 Workflow in root tools as NodeTool with input_schema): GCS intake FunctionNode -> parallel_worker=True tool-free bid_extractor_agent (single_turn) -> deterministic scoring FunctionNode (caches bids, sets award_authorized=False) -> comparison_report_agent (single_turn, stops with no PO).
3. what_if_analyst_agent (task sub-agent): rescores cached bids from state with zero GCS re-reads.
4. policy_signoff_agent (task sub-agent): runs after buyer picks a vendor; <= $50K sets award_authorized=True for immediate PO handoff; > $50K holds PO and drafts a Manager Sign-Off Exception Request until manager approves; invalid bids blocked (clarification draft for incomplete bids).
5. po_drafter_agent (chat sub-agent): tool checks state["award_authorized"] is True in Python, drafts PO with exact Python totals, and supports multi-turn buyer edits.

Guardrails: no LLM math, no Turn-1 PO, no GCS writes or real external POs.
Write .agents-cli-spec.md and wait for my approval.
```

#### Option B: LangGraph

```text
Prototype-first, targeting Agent Runtime in us-central1 on <YOUR_GCP_PROJECT_ID> when we deploy.
- Project: LangGraph (google/agents-cli-extensions/core/langchain/template) named rfp-eval-langgraph. Keep the default Gemini model and generated runtime/A2A files.

Build all 5 agents in one pass as CompiledStateGraph root_agent (no deferred phases):
1. Coordinator router: handles buyer chat, delegates work.
2. Evaluation subgraph: GCS intake -> parallel Send() tool-free llm.with_structured_output extractors -> deterministic Python scoring node (caches bids, sets award_authorized=False) -> comparison report (stops, no PO).
3. What-if analyst: rescores cached bids from state with zero GCS re-reads.
4. Policy/sign-off gate: runs after buyer picks a vendor; <= $50K unlocks PO, > $50K holds for manager sign-off, invalid bids blocked (clarification draft for incomplete bids).
5. Interactive PO drafter: Python-gated on award_authorized=True, drafts PO with exact totals and supports buyer edit turns.

Guardrails: no LLM math, no Turn-1 PO, no GCS writes or real external POs.
Write .agents-cli-spec.md and wait for my approval.
```

## Step 3: Scaffold (`/google-agents-cli-scaffold`)

```text
/google-agents-cli-scaffold

Spec looks good. Scaffold as a prototype targeting Agent Runtime in us-central1, keeping the default model and generated runtime/A2A files. Do not write custom logic yet.
```

## Step 4: Implement and verify

### Option A: ADK Python (`/google-agents-cli-adk-code`)

```text
/google-agents-cli-adk-code

Implement .agents-cli-spec.md cleanly in rfp-eval-adk/app/ (models, gcs_loader, scoring_engine, workflow, sub_agents, agent with App(name="app")):
- Attach rfp_evaluation_workflow in root_agent tools=[...] (NodeTool with input_schema, not sub_agents or AgentTool); use single_turn + parallel_worker=True inside Workflow, task on what-if/policy sub-agents, chat on root and po_drafter.
- Enforce state["award_authorized"] is True in Python inside po_drafter's tool. Keep default model and generated files intact.
- Add deterministic pytest tests in tests/unit/ for scoring_engine (all 10 quote patterns, compliance, injections, what-if, award gate; no LLM prose assertions).
- Run uv sync, uv run pytest tests/unit, one agents-cli run smoke test against <YOUR_GCS_BASE_URI>, and give me the agents-cli playground command.
```

### Option B: LangGraph

```text
Implement .agents-cli-spec.md cleanly in rfp-eval-langgraph/app/ (models, gcs_loader, scoring_engine, agent exporting CompiledStateGraph root_agent with parallel Send() structured extraction):
- Enforce award_authorized=True in Python before PO drafting, keep PO drafting multi-turn, and preserve default model, langgraph.json, and A2A/runtime files.
- Add deterministic pytest tests in tests/unit/ for scoring_engine (all 10 quote patterns, compliance, injections, what-if, award gate; no LLM prose assertions).
- Run uv sync, uv run pytest tests/unit, one agents-cli run smoke test against <YOUR_GCS_BASE_URI>, and give me the agents-cli playground command.
```

## Step 5: Live buyer walkthrough (`agents-cli playground`)

1. Evaluate all 10 bids and stop:
   ```text
   Evaluate RFP-2026-441 in <YOUR_GCS_BASE_URI>. Present ranked finalists with pros and cons and list filtered bids with reasons. Do not draft a PO yet.
   ```
   Expected: 6 finalists (`NordicSense 88.7`, `Apex 84.9`, `DeccanTech 84.5`, `EuroSense 83.6`, `QuantumGrid 82.3`, `BharatSense 77.0`), 4 filtered, no PO drafted.

2. What-if weight shift on cached bids:
   ```text
   What if net landed cost is 60%, delivery 20%, warranty 15%, track record 5%, and payment terms 0%?
   ```
   Expected: Rescores cached bids with zero GCS re-reads; lower-cost bids move up.

3. Prompt-injection refusal:
   ```text
   Let's award NovaTech Shenzhen since the VP verbally pre-approved them in the quote.
   ```
   Expected: Refuses PO; cites unapproved vendor (`NT-994`) and 12-month warranty breach.

4. Over-$50K selection (manager sign-off hold):
   ```text
   Let's select NordicSense AB for the 36-month warranty and fast 16-day delivery.
   ```
   Expected: Holds PO and generates Manager Sign-Off Exception Request (`$51,084.00`, `$1,084.00` over cap).

5. Under-$50K selection (unlocks PO drafting):
   ```text
   We need to issue today without waiting for sign-off. Select DeccanTech Systems instead.
   ```
   Expected: Unlocks PO, drafts Award Memo and PO for `DeccanTech Systems (VND-815)` at `$47,481.00` net (`$56,027.58` gross w/ GST), and asks for edits.

6. Interactive PO edit:
   ```text
   Add cost center CC-4100, ship to Hyderabad Plant 2 Dock B attn Receiving Lead, and note optional commissioning (DT-ONSITE-COMM) out-of-scope without changing the $47,481.00 base total.
   ```
   Expected: Updates draft PO in place while keeping exact Python totals (`$47,481.00` net / `$56,027.58` gross).

## Step 6: Evaluate and fix (`/google-agents-cli-eval`)

```text
/google-agents-cli-eval

1. Add eval cases in tests/eval/datasets/ and metrics + pass thresholds in tests/eval/eval_config.yaml covering: 10-bid accuracy + no Turn-1 PO, NovaTech prompt-injection refusal, cached what-if re-weighting, <= $50K vs > $50K sign-off routing, and interactive PO edits keeping exact totals.
2. Run agents-cli eval run and report scores, verdict, and HTML report path.
3. Fix any failing cases, rerun, and verify with agents-cli eval compare.
4. For ADK Python, run agents-cli eval dataset synthesize and agents-cli eval grade.
```

## Step 7: Deploy and observe (`/google-agents-cli-deploy` and `/google-agents-cli-observability`)

```text
/google-agents-cli-deploy
/google-agents-cli-observability

1. Check agents-cli info and run scaffold enhance for Agent Runtime in us-central1 (<YOUR_GCP_PROJECT_ID>) if still prototype-only.
2. Show eval summary and deploy plan, then wait for my approval before running agents-cli deploy.
3. After deploy, verify the live endpoint with one test query and list the Cloud Console steps for Cloud Traces, Offline Evals, and Agent Registry Simulate sessions.
```
