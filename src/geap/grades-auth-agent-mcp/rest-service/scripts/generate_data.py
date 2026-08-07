#!/usr/bin/env python3
"""Generate the mock grades dataset (seed.json).

Idempotent and safe to re-run — it overwrites the target file. Tweak the
constants below (or pass --out) to reshape the demo data.

Usage:
    python scripts/generate_data.py                 # writes app/data/seed.json
    python scripts/generate_data.py --out /tmp/x.json
    python scripts/generate_data.py --force         # no prompt if file exists
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Make `app` importable so we reuse the single source of truth for grading.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.grading import letter_for  # noqa: E402

# --- Edit this to reshape the demo -----------------------------------------
STUDENTS = [
    {"id": "alice", "name": "Alice Nguyen", "email": "alice@campus.edu", "year": 2},
    {"id": "bob", "name": "Bob Martinez", "email": "bob@campus.edu", "year": 3},
    {"id": "carol", "name": "Carol Diaz", "email": "carol@campus.edu", "year": 1},
]

PROFESSORS = [
    {"id": "dr_reed", "name": "Dr. Evelyn Reed", "email": "reed@campus.edu"},
    {"id": "dr_kapoor", "name": "Dr. Anil Kapoor", "email": "kapoor@campus.edu"},
]

COURSES = [
    {"code": "CHEM-101", "title": "Intro to Chemistry", "professor_id": "dr_reed"},
    {"code": "CHEM-201", "title": "Organic Chemistry", "professor_id": "dr_reed"},
    {"code": "BIO-110", "title": "Intro to Biology", "professor_id": "dr_kapoor"},
]

ENROLLMENTS = [
    ("alice", "CHEM-101"),
    ("alice", "BIO-110"),
    ("bob", "CHEM-101"),
    ("bob", "CHEM-201"),
    ("carol", "BIO-110"),
]

# (student, course, score)
GRADES = [
    ("alice", "CHEM-101", 92),
    ("alice", "BIO-110", 85),
    ("bob", "CHEM-101", 78),
    ("bob", "CHEM-201", 88),
    ("carol", "BIO-110", 95),
]
# ---------------------------------------------------------------------------


def build() -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    grades = [
        {
            "student_id": sid,
            "course_code": code,
            "score": score,
            "letter": letter_for(score),
            "updated_at": now,
            "updated_by": "seed",
        }
        for (sid, code, score) in GRADES
    ]
    return {
        "students": STUDENTS,
        "professors": PROFESSORS,
        "courses": COURSES,
        "enrollments": [{"student_id": s, "course_code": c} for (s, c) in ENROLLMENTS],
        "grades": grades,
    }


def main() -> None:
    default_out = ROOT / "app" / "data" / "seed.json"
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=default_out, help="output path")
    ap.add_argument("--force", action="store_true", help="overwrite without prompting")
    args = ap.parse_args()

    out: Path = args.out
    if out.exists() and not args.force:
        resp = input(f"{out} exists. Overwrite? [y/N] ").strip().lower()
        if resp != "y":
            print("Aborted.")
            return

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        json.dump(build(), fh, indent=2)
        fh.write("\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
