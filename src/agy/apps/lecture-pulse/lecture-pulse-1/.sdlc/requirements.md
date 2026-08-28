# Requirements — Lecture Pulse

Derived from `brief.md`. This is a backend REST API for live lecture engagement:
instructors run polls, quizzes, Q&A, and comprehension pulse checks; students respond
from their own devices; instructors read aggregated results by polling the API.

**Tech stack (fixed):** Python 3.11+, FastAPI, SQLite via SQLAlchemy, Pydantic at the
API boundary, pytest, token-based bearer auth with role claims.

---

## In scope

1. Course and lecture-session management by instructors.
2. Enrollment roster management (add/remove students on a course).
3. Student join of an active session via a join code.
4. Session lifecycle `scheduled → active → ended`, with only `active` accepting responses.
5. Poll creation (single/multiple choice) and quiz creation (choices + correct answer),
   attached to a session.
6. Poll/quiz open and close control; only an open poll/quiz accepts responses.
7. One student response per poll/quiz, with live aggregated results (per-option counts;
   for quizzes, correct-answer rate).
8. Q&A: student posts a question during an active session; participants upvote (one per
   student per question); instructor reads questions ranked by upvotes and moderates
   (`answered` / `dismissed`).
9. Comprehension pulse checks: instructor triggers a 1–5 pulse on an active session;
   student submits one rating per active pulse; instructor reads aggregated sentiment
   (distribution + average).
10. Input validation with clear, structured error responses at the API boundary.
11. Structured logging of requests and key domain actions.
12. Token-based authentication and two-role (instructor/student) authorization.
13. Audit trail for state-changing actions.
14. Automated pytest suite with ≥80% line coverage.

## Out of scope

1. Real-time WebSocket / socket push (clients poll REST for fresh aggregates).
2. Email / SMS / any outbound notification.
3. LMS integrations (Canvas / Blackboard / Moodle SSO or grade sync).
4. Front-end / UI (backend REST API only).
5. Multi-tenant org hierarchy beyond course ownership by an instructor.

---

## Functional requirements per module

### Module: Auth & Identity
- **FR-1** The system issues/accepts bearer tokens carrying a subject (user id) and a
  role claim (`instructor` | `student`).
- **FR-2** Every protected endpoint rejects requests with a missing/invalid/expired token
  with `401 Unauthorized`.
- **FR-3** Instructor-only endpoints reject a valid `student` token with `403 Forbidden`.
- **FR-4** A user record exists for each subject; a token maps to exactly one user + role.

### Module: Courses & Sessions
- **FR-5** An instructor creates a course (name, optional description); the creator becomes
  the course owner.
- **FR-6** An instructor manages a course's roster: add a student to the course, remove a
  student from the course. Only the course owner may modify its roster.
- **FR-7** An instructor creates a lecture session under a course; a session starts in
  `scheduled`. A unique join code is generated per session.
- **FR-8** An instructor transitions a session `scheduled → active → ended`. Illegal
  transitions (e.g. `ended → active`) are rejected with `409 Conflict`.
- **FR-9** A student joins an `active` session by presenting its join code; joining is only
  permitted if the student is enrolled in the parent course. Joining a non-active session
  is rejected.
- **FR-10** List a course's sessions; list a session's roster (participants who joined).
- **FR-11** Only the owning instructor may read raw aggregates and manage a session's
  interactive elements.

### Module: Polls & Quizzes
- **FR-12** An instructor creates a poll (type `single` or `multiple`) with ≥2 options,
  attached to a session. A poll starts `closed`.
- **FR-13** An instructor creates a quiz (options + exactly one correct option) attached to
  a session. A quiz starts `closed`.
- **FR-14** An instructor opens a poll/quiz (`closed → open`) and closes it (`open → closed`).
  Only an `open` poll/quiz accepts responses.
- **FR-15** A joined student submits one response per poll/quiz. For a `single` poll exactly
  one option; for `multiple` one or more options; for a quiz exactly one option.
- **FR-16** A second response from the same student to the same poll/quiz is rejected with a
  clear error (`409 Conflict`).
- **FR-17** The owning instructor reads live aggregated results: per-option selection counts,
  total respondents, and for a quiz the correct-answer rate.
- **FR-18** Submitting a response to a `closed` poll/quiz is rejected (`409 Conflict`).

### Module: Q&A / Question Upvoting
- **FR-19** A joined student posts a question (text) during an `active` session.
- **FR-20** Any participant upvotes a question; a second upvote by the same student on the
  same question is rejected (`409 Conflict`).
- **FR-21** The owning instructor reads a session's questions ranked by upvote count
  (descending).
- **FR-22** The owning instructor marks a question `answered` or `dismissed`.

### Module: Comprehension Pulse Checks
- **FR-23** The owning instructor triggers a pulse check on an `active` session (scale 1–5).
  Triggering a new pulse closes the prior active pulse for that session.
- **FR-24** A joined student submits a single rating (1–5) to the currently active pulse; a
  second rating to the same pulse by the same student is rejected (`409 Conflict`).
- **FR-25** The owning instructor reads aggregated pulse sentiment for the current or a past
  pulse: distribution across 1–5 and the mean rating.

### Module: Cross-cutting
- **FR-26** Malformed request bodies/params are rejected at the boundary (`422`) with a
  structured error object (`{ error: { code, message, details } }`).
- **FR-27** Every state-changing domain action writes an audit-trail entry (actor id, role,
  action, target type + id, timestamp).
- **FR-28** Requests and key domain actions are emitted as structured (JSON) log lines with
  a correlation/request id.

---

## Non-functional requirements

- **NFR-1 (Concurrency):** A single active session handles ~200 concurrent students
  submitting to the same poll/pulse without errors or lost writes. Uniqueness and counting
  must be correct under concurrency (enforced by DB constraints + transactional writes,
  not read-modify-write in app code).
- **NFR-2 (Latency):** Aggregate reads (poll results, pulse sentiment) return within 500ms
  under normal load; aggregation is computed by SQL `GROUP BY`, not per-row Python loops.
- **NFR-3 (Data integrity):** DB-level unique constraints enforce: one response per
  (student, poll), one upvote per (student, question), one rating per (student, pulse).
- **NFR-4 (Validation):** All input validated via Pydantic; enum fields constrained; numeric
  ranges (pulse 1–5) enforced.
- **NFR-5 (Test coverage):** ≥80% line coverage measured by `pytest --cov`.
- **NFR-6 (Observability):** Structured logging; correlation id per request.
- **NFR-7 (Portability):** SQLite file DB; app boots with no external services. SQLite
  configured with `check_same_thread=False` and appropriate connection handling to serve
  concurrent requests.

---

## PII inventory

| Field | Where | Sensitivity | Protection |
|---|---|---|---|
| User id / subject | users, audit, responses | Low (pseudonymous id) | Not exposed beyond owner-scoped reads |
| User display name | users | Medium (identifies a person) | Returned only to authorized callers; never logged in full at INFO |
| User email (if present) | users | Medium | Optional; masked in logs; never in aggregate reads |
| Bearer token | request header | High (credential) | Never logged, never persisted in plaintext; excluded from audit + structured logs |
| Question text | questions | Low–Medium (free text, may contain PII) | Visible to session owner + participants only |
| Response/rating content | responses, pulse_responses | Low | Aggregated for instructor; individual rows owner-scoped |
| Audit actor id | audit_log | Low | Retained for accountability; access restricted |

No passwords are stored (token-based auth with pre-issued/role-claim tokens). No payment or
health data.

---

## Role matrix (role × resource × action)

| Resource | Action | Instructor (owner) | Instructor (non-owner) | Student (joined) | Student (not joined) | Unauth |
|---|---|---|---|---|---|---|
| Course | create | ✅ | ✅ | ❌ | ❌ | ❌ |
| Course roster | add/remove | ✅ | ❌ | ❌ | ❌ | ❌ |
| Session | create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Session | change lifecycle | ✅ | ❌ | ❌ | ❌ | ❌ |
| Session | join (by code) | n/a | n/a | ✅ (if enrolled) | ❌ | ❌ |
| Session roster/sessions | list | ✅ | ❌ | ❌ | ❌ | ❌ |
| Poll/Quiz | create/open/close | ✅ | ❌ | ❌ | ❌ | ❌ |
| Poll/Quiz | submit response | ❌ | ❌ | ✅ (if open) | ❌ | ❌ |
| Poll/Quiz | read aggregate | ✅ | ❌ | ❌ | ❌ | ❌ |
| Question | post | ❌ | ❌ | ✅ | ❌ | ❌ |
| Question | upvote | ✅* | ✅* | ✅ | ❌ | ❌ |
| Question | read ranked | ✅ | ❌ | ❌ | ❌ | ❌ |
| Question | moderate (answer/dismiss) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pulse | trigger | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pulse | submit rating | ❌ | ❌ | ✅ | ❌ | ❌ |
| Pulse | read sentiment | ✅ | ❌ | ❌ | ❌ | ❌ |

\* "Any participant" may upvote; in practice the joined student is the primary upvoter. Upvote
is scoped to session participants. Ownership is checked for all instructor management/read
actions.

---

## Acceptance criteria

1. **Full poll lifecycle:** create session → activate → create + open poll → ≥2 students
   respond → instructor reads a correct live aggregate (counts match submissions) → close
   poll → a further response is rejected with `409`.
2. **Auth enforced:** a student token on any instructor-only endpoint returns `403`; a
   request with no/invalid token returns `401`.
3. **Double-vote rejected:** a second poll response, a second upvote of the same question,
   and a second rating of the same active pulse each return `409` with a structured error.
4. **Quiz correctness rate:** an instructor reading a quiz aggregate sees a correct-answer
   rate matching the fraction of respondents who chose the correct option.
5. **Pulse sentiment:** an instructor reading pulse sentiment sees a 1–5 distribution and a
   mean matching submitted ratings.
6. **Join enforcement:** a non-enrolled student cannot join; a student cannot respond to a
   session they have not joined; joining a `scheduled`/`ended` session is rejected.
7. **Lifecycle guards:** illegal session and poll/quiz transitions return `409`.
8. **Validation:** malformed bodies return `422` with `{ error: { code, message, details } }`.
9. **Tests green + coverage:** the pytest suite passes end to end with ≥80% line coverage.

---

## Open questions for HITL

1. **Token issuance:** The brief says "token-based (bearer) with role claims" but does not
   specify a login/registration flow. Assumption: a lightweight `/auth/token` dev endpoint
   (or seeded tokens) issues signed JWTs with `sub` + `role`; no password store. Confirm
   whether a full registration/login flow is expected (currently out of scope).
2. **Quiz answer visibility:** Assumption: the correct answer is never returned to students,
   only aggregate correct-answer rate to the instructor. Confirm.
3. **Upvoter scope:** Brief says "any participant" upvotes — assumed to mean joined students
   (and the owning instructor). Confirm whether non-owner instructors may upvote.
