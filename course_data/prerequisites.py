"""
Parse and normalize course prerequisites from course descriptions.
"""

import re


def normalize_course_code(raw_code: str, valid_subjects: set[str] | None = None) -> str:
    """
    Normalize a course code like 'CS 1110' or 'cs1110' to 'CS1110'.
    If valid_subjects is provided, only return codes with valid subjects.
    """
    if not raw_code:
        return ""

    normalized = re.sub(r"\s+", "", raw_code.upper())

    if valid_subjects:
        for subject in valid_subjects:
            if normalized.startswith(subject):
                return normalized

        return ""

    return normalized


def parse_prerequisite_groups(
    description: str | None, valid_subjects: set[str] | None = None
) -> list[list[str]]:
    """
    Parse prerequisite groups from a course description.
    Returns a list of groups, where each group is a list of alternative courses.
    Example: [['CS1110', 'CS1111'], ['MATH1310']] means (CS1110 OR CS1111) AND MATH1310
    """
    if not description:
        return []

    groups: list[list[str]] = []
    description_lower = description.lower()

    if "prerequisite" not in description_lower:
        return []

    prereq_section = re.split(r"prerequisite[s]?:\s*", description_lower, flags=re.IGNORECASE)
    if len(prereq_section) < 2:
        return []

    prereq_text = prereq_section[1]
    prereq_text = re.split(r"[.;]|\s+(and|or)\s+course", prereq_text, flags=re.IGNORECASE)[0]

    course_pattern = r"([A-Z]{2,4})\s*(\d{3,4})"
    matches = re.findall(course_pattern, prereq_text, re.IGNORECASE)

    for subject, number in matches:
        code = f"{subject.upper()}{number}"

        if valid_subjects and code[:len(subject.upper())] not in valid_subjects:
            continue

        groups.append([code])

    return groups


def parse_prerequisites(description: str | None) -> list[str]:
    """
    Simple extraction of all course codes mentioned in a description.
    Returns a flat list of course codes (no grouping).
    """
    if not description:
        return []

    course_pattern = r"([A-Z]{2,4})\s*(\d{3,4})"
    matches = re.findall(course_pattern, description, re.IGNORECASE)

    return [f"{subject.upper()}{number}" for subject, number in matches]
