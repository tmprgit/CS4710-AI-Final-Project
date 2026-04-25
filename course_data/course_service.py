#!/usr/bin/env python3

import csv
import html
import re
import sqlite3
from pathlib import Path
import requests

from prerequisites import parse_prerequisites

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "course_data.sqlite3"
COOKIE_PATH = BASE_DIR / "cookies.csv"


def clean_text(value: str | None, default: str = "") -> str:
    """Collapse repeated whitespace, remove control chars, unescape HTML."""
    normalized = html.unescape(value or "")
    normalized = re.sub(r"[\x00-\x1f\x7f]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or default


def normalize_time(raw_time: str | None) -> str:
    """Convert SIS times like '9.30' or '09.30.00.000000' into '09:30'."""
    if not raw_time:
        return ""

    match = re.match(r"(\d{1,2})[:.](\d{2})", clean_text(raw_time))
    if not match:
        return ""

    hour, minute = match.groups()
    return f"{int(hour):02d}:{minute}"

# Parse cookies.csv from the browser into the session cookies for the scraper
def load_cookies(session):
    with COOKIE_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = (row.get("Name") or "").strip()
            value = (row.get("Value") or "").strip()
            domain = (row.get("Domain") or "sisuva.admin.virginia.edu").strip()
            path = (row.get("Path") or "/").strip()
            if name:
                session.cookies.set(name, value, domain=domain, path=path)

# Helper function to make GET requests and handle JSON responses with error checking
def get_json(session, endpoint, params):
    url = f"https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/{endpoint}"
    query = {"institution": "UVA01"}
    query.update(params)
    response = session.get(
        url,
        params=query,
        timeout=30,
        headers={
            "Accept": "application/json",
            "Referer": "https://sisuva.admin.virginia.edu/",
        },
    )
    print("GET", response.url)
    response.raise_for_status()
    return response.json()

# Helper function to get subjects from the main page
def fetch_subjects(session):
    payload = get_json(session, "WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_CatalogSubjects", {})
    subjects = payload.get("subjects", [])
    return subjects

# Helper function to get courses for a given subject
def fetch_subject_courses(session, subject):
    payload = get_json(session, "WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_SubjectCourses", {"subject": subject})
    courses = payload.get("courses", [])
    return courses

# Helper function to get course details for a given subject and course ID
def fetch_course_details(session, subject, course_id):
    payload = get_json(
        session,
        "WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_CatalogCourseDetails",
        {"subject": subject, "course_id": course_id},
    )
    details = payload.get("course_details", {})
    return details

# Helper function to get sections for a given subject, course ID, and course offering number
def fetch_sections(session, subject, course_id, crse_offer_nbr):
    payload = get_json(
        session,
        "WEBLIB_HCX_CM.H_BROWSE_CLASSES.FieldFormula.IScript_BrowseSections",
        {"subject": subject, "course_id": course_id, "crse_offer_nbr": crse_offer_nbr},
    )
    sections = payload.get("sections", [])
    return sections


def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Create tables with schema from the extracted JSON
def initialize_db(db_name):
    with connect_db(db_name) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                subject_descr TEXT NOT NULL,
                course_id TEXT NOT NULL,
                crse_offer_nbr TEXT NOT NULL,
                catalog_number TEXT NOT NULL,
                title TEXT NOT NULL,
                descrlong TEXT,
                units_minimum INTEGER,
                units_maximum INTEGER,
                units_inc INTEGER,
                grading_basis TEXT,
                grading_basis_descr TEXT,
                rqmnt_designtn TEXT,
                UNIQUE(subject, course_id, crse_offer_nbr)
            );

            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                section TEXT NOT NULL,
                subject TEXT NOT NULL,
                catalog_number TEXT NOT NULL,
                title TEXT NOT NULL,
                units TEXT,
                section_type TEXT,
                instructor_names TEXT,
                days TEXT,
                start_time TEXT,
                end_time TEXT,
                meeting_instructor TEXT,
                enrollment_total INTEGER,
                class_capacity INTEGER,
                wait_total INTEGER,
                wait_capacity INTEGER,
                topic TEXT,
                enrl_stat TEXT,
                UNIQUE(course_id, section, section_type)
            );

            CREATE TABLE IF NOT EXISTS prereqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                prereq TEXT NOT NULL,
                UNIQUE(course_id, prereq)
            );
            """
        )

# Use prerequisites.py to extract prereqs from the course description and sync them with the database
def sync_course_prereqs(conn, course_row_id, description):
    conn.execute("DELETE FROM prereqs WHERE course_id = ?", (course_row_id,))
    prereqs = parse_prerequisites(description)
    if prereqs:
        conn.executemany(
            "INSERT INTO prereqs (course_id, prereq) VALUES (?, ?)",
            ((course_row_id, prereq) for prereq in prereqs),
        )

# Inser the course info, associated section info, and meetings of that section into the database
# Inserts or updates if the course/section/meeting already exists
def insert_course(conn, course):
    conn.execute(
        """
        INSERT INTO courses (
            subject, subject_descr, course_id, crse_offer_nbr, catalog_number, title,
            descrlong, units_minimum, units_maximum, units_inc,
            grading_basis, grading_basis_descr, rqmnt_designtn
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(subject, course_id, crse_offer_nbr) DO UPDATE SET
            subject_descr = excluded.subject_descr,
            catalog_number = excluded.catalog_number,
            title = excluded.title,
            descrlong = excluded.descrlong,
            units_minimum = excluded.units_minimum,
            units_maximum = excluded.units_maximum,
            units_inc = excluded.units_inc,
            grading_basis = excluded.grading_basis,
            grading_basis_descr = excluded.grading_basis_descr,
            rqmnt_designtn = excluded.rqmnt_designtn
        """,
        (
            course["subject"],
            course["subject_descr"],
            course["course_id"],
            course["crse_offer_nbr"],
            course["catalog_number"],
            course["title"],
            course["details"].get("descrlong"),
            course["details"].get("units_minimum"),
            course["details"].get("units_maximum"),
            course["details"].get("units_inc"),
            course["details"].get("grading_basis"),
            course["details"].get("grading_basis_descr"),
            course["details"].get("rqmnt_designtn"),
        ),
    )

    row = conn.execute(
        "SELECT id FROM courses WHERE subject = ? AND course_id = ? AND crse_offer_nbr = ?",
        (course["subject"], course["course_id"], course["crse_offer_nbr"]),
    ).fetchone()
    if not row:
        return

    course_row_id = row[0]
    sync_course_prereqs(conn, course_row_id, course["details"].get("descrlong"))

    for section in course["sections"]:
        meeting = section["meetings"][0] if section["meetings"] else {}
        conn.execute(
            """
            INSERT INTO sections (
                course_id, section, subject, catalog_number, title, units, section_type,
                instructor_names, days, start_time, end_time, meeting_instructor,
                enrollment_total, class_capacity, wait_total, wait_capacity, topic, enrl_stat
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(course_id, section, section_type) DO UPDATE SET
                subject = excluded.subject,
                catalog_number = excluded.catalog_number,
                title = excluded.title,
                units = excluded.units,
                instructor_names = excluded.instructor_names,
                days = excluded.days,
                start_time = excluded.start_time,
                end_time = excluded.end_time,
                meeting_instructor = excluded.meeting_instructor,
                enrollment_total = excluded.enrollment_total,
                class_capacity = excluded.class_capacity,
                wait_total = excluded.wait_total,
                wait_capacity = excluded.wait_capacity,
                topic = excluded.topic,
                enrl_stat = excluded.enrl_stat
            """,
            (
                course_row_id,
                section["section"],
                section["subject"],
                section["catalog_number"],
                section["title"],
                section["units"],
                section["section_type"],
                ", ".join(section["instructor_names"]),
                meeting.get("days", ""),
                meeting.get("start_time", ""),
                meeting.get("end_time", ""),
                meeting.get("instructor", ""),
                section["enrollment_total"],
                section["class_capacity"],
                section["wait_total"],
                section["wait_capacity"],
                section["topic"],
                section.get("enrl_stat"),
            ),
        )

# Clean API data into usable data
def build_course(session, subject, subject_descr, course_row):
    course_id = str(course_row.get("crse_id") or "")
    crse_offer_nbr = str(course_row.get("crse_offer_nbr") or "")
    catalog_number = str(course_row.get("catalog_nbr") or "")
    details = fetch_course_details(session, subject, course_id)
    sections_raw = fetch_sections(session, subject, course_id, crse_offer_nbr)

    sections = []
    for sec in sections_raw:
        if not isinstance(sec, dict):
            continue

        meetings = []
        for meeting in sec.get("meetings", []):
            if isinstance(meeting, dict):
                meetings.append(
                    {
                        "days": clean_text(meeting.get("days", "")),
                        "start_time": normalize_time(meeting.get("start_time", "")),
                        "end_time": normalize_time(meeting.get("end_time", "")),
                        "instructor": clean_text(meeting.get("instructor", "")),
                        "raw": meeting,
                    }
                )

        sections.append(
            {
                "course_id": course_id,
                "crse_offer_nbr": crse_offer_nbr,
                "subject": str(sec.get("subject") or subject),
                "catalog_number": str(sec.get("catalog_nbr") or catalog_number),
                "section": str(sec.get("class_section") or ""),
                "title": str(sec.get("descr") or details.get("course_title") or ""),
                "units": sec.get("units"),
                "section_type": sec.get("section_type"),
                "instructor_names": [
                    clean_text(instructor.get("name", ""))
                    for instructor in sec.get("instructors", [])
                    if isinstance(instructor, dict) and instructor.get("name")
                ],
                "enrollment_total": sec.get("enrollment_total"),
                "class_capacity": sec.get("class_capacity"),
                "wait_total": sec.get("wait_tot"),
                "wait_capacity": sec.get("wait_cap"),
                "topic": sec.get("topic") or None,
                "meetings": meetings,
                "raw": sec,
                "enrl_stat": sec.get("enrl_stat"),
            }
        )

    return {
        "subject": subject,
        "subject_descr": subject_descr,
        "course_id": course_id,
        "crse_offer_nbr": crse_offer_nbr,
        "catalog_number": catalog_number,
        "title": str(course_row.get("descr") or details.get("course_title") or ""),
        "details": details,
        "sections": sections,
        "raw": course_row,
    }


def main():
    session = requests.Session()
    # I used my browser's data here, could probably be changed but this works
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            )
        }
    )

    load_cookies(session)
    initialize_db(DB_NAME)

    count = 0
    seen = set()

    with connect_db(DB_NAME) as conn:
        # Get all high level subjects (CS, APMA, LAW, etc)
        subjects = fetch_subjects(session)
        for subject_row in subjects:
            subject = subject_row["subject"] # 4 letter subject code
            subject_descr = subject_row.get("descr") or "" # Full subject name

            subject_savepoint = f"subject_{subject}"
            conn.execute(f"SAVEPOINT {subject_savepoint}")
            try:
                # For each course in a subject
                course_rows = fetch_subject_courses(session, subject)
                for course_row in course_rows:
                    # Avoid duplicates
                    key = ( subject, str(course_row.get("crse_id") or "") )
                    if key in seen:
                        continue
                    seen.add(key)

                    course = build_course(session, subject, subject_descr, course_row)
                    savepoint_name = f"course_{count + 1}"
                    conn.execute(f"SAVEPOINT {savepoint_name}")
                    try:
                        insert_course(conn, course)
                        conn.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                        count += 1
                    except Exception as exc:
                        conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                        conn.execute(f"RELEASE SAVEPOINT {savepoint_name}")

                conn.execute(f"RELEASE SAVEPOINT {subject_savepoint}")
                conn.commit()
            except Exception as exc:
                conn.execute(f"ROLLBACK TO SAVEPOINT {subject_savepoint}")
                conn.execute(f"RELEASE SAVEPOINT {subject_savepoint}")
                conn.commit()
                print(f"[ERROR] main: rolled back subject {subject}: {exc}")

    print(f"Built {count} courses into {DB_NAME}")
    return 0


if __name__ == "__main__":
    main()
