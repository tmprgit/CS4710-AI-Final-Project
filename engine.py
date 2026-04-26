"""
engine.py — Three-signal hybrid retrieval engine.

  Signal 1 — Department alias boost  (rule-based, ~0 ms)
    Explicit map from common terms ("math", "cs", "econ") to course
    mnemonics. If the query references a department, courses in that
    department receive a strong multiplicative score boost. This is the
    single most important fix for categorical queries.

  Signal 2 — BM25  (rank_bm25, ~1 ms)
    Classic sparse keyword retrieval. Good at exact term matching, acronyms,
    and named technologies. We strip domain stop-words ("course", "courses",
    "class", "take") that appear across every document and would otherwise
    inflate IDF scores for irrelevant matches.

  Signal 3 — Bi-encoder (all-mpnet-base-v2, ~80 ms)
    Dense semantic retrieval. Captures paraphrases and synonyms BM25 misses.
    "I want something with proofs" → discrete math, algorithms, real analysis.

  Signal 4 — Cross-encoder re-ranking (ms-marco-MiniLM-L-6-v2, ~200 ms)
    Joint (query, document) attention. Most accurate signal but slowest;
    applied only to top-50 candidates from Signals 2+3.

  Final score = dept_boost × (w_bm25×bm25_norm + w_bi×bi_norm + w_cross×cross_norm)
  Weights: BM25 0.30 · bi-encoder 0.20 · cross-encoder 0.50
"""

from __future__ import annotations

import os
import pickle
import re
from dataclasses import dataclass, field
from datetime import time as dtime
from typing import Optional

import numpy as np
from nltk.stem import PorterStemmer
_stemmer = PorterStemmer()

try:
    from rank_bm25 import BM25Okapi
    _BM25_OK = True
except ImportError:
    _BM25_OK = False

try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    _ST_OK = True
except ImportError:
    _ST_OK = False

# ─────────────────────────────────────────────────────────────────────────────
# Models & weights
# ─────────────────────────────────────────────────────────────────────────────

BI_MODEL      = "all-mpnet-base-v2"
CROSS_MODEL   = "cross-encoder/ms-marco-MiniLM-L-6-v2"
INDEX_FILE    = os.path.join(os.path.dirname(__file__), ".index_mpnet.pkl")

W_BM25  = 0.30
W_BI    = 0.20
W_CROSS = 0.50

STAGE1_CANDIDATES = 50   # fed into cross-encoder

# Multiplicative bonus applied to courses whose mnemonic matches a detected
# department in the query. 2.5 is strong enough to dominate for categorical
# queries while still allowing cross-dept results when the query is ambiguous.
DEPT_BOOST = 2.5

# ─────────────────────────────────────────────────────────────────────────────
# Department alias map
# ─────────────────────────────────────────────────────────────────────────────

# Maps lowercase query tokens / phrases → set of course mnemonics to boost.
# Multi-word phrases are checked before single tokens.
DEPT_ALIASES: dict[str, set[str]] = {
    # Mathematics
    "math":           {"MATH"},
    "maths":          {"MATH"},
    "mathematics":    {"MATH"},
    "calculus":       {"MATH"},
    "linear algebra": {"MATH"},
    "differential equations": {"MATH"},
    # Computer Science
    "cs":             {"CS"},
    "compsci":        {"CS"},
    "computer science": {"CS"},
    # Data Science
    "ds":             {"DS"},
    "data science":   {"DS"},
    # Statistics
    "stat":           {"STAT"},
    "stats":          {"STAT"},
    "statistics":     {"STAT"},
    # Physics
    "phys":           {"PHYS"},
    "physics":        {"PHYS"},
    # Chemistry
    "chem":           {"CHEM"},
    "chemistry":      {"CHEM"},
    # Biology
    "bio":            {"BIOL"},
    "biology":        {"BIOL"},
    "biol":           {"BIOL"},
    # Economics
    "econ":           {"ECON"},
    "economics":      {"ECON"},
    # Psychology
    "psych":          {"PSYC"},
    "psychology":     {"PSYC"},
    "psyc":           {"PSYC"},
    # Philosophy
    "phil":           {"PHIL"},
    "philosophy":     {"PHIL"},
    # History
    "hist":           {"HIST"},
    "history":        {"HIST"},
    # Writing / English
    "writing":        {"ENWR"},
    "english":        {"ENWR"},
    "enwr":           {"ENWR"},
    # Engineering / ECE
    "ece":            {"ECE"},
    "electrical engineering": {"ECE"},
    "computer engineering":   {"ECE", "CS"},
    # Systems
    "sys":            {"SYS"},
    "systems engineering":    {"SYS"},
    # Commerce / Business
    "comm":           {"COMM"},
    "commerce":       {"COMM"},
    "business":       {"COMM"},
    "mcintire":       {"COMM"},
    # Sociology
    "soc":            {"SOC"},
    "sociology":      {"SOC"},
    # Environmental Science
    "evsc":           {"EVSC"},
    "environmental":  {"EVSC"},
    "environment":    {"EVSC"},
    # Public Policy
    "ppl":            {"PPL"},
    "policy":         {"PPL"},
}

# BM25 stop-words that are meaningless in a course catalog context
_BM25_STOP = {
    "course", "courses", "class", "classes", "take", "taking",
    "want", "need", "find", "good", "great", "best", "like",
    "looking", "something", "show", "me", "give", "recommend",
    "a", "an", "the", "i", "my", "is", "in", "for", "to", "of",
    "and", "or", "that", "this", "with", "are", "at", "uva",
}


# ─────────────────────────────────────────────────────────────────────────────
# Student profile
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class StudentProfile:
    major: str = "Undeclared"
    year: int = 1
    completed: list[str] = field(default_factory=list)
    busy_times: list[dict] = field(default_factory=list)
    career_goals: str = ""

    def __post_init__(self) -> None:
        self.completed = [
            normalized_code
            for normalized_code in (_normalize_course_code(code) for code in self.completed)
            if normalized_code
        ]

    @classmethod
    def from_dict(cls, d: dict) -> "StudentProfile":
        return cls(
            major=d.get("major", "Undeclared"),
            year=d.get("year", 1),
            completed=d.get("completed", []),
            busy_times=d.get("busy_times", []),
            career_goals=d.get("career_goals", ""),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Constraint solver
# ─────────────────────────────────────────────────────────────────────────────

def _t(s: str) -> dtime:
    h, m = s.split(":")
    return dtime(int(h), int(m))

def _overlap(a0: str, a1: str, b0: str, b1: str) -> bool:
    return _t(a0) < _t(b1) and _t(b0) < _t(a1)


def _normalize_course_code(raw_code: str) -> str:
    return re.sub(r"\s+", "", raw_code or "").upper()


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values

def check_constraints(course: dict, profile: StudentProfile) -> tuple[bool, list[str]]:
    notes: list[str] = []
    completed_courses = set(profile.completed)

    if course["id"] in completed_courses:
        return False, ["Already completed."]

    prereq_groups = course.get("prereq_groups") or []
    if prereq_groups:
        missing_groups = [
            " or ".join(group)
            for group in prereq_groups
            if not any(option in completed_courses for option in group)
        ]
        if missing_groups:
            return False, [f"Missing prereq(s): {'; '.join(missing_groups)}"]
    else:
        missing = [prereq for prereq in course.get("prereqs", []) if prereq not in completed_courses]
        if missing:
            return False, [f"Missing prereq(s): {', '.join(missing)}"]

    sections = course.get("sections", [])
    if not sections:
        return False, ["No active sections this semester."]

    free_sections: list[str] = []
    blocked_sections: list[str] = []
    tba_sections: list[str] = []

    for sec in sections:
        meetings = sec.get("meetings", [])
        scheduled_meetings = [
            meeting
            for meeting in meetings
            if meeting.get("days") and meeting.get("start") and meeting.get("end")
        ]

        if not scheduled_meetings:
            free_sections.append(sec["section"])
            tba_sections.append(sec["section"])
            continue

        has_conflict = any(
            any(
                set(meeting["days"]) & set(busy_time["days"])
                and _overlap(meeting["start"], meeting["end"], busy_time["start"], busy_time["end"])
                for busy_time in profile.busy_times
            )
            for meeting in scheduled_meetings
        )

        if has_conflict:
            blocked_sections.append(sec["section"])
        else:
            free_sections.append(sec["section"])

    free_sections = _dedupe_preserving_order(free_sections)
    blocked_sections = _dedupe_preserving_order(blocked_sections)
    tba_sections = _dedupe_preserving_order(tba_sections)

    if free_sections:
        if blocked_sections:
            notes.append(
                f"Section(s) {', '.join(blocked_sections)} conflict — "
                f"{', '.join(free_sections)} available."
            )
        if tba_sections:
            notes.append(f"Section(s) {', '.join(tba_sections)} have TBA meeting times.")
        return True, notes
    return False, ["All scheduled sections conflict with your schedule."]


# ─────────────────────────────────────────────────────────────────────────────
# Result
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CourseResult:
    course: dict
    bi_score: float
    bm25_score: float
    cross_score: float
    final_score: float
    dept_boosted: bool
    eligible: bool
    reasons: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Lowercase word tokens, stemmed, stripped of BM25 stop-words."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [_stemmer.stem(t) for t in tokens if t not in _BM25_STOP]



def _minmax(arr: np.ndarray) -> np.ndarray:
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.ones_like(arr)
    return (arr - lo) / (hi - lo)


# ─────────────────────────────────────────────────────────────────────────────
# Recommender
# ─────────────────────────────────────────────────────────────────────────────

class CourseRecommender:


    def __init__(self):
        if not _ST_OK:
            raise ImportError("Run: pip install sentence-transformers")
        if not _BM25_OK:
            raise ImportError("Run: pip install rank-bm25")

        print(f"[INFO] Loading bi-encoder   : {BI_MODEL}")
        self.bi    = SentenceTransformer(BI_MODEL)
        print(f"[INFO] Loading cross-encoder: {CROSS_MODEL}")
        self.cross = CrossEncoder(CROSS_MODEL, max_length=512)

        self.courses: list[dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.bm25: Optional[BM25Okapi] = None
        
        # ── NEW: Dynamic alias trackers ──
        self.dept_aliases: dict[str, set[str]] = DEPT_ALIASES.copy()
        self.dept_phrases: list[str] = []

    def _detect_dept_mnemonics(self, query: str) -> set[str]:
        """Dynamically detect department mnemonics based on catalog data."""
        q_lower = query.lower()
        matched: set[str] = set()
        for phrase in self.dept_phrases:
            escaped = re.escape(phrase)
            pattern = r"\b" + escaped + r"\b"
            if re.search(pattern, q_lower):
                matched.update(self.dept_aliases[phrase])
        return matched

    # ── Document text ──────────────────────────────────────────────────────

    def _doc_text(self, course: dict) -> str:
        """
        Document text for embedding and BM25.

        The mnemonic and full department name are repeated prominently so
        that department-referential queries ("math courses") get strong
        signal from both BM25 (token match) and the bi-encoder.
        """
        mnem = course["mnemonic"]
        dept_names = {
            "CS": "Computer Science",
            "MATH": "Mathematics",
            "STAT": "Statistics",
            "DS": "Data Science",
            "ECE": "Electrical Computer Engineering",
            "PHYS": "Physics",
            "CHEM": "Chemistry",
            "BIOL": "Biology",
            "ECON": "Economics",
            "PSYC": "Psychology",
            "PHIL": "Philosophy",
            "ENWR": "English Writing",
            "HIST": "History",
            "COMM": "Commerce Business",
            "SOC": "Sociology",
            "EVSC": "Environmental Science",
            "PPL": "Public Policy",
            "SYS": "Systems Engineering",
        }
        dept_name = course.get("subject_descr") or dept_names.get(mnem, mnem)
        tags = " ".join(course.get("tags", []))
        prereq_groups = course.get("prereq_groups") or []
        if prereq_groups:
            prereq_str = "; ".join(" or ".join(group) for group in prereq_groups)
        else:
            prereq_str = ", ".join(course.get("prereqs", [])) or "none"
        wl = course.get("workload_hrs_week", "")
        wl_str = f"Workload approximately {wl} hours per week." if wl else ""
        reviews = course.get("reviews", "")

        # Department name repeated 3× to give BM25 and the bi-encoder a
        # strong categorical anchor without drowning out the description.
        return (
            f"{course['title']}. "
            f"{mnem} {mnem} {dept_name} {dept_name} department. "
            f"Topics: {tags}. "
            f"{course['description']} "
            f"{wl_str} "
            f"Prerequisites: {prereq_str}. "
            f"Student notes: {reviews}"
        )

    # ── Query augmentation ─────────────────────────────────────────────────

    def _augment_query(self, raw: str, profile: StudentProfile) -> str:
        year_map = {1: "first-year student", 2: "sophomore",
                    3: "junior", 4: "senior"}
        yr = year_map.get(profile.year, "student")
        parts = []
        if profile.major and profile.major != "Undeclared":
            parts.append(f"I am a {yr} studying {profile.major}.")
        else:
            parts.append(f"I am a {yr}.")
        if profile.career_goals:
            parts.append(f"Career goal: {profile.career_goals}.")
        parts.append(raw)
        return " ".join(parts)

    # ── Index ──────────────────────────────────────────────────────────────

    def build_index(self, courses: list[dict], force: bool = False) -> None:
        self.courses = courses
        ids = [c.get("key", c["id"]) for c in courses]

        # Always rebuild BM25 in memory (it's instant)
        doc_texts = [self._doc_text(c) for c in courses]
        self.bm25 = BM25Okapi([_tokenize(t) for t in doc_texts])

        # Load or build bi-encoder index
        if not force and os.path.exists(INDEX_FILE):
            print("[INFO] Loading cached index…")
            with open(INDEX_FILE, "rb") as f:
                cached = pickle.load(f)
            if cached.get("model") == BI_MODEL and cached.get("ids") == ids:
                self.embeddings = cached["embeddings"]
                print(f"[INFO] Index ready — {len(self.courses)} courses.")
                return
            print("[INFO] Cache mismatch — rebuilding…")

        print(f"[INFO] Embedding {len(courses)} courses with {BI_MODEL}…")
        self.embeddings = self.bi.encode(
            doc_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({"model": BI_MODEL, "ids": ids,
                         "embeddings": self.embeddings}, f)
        print("[INFO] Index saved.")

    # ── Query ──────────────────────────────────────────────────────────────

    def query(
        self,
        raw_query: str,
        profile: StudentProfile,
        top_k: int = 5,
        show_ineligible: bool = False,
    ) -> list[CourseResult]:
        if self.embeddings is None or self.bm25 is None:
            raise RuntimeError("Call build_index() first.")

        # Keep augmented for the cross-encoder later
        augmented = self._augment_query(raw_query, profile)

        # ── Department detection ───────────────────────────────────────────
        # Note: now calling the class method `self._detect_dept_mnemonics`
        dept_mnemonics = self._detect_dept_mnemonics(raw_query)

        # ── Signal 1: BM25 ────────────────────────────────────────────────
        # Using raw_query to prevent profile hijacking
        bm25_raw = np.array(
            self.bm25.get_scores(_tokenize(raw_query)), dtype=np.float32
        )
        bm25_norm = _minmax(bm25_raw)

        # ── Signal 2: bi-encoder ──────────────────────────────────────────
        # Using raw_query
        q_vec = self.bi.encode(
            raw_query, convert_to_numpy=True, normalize_embeddings=True
        )
        bi_raw: np.ndarray = self.embeddings @ q_vec
        bi_norm = _minmax(bi_raw)

        # ── Blend signals 1+2, take top candidates for cross-encoder ──────
        combined = W_BM25 * bm25_norm + W_BI * bi_norm

        # ── Apply Department Boost (Stage 1) ───────────────────────────────
        if dept_mnemonics:
            for i, course in enumerate(self.courses):
                if course["mnemonic"] in dept_mnemonics:
                    combined[i] *= DEPT_BOOST

        top_idx = np.argsort(combined)[::-1][:STAGE1_CANDIDATES]

        # ── Signal 3: cross-encoder ───────────────────────────────────────
        # Using the augmented profile query for intelligent reranking!
        pairs = [(augmented, self._doc_text(self.courses[i])) for i in top_idx]
        raw_cross = self.cross.predict(pairs, show_progress_bar=False)
        cross_norm = 1.0 / (1.0 + np.exp(-raw_cross))   # sigmoid → [0,1]

        # Normalise within candidates so blend is fair
        bi_cand   = _minmax(bi_raw[top_idx])
        bm25_cand = _minmax(bm25_raw[top_idx])
        
        # Final semantic blend without the heavy multiplier
        blended   = W_BM25 * bm25_cand + W_BI * bi_cand + W_CROSS * cross_norm

        # ── Sort and apply constraints ─────────────────────────────────────
        order = np.argsort(blended)[::-1]

        eligible_results:   list[CourseResult] = []
        ineligible_results: list[CourseResult] = []

        for rank_pos in order:
            ci      = int(top_idx[rank_pos])
            course  = self.courses[ci]
            boosted = bool(dept_mnemonics and course["mnemonic"] in dept_mnemonics)
            eligible, reasons = check_constraints(course, profile)
            result = CourseResult(
                course       = course,
                bi_score     = float(bi_raw[ci]),
                bm25_score   = float(bm25_raw[ci]),
                cross_score  = float(cross_norm[rank_pos]),
                final_score  = float(blended[rank_pos]),
                dept_boosted = boosted,
                eligible     = eligible,
                reasons      = reasons,
            )
            (eligible_results if eligible else ineligible_results).append(result)

        if show_ineligible:
            return eligible_results[:top_k] + ineligible_results[:top_k]
        return eligible_results[:top_k]
