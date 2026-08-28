# Lecture Pulse Backend

A REST API for live lecture engagement: instructors run polls, quizzes, Q&A, and comprehension
"pulse" checks during a lecture, and students respond from their own devices while instructors
watch aggregated results. Clients read fresh aggregates by polling the REST API (no WebSocket
push in this build).

---

## 1. Overview

- **Polls & Quizzes**: Instructors create single/multiple-choice polls, or quizzes with a correct
  answer. Only an *open* poll accepts responses; one response per student. Quiz correct answers are
  never returned to students — only the aggregate correct-answer rate, to the owning instructor.
- **Q&A Upvoting**: Students post questions during an active session; participants upvote (one
  upvote per student per question). Instructors read questions ranked by upvotes and mark them
  `answered`/`dismissed`.
- **Comprehension Pulse**: Instructors trigger a 1–5 pulse; students submit one rating per active
  pulse; instructors read the aggregated distribution + average.
- **Polling architecture**: clients GET the aggregate endpoints to refresh; no server-push channel.

## 2. Tech stack

- Python 3.11 · FastAPI · SQLAlchemy 2.x over SQLite · Pydantic v2 · PyJWT (HS256) · pytest / pytest-cov

## 3. Project layout

```text
src/
├── app/
│   ├── config.py          # pydantic-settings; env parsing + validation
│   ├── db.py              # engine, SessionLocal, Base, get_db, SQLite PRAGMAs (WAL, FK on)
│   ├── security.py        # JWT encode/decode (HS256)
│   ├── logging_config.py  # structured JSON logging
│   ├── errors.py          # AppError hierarchy + exception handlers ({error:{code,message,details}})
│   ├── main.py            # create_app() factory: middleware, routers, handlers, create_all
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic v2 request/response schemas
│   ├── deps/              # DI: auth, role, ownership, membership
│   ├── routers/           # APIRouter per module
│   ├── services/          # domain logic (all SQL lives here)
│   └── middleware/        # request-id + access log
├── tests/                 # pytest unit + integration + concurrency
├── requirements.txt
├── pyproject.toml         # pytest config, coverage gate
├── .env.example           # documented required keys (no values)
└── .env.test              # schema-valid fixture values for tests
```

## 4. Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then set JWT_SECRET to a value of >= 32 chars
```

`JWT_SECRET` is the only boot-required variable (min length 32, no default). Everything else has a
safe default (see `.env.example`). `DATABASE_URL` defaults to `sqlite:///./lecture_pulse.db`.

## 5. Running

From the `src/` directory:

```bash
uvicorn app.main:app --reload
```

- OpenAPI docs: `/docs` · ReDoc: `/redoc` · Health check: `/health`

## 6. Testing

From the `src/` directory:

```bash
cp .env.test .env    # only if you don't already have a .env; supplies schema-valid fixture values
pytest
```

The coverage gate `--cov-fail-under=80` is configured in `pyproject.toml` (`pytest` runs it
automatically). The test suite (`conftest.py` sets required env before importing the app) uses an
in-memory SQLite engine with `get_db` overridden per test; the concurrency test uses a temp-file
WAL database with threads.

## 7. Auth model

Dev endpoint `POST /auth/token` mints an HS256 JWT carrying `sub` + `role` (`instructor` |
`student`) — no password store, no registration flow (dev-grade issuer; a real IdP swaps in behind
the same `Principal` dependency). Pass it as `Authorization: Bearer <token>`. Missing/invalid token
→ `401`; wrong role → `403`.

## 8. Endpoint reference

| Module | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| Auth | POST | `/auth/token` | public |
| Auth | GET | `/auth/me` | any authenticated |
| Courses | POST | `/courses` | instructor |
| Courses | GET | `/courses` | instructor (own) |
| Courses | GET | `/courses/{id}` | course owner |
| Courses | POST | `/courses/{id}/enrollments` | course owner (body: `student_subject`) |
| Courses | DELETE | `/courses/{id}/enrollments/{student_subject}` | course owner |
| Courses | GET | `/courses/{id}/enrollments` | course owner |
| Courses | POST | `/courses/{id}/sessions` | course owner |
| Courses | GET | `/courses/{id}/sessions` | course owner |
| Sessions | GET | `/sessions/{id}` | owner or joined participant (join_code hidden from students) |
| Sessions | POST | `/sessions/{id}/transition` | owner (`scheduled→active→ended`) |
| Sessions | POST | `/sessions/join` | enrolled student (body: `join_code`) |
| Sessions | GET | `/sessions/{id}/participants` | owner |
| Polls | POST | `/sessions/{id}/polls` | owner |
| Polls | POST | `/polls/{id}/open` · `/polls/{id}/close` | owner |
| Polls | POST | `/polls/{id}/responses` | joined student (one per poll) |
| Polls | GET | `/polls/{id}/results` | owner |
| Q&A | POST | `/sessions/{id}/questions` | joined student |
| Q&A | POST | `/questions/{id}/upvotes` | joined student or owning instructor (one per question) |
| Q&A | GET | `/sessions/{id}/questions` | owner (ranked by upvotes) |
| Q&A | POST | `/questions/{id}/moderate` | owner (`answered`/`dismissed`) |
| Pulse | POST | `/sessions/{id}/pulses` | owner (closes prior active pulse) |
| Pulse | POST | `/pulses/{id}/responses` | joined student (one per pulse, rating 1–5) |
| Pulse | GET | `/pulses/{id}/sentiment` | owner |

All non-2xx responses use the envelope `{"error": {"code", "message", "details"}}`.

## 9. Design notes

- **Data integrity**: DB-level UNIQUE constraints enforce one response per (student, poll), one
  upvote per (student, question), one rating per (student, pulse). Violations surface as
  `IntegrityError` and are mapped to `409 Conflict` — no read-then-write race.
- **Aggregations**: poll counts, quiz correct-answer rate, question ranking, and pulse sentiment
  are computed with SQL `GROUP BY` at read time (no denormalized counters).
- **Concurrency**: SQLite runs in WAL mode with `busy_timeout` and `foreign_keys=ON` to absorb
  ~200 concurrent writers on a single active session.
- **Observability**: structured JSON logging with a per-request `X-Request-ID`; bearer tokens and
  PII values are never logged.
- **Quiz secrecy**: option `is_correct` is stripped from every student-facing payload.
