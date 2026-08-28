# SLA Control Tower Additional Requirements

## Context

The Banking Complaint Resolution Workbench already gives case handlers and supervisors a shared complaint queue, complaint details, workflow actions, SLA deadlines, and an audit history. Supervisors also need a more visible way to identify complaints at risk of missing their target resolution dates and to balance urgent work across case handlers.

The SLA Control Tower extends the existing application with a supervisor-facing operational view. It must make deadline risk and handler workload immediately understandable while keeping all decisions and consequential actions under human control.

## Users

### Supervisors

Supervisors need to:

- see unresolved complaints grouped by SLA risk;
- identify overdue and due-soon complaints quickly;
- understand how active work is distributed across case handlers;
- filter the view to focus on a handler, priority, product, or SLA condition;
- open a complaint without losing the Control Tower context;
- assign or reassign a complaint to a case handler; and
- escalate an at-risk complaint with a recorded reason.

### Case handlers and customer service representatives

Case handlers and customer service representatives may view the SLA Control Tower, but assignment, reassignment, and escalation actions remain restricted to supervisors.

## Required experience

1. The existing `SLA Reports` navigation item opens the SLA Control Tower.
2. The Control Tower shows prominent summary counts for:
   - `Overdue`;
   - `Due within 24 hours`;
   - `Due within 3 days`; and
   - `On Track`.
3. The Control Tower presents unresolved complaints in clearly labelled red, amber, and green SLA-risk groups.
4. Each complaint card shows at least the complaint reference, summary, priority, status, assigned handler, target resolution date, and remaining or overdue time.
5. Risk must be communicated with text and icons or labels in addition to colour.
6. A user can filter the view by handler, priority, product, and SLA condition.
7. A user can clear all active filters and return to the complete Control Tower view.
8. The Control Tower includes a visible workload summary showing the number of active complaints assigned to each case handler.
9. Selecting a complaint opens its existing detail experience and preserves the current Control Tower filters when the user returns.
10. A supervisor can assign an unassigned complaint or reassign an assigned complaint to a predefined case handler.
11. A reassignment clearly identifies the current and proposed handlers and requires confirmation before it is applied.
12. A supervisor can mark an unresolved complaint as escalated by entering a non-empty reason.
13. An escalated complaint displays a prominent `Escalated` indicator in the Control Tower and complaint details.
14. Summary counts, risk groups, workload information, and the affected complaint update after assignment, reassignment, escalation, or resolution without requiring a full page reload.
15. The interface provides clear loading, empty, success, and error states.

## SLA risk rules

SLA risk is calculated from the current time, the complaint target resolution date, and whether the complaint is resolved:

- `Overdue`: unresolved and the target resolution date is earlier than the current time.
- `Due within 24 hours`: unresolved, not overdue, and due no more than 24 hours from the current time.
- `Due within 3 days`: unresolved, due more than 24 hours but no more than 72 hours from the current time.
- `On Track`: unresolved and due more than 72 hours from the current time.
- Resolved complaints are excluded from SLA-risk groups and active-handler workload totals.

Each unresolved complaint must appear in exactly one SLA-risk group. Calculations must be performed consistently by the backend so dashboard counts and complaint groupings cannot disagree.

## Assignment and escalation rules

- Only a predefined supervisor identity can assign, reassign, or escalate a complaint.
- An assignment target must be a predefined user with the case-handler role.
- Reassigning a complaint to its current handler must not create a change or duplicate audit event.
- Assignment and reassignment must not silently alter the complaint's workflow status.
- Escalation is an operational indicator and must not introduce a new complaint workflow status.
- An escalation reason is required and must remain available in the complaint history.
- An escalated complaint remains visibly escalated until the complaint is resolved.
- Resolved complaints cannot be assigned, reassigned, or newly escalated.
- Invalid or unauthorized actions must be rejected by the backend and must not mutate complaint or audit data.

## Audit history

The audit history must record:

- initial assignment;
- reassignment, including the previous and new handler;
- escalation, including the reason; and
- the acting user and timestamp for each action.

Audit entries must be created in the same successful transaction as the corresponding complaint change so that the complaint state and history remain consistent.

## Visual and interaction requirements

- Reuse the existing Banking Complaint Resolution Workbench visual language and responsive layout.
- Use high-visibility red, amber, and green treatments without relying on colour alone.
- Use lightweight native React and CSS presentation for workload bars and risk groups.
- Do not add a charting library solely for this track.
- Preserve the existing complaint dashboard and complaint-detail behavior unless a change is required for the Control Tower integration.
- Keep the view usable with keyboard navigation and provide accessible names for interactive controls.

## Scope constraints

This track does not include:

- email, SMS, push, or other outbound notifications;
- scheduled background escalation jobs;
- jurisdiction-specific or regulatory deadline calculation;
- holiday or business-calendar calculation;
- production authentication or identity integration;
- automatic assignment or workload optimization;
- automated complaint decisions;
- external case-management, CRM, or core-banking integration; or
- real customer or banking data.

All users, customers, complaints, and banking information must remain synthetic.

## Verification expectations

Verification must include:

- unit tests for every SLA-risk boundary and the exclusion of resolved complaints;
- API tests for counts, filtering, assignment, reassignment, escalation, authorization, and invalid actions;
- tests confirming audit entries and complaint changes remain consistent;
- frontend tests for risk grouping, filter behavior, workload display, and supervisor-only actions; and
- a production frontend build or equivalent type-checking verification.

## Success criteria

The additional track is successful when:

- a supervisor can identify overdue and due-soon complaints immediately;
- summary counts and risk groups use the same deterministic SLA rules;
- active workload per case handler is clearly visible;
- filters help a supervisor isolate relevant complaints;
- a supervisor can assign, reassign, and escalate eligible complaints;
- unauthorized and invalid actions are prevented by the backend;
- every assignment, reassignment, and escalation is auditable;
- the Control Tower updates visibly after material actions; and
- the feature uses only synthetic data and remains within the defined scope.
