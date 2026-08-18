# Product Guidelines: Banking Complaint Resolution Workbench

## 1. Brand Voice & Tone
- **Objective & Objective**: System messages, alerts, and field labels must be professional, factual, and reassuring.
- **Empathetic & Clear**: The language should show a sense of urgency regarding customer issues while keeping communication clean, structured, and easily digestible.
- **Internal Professionalism**: Tone is tailored for internal bank case handlers and compliance supervisors, using standardized industry terminology (e.g., "Resolution Proposal", "Audit Trail", "SLA Deadline").

## 2. Visual Design & Aesthetics
- **Theme**: Secure, trustworthy, and modern corporate banking interface.
- **Colors**:
  - **Primary**: Deep Navy Blue (`#0F2942`) — represents stability, authority, and safety.
  - **Secondary/Secondary**: Slate Gray (`#4A5D6E`) and soft Cool Gray (`#F4F6F8`) for neutral backgrounds.
  - **Accent**: Muted Teal (`#0D9488`) — used for CTAs, active states, and successful resolution indicators.
  - **Alerts**:
    - *Critical/Overdue SLA*: Strong Red (`#DC2626`)
    - *High Priority/Warning*: Deep Amber (`#D97706`)
    - *Medium Priority*: Warm Yellow (`#F59E0B`)
    - *Low Priority/Informational*: Clean Green (`#16A34A`)
- **Typography**: Clean, highly readable system sans-serif font stack (e.g., Inter, system-ui) optimized for data-dense dashboards.
- **Information Density**: Medium-to-high density, appropriate for back-office enterprise software where quick scanning of multiple data points is paramount.

## 3. UX Principles & Interactivity
- **Context Preservation**: Avoid page-navigation transitions wherever possible. Use drawers, modals, or split-screen master-detail layouts so case handlers can edit details without losing track of other case context.
- **SLA Countdown & Alerts**: High-visibility countdown badges for cases with imminent SLA deadlines (e.g., glowing alert headers for < 24 hours remaining).
- **Audit Traceability**: Any status transition or reassignment must prompt for an optional note or comment to keep the audit history fully self-contained.
- **Supervisor Action Confirmation**: Destructive or high-impact actions (like final resolution approval with financial payouts) must require double-confirmation with feedback text.
