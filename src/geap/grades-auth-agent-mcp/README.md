# grades-auth-agent-mcp

A complete, runnable demonstration of a **token-based authentication + authorization
"on-behalf-of" (OBO) chain**: an AI agent answers questions on behalf of the
signed-in user, and the user's identity flows through every hop so data access is
enforced per-user.

```
Agent (ADK / Gemini)  ──▶  MCP Server (Cloud Run)  ──▶  REST Service (Cloud Run)
  header_provider injects     forwards the token          validates token +
  the user's JWT per session   verbatim                    enforces per-user authz
```

**Same agent, same tools — different user token → different authorized outcome.**
That's the guarantee: a student sees only their own grades; a professor sees only
the courses they teach; an admin sees everything — and the resource server (REST)
is the authority that decides, based on the forwarded identity.

## Components

| Folder | What it is | Status |
|---|---|---|
| [`rest-service/`](rest-service/) | Grades REST API — the resource server; validates the JWT and enforces deny-by-default authz (scope + ownership) | ✅ deployed |
| [`mcp-server/`](mcp-server/) | FastMCP server (Streamable HTTP) — the OBO hop; forwards the user token to REST, makes no authz decisions | ✅ deployed |
| [`agent/`](agent/) | ADK 2.x `LlmAgent` (Gemini) — injects the user's token into MCP calls via `header_provider` | ✅ built |

Each folder has its own README with details, local-run, tests, and deploy steps.

## Live endpoints

| Service | URL |
|---|---|
| REST | `https://grades-rest-47444200274.us-central1.run.app` |
| MCP  | `https://grades-mcp-47444200274.us-central1.run.app/mcp` |

Project `default-project-alpha-1`, region `us-central1`.

## Roles & scopes

| Role | Reads | Writes | Scopes |
|---|---|---|---|
| `student` | own grades only | – | `grades.read.self` |
| `professor` | courses they teach | courses they teach | `grades.read.course`, `grades.write.course` |
| `admin` | everything | everything | all + `grades.admin` |

Demo identities: `alice`, `bob`, `carol` (students), `dr_reed`, `dr_kapoor`
(professors), `admin`.

---

## How to test it right now

Everything below hits the **live Cloud Run** services — no local servers to start.

### Setup (once per shell)
```bash
PY=/home/user_alpha_sanjitmehta_altostrat/work/python/venvs/venv_1/bin/python
cd /home/user_alpha_sanjitmehta_altostrat/work/sanjitmehta-google-antigravity-workshop/src/geap/grades-auth-agent-mcp
REST=https://grades-rest-47444200274.us-central1.run.app
MCP=https://grades-mcp-47444200274.us-central1.run.app/mcp
```

### 1. Test the REST service (curl — fastest)
```bash
STUDENT=$($PY rest-service/scripts/generate_token.py alice)
PROF=$($PY rest-service/scripts/generate_token.py dr_reed)

curl -s $REST/health                                                       # {"status":"ok"}
curl -s -H "Authorization: Bearer $STUDENT" $REST/students/alice/grades    # 200, her grades
curl -s -H "Authorization: Bearer $STUDENT" $REST/students/bob/grades      # 403
curl -s -H "Authorization: Bearer $PROF"    $REST/courses/CHEM-101/grades   # 200, whole class
```

### 2. Test the MCP server (through the MCP protocol)
```bash
$PY mcp-server/scripts/call_tool.py $MCP "$STUDENT" --list
$PY mcp-server/scripts/call_tool.py $MCP "$STUDENT" get_my_grades
$PY mcp-server/scripts/call_tool.py $MCP "$STUDENT" get_student_grades student_id=bob   # 403 error
$PY mcp-server/scripts/call_tool.py $MCP "$PROF"    get_course_grades course_code=CHEM-101
```

### 3. Test the full agent (LLM + OBO, natural language) — recommended
```bash
cd agent
export GOOGLE_GENAI_USE_VERTEXAI=TRUE GOOGLE_CLOUD_PROJECT=default-project-alpha-1 \
       GOOGLE_CLOUD_LOCATION=us-central1 MODEL=gemini-2.5-flash

$PY run.py --list-tools                                                  # verify wiring (no LLM)
$PY run.py --user alice   --prompt "What are my grades?"
$PY run.py --user alice   --prompt "Look up grades for student id bob"   # polite 403 refusal
$PY run.py --user dr_reed --prompt "Show all grades for CHEM-101"
$PY run.py --user dr_reed --prompt "Record 88 for bob in CHEM-101"
```
Swap `--user` between `alice`, `dr_reed`, `admin` to see the same agent return
different data per identity. Tool calls print as they happen, so you can watch the
OBO hop.

### 4. Interactive chat UI (ADK dev UI)
```bash
cd agent
cp .env.example .env          # already has the Vertex + MCP settings
export USER_JWT=$($PY ../rest-service/scripts/generate_token.py dr_reed)
adk web                       # browser chat; pick the "agent" app
# or terminal chat (run from the grades-auth-agent-mcp/ dir):
adk run agent
```

### Notes
- **Tokens expire after 60 min** — just re-run the `generate_token.py` line
  (or add `--ttl 240` for longer).
- `adk web` needs `node` + a browser; if headless, use `run.py`.
- All Python uses the shared venv at the `PY` path above.

---

## Using it from MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```
- Transport: **Streamable HTTP**
- URL: `https://grades-mcp-47444200274.us-central1.run.app/mcp`
- Authentication → **Bearer Token**: paste a JWT from
  `rest-service/scripts/generate_token.py <user>` (required for tool calls)

CLI form:
```bash
npx @modelcontextprotocol/inspector --cli $MCP --transport http \
  --header "Authorization: Bearer $($PY rest-service/scripts/generate_token.py dr_reed)" \
  --method tools/call --tool-name get_course_grades --tool-arg course_code=CHEM-101
```

---

## Deploy (re-deploy after changes)

```bash
# REST service
cd rest-service && PROJECT_ID=default-project-alpha-1 REGION=us-central1 ./deploy.sh

# MCP server (point it at the REST URL)
cd mcp-server  && PROJECT_ID=default-project-alpha-1 REGION=us-central1 \
  REST_BASE_URL=https://grades-rest-47444200274.us-central1.run.app ./deploy.sh
```

Cloud Run deploy requires these roles on the deployer (see
`rest-service/grant-iam.sh`): `run.admin`, `cloudbuild.builds.editor`,
`artifactregistry.admin`, `storage.admin`, and `iam.serviceAccountUser` on the
runtime service account.

## Auth model (recap)

Two independent layers — don't conflate them:
1. **Platform** (Cloud Run / IAM) — reachability. Deployed `--allow-unauthenticated`
   *on purpose*: IAM gates a *Google* identity, not the per-user identity the OBO
   chain needs.
2. **App** (our JWT) — the real gate. Validated + enforced in the REST service;
   forwarded (never decided) by the MCP server; injected by the agent.

## What's next (optional)

1. **Register the MCP server in the GEAP Agent Registry** and import into a Gemini
   Enterprise app with OAuth, so the platform forwards the real user token
   (dropping manual injection).
2. **Production hardening**: move `JWT_SECRET` to Secret Manager, switch
   `AUTH_MODE=gcp` + JWKS to validate real GE-forwarded tokens, and add an IAM
   invoker guard so only the agent's service account can reach the MCP server.
