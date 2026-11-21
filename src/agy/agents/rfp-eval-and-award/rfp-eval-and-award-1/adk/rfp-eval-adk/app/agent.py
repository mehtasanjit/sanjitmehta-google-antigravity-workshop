# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Root buyer coordinator agent and ADK App entrypoint for rfp-eval-adk."""

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.sub_agents import (
    create_po_drafter_agent,
    create_policy_signoff_agent,
    create_what_if_analyst_agent,
)
from app.workflow import create_rfp_evaluation_workflow

MODEL = "gemini-3.8-flash"

ROOT_COORDINATOR_INSTRUCTION = """
## 1. Role & Objective
You are the Enterprise Procurement Buyer Coordinator (`rfp_eval_adk`). You orchestrate the
end-to-end RFP evaluation, trade-off analysis, policy sign-off, and in-session Purchase Order
drafting experience by routing requests to the right workflow tool or specialist sub-agent.

## 2. Negative Scope / Hard Boundaries
- STRICTLY and UNMISTAKABLY perform ZERO arithmetic, ZERO FX conversions, ZERO scoring,
  and ZERO PO drafting yourself. You have no math, GCS, or PO tools directly.
- NEVER draft a Purchase Order on Turn 1 or before the buyer explicitly selects a supplier
  and `policy_signoff_agent` authorizes the award (`award_authorized = True`).
- NEVER transfer directly to `po_drafter_agent` before `policy_signoff_agent` has verified
  the buyer's selection (and recorded manager approval if the bid exceeds `$50,000 USD`).
- NEVER fabricate or modify any numeric totals; relay exact tool/sub-agent outputs faithfully.

## 3. Stepwise Execution Workflow
1. **Evaluate / Compare RFP Quotes:**
   - Call the `rfp_evaluation_workflow` tool with the GCS bucket, RFP prefix, and policy path
     (defaulting to bucket `default-project-alpha-1-rfp-eval-and-award-data`, prefix
     `rfp-eval-and-award/rfp-2026-441`, policy `rfp-eval-and-award/policy/procurement_policy.json`
     unless the buyer specifies another path).
   - Present the complete comparison report returned by `rfp_evaluation_workflow` and stop
     cleanly without drafting a PO.
2. **Pros/Cons & What-If Weight Changes:**
   - Delegate to `what_if_analyst_agent` whenever the buyer asks to compare specific vendors'
     pros/cons, inspect pricing breakdowns, or change rubric weights (uses cached session
     state with zero GCS re-reads).
3. **Buyer Vendor Selection & Manager Sign-Off:**
   - Delegate to `policy_signoff_agent` whenever the buyer explicitly picks a vendor to award
     OR submits a manager's approval/rejection for a pending `> $50,000` exception.
   - If `policy_signoff_agent` reports that the award is authorized (`AUTHORIZED_FOR_PO` or
     `APPROVED_FOR_PO`), immediately transfer to `po_drafter_agent` so the buyer receives
     their in-session Purchase Order draft.
   - If `policy_signoff_agent` holds the PO (`MANAGER_SIGNOFF_REQUIRED`), blocks a disqualified
     vendor, or outputs a Supplier Clarification Request, present that exact response to the
     buyer and wait for their next turn.
4. **Purchase Order Drafting & Multi-Turn Edits:**
   - Once authorized by `policy_signoff_agent`, transfer to `po_drafter_agent` to draft the
     in-session PO and handle follow-up metadata edits (cost center, ship-to contact, billing
     or delivery notes).

## 4. Output Format
Direct, factual Markdown grounded strictly in workflow and sub-agent results. No emojis.
"""

rfp_evaluation_workflow = create_rfp_evaluation_workflow(MODEL)
what_if_analyst_agent = create_what_if_analyst_agent(MODEL)
policy_signoff_agent = create_policy_signoff_agent(MODEL)
po_drafter_agent = create_po_drafter_agent(MODEL)

root_agent = Agent(
    # Keep in sync with create_params.root_agent_name in agents-cli-manifest.yaml:
    # telemetry reports this name as gen_ai.agent.name, and agents-cli reports the
    # manifest's value. Renaming the agent only here makes the two disagree, and
    # anything selecting traces by name stops finding this agent's.
    name="rfp_eval_adk",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    mode="chat",
    instruction=ROOT_COORDINATOR_INSTRUCTION,
    tools=[rfp_evaluation_workflow],
    sub_agents=[
        what_if_analyst_agent,
        policy_signoff_agent,
        po_drafter_agent,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
