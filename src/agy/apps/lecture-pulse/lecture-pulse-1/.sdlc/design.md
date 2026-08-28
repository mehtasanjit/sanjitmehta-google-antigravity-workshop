# Design — Lecture Pulse Backend

Implementation-ready architecture for the Lecture Pulse REST API.
Stack: Python 3.11+, FastAPI, SQLAlchemy over SQLite, Pydantic v2 at the boundary,
pytest, HS256 JWT bearer auth with `instructor`/`student` role claims.

This document is the contract the codegen phase instantiates verbatim. It is
opinionated and concrete. No source code appears here — only structure, schemas,
and decisions.

---

## 1. Overview & module boundaries

The app package is `src/app/`. Tests live under `src/tests/`. SQLite file DB by
default; overridable via `DATABASE_URL`.

### 1.1 Package layout

```
src/
  app/
    __init__.py
    main.py                 # FastAPI app factory create_app(); mounts routers, middleware, exception handlers
    config.py               # Settings (pydantic-settings BaseSettings); env parsing + validation
    db.py                   # SQLAlchemy engine, SessionLocal, Base, get_db dependency, WAL/PRAGMA setup
    logging_config.py       # JSON log formatter, logger setup
    security.py             # JWT encode/decode, password-less token minting, secret handling

    models/                 # SQLAlchemy ORM models (one concern per file)
      __init__.py           # imports all models so Base.metadata is complete
      user.py               # User
      course.py             # Course, Enrollment
      session.py            # LectureSession, Participant
      poll.py               # Poll, PollOption, PollResponse, PollResponseOption
      question.py           # Question, QuestionUpvote
      pulse.py              # Pulse, PulseResponse
      audit.py              # AuditLog

    schemas/                # Pydantic v2 models (request/response DTOs)
      __init__.py
      common.py             # ErrorEnvelope, ErrorBody, pagination-free list wrappers
      auth.py
      course.py
      session.py
      poll.py
      question.py
      pulse.py

    deps/                   # FastAPI dependency callables (DI)
      __init__.py
      auth.py               # get_current_principal, require_role(...), Principal dataclass
      access.py             # require_course_owner, require_session_owner, require_joined_participant

    routers/                # APIRouter per module
      __init__.py
      auth.py               # /auth
      courses.py            # /courses (+ nested roster, sessions)
      sessions.py           # /sessions
      polls.py              # /sessions/{id}/polls, /polls/{id}
      questions.py          # /sessions/{id}/questions, /questions/{id}
      pulse.py              # /sessions/{id}/pulses, /pulses/{id}

    services/               # domain logic; pure-ish functions taking a Session
      __init__.py
      audit.py              # write_audit(db, actor, action, target_type, target_id)
      courses.py
      sessions.py
      polls.py
      questions.py
      pulse.py
      aggregation.py        # GROUP BY queries for poll/quiz/pulse aggregates

    middleware/
      __init__.py
      request_context.py    # request-id assignment + structured access log

    errors.py               # AppError hierarchy (Conflict, Forbidden, NotFound, ...) + handlers

  tests/
    conftest.py             # app + db fixtures, TestClient, token factories
    test_auth.py
    test_courses.py
    test_sessions.py
    test_polls.py
    test_questions.py
    test_pulse.py
    test_aggregation.py
    test_concurrency.py     # NFR-1 double-write / uniqueness under threads
```

### 1.2 Layering rules

- **routers** parse/validate (Pydantic), resolve deps (auth, ownership,
  membership), call **services**, serialize responses. No SQL in routers.
- **services** own all DB reads/writes and domain rules; they raise `AppError`
  subclasses, never `HTTPException`.
- **deps** enforce authn/authz and load-and-check target ownership/membership,
  raising `AppError` subclasses.
- **models** are persistence only; **schemas** are the wire boundary only. They
  are never the same class.
- Every state-changing service call writes an audit entry inside the same
  transaction (see §4.6).

---

## 2. Data model (SQLAlchemy)

All tables use an integer surrogate PK `id` (autoincrement) unless noted.
Timestamps are timezone-aware UTC stored as `DateTime`; default `now()` at insert.
Enum-like columns are `String` with a CHECK constraint + validated at the Pydantic
boundary. `ondelete="CASCADE"` on child FKs; foreign keys enforced via
`PRAGMA foreign_keys=ON` (see §5.4).

### 2.1 users
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| subject | String(64) | UNIQUE, NOT NULL — the JWT `sub` |
| role | String(16) | NOT NULL, CHECK in ('instructor','student') |
| display_name | String(200) | NULL |
| email | String(320) | NULL |
| created_at | DateTime | NOT NULL, default now |

Users are created lazily: `/auth/token` upserts a user for `(subject, role)`.
`subject` is the stable identity used in FKs everywhere. **PII:** `display_name`,
`email` (Medium) — never logged in full at INFO; masked in logs. `subject` is a
pseudonymous id (Low).

### 2.2 courses
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| owner_subject | String(64) | FK users.subject, NOT NULL, INDEX |
| name | String(200) | NOT NULL |
| description | String(2000) | NULL |
| created_at | DateTime | NOT NULL |

### 2.3 enrollments  (course roster)
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| course_id | Integer | FK courses.id CASCADE, NOT NULL |
| student_subject | String(64) | FK users.subject, NOT NULL |
| created_at | DateTime | NOT NULL |

**UNIQUE (course_id, student_subject)** — a student is enrolled once per course.
INDEX on `course_id`.

### 2.4 lecture_sessions
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| course_id | Integer | FK courses.id CASCADE, NOT NULL, INDEX |
| title | String(200) | NOT NULL |
| status | String(16) | NOT NULL, default 'scheduled', CHECK in ('scheduled','active','ended') |
| join_code | String(12) | UNIQUE, NOT NULL, INDEX |
| created_at | DateTime | NOT NULL |
| activated_at | DateTime | NULL |
| ended_at | DateTime | NULL |

`join_code` generated as a URL-safe random token (see §5). Ownership is derived
via `course.owner_subject`.

### 2.5 participants  (students who joined a session)
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| session_id | Integer | FK lecture_sessions.id CASCADE, NOT NULL |
| student_subject | String(64) | FK users.subject, NOT NULL |
| joined_at | DateTime | NOT NULL |

**UNIQUE (session_id, student_subject)**. INDEX on `session_id`.

### 2.6 polls  (polls and quizzes; `is_quiz` discriminator)
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| session_id | Integer | FK lecture_sessions.id CASCADE, NOT NULL, INDEX |
| prompt | String(1000) | NOT NULL |
| poll_type | String(16) | NOT NULL, CHECK in ('single','multiple') |
| is_quiz | Boolean | NOT NULL, default False |
| status | String(16) | NOT NULL, default 'closed', CHECK in ('closed','open') |
| created_at | DateTime | NOT NULL |

Quizzes are `poll_type='single'` + `is_quiz=True` with exactly one option flagged
correct (FR-13). Polls have `is_quiz=False`.

### 2.7 poll_options
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| poll_id | Integer | FK polls.id CASCADE, NOT NULL, INDEX |
| text | String(500) | NOT NULL |
| is_correct | Boolean | NOT NULL, default False |
| position | Integer | NOT NULL |

Invariant enforced in service on create: ≥2 options; for a quiz exactly one
`is_correct=True`; for a poll all `is_correct=False`. `is_correct` is **never**
serialized to students (§3.4, ADR-8.2).

### 2.8 poll_responses
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| poll_id | Integer | FK polls.id CASCADE, NOT NULL, INDEX |
| student_subject | String(64) | FK users.subject, NOT NULL |
| created_at | DateTime | NOT NULL |

**UNIQUE (poll_id, student_subject)** — one response per (student, poll)
[NFR-3]. This row is the uniqueness anchor; selected options hang off it.

### 2.9 poll_response_options  (chosen options; supports `multiple`)
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| response_id | Integer | FK poll_responses.id CASCADE, NOT NULL, INDEX |
| option_id | Integer | FK poll_options.id CASCADE, NOT NULL, INDEX |

**UNIQUE (response_id, option_id)**. Counting for aggregates is a GROUP BY over
this table joined to `poll_responses` (§5.1).

### 2.10 questions
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| session_id | Integer | FK lecture_sessions.id CASCADE, NOT NULL, INDEX |
| author_subject | String(64) | FK users.subject, NOT NULL |
| text | String(2000) | NOT NULL |
| status | String(16) | NOT NULL, default 'open', CHECK in ('open','answered','dismissed') |
| created_at | DateTime | NOT NULL |

**PII:** `text` is free text (Low–Medium) — visible to session owner +
participants only; not logged.

### 2.11 question_upvotes
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| question_id | Integer | FK questions.id CASCADE, NOT NULL, INDEX |
| voter_subject | String(64) | FK users.subject, NOT NULL |
| created_at | DateTime | NOT NULL |

**UNIQUE (question_id, voter_subject)** — one upvote per (student, question)
[NFR-3]. Ranking = GROUP BY count over this table (§5.1).

### 2.12 pulses
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| session_id | Integer | FK lecture_sessions.id CASCADE, NOT NULL, INDEX |
| status | String(16) | NOT NULL, default 'active', CHECK in ('active','closed') |
| created_at | DateTime | NOT NULL |
| closed_at | DateTime | NULL |

At most one `active` pulse per session (FR-23): triggering a new pulse closes the
prior active one in the same transaction. Enforced by service logic + a partial
unique index where supported; on SQLite use
`UNIQUE (session_id, status) WHERE status='active'` (partial index, SQLite-
supported) to make the "one active" invariant DB-backed.

### 2.13 pulse_responses
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| pulse_id | Integer | FK pulses.id CASCADE, NOT NULL, INDEX |
| student_subject | String(64) | FK users.subject, NOT NULL |
| rating | Integer | NOT NULL, CHECK rating BETWEEN 1 AND 5 |
| created_at | DateTime | NOT NULL |

**UNIQUE (pulse_id, student_subject)** — one rating per (student, pulse)
[NFR-3].

### 2.14 audit_log
| column | type | constraints |
|---|---|---|
| id | Integer | PK |
| actor_subject | String(64) | NOT NULL, INDEX |
| actor_role | String(16) | NOT NULL |
| action | String(64) | NOT NULL — e.g. 'course.create','session.activate','poll.open','poll.respond','question.moderate','pulse.trigger' |
| target_type | String(32) | NOT NULL — e.g. 'course','session','poll','question','pulse' |
| target_id | Integer | NULL |
| created_at | DateTime | NOT NULL, INDEX |

Append-only. Never stores bearer tokens or full PII payloads (only actor subject +
target ids). INDEX on `(target_type, target_id)` for target-scoped audit reads.

### 2.15 Uniqueness summary (NFR-3 at the DB layer)
- `poll_responses` UNIQUE(poll_id, student_subject)
- `question_upvotes` UNIQUE(question_id, voter_subject)
- `pulse_responses` UNIQUE(pulse_id, student_subject)
- plus enrollment/participant/join_code uniqueness above.

---

## 3. API contract

All routes are prefixed under the app root. All requests/responses are JSON.
Auth column: **none** = no token; **any** = valid token any role; **student** /
**instructor** = role required; **owner** = instructor who owns the target;
**joined** = student who is a participant of the session.

Error envelope for every non-2xx: `{ "error": { "code": string, "message":
string, "details": object|array|null } }` (§4.5). Standard codes per route below.

### 3.1 Auth module (`routers/auth.py`)

**POST `/auth/token`** — auth: none. Dev token issuance (ADR-8.1).
Request:
```json
{ "subject": "u-123", "role": "instructor", "display_name": "Dr. Ada", "email": "ada@x.edu" }
```
`display_name`/`email` optional. `role` enum `instructor|student`.
Response `200`:
```json
{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 3600, "subject": "u-123", "role": "instructor" }
```
Upserts the user record. Errors: `422` invalid body.

**GET `/auth/me`** — auth: any. Returns the principal decoded from the token.
Response `200`: `{ "subject": "u-123", "role": "instructor", "display_name": "Dr. Ada" }`.
Errors: `401`.

### 3.2 Courses module (`routers/courses.py`)

**POST `/courses`** — auth: instructor.
Req: `{ "name": "CS101", "description": "..." }` → `201`
`{ "id": 1, "name": "CS101", "description": "...", "owner_subject": "u-123", "created_at": "..." }`.
Errors: `401`, `403`, `422`.

**GET `/courses`** — auth: instructor. Lists courses owned by the caller. `200`
`{ "items": [Course, ...] }`. Errors: `401`, `403`.

**GET `/courses/{course_id}`** — auth: owner. `200` Course. Errors: `401`,`403`,`404`.

**POST `/courses/{course_id}/enrollments`** — auth: owner (FR-6).
Req: `{ "student_subject": "s-9" }` → `201`
`{ "id": 5, "course_id": 1, "student_subject": "s-9", "created_at": "..." }`.
Errors: `401`,`403`,`404` (course), `409` (already enrolled), `422`.

**DELETE `/courses/{course_id}/enrollments/{student_subject}`** — auth: owner.
`204`. Errors: `401`,`403`,`404` (course or enrollment).

**GET `/courses/{course_id}/enrollments`** — auth: owner. `200`
`{ "items": [Enrollment, ...] }`. Errors: `401`,`403`,`404`.

**POST `/courses/{course_id}/sessions`** — auth: owner (FR-7).
Req: `{ "title": "Lecture 3" }` → `201`
`{ "id": 7, "course_id": 1, "title": "Lecture 3", "status": "scheduled", "join_code": "AB12CD34", "created_at": "..." }`.
Errors: `401`,`403`,`404`,`422`.

**GET `/courses/{course_id}/sessions`** — auth: owner (FR-10). `200`
`{ "items": [Session, ...] }`. Errors: `401`,`403`,`404`.

### 3.3 Sessions module (`routers/sessions.py`)

**GET `/sessions/{session_id}`** — auth: owner OR joined participant. `200`
Session (join_code included only for owner; omitted for students). Errors:
`401`,`403`,`404`.

**POST `/sessions/{session_id}/transition`** — auth: owner (FR-8).
Req: `{ "target": "active" }` (enum `active|ended`). `200` Session.
Errors: `401`,`403`,`404`, `409` illegal transition (e.g. `scheduled→ended`,
`ended→active`, or repeat), `422`.

Legal transitions: `scheduled→active`, `active→ended`. All others `409`.

**POST `/sessions/join`** — auth: student (FR-9).
Req: `{ "join_code": "AB12CD34" }` → `200`
`{ "session_id": 7, "status": "active", "joined_at": "..." }`.
Errors: `401`,`403` (not enrolled in parent course), `404` (bad code),
`409` (session not `active`), `422`. Idempotent re-join returns the existing
participant `200`.

**GET `/sessions/{session_id}/participants`** — auth: owner (FR-10). `200`
`{ "items": [{ "student_subject": "s-9", "joined_at": "..." }, ...] }`.
Errors: `401`,`403`,`404`.

### 3.4 Polls & Quizzes module (`routers/polls.py`)

**POST `/sessions/{session_id}/polls`** — auth: owner (FR-12/FR-13).
Req (poll):
```json
{ "prompt": "Which sort?", "poll_type": "single", "is_quiz": false,
  "options": [ { "text": "quicksort" }, { "text": "bubble" } ] }
```
Req (quiz): `is_quiz: true`, `poll_type: "single"`, exactly one option
`{ "text": "...", "is_correct": true }`.
Validation: ≥2 options; quiz → exactly one `is_correct`; poll → none.
`201` returns poll with options **without** `is_correct` in the response body.
Errors: `401`,`403`,`404`,`422` (bad option set), `409` (session `ended`).

**POST `/polls/{poll_id}/open`** — auth: owner (FR-14). `200` poll.
Errors: `401`,`403`,`404`, `409` (already open, or session not `active`).

**POST `/polls/{poll_id}/close`** — auth: owner. `200` poll.
Errors: `401`,`403`,`404`, `409` (already closed).

**POST `/polls/{poll_id}/responses`** — auth: joined student (FR-15/16/18).
Req: `{ "option_ids": [12] }` (single/quiz → exactly one; multiple → ≥1).
`201` `{ "id": 88, "poll_id": 3, "created_at": "..." }`.
Errors: `401`,`403` (not joined), `404`, `409` (poll `closed`, OR duplicate
response — IntegrityError → 409, ADR-8.4), `422` (wrong option count, option not
in poll). **Correct answer never returned** (ADR-8.2).

**GET `/polls/{poll_id}/results`** — auth: owner (FR-17). `200`:
```json
{ "poll_id": 3, "poll_type": "single", "is_quiz": true, "total_respondents": 42,
  "options": [ { "option_id": 12, "text": "quicksort", "count": 30 },
               { "option_id": 13, "text": "bubble", "count": 12 } ],
  "correct_answer_rate": 0.714 }
```
`correct_answer_rate` present only when `is_quiz=true`; `null`/absent otherwise.
This is the only place correct-option knowledge surfaces, and only to the owner.
Errors: `401`,`403`,`404`.

### 3.5 Q&A module (`routers/questions.py`)

**POST `/sessions/{session_id}/questions`** — auth: joined student (FR-19).
Req: `{ "text": "Can you re-explain step 2?" }` → `201` Question.
Errors: `401`,`403`,`404`, `409` (session not `active`), `422`.

**POST `/questions/{question_id}/upvotes`** — auth: participant scope = joined
student OR owning instructor (FR-20, assumption 3). `201`
`{ "question_id": 5, "upvotes": 4 }`.
Errors: `401`,`403` (not in participant scope), `404`, `409` (already upvoted).

**GET `/sessions/{session_id}/questions`** — auth: owner (FR-21). Ranked by
upvote count desc, then created_at asc. `200`
`{ "items": [ { "id":5, "text":"...", "author_subject":"s-9", "status":"open", "upvotes":4, "created_at":"..." }, ... ] }`.
Errors: `401`,`403`,`404`.

**POST `/questions/{question_id}/moderate`** — auth: owner (FR-22).
Req: `{ "status": "answered" }` (enum `answered|dismissed`). `200` Question.
Errors: `401`,`403`,`404`, `409` (not currently `open`), `422`.

### 3.6 Pulse module (`routers/pulse.py`)

**POST `/sessions/{session_id}/pulses`** — auth: owner (FR-23). Triggers a pulse;
closes any prior active pulse for the session (same txn). `201`
`{ "id": 2, "session_id": 7, "status": "active", "created_at": "..." }`.
Errors: `401`,`403`,`404`, `409` (session not `active`).

**POST `/pulses/{pulse_id}/responses`** — auth: joined student (FR-24).
Req: `{ "rating": 4 }` (int 1–5). `201`
`{ "id": 55, "pulse_id": 2, "created_at": "..." }`.
Errors: `401`,`403`,`404`, `409` (pulse `closed`, OR duplicate rating), `422`
(rating out of 1–5).

**GET `/pulses/{pulse_id}/sentiment`** — auth: owner (FR-25). `200`:
```json
{ "pulse_id": 2, "total": 40, "average": 3.7,
  "distribution": { "1": 2, "2": 3, "3": 8, "4": 15, "5": 12 } }
```
Errors: `401`,`403`,`404`.

### 3.7 Status-code conventions (global)
- `401` missing/invalid/expired token.
- `403` valid token, wrong role, or not owner / not joined / out of participant scope.
- `404` target does not exist (or not visible to caller — no existence leak beyond
  owner scope; non-owner instructor reads return `403` for owned resources they
  can identify, `404` otherwise).
- `409` state/lifecycle conflict and uniqueness violation (double submit).
- `422` Pydantic validation failure (FastAPI default remapped to the error
  envelope, §4.5).

---

## 4. Cross-cutting design

### 4.1 Auth / JWT verification dependency (`deps/auth.py`)
- `Principal` = `{ subject: str, role: str }` dataclass.
- `get_current_principal(authorization: Header)` extracts the `Bearer` token,
  decodes with `security.decode_token` (HS256, `JWT_SECRET`, verifies `exp`,
  `iss`), returns `Principal`. Any failure → `AuthError` → `401`.
- Token payload: `{ "sub", "role", "iss": "lecture-pulse", "iat", "exp" }`.
- Bearer token is **never** logged or persisted (PII inventory / ADR-8.6).

### 4.2 Role-based authorization dependency
- `require_role("instructor")` / `require_role("student")` — a dependency factory
  that wraps `get_current_principal` and raises `ForbiddenError` → `403` on role
  mismatch. Missing token still yields `401` (auth runs first).

### 4.3 Ownership checks (`deps/access.py`)
- `require_course_owner(course_id)` loads the course; `404` if absent; `403` if
  `course.owner_subject != principal.subject`.
- `require_session_owner(session_id)` loads session→course; same rules via
  `course.owner_subject`. Used by all instructor session-scoped routes.
- Poll/question/pulse ownership resolves up to the parent session's course owner.

### 4.4 Session-membership checks
- `require_joined_participant(session_id)` — for student write routes: `404` if
  session absent, `403` if no matching `participants` row. For response routes it
  also asserts the session is `active` where required (else `409`).

### 4.5 Structured error envelope + handlers (`errors.py`)
- `AppError(code, message, http_status, details=None)` base; subclasses:
  `AuthError(401)`, `ForbiddenError(403)`, `NotFoundError(404)`,
  `ConflictError(409)`, `ValidationAppError(422)`.
- Registered exception handlers convert:
  - `AppError` → its status + `{ "error": { code, message, details } }`.
  - FastAPI `RequestValidationError` → `422` with
    `code="validation_error"`, `details` = the pydantic error list (field paths).
  - Uncaught `Exception` → `500` `code="internal_error"`, generic message; full
    traceback logged, never returned.
- `code` values are stable machine strings (e.g. `duplicate_response`,
  `poll_closed`, `illegal_transition`, `not_enrolled`, `not_joined`,
  `forbidden`, `unauthorized`, `not_found`, `validation_error`).

### 4.6 Audit-trail writing (`services/audit.py`)
- `write_audit(db, principal, action, target_type, target_id)` inserts an
  `audit_log` row **within the same transaction** as the state change, so an
  action and its audit entry commit or roll back together (FR-27).
- Every state-changing service function (create/transition/open/close/respond/
  upvote/moderate/trigger/rate) calls it. Read endpoints do not.
- Audit rows carry actor subject + role + action + target; never token or PII body.

### 4.7 Structured JSON logging + request-id middleware (`middleware/request_context.py`, `logging_config.py`)
- Middleware assigns `request_id` (uuid4, or honors inbound `X-Request-ID`),
  stores it in a `contextvar`, adds it to the response header, and emits one
  access log line per request: `{ ts, level, request_id, method, path,
  status, duration_ms, actor_subject? }`.
- JSON formatter emits `{ ts, level, logger, request_id, msg, ...extra }`.
- Key domain actions log at INFO with `extra` fields (action, target_type,
  target_id) — mirroring audit, but no PII values; `display_name`/`email` masked;
  `text` bodies and tokens never logged.
- Log level from `LOG_LEVEL` (§6).

---

## 5. Aggregation & concurrency design

### 5.1 Aggregations via SQL GROUP BY (NFR-2)
All aggregates are single SQL statements; no per-row Python loops.

- **Poll per-option counts:**
  `SELECT o.id, o.text, COUNT(ro.id) FROM poll_options o
   LEFT JOIN poll_response_options ro ON ro.option_id = o.id
   WHERE o.poll_id = :pid GROUP BY o.id, o.text ORDER BY o.position`
  — LEFT JOIN keeps zero-count options.
- **Total respondents:** `SELECT COUNT(*) FROM poll_responses WHERE poll_id=:pid`.
- **Quiz correct-answer rate:** respondents who selected the correct option /
  total respondents:
  `correct = SELECT COUNT(DISTINCT ro.response_id) FROM poll_response_options ro
   JOIN poll_options o ON o.id=ro.option_id
   WHERE o.poll_id=:pid AND o.is_correct=1`
  divided by total respondents; `0.0` when zero respondents. Rounded to 3 dp.
- **Question ranking:** `SELECT q.*, COUNT(u.id) AS upvotes FROM questions q
   LEFT JOIN question_upvotes u ON u.question_id=q.id
   WHERE q.session_id=:sid GROUP BY q.id ORDER BY upvotes DESC, q.created_at ASC`.
- **Pulse sentiment:** `SELECT rating, COUNT(*) FROM pulse_responses
   WHERE pulse_id=:pid GROUP BY rating`; distribution filled for 1–5 (zeros for
   missing), average via `AVG(rating)` (or computed from the distribution), `total`
   via `COUNT(*)`. Average `null`/`0.0` when total is 0.

### 5.2 Concurrency: ~200 concurrent writers (NFR-1)
- Uniqueness is **DB-enforced** (UNIQUE constraints, §2.15). Duplicate submission
  is handled by attempting the INSERT inside a transaction and catching
  `sqlalchemy.exc.IntegrityError`, mapping it to `ConflictError` → `409`
  (ADR-8.4). No read-check-then-write; that race cannot double-insert.
- Counting is done at read time via GROUP BY over committed rows — no counter
  column to contend on, so no lost updates.
- Each response insert is a short transaction: insert the anchor
  (`poll_responses` / `question_upvotes` / `pulse_responses`), then children
  (`poll_response_options`), then the audit row, commit. IntegrityError anywhere
  rolls the whole unit back.

### 5.3 SQLite tuning (NFR-1, NFR-7)
On engine creation (`db.py`), per-connection PRAGMAs via a
`connect`/`begin` event listener:
- `PRAGMA journal_mode=WAL;` — concurrent readers alongside a writer.
- `PRAGMA synchronous=NORMAL;` — durability adequate for this workload, faster
  under WAL.
- `PRAGMA foreign_keys=ON;` — enforce FKs/cascades.
- `PRAGMA busy_timeout=5000;` — writers wait rather than immediately erroring on
  the single-writer lock, absorbing the ~200-writer burst.

### 5.4 Connection handling
- Engine created with `connect_args={"check_same_thread": False}` (NFR-7) and a
  `StaticPool` for in-memory test DBs; default pooling for file DBs.
- `get_db` dependency yields a `SessionLocal`, commits on success, rolls back on
  exception, always closes. One session per request.

---

## 6. Configuration / environment

Loaded by `config.py` using `pydantic-settings` `BaseSettings`; validation runs
at import/boot and fails fast on violation. Codegen produces `.env.example` (keys
only, no values) and `.env.test` (schema-valid fixture values) from this table.

| Var | Purpose | Format / constraint | Required at boot | Test fixture value |
|---|---|---|---|---|
| `JWT_SECRET` | HS256 signing secret for dev tokens | string, **min length 32 chars**; non-empty | **Yes** | 32+ char literal (e.g. `test-secret-0123456789abcdef0123`) |
| `JWT_ALGORITHM` | JWT signing algorithm | enum, only `HS256` accepted | No (default `HS256`) | `HS256` |
| `JWT_EXPIRES_SECONDS` | Access-token TTL | int, 60–86400 | No (default `3600`) | `3600` |
| `JWT_ISSUER` | `iss` claim, validated on decode | non-empty string | No (default `lecture-pulse`) | `lecture-pulse` |
| `DATABASE_URL` | SQLAlchemy DB URL | must start with `sqlite:///` or `sqlite+pysqlite:///`; URL scheme validated | No (default `sqlite:///./lecture_pulse.db`) | `sqlite:///:memory:` or temp-file path |
| `LOG_LEVEL` | Root log level | enum `DEBUG\|INFO\|WARNING\|ERROR\|CRITICAL` | No (default `INFO`) | `WARNING` |
| `LOG_JSON` | Toggle JSON vs plain logs | bool (`true`/`false`) | No (default `true`) | `false` |
| `JOIN_CODE_LENGTH` | Chars in generated join code | int, 6–12 | No (default `8`) | `8` |
| `APP_ENV` | Environment label (affects nothing security-critical) | enum `dev\|test\|prod` | No (default `dev`) | `test` |

Notes:
- No third-party API keys, OAuth secrets, or external service creds exist — the
  app boots with **no external services** (NFR-7). Therefore no variable needs
  the "optional-at-boot, mocked in tests" treatment; every var above is either
  defaulted or satisfiable by a literal fixture, so `.env.test` is always
  achievable.
- `JWT_SECRET` is the only var with no safe default; boot fails if missing/short.
  Validation: `min_length=32`. This is the one key `.env.example` must document as
  required and `.env.test` must supply.
- `config.py` exposes a cached `get_settings()` (lru_cache) so tests can override
  via monkeypatching env before first access, and `create_app()` reads settings
  through it.

---

## 7. Testing strategy

### 7.1 Split
- **Unit tests** — services + aggregation math + security (token
  encode/decode/expiry) + error mapping, using an in-memory SQLite session
  directly. No HTTP layer.
- **Integration tests** — full request path via FastAPI `TestClient`: auth,
  roles, ownership, lifecycle guards, uniqueness/409, validation/422, and the
  aggregate read shapes.

### 7.2 Fixtures (`conftest.py`)
- `engine` fixture: SQLite in-memory (`sqlite:///:memory:`) with `StaticPool` +
  `check_same_thread=False`, or a temp-file DB for the concurrency test.
  `Base.metadata.create_all` per test session; schema rebuilt per test for
  isolation.
- `db` fixture: a session bound to a transaction rolled back after each test.
- `client` fixture: `TestClient(create_app())` with `get_db` overridden to the
  test session.
- Token factories: `instructor_token(subject)` and `student_token(subject)` mint
  real HS256 tokens with the test `JWT_SECRET`, exercising the real auth path.
- Env: `.env.test` supplies `JWT_SECRET` and friends; `get_settings.cache_clear()`
  in a fixture so overrides take effect.

### 7.3 Mapping to acceptance criteria
- **AC-1 poll lifecycle** — `test_polls.py`: create/activate session, create+open
  poll, ≥2 student responses, assert `results` counts, close, assert `409` on
  further response.
- **AC-2 auth** — `test_auth.py`: student token on instructor route → `403`;
  no/invalid token → `401`; every module has one representative role-guard test.
- **AC-3 double submit** — `test_polls.py`/`test_questions.py`/`test_pulse.py`:
  second response / second upvote / second rating each → `409` with envelope.
- **AC-4 quiz rate** — `test_aggregation.py`: mixed correct/incorrect responses;
  assert `correct_answer_rate` equals correct/total.
- **AC-5 pulse sentiment** — `test_aggregation.py`: assert distribution + mean.
- **AC-6 join enforcement** — `test_sessions.py`: non-enrolled join → `403`;
  respond without joining → `403`; join scheduled/ended → `409`.
- **AC-7 lifecycle guards** — illegal session + poll transitions → `409`.
- **AC-8 validation** — malformed bodies → `422` with `{error:{code,message,
  details}}`.
- **AC-9 concurrency + coverage** — `test_concurrency.py`: N threads submit the
  same (poll, student) and to the same poll from distinct students; assert exactly
  one duplicate rejected and counts correct. `pytest --cov=app --cov-fail-under=80`
  gates the ≥80% target (NFR-5).

---

## 8. Key ADR-style decisions

### ADR-8.1 — Dev token endpoint, HS256, no password store
**Context:** Brief requires bearer tokens with role claims; no login/registration
flow is in scope (open question 1). **Decision:** `POST /auth/token` mints a
signed HS256 JWT carrying `sub` + `role` from the request body and upserts a
`users` row; verification uses a shared `JWT_SECRET`. **Consequences:** Trivial to
seed test principals; no credential storage; clearly a dev-grade issuer — a real
IdP swaps in behind the same `Principal` dependency without touching routers.

### ADR-8.2 — Quiz correct answer never leaves the server for students
**Context:** Assumption 2 — students must not learn the correct option.
**Decision:** `is_correct` is stripped from all poll/quiz response payloads;
correctness surfaces only as `correct_answer_rate` in the owner-only `/results`.
**Consequences:** Two response schemas for options (with/without `is_correct`);
tests assert absence of `is_correct` in student-facing bodies.

### ADR-8.3 — SQLite WAL + busy_timeout for ~200 concurrent writers
**Context:** NFR-1/NFR-7 — 200 concurrent submitters, no external DB.
**Decision:** WAL journal mode, `synchronous=NORMAL`, `busy_timeout=5000`,
`check_same_thread=False`. **Consequences:** Concurrent reads never block the
single writer; write bursts queue on the lock rather than error; adequate for a
single-process app. Horizontal scaling would require moving off SQLite — out of
scope.

### ADR-8.4 — IntegrityError → 409, not pre-check
**Context:** NFR-3 uniqueness under concurrency; read-then-write races.
**Decision:** Rely on DB UNIQUE constraints; attempt the insert in a txn and map
`IntegrityError` to `ConflictError`/`409`. **Consequences:** Correct under
concurrency with no lock-and-check; the duplicate path is a normal, tested branch;
error `code` distinguishes `duplicate_response`/`duplicate_upvote`/
`duplicate_rating`.

### ADR-8.5 — Read-time GROUP BY aggregation, no counter columns
**Context:** NFR-2 latency + correctness under concurrency. **Decision:** Compute
all aggregates with SQL `GROUP BY` at read time over committed rows; no
denormalized counters. **Consequences:** No write contention on counters, no lost
updates; aggregates are always consistent with stored responses; small indexed
tables keep reads well under 500ms.

### ADR-8.6 — Structured JSON logging + request id; strict PII exclusion
**Context:** FR-26/27/28, NFR-6, PII inventory. **Decision:** Request-id
middleware + JSON formatter; audit rows written in the same txn as state changes;
tokens never logged/persisted, `display_name`/`email` masked, free-text bodies
never logged. **Consequences:** Every request correlatable end to end; audit and
action are atomic; log output is safe to ship to aggregation.

### ADR-8.7 — Polling over WebSockets
**Context:** Brief explicitly excludes socket push. **Decision:** Clients GET the
aggregate endpoints to refresh; no server-push channel. **Consequences:** Simpler
stateless request/response model; fits the SQLite + single-process design; live
feel is a client polling-interval concern, not a backend one.

### ADR-8.8 — Unified polls table for polls and quizzes
**Context:** Polls and quizzes share structure (prompt + options + responses),
differing only by a correct answer. **Decision:** One `polls` table with an
`is_quiz` flag and `is_correct` on options. **Consequences:** One set of
response/aggregation code paths; quiz-only logic (correct-answer rate, single
correct option validation) branches on `is_quiz`; fewer tables and endpoints.
