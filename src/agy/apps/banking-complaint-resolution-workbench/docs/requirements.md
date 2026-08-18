# Banking Complaint Resolution Workbench Requirements

## The need

Bank complaint operations teams need a clear and controlled way to record, investigate, review, and resolve customer complaints. When complaint information is spread across inboxes, spreadsheets, and disconnected systems, cases can be difficult to prioritize, ownership can be unclear, and important decisions may not have a complete audit history.

The Banking Complaint Resolution Workbench is an internal application that gives case handlers and supervisors a shared view of complaint work. It must support timely case handling while ensuring that high-priority complaints receive independent review before they are resolved.

## Users

### Case handlers

Case handlers need to:

- record a new complaint;
- find and review complaints assigned to them;
- investigate a complaint and add notes;
- update the complaint as work progresses;
- record a proposed resolution; and
- submit high-priority resolutions for supervisor approval.

### Supervisors

Supervisors need to:

- see complaint volume, status, ownership, priority, and target dates;
- assign or reassign complaints;
- review proposed resolutions for high-priority complaints;
- approve or reject a proposed resolution; and
- review the history of actions taken on a complaint.

## Complaint information

Each complaint must include:

- a unique complaint reference;
- a synthetic customer reference;
- the banking product involved;
- a complaint category;
- the channel through which the complaint was received;
- a short summary and detailed description;
- a priority of `Low`, `Medium`, or `High`;
- a status;
- the assigned case handler, when assigned;
- the date and time received;
- a target resolution date; and
- resolution details, when a resolution has been proposed or completed.

## Required experience

1. A user can view a work queue containing all complaints.
2. The work queue shows the complaint reference, product, category, priority, status, owner, received date, and target resolution date.
3. A user can search by complaint or customer reference and filter the queue by status, priority, product, and owner.
4. A case handler can create a complaint and receive a unique complaint reference.
5. A supervisor can assign or reassign a complaint to a case handler.
6. A case handler can open a complaint, review its details, and add timestamped investigation notes.
7. The application clearly identifies complaints that have passed their target resolution date without being resolved.
8. A case handler can move a complaint from `Open` to `Investigating`.
9. A case handler can record resolution details for a complaint under investigation.
10. A low- or medium-priority complaint can be resolved by its assigned case handler.
11. A high-priority complaint must be submitted for approval and cannot be resolved directly by its case handler.
12. A supervisor other than the submitting case handler can approve or reject a proposed high-priority resolution.
13. Approval resolves the complaint. Rejection requires a reason and returns the complaint to `Investigating`.
14. A user can view an audit history showing material actions taken on the complaint.
15. A supervisor can see summary counts for open, investigating, pending-approval, overdue, and resolved complaints.

## Workflow rules

- A new complaint begins in `Open` status.
- The supported statuses are `Open`, `Investigating`, `Pending Approval`, and `Resolved`.
- Only the assigned case handler can investigate or propose a resolution for a complaint.
- A complaint must contain resolution details before it can be resolved or submitted for approval.
- Low- and medium-priority complaints move from `Investigating` directly to `Resolved`.
- High-priority complaints move from `Investigating` to `Pending Approval`.
- The person who submitted a proposed resolution must not approve or reject that proposal.
- An approved high-priority complaint moves to `Resolved`.
- A rejected high-priority complaint returns to `Investigating`, and the rejection reason must be retained.
- Resolved complaints remain available for viewing and must not be deleted through the application.
- Complaint creation, assignment changes, priority changes, status changes, resolution submission, approval, rejection, and rejection reasons must be recorded in the audit history with the acting user and timestamp.

## Demo users and data

- The application must use only fictional users, customers, complaints, and banking information.
- The required roles must be demonstrable through predefined synthetic case-handler and supervisor identities.
- Production authentication, identity management, and authorization integration are outside the initial scope.

## Initial scope

The initial version is limited to internal complaint intake and resolution workflow. It does not need to support:

- a customer-facing portal;
- email, SMS, or other outbound notifications;
- document uploads;
- integration with core banking, CRM, regulatory, or case-management systems;
- regulatory submission or jurisdiction-specific deadline calculations;
- automated complaint classification, summarization, decision-making, or response generation;
- production authentication or security certification; or
- the use of real customer or bank data.

## Success criteria

The initial application is successful when:

- a case handler can create, find, investigate, and resolve an eligible complaint;
- a supervisor can assign work and identify overdue or high-priority complaints;
- a high-priority complaint cannot be resolved without independent supervisor approval;
- self-approval of a high-priority resolution is prevented;
- a rejected resolution returns to investigation with its reason preserved;
- the complaint history clearly shows who performed each material action and when; and
- all demonstrated information is synthetic.
