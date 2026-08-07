"""Score -> letter-grade conversion, shared by the API and the data generator."""

_BANDS = [
    (93, "A"), (90, "A-"),
    (87, "B+"), (83, "B"), (80, "B-"),
    (77, "C+"), (73, "C"), (70, "C-"),
    (60, "D"),
]


def letter_for(score: float) -> str:
    """Return the letter grade for a numeric score in [0, 100]."""
    for threshold, letter in _BANDS:
        if score >= threshold:
            return letter
    return "F"
