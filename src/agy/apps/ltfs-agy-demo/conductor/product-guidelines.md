# Product Guidelines: Kanban Board Application

## Design System & Aesthetics
- **Visual Style:** Modern, clean, high-contrast dark theme with CSS custom properties (variables) for consistent colors, shadows, and borders.
- **Typography:** System UI font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`) for crisp legibility and fast rendering.
- **Iconography:** Lucide React icons for intuitive visual cues (e.g., priorities, action buttons, search, and filter indicators).

## UX & Interaction Principles
- **Immediate Visual Feedback:** Interactive states for buttons, cards, and modal triggers (hover, active, focus outlines).
- **Modal Interfaces:** Clean backdrop overlays for card creation/editing and column creation without navigating away from the main board context.
- **Non-blocking Data Operations:** State changes update local state and localStorage synchronously without page reloads or layout shifts.
- **Accessibility & Focus:** Ensure modals close on backdrop click or Escape key, and maintain accessible contrast ratios.

## Tone & Microcopy
- **Voice:** Direct, concise, and operational.
- **Button & Field Labels:** Clear action verbs (e.g., "Add Column", "Create Task", "Export Data", "Reset").
- **Empty States:** Friendly, helpful guidance when columns or search results are empty.
