# Technical Specification - Restrict Complaint Registration

## 1. Overview & Objectives
The goal of this track is to restrict the ability to register new complaints exclusively to the **Intake Specialist** role. Currently, any role (including **Investigator**) can access and submit the complaint registration form. This change will enforce role-based access control within the frontend user experience.

## 2. Functional Requirements

### 2.1 Sidebar Navigation Restriction
*   The "Register Complaint" button/menu item in the sidebar must only be visible when the active role is `"Intake Specialist"`.
*   When the active role is `"Investigator"`, the "Register Complaint" button/menu item must be completely removed (hidden) from the DOM.

### 2.2 Role Transition & Auto-Redirect
*   If a user is currently viewing the "Register Complaint" form (view is `'new-complaint'`) and changes their active role to `"Investigator"` using the header dropdown, the application must automatically transition them back to the `"dashboard"` view.
*   Enforce a backup rendering protection: if the `currentView` is `'new-complaint'` but the `activeRole` is not `"Intake Specialist"`, the application should automatically redirect to the dashboard view or refuse to render the form.

### 2.3 Backend Constraints
*   As per design agreements, the backend API endpoint (`POST /api/complaints`) remains public and open, with role-based restriction enforced entirely in the client-side presentation layer.

## 3. Visual Guidelines
*   No visual pollution or disabled placeholders in the sidebar; the navigation menu should seamlessly adjust space when "Register Complaint" is hidden.

## 4. Acceptance Criteria
*   The "Register Complaint" sidebar item is visible ONLY when active role is `"Intake Specialist"`.
*   The "Register Complaint" sidebar item is NOT rendered when active role is `"Investigator"`.
*   Switching the active role to `"Investigator"` while filling out the complaint registration form automatically redirects the user to the Dashboard (`currentView` becomes `'dashboard'`).
*   All Vitest and Jest unit/integration tests run successfully.
*   New unit tests are introduced to explicitly verify these role-based restrictions.

## 5. Out of Scope
*   Backend-enforced role authorization via HTTP headers or JWT tokens.
*   Dynamic database-stored permissions (role boundaries are static for MVP simplicity).
