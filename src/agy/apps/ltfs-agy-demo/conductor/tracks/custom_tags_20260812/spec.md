# Track Specification: Custom Tags & Color-Coding for Task Cards

## Overview
Enhance the Kanban Board task cards by enabling custom tag creation with distinct color palettes, visual tag badges on cards, and dynamic tag filtering in the filter bar.

## Functional Requirements
1. **Custom Tag Creation & Assignment:**
   - Allow users to add custom text tags directly inside the `CardModal` (card creation/editing).
   - Provide a preset color palette selection (e.g., Ocean Blue, Emerald Green, Sunset Orange, Berry Purple, Coral Red, Amber Gold) when creating or editing a tag.
   - Allow removing existing tags from a card.
2. **Visual Tag Badges:**
   - Display colored badge pills on `Card` components on the board.
   - Render tag badge pills in the `CardModal` detail view.
3. **Dynamic Tag Filtering:**
   - Update `FilterBar` to dynamically aggregate all active tags across board cards and populate the tag dropdown menu.
   - Ensure selecting a tag filters visible cards in real time.
4. **Data Persistence:**
   - Preserve custom tag names and assigned color hex codes/identifiers in `localStorage` alongside card data.

## Non-Functional Requirements
- Maintain smooth UI responsiveness without layout shifts when adding/removing tags.
- Ensure text contrast on colored tag badges complies with accessible WCAG ratios.

## Acceptance Criteria
- [ ] Users can create a new tag with a custom label and selected color in `CardModal`.
- [ ] Cards with tags display colored badge pills on the Kanban board.
- [ ] The tag filter dropdown in `FilterBar` dynamically reflects all available custom tags.
- [ ] Selecting a custom tag in `FilterBar` filters the board cards accurately.
- [ ] Tags and assigned colors persist after refreshing the browser page (`localStorage`).

## Out of Scope
- Global tag deletion across all cards from a standalone management modal (tags can be managed per card).
