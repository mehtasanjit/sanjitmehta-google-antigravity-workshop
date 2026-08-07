"""In-memory data store backed by a JSON seed file.

Loaded once at startup. Writes mutate the in-memory copy only (non-durable across
Cloud Run instances) — fine for a demo. Swap this module for a real DB later
without touching the API or authz layers.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from .grading import letter_for


class NotFound(Exception):
    """Raised when a requested entity does not exist."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Store:
    def __init__(self, data: dict):
        self.students = {s["id"]: s for s in data.get("students", [])}
        self.professors = {p["id"]: p for p in data.get("professors", [])}
        self.courses = {c["code"]: c for c in data.get("courses", [])}
        # enrollments: set of (student_id, course_code)
        self.enrollments = {
            (e["student_id"], e["course_code"]) for e in data.get("enrollments", [])
        }
        # grades keyed by (student_id, course_code)
        self.grades = {
            (g["student_id"], g["course_code"]): dict(g) for g in data.get("grades", [])
        }

    # --- loading ----------------------------------------------------------
    @classmethod
    def from_file(cls, path: Path) -> "Store":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"Seed data not found at {p}. Run: python scripts/generate_data.py"
            )
        with p.open() as fh:
            return cls(json.load(fh))

    # --- lookups ----------------------------------------------------------
    def student_name(self, student_id: str) -> str:
        s = self.students.get(student_id)
        return s["name"] if s else student_id

    def course(self, code: str) -> dict:
        c = self.courses.get(code)
        if not c:
            raise NotFound(f"course {code}")
        return c

    def student(self, student_id: str) -> dict:
        s = self.students.get(student_id)
        if not s:
            raise NotFound(f"student {student_id}")
        return s

    def courses_taught_by(self, professor_id: str) -> set[str]:
        return {code for code, c in self.courses.items() if c["professor_id"] == professor_id}

    def courses_for_student(self, student_id: str) -> set[str]:
        return {code for (sid, code) in self.enrollments if sid == student_id}

    def is_enrolled(self, student_id: str, course_code: str) -> bool:
        return (student_id, course_code) in self.enrollments

    # --- grade views ------------------------------------------------------
    def _enrich(self, g: dict) -> dict:
        course = self.courses.get(g["course_code"], {})
        return {
            "student_id": g["student_id"],
            "student_name": self.student_name(g["student_id"]),
            "course_code": g["course_code"],
            "course_title": course.get("title", g["course_code"]),
            "score": g["score"],
            "letter": g.get("letter") or letter_for(g["score"]),
            "updated_at": g.get("updated_at", ""),
            "updated_by": g.get("updated_by", ""),
        }

    def grades_for_student(self, student_id: str, only_courses: set[str] | None = None) -> list[dict]:
        out = []
        for (sid, code), g in self.grades.items():
            if sid != student_id:
                continue
            if only_courses is not None and code not in only_courses:
                continue
            out.append(self._enrich(g))
        return sorted(out, key=lambda g: g["course_code"])

    def grades_for_course(self, course_code: str) -> list[dict]:
        self.course(course_code)  # ensures it exists
        out = [self._enrich(g) for (sid, code), g in self.grades.items() if code == course_code]
        return sorted(out, key=lambda g: g["student_id"])

    def course_view(self, code: str) -> dict:
        c = self.course(code)
        return {
            "code": c["code"],
            "title": c["title"],
            "professor_id": c["professor_id"],
            "professor_name": self.professors.get(c["professor_id"], {}).get("name", c["professor_id"]),
        }

    # --- mutations --------------------------------------------------------
    def upsert_grade(self, student_id: str, course_code: str, score: float, updated_by: str) -> dict:
        self.course(course_code)   # 404 if course missing
        self.student(student_id)   # 404 if student missing
        record = {
            "student_id": student_id,
            "course_code": course_code,
            "score": score,
            "letter": letter_for(score),
            "updated_at": _now_iso(),
            "updated_by": updated_by,
        }
        self.grades[(student_id, course_code)] = record
        return self._enrich(record)
