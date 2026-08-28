# Project Brief — Lecture Pulse

## One-line summary
A backend REST API for live lecture engagement: instructors run polls, quizzes,
Q&A, and comprehension pulse checks during a lecture, and students respond from
their own devices while instructors watch aggregated results update.

## Business context
Instructors lack a lightweight way to gauge whether a room of students is
following a lecture in real time. Lecture Pulse gives an instructor immediate,
aggregated signal — poll results, quiz scores, upvoted questions, and a
comprehension "pulse" — so they can adjust pace and address confusion while the
lecture is still happening. The two primary user roles are **instructors**, who
create and manage sessions and their interactive elements, and **students**, who
join a session and respond. Clients read fresh aggregates by polling the REST
API (no real-time socket push in this build).

## Scope

### 1. Sessions & Rosters
- Instructor creates a **course** and a **lecture session** under it.
- Instructor manages an **enrollment roster** (add/remove students to a course).
- A student **joins an active session** (via a session join code) to participate.
- Session lifecycle: `scheduled` → `active` → `ended`; only an active session
  accepts student responses.
- List a course's sessions and a session's roster.

### 2. Live Polls & Quizzes
- Instructor creates a **poll** (single/multiple choice) or **quiz** (choices
  with a correct answer) attached to a session.
- Instructor **opens** and **closes** a poll/quiz; only an open poll accepts
  responses.
- Student **submits one response** per poll/quiz.
- Instructor reads **live aggregated results**: per-option counts and, for a
  quiz, the correct-answer rate.

### 3. Q&A / Question Upvoting
- Student **posts a question** during an active session.
- Any participant **upvotes** a question (one upvote per student per question).
- Instructor reads questions **ranked by upvotes**, and can mark a question
  `answered` or `dismissed`.

### 4. Comprehension Pulse Checks
- Instructor **triggers a pulse check** (e.g. a 1–5 "how well do you follow?"
  scale) on an active session.
- Student **submits a pulse rating** (one active pulse response per student).
- Instructor reads the **aggregated pulse sentiment** (distribution + average)
  for the current or a past pulse.

## Cross-cutting requirements
- **Input validation** — validate and reject malformed requests at the API
  boundary with clear, structured error responses.
- **Structured logging** — consistent structured logging of requests and key
  domain actions (session state changes, poll open/close, responses).
- **Authentication & role-based authorization** — two roles, `instructor` and
  `student`. Instructor-only actions (create/manage sessions, polls, pulses;
  read raw aggregates for their own sessions) are rejected for students and for
  unauthenticated callers. Students may only act within sessions they have
  joined.
- **Audit trail** — record who did what and when for state-changing actions
  (session created/opened/ended, poll opened/closed, responses submitted,
  question moderated).

## Tech stack (fixed)
- **Language/runtime:** Python 3.11+
- **Web framework:** FastAPI
- **Storage:** SQLite (via SQLAlchemy)
- **Validation:** Pydantic models at the API boundary
- **Tests:** pytest
- **Auth:** token-based (bearer) with role claims for instructor vs student

## Non-functional
- **Concurrency:** a single active session must handle ~200 students submitting
  responses to the same poll/pulse without errors or lost writes.
- **Latency:** aggregate reads (poll results, pulse sentiment) return within
  500ms under normal load.
- **Data integrity:** a student cannot submit more than one response per
  poll/quiz, more than one upvote per question, or more than one rating per
  active pulse check — enforced at the storage layer.
- **Test coverage:** backend logic covered by automated tests to at least 80%
  of lines.

## Explicitly OUT of scope
- **Real-time WebSocket / socket push** — clients obtain fresh aggregates by
  polling REST endpoints; no server-push channel in this build.
- **Email / SMS notifications** — no outbound notification delivery.
- **LMS integrations** — no Canvas / Blackboard / Moodle SSO or grade sync.

## Acceptance criteria
- **Full poll lifecycle works:** create session → open poll → students respond →
  instructor reads a correct live aggregate → close poll (further responses
  rejected).
- **Auth enforced:** students are blocked from instructor-only actions, and
  unauthenticated requests are rejected.
- **Double-vote rejected:** a second response from the same student to the same
  poll (or a second upvote / second pulse rating) is rejected with a clear
  error.
- **All tests pass:** the generated pytest suite runs green end to end, meeting
  the ≥80% line-coverage target.
