# Product Guidelines: Lecture Pulse

## Brand Identity & Tone
- **Voice & Tone**: Empathetic, supportive, professional, and clear. Avoid jargon or overly playful language that might distract during academic lectures.
- **Student Perception**: Low-pressure, welcoming, and strictly non-judgmental to encourage honest feedback.
- **Lecturer Perception**: Efficient, reliable, and actionable at a quick glance while presenting.

## Visual Design & Aesthetics
- **Theme & Color Palette**:
  - Primary Theme: Sleek dark mode by default with clean light accent options.
  - Accent Colors: High-contrast status indicators for pulse meters:
    - Green / Indigo: "Got It" / Understanding
    - Yellow / Amber: "Slower" / Needs Context
    - Crimson / Coral: "Confused" / Help Needed
  - Modern Glassmorphism: Subtle backdrop blurs, soft borders, and gentle shadows for floating cards and meters.
- **Typography**: Modern sans-serif typography (Inter / Outfit / System UI) with high legibility and clear hierarchy for quick scanning.
- **Micro-interactions**: Subtle CSS animations for live counter increments, pulse updates, and upvote button clicks to convey real-time reactivity without distracting.

## User Experience (UX) & Interaction Principles
- **Student Flow**:
  1. Instant entry via short join code or QR code link.
  2. One-tap sentiment feedback buttons always accessible at the top/bottom of screen.
  3. Simple text box for submitting questions anonymously with instant live confirmation.
  4. One-tap upvote buttons on peer questions.
- **Lecturer Flow**:
  1. One-click session creation generating a distinct 6-character room code and QR display card.
  2. Prominent real-time pulse meter gauge (showing percentages and trend over time).
  3. Dynamic Q&A column automatically sorted by upvotes, with "Mark Answered" and "Dismiss" controls.
  4. Fullscreen / Presenter mode toggle for projecting or placing alongside lecture slides.

## Accessibility & Performance
- **Accessibility (A11y)**: High contrast ratio compliant (WCAG AA), screen-reader friendly ARIA labels, and full keyboard navigation support.
- **Responsive Layout**: Seamless experience on mobile devices (smartphones/tablets for students) and desktop/laptop displays (for lecturers).
- **Performance**: Real-time websocket/event-driven communication with minimal payload sizes to maintain smooth performance even under weak campus Wi-Fi networks.
