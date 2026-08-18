# Specification: Banking Complaint Resolution Workbench MVP

## 1. Overview
The Banking Complaint Resolution Workbench is an internal enterprise application designed to streamline the logging, assignment, investigation, and resolution of customer complaints. This MVP establishes the core database structure, API endpoints, role-based workflows (CSR, Case Handler, and Supervisor), a visual details page with a real-time audit history timeline, and interactive dashboard metrics.

To simplify demonstration and testing, user identity is simulated via a role-switcher in the header, and the system is initialized with robust mock data.

## 2. Functional Requirements

### 2.1 User Roles & Interface Perspective
- **Header Switcher**: A dropdown menu in the persistent header allows the user to act as one of the following roles:
  - **Customer Service Representative (CSR)** (e.g., Jane Doe)
  - **Case Handler / Investigator** (e.g., John Smith, Alice Johnson)
  - **Supervisor / Approver** (e.g., Robert Vance)
- **Role-Based Views**:
  - **CSR Perspective**:
    - Can view the dashboard but only see a list of complaints.
    - Can click "Log New Complaint" to open a modal/form to enter complaint details.
    - Cannot edit existing complaints under investigation or approve resolutions.
  - **Case Handler Perspective**:
    - Can view the dashboard with complaints assigned to them (or unassigned).
    - Can open a complaint and click "Claim Case" or "Start Investigation".
    - Can add internal comments to the case timeline.
    - Can submit a "Resolution Proposal" with resolution notes and proposed actions, which transitions the case to "Pending Approval".
  - **Supervisor Perspective**:
    - Can view all complaints and supervisory metrics (e.g., Pending Approval).
    - Can open any case in "Pending Approval" status and perform **Approve & Close** or **Reject (Needs Revision)**.
    - Rejections require mandatory supervisor feedback comments, which transitions the case back to "Needs Revision" status.

### 2.2 Complaint Data Schema
Each complaint contains:
- **id**: String, auto-generated unique ID (e.g., `CRW-2026-0001`).
- **customer_name**: String.
- **account_number**: String.
- **customer_email**: String.
- **customer_phone**: String.
- **title**: String, summary of the dispute.
- **description**: String, detailed complaint narrative.
- **category**: String (Credit Cards, Personal Loans, Mortgages, Savings, Digital Banking).
- **subcategory**: String (Fee Dispute, Unauthorised Charge, Service Delay).
- **disputed_amount**: Float, decimal amount in dispute (optional, can be $0.00).
- **priority**: String (`Low`, `Medium`, `High`, `Critical`).
- **status**: String (`Registered`, `Under Investigation`, `Resolution Proposed`, `Pending Approval`, `Resolved`, `Needs Revision`).
- **sla_deadline**: DateTime, auto-calculated based on priority (Critical: 24h, High: 3d, Medium: 7d, Low: 15d).
- **assigned_to**: String (null or Case Handler name).
- **logged_by**: String (CSR name).
- **resolution_notes**: String (null or text written by Case Handler).
- **supervisor_feedback**: String (null or text written by Supervisor during rejection).

### 2.3 Interactive Dashboard Metrics
- **Active Cases**: Total count of cases in progress.
- **Pending Approval**: Count of cases awaiting supervisor approval.
- **SLA Critical**: Count of active cases with less than 24 hours remaining on their SLA deadline.
- **Resolved Cases**: Total count of resolved cases.

### 2.4 Audit Logging & Visual Timeline
- **Audit Event Schema**:
  - `id`: Integer, auto-incrementing.
  - `complaint_id`: String, matching the complaint.
  - `timestamp`: DateTime.
  - `user_name`: String, the actor who performed the action.
  - `user_role`: String, the role of the actor.
  - `event_type`: String (e.g., Log Complaint, Claim Case, Add Comment, Submit Proposal, Approve Case, Reject Case).
  - `description`: String, human-readable summary of the action.
- **Visual Timeline**: A chronological feed displayed on the complaint details screen showing all audit events and internal comments in a vertical timeline. This ensures 100% audit transparency.

## 3. Tech Stack Integration & Architecture
- **Backend (FastAPI)**:
  - `GET /api/complaints`: List complaints.
  - `GET /api/complaints/{id}`: Get complaint details and its complete audit history.
  - `POST /api/complaints`: Log a new complaint.
  - `POST /api/complaints/{id}/claim`: Claim/assign a case.
  - `POST /api/complaints/{id}/comment`: Add a comment/audit note.
  - `POST /api/complaints/{id}/propose`: Propose resolution.
  - `POST /api/complaints/{id}/approve`: Approve resolution.
  - `POST /api/complaints/{id}/reject`: Reject resolution.
  - `GET /api/dashboard/stats`: Fetch real-time dashboard metrics.
- **Database**: SQLite database file (`complaints.db`) managed via SQLAlchemy models with SQLite transaction safety.
- **Frontend (React)**:
  - Single Page Application with simulated route transitions.
  - Clean Vanilla CSS layout featuring a persistent header (with role switcher), dashboard summary cards, searchable/filterable case table, and split-screen master-detail layout for case investigation.

## 4. Acceptance Criteria
1. **Security & RBAC**: Attempting to approve a case without a Supervisor active in the header must return an HTTP 403 Forbidden error on the API.
2. **Audit Trait Integrity**: Every mutation MUST write a corresponding entry to the audit log table.
3. **SLA Deadlines**: Adding a new case must automatically compute and save the correct SLA datetime based on its priority.
4. **Visual Completeness**: Dashboard metrics must update in real-time.
5. **No Tailwind**: All UI components styled using native Vanilla CSS.
