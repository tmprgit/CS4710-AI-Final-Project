from __future__ import annotations

import html
import re
import sqlite3
from pathlib import Path

from course_data.prerequisites import normalize_course_code, parse_prerequisite_groups


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "course_data" / "course_data.sqlite3"

EXAMPLE_PROFILES = [
    {
        "name": "Alex",
        "major": "Computer Science",
        "year": 3,
        "completed": ["CS1110", "CS2100", "CS2120", "MATH1310", "MATH1320"],
        "busy_times": [{"days": ["Tue", "Thu"], "start": "15:30", "end": "18:30"}],
        "career_goals": "software engineering, NLP, machine learning",
    },
    {
        "name": "Jordan",
        "major": "Data Science",
        "year": 2,
        "completed": ["CS1110", "STAT1601", "MATH1310"],
        "busy_times": [{"days": ["Mon", "Wed", "Fri"], "start": "09:00", "end": "11:00"}],
        "career_goals": "applied machine learning and data analysis",
    },
    {
        "name": "Sam",
        "major": "Undeclared",
        "year": 1,
        "completed": [],
        "busy_times": [],
        "career_goals": "exploring technology and AI",
    },
    {
        "name": "Riley",
        "major": "Biology",
        "year": 2,
        "completed": ["BIOL2100", "CHEM1410", "STAT1601"],
        "busy_times": [{"days": ["Mon", "Wed"], "start": "13:00", "end": "16:00"}],
        "career_goals": "computational biology and medical research",
    },
]

DAY_NAME_BY_CODE = {
    "Mo": "Mon",
    "Tu": "Tue",
    "We": "Wed",
    "Th": "Thu",
    "Fr": "Fri",
    "Sa": "Sat",
    "Su": "Sun",
}

COURSE_QUERY = """
SELECT
    c.id,
    c.subject,
    c.subject_descr,
    c.catalog_number,
    c.title,
    c.descrlong,
    c.units_minimum,
    c.units_maximum,
    c.rqmnt_designtn
FROM courses c
ORDER BY c.subject, c.catalog_number, c.title
"""

SECTION_QUERY = """
SELECT
    s.id AS section_id,
    s.course_id,
    s.section,
    s.section_type,
    s.title,
    s.instructor_names,
    s.days,
    s.start_time,
    s.end_time,
    s.meeting_instructor
FROM sections s
ORDER BY s.course_id, s.section, s.section_type, s.start_time, s.end_time
"""

PREREQ_QUERY = """
SELECT
    p.course_id,
    p.prereq
FROM prereqs p
ORDER BY p.course_id, p.prereq
"""


def parse_course_number(catalog_number: str) -> int:
    """Extract the numeric part of a catalog number like '1110' or '1110-001'."""
    match = re.search(r"\d+", catalog_number or "")
    return int(match.group()) if match else 0


def clean_text(value: str | None, default: str = "") -> str:
    """Collapse repeated whitespace and provide a default for blank values."""
    normalized = html.unescape(value or "")
    normalized = re.sub(r"\*+\s*available as of\s+\d{2}/\d{2}/\d{4}", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"[\x00-\x1f\x7f]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or default


def normalize_time(raw_time: str | None) -> str:
    """Convert database times like '9.30' or '09.30.00.000000' into '09:30'."""
    if not raw_time:
        return ""

    match = re.match(r"(\d{1,2})[:.](\d{2})", clean_text(raw_time))
    if not match:
        return ""

    hour, minute = match.groups()
    return f"{int(hour):02d}:{minute}"


def parse_meeting_days(day_codes: str | None) -> list[str]:
    """Convert abbreviated database day codes into readable weekday names."""
    normalized = clean_text(day_codes)
    if not normalized or normalized.upper() in {"ARR", "NO MTGS.", "TBA"}:
        return []

    codes = re.findall(r"Mo|Tu|We|Th|Fr|Sa|Su", normalized, flags=re.IGNORECASE)
    return [DAY_NAME_BY_CODE[code[:1].upper() + code[1:].lower()] for code in codes]


def format_credits(minimum: int | None, maximum: int | None) -> int | str:
    """Return either a single credit value or a range string."""
    if minimum and maximum and minimum != maximum:
        return f"{minimum}-{maximum}"
    return minimum or maximum or 0


def build_section_label(section: str, section_type: str | None) -> str:
    """Include the section type when one exists."""
    return f"{section} {section_type}" if section_type else section


def merge_unique_items(existing_items: list[str], new_items: list[str]) -> list[str]:
    merged = list(existing_items)
    seen = set(existing_items)
    for item in new_items:
        if item in seen:
            continue
        seen.add(item)
        merged.append(item)
    return merged


def split_instructor_names(*raw_values: str | None) -> list[str]:
    names: list[str] = []
    for raw_value in raw_values:
        if not raw_value:
            continue

        for part in html.unescape(raw_value).replace("\r", ",").replace("\n", ",").split(","):
            name = clean_text(part).strip("- ")
            if name:
                names.append(name)

    return merge_unique_items([], names)


def format_instructors(instructors: list[str]) -> str:
    return ", ".join(instructors) if instructors else "TBA"


def build_fallback_prereq_groups(
    raw_prereqs: list[str],
    valid_subjects: set[str],
    course_code: str,
) -> list[list[str]]:
    groups: list[list[str]] = []
    for raw_prereq in raw_prereqs:
        code = normalize_course_code(raw_prereq, valid_subjects=valid_subjects)
        if code and code != course_code:
            groups.append([code])
    return groups


def finalize_prereq_groups(prereq_groups: list[list[str]], course_code: str) -> list[list[str]]:
    cleaned_groups: list[list[str]] = []
    seen_groups: set[tuple[str, ...]] = set()

    for group in prereq_groups:
        cleaned_group = [code for code in group if code != course_code]
        if not cleaned_group:
            continue

        group_key = tuple(cleaned_group)
        if group_key in seen_groups:
            continue

        cleaned_groups.append(cleaned_group)
        seen_groups.add(group_key)

    return cleaned_groups


def load_rows(connection: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    """Run a query and return all rows with sqlite row access."""
    return connection.execute(query).fetchall()


def load_optional_rows(connection: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    """Return query results, or an empty list when an optional table is missing."""
    try:
        return load_rows(connection, query)
    except sqlite3.OperationalError as error:
        if "no such table" in str(error).lower():
            return []
        raise


def load_courses(database_path: Path = DATABASE_PATH) -> list[dict]:
    """
    Read the course catalog from SQLite and shape it into the app's expected format.

    The output structure is intentionally kept compatible with the existing codebase.
    """
    if not database_path.exists():
        raise FileNotFoundError(f"Course database not found at {database_path}")

    try:
        with sqlite3.connect(database_path) as connection:
            connection.row_factory = sqlite3.Row
            course_rows = load_rows(connection, COURSE_QUERY)
            section_rows = load_rows(connection, SECTION_QUERY)
            prereq_rows = load_optional_rows(connection, PREREQ_QUERY)
    except sqlite3.Error as error:
        raise RuntimeError(f"Failed to load catalog data from {database_path}") from error

    valid_subjects = {row["subject"] for row in course_rows}

    sections_by_course_id: dict[int, dict[int, dict]] = {}
    for row in section_rows:
        course_sections = sections_by_course_id.setdefault(row["course_id"], {})
        section_data = course_sections.get(row["section_id"])
        if section_data is None:
            instructors = split_instructor_names(row["instructor_names"])
            meeting_days = parse_meeting_days(row["days"])
            meeting_start = normalize_time(row["start_time"])
            meeting_end = normalize_time(row["end_time"])
            meeting_instructors = split_instructor_names(row["meeting_instructor"])

            meetings = []
            if meeting_days or meeting_start or meeting_end:
                meetings.append({
                    "days": meeting_days,
                    "start": meeting_start,
                    "end": meeting_end,
                    "instructors": meeting_instructors,
                    "instructor": format_instructors(meeting_instructors),
                })

            section_data = {
                "section": build_section_label(row["section"], row["section_type"]),
                "title": clean_text(row["title"]),
                "instructors": instructors,
                "instructor": format_instructors(instructors),
                "meetings": meetings,
            }
            course_sections[row["section_id"]] = section_data


    prereqs_by_course_id: dict[int, list[str]] = {}
    for row in prereq_rows:
        prereqs_by_course_id.setdefault(row["course_id"], []).append(row["prereq"])

    courses: list[dict] = []
    for row in course_rows:
        subject_name = clean_text(row["subject_descr"], row["subject"])
        requirement_name = clean_text(row["rqmnt_designtn"])
        course_code = f"{row['subject']}{row['catalog_number']}"
        prereq_groups = finalize_prereq_groups(
            parse_prerequisite_groups(row["descrlong"], valid_subjects=valid_subjects),
            course_code=course_code,
        )
        if not prereq_groups:
            prereq_groups = build_fallback_prereq_groups(
                prereqs_by_course_id.get(row["id"], []),
                valid_subjects=valid_subjects,
                course_code=course_code,
            )

        prereqs: list[str] = []
        for group in prereq_groups:
            for prereq in group:
                if prereq not in prereqs:
                    prereqs.append(prereq)

        sections = list(sections_by_course_id.get(row["id"], {}).values())

        # Keep field names stable because other modules import and use this shape directly.
        course = {
            "key": f"{row['id']}:{course_code}",
            "id": course_code,
            "mnemonic": row["subject"],
            "subject_descr": subject_name,
            "number": parse_course_number(row["catalog_number"]),
            "catalog_number": row["catalog_number"],
            "title": clean_text(row["title"], "Untitled Course"),
            "description": clean_text(row["descrlong"], "No description available."),
            "credits": format_credits(row["units_minimum"], row["units_maximum"]),
            "prereqs": prereqs,
            "prereq_groups": prereq_groups,
            "sections": sections,
            "tags": [tag for tag in (subject_name, requirement_name) if tag],
            "reviews": "",
        }
        courses.append(course)

    return courses


try:
    COURSES = load_courses()
except (FileNotFoundError, RuntimeError):
    # Importing the module should not crash the whole app if catalog data is unavailable.
    COURSES = []
