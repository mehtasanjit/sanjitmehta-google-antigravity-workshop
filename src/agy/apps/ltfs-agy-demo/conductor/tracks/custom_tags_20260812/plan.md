# Track Implementation Plan: Custom Tags & Color-Coding for Task Cards

## Phase 1: Data Model & Custom Hook Updates
- [ ] Task: Update data structures and initial data with color-coded tags
  - [ ] Write unit test verifying card objects support tag objects `{ name, color }`
  - [ ] Update `initialData.js` and `useKanban.js` hook to handle tag objects with color properties
  - [ ] Ensure backward compatibility for string-only legacy tags
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Card Modal Tag & Color Picker UI
- [ ] Task: Add inline tag creation and color picker palette to CardModal
  - [ ] Create color palette selector in `CardModal.jsx` (Ocean Blue, Emerald Green, Sunset Orange, Berry Purple, Coral Red, Amber Gold)
  - [ ] Implement tag addition with selected color and removal actions
  - [ ] Add CSS styling in `index.css` for tag creation UI and color palette buttons
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Card Rendering & Dynamic FilterBar Integration
- [ ] Task: Render colored tag badge pills on Kanban Card
  - [ ] Update `Card.jsx` to render badge pills using tag color properties
  - [ ] Add CSS rules for tag badge pill styling in `index.css`
- [ ] Task: Dynamically populate FilterBar dropdown with custom tags
  - [ ] Update `FilterBar.jsx` to extract unique tags and colors across all cards
  - [ ] Verify tag filtering works seamlessly with custom color tags
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
