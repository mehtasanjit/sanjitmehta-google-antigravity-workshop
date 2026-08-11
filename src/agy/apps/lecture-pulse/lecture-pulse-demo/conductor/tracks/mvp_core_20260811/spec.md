# Specification: Lecture Pulse Core MVP

## Overview
Implement the Core MVP for **Lecture Pulse**, a real-time classroom engagement platform built with Python (FastAPI + Uvicorn + WebSockets) and React + Vite (TypeScript/JavaScript). The MVP empowers lecturers to create live sessions with unique join codes and enables students to anonymously submit real-time comprehension signals ("Slower", "Confused", "Got It") and upvoteable Q&A items during lectures.

## Functional Requirements

### 1. Session Management
- **Lecturer Session Creation**: API endpoint to create a session with Title and Description. Generates a unique 6-character room code (e.g. `LP-392`).
- **Student Frictionless Join**: Page (`/join`) where students enter the room code to join instantly without account creation.

### 2. Live Confusion & Pace Gauge
- **Student Controls**: 3 pulse check buttons ("Slower", "Confused", "Got It").
- **WebSocket Broadcast**: Immediate WebSocket push on pulse button click, updating metrics across all connected clients in real time.

### 3. Anonymous Q&A Queue with Upvoting
- **Question Submission**: Anonymous text input for student questions.
- **Upvote Feed & Sorting**: Live feed automatically ordered by upvote count.
- **Lecturer Moderation**: Lecturer controls to mark questions as answered or dismiss them.

### 4. Lecturer Live Dashboard
- **Real-time Sentiment Gauge**: Visual progress bars/counters for "Got It", "Slower", and "Confused".
- **Top Q&A Feed**: Upvote-sorted question feed with action buttons.
- **Presenter Mode**: High-contrast, distraction-free view toggle for side-by-side display with slides.

## Architecture & Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLite database + in-memory WebSocket connection manager.
- **Frontend**: React + Vite, Tailwind CSS / Modern Vanilla CSS, WebSockets client.

## Acceptance Criteria
- [ ] Session creation generates a valid unique 6-character room code.
- [ ] Students join via room code without login.
- [ ] Student pulse clicks broadcast live metrics to the lecturer dashboard within < 100ms.
- [ ] Submitted questions appear instantly and can be upvoted by other students.
- [ ] Lecturer can mark questions answered or dismiss them.
- [ ] Unit & integration tests pass for API endpoints and WebSocket handlers.
