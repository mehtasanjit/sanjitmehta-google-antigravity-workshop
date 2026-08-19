# Technical Specification - Banking Internal Complaint Tracker MVP

## 1. Overview & Objectives
The goal of this track is to bootstrap and build a functional, visually stunning, and interactive Minimum Viable Product (MVP) for the **Banking Internal Complaint Tracker**. 

This application will demonstrate a simplified complaint-resolution lifecycle (New -> Assigned -> In Progress -> Resolved) using a FastAPI backend with SQLite database and a React.js (Vite) frontend.

## 2. Functional Requirements

### 2.1 Backend (FastAPI)
*   **Database Schema:** A SQLite database containing two tables:
    *   `complaints`: Tracks the core complaint data.
    *   `activity_logs`: Tracks a history of state transitions and agent comments for compliance audit.
*   **Database Seeding:** On startup, if the database is empty, seed it with 4 realistic complaints of varying severities.
*   **CRUD Operations:** Endpoints to list all complaints, fetch a single complaint's details, create a new complaint, and record action logs.
*   **State Machine Transitions:** Safe transition endpoints to move a complaint between the valid workflow stages (New -> Assigned -> In Progress -> Resolved).

### 2.2 Frontend (React + Vite)
*   **Dashboard View:** Includes summary cards at the top (e.g., "Total Complaints", "New", "Under Investigation", "Resolved") with modern micro-animations.
*   **Interactive Kanban Board:** Displays four columns corresponding to the workflow stages. Cards will display key complaint metadata (ID, customer name, severity badge, description, date).
*   **Intuitive Card Action Buttons:** Cards will feature context-aware buttons that allow seamless transition of complaints to the next logical stage:
    *   *New* cards feature an **"Assign to Specialist"** button.
    *   *Assigned* cards feature an **"Investigate Case"** button.
    *   *In Progress* cards feature a **"Resolve Complaint"** button.
*   **Create Complaint Modal:** A sliding pane or pop-up modal containing a clean form to register new customer complaints.
*   **Details Pane / Side Drawer:** Clicking any card slides out a side drawer showing detailed account info, full description, and a vertical timeline representing the **Activity Log / Action History**.

## 3. Data Schema & Models

### 3.1 `complaints` Table
*   `id`: INTEGER (Primary Key, Autoincrement)
*   `customer_name`: VARCHAR (Required)
*   `account_number`: VARCHAR (Masked in UI, e.g., `XXXXXX1234`)
*   `account_type`: VARCHAR (e.g., "Checking", "Savings", "Credit Card")
*   `severity`: VARCHAR (Low, Medium, High)
*   `status`: VARCHAR (New, Assigned, In Progress, Resolved)
*   `description`: TEXT (Required)
*   `assigned_to`: VARCHAR (Optional, specialist name)
*   `created_at`: TIMESTAMP (Default current time)
*   `updated_at`: TIMESTAMP (Default current time)

### 3.2 `activity_logs` Table
*   `id`: INTEGER (Primary Key, Autoincrement)
*   `complaint_id`: INTEGER (Foreign Key referencing `complaints.id`)
*   `action`: VARCHAR (e.g., "Created", "Assigned Specialist", "Started Investigation", "Resolved Case")
*   `performed_by`: VARCHAR (e.g., "Intake Agent", "Investigator")
*   `comments`: TEXT (Optional notes)
*   `timestamp`: TIMESTAMP (Default current time)

## 4. API Endpoints
*   `GET /api/complaints`: Returns all complaints.
*   `GET /api/complaints/{id}`: Returns a single complaint's full details and its activity logs.
*   `POST /api/complaints`: Registers a new complaint. Seeds a "Created" entry in `activity_logs`.
*   `POST /api/complaints/{id}/transition`: Transition state of a complaint. Expects `new_status` and optional `comments` and `performed_by`. Automatically inserts an entry in `activity_logs`.

## 5. Visual Guidelines (Charcoal & Mint Theme)
*   The frame and header will use a deep, modern **Charcoal / Slate background** (`#1A1D20`).
*   Cards will use pure white backgrounds (`#FFFFFF`) with generous internal padding, clean rounded borders (`border-radius: 12px`), and soft, premium-feeling drop shadows.
*   **Severity Badges:** Low (Soft Blue), Medium (Amber), High (Coral Red).
*   **Workflow Column Indicators:** Clean header titles with total item badges. Mint green accents (`#10B981`) will be used on action buttons and success state cards.

## 6. Acceptance Criteria
*   The React app builds cleanly with Vite and connects to FastAPI.
*   The FastAPI server connects to a local SQLite file database and seeds 4 realistic complaints on its first start.
*   A user can view the complete complaint dashboard and move any card through the stages (New -> Assigned -> In Progress -> Resolved) using the card action buttons.
*   Every status transition is successfully saved to the database and appears immediately in that complaint's activity timeline log.
*   A user can successfully register a new complaint using the "Register Complaint" form, which instantly populates the "New" column.
*   The application UI is fully responsive and strictly matches the "Modern FinTech (Charcoal & Mint)" visual aesthetic guidelines.

## 7. Out of Scope for MVP
*   Real multi-user Authentication (users will switch roles in a simple UI dropdown instead).
*   External notifications (e.g., sending emails to clients).
*   Document generation or financial payout processing.
