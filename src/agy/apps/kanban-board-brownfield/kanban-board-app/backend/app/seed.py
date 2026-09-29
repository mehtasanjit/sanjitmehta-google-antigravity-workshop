"""Fictional demo data. Due dates are relative to the seed date so one card is always overdue."""

from datetime import date, timedelta

COLUMN_NAMES = ["Backlog", "To Do", "In Progress", "Done"]


def demo_cards(today: date) -> list[dict]:
    """Return demo cards keyed by column name, in display order."""

    def days(offset: int) -> str:
        return (today + timedelta(days=offset)).isoformat()

    return [
        # Backlog
        {"column": "Backlog", "title": "Research dark mode", "priority": "Low",
         "assignee": "Priya", "tags": ["ui", "research"], "due_date": None,
         "description": "Collect examples and accessibility guidance for a dark theme."},
        {"column": "Backlog", "title": "Draft onboarding checklist", "priority": "Medium",
         "assignee": "Marco", "tags": ["docs"], "due_date": days(14),
         "description": "First-week checklist for new team members."},
        {"column": "Backlog", "title": "Evaluate analytics options", "priority": "Low",
         "assignee": "", "tags": ["research"], "due_date": None,
         "description": ""},
        {"column": "Backlog", "title": "Add CSV export", "priority": "Medium",
         "assignee": "", "tags": ["feature"], "due_date": None,
         "description": "Let users download the board as a CSV file."},
        {"column": "Backlog", "title": "Improve empty states", "priority": "Low",
         "assignee": "Sofia", "tags": ["ui"], "due_date": days(21),
         "description": "Friendlier text and hints when a list has no items."},
        {"column": "Backlog", "title": "Plan team offsite", "priority": "Low",
         "assignee": "Marco", "tags": ["team"], "due_date": days(30),
         "description": "Shortlist venues and dates."},
        # To Do
        {"column": "To Do", "title": "Write release notes", "priority": "Medium",
         "assignee": "Aisha", "tags": ["docs", "release"], "due_date": days(5),
         "description": "Summarise user-facing changes for the next release."},
        {"column": "To Do", "title": "Fix login timeout bug", "priority": "High",
         "assignee": "Chen", "tags": ["bug"], "due_date": days(-3),
         "description": "Sessions expire after 5 minutes instead of 30."},
        {"column": "To Do", "title": "Update team calendar", "priority": "Low",
         "assignee": "Marco", "tags": [], "due_date": days(2),
         "description": ""},
        {"column": "To Do", "title": "Add password reset email", "priority": "High",
         "assignee": "Sofia", "tags": ["feature", "security"], "due_date": days(4),
         "description": "Send a one-time reset link that expires after 1 hour."},
        {"column": "To Do", "title": "Review accessibility audit", "priority": "Medium",
         "assignee": "Priya", "tags": ["ui", "accessibility"], "due_date": days(6),
         "description": "Go through the audit findings and file follow-up tasks."},
        {"column": "To Do", "title": "Clean up feature flags", "priority": "Low",
         "assignee": "Chen", "tags": ["tech-debt"], "due_date": None,
         "description": "Remove flags that have been fully rolled out."},
        # In Progress
        {"column": "In Progress", "title": "Redesign settings page", "priority": "High",
         "assignee": "Priya", "tags": ["ui"], "due_date": days(3),
         "description": "Group settings into sections and add inline help."},
        {"column": "In Progress", "title": "Migrate CI pipeline", "priority": "Medium",
         "assignee": "Chen", "tags": ["infra"], "due_date": days(7),
         "description": "Move builds to the new runner pool."},
        {"column": "In Progress", "title": "Customer feedback survey", "priority": "Medium",
         "assignee": "Aisha", "tags": ["research"], "due_date": None,
         "description": "Short survey for beta users."},
        {"column": "In Progress", "title": "Update API documentation", "priority": "Medium",
         "assignee": "Sofia", "tags": ["docs"], "due_date": days(-1),
         "description": "Document the new endpoints and error formats."},
        # Done
        {"column": "Done", "title": "Set up project repository", "priority": "High",
         "assignee": "Chen", "tags": ["infra"], "due_date": days(-10),
         "description": "Repository, branch protection, and README."},
        {"column": "Done", "title": "Choose icon set", "priority": "Low",
         "assignee": "Priya", "tags": ["ui"], "due_date": None,
         "description": ""},
        {"column": "Done", "title": "Kick-off meeting", "priority": "Medium",
         "assignee": "Marco", "tags": ["team"], "due_date": days(-14),
         "description": "Agree goals, roles, and the first milestone."},
        {"column": "Done", "title": "Set up error monitoring", "priority": "High",
         "assignee": "Sofia", "tags": ["infra"], "due_date": days(-5),
         "description": "Send frontend and backend errors to the monitoring tool."},
    ]
