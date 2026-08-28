# Security Review — Lecture Pulse backend

- **Scope:** Full-codebase threat-model pass over `src/` (FastAPI / SQLAlchemy 2.x / SQLite / Pydantic v2 / PyJWT).
- **Reviewer:** Security review agent
- **Date:** 2026-08-24
- **Tests:** 24/24 passing (reported). Deps in shared venv `venv_1`.
- **Disposition:** **SHIP-WITH-FOLLOWUPS** — no critical/exploitable-as-shipped findings for the stated Gate-1 dev posture; one High is the *accepted* dev-token assumption that MUST be closed before any non-dev deployment.

---

## Executive summary

The application is well-structured and shows a security-conscious design. AuthN/AuthZ is
enforced on every route via FastAPI dependencies; ownership and session-membership checks are
consistent and cover the IDOR/horizontal-privilege surface. Quiz correct-answer secrecy is
correctly implemented — `is_correct` is never placed on any response schema. JWT verification is
done correctly (HS256 with an explicit algorithm allowlist, signature + `exp` + `iss` verified,
required claims enforced), the signing secret is sourced from env with a hard `min_length=32`
and no default (boot-fails if absent), and no secrets or bearer tokens are logged or persisted.
All data access uses SQLAlchemy ORM/parameterized queries — no raw SQL string interpolation.
Data-integrity security controls (double-submit prevention, one-active-pulse) are enforced at
the DB layer with unique constraints and a partial unique index, not read-modify-write. Audit
entries are written in the same transaction as each state change. Input validation is enforced
at the boundary by Pydantic and the 500 handler returns a sanitized envelope with no stack
traces.

The dominant residual risk is the **dev token issuer** (`POST /auth/token`), which mints a
signed JWT for any `subject` + `role` with no credential check and is active regardless of
`APP_ENV`. This is the explicitly accepted Gate-1 assumption, so it does not block the current
gate, but it is a complete authentication bypass if this build reaches a shared/production
environment and must be gated. Secondary items are hardening gaps: no `.gitignore` protecting
the committed `.env`, fully unpinned dependencies, no rate limiting, and no security response
headers.

**Severity counts:** Critical 0 · High 1 · Medium 4 · Low 6 · Info/Pass (see passing checks).

---

## Findings

### HIGH

#### H-1 — Credential-less token issuer mints arbitrary subject+role tokens, active in all environments
- **Location:** `src/app/routers/auth.py` (`POST /auth/token`, lines 13–24); `src/app/config.py` (`APP_ENV`, line 16).
- **Issue:** `issue_token` accepts a body with any `subject` and `role ∈ {instructor, student}`
  and returns a validly signed JWT with **no authentication**. Any caller can mint an
  instructor token for any subject and obtain full instructor privileges. The endpoint is
  wired unconditionally in `create_app()` and is **not gated on `APP_ENV`**, so it is present
  even when `APP_ENV=prod`.
- **Amplification (PII/identity spoofing):** `issue_token` calls
  `upsert_user(db, body.subject, body.role, body.display_name, body.email)`
  (`src/app/services/courses.py:8`), which *overwrites* the `display_name`, `email`, and `role`
  of an **existing** user whenever a matching `subject` is supplied. A caller can therefore
  rewrite another user's PII or silently change their role by POSTing to the unauthenticated
  endpoint.
- **Residual-risk assessment:** Accepted for Gate-1 per the stated dev-token assumption — the
  signing key, issuer, expiry, and claim verification around the token are all correct, so the
  *token format* is sound; the weakness is purely the issuance policy. Does **not** block this
  gate.
- **Recommendation (production follow-up, mandatory before non-dev deploy):**
  1. Gate the endpoint behind `APP_ENV in {dev, test}`; return 404/disabled otherwise, or move
     it to a separate dev-only router not mounted in prod.
  2. Replace with a real identity source (IdP/OIDC, or at minimum an authenticated exchange)
     for production; do not let the token endpoint set `role`.
  3. Split identity provisioning from token issuance so the token path cannot overwrite an
     existing user's `email`/`display_name`/`role`; treat `upsert_user` role/PII updates as an
     admin-only operation.

---

### MEDIUM

#### M-1 — No `.gitignore`; `.env` containing `JWT_SECRET` is at risk of being committed
- **Location:** project root / `src/.env` (present), no `.gitignore` anywhere in the app tree.
- **Issue:** `src/.env` exists on disk and holds `JWT_SECRET`. The whole `lecture-pulse-1`
  tree is currently untracked (`git status: ?? ./`) and there is **no `.gitignore`**, so a
  naive `git add .` would commit the live `.env`. Today the value is a fixture identical to
  `.env.test` (`test-secret-0123456789abcdef0123456789`), so current exposure is low, but the
  control that prevents a real secret from being committed is absent.
- **Recommendation:** Add a `.gitignore` with `.env` (and `*.db`, `__pycache__/`, `.pytest_cache/`)
  before any real secret is placed in `.env`. Keep only `.env.example` (already present, values
  blanked — good) and `.env.test` (fixture-only — good) in version control.

#### M-2 — Dependencies are unpinned (supply-chain risk)
- **Location:** `src/requirements.txt`.
- **Issue:** `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `PyJWT`, `pytest`,
  `pytest-cov`, `httpx` are declared with **no version pins** (only `sqlalchemy>=2.0`,
  `pydantic>=2.0` have floors). Builds are non-reproducible and a future compromised/breaking
  release is pulled silently. Installed set at review time is current and clean
  (PyJWT 2.13.0, FastAPI 0.139.0, SQLAlchemy 2.0.52, Pydantic 2.13.4).
- **Note:** Automated CVE scan could not be completed — `pip-audit` is not installed in
  `venv_1` (and `npm audit` is N/A for a Python project). Treat the "no known CVEs" conclusion
  as *not verified by tooling*.
- **Recommendation:** Pin exact versions (or use a lockfile), and add `pip-audit` to CI.

#### M-3 — No rate limiting on the token endpoint (or any route)
- **Location:** `src/app/main.py` (no rate-limit middleware); `src/app/routers/auth.py`.
- **Issue:** No throttling exists. Combined with H-1, `POST /auth/token` can be flooded to mint
  unlimited tokens or to repeatedly overwrite user PII (M-1/H-1). `POST /sessions/join` is also
  unthrottled, allowing join-code guessing (mitigated by the 8-char random code, but bounded
  only by CPU).
- **Recommendation:** Add rate limiting (e.g. `slowapi`/reverse-proxy limits) on `/auth/token`
  and `/sessions/join`.

#### M-4 — Token endpoint allows one user to overwrite another user's PII/role
- **Location:** `src/app/services/courses.py:8` (`upsert_user`), reached from `auth.py:15`.
- **Issue:** See H-1 amplification. Called out separately because the fix is independent of
  disabling the dev issuer: even a legitimately authenticated identity-provisioning flow should
  not let a caller mutate a *different* subject's `email`/`display_name`/`role`.
- **Recommendation:** Scope PII writes to the caller's own subject, or make role/PII mutation an
  owner/admin-guarded operation distinct from token issuance.

---

### LOW

#### L-1 — No security response headers
- **Location:** `src/app/main.py`.
- **Issue:** No middleware sets `X-Content-Type-Options`, `X-Frame-Options`/CSP,
  `Strict-Transport-Security`, `Referrer-Policy`, etc. (the FastAPI equivalent of Helmet). For a
  pure JSON API the risk is limited, but defense-in-depth headers are absent.
- **Recommendation:** Add a small headers middleware or set them at the reverse proxy.

#### L-2 — Audit rows are not correlated to the request id and record no field-level detail
- **Location:** `src/app/models/audit.py`, `src/app/services/audit.py`.
- **Issue:** Audit entries capture actor_subject, actor_role, action, target_type, target_id,
  created_at — this satisfies FR-27. However there is no `request_id` column, so audit rows
  cannot be joined to the structured access log (`request_context.py` emits `request_id` only to
  logs), and no before/after `fields` detail is captured, weakening forensic reconstruction.
- **Recommendation:** Add `request_id` (from `request_id_var`) and an optional `details`/`fields`
  JSON column to `AuditLog`.

#### L-3 — Audit log is append-only by convention only; no read path / tamper protection
- **Location:** `src/app/models/audit.py`, services (`write_audit` only ever `INSERT`s).
- **Issue:** No code updates or deletes audit rows (good), but there is no DB-level guard
  (trigger/permission) enforcing immutability, and no `auditor`-role read endpoint exists (the
  role model is instructor/student only). The trail is write-only and unreviewable in-app, and
  an app-level bug or DB access could mutate it.
- **Recommendation:** If audit review is required, add a read path restricted to an auditor
  principal; consider DB triggers or hash-chaining for tamper-evidence in higher environments.

#### L-4 — JWT algorithm is env-configurable rather than pinned
- **Location:** `src/app/config.py:9` (`JWT_ALGORITHM`), `src/app/security.py:15,22`.
- **Issue:** `decode_token` correctly passes an allowlist (`algorithms=[settings.JWT_ALGORITHM]`),
  so classic alg-confusion (`none`, RS↔HS) is not exploitable at fixed config. But allowing the
  algorithm to be set from env is an unnecessary downgrade lever.
- **Recommendation:** Pin `HS256` as a constant used for both encode and decode; drop the env
  knob (or validate it against an allowlist of one).

#### L-5 — Resource existence disclosed to unauthorized callers via 403-vs-404
- **Location:** `src/app/deps/access.py` (`require_course_owner`, `require_session_owner`, etc.);
  `src/app/routers/sessions.py:34`.
- **Issue:** Non-owners receive 403 for existing resources and 404 for missing ones, allowing
  enumeration of valid course/session/poll ids. Low impact given ids are sequential integers and
  aggregate data is still protected.
- **Recommendation:** Optionally return 404 for both not-found and not-authorized on
  owner-scoped resources.

#### L-6 — Generic 500 handler logs `str(exc)` at ERROR
- **Location:** `src/app/errors.py:89`.
- **Issue:** The response envelope is correctly sanitized (no stack/detail leaked to clients —
  good). The server-side log includes the exception string and traceback; if an exception message
  ever embeds user input/PII it lands in logs. Low risk but worth noting for the PII-in-logs goal.
- **Recommendation:** Keep `exc_info` for traceback but avoid interpolating `str(exc)` where the
  message may contain request data; rely on the request_id for correlation.

---

## PII handling (explicit section)

PII inventory items from `requirements.md` and how they are handled:

| PII item | Stored | Serialization exposure | Log exposure | Assessment |
|---|---|---|---|---|
| Subject / user id | `users`, audit, responses | Owner-scoped reads only; `author_subject`/`student_subject` returned only to session owner (question ranking, participant list) | Present in structured audit rows + access-log `path` only for `/courses/{id}/enrollments/{student_subject}` (an id, not sensitive PII) | OK |
| `display_name` | `users` | Returned only via `/auth/me` for the caller's own subject | Never logged | OK |
| `email` | `users` | **Never serialized on any response schema** (not in `MeResponse`, `ParticipantOut`, or any Out model) | Never logged | OK — but writable for arbitrary subjects via H-1/M-4 |
| Bearer token | request header | Never in any response | Never logged or persisted (verified: no logging of `authorization`/token) | OK |
| Question text | `questions` | Returned only to session owner (ranked list) and echoed to its own author on create | Not logged | OK |
| Response / rating content | `poll_responses`, `pulse_responses` | Only aggregated (GROUP BY) to the owner; no individual-row endpoint | Not logged | OK |
| Audit actor id | `audit_log` | No read endpoint exists | N/A | OK (see L-3) |

- **Quiz correct-answer secrecy:** CONFIRMED. `PollOption.is_correct` exists on the model
  (`models/poll.py:29`) but is **absent from `PollOptionOut`** (`schemas/poll.py:18–22`, only
  `id`/`text`/`position`). `_poll_out` (`routers/polls.py:13`) builds options exclusively from
  `PollOptionOut`. Correct answers surface only as an aggregate `correct_answer_rate` on the
  owner-only results endpoint.
- **Structured-log masking:** Access log (`middleware/request_context.py`) emits
  method/path/status/duration + request_id only — no bodies, no query strings, no headers. No PII
  is written at INFO. JSON formatter copies only explicit `extra` fields, so no accidental record
  attributes carry PII.
- **Residual PII risk:** H-1/M-4 (arbitrary overwrite of `email`/`display_name` via the token
  endpoint) is the only PII-integrity gap; there is no PII *confidentiality* leak in responses or
  logs.

---

## Authorization coverage matrix (route → guard → verified)

| Route | Guard(s) in code | Enforces | Matches role matrix |
|---|---|---|---|
| `POST /auth/token` | none (by design) | dev token issuance | ⚠ H-1 (accepted dev assumption) |
| `GET /auth/me` | `get_current_principal` | authenticated | ✅ |
| `POST /courses` | `require_role('instructor')` | instructor | ✅ |
| `GET /courses` | `require_role('instructor')` | instructor, owner-scoped list | ✅ |
| `GET /courses/{id}` | `require_course_owner` | owner | ✅ |
| `POST /courses/{id}/enrollments` | `require_course_owner` | owner | ✅ |
| `DELETE /courses/{id}/enrollments/{sub}` | `require_course_owner` | owner | ✅ |
| `GET /courses/{id}/enrollments` | `require_course_owner` | owner | ✅ |
| `POST /courses/{id}/sessions` | `require_course_owner` | owner | ✅ |
| `GET /courses/{id}/sessions` | `require_course_owner` | owner | ✅ |
| `POST /sessions/join` | `require_role('student')` + enrollment check in service | enrolled student, session active | ✅ |
| `GET /sessions/{id}` | `get_current_principal` + owner/joined branch; join_code masked for students; else 403 | owner or joined | ✅ |
| `POST /sessions/{id}/transition` | `require_session_owner` | owner | ✅ |
| `GET /sessions/{id}/participants` | `require_session_owner` | owner | ✅ |
| `POST /sessions/{id}/polls` | `require_session_owner` | owner | ✅ |
| `POST /polls/{id}/open` | `require_poll_owner` | owner | ✅ |
| `POST /polls/{id}/close` | `require_poll_owner` | owner | ✅ |
| `POST /polls/{id}/responses` | `require_poll_participant` | joined student; poll open enforced | ✅ |
| `GET /polls/{id}/results` | `require_poll_owner` | owner | ✅ |
| `POST /sessions/{id}/questions` | `require_joined_participant` | joined student; session active | ✅ |
| `POST /questions/{id}/upvotes` | `require_question_participant_or_owner` | owner or joined | ✅ |
| `GET /sessions/{id}/questions` | `require_session_owner` | owner | ✅ |
| `POST /questions/{id}/moderate` | `require_question_owner` | owner | ✅ |
| `POST /sessions/{id}/pulses` | `require_session_owner` | owner; session active | ✅ |
| `POST /pulses/{id}/responses` | `require_pulse_participant` | joined student; pulse active | ✅ |
| `GET /pulses/{id}/sentiment` | `require_pulse_owner` | owner | ✅ |
| `GET /health` | none | liveness only, no data | ✅ |

**IDOR / horizontal-privilege verdict:** No gaps found. Ownership is resolved via
`course.owner_subject` for every instructor management/read action (including nested poll/
question/pulse resources, which re-derive the owning session), and student data access requires
a `Participant` row for the specific session. A student cannot read another session's data
(403), and a non-owner instructor cannot act on resources they do not own (403). `require_role`
checks the exact role string.

---

## Other checklist results

- **JWT verification** (`security.py`): HS256, `algorithms=[...]` allowlist (no alg confusion),
  `issuer` verified, `options={"require": ["exp","iss","sub"]}`, signature + expiry enforced by
  PyJWT. `deps/auth.py` catches all decode errors and returns a generic `401` (no internal
  detail leak). PASS.
- **Secret sourcing** (`config.py`): `JWT_SECRET: str = Field(..., min_length=32)` — required,
  no default, boots-fail if missing or too short. PASS.
- **No committed secrets:** `grep` over `src/app` found no hardcoded api-key/secret/password/
  token assignments. `.env.test` holds fixture values only. PASS (see M-1 for the `.gitignore`
  gap).
- **Injection surface:** No raw SQL with user input. Only `text()` usage is a static partial-
  index predicate (`models/pulse.py:17`) and `PRAGMA` statements (`db.py`); all queries are ORM/
  parameterized. PASS.
- **Error envelope:** `{ error: { code, message, details } }` for AppError/validation; generic
  500 returns `internal_error` with `details: null` and no stack trace to the client. PASS.
- **Input validation:** Pydantic v2 at the boundary — enum `Literal`s, length bounds (prompt,
  option text, question text, title), numeric range (`rating` `ge=1, le=5`), min option count.
  Server-side re-validation of option ids and quiz-single-answer rules in the service. PASS.
- **Data-integrity security controls:** `uq_poll_response`, `uq_pulse_response`, `uq_upvote`,
  `uq_participant` unique constraints + `uq_one_active_pulse` partial unique index enforce
  double-submit and one-active-pulse at the DB layer; services translate `IntegrityError` into
  `409`. `PRAGMA foreign_keys=ON`, `busy_timeout`, WAL configured. Audit written in the same
  transaction as each state change (`get_db` commits once at end of request). PASS.
- **PyJWT usage correctness:** version 2.13.0, algorithm allowlist, required claims — correct.
  PASS (see L-4 for the env-configurable-algorithm hardening nit).

---

## Required fixes before sign-off

Blocking this gate: **none** (the single High is the explicitly accepted Gate-1 dev-token
assumption).

Mandatory before any non-dev / shared deployment:
1. **H-1 / M-4** — Gate or remove `POST /auth/token`; replace with real auth; stop the token
   path from writing arbitrary subjects' PII/role.

Recommended follow-ups (hardening, non-blocking):
2. **M-1** — Add `.gitignore` (ignore `.env`, `*.db`, caches) before any real secret is used.
3. **M-2** — Pin dependency versions / add a lockfile; add `pip-audit` to CI (could not run
   here — tool absent).
4. **M-3** — Add rate limiting on `/auth/token` and `/sessions/join`.
5. **L-1..L-6** — Security headers, audit `request_id`/details, audit immutability + auditor
   read path, pin JWT alg constant, uniform 404 for owner-scoped resources, avoid `str(exc)` in
   500 logs.

## Final risk disposition

**SHIP-WITH-FOLLOWUPS.** The service is safe to run in the intended local/dev Gate-1 context:
authorization is complete and correct, quiz answers and PII are not leaked in responses or logs,
inputs are validated, queries are parameterized, and integrity constraints hold under
concurrency. The one High finding is the sanctioned dev-token issuer and is tracked as a
mandatory production follow-up rather than a current-gate blocker. Medium items are
config/supply-chain hygiene that should be closed promptly.
