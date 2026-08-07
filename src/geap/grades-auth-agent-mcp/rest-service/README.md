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

This README is a build-and-deploy-your-own guide. Nothing here is specific to any
one Google Cloud project; substitute your own values for the `<PLACEHOLDERS>`.

---

## Prerequisites

- **Python 3.12+**
- **Google Cloud SDK** (`gcloud`) authenticated: `gcloud auth login`
- A **GCP project** with billing enabled, and these APIs on:
  ```bash
  gcloud config set project <YOUR_PROJECT_ID>
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
                         artifactregistry.googleapis.com
  ```
- IAM roles for the account that will **deploy** (see [Deploy](#deploy-to-cloud-run)).

## Roles & scopes (the authorization model)

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

## Project layout

```
rest-service/
├── app/
│   ├── main.py       # FastAPI app + routes
│   ├── config.py     # env-driven config (AUTH_MODE, JWT_*, DATA_PATH)
│   ├── auth.py       # token validation → Principal (pluggable: local | gcp)
│   ├── authz.py      # deny-by-default rules (scope + ownership)
│   ├── store.py      # in-memory JSON store + queries/mutations
│   ├── grading.py    # score → letter (shared with the generator)
│   ├── models.py     # Pydantic schemas
│   └── data/seed.json# generated dataset
├── scripts/
│   ├── generate_data.py  # (re)build seed.json
│   └── generate_token.py # mint demo JWTs
├── tests/            # authn + authz matrix
├── Dockerfile
├── deploy.sh         # gcloud run deploy --source
├── grant-iam.sh      # grant a deployer the needed roles
└── requirements*.txt
```

---

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

In another shell (same venv):

```bash
STUDENT=$(python scripts/generate_token.py alice)
PROF=$(python scripts/generate_token.py dr_reed)

# Alice reads her own grades  -> 200
curl -s -H "Authorization: Bearer $STUDENT" localhost:8080/students/alice/grades

# Alice tries to read Bob's   -> 403
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $STUDENT" \
  localhost:8080/students/bob/grades

# Prof enters a grade          -> 200, updated_by records the real user
curl -s -X POST -H "Authorization: Bearer $PROF" -H 'Content-Type: application/json' \
  -d '{"student_id":"bob","score":91}' localhost:8080/courses/CHEM-101/grades
```

## Customize the demo data

`scripts/generate_data.py` writes `app/data/seed.json`. Edit the constants at the
top (students / professors / courses / enrollments / grades) and re-run:

```bash
python scripts/generate_data.py --force        # overwrite in place
python scripts/generate_data.py --out /tmp/x.json
```

Grade writes via `POST` mutate the in-memory copy only (non-durable across Cloud
Run instances) — expected for a demo. Re-run the generator + restart to reset.
Swap `app/store.py` for a real DB later without touching the API or authz layers.

## Tests

```bash
pip install -r requirements-dev.txt
pytest        # authn + authz matrix (self-ok, cross-student-403, prof-course, admin)
```

Tests use their own temporary seed + secret (see `tests/conftest.py`), so they
don't depend on `generate_data.py` having run.

---

## Deploy to Cloud Run

### 1. Grant the deployer the needed roles

A direct `gcloud run deploy --source` build needs these on the **deploying**
account (run by a Project Owner / IAM Admin). Edit and run `grant-iam.sh`, or:

```bash
PROJECT=<YOUR_PROJECT_ID>
MEMBER="user:<YOU>@<YOUR_DOMAIN>"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for ROLE in roles/run.admin roles/cloudbuild.builds.editor \
            roles/artifactregistry.admin roles/storage.admin; do
  gcloud projects add-iam-policy-binding $PROJECT --member="$MEMBER" --role="$ROLE"
done
gcloud iam service-accounts add-iam-policy-binding $RUNTIME_SA \
  --project=$PROJECT --member="$MEMBER" --role="roles/iam.serviceAccountUser"
```

> These are the convenient predefined roles for the one-command path. For a
> locked-down alternative (resource-scoped `writer`/`objectAdmin` + a named
> staging bucket), pre-create the Artifact Registry repo and staging bucket and
> grant the scoped roles instead.

### 2. Deploy

```bash
PROJECT_ID=<YOUR_PROJECT_ID> REGION=<YOUR_REGION> \
JWT_SECRET=<A_STRONG_RANDOM_SECRET> \
./deploy.sh
```

The script runs `gcloud run deploy grades-rest --source . --allow-unauthenticated`
and sets the auth env vars. **Change `JWT_SECRET`** from the default — and for
anything beyond a demo, source it from Secret Manager instead:
`--set-secrets JWT_SECRET=grades-jwt-secret:latest`.

### 3. Get your service URL

```bash
gcloud run services describe grades-rest --project=<YOUR_PROJECT_ID> \
  --region=<YOUR_REGION> --format='value(status.url)'
```

Use that URL when you deploy the MCP server (`REST_BASE_URL`). Mint tokens with
the **same** `JWT_SECRET` you deployed with:

```bash
JWT_SECRET=<SAME_SECRET> python scripts/generate_token.py dr_reed
```

---

## Auth model & Cloud Run

Two independent layers — don't conflate them:

1. **Platform auth (Cloud Run / IAM)** — gates *who can invoke the URL*. We deploy
   `--allow-unauthenticated` **on purpose**: IAM gates a *Google* identity, which
   is not the student/professor identity the OBO chain needs.
2. **App auth (this service)** — validates our JWT and enforces per-user authz.
   **This is the real gate**, so it fails closed (missing/invalid token → 401,
   missing scope or wrong owner → 403).

> Later hardening: add IAM so only the MCP server's service account can invoke
> this service (defense-in-depth) while keeping the user JWT for authorization.

### Auth modes (config-only swap)

- `AUTH_MODE=local` (default) — validates HS256 tokens from `generate_token.py`.
- `AUTH_MODE=gcp` (for Gemini Enterprise) — validate RS256 tokens forwarded by the
  platform via a `JWKS_URL`. Only `app/auth.py`'s decode path + env change; the
  authz layer is unchanged.

## Config (env vars)

| Var | Default | Purpose |
|---|---|---|
| `AUTH_MODE` | `local` | `local` (HS256) or `gcp` (JWKS) |
| `JWT_SECRET` | `dev-secret-change-me` | HS256 signing/verify key (local mode) — **change it** |
| `JWT_ISSUER` | `grades-auth-local` | expected `iss` |
| `JWT_AUDIENCE` | `grades-rest` | expected `aud` |
| `JWKS_URL` | – | JWKS endpoint (gcp mode) |
| `DATA_PATH` | `app/data/seed.json` | dataset location |
| `PORT` | `8080` | listen port (Cloud Run sets this) |
