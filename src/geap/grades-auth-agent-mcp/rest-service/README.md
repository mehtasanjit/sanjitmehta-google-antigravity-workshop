# Grades REST Service

The **resource server** at the bottom of the on-behalf-of (OBO) auth chain:

```
Agent ──▶ MCP server ──▶ [ Grades REST Service ]   ← you are here
                             validates the forwarded user token
                             enforces per-user authorization
```

It validates a bearer JWT and enforces **deny-by-default** authorization that
combines **scope** (did the user consent to this action?) with **ownership**
(does *this* user own/teach *this* resource?). Every response is filtered to the
caller's identity — that's the OBO guarantee.

## Roles & scopes

| Role | Reads | Writes | Default scopes |
|---|---|---|---|
| `student` | own grades only | – | `grades.read.self` |
| `professor` | grades for courses they teach | grades for courses they teach | `grades.read.course`, `grades.write.course` |
| `admin` | everything | everything | all of the above + `grades.admin` |

## Endpoints

| Method | Path | Rule |
|---|---|---|
| `GET` | `/health` | public (Cloud Run liveness) |
| `GET` | `/me` | any authenticated — echoes identity from token |
| `GET` | `/courses` | any authenticated — list filtered to caller |
| `GET` | `/students/{id}/grades` | self (student) / taught-slice (prof) / any (admin) |
| `GET` | `/courses/{code}/grades` | owning professor / admin |
| `POST` | `/courses/{code}/grades` | owning professor / admin — body `{student_id, score}` |

Interactive docs at `/docs` when running.

## Run locally

```bash
cd rest-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# 1. Generate the mock dataset (safe to re-run; --force to skip the prompt)
python scripts/generate_data.py --force

# 2. Start the API
uvicorn app.main:app --reload --port 8080
```

In another shell:

```bash
# Mint demo tokens (secret/issuer/audience default to the local config)
STUDENT=$(python scripts/generate_token.py alice)
PROF=$(python scripts/generate_token.py dr_reed)

# Alice reads her own grades  -> 200
curl -s -H "Authorization: Bearer $STUDENT" localhost:8080/students/alice/grades | jq

# Alice tries to read Bob's   -> 403
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $STUDENT" \
  localhost:8080/students/bob/grades

# Prof reads their course      -> 200
curl -s -H "Authorization: Bearer $PROF" localhost:8080/courses/CHEM-101/grades | jq

# Prof enters a grade          -> 200, updated_by records the real user
curl -s -X POST -H "Authorization: Bearer $PROF" -H 'Content-Type: application/json' \
  -d '{"student_id":"bob","score":91}' localhost:8080/courses/CHEM-101/grades | jq
```

## Data generation

- `scripts/generate_data.py` writes `app/data/seed.json`. Edit the constants at
  the top (students/professors/courses/enrollments/grades) and re-run to reshape
  the demo. `--force` overwrites without prompting; `--out` targets another path.
- Writes via `POST` mutate the in-memory copy only (non-durable across Cloud Run
  instances) — expected for a demo. Re-run the generator + restart to reset.

## Tests

```bash
pip install -r requirements-dev.txt
pytest            # authn + authz matrix (self-ok, cross-student-403, prof-course, admin)
```

The tests use their own temporary seed and secret (see `tests/conftest.py`), so
they don't depend on `generate_data.py` having run.

## Auth model & Cloud Run

Two independent layers — don't conflate them:

1. **Platform auth (Cloud Run / IAM)** — gates *who can invoke the URL*. We
   deploy `--allow-unauthenticated` **on purpose**: IAM gates a *Google*
   identity, which is not the student/professor identity the OBO chain needs.
2. **App auth (this service)** — validates our JWT and enforces per-user authz.
   **This is the real gate**, so it must fail closed (it does: missing/invalid
   token → 401, missing scope or wrong owner → 403).

> Later hardening: add IAM so only the MCP server's service account can invoke
> this service (defense-in-depth), and/or require Google `--no-allow-unauthenticated`
> between MCP→REST while keeping the user JWT for authorization.

### Auth modes (config-only swap)

- `AUTH_MODE=local` (default) — validates HS256 tokens from `generate_token.py`.
- `AUTH_MODE=gcp` (future) — validate RS256 tokens forwarded by Gemini
  Enterprise via a `JWKS_URL`. Only `app/auth.py`'s decode path + env change.

## Deploy to Cloud Run

```bash
PROJECT_ID=your-project REGION=us-central1 ./deploy.sh
```

For production, move the secret to Secret Manager:
`--set-secrets JWT_SECRET=grades-jwt-secret:latest`.

## Config (env vars)

| Var | Default | Purpose |
|---|---|---|
| `AUTH_MODE` | `local` | `local` (HS256) or `gcp` (JWKS, future) |
| `JWT_SECRET` | `dev-secret-change-me` | HS256 signing/verify key (local mode) |
| `JWT_ISSUER` | `grades-auth-local` | expected `iss` |
| `JWT_AUDIENCE` | `grades-rest` | expected `aud` |
| `JWKS_URL` | – | JWKS endpoint (gcp mode) |
| `DATA_PATH` | `app/data/seed.json` | dataset location |
| `PORT` | `8080` | listen port (Cloud Run sets this) |
