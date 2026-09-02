# Specification: Banking Complaint Resolution Workbench MVP

## 1. Overview
An internal Single-Page Application (SPA) built with **React + Vite** and a **FastAPI + SQLite** backend, featuring an interactive Kanban board designed for bank case handlers, investigators, supervisors, and intake specialists to record, investigate, review, approve, and resolve customer complaints, backed by an immutable audit history and realistic synthetic data.

## 2. Functional Requirements

### 2.1 Role-Based Access & Perspectives
The UI includes a quick Role Selector in the navigation bar to simulate and enforce role-based behaviors:
- **Intake Specialist**: Can create new complaints, view all columns, search/filter cases.
- **Case Handler / Investigator**: Can assign cases to themselves, log investigation findings, select root cause, calculate proposed financial redress, submit cases to supervisor for review, and close approved cases.
- **Supervisor**: Can view all cases, review cases in `Pending Review`, approve or reject with mandatory comments, reassign cases, change priority, and override states.
- **Compliance Auditor**: Read-only view with complete audit trail inspection and timeline review.

### 2.2 Kanban Board Workflow Stages
Six distinct columns representing the complaint lifecycle:
1. `New / Intake`: Complaints recorded by intake specialists.
2. `In Investigation`: Cases actively being investigated by assigned case handlers.
3. `Under Supervisor Review`: Cases with proposed resolution / redress submitted for supervisor review.
4. `Approved`: Cases approved by a supervisor, ready for final customer communication and settlement.
5. `Resolved`: Cases successfully resolved and closed.
6. `Escalated`: High-risk, regulatory, or disputed cases requiring escalated handling.

### 2.3 Complaint Creation (Intake)
- Customer synthetic information: Customer Name, Customer ID, Synthetic Email/Phone, Account / Card Number, Account Type (Checking, Savings, Credit Card, Mortgage, Business Account).
- Complaint metadata: Title, Category (e.g., Unauthorized Transaction, Overdraft Fee Dispute, Delayed Wire Transfer, Incorrect Billing, Poor Branch Service, Loan Servicing Error), Product Type, Severity/Priority (Low, Medium, High, Critical), Channel (Branch, Phone, Online Banking, Mobile App, Written Letter), Disputed Amount ($), Narrative Description.

### 2.4 Case Investigation & Redress Calculation
- View customer summary and synthetic related account info.
- Investigation Notes and Root Cause taxonomy (e.g., Bank System Issue, Operational Error, Policy Dispute, Customer Misunderstanding, Third-Party Fraud).
- Redress calculator: Refund Amount + Goodwill Compensation + Interest Correction = Total Financial Redress ($).
- Action buttons: "Submit for Supervisor Review", "Request More Information", "Escalate".

### 2.5 Supervisor Review & Sign-Off
- Supervisor approval action with optional sign-off note.
- Supervisor rejection action with mandatory rejection reason (moves case back to `In Investigation` with audit note).
- Priority override and re-assignment capability.

### 2.6 Immutable Audit Trail
- Every state transition, assignment change, note creation, redress update, approval, or rejection generates an immutable audit log entry.
- Audit records store: `id`, `complaint_id`, `timestamp`, `actor_role`, `actor_name`, `action_type`, `from_status`, `to_status`, `details_or_notes`.
- Visual chronological timeline displayed inside the case details drawer/modal.

### 2.7 Synthetic Banking Data & Management
- Built-in seeder generating 15-20 diverse synthetic complaints across different banking categories and stages.
- "Reset to Synthetic Data" button to instantly restore clean test state.

## 3. Non-Functional Requirements & Constraints
- **Frontend Framework**: React 18 / 19 with Vite, Lucide icons, Tailwind CSS / modern reactive styling for smooth interactions, drag & drop / instant column moves, modal overlays, and toast feedback.
- **Zero External Integrations**: Fully self-contained local SQLite storage; no external cloud/database credentials required.
- **Synthetic Data Only**: 100% synthetic customer and banking details.
- **Performance & Responsiveness**: Instant local response, fluid reactive transitions, and mobile/desktop responsive design.
- **Testability**: Comprehensive automated tests covering all API endpoints, role permissions, state transitions, and audit trail generation.

## 4. Acceptance Criteria
- [x] Able to view complaints organized into Kanban columns by status in a reactive React + Vite UI.
- [x] Able to switch roles and verify role-specific actions and restrictions.
- [x] Able to create new complaints with synthetic customer and account details.
- [x] Able to assign cases to handlers and move cases through investigation, review, approval, and resolution.
- [x] Supervisor can approve or reject (with required reason) proposed resolutions.
- [x] Every action automatically records an entry in the immutable audit trail visible on the case detail view.
- [x] Synthetic data generator populates initial realistic complaints and can be reset anytime.
