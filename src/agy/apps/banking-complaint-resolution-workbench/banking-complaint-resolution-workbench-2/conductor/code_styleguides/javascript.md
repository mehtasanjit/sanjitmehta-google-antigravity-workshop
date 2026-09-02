# Google JavaScript Style Guide Summary

## 1. Source File & Syntax Basics
- ES6+ JavaScript modules.
- Use `const` by default, `let` when mutated. Never use `var`.
- Use strict equality (`===`, `!==`).
- Clean async/await for asynchronous API requests with try/catch error handling.

## 2. Formatting & Architecture
- Indentation: 2 spaces.
- Clear event-driven state updates for the Kanban board.
- Separation of concerns between API client methods, state store, and UI renderers.
