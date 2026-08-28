# Implementation Plan - Restrict Complaint Registration

## Phase 1: Environment & Test Preparation (TDD Red)
- [x] Task 1.1: Write Role Restriction Unit Tests (Red Phase)
  - [x] Add unit tests in `frontend/src/test/Dashboard.test.tsx` or a new test file to verify that "Register Complaint" button is hidden when active role is `"Investigator"`.
  - [x] Add unit tests to verify that switching role to `"Investigator"` while on `"new-complaint"` view redirects the view to `"dashboard"`.
  - [x] Execute Vitest suite to confirm the new tests fail.
- [x] Task 1.2: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Implementation (TDD Green)
- [x] Task 2.1: Enforce Role Restriction in Frontend (Green Phase)
  - [x] Modify `frontend/src/App.tsx` sidebar navigation to conditionally render the "Register Complaint" menu item only if `activeRole === 'Intake Specialist'`.
  - [x] Modify `frontend/src/App.tsx` role select dropdown's `onChange` event (and/or a `useEffect` hook) to reset `currentView` to `'dashboard'` if active role changes to any value other than `'Intake Specialist'` while on the `'new-complaint'` view.
  - [x] Run Vitest suite to confirm all unit tests pass.
- [x] Task 2.2: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Final Verification & Integration
- [x] Task 3.1: Final Suite Run & Quality Gate
  - [x] Run complete backend test suite using `pytest`.
  - [x] Run complete frontend test suite using `vitest`.
  - [x] Run frontend build (`npm run build`) to ensure type-safety and bundle validity.
- [x] Task 3.2: Phase Verification & Checkpoint (Refer to workflow.md)
