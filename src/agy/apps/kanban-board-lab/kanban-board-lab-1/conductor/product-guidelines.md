# Product Guidelines: Kanban Board Lab

## 1. Visual Design & Aesthetic Principles
- **Minimalist Modern UI**: Clean, distraction-free interface emphasizing scannability, content hierarchy, and generous whitespace.
- **Color Palette & Contrast**: Neutral slate/gray baseline with intentional accent colors reserved for priority levels (`High`, `Medium`, `Low`), column WIP limit warnings, and action states.
- **Accessible Contrast**: All text, interactive icons, and border boundaries must meet or exceed WCAG 2.1 AA contrast ratios (at least 4.5:1 for body copy).
- **Theming**: System-adaptive theme with an accessible manual Light / Dark mode toggle. High contrast preserved in both modes.

## 2. Voice, Tone & Messaging
- **Empathetic & Direct**: Explanations are clear, courteous, and free of technical jargon or blame.
- **Actionable Guidance**: When an action is prevented (such as moving a card into a column that has reached its Work-in-Progress limit), the message must explicitly explain *why* the move was blocked and *how* to resolve it (e.g., *"Cannot move card: 'In Progress' column has reached its limit of 3 cards. Complete or move an existing card first."*).
- **Destructive Actions**: Modal confirmations for archiving or resetting the board must clearly name the affected item(s) and consequences before user confirmation.

## 3. Interaction & Motion Principles
- **Tactile Micro-interactions**: Smooth card pickup elevation, responsive drop-indicator targets, and subtle hover highlights provide reassuring physical feedback.
- **Accessibility & Motion Preference**: Strict adherence to `@media (prefers-reduced-motion: reduce)`. When reduced motion is requested, all transitions snap instantly without animated easing.
- **Dual Control Parity**: Every pointer interaction (drag-and-drop, column reorder) must have a first-class, fully accessible keyboard counterpart (e.g., dedicated move buttons / action menus with keyboard shortcuts and visible focus rings).

## 4. Accessibility & Inclusivity Standards
- **Non-Color Dependent Indicators**: Priority levels and overdue statuses must never rely solely on color; they must include descriptive text badges, icons, and ARIA labels.
- **Live Regions (`aria-live`)**: Validation alerts, WIP limit breaches, and card movement confirmations must announce promptly to screen readers.
- **Focus Management**: Dialogs trap focus predictably on open, return focus to the trigger on close, and allow ESC dismissal without state loss.
